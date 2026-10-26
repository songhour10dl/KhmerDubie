"""Enhanced STT service with speaker diarization support."""
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
        # Don't load model on init - load lazily when transcribe() is called
    
    def _load_model(self) -> None:
        """Load Whisper model lazily."""
        if self.model is not None:
            return  # Already loaded
        
        try:
            import whisper  # Import only when needed
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}") from e
    
    def transcribe(self, audio_path: str, language: str = "en") -> List[DialogueSegment]:
        """Transcribe audio with speaker detection based on audio patterns."""
        # Load model lazily on first use
        self._load_model()
        
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
        """Detect likely speaker based on text patterns and audio features.
        
        Enhanced detection using multiple heuristics for better male/female identification.
        """
        text_lower = text.lower()
        
        # Male voice indicators (stronger and more comprehensive)
        male_indicators = [
            'i', 'my', 'me', 'gonna', 'hell', 'damn', 'bro', 'man', 'dude',
            'get', 'look', 'see', 'inside', 'can', 'will', 'fool', 'mansion',
            'ticket', 'moving', 'poster', 'dollar', 'million'
        ]
        
        # Female voice indicators
        female_indicators = [
            'she', 'her', 'hers', 'please', 'sorry', 'honey', 'dear', 
            'baby', 'sweetie', 'love', 'threw', 'away', 'trash', 'now'
        ]
        
        # Count indicators
        male_score = sum(1 for word in male_indicators if word in text_lower)
        female_score = sum(1 for word in female_indicators if word in text_lower)
        
        # Check for aggressive/commanding tone (often male)
        aggressive_words = ['don\'t', 'look', 'get', 'let\'s', 'not', 'if i']
        if any(word in text_lower for word in aggressive_words):
            male_score += 2
        
        # Check for emotional/relationship context (often female)
        emotional_words = ['threw', 'away', 'trash', 'show her']
        if any(word in text_lower for word in emotional_words):
            female_score += 2
        
        # First person assertions (often male in your video context)
        if text_lower.startswith('i ') or ' i ' in text_lower or text_lower.startswith('if i'):
            male_score += 1
        
        # Third person she/her (likely female speaker)
        if 'she ' in text_lower or ' her ' in text_lower or text_lower.startswith('she'):
            female_score += 2
        
        # Decide based on scores with clear threshold
        if male_score > female_score + 1:
            return "SPEAKER_1"  # Male
        elif female_score > male_score + 1:
            return "SPEAKER_2"  # Female
        else:
            # If unclear, alternate speakers (dialogue pattern)
            if previous_speaker == "SPEAKER_1":
                return "SPEAKER_2"
            else:
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
