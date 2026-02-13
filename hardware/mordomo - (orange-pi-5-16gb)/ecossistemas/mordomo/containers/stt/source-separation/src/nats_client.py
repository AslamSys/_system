"""NATS client for Source Separation service."""

import asyncio
import json
import base64
import logging
from typing import Optional, Callable, Awaitable
from datetime import datetime

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

from .config import NATSConfig

logger = logging.getLogger(__name__)


class OverlapDetectedMessage:
    """Message received when overlap is detected."""
    
    def __init__(self, data: dict):
        self.audio = base64.b64decode(data["audio"])
        self.duration = data["duration"]
        self.speakers = data["speakers"]
        self.conversation_id = data["conversation_id"]
        self.timestamp = data["timestamp"]


class SeparatedAudioMessage:
    """Message to send with separated audio channels."""
    
    def __init__(
        self,
        channels: list,
        conversation_id: str,
        original_duration: float,
        timestamp: Optional[float] = None
    ):
        self.channels = channels
        self.conversation_id = conversation_id
        self.original_duration = original_duration
        self.timestamp = timestamp or datetime.now().timestamp()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "channels": self.channels,
            "conversation_id": self.conversation_id,
            "original_duration": self.original_duration,
            "timestamp": self.timestamp
        }


class NATSClient:
    """NATS client for pub/sub messaging."""
    
    def __init__(self, config: NATSConfig):
        """
        Initialize NATS client.
        
        Args:
            config: NATS configuration
        """
        self.config = config
        self.nc: Optional[NATS] = None
        self._connected = False
    
    async def connect(self):
        """Connect to NATS servers."""
        if self._connected:
            return
        
        logger.info(f"Connecting to NATS servers: {self.config.servers}")
        
        self.nc = NATS()
        
        try:
            await self.nc.connect(
                servers=self.config.servers,
                max_reconnect_attempts=self.config.connection.max_reconnect_attempts,
                reconnect_time_wait=self.config.connection.reconnect_time_wait,
            )
            
            self._connected = True
            logger.info("Successfully connected to NATS")
            
        except (ErrNoServers, ErrConnectionClosed) as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from NATS."""
        if self.nc and self._connected:
            logger.info("Disconnecting from NATS")
            await self.nc.drain()
            await self.nc.close()
            self._connected = False
    
    async def subscribe_overlap_detected(
        self,
        handler: Callable[[OverlapDetectedMessage], Awaitable[None]]
    ):
        """
        Subscribe to audio.overlap_detected messages.
        
        Args:
            handler: Async function to handle incoming messages
        """
        if not self._connected:
            await self.connect()
        
        subject = self.config.subjects.input
        logger.info(f"Subscribing to {subject}")
        
        async def message_handler(msg):
            try:
                # Parse JSON payload
                data = json.loads(msg.data.decode())
                
                # Create message object
                message = OverlapDetectedMessage(data)
                
                logger.info(
                    f"Received overlap detection for conversation {message.conversation_id}, "
                    f"duration: {message.duration}s, speakers: {len(message.speakers)}"
                )
                
                # Call handler
                await handler(message)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message: {e}")
            except Exception as e:
                logger.error(f"Error handling message: {e}", exc_info=True)
        
        await self.nc.subscribe(subject, cb=message_handler)
    
    async def publish_separated_audio(self, message: SeparatedAudioMessage):
        """
        Publish separated audio channels.
        
        Args:
            message: Separated audio message
        """
        if not self._connected:
            await self.connect()
        
        subject = self.config.subjects.output
        
        # Convert to JSON
        payload = json.dumps(message.to_dict()).encode()
        
        logger.info(
            f"Publishing {len(message.channels)} separated channels "
            f"for conversation {message.conversation_id}"
        )
        
        try:
            await self.nc.publish(subject, payload)
            logger.debug(f"Published to {subject}")
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self.nc is not None and not self.nc.is_closed
