"""Tests for NATS client."""

import pytest
import asyncio
import json
import base64

from src.nats_client import (
    NATSClient,
    OverlapDetectedMessage,
    SeparatedAudioMessage
)
from src.config import NATSConfig


@pytest.fixture
def nats_config():
    """NATS configuration fixture."""
    return NATSConfig(
        servers=["nats://localhost:4222"],
        subjects={
            "input": "audio.overlap_detected",
            "output": "audio.separated"
        }
    )


@pytest.fixture
def nats_client(nats_config):
    """NATS client fixture."""
    return NATSClient(nats_config)


def test_overlap_detected_message():
    """Test OverlapDetectedMessage parsing."""
    audio_data = b"test_audio_data"
    data = {
        "audio": base64.b64encode(audio_data).decode(),
        "duration": 2.5,
        "speakers": ["user_1", "user_2"],
        "conversation_id": "test-123",
        "timestamp": 1732723200.123
    }
    
    message = OverlapDetectedMessage(data)
    
    assert message.audio == audio_data
    assert message.duration == 2.5
    assert message.speakers == ["user_1", "user_2"]
    assert message.conversation_id == "test-123"
    assert message.timestamp == 1732723200.123


def test_separated_audio_message():
    """Test SeparatedAudioMessage creation."""
    channels = [
        {
            "audio": "base64_encoded_audio_1",
            "speaker_id": "user_1",
            "confidence": 0.85
        },
        {
            "audio": "base64_encoded_audio_2",
            "speaker_id": "user_2",
            "confidence": 0.78
        }
    ]
    
    message = SeparatedAudioMessage(
        channels=channels,
        conversation_id="test-123",
        original_duration=2.5,
        timestamp=1732723201.456
    )
    
    assert message.channels == channels
    assert message.conversation_id == "test-123"
    assert message.original_duration == 2.5
    assert message.timestamp == 1732723201.456


def test_separated_audio_message_to_dict():
    """Test SeparatedAudioMessage serialization."""
    channels = [{"audio": "test", "speaker_id": "user_1", "confidence": 0.85}]
    
    message = SeparatedAudioMessage(
        channels=channels,
        conversation_id="test-123",
        original_duration=2.5
    )
    
    data = message.to_dict()
    
    assert "channels" in data
    assert "conversation_id" in data
    assert "original_duration" in data
    assert "timestamp" in data
    assert data["channels"] == channels


def test_nats_client_initialization(nats_client, nats_config):
    """Test NATS client initialization."""
    assert nats_client.config == nats_config
    assert nats_client.nc is None
    assert not nats_client._connected
    assert not nats_client.is_connected


@pytest.mark.asyncio
async def test_nats_client_connection_properties(nats_client):
    """Test NATS client connection state tracking."""
    assert not nats_client.is_connected
    
    # Note: Actual connection test would require NATS server
    # For unit tests, we'd mock the NATS client


# Integration tests would go here (requiring actual NATS server)
# These would test:
# - Actual connection to NATS
# - Subscribing and receiving messages
# - Publishing messages
# - Reconnection logic
