"""Project model for state management."""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json
from pathlib import Path
from .video_metadata import VideoMetadata
from .dialogue_segment import DialogueSegment


@dataclass
class Project:
    """Project state container."""
    video_path: Optional[str] = None
    metadata: Optional[VideoMetadata] = None
    segments: List[DialogueSegment] = field(default_factory=list)
    output_path: Optional[str] = None
    project_dir: Optional[str] = None
    
    def save(self, filepath: str) -> None:
        """Save project to JSON file."""
        data = {
            'video_path': self.video_path,
            'metadata': asdict(self.metadata) if self.metadata else None,
            'segments': [asdict(seg) for seg in self.segments],
            'output_path': self.output_path,
            'project_dir': self.project_dir
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, filepath: str) -> 'Project':
        """Load project from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        project = cls()
        project.video_path = data.get('video_path')
        project.output_path = data.get('output_path')
        project.project_dir = data.get('project_dir')
        
        if data.get('metadata'):
            # Reconstruct metadata object
            project.metadata = VideoMetadata(**data['metadata'])
        
        if data.get('segments'):
            project.segments = [DialogueSegment(**seg) for seg in data['segments']]
        
        return project
