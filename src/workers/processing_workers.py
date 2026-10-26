"""Enhanced background worker threads with pause/stop/continue support."""
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from typing import List, Optional
from ..services.processing_pipeline import ProcessingPipeline
from ..models import DialogueSegment


class CancellableWorker(QThread):
    """Base worker with pause/stop/continue support."""
    
    progress = Signal(str, int)
    error = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._is_paused = False
        self._is_stopped = False
        self._mutex = QMutex()
        self._pause_condition = QWaitCondition()
    
    def pause(self):
        """Pause the worker."""
        self._mutex.lock()
        self._is_paused = True
        self._mutex.unlock()
        self.progress.emit("Paused", 0)
    
    def resume(self):
        """Resume the worker."""
        self._mutex.lock()
        self._is_paused = False
        self._pause_condition.wakeAll()
        self._mutex.unlock()
        self.progress.emit("Resumed", 0)
    
    def stop(self):
        """Stop the worker."""
        self._mutex.lock()
        self._is_stopped = True
        self._is_paused = False
        self._pause_condition.wakeAll()
        self._mutex.unlock()
    
    def check_pause_stop(self):
        """Check if paused or stopped. Returns True if should continue."""
        self._mutex.lock()
        
        # Check if stopped
        if self._is_stopped:
            self._mutex.unlock()
            return False
        
        # Wait while paused
        while self._is_paused and not self._is_stopped:
            self._pause_condition.wait(self._mutex)
        
        stopped = self._is_stopped
        self._mutex.unlock()
        
        return not stopped


class TranscriptionWorker(CancellableWorker):
    """Worker thread for audio transcription with pause/stop support."""
    
    finished = Signal(list)  # List[DialogueSegment]
    
    def __init__(self, pipeline: ProcessingPipeline):
        super().__init__()
        self.pipeline = pipeline
    
    def run(self):
        """Execute transcription task."""
        try:
            def progress_callback(msg, pct):
                if not self.check_pause_stop():
                    raise InterruptedError("Transcription stopped by user")
                self.progress.emit(msg, pct)
            
            segments = self.pipeline.extract_and_transcribe(
                progress_callback=progress_callback
            )
            
            if self._is_stopped:
                self.error.emit("Transcription stopped by user")
            else:
                self.finished.emit(segments)
        except InterruptedError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(str(e))


class TranslationWorker(CancellableWorker):
    """Worker thread for translation with pause/stop support."""
    
    finished = Signal(list)  # List[DialogueSegment]
    
    def __init__(self, pipeline: ProcessingPipeline, segments: List[DialogueSegment] = None):
        super().__init__()
        self.pipeline = pipeline
        self.segments = segments
    
    def run(self):
        """Execute translation task."""
        try:
            def progress_callback(msg, pct):
                if not self.check_pause_stop():
                    raise InterruptedError("Translation stopped by user")
                self.progress.emit(msg, pct)
            
            segments = self.pipeline.translate_segments(
                segments=self.segments,
                progress_callback=progress_callback
            )
            
            if self._is_stopped:
                self.error.emit("Translation stopped by user")
            else:
                self.finished.emit(segments)
        except InterruptedError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(str(e))
        finally:
            # Ensure thread cleanup
            self.quit()
            self.wait()


class TTSWorker(CancellableWorker):
    """Worker thread for TTS generation with pause/stop support."""
    
    finished = Signal(list)  # List[DialogueSegment]
    
    def __init__(self, pipeline: ProcessingPipeline, segments: List[DialogueSegment] = None):
        super().__init__()
        self.pipeline = pipeline
        self.segments = segments
    
    def run(self):
        """Execute TTS generation task."""
        try:
            def progress_callback(msg, pct):
                if not self.check_pause_stop():
                    raise InterruptedError("TTS generation stopped by user")
                self.progress.emit(msg, pct)
            
            segments = self.pipeline.generate_speech(
                segments=self.segments,
                progress_callback=progress_callback
            )
            
            if self._is_stopped:
                self.error.emit("TTS generation stopped by user")
            else:
                self.finished.emit(segments)
        except InterruptedError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(str(e))
        finally:
            # Ensure thread cleanup
            self.quit()
            self.wait()


class ExportWorker(CancellableWorker):
    """Worker thread for video export with pause/stop support."""
    
    finished = Signal(str)  # output path
    
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
            def progress_callback(msg, pct):
                if not self.check_pause_stop():
                    raise InterruptedError("Export stopped by user")
                self.progress.emit(msg, pct)
            
            output = self.pipeline.export_video(
                self.output_path,
                mix_original=self.mix_original,
                original_volume=self.original_volume,
                generate_subtitles=self.generate_subtitles,
                progress_callback=progress_callback
            )
            
            if self._is_stopped:
                self.error.emit("Export stopped by user")
            else:
                self.finished.emit(output)
        except InterruptedError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(str(e))
        finally:
            # Ensure thread cleanup
            self.quit()
            self.wait()
