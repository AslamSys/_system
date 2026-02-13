"""
gRPC service for Speaker Identification and Diarization.
Receives audio + transcript from Whisper ASR, processes, and returns results.
"""

import grpc
import asyncio
import structlog
import numpy as np
from concurrent import futures
from typing import Optional

from .config import GRPCConfig
from .speaker_identifier import SpeakerIdentifier, DiarizationResult
from .nats_client import NATSClient
from .metrics import speaker_diarization_latency_seconds

# Import generated protobuf classes
from . import speaker_id_pb2
from . import speaker_id_pb2_grpc

logger = structlog.get_logger(__name__)


class SpeakerIdentifierService(speaker_id_pb2_grpc.SpeakerIdentifierServicer):
    """gRPC service implementation."""
    
    def __init__(
        self,
        speaker_identifier: SpeakerIdentifier,
        nats_client: NATSClient
    ):
        self.speaker_identifier = speaker_identifier
        self.nats_client = nats_client
    
    async def DiarizeAudio(
        self,
        request: speaker_id_pb2.DiarizeRequest,
        context: grpc.aio.ServicerContext
    ) -> speaker_id_pb2.DiarizeResponse:
        """Process single audio request."""
        try:
            logger.info(
                "diarize_request_received",
                conversation_id=request.conversation_id,
                audio_size=len(request.audio),
                transcript_length=len(request.transcript)
            )
            
            # Convert audio bytes to numpy array (16kHz, mono, int16)
            audio_array = np.frombuffer(request.audio, dtype=np.int16)
            audio_array = audio_array.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
            
            # Process with speaker identifier
            with speaker_diarization_latency_seconds.time():
                result: DiarizationResult = await self.speaker_identifier.identify_and_diarize(
                    audio=audio_array,
                    transcript=request.transcript,
                    conversation_id=request.conversation_id
                )
            
            # Publish results to NATS (handles gate mechanism)
            for segment in result.segments:
                await self.nats_client.publish_diarization_result({
                    "speaker_id": segment.speaker_id,
                    "recognized": segment.recognized,
                    "confidence": segment.confidence,
                    "text": segment.text,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "overlap_detected": result.overlap_detected,
                    "timestamp": request.timestamp,
                    "conversation_id": request.conversation_id
                })
            
            # Trigger source separation if overlap detected
            if result.overlap_detected:
                await self.nats_client.trigger_source_separation(
                    request.audio,
                    request.conversation_id
                )
            
            # Build gRPC response
            response = speaker_id_pb2.DiarizeResponse(
                overlap_detected=result.overlap_detected,
                timestamp=request.timestamp,
                conversation_id=request.conversation_id
            )
            
            # Add segments
            for segment in result.segments:
                proto_segment = speaker_id_pb2.SpeakerSegment(
                    speaker_id=segment.speaker_id,
                    recognized=segment.recognized,
                    confidence=segment.confidence,
                    text=segment.text,
                    start_time=segment.start_time,
                    end_time=segment.end_time
                )
                response.segments.append(proto_segment)
            
            # Set first segment as primary (for backward compatibility)
            if result.segments:
                primary = result.segments[0]
                response.speaker_id = primary.speaker_id
                response.recognized = primary.recognized
                response.confidence = primary.confidence
                response.text = primary.text
                response.start_time = primary.start_time
                response.end_time = primary.end_time
            
            logger.info(
                "diarize_request_completed",
                conversation_id=request.conversation_id,
                segments=len(result.segments),
                overlap=result.overlap_detected,
                processing_time=f"{result.processing_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "diarize_request_failed",
                error=str(e),
                conversation_id=request.conversation_id
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Diarization failed: {str(e)}")
            raise
    
    async def DiarizeStream(
        self,
        request_iterator,
        context: grpc.aio.ServicerContext
    ):
        """Process streaming audio requests."""
        try:
            async for request in request_iterator:
                response = await self.DiarizeAudio(request, context)
                yield response
                
        except Exception as e:
            logger.error("stream_diarization_failed", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Stream diarization failed: {str(e)}")
            raise


class GRPCServer:
    """gRPC server wrapper."""
    
    def __init__(
        self,
        config: GRPCConfig,
        speaker_identifier: SpeakerIdentifier,
        nats_client: NATSClient
    ):
        self.config = config
        self.server: Optional[grpc.aio.Server] = None
        self.service = SpeakerIdentifierService(speaker_identifier, nats_client)
    
    async def start(self):
        """Start gRPC server."""
        try:
            self.server = grpc.aio.server(
                futures.ThreadPoolExecutor(max_workers=self.config.max_workers)
            )
            
            speaker_id_pb2_grpc.add_SpeakerIdentifierServicer_to_server(
                self.service,
                self.server
            )
            
            listen_addr = f"[::]:{self.config.port}"
            self.server.add_insecure_port(listen_addr)
            
            await self.server.start()
            
            logger.info(
                "grpc_server_started",
                address=listen_addr,
                max_workers=self.config.max_workers
            )
            
        except Exception as e:
            logger.error("grpc_server_start_failed", error=str(e))
            raise
    
    async def stop(self):
        """Stop gRPC server."""
        if self.server:
            await self.server.stop(grace=5)
            logger.info("grpc_server_stopped")
    
    async def wait_for_termination(self):
        """Wait for server termination."""
        if self.server:
            await self.server.wait_for_termination()
