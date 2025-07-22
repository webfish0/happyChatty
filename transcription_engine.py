import asyncio
import logging
import tempfile
import os
import wave
from typing import List, Dict, Optional, Tuple
import speech_recognition as sr
from pyannote.audio import Pipeline
import torch
import numpy as np
from dataclasses import dataclass
from performance_profiler import profile_transcription, ComponentProfiler

logger = logging.getLogger(__name__)

@dataclass
class TranscriptionSegment:
    """Represents a transcribed audio segment with speaker information."""
    text: str
    speaker: str
    start_time: float
    end_time: float
    confidence: float = 1.0

class AsyncTranscriptionEngine:
    """Real-time speech transcription with speaker diarization."""
    
    def __init__(self, 
                 huggingface_token: str,
                 model_name: str = "pyannote/speaker-diarization-3.1",
                 whisper_model: str = "base"):
        self.huggingface_token = huggingface_token
        self.model_name = model_name
        self.whisper_model = whisper_model
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize pyannote pipeline for speaker diarization
        try:
            self.diarization_pipeline = Pipeline.from_pretrained(
                self.model_name,
                use_auth_token=self.huggingface_token
            )
            logger.info("Speaker diarization pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load diarization pipeline: {e}")
            self.diarization_pipeline = None
            
    async def transcribe_audio(self, audio_data: bytes) -> List[TranscriptionSegment]:
        """Transcribe audio with speaker diarization."""
        with ComponentProfiler("transcription", "transcribe_audio", {"audio_size": len(audio_data)}):
            try:
                # Save audio data to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_filename = temp_file.name
                    
                # Write audio data to WAV file
                with wave.open(temp_filename, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(16000)
                    wav_file.writeframes(audio_data)
                
                # Perform transcription
                segments = await self._transcribe_file(temp_filename)
                
                # Clean up
                os.unlink(temp_filename)
                
                return segments
                
            except Exception as e:
                logger.error(f"Error transcribing audio: {e}")
                return []
            
    async def _transcribe_file(self, audio_file: str) -> List[TranscriptionSegment]:
        """Transcribe audio file with speaker diarization."""
        with ComponentProfiler("transcription", "_transcribe_file", {"file_size": os.path.getsize(audio_file)}):
            segments = []
            
            try:
                # Load audio for speech recognition
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
                    
                # Basic transcription (fallback if diarization fails)
                try:
                    text = self.recognizer.recognize_google(audio)
                    if text:
                        segments.append(TranscriptionSegment(
                            text=text,
                            speaker="SPEAKER_00",
                            start_time=0.0,
                            end_time=len(audio.frame_data) / (audio.sample_rate * audio.sample_width),
                            confidence=0.8
                        ))
                except sr.UnknownValueError:
                    logger.warning("Speech recognition could not understand audio")
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    
                # Speaker diarization if pipeline is available
                if self.diarization_pipeline:
                    try:
                        # Run diarization
                        diarization = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: self.diarization_pipeline(audio_file)
                        )
                        
                        # Map diarization results to segments
                        speaker_segments = []
                        for turn, _, speaker in diarization.itertracks(yield_label=True):
                            speaker_segments.append({
                                'start': turn.start,
                                'end': turn.end,
                                'speaker': speaker
                            })
                        
                        # Update segments with speaker information
                        if speaker_segments and segments:
                            # For now, assign the first speaker to the transcribed text
                            # In a more sophisticated implementation, we'd segment the audio
                            segments[0].speaker = speaker_segments[0]['speaker']
                            
                    except Exception as e:
                        logger.warning(f"Speaker diarization failed: {e}")
                        
            except Exception as e:
                logger.error(f"Error in file transcription: {e}")
                
            return segments
        
    async def transcribe_chunk(self, audio_chunk: bytes) -> Optional[TranscriptionSegment]:
        """Transcribe a single audio chunk."""
        segments = await self.transcribe_audio(audio_chunk)
        return segments[0] if segments else None
        
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for transcription."""
        return ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR", "zh-CN", "ja-JP", "ko-KR"]
        
    async def test_microphone(self) -> bool:
        """Test if microphone is working."""
        try:
            # Try to record a short sample
            import sounddevice as sd
            duration = 1.0
            sample_rate = 16000
            channels = 1
            
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=channels,
                dtype='int16'
            )
            sd.wait()
            
            # Check if we got any audio
            if len(recording) > 0 and np.mean(np.abs(recording)) > 10:
                logger.info("Microphone test successful")
                return True
            else:
                logger.warning("Microphone test failed - no audio detected")
                return False
                
        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            return False

class BasicTranscriptionEngine:
    """Basic speech transcription without speaker diarization."""
    
    def __init__(self, whisper_model: str = "base"):
        self.whisper_model = whisper_model
        self.recognizer = sr.Recognizer()
        
    async def process_audio_chunk_async(self, audio_chunk: bytes) -> List[TranscriptionSegment]:
        """Process audio chunk with basic transcription."""
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
                
            # Write audio data to WAV file
            with wave.open(temp_filename, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_chunk)
            
            # Basic transcription
            segments = []
            try:
                with sr.AudioFile(temp_filename) as source:
                    audio = self.recognizer.record(source)
                    
                text = self.recognizer.recognize_google(audio)
                if text:
                    segments.append(TranscriptionSegment(
                        text=text,
                        speaker="SPEAKER_00",  # Default speaker
                        start_time=0.0,
                        end_time=len(audio.frame_data) / (audio.sample_rate * audio.sample_width),
                        confidence=0.8
                    ))
            except sr.UnknownValueError:
                logger.warning("Speech recognition could not understand audio")
            except sr.RequestError as e:
                logger.error(f"Speech recognition error: {e}")
                
            # Clean up
            os.unlink(temp_filename)
            return segments
            
        except Exception as e:
            logger.error(f"Error in basic transcription: {e}")
            return []