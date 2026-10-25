"""Simple test to verify core services without GUI."""
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

def test_imports():
    """Test that core modules can be imported."""
    try:
        from src.models import DialogueSegment, VideoMetadata, Project
        print("✓ Models imported successfully")
        
        from src.services.ffmpeg_service import FFmpegService
        print("✓ FFmpeg service imported successfully")
        
        from src.services.omniroute_service import OmniRouteService
        print("✓ OmniRoute service imported successfully")
        
        from src.services.tts_service import TTSService
        print("✓ TTS service imported successfully")
        
        from src.services.subtitle_service import SubtitleService
        print("✓ Subtitle service imported successfully")
        
        from src.utils.config import config
        print("✓ Configuration imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_ffmpeg():
    """Test FFmpeg availability."""
    try:
        from src.services.ffmpeg_service import FFmpegService
        ffmpeg = FFmpegService()
        print("✓ FFmpeg service initialized successfully")
        return True
    except Exception as e:
        print(f"✗ FFmpeg test failed: {e}")
        return False


def test_models():
    """Test data models."""
    try:
        from src.models import DialogueSegment, VideoMetadata, AudioTrack, Project
        
        # Test DialogueSegment
        seg = DialogueSegment(
            start_time=0.0,
            end_time=5.0,
            english_text="Test"
        )
        assert seg.duration == 5.0
        print("✓ DialogueSegment works")
        
        # Test VideoMetadata
        audio = AudioTrack(index=0, codec="aac", sample_rate=48000, channels=2)
        meta = VideoMetadata(
            filepath="test.mp4",
            duration=120.0,
            width=1920,
            height=1080,
            fps=30.0,
            video_codec="h264",
            audio_tracks=[audio],
            format_name="mp4"
        )
        assert meta.resolution == "1920x1080"
        print("✓ VideoMetadata works")
        
        # Test Project
        project = Project(video_path="test.mp4")
        assert project.video_path == "test.mp4"
        print("✓ Project works")
        
        return True
    except Exception as e:
        print(f"✗ Models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subtitle_service():
    """Test subtitle generation."""
    try:
        from src.services.subtitle_service import SubtitleService
        from src.models import DialogueSegment
        
        segments = [
            DialogueSegment(
                start_time=0.0,
                end_time=2.5,
                english_text="Hello world",
                khmer_text="សួស្តីពិភពលោក"
            )
        ]
        
        service = SubtitleService()
        output_path = "temp/test_verify.srt"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        result = service.generate_srt(segments, output_path, use_khmer=True)
        
        if Path(result).exists():
            with open(result, 'r', encoding='utf-8') as f:
                content = f.read()
                if "សួស្តីពិភពលោក" in content:
                    print("✓ Subtitle service works (Khmer text preserved)")
                    Path(result).unlink()
                    return True
        
        print("✗ Subtitle generation failed")
        return False
        
    except Exception as e:
        print(f"✗ Subtitle service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("KhmerDub Studio - Core Functionality Verification")
    print("=" * 60)
    print()
    
    results = []
    
    print("Testing imports...")
    results.append(("Imports", test_imports()))
    print()
    
    print("Testing FFmpeg...")
    results.append(("FFmpeg", test_ffmpeg()))
    print()
    
    print("Testing data models...")
    results.append(("Models", test_models()))
    print()
    
    print("Testing subtitle service...")
    results.append(("Subtitles", test_subtitle_service()))
    print()
    
    print("=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    print()
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All core services are functional!")
        print("\nNote: GUI requires PySide6 with Windows Long Path support enabled.")
        print("See README.md for installation instructions.")
        return 0
    else:
        print("\n✗ Some tests failed. Check error messages above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
