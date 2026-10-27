"""Main application window."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QTextEdit, QProgressBar, QMessageBox,
    QTabWidget, QSplitter, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFormLayout, QComboBox, QRadioButton, QCheckBox
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QColor, QPalette
from pathlib import Path
from typing import Optional
from ..services import ProcessingPipeline
from ..models import Project, DialogueSegment
from ..workers import TranscriptionWorker, TranslationWorker, TTSWorker, ExportWorker
from ..utils.config import config
from ..utils.logger import setup_logger
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """KhmerDub Studio main window."""
    
    def __init__(self):
        super().__init__()
        # Force reload config to ensure latest settings from .env
        config.reload()
        
        # Read translation provider from config
        self.translation_provider = getattr(config, 'translation_provider', 'hybrid')
        
        # Get manual dictionary path for hybrid mode
        manual_dict_path = getattr(config, 'manual_dict_path', 'translations.json')
        
        # Log for debugging
        logger = setup_logger(__name__)
        logger.info(f"MainWindow initialized with translation_provider={self.translation_provider}, manual_dict={manual_dict_path}")
        
        # Initialize pipeline with config settings
        self.pipeline = ProcessingPipeline(
            translation_provider=self.translation_provider,
            manual_dict_path=manual_dict_path
        )
        
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
        self.metadata_text.setMaximumHeight(150)
        metadata_layout.addWidget(self.metadata_text)
        layout.addWidget(metadata_group)
        
        # Voice Mode Selection
        mode_group = QGroupBox("Voice Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        mode_radio_layout = QHBoxLayout()
        
        self.voice_mode_auto = QRadioButton("Auto-Detect Male/Female")
        self.voice_mode_auto.setChecked(True)
        self.voice_mode_auto.toggled.connect(self.on_voice_mode_changed)
        mode_radio_layout.addWidget(self.voice_mode_auto)
        
        self.voice_mode_single = QRadioButton("Use Single Voice")
        self.voice_mode_single.toggled.connect(self.on_voice_mode_changed)
        mode_radio_layout.addWidget(self.voice_mode_single)
        
        mode_layout.addLayout(mode_radio_layout)
        
        # Single voice selection
        self.single_voice_group = QGroupBox("Choose Voice (Single Mode)")
        self.single_voice_group.setEnabled(False)
        single_voice_layout = QFormLayout(self.single_voice_group)
        
        self.single_voice_combo = QComboBox()
        self.single_voice_combo.addItems([
            "km-KH-SreymomNeural (Female)",
            "km-KH-PisethNeural (Male)"
        ])
        single_voice_layout.addRow("Voice:", self.single_voice_combo)
        
        mode_layout.addWidget(self.single_voice_group)
        layout.addWidget(mode_group)
        
        # Voice assignment section (only for auto-detect mode)
        self.voice_assign_group = QGroupBox("Voice Assignment (Auto-Detect Mode)")
        voice_layout = QFormLayout(self.voice_assign_group)
        
        self.speaker1_voice = QComboBox()
        self.speaker1_voice.addItems([
            "km-KH-PisethNeural (Male)",
            "km-KH-SreymomNeural (Female)"
        ])
        self.speaker1_voice.setCurrentIndex(0)  # Male default
        voice_layout.addRow("Speaker 1 (Usually Male):", self.speaker1_voice)
        
        self.speaker2_voice = QComboBox()
        self.speaker2_voice.addItems([
            "km-KH-SreymomNeural (Female)",
            "km-KH-PisethNeural (Male)"
        ])
        self.speaker2_voice.setCurrentIndex(0)  # Female default
        voice_layout.addRow("Speaker 2 (Usually Female):", self.speaker2_voice)
        
        self.voice_assign_group.setLayout(voice_layout)
        layout.addWidget(self.voice_assign_group)
        
        # Processing buttons
        process_group = QGroupBox("Processing")
        process_layout = QVBoxLayout(process_group)
        
        # Auto-run checkbox
        auto_run_layout = QHBoxLayout()
        self.auto_run_checkbox = QCheckBox("Auto-Run All Steps (Transcribe → Translate → Generate Speech)")
        self.auto_run_checkbox.setStyleSheet("QCheckBox { font-weight: bold; color: #2ECC71; }")
        auto_run_layout.addWidget(self.auto_run_checkbox)
        auto_run_layout.addStretch()
        process_layout.addLayout(auto_run_layout)
        
        # Transcribe section
        transcribe_layout = QHBoxLayout()
        self.transcribe_btn = QPushButton("1. Transcribe Audio")
        self.transcribe_btn.clicked.connect(self.start_transcription)
        self.transcribe_btn.setEnabled(False)
        transcribe_layout.addWidget(self.transcribe_btn)
        
        self.transcribe_pause_btn = QPushButton("Pause")
        self.transcribe_pause_btn.clicked.connect(self.pause_transcription)
        self.transcribe_pause_btn.setEnabled(False)
        transcribe_layout.addWidget(self.transcribe_pause_btn)
        
        self.transcribe_stop_btn = QPushButton("Stop")
        self.transcribe_stop_btn.clicked.connect(self.stop_transcription)
        self.transcribe_stop_btn.setEnabled(False)
        transcribe_layout.addWidget(self.transcribe_stop_btn)
        
        process_layout.addLayout(transcribe_layout)
        
        # Translate section
        translate_layout = QHBoxLayout()
        self.translate_btn = QPushButton("2. Translate to Khmer")
        self.translate_btn.clicked.connect(self.start_translation)
        self.translate_btn.setEnabled(False)
        translate_layout.addWidget(self.translate_btn)
        
        self.translate_pause_btn = QPushButton("Pause")
        self.translate_pause_btn.clicked.connect(self.pause_translation)
        self.translate_pause_btn.setEnabled(False)
        translate_layout.addWidget(self.translate_pause_btn)
        
        self.translate_stop_btn = QPushButton("Stop")
        self.translate_stop_btn.clicked.connect(self.stop_translation)
        self.translate_stop_btn.setEnabled(False)
        translate_layout.addWidget(self.translate_stop_btn)
        
        process_layout.addLayout(translate_layout)
        
        # TTS section
        tts_layout = QHBoxLayout()
        self.generate_speech_btn = QPushButton("3. Generate Khmer Speech")
        self.generate_speech_btn.clicked.connect(self.start_tts)
        self.generate_speech_btn.setEnabled(False)
        tts_layout.addWidget(self.generate_speech_btn)
        
        self.tts_pause_btn = QPushButton("Pause")
        self.tts_pause_btn.clicked.connect(self.pause_tts)
        self.tts_pause_btn.setEnabled(False)
        tts_layout.addWidget(self.tts_pause_btn)
        
        self.tts_stop_btn = QPushButton("Stop")
        self.tts_stop_btn.clicked.connect(self.stop_tts)
        self.tts_stop_btn.setEnabled(False)
        tts_layout.addWidget(self.tts_stop_btn)
        
        process_layout.addLayout(tts_layout)
        
        layout.addWidget(process_group)
        layout.addStretch()
        
        return widget
    
    def create_transcript_tab(self) -> QWidget:
        """Create transcript editing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("English Transcript with Speaker Detection")
        label_font = QFont()
        label_font.setPointSize(12)
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        self.transcript_table = QTableWidget()
        self.transcript_table.setColumnCount(4)
        self.transcript_table.setHorizontalHeaderLabels(["Time", "Duration", "Speaker", "Text"])
        self.transcript_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.transcript_table)
        
        return widget
    
    def create_translation_tab(self) -> QWidget:
        """Create translation editing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Khmer Translation with Voice Assignment")
        label_font = QFont()
        label_font.setPointSize(12)
        label_font.setBold(True)
        label.setFont(label_font)
        layout.addWidget(label)
        
        self.translation_table = QTableWidget()
        self.translation_table.setColumnCount(5)
        self.translation_table.setHorizontalHeaderLabels(["Time", "Speaker", "English", "Khmer", "Status"])
        self.translation_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.translation_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
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
        self.transcribe_pause_btn.setEnabled(True)
        self.transcribe_stop_btn.setEnabled(True)
        
        self.current_worker = TranscriptionWorker(self.pipeline)
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_transcription_finished)
        self.current_worker.error.connect(self.on_worker_error)
        self.current_worker.start()
    
    def pause_transcription(self):
        """Pause/resume transcription."""
        if self.current_worker and isinstance(self.current_worker, TranscriptionWorker):
            if self.transcribe_pause_btn.text() == "Pause":
                self.current_worker.pause()
                self.transcribe_pause_btn.setText("Resume")
            else:
                self.current_worker.resume()
                self.transcribe_pause_btn.setText("Pause")
    
    def stop_transcription(self):
        """Stop transcription."""
        if self.current_worker and isinstance(self.current_worker, TranscriptionWorker):
            self.current_worker.stop()
            self.transcribe_pause_btn.setEnabled(False)
            self.transcribe_stop_btn.setEnabled(False)
            self.transcribe_pause_btn.setText("Pause")
    
    def on_transcription_finished(self, segments):
        """Handle transcription completion."""
        # Clean up thread from main thread (prevents deadlock)
        if self.current_worker:
            self.current_worker.quit()
            self.current_worker.wait()
        
        self.set_processing_state(False, "Transcription complete")
        self.transcribe_pause_btn.setEnabled(False)
        self.transcribe_stop_btn.setEnabled(False)
        self.transcribe_pause_btn.setText("Pause")
        self.update_transcript_table(segments)
        self.translate_btn.setEnabled(True)
        
        # Auto-run: proceed to translation using timer to avoid deadlock
        if self.auto_run_checkbox.isChecked():
            self.status_label.setText("Auto-run enabled: Starting translation...")
            QTimer.singleShot(100, self._start_translation_auto)
        else:
            self.tabs.setCurrentIndex(1)  # Switch to transcript tab
    
    def _start_translation_auto(self):
        """Helper method for auto-run translation (called from main thread)."""
        if not self.auto_run_checkbox.isChecked():
            return
        self.start_translation()
    
    def update_transcript_table(self, segments):
        """Update transcript table with segments and speaker info."""
        self.transcript_table.setColumnCount(4)
        self.transcript_table.setHorizontalHeaderLabels(["Time", "Duration", "Speaker", "Text"])
        self.transcript_table.setRowCount(len(segments))
        
        for idx, seg in enumerate(segments):
            self.transcript_table.setItem(idx, 0, QTableWidgetItem(f"{seg.start_time:.2f}s"))
            self.transcript_table.setItem(idx, 1, QTableWidgetItem(f"{seg.duration:.2f}s"))
            
            speaker_text = seg.speaker or "Unknown"
            if seg.speaker == "SPEAKER_1":
                speaker_text += " (Male)"
            elif seg.speaker == "SPEAKER_2":
                speaker_text += " (Female)"
            self.transcript_table.setItem(idx, 2, QTableWidgetItem(speaker_text))
            self.transcript_table.setItem(idx, 3, QTableWidgetItem(seg.english_text))
        
        self.transcript_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
    
    def start_translation(self):
        """Start translation process."""
        if not self.project or not self.project.segments:
            return
        
        self.set_processing_state(True, "Translating (parallel processing)...")
        self.translate_pause_btn.setEnabled(True)
        self.translate_stop_btn.setEnabled(True)
        
        self.current_worker = TranslationWorker(self.pipeline)
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_translation_finished)
        self.current_worker.error.connect(self.on_worker_error)
        self.current_worker.start()
    
    def pause_translation(self):
        """Pause/resume translation."""
        if self.current_worker and isinstance(self.current_worker, TranslationWorker):
            if self.translate_pause_btn.text() == "Pause":
                self.current_worker.pause()
                self.translate_pause_btn.setText("Resume")
            else:
                self.current_worker.resume()
                self.translate_pause_btn.setText("Pause")
    
    def stop_translation(self):
        """Stop translation."""
        if self.current_worker and isinstance(self.current_worker, TranslationWorker):
            self.current_worker.stop()
            self.translate_pause_btn.setEnabled(False)
            self.translate_stop_btn.setEnabled(False)
            self.translate_pause_btn.setText("Pause")
    
    def on_translation_finished(self, segments):
        """Handle translation completion."""
        # Clean up thread from main thread (prevents deadlock)
        if self.current_worker:
            self.current_worker.quit()
            self.current_worker.wait()
        
        self.set_processing_state(False, "Translation complete")
        self.translate_pause_btn.setEnabled(False)
        self.translate_stop_btn.setEnabled(False)
        self.translate_pause_btn.setText("Pause")
        self.update_translation_table(segments)
        self.generate_speech_btn.setEnabled(True)
        
        # Auto-run: proceed to TTS generation using timer
        if self.auto_run_checkbox.isChecked():
            self.status_label.setText("Auto-run enabled: Starting TTS generation...")
            QTimer.singleShot(100, self._start_tts_auto)
        else:
            self.tabs.setCurrentIndex(2)  # Switch to translation tab
    
    def _start_tts_auto(self):
        """Helper method for auto-run TTS (called from main thread)."""
        if not self.auto_run_checkbox.isChecked():
            return
        self.start_tts()
    
    def update_translation_table(self, segments):
        """Update translation table with segments and voice info."""
        self.translation_table.setColumnCount(5)
        self.translation_table.setHorizontalHeaderLabels(["Time", "Speaker", "English", "Khmer", "Status"])
        self.translation_table.setRowCount(len(segments))
        
        for idx, seg in enumerate(segments):
            self.translation_table.setItem(idx, 0, QTableWidgetItem(f"{seg.start_time:.2f}s"))
            
            speaker_text = seg.speaker or "Unknown"
            if seg.speaker == "SPEAKER_1":
                speaker_text += " (♂)"
            elif seg.speaker == "SPEAKER_2":
                speaker_text += " (♀)"
            self.translation_table.setItem(idx, 1, QTableWidgetItem(speaker_text))
            
            self.translation_table.setItem(idx, 2, QTableWidgetItem(seg.english_text))
            self.translation_table.setItem(idx, 3, QTableWidgetItem(seg.khmer_text or ""))
            
            status = "✓" if seg.khmer_text and seg.audio_path else "✓" if seg.khmer_text else "✗"
            self.translation_table.setItem(idx, 4, QTableWidgetItem(status))
        
        self.translation_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.translation_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
    
    def on_voice_mode_changed(self):
        """Handle voice mode toggle between auto-detect and single voice."""
        if self.voice_mode_auto.isChecked():
            self.voice_assign_group.setEnabled(True)
            self.single_voice_group.setEnabled(False)
        else:
            self.voice_assign_group.setEnabled(False)
            self.single_voice_group.setEnabled(True)
    
    def on_voice_mode_changed(self):
        """Handle voice mode toggle between auto-detect and single voice."""
        if self.voice_mode_auto.isChecked():
            self.voice_assign_group.setEnabled(True)
            self.single_voice_group.setEnabled(False)
        else:
            self.voice_assign_group.setEnabled(False)
            self.single_voice_group.setEnabled(True)
    
    def pause_tts(self):
        """Pause/resume TTS."""
        if self.current_worker and isinstance(self.current_worker, TTSWorker):
            if self.tts_pause_btn.text() == "Pause":
                self.current_worker.pause()
                self.tts_pause_btn.setText("Resume")
            else:
                self.current_worker.resume()
                self.tts_pause_btn.setText("Pause")
    
    def stop_tts(self):
        """Stop TTS."""
        if self.current_worker and isinstance(self.current_worker, TTSWorker):
            self.current_worker.stop()
            self.tts_pause_btn.setEnabled(False)
            self.tts_stop_btn.setEnabled(False)
            self.tts_pause_btn.setText("Pause")
    
    def start_tts(self):
        """Start TTS generation process with voice assignment."""
        if not self.project or not self.project.segments:
            return
        
        # Apply voice settings based on mode
        if self.voice_mode_auto.isChecked():
            # Auto-detect mode: use speaker-specific voices
            speaker1_text = self.speaker1_voice.currentText()
            speaker2_text = self.speaker2_voice.currentText()
            
            speaker1_voice = speaker1_text.split(" (")[0]
            speaker2_voice = speaker2_text.split(" (")[0]
            
            self.pipeline.set_speaker_voice("SPEAKER_1", speaker1_voice)
            self.pipeline.set_speaker_voice("SPEAKER_2", speaker2_voice)
            self.pipeline.set_speaker_voice("UNKNOWN", speaker2_voice)
            
            self.status_label.setText("Generating speech (auto-detect mode, male/female voices)")
        else:
            # Single voice mode: use same voice for all
            single_voice_text = self.single_voice_combo.currentText()
            single_voice = single_voice_text.split(" (")[0]
            
            self.pipeline.set_speaker_voice("SPEAKER_1", single_voice)
            self.pipeline.set_speaker_voice("SPEAKER_2", single_voice)
            self.pipeline.set_speaker_voice("UNKNOWN", single_voice)
            
            voice_type = "Male" if "Piseth" in single_voice else "Female"
            self.status_label.setText(f"Generating speech (single {voice_type} voice)")
        
        self.set_processing_state(True, "Generating speech (parallel processing)...")
        self.tts_pause_btn.setEnabled(True)
        self.tts_stop_btn.setEnabled(True)
        
        self.current_worker = TTSWorker(self.pipeline)
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.on_tts_finished)
        self.current_worker.error.connect(self.on_worker_error)
        self.current_worker.start()
    
    def on_tts_finished(self, segments):
        """Handle TTS completion."""
        self.set_processing_state(False, "Speech generation complete")
        self.tts_pause_btn.setEnabled(False)
        self.tts_stop_btn.setEnabled(False)
        self.tts_pause_btn.setText("Pause")
        self.update_translation_table(segments)
        self.export_btn.setEnabled(True)
        
        # Show alert if auto-run was enabled
        if self.auto_run_checkbox.isChecked():
            QMessageBox.information(
                self,
                "Auto-Run Complete!",
                "✓ Transcription complete\n"
                "✓ Translation complete\n"
                "✓ Khmer speech generated\n\n"
                "All 3 steps finished! Ready to export your dubbed video.\n\n"
                "Go to Export tab and choose output location."
            )
            self.tabs.setCurrentIndex(3)  # Switch to export tab
        else:
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
            mix_original=False,
            original_volume=0.0,
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
            # Settings saved - reload pipeline with new config
            self.reload_pipeline()
            self.status_label.setText("Settings saved and applied")
    
    def reload_pipeline(self):
        """Reload pipeline with current config settings."""
        # Read updated config
        self.translation_provider = getattr(config, 'translation_provider', 'hybrid')
        manual_dict_path = getattr(config, 'manual_dict_path', 'translations.json')
        
        # Recreate pipeline with new settings
        self.pipeline = ProcessingPipeline(
            translation_provider=self.translation_provider,
            manual_dict_path=manual_dict_path
        )
        
        # Log the change
        from ..utils.logger import setup_logger
        logger = setup_logger(__name__)
        logger.info(f"Pipeline reloaded with provider: {self.translation_provider}")
