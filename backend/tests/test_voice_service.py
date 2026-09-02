"""Tests for voice service with fallback chain."""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.voice_service import VoiceService, VoiceUnavailableError


def test_voice_service_import():
    """Test that voice service can be imported without errors."""
    from app.services.voice_service import VoiceService, VoiceUnavailableError
    assert VoiceService is not None
    assert VoiceUnavailableError is not None


def test_voice_service_initialization():
    """Test that voice service initializes with providers."""
    service = VoiceService()
    assert len(service.stt_providers) == 2
    assert service.stt_providers[0][0] == "sarvam"
    assert service.stt_providers[1][0] == "azure"
    assert len(service.tts_providers) == 2
    assert service.tts_providers[0][0] == "sarvam"
    assert service.tts_providers[1][0] == "azure"


@pytest.mark.asyncio
async def test_stt_fallback_raises_when_all_providers_disabled():
    """Test that STT raises VoiceUnavailableError when all providers fail."""
    service = VoiceService()
    
    with pytest.raises(VoiceUnavailableError) as exc_info:
        await service.speech_to_text(b"test audio", "en")
    
    assert "No voice providers available" in str(exc_info.value)


@pytest.mark.asyncio
async def test_tts_fallback_raises_when_all_providers_disabled():
    """Test that TTS raises VoiceUnavailableError when all providers fail."""
    service = VoiceService()
    
    mock_provider1 = AsyncMock()
    mock_provider1.synthesize.side_effect = RuntimeError("Provider 1 failed")
    
    mock_provider2 = AsyncMock()
    mock_provider2.synthesize.side_effect = RuntimeError("Provider 2 failed")
    
    service.tts_providers = [
        ("provider1", mock_provider1),
        ("provider2", mock_provider2),
    ]
    
    with pytest.raises(VoiceUnavailableError) as exc_info:
        await service.text_to_speech("Hello world", "en")
    
    assert "No voice providers available" in str(exc_info.value)


@pytest.mark.asyncio
async def test_stt_fallback_to_second_provider():
    """Test that STT falls back to second provider when first fails."""
    service = VoiceService()
    
    mock_provider1 = AsyncMock()
    mock_provider1.transcribe.side_effect = RuntimeError("Provider 1 failed")
    
    mock_provider2 = AsyncMock()
    mock_provider2.transcribe.return_value = "recognized text"
    
    service.stt_providers = [
        ("provider1", mock_provider1),
        ("provider2", mock_provider2),
    ]
    
    result = await service.speech_to_text(b"test audio", "en")
    
    assert result == "recognized text"
    mock_provider1.transcribe.assert_called_once()
    mock_provider2.transcribe.assert_called_once()


@pytest.mark.asyncio
async def test_tts_fallback_to_second_provider():
    """Test that TTS falls back to second provider when first fails."""
    service = VoiceService()
    
    mock_provider1 = AsyncMock()
    mock_provider1.synthesize.side_effect = RuntimeError("Provider 1 failed")
    
    mock_provider2 = AsyncMock()
    mock_provider2.synthesize.return_value = b"audio bytes"
    
    service.tts_providers = [
        ("provider1", mock_provider1),
        ("provider2", mock_provider2),
    ]
    
    result = await service.text_to_speech("Hello world", "en")
    
    assert result == b"audio bytes"
    mock_provider1.synthesize.assert_called_once()
    mock_provider2.synthesize.assert_called_once()


@pytest.mark.asyncio
async def test_stt_fallback_stops_at_first_success():
    """Test that STT stops at first successful provider."""
    service = VoiceService()
    
    mock_provider1 = AsyncMock()
    mock_provider1.transcribe.return_value = "first provider result"
    
    mock_provider2 = AsyncMock()
    mock_provider2.transcribe.return_value = "second provider result"
    
    service.stt_providers = [
        ("provider1", mock_provider1),
        ("provider2", mock_provider2),
    ]
    
    result = await service.speech_to_text(b"test audio", "en")
    
    assert result == "first provider result"
    mock_provider1.transcribe.assert_called_once()
    mock_provider2.transcribe.assert_not_called()


