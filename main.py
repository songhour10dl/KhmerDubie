"""KhmerDub Studio - AI Video Dubbing Application."""
import sys
from PySide6.QtWidgets import QApplication
from src.ui import MainWindow
from src.utils.logger import setup_logger


def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logger('khmerdub', log_file='logs/khmerdub.log')
    logger.info("Starting KhmerDub Studio")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("KhmerDub Studio")
    app.setOrganizationName("KhmerDub")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
