"""Dialogue segment model."""
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class DialogueSegment:
    """A single dialogue segment with timing information."""
    start_time: float  # seconds
    end_time: float  # seconds
    english_text: str
    khmer_text: Optional[str] = None
    audio_path: Optional[str] = None
    speaker: Optional[str] = None
    segment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def duration(self) -> float:
        """Get segment duration in seconds."""
        return self.end_time - self.start_time
    
    def format_time(self, seconds: float) -> str:
        """Format time as HH:MM:SS,mmm for SRT."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    @property
    def start_time_srt(self) -> str:
        """Get start time in SRT format."""
        return self.format_time(self.start_time)
    
    @property
    def end_time_srt(self) -> str:
        """Get end time in SRT format."""
        return self.format_time(self.end_time)
