"""
Speaker Verification Service
Serviço principal que conecta ao NATS e processa mensagens
"""
import asyncio
import base64
import json
import logging
import numpy as np
import yaml
from pathlib import Path
from nats.aio.client import Client as NATS
from datetime import datetime
from speaker_verifier import SpeakerVerifier

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpeakerVerificationService:
    """
    Serviço de verificação de falante com NATS
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Inicializa o serviço
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config = self._load_config(config_path)
        self.nc = NATS()
        self.verifier = None
        self.stats = {
            'verifications_total': 0,
            'verified_count': 0,
            'rejected_count': 0,
            'errors_count': 0,
            'by_user': {}
        }
    
    def _load_config(self, config_path: str) -> dict:
        """Carrega configuração do YAML"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    async def start(self):
        """Inicia o serviço"""
        try:
            # Conecta ao NATS
            nats_url = self.config['nats']['url']
            logger.info(f"Connecting to NATS at {nats_url}")
            await self.nc.connect(nats_url)
            logger.info("Connected to NATS")
            
            # Inicializa verificador
            self.verifier = SpeakerVerifier(self.config)
            
            # Subscreve ao tópico de wake word
            subscribe_subject = self.config['nats']['subscribe']
            logger.info(f"Subscribing to {subscribe_subject}")
            await self.nc.subscribe(subscribe_subject, cb=self._handle_message)
            
            logger.info("✅ Speaker Verification Service started successfully")
            logger.info(f"   Threshold: {self.config['verification']['threshold']}")
            logger.info(f"   Users enrolled: {len(self.config['users'])}")
            
            # Mantém serviço rodando
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error starting service: {e}")
            raise
    
    async def _handle_message(self, msg):
        """
        Processa mensagem recebida do NATS
        
        Args:
            msg: Mensagem NATS
        """
        try:
            # Parse payload
            payload = json.loads(msg.data.decode())
            timestamp = payload.get('timestamp', datetime.now().timestamp())
            logger.info(f"📩 Received wake_word.detected at {timestamp}")
            
            # Decodifica áudio
            audio_base64 = payload.get('audio_snippet')
            if not audio_base64:
                logger.error("❌ No audio_snippet in payload")
                self.stats['errors_count'] += 1
                return
            
            audio_bytes = base64.b64decode(audio_base64)
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Verifica falante
            is_verified, user_id, confidence = self.verifier.verify(audio_data)
            
            self.stats['verifications_total'] += 1
            
            # Publica resultado
            if is_verified:
                await self._publish_verified(user_id, confidence, timestamp)
                self.stats['verified_count'] += 1
                self.stats['by_user'][user_id] = self.stats['by_user'].get(user_id, 0) + 1
            else:
                await self._publish_rejected(confidence, timestamp)
                self.stats['rejected_count'] += 1
            
            # Log stats periodicamente
            if self.stats['verifications_total'] % 10 == 0:
                self._log_stats()
                
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}", exc_info=True)
            self.stats['errors_count'] += 1
    
    async def _publish_verified(self, user_id: str, confidence: float, timestamp: float):
        """
        Publica evento de verificação bem-sucedida
        
        Args:
            user_id: ID do usuário verificado
            confidence: Score de confiança
            timestamp: Timestamp original
        """
        subject = self.config['nats']['publish_verified']
        payload = {
            'user_id': user_id,
            'confidence': round(confidence, 3),
            'timestamp': timestamp
        }
        
        await self.nc.publish(subject, json.dumps(payload).encode())
        logger.info(f"✅ Published speaker.verified: {user_id} (confidence: {confidence:.3f})")
    
    async def _publish_rejected(self, similarity: float, timestamp: float):
        """
        Publica evento de rejeição
        
        Args:
            similarity: Melhor similaridade encontrada
            timestamp: Timestamp original
        """
        subject = self.config['nats']['publish_rejected']
        payload = {
            'reason': 'unknown_voice',
            'similarity': round(similarity, 3),
            'timestamp': timestamp
        }
        
        await self.nc.publish(subject, json.dumps(payload).encode())
        logger.info(f"❌ Published speaker.rejected: similarity {similarity:.3f}")
    
    def _log_stats(self):
        """Loga estatísticas do serviço"""
        total = self.stats['verifications_total']
        verified = self.stats['verified_count']
        rejected = self.stats['rejected_count']
        errors = self.stats['errors_count']
        
        verified_pct = (verified / total * 100) if total > 0 else 0
        rejected_pct = (rejected / total * 100) if total > 0 else 0
        
        logger.info("=" * 60)
        logger.info(f"📊 Statistics Summary:")
        logger.info(f"   Total verifications: {total}")
        logger.info(f"   ✅ Verified: {verified} ({verified_pct:.1f}%)")
        logger.info(f"   ❌ Rejected: {rejected} ({rejected_pct:.1f}%)")
        logger.info(f"   ⚠️  Errors: {errors}")
        logger.info(f"   By user: {self.stats['by_user']}")
        logger.info("=" * 60)
        
        # Stats do verificador
        verifier_stats = self.verifier.get_stats()
        logger.info(f"🔧 Verifier stats: {verifier_stats}")
    
    async def stop(self):
        """Para o serviço"""
        logger.info("Stopping service...")
        await self.nc.close()
        logger.info("Service stopped")


async def main():
    """Função principal"""
    service = SpeakerVerificationService()
    
    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        await service.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await service.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
