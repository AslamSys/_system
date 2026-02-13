import asyncio
import logging
import signal
import sys

from config import settings
from detector import WakeWordDetector
from metrics import start_metrics_server


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def setup_signal_handlers(detector: WakeWordDetector):
    """Configura handlers para sinais de sistema"""
    def signal_handler(sig, frame):
        logger.info(f"\n🛑 Sinal recebido: {sig}")
        detector.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("🎯 Wake Word Detector - Ecossistema Mordomo")
    logger.info("=" * 60)
    logger.info(f"Engine: OpenWakeWord (Open Source)")
    logger.info(f"Keyword: {settings.wake_word_keyword}")
    logger.info(f"Threshold: {settings.wake_word_threshold}")
    logger.info(f"Framework: {settings.inference_framework}")
    logger.info(f"ZeroMQ: {settings.zeromq_endpoint}")
    logger.info(f"NATS: {settings.nats_url}")
    logger.info("=" * 60)
    
    # Inicia servidor de métricas
    start_metrics_server(settings.prometheus_port)
    
    # Cria detector
    detector = WakeWordDetector()
    
    # Configura handlers de sinal
    setup_signal_handlers(detector)
    
    try:
        # Inicializa
        await detector.initialize()
        
        # Executa
        await detector.run()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        return 1
    finally:
        await detector.cleanup()
    
    logger.info("👋 Wake Word Detector finalizado")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
