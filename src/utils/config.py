"""Configuration management."""
import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Application configuration."""
    
    def __init__(self):
        # Load .env file
        load_dotenv()
        
        # OmniRoute
        self.omniroute_base_url = os.getenv('OMNIROUTE_BASE_URL', 'http://localhost:8000')
        self.omniroute_api_key = os.getenv('OMNIROUTE_API_KEY', '')
        self.omniroute_model = os.getenv('OMNIROUTE_MODEL', 'gpt-4')
        
        # STT
        self.stt_provider = os.getenv('STT_PROVIDER', 'whisper')
        self.stt_api_key = os.getenv('STT_API_KEY', '')
        self.stt_model = os.getenv('STT_MODEL', 'base')
        
        # TTS
        self.tts_provider = os.getenv('TTS_PROVIDER', 'kiri')
        self.tts_api_key = os.getenv('TTS_API_KEY', '')
        self.tts_voice = os.getenv('TTS_VOICE', 'khmer_female_1')
        self.tts_base_url = os.getenv('TTS_BASE_URL', 'https://api.kiri.ai/v1')
        
        # Processing
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '3'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '300'))
        
        # Paths
        self.temp_dir = Path(os.getenv('TEMP_DIR', './temp'))
        self.output_dir = Path(os.getenv('OUTPUT_DIR', './output'))
        
        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg
        self.ffmpeg_path = os.getenv('FFMPEG_PATH', 'ffmpeg')
        self.ffprobe_path = os.getenv('FFPROBE_PATH', 'ffprobe')
        
        # Audio settings
        self.audio_codec = os.getenv('AUDIO_CODEC', 'aac')
        self.audio_bitrate = os.getenv('AUDIO_BITRATE', '128k')
        self.audio_sample_rate = int(os.getenv('AUDIO_SAMPLE_RATE', '48000'))
    
    def save_to_env(self, env_path: str = '.env') -> None:
        """Save current configuration to .env file."""
        env_content = f"""# OmniRoute Configuration
OMNIROUTE_BASE_URL={self.omniroute_base_url}
OMNIROUTE_API_KEY={self.omniroute_api_key}
OMNIROUTE_MODEL={self.omniroute_model}

# Speech-to-Text Provider
STT_PROVIDER={self.stt_provider}
STT_API_KEY={self.stt_api_key}
STT_MODEL={self.stt_model}

# Text-to-Speech Provider (Khmer)
TTS_PROVIDER={self.tts_provider}
TTS_API_KEY={self.tts_api_key}
TTS_VOICE={self.tts_voice}
TTS_BASE_URL={self.tts_base_url}

# Processing Settings
MAX_CONCURRENT_REQUESTS={self.max_concurrent_requests}
REQUEST_TIMEOUT={self.request_timeout}
TEMP_DIR={self.temp_dir}
OUTPUT_DIR={self.output_dir}

# FFmpeg Settings
FFMPEG_PATH={self.ffmpeg_path}
FFPROBE_PATH={self.ffprobe_path}

# Audio Settings
AUDIO_CODEC={self.audio_codec}
AUDIO_BITRATE={self.audio_bitrate}
AUDIO_SAMPLE_RATE={self.audio_sample_rate}
"""
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)


# Global config instance
config = Config()
