"""Unit tests for OmniRoute service."""
import pytest
from src.services.omniroute_service import OmniRouteService


def test_omniroute_service_initialization():
    """Test OmniRoute service can be initialized."""
    service = OmniRouteService(
        base_url="http://localhost:8000",
        api_key="test_key",
        model="gpt-4"
    )
    assert service.base_url == "http://localhost:8000"
    assert service.api_key == "test_key"
    assert service.model == "gpt-4"


def test_translation_prompt_building():
    """Test translation prompt is built correctly."""
    service = OmniRouteService()
    prompt = service._build_translation_prompt("Hello", "English", "Khmer")
    assert "Hello" in prompt
    assert "English" in prompt
    assert "Khmer" in prompt


def test_headers_with_api_key():
    """Test request headers include API key."""
    service = OmniRouteService(api_key="test_key_123")
    headers = service._get_headers()
    assert "Authorization" in headers
    assert "Bearer test_key_123" in headers["Authorization"]


def test_headers_without_api_key():
    """Test request headers work without API key."""
    service = OmniRouteService(api_key="")
    headers = service._get_headers()
    assert "Content-Type" in headers
    # Authorization should not be present if no key
    assert "Authorization" not in headers or not headers["Authorization"]


# Note: Actual translation tests require a running OmniRoute instance
# and valid API credentials, so they are integration tests
