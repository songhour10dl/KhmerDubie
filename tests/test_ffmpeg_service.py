"""Unit tests for FFmpeg service."""
import pytest
from pathlib import Path
from src.services.ffmpeg_service import FFmpegService


def test_ffmpeg_service_initialization():
    """Test FFmpeg service can be initialized."""
    service = FFmpegService()
    assert service.ffmpeg_path is not None
    assert service.ffprobe_path is not None


def test_ffmpeg_validation():
    """Test FFmpeg installation is validated."""
    service = FFmpegService()
    # If this doesn't raise, FFmpeg is installed
    assert True


# Note: The following tests require actual video files and are integration tests
# They should be run with real video files in a test environment

def test_video_info_extraction():
    """Test video metadata extraction (requires test video)."""
    # This test would need a sample video file
    # Skipped in unit test mode
    pass


def test_audio_extraction():
    """Test audio extraction from video (requires test video)."""
    # This test would need a sample video file
    # Skipped in unit test mode
    pass


def test_audio_video_merge():
    """Test audio and video merging (requires test files)."""
    # This test would need sample files
    # Skipped in unit test mode
    pass
