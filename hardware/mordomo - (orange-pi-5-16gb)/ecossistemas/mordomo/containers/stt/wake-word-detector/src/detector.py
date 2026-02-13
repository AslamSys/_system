import asyncio
import json
import logging
import struct
import time
import uuid
import numpy as np
from typing import Optional
from datetime import datetime

import zmq
import zmq.asyncio
from nats.aio.client import Client as NATS
from openwakeword.model import Model

from config import settings
from metrics import (
    detections_total,
    suppressed_state,
    confidence_histogram,
    processing_latency,
    suppression_duration,
    conversation_ended_events_total
)

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """
    Detector de Wake Word usando OpenWakeWord
    
    Estados:
    - IDLE: Detectando continuamente
    - SUPPRESSED: Suprimido após detecção (aguardando conversation.ended)
    """
    
    def __init__(self):
        self.state = "IDLE"
        self.current_session_id: Optional[str] = None
        self.suppression_start_time: Optional[float] = None
        self.max_suppression_timeout = settings.max_suppression_timeout
        
        # OpenWakeWord
        self.oww_model: Optional[Model] = None
        self.chunk_size = 1280  # OpenWakeWord usa chunks de 1280 samples (80ms @ 16kHz)
        
        # ZeroMQ
        self.zmq_context: Optional[zmq.asyncio.Context] = None
        self.zmq_socket: Optional[zmq.asyncio.Socket] = None
        
        # NATS
        self.nats_client: Optional[NATS] = None
        
        # Controle
    async def initialize(self):
        """Inicializa componentes"""
        logger.info("🚀 Inicializando Wake Word Detector...")
        
        # Inicializa OpenWakeWord
        try:
            self.oww_model = Model(
                wakeword_models=[settings.wake_word_keyword],
                inference_framework=settings.inference_framework
            )
            logger.info(f"✅ OpenWakeWord inicializado - Keyword: '{settings.wake_word_keyword}'")
            logger.info(f"   Chunk size: {self.chunk_size} samples")
            logger.info(f"   Sample rate: 16000 Hz")
            logger.info(f"   Inference framework: {settings.inference_framework}")
            logger.info(f"   Threshold: {settings.wake_word_threshold}")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar OpenWakeWord: {e}")
            raise
        
        # Inicializa ZeroMQ
        try:
            self.zmq_context = zmq.asyncio.Context()
            self.zmq_socket = self.zmq_context.socket(zmq.SUB)
            self.zmq_socket.connect(settings.zeromq_endpoint)
            self.zmq_socket.setsockopt_string(zmq.SUBSCRIBE, settings.zeromq_topic)
            logger.info(f"✅ ZeroMQ conectado: {settings.zeromq_endpoint}")
            logger.info(f"   Tópico: {settings.zeromq_topic}")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ZeroMQ: {e}")
            raise
        
        # Inicializa NATS
        try:
            self.nats_client = NATS()
            await self.nats_client.connect(settings.nats_url)
            logger.info(f"✅ NATS conectado: {settings.nats_url}")
            
            # Subscreve ao evento conversation.ended
            await self.nats_client.subscribe(
                settings.nats_subscribe_subject,
                cb=self._on_conversation_ended
            )
            logger.info(f"✅ Subscrito ao tópico: {settings.nats_subscribe_subject}")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar NATS: {e}")
            raise
        
        # Define estado inicial
        self.state = "IDLE"
        suppressed_state.set(0)
        logger.info("✅ Wake Word Detector pronto - Estado: IDLE")
        
    async def _on_conversation_ended(self, msg):
        """Callback quando conversa termina"""
        try:
            payload = json.loads(msg.data.decode())
            session_id = payload.get("session_id")
            
            logger.info(f"📥 Evento recebido: conversation.ended (session: {session_id})")
            conversation_ended_events_total.inc()
            
            # Se é a sessão atual, volta pro IDLE
            if session_id == self.current_session_id:
                # Calcula duração da supressão
                if self.suppression_start_time:
                    duration = time.time() - self.suppression_start_time
                    suppression_duration.observe(duration)
                    logger.info(f"⏱️  Supressão durou {duration:.2f}s")
                
                # Volta pro IDLE
                self.state = "IDLE"
                suppressed_state.set(0)
                self.current_session_id = None
                self.suppression_start_time = None
                logger.info("🟢 Estado: IDLE - Voltou a detectar wake word")
            else:
                logger.debug(f"Evento ignorado - session_id diferente: {session_id} != {self.current_session_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar conversation.ended: {e}")
    
    async def _check_suppression_timeout(self):
        """Verifica timeout de segurança da supressão"""
        while self.running:
            if self.state == "SUPPRESSED" and self.suppression_start_time:
                elapsed = time.time() - self.suppression_start_time
                
                if elapsed > self.max_suppression_timeout:
                    logger.warning(f"⚠️  Timeout de supressão atingido ({self.max_suppression_timeout}s)")
                    suppression_duration.observe(elapsed)
                    
                    # Força volta ao IDLE
                    self.state = "IDLE"
                    suppressed_state.set(0)
                    self.current_session_id = None
                    self.suppression_start_time = None
                    logger.info("🟢 Estado: IDLE (por timeout)")
            
            await asyncio.sleep(1)
    async def _process_audio_frame(self, audio_data: bytes):
        """Processa frame de áudio com OpenWakeWord"""
        
        # Se estiver suprimido, ignora
        if self.state == "SUPPRESSED":
            return
        
        try:
            start_time = time.time()
            
            # Converte bytes para numpy array int16
            pcm = np.frombuffer(audio_data, dtype=np.int16)
            
            # OpenWakeWord precisa de chunks de 1280 samples
            # Se receber menos, acumula (buffer interno do OpenWakeWord cuida disso)
            if len(pcm) < self.chunk_size:
                # Pad com zeros se necessário
                pcm = np.pad(pcm, (0, self.chunk_size - len(pcm)), mode='constant')
            
            # Processa com OpenWakeWord
            prediction = self.oww_model.predict(pcm)
            
            # Registra latência
            latency = time.time() - start_time
            processing_latency.observe(latency)
            
            # Verifica detecção
            for model_name, score in prediction.items():
                if score >= settings.wake_word_threshold:
                    await self._on_wake_word_detected(confidence=score)
                    break
                    
        except Exception as e:
            logger.error(f"❌ Erro ao processar frame: {e}")
    
    async def _on_wake_word_detected(self, confidence: float = 0.0):
        """Callback quando wake word é detectada"""
        timestamp = time.time()
        session_id = str(uuid.uuid4())
        
        logger.info(f"🎯 WAKE WORD DETECTADA! Session: {session_id}")
        logger.info(f"   Confiança: {confidence:.3f}")
        
        # Incrementa contador
        detections_total.inc()
        
        # Registra confiança
        confidence_histogram.observe(confidence)
        
        try:
            payload = {
                "timestamp": timestamp,
                "confidence": confidence,
                "keyword": settings.wake_word_keyword,
                "session_id": session_id,
                "detected_at": datetime.fromtimestamp(timestamp).isoformat()
            }
            
            await self.nats_client.publish(
                settings.nats_publish_subject,
                json.dumps(payload).encode()
            )
            
            logger.info(f"📤 Evento publicado: {settings.nats_publish_subject}")
            logger.debug(f"   Payload: {payload}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao publicar evento: {e}")
        
        # Entra em SUPPRESSED
        self.state = "SUPPRESSED"
        suppressed_state.set(1)
        self.current_session_id = session_id
        self.suppression_start_time = time.time()
        logger.info("🔴 Estado: SUPPRESSED - Aguardando conversation.ended")
    
    async def run(self):
        """Loop principal de processamento"""
        self.running = True
        
        # Inicia task de verificação de timeout
        timeout_task = asyncio.create_task(self._check_suppression_timeout())
        
        logger.info("🎧 Iniciando escuta de áudio...")
        logger.info(f"   Estado inicial: {self.state}")
        
        try:
            while self.running:
                # Recebe mensagem do ZeroMQ
                topic, audio_data = await self.zmq_socket.recv_multipart()
                
                # Processa frame
                await self._process_audio_frame(audio_data)
                
        except asyncio.CancelledError:
            logger.info("🛑 Processamento cancelado")
        except Exception as e:
            logger.error(f"❌ Erro no loop principal: {e}")
        finally:
            self.running = False
            timeout_task.cancel()
            await self.cleanup()
    
    async def cleanup(self):
        """Limpa recursos"""
        logger.info("🧹 Limpando recursos...")
        
        if self.oww_model:
            # OpenWakeWord não precisa de cleanup explícito
            self.oww_model = None
            logger.info("✅ OpenWakeWord finalizado")
        
        if self.zmq_socket:
            self.zmq_socket.close()
            logger.info("✅ ZeroMQ socket fechado")
        
        if self.zmq_context:
            self.zmq_context.term()
            logger.info("✅ ZeroMQ context finalizado")
        
        if self.nats_client and self.nats_client.is_connected:
            await self.nats_client.drain()
            logger.info("✅ NATS desconectado")
