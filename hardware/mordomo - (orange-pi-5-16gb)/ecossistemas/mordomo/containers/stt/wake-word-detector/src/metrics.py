from prometheus_client import Counter, Gauge, Histogram, start_http_server
import logging

logger = logging.getLogger(__name__)


# Contadores
detections_total = Counter(
    'wake_word_detections_total',
    'Total de detecções da wake word'
)

conversation_ended_events_total = Counter(
    'wake_word_conversation_ended_events_total',
    'Total de eventos conversation.ended recebidos'
)

# Gauges
suppressed_state = Gauge(
    'wake_word_suppressed',
    'Estado atual: 0 = IDLE (detectando), 1 = SUPPRESSED (suprimido)'
)

# Histogramas
confidence_histogram = Histogram(
    'wake_word_confidence',
    'Distribuição da confiança das detecções',
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
)

processing_latency = Histogram(
    'wake_word_processing_latency_seconds',
    'Latência de processamento de frame de áudio',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1]
)

suppression_duration = Histogram(
    'wake_word_suppression_duration_seconds',
    'Duração do período de supressão',
    buckets=[1, 5, 10, 30, 60, 120, 300]
)


def start_metrics_server(port: int):
    """Inicia servidor de métricas Prometheus"""
    try:
        start_http_server(port)
        logger.info(f"📊 Servidor de métricas iniciado na porta {port}")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor de métricas: {e}")
