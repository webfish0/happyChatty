import asyncio
import logging
import numpy as np
import sounddevice as sd
from typing import Optional, Callable, AsyncGenerator
import threading
import queue

logger = logging.getLogger(__name__)

class AsyncAudioCapture:
    """Async audio capture using sounddevice for cross-platform compatibility."""
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 chunk_size: int = 1024,
                 device: Optional[int] = None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device = device
        
        self._stream = None
        self._audio_queue = queue.Queue()
        self._is_recording = False
        self._recording_thread = None
        
    async def start_recording(self) -> None:
        """Start async audio recording."""
        if self._is_recording:
            logger.warning("Recording already in progress")
            return
            
        try:
            # Get default input device if none specified
            if self.device is None:
                devices = sd.query_devices()
                input_devices = [i for i, d in enumerate(devices) 
                               if d['max_input_channels'] > 0]
                if input_devices:
                    self.device = input_devices[0]
                    logger.info(f"Using input device: {devices[self.device]['name']}")
                else:
                    raise RuntimeError("No input devices found")
            
            self._is_recording = True
            self._recording_thread = threading.Thread(target=self._record_audio)
            self._recording_thread.start()
            logger.info("Audio recording started")
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            raise
            
    def _record_audio(self) -> None:
        """Internal method to record audio in a separate thread."""
        try:
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                if self._is_recording:
                    # Convert to bytes and add to queue
                    audio_bytes = (indata * 32767).astype(np.int16).tobytes()
                    self._audio_queue.put(audio_bytes)
            
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device,
                dtype=np.float32,
                blocksize=self.chunk_size,
                callback=audio_callback
            ):
                while self._is_recording:
                    sd.sleep(100)
                    
        except Exception as e:
            logger.error(f"Error in audio recording: {e}")
            self._is_recording = False
            
    async def stop_recording(self) -> None:
        """Stop audio recording."""
        if not self._is_recording:
            return
            
        self._is_recording = False
        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.join(timeout=1.0)
            
        logger.info("Audio recording stopped")
        
    async def get_audio_chunks(self) -> AsyncGenerator[bytes, None]:
        """Get audio chunks as async generator."""
        while self._is_recording or not self._audio_queue.empty():
            try:
                # Get audio data with timeout to allow async operation
                audio_data = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self._audio_queue.get(timeout=0.1)
                )
                yield audio_data
            except queue.Empty:
                await asyncio.sleep(0.01)
                
    def get_audio_level(self, audio_data: bytes) -> float:
        """Calculate audio level from raw audio data."""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            # Calculate RMS
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
            # Normalize to 0-1 range
            level = min(rms / 32767.0, 1.0)
            logger.debug(f"Audio level: {level:.3f} (RMS: {rms:.1f})")
            return level
        except Exception as e:
            logger.error(f"Error calculating audio level: {e}")
            return 0.0
            
    async def get_audio_level_stream(self) -> AsyncGenerator[float, None]:
        """Get audio level as async generator."""
        async for chunk in self.get_audio_chunks():
            yield self.get_audio_level(chunk)
            
    def list_devices(self) -> list:
        """List available audio input devices."""
        devices = sd.query_devices()
        input_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
                
        return input_devices