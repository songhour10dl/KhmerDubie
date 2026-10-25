"""Unit tests for subtitle service."""
import pytest
from pathlib import Path
from src.services.subtitle_service import SubtitleService
from src.models.dialogue_segment import DialogueSegment


def test_srt_generation():
    """Test SRT subtitle file generation."""
    segments = [
        DialogueSegment(
            start_time=0.0,
            end_time=2.5,
            english_text="Hello world",
            khmer_text="សួស្តីពិភពលោក"
        ),
        DialogueSegment(
            start_time=3.0,
            end_time=5.0,
            english_text="How are you?",
            khmer_text="អ្នកសុខសប្បាយទេ?"
        )
    ]
    
    service = SubtitleService()
    output_path = "temp/test_output.srt"
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    result = service.generate_srt(segments, output_path, use_khmer=True)
    
    assert Path(result).exists()
    
    # Check content
    with open(result, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "សួស្តីពិភពលោក" in content
        assert "អ្នកសុខសប្បាយទេ?" in content
        assert "00:00:00,000 --> 00:00:02,500" in content
    
    # Cleanup
    Path(result).unlink()


def test_srt_time_formatting():
    """Test SRT time format is correct."""
    segment = DialogueSegment(
        start_time=65.5,  # 1:05.5
        end_time=125.750,  # 2:05.750
        english_text="Test"
    )
    
    assert segment.start_time_srt == "00:01:05,500"
    assert segment.end_time_srt == "00:02:05,750"


def test_dual_subtitle_generation():
    """Test dual language subtitle generation."""
    segments = [
        DialogueSegment(
            start_time=0.0,
            end_time=2.0,
            english_text="Hello",
            khmer_text="សួស្តី"
        )
    ]
    
    service = SubtitleService()
    output_path = "temp/test_dual.srt"
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    result = service.generate_dual_srt(segments, output_path)
    
    assert Path(result).exists()
    
    with open(result, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Hello" in content
        assert "សួស្តី" in content
    
    # Cleanup
    Path(result).unlink()
