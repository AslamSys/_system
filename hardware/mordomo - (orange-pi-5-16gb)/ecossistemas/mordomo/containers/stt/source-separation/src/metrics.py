"""Prometheus metrics for Source Separation service."""

import logging
from typing import Optional
from prometheus_client import Counter, Histogram, Gauge, start_http_server

logger = logging.getLogger(__name__)


class Metrics:
    """Prometheus metrics collector."""
    
    def __init__(self, enabled: bool = True, port: int = 9090):
        """
        Initialize metrics.
        
        Args:
            enabled: Whether metrics are enabled
            port: HTTP port for Prometheus scraping
        """
        self.enabled = enabled
        self.port = port
        self._server_started = False
        
        if not enabled:
            logger.info("Metrics disabled")
            return
        
        # Counter: Total separation requests
        self.requests_total = Counter(
            'source_separation_requests_total',
            'Total number of source separation requests',
            ['status']  # success, error
        )
        
        # Histogram: Processing latency
        self.latency_seconds = Histogram(
            'source_separation_latency_seconds',
            'Time taken to separate audio sources',
            buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
        )
        
        # Counter: Successful separations
        self.success_total = Counter(
            'source_separation_success_total',
            'Total number of successful separations',
            ['num_speakers']
        )
        
        # Gauge: Quality score (confidence average)
        self.quality_score = Gauge(
            'source_separation_quality_score',
            'Average confidence score of separated channels'
        )
        
        # Gauge: Current processing
        self.processing_current = Gauge(
            'source_separation_processing_current',
            'Number of separations currently being processed'
        )
        
        # Counter: Audio duration processed
        self.audio_duration_seconds = Counter(
            'source_separation_audio_duration_seconds_total',
            'Total audio duration processed in seconds'
        )
        
        # Histogram: Number of speakers
        self.num_speakers = Histogram(
            'source_separation_num_speakers',
            'Number of speakers in separation requests',
            buckets=[1, 2, 3, 4, 5]
        )
        
        logger.info(f"Metrics initialized on port {port}")
    
    def start_server(self):
        """Start Prometheus HTTP server."""
        if not self.enabled or self._server_started:
            return
        
        try:
            start_http_server(self.port)
            self._server_started = True
            logger.info(f"Prometheus metrics server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    def record_request(self, status: str = 'success'):
        """Record a separation request."""
        if self.enabled:
            self.requests_total.labels(status=status).inc()
    
    def record_latency(self, seconds: float):
        """Record processing latency."""
        if self.enabled:
            self.latency_seconds.observe(seconds)
    
    def record_success(self, num_speakers: int):
        """Record successful separation."""
        if self.enabled:
            self.success_total.labels(num_speakers=str(num_speakers)).inc()
    
    def record_quality(self, confidence: float):
        """Record quality score."""
        if self.enabled:
            self.quality_score.set(confidence)
    
    def increment_processing(self):
        """Increment current processing count."""
        if self.enabled:
            self.processing_current.inc()
    
    def decrement_processing(self):
        """Decrement current processing count."""
        if self.enabled:
            self.processing_current.dec()
    
    def record_audio_duration(self, seconds: float):
        """Record audio duration processed."""
        if self.enabled:
            self.audio_duration_seconds.inc(seconds)
    
    def record_num_speakers(self, count: int):
        """Record number of speakers."""
        if self.enabled:
            self.num_speakers.observe(count)


# Global metrics instance
_metrics: Optional[Metrics] = None


def initialize_metrics(enabled: bool = True, port: int = 9090) -> Metrics:
    """
    Initialize global metrics instance.
    
    Args:
        enabled: Whether metrics are enabled
        port: HTTP port for Prometheus
        
    Returns:
        Metrics instance
    """
    global _metrics
    _metrics = Metrics(enabled=enabled, port=port)
    return _metrics


def get_metrics() -> Metrics:
    """Get global metrics instance."""
    if _metrics is None:
        raise RuntimeError("Metrics not initialized. Call initialize_metrics() first.")
    return _metrics
