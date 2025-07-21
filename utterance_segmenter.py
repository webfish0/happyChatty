import asyncio
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import numpy as np

from transcription_engine import TranscriptionSegment

logger = logging.getLogger(__name__)

@dataclass
class Utterance:
    """Represents a single speaker utterance."""
    speaker: str
    text: str
    start_time: datetime
    end_time: datetime
    confidence: float
    pause_duration: float = 0.0
    
    @property
    def duration(self) -> float:
        """Duration of utterance in seconds."""
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def words_per_minute(self) -> float:
        """Calculate words per minute."""
        if self.duration > 0:
            word_count = len(self.text.split())
            return (word_count / self.duration) * 60
        return 0.0

class UtteranceSegmenter:
    """Segments continuous transcription into speaker utterances based on pauses and speaker changes."""
    
    def __init__(self):
        self.min_pause_duration = 0.5  # Minimum pause to consider end of utterance
        self.max_utterance_duration = 10.0  # Maximum utterance duration in seconds
        self.min_utterance_duration = 0.3  # Minimum utterance duration
        
        # State tracking
        self.pending_segments = []
        self.current_utterance = None
        self.last_activity_time = None
        
    def process_segments(self, segments: List[TranscriptionSegment]) -> List[Utterance]:
        """Process new transcription segments into utterances."""
        utterances = []
        
        for segment in segments:
            # Convert relative times to absolute datetime
            segment_start = datetime.now() - timedelta(seconds=2.0) + timedelta(seconds=segment.start_time)
            segment_end = datetime.now() - timedelta(seconds=2.0) + timedelta(seconds=segment.end_time)
            
            # Check if this continues current utterance or starts new one
            if self._should_start_new_utterance(segment, segment_start):
                # Finalize current utterance
                if self.current_utterance:
                    finalized = self._finalize_current_utterance()
                    if finalized:
                        utterances.append(finalized)
                
                # Start new utterance
                self.current_utterance = Utterance(
                    speaker=segment.speaker,
                    text=segment.text,
                    start_time=segment_start,
                    end_time=segment_end,
                    confidence=segment.confidence
                )
            else:
                # Continue current utterance
                self._continue_current_utterance(segment, segment_end)
            
            self.last_activity_time = segment_end
        
        # Check for timeout on current utterance
        if self.current_utterance and self._should_finalize_timeout():
            finalized = self._finalize_current_utterance()
            if finalized:
                utterances.append(finalized)
        
        return utterances
    
    def _should_start_new_utterance(self, segment: TranscriptionSegment, segment_start: datetime) -> bool:
        """Determine if this segment should start a new utterance."""
        if not self.current_utterance:
            return True
            
        # Speaker change
        if segment.speaker != self.current_utterance.speaker:
            return True
            
        # Long pause
        if self.last_activity_time:
            pause_duration = (segment_start - self.last_activity_time).total_seconds()
            if pause_duration >= self.min_pause_duration:
                return True
                
        # Maximum utterance duration reached
        current_duration = (segment_start - self.current_utterance.start_time).total_seconds()
        if current_duration >= self.max_utterance_duration:
            return True
            
        return False
    
    def _continue_current_utterance(self, segment: TranscriptionSegment, segment_end: datetime):
        """Continue building the current utterance."""
        if not self.current_utterance:
            return
            
        # Append text with space
        if self.current_utterance.text and segment.text:
            self.current_utterance.text += " " + segment.text
        elif segment.text:
            self.current_utterance.text = segment.text
            
        # Update end time and confidence
        self.current_utterance.end_time = segment_end
        # Average confidence
        if self.current_utterance.confidence > 0:
            self.current_utterance.confidence = (
                self.current_utterance.confidence + segment.confidence
            ) / 2
        else:
            self.current_utterance.confidence = segment.confidence
    
    def _should_finalize_timeout(self) -> bool:
        """Check if current utterance should be finalized due to timeout."""
        if not self.current_utterance or not self.last_activity_time:
            return False
            
        timeout_duration = 2.0  # 2 second timeout
        time_since_last = (datetime.now() - self.last_activity_time).total_seconds()
        
        return time_since_last >= timeout_duration
    
    def _finalize_current_utterance(self) -> Optional[Utterance]:
        """Finalize and validate the current utterance."""
        if not self.current_utterance:
            return None
            
        # Calculate pause duration
        if self.last_activity_time:
            self.current_utterance.pause_duration = (
                datetime.now() - self.last_activity_time
            ).total_seconds()
        
        # Validate utterance
        utterance = self.current_utterance
        
        # Check minimum duration
        if utterance.duration < self.min_utterance_duration:
            logger.debug(f"Skipping short utterance: {utterance.duration:.2f}s")
            self.current_utterance = None
            return None
            
        # Check if text is meaningful
        if not utterance.text.strip() or len(utterance.text.strip()) < 2:
            logger.debug("Skipping empty/meaningless utterance")
            self.current_utterance = None
            return None
            
        # Clean up text
        utterance.text = self._clean_text(utterance.text)
        
        logger.info(f"Finalized utterance: {utterance.speaker} - '{utterance.text[:50]}...' ({utterance.duration:.2f}s)")
        
        self.current_utterance = None
        return utterance
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize transcribed text."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove filler words (optional)
        filler_words = {'uh', 'um', 'like', 'you know', 'so', 'actually'}
        words = text.split()
        cleaned_words = [w for w in words if w.lower() not in filler_words]
        
        return ' '.join(cleaned_words)
    
    def reset(self):
        """Reset the segmenter state."""
        if self.current_utterance:
            logger.warning("Resetting with active utterance - discarding current utterance")
            
        self.pending_segments = []
        self.current_utterance = None
        self.last_activity_time = None
        
    def get_stats(self) -> Dict[str, any]:
        """Get segmenter statistics."""
        return {
            "has_active_utterance": self.current_utterance is not None,
            "min_pause_duration": self.min_pause_duration,
            "max_utterance_duration": self.max_utterance_duration,
            "last_activity": self.last_activity_time.isoformat() if self.last_activity_time else None
        }

class AsyncUtteranceSegmenter(UtteranceSegmenter):
    """Async wrapper for utterance segmenter."""
    
    async def process_segments_async(self, segments: List[TranscriptionSegment]) -> List[Utterance]:
        """Process segments asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_segments, segments)
    
    async def reset_async(self):
        """Reset asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.reset)