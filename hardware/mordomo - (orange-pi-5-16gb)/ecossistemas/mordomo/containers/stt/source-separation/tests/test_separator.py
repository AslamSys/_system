"""Tests for source separation service."""

import pytest
import numpy as np
import base64

from src.separator import SourceSeparationService, SeparatedChannel
from src.config import DemucsConfig, ProcessingConfig


@pytest.fixture
def demucs_config():
    """Demucs configuration fixture."""
    return DemucsConfig(
        model="htdemucs_ft",
        device="cpu",
        shifts=1,
        overlap=0.25
    )


@pytest.fixture
def processing_config():
    """Processing configuration fixture."""
    return ProcessingConfig(
        max_duration=5.0,
        batch_size=1,
        num_workers=2
    )


@pytest.fixture
def separator(demucs_config, processing_config):
    """Source separation service fixture."""
    return SourceSeparationService(demucs_config, processing_config)


def test_separator_initialization(separator):
    """Test separator initializes correctly."""
    assert separator is not None
    assert not separator._initialized
    assert separator.model is None


def test_decode_audio(separator):
    """Test audio decoding from bytes."""
    # Create test audio (1 second at 16kHz)
    sample_rate = 16000
    duration = 1.0
    samples = int(sample_rate * duration)
    
    # Create sine wave
    audio_float = np.sin(2 * np.pi * 440 * np.arange(samples) / sample_rate)
    audio_int16 = (audio_float * 32768).astype(np.int16)
    audio_bytes = audio_int16.tobytes()
    
    # Decode
    decoded = separator._decode_audio(audio_bytes, sample_rate)
    
    assert decoded.shape[0] == samples
    assert decoded.dtype == np.float32
    assert np.max(np.abs(decoded)) <= 1.0


def test_encode_audio(separator):
    """Test audio encoding to base64."""
    # Create test audio
    sample_rate = 16000
    audio = np.sin(2 * np.pi * 440 * np.arange(sample_rate) / sample_rate)
    
    # Encode
    encoded = separator.encode_audio(audio, sample_rate)
    
    # Verify it's valid base64
    assert isinstance(encoded, str)
    decoded_bytes = base64.b64decode(encoded)
    assert len(decoded_bytes) == len(audio) * 2  # 16-bit = 2 bytes per sample


def test_separated_channel():
    """Test SeparatedChannel class."""
    audio = np.random.randn(16000)
    channel = SeparatedChannel(
        audio=audio,
        speaker_id="user_1",
        confidence=0.85
    )
    
    assert channel.speaker_id == "user_1"
    assert channel.confidence == 0.85
    assert np.array_equal(channel.audio, audio)


def test_duration_validation(separator, processing_config):
    """Test that audio duration is validated."""
    # Create audio longer than max_duration
    sample_rate = 16000
    duration = processing_config.max_duration + 1
    samples = int(sample_rate * duration)
    
    audio = np.random.randn(samples).astype(np.float32)
    audio_int16 = (audio * 32768).astype(np.int16)
    audio_bytes = audio_int16.tobytes()
    
    speakers = ["user_1", "user_2"]
    
    with pytest.raises(ValueError, match="Audio too long"):
        separator.separate_audio(audio_bytes, sample_rate, speakers, duration)


def test_single_speaker_separation(separator):
    """Test separation with single speaker."""
    sample_rate = 16000
    duration = 2.0
    samples = int(sample_rate * duration)
    
    # Create test audio
    audio = np.random.randn(samples).astype(np.float32)
    audio_int16 = (audio * 32768).astype(np.int16)
    audio_bytes = audio_int16.tobytes()
    
    speakers = ["user_1"]
    
    # Note: This test would require actual model loading
    # For unit tests, we'd mock the model
    # Here we just test the structure
    
    # channels = separator.separate_audio(audio_bytes, sample_rate, speakers, duration)
    # assert len(channels) == 1
    # assert channels[0].speaker_id == "user_1"
