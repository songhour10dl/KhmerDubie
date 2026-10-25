"""Processing pipeline orchestrator."""
from pathlib import Path
from typing import List, Callable, Optional
import uuid
from ..models import Project, DialogueSegment
from ..utils.logger import setup_logger
from ..utils.config import config
from .ffmpeg_service import FFmpegService
from .stt_service import STTService
from .omniroute_service import OmniRouteService
from .tts_service import TTSService
from .subtitle_service import SubtitleService


logger = setup_logger(__name__)


class ProcessingPipeline:
    """Orchestrates the complete dubbing pipeline."""
    
    def __init__(self):
        self.ffmpeg = FFmpegService()
        self.stt = None  # Lazy load
        self.translator = OmniRouteService()
        self.tts = TTSService()
        self.subtitle = SubtitleService()
        self.project: Optional[Project] = None
    
    def create_project(self, video_path: str) -> Project:
        """Create a new project from video file."""
        try:
            logger.info(f"Creating project for video: {video_path}")
            
            # Extract metadata
            metadata = self.ffmpeg.get_video_info(video_path)
            
            # Create project
            project = Project(
                video_path=video_path,
                metadata=metadata,
                project_dir=str(config.temp_dir / str(uuid.uuid4()))
            )
            
            # Create project directory
            Path(project.project_dir).mkdir(parents=True, exist_ok=True)
            
            self.project = project
            logger.info(f"Project created: {project.project_dir}")
            return project
            
        except Exception as e:
            logger.error(f"Project creation failed: {e}")
            raise
    
    def extract_and_transcribe(self, progress_callback: Callable[[str, int], None] = None) -> List[DialogueSegment]:
        """Extract audio and transcribe to English."""
        try:
            if not self.project:
                raise RuntimeError("No active project")
            
            if progress_callback:
                progress_callback("Extracting audio...", 10)
            
            # Extract audio
            audio_path = str(Path(self.project.project_dir) / "extracted_audio.wav")
            self.ffmpeg.extract_audio(self.project.video_path, audio_path)
            
            if progress_callback:
                progress_callback("Loading Whisper model...", 30)
            
            # Lazy load STT
            if not self.stt:
                self.stt = STTService()
            
            if progress_callback:
                progress_callback("Transcribing audio...", 40)
            
            # Transcribe
            segments = self.stt.transcribe(audio_path, language="en")
            
            self.project.segments = segments
            
            if progress_callback:
                progress_callback("Transcription complete", 100)
            
            logger.info(f"Transcribed {len(segments)} segments")
            return segments
            
        except Exception as e:
            logger.error(f"Transcription pipeline failed: {e}")
            raise
    
    def translate_segments(self, segments: List[DialogueSegment] = None,
                          progress_callback: Callable[[str, int], None] = None) -> List[DialogueSegment]:
        """Translate English segments to Khmer."""
        try:
            segments = segments or self.project.segments
            total = len(segments)
            
            for idx, segment in enumerate(segments):
                if progress_callback:
                    progress = int((idx / total) * 100)
                    progress_callback(f"Translating segment {idx + 1}/{total}...", progress)
                
                # Translate
                segment.khmer_text = self.translator.translate(
                    segment.english_text,
                    source_lang="English",
                    target_lang="Khmer"
                )
            
            if progress_callback:
                progress_callback("Translation complete", 100)
            
            logger.info(f"Translated {total} segments to Khmer")
            return segments
            
        except Exception as e:
            logger.error(f"Translation pipeline failed: {e}")
            raise
    
    def generate_speech(self, segments: List[DialogueSegment] = None,
                       progress_callback: Callable[[str, int], None] = None) -> List[DialogueSegment]:
        """Generate Khmer speech for all segments."""
        try:
            segments = segments or self.project.segments
            total = len(segments)
            
            for idx, segment in enumerate(segments):
                if not segment.khmer_text:
                    logger.warning(f"Segment {idx} has no Khmer text, skipping")
                    continue
                
                if progress_callback:
                    progress = int((idx / total) * 100)
                    progress_callback(f"Generating speech {idx + 1}/{total}...", progress)
                
                # Generate audio file path
                audio_path = str(Path(self.project.project_dir) / f"segment_{segment.segment_id}.wav")
                
                # Synthesize
                segment.audio_path = self.tts.synthesize(segment.khmer_text, audio_path)
            
            if progress_callback:
                progress_callback("Speech generation complete", 100)
            
            logger.info(f"Generated speech for {total} segments")
            return segments
            
        except Exception as e:
            logger.error(f"Speech generation pipeline failed: {e}")
            raise
    
    def export_video(self, output_path: str, 
                    mix_original: bool = True,
                    original_volume: float = 0.1,
                    generate_subtitles: bool = True,
                    progress_callback: Callable[[str, int], None] = None) -> str:
        """Export final dubbed video."""
        try:
            if not self.project or not self.project.segments:
                raise RuntimeError("No segments to export")
            
            if progress_callback:
                progress_callback("Preparing audio segments...", 10)
            
            # Collect audio segments
            audio_files = [seg.audio_path for seg in self.project.segments if seg.audio_path]
            
            if not audio_files:
                raise RuntimeError("No audio files generated")
            
            # Concatenate audio
            if progress_callback:
                progress_callback("Concatenating audio...", 30)
            
            merged_audio = str(Path(self.project.project_dir) / "merged_audio.wav")
            self.ffmpeg.concatenate_audio(audio_files, merged_audio)
            
            # Merge with video
            if progress_callback:
                progress_callback("Merging with video...", 60)
            
            if mix_original:
                final_path = self.ffmpeg.merge_audio_video(
                    self.project.video_path,
                    merged_audio,
                    output_path,
                    original_volume
                )
            else:
                final_path = self.ffmpeg.replace_audio(
                    self.project.video_path,
                    merged_audio,
                    output_path
                )
            
            # Generate subtitles
            if generate_subtitles:
                if progress_callback:
                    progress_callback("Generating subtitles...", 90)
                
                subtitle_path = str(Path(output_path).with_suffix('.srt'))
                self.subtitle.generate_srt(self.project.segments, subtitle_path, use_khmer=True)
            
            if progress_callback:
                progress_callback("Export complete", 100)
            
            self.project.output_path = final_path
            logger.info(f"Video exported successfully: {final_path}")
            return final_path
            
        except Exception as e:
            logger.error(f"Export pipeline failed: {e}")
            raise
    
    def save_project(self, filepath: str = None) -> str:
        """Save project state to file."""
        if not self.project:
            raise RuntimeError("No active project")
        
        if not filepath:
            filepath = str(Path(self.project.project_dir) / "project.json")
        
        self.project.save(filepath)
        logger.info(f"Project saved: {filepath}")
        return filepath
    
    def load_project(self, filepath: str) -> Project:
        """Load project from file."""
        self.project = Project.load(filepath)
        logger.info(f"Project loaded: {filepath}")
        return self.project
