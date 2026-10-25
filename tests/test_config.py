"""Test configuration module."""
import pytest
from src.utils.config import Config


def test_config_initialization():
    """Test configuration can be initialized."""
    config = Config()
    assert config.omniroute_base_url is not None
    assert config.temp_dir.exists()
    assert config.output_dir.exists()


def test_config_paths_created():
    """Test that config creates necessary directories."""
    config = Config()
    assert config.temp_dir.is_dir()
    assert config.output_dir.is_dir()
