"""
NATS client for Speaker ID/Diarization service.
Handles gate mechanism (buffering until speaker.verified) and publishes results.
"""

import asyncio
import json
import structlog
from typing import Optional, Dict, Any
from nats.aio.client import Client as NATS
from enum import Enum

from .config import NATSConfig

logger = structlog.get_logger(__name__)


class GateState(Enum):
    """Gate states for buffering mechanism."""
    IDLE = "idle"
    BUFFERING = "buffering"
    ANALYZING = "analyzing"


class NATSClient:
    """NATS client with gate mechanism for speaker verification."""
    
    def __init__(self, config: NATSConfig):
        self.config = config
        self.nc: Optional[NATS] = None
        self.gate_state = GateState.IDLE
        self.buffer: list[Dict[str, Any]] = []
        self.current_conversation_id: Optional[str] = None
        
    async def connect(self):
        """Connect to NATS server."""
        try:
            self.nc = NATS()
            await self.nc.connect(self.config.url)
            logger.info("connected_to_nats", url=self.config.url)
            
            # Subscribe to gate control events
            await self.nc.subscribe(
                self.config.subscribe_verified, 
                cb=self._on_speaker_verified
            )
            await self.nc.subscribe(
                self.config.subscribe_rejected, 
                cb=self._on_speaker_rejected
            )
            await self.nc.subscribe(
                self.config.subscribe_conversation_ended, 
                cb=self._on_conversation_ended
            )
            
            logger.info("subscribed_to_gate_events")
            
        except Exception as e:
            logger.error("nats_connection_failed", error=str(e))
            raise
    
    async def disconnect(self):
        """Disconnect from NATS server."""
        if self.nc:
            await self.nc.close()
            logger.info("disconnected_from_nats")
    
    async def _on_speaker_verified(self, msg):
        """Handle speaker.verified event - open gate."""
        try:
            data = json.loads(msg.data.decode())
            conversation_id = data.get("conversation_id")
            
            logger.info(
                "gate_opened",
                conversation_id=conversation_id,
                buffered_items=len(self.buffer)
            )
            
            self.gate_state = GateState.ANALYZING
            self.current_conversation_id = conversation_id
            
            # Publish all buffered results
            await self._flush_buffer()
            
        except Exception as e:
            logger.error("error_processing_verified", error=str(e))
    
    async def _on_speaker_rejected(self, msg):
        """Handle speaker.rejected event - discard buffer."""
        try:
            data = json.loads(msg.data.decode())
            conversation_id = data.get("conversation_id")
            
            logger.warning(
                "gate_rejected",
                conversation_id=conversation_id,
                discarded_items=len(self.buffer)
            )
            
            # Discard buffer
            self.buffer.clear()
            self.gate_state = GateState.IDLE
            self.current_conversation_id = None
            
        except Exception as e:
            logger.error("error_processing_rejected", error=str(e))
    
    async def _on_conversation_ended(self, msg):
        """Handle conversation.ended event - reset gate."""
        try:
            data = json.loads(msg.data.decode())
            conversation_id = data.get("conversation_id")
            
            logger.info(
                "conversation_ended",
                conversation_id=conversation_id,
                resetting_gate=True
            )
            
            # Reset to IDLE
            self.buffer.clear()
            self.gate_state = GateState.IDLE
            self.current_conversation_id = None
            
        except Exception as e:
            logger.error("error_processing_conversation_ended", error=str(e))
    
    async def publish_diarization_result(self, result: Dict[str, Any]):
        """
        Publish diarization result.
        If gate is closed (BUFFERING), store in buffer.
        If gate is open (ANALYZING), publish immediately.
        """
        try:
            if self.gate_state == GateState.IDLE:
                # Start buffering mode on first result
                self.gate_state = GateState.BUFFERING
                logger.info("gate_buffering_started")
            
            if self.gate_state == GateState.BUFFERING:
                # Store in buffer
                self.buffer.append(result)
                logger.debug(
                    "result_buffered",
                    speaker_id=result.get("speaker_id"),
                    buffer_size=len(self.buffer)
                )
                
            elif self.gate_state == GateState.ANALYZING:
                # Publish immediately
                await self._publish_result(result)
                
        except Exception as e:
            logger.error("error_publishing_result", error=str(e))
    
    async def _flush_buffer(self):
        """Flush all buffered results to NATS."""
        if not self.buffer:
            return
        
        logger.info("flushing_buffer", count=len(self.buffer))
        
        for result in self.buffer:
            await self._publish_result(result)
        
        self.buffer.clear()
        logger.info("buffer_flushed")
    
    async def _publish_result(self, result: Dict[str, Any]):
        """Publish a single result to NATS."""
        try:
            speaker_id = result.get("speaker_id")
            recognized = result.get("recognized", False)
            
            # Choose subject based on recognition
            if recognized:
                subject = self.config.publish_recognized.format(speaker_id=speaker_id)
            else:
                subject = self.config.publish_unknown
            
            # Publish to NATS
            await self.nc.publish(
                subject,
                json.dumps(result).encode()
            )
            
            logger.info(
                "result_published",
                subject=subject,
                speaker_id=speaker_id,
                recognized=recognized,
                confidence=result.get("confidence")
            )
            
        except Exception as e:
            logger.error("error_publishing_to_nats", error=str(e), result=result)
    
    async def trigger_source_separation(self, audio_data: bytes, conversation_id: str):
        """Trigger source separation when overlap detected."""
        try:
            payload = {
                "audio": audio_data.hex(),  # Convert bytes to hex string
                "conversation_id": conversation_id,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self.nc.publish(
                "audio.separation.trigger",
                json.dumps(payload).encode()
            )
            
            logger.info(
                "source_separation_triggered",
                conversation_id=conversation_id
            )
            
        except Exception as e:
            logger.error("error_triggering_separation", error=str(e))
