"""
Configuration module for Speaker ID/Diarization service.
Loads settings from environment variables and provides configuration access.
"""

import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DiarizationConfig:
    """Diarization-specific configuration."""
    model: str
    min_speaker_duration: float
    max_speakers: int


@dataclass
class RecognitionConfig:
    """Speaker recognition configuration."""
    embeddings_path: str
    threshold: float
    unknown_detection: bool
    embedding_dimension: int


@dataclass
class OverlapConfig:
    """Overlap detection configuration."""
    detection_enabled: bool
    threshold: float
    min_duration: float


@dataclass
class SourceSeparationConfig:
    """Source separation configuration."""
    enabled: bool
    min_overlap_duration: float


@dataclass
class NATSConfig:
    """NATS messaging configuration."""
    url: str
    publish_recognized: str
    publish_unknown: str
    subscribe_verified: str
    subscribe_rejected: str
    subscribe_conversation_ended: str


@dataclass
class GRPCConfig:
    """gRPC server configuration."""
    port: int
    max_workers: int
    max_concurrent_requests: int


@dataclass
class MetricsConfig:
    """Prometheus metrics configuration."""
    port: int
    enabled: bool


@dataclass
class Config:
    """Main configuration container."""
    diarization: DiarizationConfig
    recognition: RecognitionConfig
    overlap: OverlapConfig
    source_separation: SourceSeparationConfig
    nats: NATSConfig
    grpc: GRPCConfig
    metrics: MetricsConfig
    log_level: str


def load_config() -> Config:
    """Load configuration from environment variables."""
    
    diarization = DiarizationConfig(
        model=os.getenv("DIARIZATION_MODEL", "pyannote/speaker-diarization-3.1"),
        min_speaker_duration=float(os.getenv("MIN_SPEAKER_DURATION", "1.0")),
        max_speakers=int(os.getenv("MAX_SPEAKERS", "3"))
    )
    
    recognition = RecognitionConfig(
        embeddings_path=os.getenv("EMBEDDINGS_PATH", "/data/embeddings"),
        threshold=float(os.getenv("RECOGNITION_THRESHOLD", "0.70")),
        unknown_detection=os.getenv("UNKNOWN_DETECTION", "true").lower() == "true",
        embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "256"))
    )
    
    overlap = OverlapConfig(
        detection_enabled=os.getenv("OVERLAP_DETECTION", "true").lower() == "true",
        threshold=float(os.getenv("OVERLAP_THRESHOLD", "0.5")),
        min_duration=float(os.getenv("OVERLAP_MIN_DURATION", "0.5"))
    )
    
    source_separation = SourceSeparationConfig(
        enabled=os.getenv("SOURCE_SEPARATION_ENABLED", "true").lower() == "true",
        min_overlap_duration=float(os.getenv("SOURCE_SEPARATION_MIN_OVERLAP", "0.5"))
    )
    
    nats = NATSConfig(
        url=os.getenv("NATS_URL", "nats://nats:4222"),
        publish_recognized="speech.diarized.{speaker_id}",
        publish_unknown="speech.diarized.unknown",
        subscribe_verified="speaker.verified",
        subscribe_rejected="speaker.rejected",
        subscribe_conversation_ended="conversation.ended"
    )
    
    grpc = GRPCConfig(
        port=int(os.getenv("GRPC_PORT", "50053")),
        max_workers=10,
        max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    )
    
    metrics = MetricsConfig(
        port=int(os.getenv("METRICS_PORT", "8003")),
        enabled=True
    )
    
    return Config(
        diarization=diarization,
        recognition=recognition,
        overlap=overlap,
        source_separation=source_separation,
        nats=nats,
        grpc=grpc,
        metrics=metrics,
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )
