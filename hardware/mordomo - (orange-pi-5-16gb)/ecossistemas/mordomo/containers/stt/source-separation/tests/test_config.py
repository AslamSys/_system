"""Tests for configuration module."""

import pytest
from pathlib import Path
import yaml

from src.config import (
    Config,
    DemucsConfig,
    ProcessingConfig,
    TriggerConfig,
    NATSConfig,
    MetricsConfig,
    load_config,
)


def test_demucs_config_defaults():
    """Test DemucsConfig default values."""
    config = DemucsConfig()
    assert config.model == "htdemucs_ft"
    assert config.device == "cpu"
    assert config.shifts == 1
    assert config.overlap == 0.25


def test_processing_config_defaults():
    """Test ProcessingConfig default values."""
    config = ProcessingConfig()
    assert config.max_duration == 5.0
    assert config.batch_size == 1
    assert config.num_workers == 2


def test_trigger_config_defaults():
    """Test TriggerConfig default values."""
    config = TriggerConfig()
    assert config.min_overlap_duration == 0.5
    assert config.confidence_threshold == 0.6


def test_nats_config_defaults():
    """Test NATSConfig default values."""
    config = NATSConfig()
    assert config.servers == ["nats://localhost:4222"]
    assert config.subjects.input == "audio.overlap_detected"
    assert config.subjects.output == "audio.separated"
    assert config.connection.max_reconnect_attempts == 10
    assert config.connection.reconnect_time_wait == 2


def test_metrics_config_defaults():
    """Test MetricsConfig default values."""
    config = MetricsConfig()
    assert config.port == 9090
    assert config.enabled is True


def test_config_defaults():
    """Test Config with all default values."""
    config = Config()
    assert isinstance(config.demucs, DemucsConfig)
    assert isinstance(config.processing, ProcessingConfig)
    assert isinstance(config.trigger, TriggerConfig)
    assert isinstance(config.nats, NATSConfig)
    assert isinstance(config.metrics, MetricsConfig)


def test_load_config_with_custom_values(tmp_path):
    """Test loading config from YAML file."""
    config_data = {
        "demucs": {
            "model": "custom_model",
            "device": "cuda",
            "shifts": 2,
            "overlap": 0.5
        },
        "processing": {
            "max_duration": 10.0,
            "batch_size": 2,
            "num_workers": 4
        },
        "nats": {
            "servers": ["nats://custom:4222"],
            "subjects": {
                "input": "custom.input",
                "output": "custom.output"
            }
        }
    }
    
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    config = load_config(config_file)
    
    assert config.demucs.model == "custom_model"
    assert config.demucs.device == "cuda"
    assert config.demucs.shifts == 2
    assert config.processing.max_duration == 10.0
    assert config.nats.servers == ["nats://custom:4222"]
    assert config.nats.subjects.input == "custom.input"


def test_load_config_missing_file():
    """Test loading config when file doesn't exist."""
    config = load_config(Path("/nonexistent/config.yaml"))
    # Should return default config
    assert isinstance(config, Config)
    assert config.demucs.model == "htdemucs_ft"
