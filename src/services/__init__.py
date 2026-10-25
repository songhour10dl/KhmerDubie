from .ffmpeg_service import FFmpegService
from .omniroute_service import OmniRouteService
from .tts_service import TTSService
from .subtitle_service import SubtitleService

# Import STT and pipeline separately to handle whisper dependency
try:
    from .stt_service import STTService
    _stt_available = True
except ImportError:
    _stt_available = False

# ProcessingPipeline can be imported even without STT (will lazy load)
from .processing_pipeline import ProcessingPipeline

if _stt_available:
    __all__ = [
        'FFmpegService',
        'STTService',
        'OmniRouteService',
        'TTSService',
        'SubtitleService',
        'ProcessingPipeline'
    ]
else:
    __all__ = [
        'FFmpegService',
        'OmniRouteService',
        'TTSService',
        'SubtitleService',
        'ProcessingPipeline'
    ]
