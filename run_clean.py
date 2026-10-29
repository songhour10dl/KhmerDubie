"""KhmerDub Studio launcher with suppressed NumPy warnings."""
import warnings
import sys

# Suppress NumPy warnings before importing NumPy
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')

# Now run the main application
if __name__ == '__main__':
    from main import main
    main()
