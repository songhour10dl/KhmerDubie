"""Subtitle generation service."""
from pathlib import Path
from typing import List
from ..models.dialogue_segment import DialogueSegment
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class SubtitleService:
    """SRT subtitle file generator."""
    
    @staticmethod
    def generate_srt(segments: List[DialogueSegment], output_path: str, 
                     use_khmer: bool = True) -> str:
        """Generate SRT subtitle file from dialogue segments."""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for idx, segment in enumerate(segments, start=1):
                    # Skip segments without translation if using Khmer
                    if use_khmer and not segment.khmer_text:
                        continue
                    
                    # Write sequence number
                    f.write(f"{idx}\n")
                    
                    # Write timestamp
                    f.write(f"{segment.start_time_srt} --> {segment.end_time_srt}\n")
                    
                    # Write text
                    text = segment.khmer_text if use_khmer else segment.english_text
                    f.write(f"{text}\n\n")
            
            logger.info(f"Generated SRT subtitle file: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Subtitle generation failed: {e}")
            raise RuntimeError(f"Subtitle generation failed: {e}") from e
    
    @staticmethod
    def generate_dual_srt(segments: List[DialogueSegment], output_path: str) -> str:
        """Generate SRT with both English and Khmer subtitles."""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for idx, segment in enumerate(segments, start=1):
                    # Write sequence number
                    f.write(f"{idx}\n")
                    
                    # Write timestamp
                    f.write(f"{segment.start_time_srt} --> {segment.end_time_srt}\n")
                    
                    # Write both texts
                    f.write(f"{segment.english_text}\n")
                    if segment.khmer_text:
                        f.write(f"{segment.khmer_text}\n")
                    f.write("\n")
            
            logger.info(f"Generated dual SRT subtitle file: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Dual subtitle generation failed: {e}")
            raise RuntimeError(f"Dual subtitle generation failed: {e}") from e
