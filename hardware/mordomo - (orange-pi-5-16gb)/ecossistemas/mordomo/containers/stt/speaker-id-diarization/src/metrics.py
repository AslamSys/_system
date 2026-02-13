"""
Prometheus metrics for Speaker ID/Diarization service.
Tracks latency, accuracy, unknown detections, overlaps, etc.
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import structlog

logger = structlog.get_logger(__name__)


# Counters
speaker_identifications_total = Counter(
    'speaker_identifications_total',
    'Total speaker identifications',
    ['speaker_id', 'recognized']
)

speaker_unknown_detections_total = Counter(
    'speaker_unknown_detections_total',
    'Total unknown speaker detections'
)

speaker_overlap_detections_total = Counter(
    'speaker_overlap_detections_total',
    'Total voice overlap detections'
)

source_separation_triggers_total = Counter(
    'source_separation_triggers_total',
    'Total source separation triggers'
)

gate_operations_total = Counter(
    'gate_operations_total',
    'Total gate operations',
    ['operation']  # verified, rejected, conversation_ended
)

# Histograms
speaker_diarization_latency_seconds = Histogram(
    'speaker_diarization_latency_seconds',
    'Diarization processing latency in seconds',
    buckets=[0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0]
)

speaker_confidence_histogram = Histogram(
    'speaker_confidence_histogram',
    'Speaker recognition confidence distribution',
    ['speaker_id'],
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
)

# Gauges
gate_buffer_size = Gauge(
    'gate_buffer_size',
    'Current number of buffered results'
)

active_conversations = Gauge(
    'active_conversations',
    'Number of active conversations'
)

enrolled_speakers_total = Gauge(
    'enrolled_speakers_total',
    'Total number of enrolled speakers'
)


class MetricsCollector:
    """Centralized metrics collection."""
    
    def __init__(self, port: int = 8003):
        self.port = port
    
    def start_server(self):
        """Start Prometheus metrics HTTP server."""
        try:
            start_http_server(self.port)
            logger.info("metrics_server_started", port=self.port)
        except Exception as e:
            logger.error("metrics_server_failed", error=str(e))
    
    @staticmethod
    def record_identification(speaker_id: str, recognized: bool, confidence: float):
        """Record speaker identification."""
        speaker_identifications_total.labels(
            speaker_id=speaker_id,
            recognized=str(recognized)
        ).inc()
        
        if not recognized:
            speaker_unknown_detections_total.inc()
        
        speaker_confidence_histogram.labels(speaker_id=speaker_id).observe(confidence)
    
    @staticmethod
    def record_overlap():
        """Record voice overlap detection."""
        speaker_overlap_detections_total.inc()
    
    @staticmethod
    def record_source_separation_trigger():
        """Record source separation trigger."""
        source_separation_triggers_total.inc()
    
    @staticmethod
    def record_gate_operation(operation: str):
        """Record gate operation (verified, rejected, conversation_ended)."""
        gate_operations_total.labels(operation=operation).inc()
    
    @staticmethod
    def set_buffer_size(size: int):
        """Set current buffer size."""
        gate_buffer_size.set(size)
    
    @staticmethod
    def set_active_conversations(count: int):
        """Set active conversations count."""
        active_conversations.set(count)
    
    @staticmethod
    def set_enrolled_speakers(count: int):
        """Set enrolled speakers count."""
        enrolled_speakers_total.set(count)
