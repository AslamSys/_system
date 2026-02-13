#!/usr/bin/env python3
"""
Audio Capture + VAD - Main Entry Point

Captura áudio do microfone continuamente, aplica VAD e distribui via ZeroMQ.
"""

import sys
import signal
import logging
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.audio_capture import AudioCaptureVAD
from src.config_loader import load_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    """Handler para Ctrl+C"""
    logger.info("Recebido sinal de interrupção. Encerrando...")
    sys.exit(0)


def main():
    """Função principal"""
    # Registrar handler de sinal
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Carregar configuração
        logger.info("Carregando configuração...")
        config = load_config()
        
        # Ajustar nível de log
        log_level = config.get('logging', {}).get('level', 'INFO')
        logging.getLogger().setLevel(getattr(logging, log_level))
        
        # Criar e iniciar captura de áudio
        logger.info("Iniciando Audio Capture + VAD...")
        audio_capture = AudioCaptureVAD(config)
        
        logger.info("✅ Sistema iniciado. Pressione Ctrl+C para parar.")
        audio_capture.start()
        
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Encerrando...")


if __name__ == "__main__":
    main()
