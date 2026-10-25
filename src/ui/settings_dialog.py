"""Settings dialog for API configuration."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QMessageBox, QComboBox,
    QSpinBox
)
from PySide6.QtCore import Qt
from ..utils.config import config
from ..services import OmniRouteService, TTSService


class SettingsDialog(QDialog):
    """Settings dialog for API and provider configuration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # OmniRoute settings
        omniroute_group = QGroupBox("OmniRoute Translation")
        omniroute_layout = QFormLayout(omniroute_group)
        
        self.omniroute_url = QLineEdit()
        omniroute_layout.addRow("Base URL:", self.omniroute_url)
        
        self.omniroute_key = QLineEdit()
        self.omniroute_key.setEchoMode(QLineEdit.Password)
        omniroute_layout.addRow("API Key:", self.omniroute_key)
        
        self.omniroute_model = QLineEdit()
        omniroute_layout.addRow("Model:", self.omniroute_model)
        
        test_omniroute_btn = QPushButton("Test Connection")
        test_omniroute_btn.clicked.connect(self.test_omniroute)
        omniroute_layout.addRow("", test_omniroute_btn)
        
        layout.addWidget(omniroute_group)
        
        # TTS settings
        tts_group = QGroupBox("Text-to-Speech (Khmer)")
        tts_layout = QFormLayout(tts_group)
        
        self.tts_provider = QComboBox()
        self.tts_provider.addItems(["elevenlabs", "edge", "gtts", "google", "local", "kiri"])
        self.tts_provider.currentTextChanged.connect(self.on_tts_provider_changed)
        tts_layout.addRow("Provider:", self.tts_provider)
        
        self.tts_url = QLineEdit()
        tts_layout.addRow("Base URL:", self.tts_url)
        
        self.tts_key = QLineEdit()
        self.tts_key.setEchoMode(QLineEdit.Password)
        self.tts_key_label = QLabel("API Key:")
        tts_layout.addRow(self.tts_key_label, self.tts_key)
        
        self.tts_voice = QLineEdit()
        tts_layout.addRow("Voice ID:", self.tts_voice)
        
        test_tts_btn = QPushButton("Test Connection")
        test_tts_btn.clicked.connect(self.test_tts)
        tts_layout.addRow("", test_tts_btn)
        
        layout.addWidget(tts_group)
        
        # Processing settings
        process_group = QGroupBox("Processing Settings")
        process_layout = QFormLayout(process_group)
        
        self.max_concurrent = QSpinBox()
        self.max_concurrent.setMinimum(1)
        self.max_concurrent.setMaximum(10)
        process_layout.addRow("Max Concurrent Requests:", self.max_concurrent)
        
        self.request_timeout = QSpinBox()
        self.request_timeout.setMinimum(10)
        self.request_timeout.setMaximum(600)
        self.request_timeout.setSuffix(" seconds")
        process_layout.addRow("Request Timeout:", self.request_timeout)
        
        layout.addWidget(process_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """Load current settings into form."""
        self.omniroute_url.setText(config.omniroute_base_url)
        self.omniroute_key.setText(config.omniroute_api_key)
        self.omniroute_model.setText(config.omniroute_model)
        
        self.tts_provider.setCurrentText(config.tts_provider)
        self.tts_url.setText(config.tts_base_url)
        self.tts_key.setText(config.tts_api_key)
        self.tts_voice.setText(config.tts_voice)
        
        self.max_concurrent.setValue(config.max_concurrent_requests)
        self.request_timeout.setValue(config.request_timeout)
        
        # Update UI based on provider
        self.on_tts_provider_changed(config.tts_provider)
    
    def save_settings(self):
        """Save settings to config."""
        config.omniroute_base_url = self.omniroute_url.text()
        config.omniroute_api_key = self.omniroute_key.text()
        config.omniroute_model = self.omniroute_model.text()
        
        config.tts_provider = self.tts_provider.currentText()
        config.tts_base_url = self.tts_url.text()
        config.tts_api_key = self.tts_key.text()
        config.tts_voice = self.tts_voice.text()
        
        config.max_concurrent_requests = self.max_concurrent.value()
        config.request_timeout = self.request_timeout.value()
        
        # Save to .env file
        config.save_to_env()
        
        QMessageBox.information(self, "Success", "Settings saved successfully")
        self.accept()
    
    def test_omniroute(self):
        """Test OmniRoute connection."""
        try:
            service = OmniRouteService(
                base_url=self.omniroute_url.text(),
                api_key=self.omniroute_key.text(),
                model=self.omniroute_model.text()
            )
            
            success, message = service.test_connection()
            
            if success:
                QMessageBox.information(self, "Success", f"OmniRoute connection successful!\n\n{message}")
            else:
                QMessageBox.warning(self, "Connection Failed", f"OmniRoute connection failed:\n\n{message}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Test failed:\n\n{str(e)}")
    
    def on_tts_provider_changed(self, provider: str):
        """Update UI when TTS provider changes."""
        # Providers that need API key
        needs_api_key = provider in ["elevenlabs", "kiri", "google"]
        needs_base_url = provider in ["kiri", "elevenlabs"]
        
        self.tts_key.setEnabled(needs_api_key)
        self.tts_key_label.setEnabled(needs_api_key)
        self.tts_url.setEnabled(needs_base_url)
        
        # Update voice placeholder based on provider
        if provider == "elevenlabs":
            self.tts_voice.setPlaceholderText("Leave empty to auto-select multilingual voice")
            self.tts_voice.setEnabled(True)
        elif provider == "edge":
            self.tts_voice.setPlaceholderText("km-KH-SreymomNeural or km-KH-PisethNeural")
        elif provider == "gtts":
            self.tts_voice.setPlaceholderText("km (fixed)")
            self.tts_voice.setEnabled(False)
        elif provider == "google":
            self.tts_voice.setPlaceholderText("km-KH-Standard-A")
        elif provider == "local":
            self.tts_voice.setPlaceholderText("km (eSpeak-ng)")
            self.tts_voice.setEnabled(False)
        else:
            self.tts_voice.setEnabled(True)
    
    def test_tts(self):
        """Test TTS connection."""
        try:
            provider = self.tts_provider.currentText()
            
            # Show installation hint for providers
            if provider == "elevenlabs":
                hint = "\nNote: If test fails, install with: pip install elevenlabs\nGet API key from: https://elevenlabs.io"
            elif provider == "edge":
                hint = "\nNote: If test fails, install with: pip install edge-tts"
            elif provider == "gtts":
                hint = "\nNote: If test fails, install with: pip install gtts"
            elif provider == "local":
                hint = "\nNote: Requires eSpeak-ng: https://github.com/espeak-ng/espeak-ng/releases"
            else:
                hint = ""
            
            service = TTSService(
                provider=provider,
                api_key=self.tts_key.text() if self.tts_key.isEnabled() else None,
                base_url=self.tts_url.text() if self.tts_url.isEnabled() else None,
                voice=self.tts_voice.text() if self.tts_voice.isEnabled() else None
            )
            
            success, message = service.test_connection()
            
            if success:
                QMessageBox.information(self, "Success", f"TTS connection successful!\n\n{message}{hint}")
            else:
                QMessageBox.warning(self, "Connection Failed", f"TTS connection failed:\n\n{message}{hint}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Test failed:\n\n{str(e)}")
