"""Main application for Source Separation service."""

import asyncio
import logging
import signal
import sys
import time
from typing import Optional

import structlog

from .config import get_config
from .separator import SourceSeparationService
from .nats_client import NATSClient, OverlapDetectedMessage, SeparatedAudioMessage
from .metrics import initialize_metrics, get_metrics

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


class SourceSeparationApp:
    """Main application orchestrating all components."""
    
    def __init__(self):
        """Initialize application."""
        self.config = get_config()
        self.separator: Optional[SourceSeparationService] = None
        self.nats_client: Optional[NATSClient] = None
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("shutdown_signal_received", signal=signum)
        self.running = False
    
    async def initialize(self):
        """Initialize all services."""
        logger.info("initializing_application")
        
        # Initialize metrics
        metrics = initialize_metrics(
            enabled=self.config.metrics.enabled,
            port=self.config.metrics.port
        )
        metrics.start_server()
        
        # Initialize separator (lazy load model)
        self.separator = SourceSeparationService(
            demucs_config=self.config.demucs,
            processing_config=self.config.processing
        )
        
        # Initialize NATS client
        self.nats_client = NATSClient(self.config.nats)
        await self.nats_client.connect()
        
        logger.info("application_initialized")
    
    async def handle_overlap_detection(self, message: OverlapDetectedMessage):
        """
        Handle incoming overlap detection message.
        
        Args:
            message: Overlap detection message from NATS
        """
        metrics = get_metrics()
        
        # Track processing
        metrics.increment_processing()
        metrics.record_num_speakers(len(message.speakers))
        metrics.record_audio_duration(message.duration)
        
        start_time = time.time()
        
        try:
            logger.info(
                "processing_overlap",
                conversation_id=message.conversation_id,
                duration=message.duration,
                num_speakers=len(message.speakers)
            )
            
            # Validate minimum duration
            if message.duration < self.config.trigger.min_overlap_duration:
                logger.warning(
                    "audio_too_short",
                    duration=message.duration,
                    min_duration=self.config.trigger.min_overlap_duration
                )
                metrics.record_request(status='skipped')
                return
            
            # Separate audio
            channels = self.separator.separate_audio(
                audio_data=message.audio,
                sample_rate=16000,  # As per spec
                speakers=message.speakers,
                duration=message.duration
            )
            
            # Encode channels for transmission
            encoded_channels = []
            total_confidence = 0.0
            
            for channel in channels:
                encoded_audio = self.separator.encode_audio(
                    channel.audio,
                    sample_rate=16000
                )
                
                encoded_channels.append({
                    "audio": encoded_audio,
                    "speaker_id": channel.speaker_id,
                    "confidence": channel.confidence
                })
                
                total_confidence += channel.confidence
            
            # Calculate average confidence
            avg_confidence = total_confidence / len(channels) if channels else 0.0
            
            # Create response message
            response = SeparatedAudioMessage(
                channels=encoded_channels,
                conversation_id=message.conversation_id,
                original_duration=message.duration,
                timestamp=message.timestamp
            )
            
            # Publish to NATS
            await self.nats_client.publish_separated_audio(response)
            
            # Record metrics
            elapsed = time.time() - start_time
            metrics.record_latency(elapsed)
            metrics.record_request(status='success')
            metrics.record_success(len(channels))
            metrics.record_quality(avg_confidence)
            
            logger.info(
                "separation_completed",
                conversation_id=message.conversation_id,
                num_channels=len(channels),
                latency=elapsed,
                avg_confidence=avg_confidence
            )
            
        except Exception as e:
            logger.error(
                "separation_failed",
                conversation_id=message.conversation_id,
                error=str(e),
                exc_info=True
            )
            metrics.record_request(status='error')
            
        finally:
            metrics.decrement_processing()
    
    async def run(self):
        """Run the application."""
        await self.initialize()
        
        # Subscribe to overlap detection
        await self.nats_client.subscribe_overlap_detected(
            handler=self.handle_overlap_detection
        )
        
        logger.info("service_started", subjects={
            "input": self.config.nats.subjects.input,
            "output": self.config.nats.subjects.output
        })
        
        self.running = True
        
        # Keep running until shutdown signal
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("service_cancelled")
        
        # Cleanup
        await self.shutdown()
    
    async def shutdown(self):
        """Shutdown application gracefully."""
        logger.info("shutting_down")
        
        if self.nats_client:
            await self.nats_client.disconnect()
        
        logger.info("shutdown_complete")


async def main():
    """Main entry point."""
    app = SourceSeparationApp()
    
    try:
        await app.run()
    except KeyboardInterrupt:
        logger.info("keyboard_interrupt")
    except Exception as e:
        logger.error("application_error", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
