"""Video metadata model."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AudioTrack:
    """Audio track information."""
    index: int
    codec: str
    sample_rate: int
    channels: int
    language: Optional[str] = None


@dataclass
class VideoMetadata:
    """Video file metadata."""
    filepath: str
    duration: float  # seconds
    width: int
    height: int
    fps: float
    video_codec: str
    audio_tracks: List[AudioTrack]
    format_name: str
    bitrate: Optional[int] = None
    
    @property
    def resolution(self) -> str:
        """Get resolution as string."""
        return f"{self.width}x{self.height}"
    
    @property
    def duration_str(self) -> str:
        """Get duration as HH:MM:SS string."""
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
