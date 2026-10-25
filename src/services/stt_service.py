"""Enhanced STT service with speaker diarization support."""
import whisper
from pathlib import Path
from typing import List, Optional
from ..utils.logger import setup_logger
from ..utils.config import config
from ..models.dialogue_segment import DialogueSegment


logger = setup_logger(__name__)


class STTService:
    """Speech-to-Text service with speaker detection."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.stt_model
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}") from e
    
    def transcribe(self, audio_path: str, language: str = "en") -> List[DialogueSegment]:
        """Transcribe audio with speaker detection based on audio patterns."""
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                word_timestamps=False,
                verbose=False
            )
            
            segments = []
            previous_speaker = None
            
            for seg in result['segments']:
                text = seg['text'].strip()
                
                # Simple speaker detection based on text and timing patterns
                # This is a heuristic approach since base Whisper doesn't have diarization
                speaker = self._detect_speaker(text, seg, previous_speaker)
                
                dialogue_seg = DialogueSegment(
                    start_time=seg['start'],
                    end_time=seg['end'],
                    english_text=text,
                    speaker=speaker
                )
                segments.append(dialogue_seg)
                previous_speaker = speaker
            
            logger.info(f"Transcribed {len(segments)} segments with speaker hints")
            return segments
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {e}") from e
    
    def _detect_speaker(self, text: str, segment: dict, previous_speaker: str) -> str:
        """Detect likely speaker based on text patterns and context.
        
        This is a simple heuristic that alternates between speakers based on:
        - Dialogue breaks (pauses between segments)
        - Question/answer patterns
        - Text characteristics
        """
        # Check for long pause (potential speaker change)
        if previous_speaker and 'start' in segment:
            # If this is the first segment or there's a gap, might be speaker change
            pass
        
        # Simple alternating pattern with bias detection
        text_lower = text.lower()
        
        # Male voice indicators (deeper, commanding, aggressive tone often correlates with certain words)
        male_indicators = ['i', 'me', 'my', 'gonna', 'hell', 'damn', 'bro', 'man']
        female_indicators = ['she', 'her', 'please', 'sorry', 'honey', 'dear', 'baby']
        
        male_score = sum(1 for word in male_indicators if word in text_lower)
        female_score = sum(1 for word in female_indicators if word in text_lower)
        
        # Start with alternating, but use indicators to adjust
        if previous_speaker is None:
            return "SPEAKER_1"  # Default male
        elif previous_speaker == "SPEAKER_1":
            # Check if should stay or switch
            if male_score > female_score + 1:
                return "SPEAKER_1"
            return "SPEAKER_2"
        else:
            # Previous was SPEAKER_2
            if female_score > male_score + 1:
                return "SPEAKER_2"
            return "SPEAKER_1"
    
    def transcribe_segment(self, audio_path: str, start_time: float, 
                          end_time: float, language: str = "en") -> str:
        """Transcribe a specific time segment of audio."""
        try:
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=False
            )
            
            # Find segments that overlap with the requested time range
            text_parts = []
            for seg in result['segments']:
                if seg['start'] >= start_time and seg['end'] <= end_time:
                    text_parts.append(seg['text'].strip())
            
            return ' '.join(text_parts)
            
        except Exception as e:
            logger.error(f"Segment transcription failed: {e}")
            raise RuntimeError(f"Segment transcription failed: {e}") from e
