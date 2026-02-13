"""Tests for Prometheus metrics."""

import pytest
from src.metrics import Metrics, initialize_metrics, get_metrics


def test_metrics_initialization_enabled():
    """Test metrics initialization when enabled."""
    metrics = Metrics(enabled=True, port=9999)
    
    assert metrics.enabled is True
    assert metrics.port == 9999
    assert not metrics._server_started
    
    # Check that counters/gauges/histograms are created
    assert metrics.requests_total is not None
    assert metrics.latency_seconds is not None
    assert metrics.success_total is not None
    assert metrics.quality_score is not None


def test_metrics_initialization_disabled():
    """Test metrics initialization when disabled."""
    metrics = Metrics(enabled=False)
    
    assert metrics.enabled is False
    assert not metrics._server_started


def test_record_request():
    """Test recording requests."""
    metrics = Metrics(enabled=True, port=9999)
    
    # Should not raise
    metrics.record_request(status='success')
    metrics.record_request(status='error')


def test_record_latency():
    """Test recording latency."""
    metrics = Metrics(enabled=True, port=9999)
    
    metrics.record_latency(1.5)
    metrics.record_latency(2.3)


def test_record_success():
    """Test recording success."""
    metrics = Metrics(enabled=True, port=9999)
    
    metrics.record_success(num_speakers=2)
    metrics.record_success(num_speakers=3)


def test_record_quality():
    """Test recording quality score."""
    metrics = Metrics(enabled=True, port=9999)
    
    metrics.record_quality(0.85)
    metrics.record_quality(0.92)


def test_processing_counter():
    """Test processing counter increment/decrement."""
    metrics = Metrics(enabled=True, port=9999)
    
    metrics.increment_processing()
    metrics.increment_processing()
    metrics.decrement_processing()


def test_record_audio_duration():
    """Test recording audio duration."""
    metrics = Metrics(enabled=True, port=9999)
    
    metrics.record_audio_duration(2.5)
    metrics.record_audio_duration(3.7)


def test_record_num_speakers():
    """Test recording number of speakers."""
    metrics = Metrics(enabled=True, port=9999)
    
    metrics.record_num_speakers(2)
    metrics.record_num_speakers(3)


def test_initialize_metrics():
    """Test global metrics initialization."""
    metrics = initialize_metrics(enabled=True, port=9876)
    
    assert metrics.enabled is True
    assert metrics.port == 9876


def test_get_metrics():
    """Test getting global metrics instance."""
    # First initialize
    initialize_metrics(enabled=True, port=9876)
    
    # Then get
    metrics = get_metrics()
    assert metrics is not None
    assert metrics.enabled is True


def test_get_metrics_not_initialized():
    """Test getting metrics before initialization raises error."""
    # Reset global state
    import src.metrics as metrics_module
    metrics_module._metrics = None
    
    with pytest.raises(RuntimeError, match="Metrics not initialized"):
        get_metrics()


def test_metrics_disabled_no_recording():
    """Test that disabled metrics don't record."""
    metrics = Metrics(enabled=False)
    
    # Should not raise errors
    metrics.record_request('success')
    metrics.record_latency(1.0)
    metrics.record_success(2)
    metrics.record_quality(0.85)
