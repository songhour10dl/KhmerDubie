"""Background worker threads for long-running tasks."""
from PySide6.QtCore import QThread, Signal
from typing import List, Optional
from ..services.processing_pipeline import ProcessingPipeline
from ..models import DialogueSegment


class TranscriptionWorker(QThread):
    """Worker thread for audio transcription."""
    
    progress = Signal(str, int)  # message, percentage
    finished = Signal(list)  # List[DialogueSegment]
    error = Signal(str)
    
    def __init__(self, pipeline: ProcessingPipeline):
        super().__init__()
        self.pipeline = pipeline
    
    def run(self):
        """Execute transcription task."""
        try:
            segments = self.pipeline.extract_and_transcribe(
                progress_callback=lambda msg, pct: self.progress.emit(msg, pct)
            )
            self.finished.emit(segments)
        except Exception as e:
            self.error.emit(str(e))


class TranslationWorker(QThread):
    """Worker thread for translation."""
    
    progress = Signal(str, int)  # message, percentage
    finished = Signal(list)  # List[DialogueSegment]
    error = Signal(str)
    
    def __init__(self, pipeline: ProcessingPipeline, segments: List[DialogueSegment] = None):
        super().__init__()
        self.pipeline = pipeline
        self.segments = segments
    
    def run(self):
        """Execute translation task."""
        try:
            segments = self.pipeline.translate_segments(
                segments=self.segments,
                progress_callback=lambda msg, pct: self.progress.emit(msg, pct)
            )
            self.finished.emit(segments)
        except Exception as e:
            self.error.emit(str(e))


class TTSWorker(QThread):
    """Worker thread for text-to-speech generation."""
    
    progress = Signal(str, int)  # message, percentage
    finished = Signal(list)  # List[DialogueSegment]
    error = Signal(str)
    
    def __init__(self, pipeline: ProcessingPipeline, segments: List[DialogueSegment] = None):
        super().__init__()
        self.pipeline = pipeline
        self.segments = segments
    
    def run(self):
        """Execute TTS generation task."""
        try:
            segments = self.pipeline.generate_speech(
                segments=self.segments,
                progress_callback=lambda msg, pct: self.progress.emit(msg, pct)
            )
            self.finished.emit(segments)
        except Exception as e:
            self.error.emit(str(e))


class ExportWorker(QThread):
    """Worker thread for video export."""
    
    progress = Signal(str, int)  # message, percentage
    finished = Signal(str)  # output path
    error = Signal(str)
    
    def __init__(self, pipeline: ProcessingPipeline, output_path: str,
                 mix_original: bool = True, original_volume: float = 0.1,
                 generate_subtitles: bool = True):
        super().__init__()
        self.pipeline = pipeline
        self.output_path = output_path
        self.mix_original = mix_original
        self.original_volume = original_volume
        self.generate_subtitles = generate_subtitles
    
    def run(self):
        """Execute export task."""
        try:
            output = self.pipeline.export_video(
                self.output_path,
                mix_original=self.mix_original,
                original_volume=self.original_volume,
                generate_subtitles=self.generate_subtitles,
                progress_callback=lambda msg, pct: self.progress.emit(msg, pct)
            )
            self.finished.emit(output)
        except Exception as e:
            self.error.emit(str(e))