@pytest.mark.asyncio
async def test_tts_fallback_stops_at_first_success():
    """Test that TTS stops at first successful provider."""
    service = VoiceService()
    
    mock_provider1 = AsyncMock()
    mock_provider1.synthesize.return_value = b"first provider audio"
    
    mock_provider2 = AsyncMock()
    mock_provider2.synthesize.return_value = b"second provider audio"
    
    service.tts_providers = [
        ("provider1", mock_provider1),
        ("provider2", mock_provider2),
    ]
    
    result = await service.text_to_speech("Hello world", "en")
    
    assert result == b"first provider audio"
    mock_provider1.synthesize.assert_called_once()
    mock_provider2.synthesize.assert_not_called()


@pytest.mark.asyncio
async def test_stt_all_providers_fail():
    """Test that STT raises VoiceUnavailableError when all providers fail."""
    service = VoiceService()
    
    mock_provider1 = AsyncMock()
    mock_provider1.transcribe.side_effect = RuntimeError("Provider 1 failed")
    
    mock_provider2 = AsyncMock()
    mock_provider2.transcribe.side_effect = RuntimeError("Provider 2 failed")
    
    service.stt_providers = [
        ("provider1", mock_provider1),
        ("provider2", mock_provider2),
    ]
    
    with pytest.raises(VoiceUnavailableError) as exc_info:
        await service.speech_to_text(b"test audio", "en")
    
    assert "No voice providers available" in str(exc_info.value)
    mock_provider1.transcribe.assert_called_once()
    mock_provider2.transcribe.assert_called_once()


@pytest.mark.asyncio
async def test_tts_all_providers_fail():
    """Test that TTS raises VoiceUnavailableError when all providers fail."""
    service = VoiceService()
    
    mock_provider1 = AsyncMock()
    mock_provider1.synthesize.side_effect = RuntimeError("Provider 1 failed")
    
    mock_provider2 = AsyncMock()
    mock_provider2.synthesize.side_effect = RuntimeError("Provider 2 failed")
    
    service.tts_providers = [
        ("provider1", mock_provider1),
        ("provider2", mock_provider2),
    ]
    
    with pytest.raises(VoiceUnavailableError) as exc_info:
        await service.text_to_speech("Hello world", "en")
    
    assert "No voice providers available" in str(exc_info.value)
    mock_provider1.synthesize.assert_called_once()
    mock_provider2.synthesize.assert_called_once()


@pytest.mark.asyncio
async def test_tts_segments_fallback_to_second_provider():
    """Test that TTS segments falls back to second provider when first fails."""
    service = VoiceService()

    mock_provider1 = AsyncMock()
    mock_provider1.text_to_speech_segments.side_effect = RuntimeError("Provider 1 failed")

    mock_provider2 = AsyncMock()
    mock_provider2.text_to_speech_segments.return_value = b"segments audio"

    service.tts_providers = [
        ("provider1", mock_provider1),
        ("provider2", mock_provider2),
    ]

    result = await service.text_to_speech_segments([{"text": "hi", "language": "en"}])

    assert result == b"segments audio"
    mock_provider2.text_to_speech_segments.assert_called_once()


@pytest.mark.asyncio
async def test_tts_segments_all_providers_fail():
    """Test that TTS segments raises VoiceUnavailableError when all providers fail."""
    service = VoiceService()

    mock_provider1 = AsyncMock()
    mock_provider1.text_to_speech_segments.side_effect = RuntimeError("Provider 1 failed")

    mock_provider2 = AsyncMock()
    mock_provider2.text_to_speech_segments.side_effect = NotImplementedError("no impl")

    service.tts_providers = [
        ("provider1", mock_provider1),
        ("provider2", mock_provider2),
    ]

    with pytest.raises(VoiceUnavailableError) as exc_info:
        await service.text_to_speech_segments([{"text": "hi", "language": "en"}])

    assert "No voice providers available" in str(exc_info.value)


def test_voice_unavailable_error_is_exception():
    """Test that VoiceUnavailableError is a proper exception."""
    error = VoiceUnavailableError("test message")
    assert isinstance(error, Exception)
    assert str(error) == "test message"
