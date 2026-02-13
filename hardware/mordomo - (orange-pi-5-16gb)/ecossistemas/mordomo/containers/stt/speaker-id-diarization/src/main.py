"""
Main entry point for Speaker ID/Diarization service.
Initializes all components and starts the server.
"""

import asyncio
import signal
import structlog
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .config import load_config
from .speaker_identifier import SpeakerIdentifier
from .nats_client import NATSClient
from .grpc_server import GRPCServer
from .metrics import MetricsCollector

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class EmbeddingsWatcher(FileSystemEventHandler):
    """Watch embeddings directory for changes and hot reload."""
    
    def __init__(self, speaker_identifier: SpeakerIdentifier):
        self.speaker_identifier = speaker_identifier
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.npy'):
            logger.info("new_embedding_detected", path=event.src_path)
            self.speaker_identifier.reload_embeddings()
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.npy'):
            logger.info("embedding_modified", path=event.src_path)
            self.speaker_identifier.reload_embeddings()
    
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.npy'):
            logger.info("embedding_deleted", path=event.src_path)
            self.speaker_identifier.reload_embeddings()


class SpeakerIDService:
    """Main service orchestrator."""
    
    def __init__(self):
        self.config = load_config()
        self.speaker_identifier: SpeakerIdentifier = None
        self.nats_client: NATSClient = None
        self.grpc_server: GRPCServer = None
        self.metrics_collector: MetricsCollector = None
        self.embeddings_observer: Observer = None
        self.shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """Initialize all components."""
        try:
            logger.info("initializing_speaker_id_service")
            
            # Start metrics server
            self.metrics_collector = MetricsCollector(self.config.metrics.port)
            if self.config.metrics.enabled:
                self.metrics_collector.start_server()
            
            # Initialize speaker identifier
            self.speaker_identifier = SpeakerIdentifier(
                diarization_config=self.config.diarization,
                recognition_config=self.config.recognition,
                overlap_config=self.config.overlap
            )
            
            # Initialize NATS client
            self.nats_client = NATSClient(self.config.nats)
            await self.nats_client.connect()
            
            # Initialize gRPC server
            self.grpc_server = GRPCServer(
                config=self.config.grpc,
                speaker_identifier=self.speaker_identifier,
                nats_client=self.nats_client
            )
            await self.grpc_server.start()
            
            # Start embeddings directory watcher
            self._start_embeddings_watcher()
            
            logger.info("speaker_id_service_initialized")
            
        except Exception as e:
            logger.error("initialization_failed", error=str(e))
            raise
    
    def _start_embeddings_watcher(self):
        """Start watching embeddings directory for changes."""
        try:
            embeddings_path = Path(self.config.recognition.embeddings_path)
            
            if not embeddings_path.exists():
                logger.warning(
                    "embeddings_directory_not_found_skipping_watcher",
                    path=str(embeddings_path)
                )
                return
            
            event_handler = EmbeddingsWatcher(self.speaker_identifier)
            self.embeddings_observer = Observer()
            self.embeddings_observer.schedule(
                event_handler,
                str(embeddings_path),
                recursive=False
            )
            self.embeddings_observer.start()
            
            logger.info(
                "embeddings_watcher_started",
                path=str(embeddings_path)
            )
            
        except Exception as e:
            logger.error("embeddings_watcher_failed", error=str(e))
    
    async def run(self):
        """Run the service."""
        try:
            # Setup signal handlers
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(
                    sig,
                    lambda: asyncio.create_task(self.shutdown())
                )
            
            logger.info("speaker_id_service_running")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error("service_error", error=str(e))
            raise
    
    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("shutting_down_speaker_id_service")
        
        # Stop embeddings watcher
        if self.embeddings_observer:
            self.embeddings_observer.stop()
            self.embeddings_observer.join()
        
        # Stop gRPC server
        if self.grpc_server:
            await self.grpc_server.stop()
        
        # Disconnect NATS
        if self.nats_client:
            await self.nats_client.disconnect()
        
        self.shutdown_event.set()
        logger.info("speaker_id_service_shutdown_complete")


async def main():
    """Main entry point."""
    service = SpeakerIDService()
    
    try:
        await service.initialize()
        await service.run()
    except KeyboardInterrupt:
        logger.info("received_keyboard_interrupt")
    except Exception as e:
        logger.error("service_fatal_error", error=str(e))
        raise
    finally:
        await service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
