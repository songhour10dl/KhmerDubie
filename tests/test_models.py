"""Unit tests for data models."""
import pytest
from src.models import DialogueSegment, VideoMetadata, AudioTrack, Project


def test_dialogue_segment_creation():
    """Test dialogue segment can be created."""
    segment = DialogueSegment(
        start_time=0.0,
        end_time=5.0,
        english_text="Test dialogue"
    )
    assert segment.start_time == 0.0
    assert segment.end_time == 5.0
    assert segment.duration == 5.0
    assert segment.english_text == "Test dialogue"
    assert segment.segment_id is not None


def test_dialogue_segment_duration():
    """Test duration calculation."""
    segment = DialogueSegment(start_time=10.5, end_time=15.75, english_text="Test")
    assert segment.duration == 5.25


def test_video_metadata_creation():
    """Test video metadata can be created."""
    audio = AudioTrack(index=0, codec="aac", sample_rate=48000, channels=2)
    metadata = VideoMetadata(
        filepath="test.mp4",
        duration=120.0,
        width=1920,
        height=1080,
        fps=30.0,
        video_codec="h264",
        audio_tracks=[audio],
        format_name="mp4"
    )
    assert metadata.resolution == "1920x1080"
    assert metadata.duration_str == "00:02:00"


def test_project_creation():
    """Test project can be created and saved."""
    project = Project(video_path="test.mp4")
    assert project.video_path == "test.mp4"
    assert len(project.segments) == 0


def test_project_with_segments():
    """Test project with segments."""
    segments = [
        DialogueSegment(start_time=0.0, end_time=2.0, english_text="Test 1"),
        DialogueSegment(start_time=2.0, end_time=4.0, english_text="Test 2")
    ]
    project = Project(video_path="test.mp4", segments=segments)
    assert len(project.segments) == 2
