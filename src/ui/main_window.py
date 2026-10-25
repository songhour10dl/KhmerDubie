"""Main application window."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QTextEdit, QProgressBar, QMessageBox,
    QTabWidget, QSplitter, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPalette
from pathlib import Path
from typing import Optional
from ..services import ProcessingPipeline
from ..models import Project, DialogueSegment
from ..workers import TranscriptionWorker, TranslationWorker, TTSWorker, ExportWorker
from ..utils.config import config
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """KhmerDub Studio main window."""
    
    def __init__(self):
        super().__init__()
        self.pipeline = ProcessingPipeline()
        self.project: Optional[Project] = None
        self.current_worker = None
        
        self.init_ui()
        self.apply_dark_theme()
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("KhmerDub Studio - AI Video Dubbing")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_project_tab(), "Project")
        self.tabs.addTab(self.create_transcript_tab(), "Transcript")
        self.tabs.addTab(self.create_translation_tab(), "Translation")
        self.tabs.addTab(self.create_export_tab(), "Export")
        main_layout.addWidget(self.tabs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
    
    def create_header(self) -> QWidget:
        """Create application header."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        title = QLabel("KhmerDub Studio")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addStretch()
        
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)
        
        return widget
    
    def create_project_tab(self) -> QWidget:
        """Create project tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Video import section
        import_group = QGroupBox("Import Video")
        import_layout = QVBoxLayout(import_group)
        
        btn_layout = QHBoxLayout()
        self.import_btn = QPushButton("Select Video File")
        self.import_btn.clicked.connect(self.import_video)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addStretch()
        import_layout.addLayout(btn_layout)
        
        self.video_info_label = QLabel("No video loaded")
        import_layout.addWidget(self.video_info_label)
        
        layout.addWidget(import_group)
        
        # Metadata display
        metadata_group = QGroupBox("Video Metadata")
        metadata_layout = QVBoxLayout(metadata_group)
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setMaximumHeight(200)
        metadata_layout.addWidget(self.metadata_text)
        layout.addWidget(metadata_group)
        
        # Processing buttons
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout(process_group)
        
        self.transcribe_btn = QPushButton("1. Transcribe Audio")
        self.transcribe_btn.clicked.connect(self.start_transcription)
        self.transcribe_btn.setEnabled(False)
        process_layout.addWidget(self.transcribe_btn)
        
        self.translate_btn = QPushButton("2. Translate to Khmer")
        self.translate_btn.clicked.connect(self.start_translation)
        self.translate_btn.setEnabled(False)
        process_layout.addWidget(self.translate_btn)
        
        self.generate_speech_btn = QPushButton("3. Generate Khmer Speech")
        self.generate_speech_btn.clicked.connect(self.start_tts)
        self.generate_speech_btn.setEnabled(False)
        process_layout.addWidget(self.generate_speech_btn)
        
        layout.addWidget(process_group)
        layout.addStretch()
        
        return widget
    
    def create_transcript_tab(self) -> QWidget:
        """Create transcript editing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("English Transcript")
        label_font = QFont()
        label_font.setPointSize(12)
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        self.transcript_table = QTableWidget()
        self.transcript_table.setColumnCount(3)
        self.transcript_table.setHorizontalHeaderLabels(["Time", "Duration", "Text"])
        self.transcript_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.transcript_table)
        
        return widget
    
    def create_translation_tab(self) -> QWidget:
        """Create translation editing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Khmer Translation")
        label_font = QFont()
        label_font.setPointSize(12)
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        self.translation_table = QTableWidget()
        self.translation_table.setColumnCount(4)
        self.translation_table.setHorizontalHeaderLabels(["Time", "English", "Khmer", "Status"])
        self.translation_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.translation_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.translation_table)
        
        return widget
    
    def create_export_tab(self) -> QWidget:
        """Create export tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Export settings
        settings_group = QGroupBox("Export Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Path:"))
        self.output_path_label = QLabel("Not set")
        output_layout.addWidget(self.output_path_label)
        output_layout.addStretch()
        
        select_output_btn = QPushButton("Choose Output Location")
        select_output_btn.clicked.connect(self.select_output_path)
        output_layout.addWidget(select_output_btn)
        settings_layout.addLayout(output_layout)
        
        layout.addWidget(settings_group)
        
        # Export button
        self.export_btn = QPushButton("Export Dubbed Video")
        self.export_btn.setMinimumHeight(50)
        self.export_btn.clicked.connect(self.start_export)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        
        layout.addStretch()
        
        return widget
    
    def apply_dark_theme(self):
        """Apply dark theme to the application."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)
    
    def import_video(self):
        """Import a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            str(Path.home()),
            "Video Files (*.mp4 *.mkv *.mov *.avi);;All Files (*.*)"
        )
        
        if file_path:
            try:
                self.project = self.pipeline.create_project(file_path)
                self.update_video_info()
                self.transcribe_btn.setEnabled(True)
                self.status_label.setText(f"Video loaded: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load video: {str(e)}")
    
    def update_video_info(self):
        """Update video metadata display."""
        if not self.project or not self.project.metadata:
            return
        
        meta = self.project.metadata
        self.video_info_label.setText(f"Loaded: {Path(meta.filepath).name}")
        
        info_text = f"""
Duration: {meta.duration_str}
Resolution: {meta.resolution}
Frame Rate: {meta.fps:.2f} fps
Video Codec: {meta.video_codec}
Format: {meta.format_name}
Audio Tracks: {len(meta.audio_tracks)}
"""
        self.metadata_text.setPlainText(info_text.strip())
    
    def start_transcription(self):
        """Start transcription process."""
        if not self.project:
            return
        
        self.set_processing_state(True, "Transcribing...")
        self.current_worker = TranscriptionWorker(self.pipeline)
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_transcription_finished)
        self.current_worker.error.connect(self.on_worker_error)
        self.current_worker.start()
    
    def on_transcription_finished(self, segments):
        """Handle transcription completion."""
        self.set_processing_state(False, "Transcription complete")
        self.update_transcript_table(segments)
        self.translate_btn.setEnabled(True)
        self.tabs.setCurrentIndex(1)  # Switch to transcript tab
    
    def update_transcript_table(self, segments):
        """Update transcript table with segments."""
        self.transcript_table.setRowCount(len(segments))
        for idx, seg in enumerate(segments):
            self.transcript_table.setItem(idx, 0, QTableWidgetItem(f"{seg.start_time:.2f}s"))
            self.transcript_table.setItem(idx, 1, QTableWidgetItem(f"{seg.duration:.2f}s"))
            self.transcript_table.setItem(idx, 2, QTableWidgetItem(seg.english_text))
    
    def start_translation(self):
        """Start translation process."""
        if not self.project or not self.project.segments:
            return
        
        self.set_processing_state(True, "Translating...")
        self.current_worker = TranslationWorker(self.pipeline)
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_translation_finished)
        self.current_worker.error.connect(self.on_worker_error)
        self.current_worker.start()
    
    def on_translation_finished(self, segments):
        """Handle translation completion."""
        self.set_processing_state(False, "Translation complete")
        self.update_translation_table(segments)
        self.generate_speech_btn.setEnabled(True)
        self.tabs.setCurrentIndex(2)  # Switch to translation tab
    
    def update_translation_table(self, segments):
        """Update translation table with segments."""
        self.translation_table.setRowCount(len(segments))
        for idx, seg in enumerate(segments):
            self.translation_table.setItem(idx, 0, QTableWidgetItem(f"{seg.start_time:.2f}s"))
            self.translation_table.setItem(idx, 1, QTableWidgetItem(seg.english_text))
            self.translation_table.setItem(idx, 2, QTableWidgetItem(seg.khmer_text or ""))
            status = "✓" if seg.khmer_text else "✗"
            self.translation_table.setItem(idx, 3, QTableWidgetItem(status))
    
    def start_tts(self):
        """Start TTS generation process."""
        if not self.project or not self.project.segments:
            return
        
        self.set_processing_state(True, "Generating speech...")
        self.current_worker = TTSWorker(self.pipeline)
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_tts_finished)
        self.current_worker.error.connect(self.on_worker_error)
        self.current_worker.start()
    
    def on_tts_finished(self, segments):
        """Handle TTS completion."""
        self.set_processing_state(False, "Speech generation complete")
        self.update_translation_table(segments)
        self.export_btn.setEnabled(True)
        self.tabs.setCurrentIndex(3)  # Switch to export tab
    
    def select_output_path(self):
        """Select output file path."""
        if not self.project:
            return
        
        default_name = Path(self.project.video_path).stem + "_dubbed.mp4"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Dubbed Video",
            str(config.output_dir / default_name),
            "MP4 Video (*.mp4);;All Files (*.*)"
        )
        
        if file_path:
            self.output_path_label.setText(file_path)
            self.project.output_path = file_path
    
    def start_export(self):
        """Start export process."""
        if not self.project or not self.project.output_path:
            QMessageBox.warning(self, "Warning", "Please select an output path first")
            return
        
        self.set_processing_state(True, "Exporting...")
        self.current_worker = ExportWorker(
            self.pipeline,
            self.project.output_path,
            mix_original=True,
            original_volume=0.1,
            generate_subtitles=True
        )
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_export_finished)
        self.current_worker.error.connect(self.on_worker_error)
        self.current_worker.start()
    
    def on_export_finished(self, output_path):
        """Handle export completion."""
        self.set_processing_state(False, "Export complete")
        QMessageBox.information(
            self,
            "Success",
            f"Video dubbed successfully!\n\nOutput: {output_path}"
        )
    
    def update_progress(self, message: str, percentage: int):
        """Update progress bar and status."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
    
    def set_processing_state(self, processing: bool, message: str = ""):
        """Enable/disable UI during processing."""
        self.progress_bar.setVisible(processing)
        if not processing:
            self.progress_bar.setValue(0)
        
        self.import_btn.setEnabled(not processing)
        self.transcribe_btn.setEnabled(not processing and self.project is not None)
        self.translate_btn.setEnabled(not processing and self.project and len(self.project.segments) > 0)
        self.generate_speech_btn.setEnabled(not processing and self.project and any(s.khmer_text for s in self.project.segments))
        
        if message:
            self.status_label.setText(message)
    
    def on_worker_error(self, error_msg: str):
        """Handle worker errors."""
        self.set_processing_state(False, "Error occurred")
        QMessageBox.critical(self, "Error", f"Processing failed:\n\n{error_msg}")
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Settings saved
            self.status_label.setText("Settings saved")
