"""Enhanced processing pipeline with speaker-based voice assignment and optimizations."""
from pathlib import Path
from typing import List, Callable, Optional, Dict
import uuid
import concurrent.futures
from ..models import Project, DialogueSegment
from ..utils.logger import setup_logger
from ..utils.config import config
from .ffmpeg_service import FFmpegService
from .stt_service import STTService
from .omniroute_service import OmniRouteService
from .alternative_translation import (
    GoogleTranslateService,
    HybridTranslationService,
    AltTranslationService
)
from .nllb_translation import (
    NLLBTranslationService,
    NLLBHybridService
)
from .tts_service import TTSService
from .subtitle_service import SubtitleService


logger = setup_logger(__name__)


class ProcessingPipeline:
    """Orchestrates the complete dubbing pipeline with optimizations."""
    
    def __init__(self, translation_provider: str = "hybrid", manual_dict_path: str = None):
        self.ffmpeg = FFmpegService()
        self.stt = None  # Lazy load
        # Use config's TTS provider for consistency
        self.tts = TTSService(
            provider=config.tts_provider,
            api_key=config.tts_api_key,
            base_url=config.tts_base_url,
            voice=config.tts_voice
        )
        self.subtitle = SubtitleService()
        self.project: Optional[Project] = None
        
        # Set translation provider
        self.translation_provider = translation_provider.lower()
        if self.translation_provider == "hybrid":
            self.translator = HybridTranslationService(manual_dict_path=manual_dict_path)
            logger.info("Using Hybrid translation (manual + API fallback)")
        elif self.translation_provider == "alternative":
            self.translator = AltTranslationService(skip_google=True)
            logger.info("Using Alternative translation services (MyMemory/LibreTranslate)")
        elif self.translation_provider == "nllb":
            self.translator = NLLBTranslationService(use_local=False)
            logger.info("Using NLLB-200 translation (Hugging Face API)")
        elif self.translation_provider == "nllb-hybrid":
            self.translator = NLLBHybridService(manual_dict_path=manual_dict_path, use_local_nllb=False)
            logger.info("Using NLLB-200 Hybrid (manual + NLLB API)")
        elif self.translation_provider == "nllb-local":
            self.translator = NLLBTranslationService(use_local=True)
            logger.info("Using NLLB-200 Local (on-device model)")
        elif self.translation_provider == "google":
            self.translator = GoogleTranslateService()
            logger.info("Using Google Translate for translations")
        else:
            self.translator = OmniRouteService()
            logger.info("Using OmniRoute for translations")
        
        # Voice assignment for speakers
        self.speaker_voices = {
            "SPEAKER_1": "km-KH-PisethNeural",      # Male voice
            "SPEAKER_2": "km-KH-SreymomNeural",     # Female voice
            "UNKNOWN": "km-KH-SreymomNeural"        # Default female
        }
    
    def set_speaker_voice(self, speaker: str, voice: str):
        """Assign a specific voice to a speaker."""
        self.speaker_voices[speaker] = voice
        logger.info(f"Assigned voice {voice} to {speaker}")
    
    def create_project(self, video_path: str) -> Project:
        """Create a new project from video file."""
        try:
            logger.info(f"Creating project for video: {video_path}")
            
            # Extract metadata
            metadata = self.ffmpeg.get_video_info(video_path)
            
            # Create project with short directory name
            project_id = str(uuid.uuid4())[:8]  # Use only first 8 chars of UUID
            project = Project(
                video_path=video_path,
                metadata=metadata,
                project_dir=str(config.temp_dir / f"p{project_id}")
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
        """Extract audio and transcribe with speaker detection."""
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
                progress_callback("Transcribing audio with speaker detection...", 40)
            
            # Transcribe with speaker hints
            segments = self.stt.transcribe(audio_path, language="en")
            
            self.project.segments = segments
            
            if progress_callback:
                progress_callback("Transcription complete", 100)
            
            logger.info(f"Transcribed {len(segments)} segments with speaker detection")
            return segments
            
        except Exception as e:
            logger.error(f"Transcription pipeline failed: {e}")
            raise
    
    def translate_segments(self, segments: List[DialogueSegment] = None,
                          progress_callback: Callable[[str, int], None] = None) -> List[DialogueSegment]:
        """Translate segments in parallel for faster processing."""
        try:
            # Get segments from parameter or project
            if segments is None:
                if self.project is None:
                    raise RuntimeError("No project loaded. Cannot translate segments.")
                if not hasattr(self.project, 'segments') or self.project.segments is None:
                    raise RuntimeError("Project has no segments. Run transcription first.")
                segments = self.project.segments
            
            if not segments or len(segments) == 0:
                raise RuntimeError("No segments to translate. Run transcription first.")
            
            total = len(segments)
            
            logger.info(f"Starting parallel translation of {total} segments")
            
            # Use thread pool for parallel translation
            max_workers = min(config.max_concurrent_requests, total)
            completed = 0
            
            def translate_single(segment: DialogueSegment) -> DialogueSegment:
                """Translate a single segment."""
                try:
                    # Different translators have different signatures
                    translator_type = type(self.translator).__name__
                    
                    if translator_type == 'OmniRouteService':
                        # OmniRoute supports context parameter
                        context = f"Speaker: {segment.speaker or 'Unknown'}"
                        segment.khmer_text = self.translator.translate(
                            segment.english_text,
                            source_lang="English",
                            target_lang="Khmer",
                            context=context
                        )
                    elif translator_type in ['HybridTranslationService', 'AltTranslationService', 'NLLBHybridService']:
                        # Hybrid, Alternative, and NLLB Hybrid only accept text
                        segment.khmer_text = self.translator.translate(segment.english_text)
                    elif translator_type in ['GoogleTranslateService', 'NLLBTranslationService']:
                        # Google and NLLB accept source/target lang
                        segment.khmer_text = self.translator.translate(
                            segment.english_text,
                            source_lang='en',
                            target_lang='km'
                        )
                    else:
                        # Default: just pass text
                        segment.khmer_text = self.translator.translate(segment.english_text)
                    
                    return segment
                except Exception as e:
                    logger.error(f"Translation failed for segment: {e}")
                    segment.khmer_text = segment.english_text  # Fallback
                    return segment
            
            # Process in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_segment = {
                    executor.submit(translate_single, seg): seg 
                    for seg in segments
                }
                
                for future in concurrent.futures.as_completed(future_to_segment):
                    completed += 1
                    if progress_callback:
                        progress = int((completed / total) * 100)
                        progress_callback(f"Translating segment {completed}/{total}...", progress)
            
            if progress_callback:
                progress_callback("Translation complete", 100)
            
            logger.info(f"Translated {total} segments to Khmer in parallel")
            return segments
            
        except Exception as e:
            logger.error(f"Translation pipeline failed: {e}")
            raise
    
    def generate_speech(self, segments: List[DialogueSegment] = None,
                       progress_callback: Callable[[str, int], None] = None) -> List[DialogueSegment]:
        """Generate speech with speaker-specific voices in parallel."""
        try:
            segments = segments or self.project.segments
            total = len(segments)
            
            logger.info(f"Starting parallel TTS generation for {total} segments")
            
            # Use thread pool for parallel TTS generation
            max_workers = min(config.max_concurrent_requests, total)
            completed = 0
            
            def generate_single(segment: DialogueSegment) -> DialogueSegment:
                """Generate TTS for a single segment."""
                try:
                    if not segment.khmer_text:
                        logger.warning(f"Segment has no Khmer text, skipping")
                        return segment
                    
                    # Assign voice based on speaker
                    speaker = segment.speaker or "UNKNOWN"
                    voice = self.speaker_voices.get(speaker, self.speaker_voices["UNKNOWN"])
                    
                    # Generate audio file path with short name
                    seg_id = segment.segment_id[:8]  # Use only first 8 chars
                    audio_path = str(Path(self.project.project_dir) / f"s{seg_id}.wav")
                    
                    # Synthesize with speaker-specific voice
                    segment.audio_path = self.tts.synthesize(
                        segment.khmer_text, 
                        audio_path,
                        voice=voice
                    )
                    
                    logger.info(f"Generated TTS with voice {voice} for {speaker}")
                    return segment
                    
                except Exception as e:
                    logger.error(f"TTS generation failed for segment: {e}")
                    return segment
            
            # Process in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_segment = {
                    executor.submit(generate_single, seg): seg 
                    for seg in segments
                }
                
                for future in concurrent.futures.as_completed(future_to_segment):
                    completed += 1
                    if progress_callback:
                        progress = int((completed / total) * 100)
                        progress_callback(f"Generating speech {completed}/{total}...", progress)
            
            if progress_callback:
                progress_callback("Speech generation complete", 100)
            
            logger.info(f"Generated speech for {total} segments in parallel")
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
            
            # Get video duration for timeline composition
            video_duration = self.project.metadata.duration
            
            # Compose audio timeline with proper synchronization
            if progress_callback:
                progress_callback("Composing audio timeline...", 30)
            
            merged_audio = str(Path(self.project.project_dir) / "merged_audio.wav")
            self.ffmpeg.compose_audio_timeline(self.project.segments, merged_audio, video_duration)
            
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
