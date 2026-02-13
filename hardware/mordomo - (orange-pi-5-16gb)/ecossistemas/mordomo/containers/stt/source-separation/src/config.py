"""Configuration module for Source Separation service."""

from typing import List, Optional
from pathlib import Path
import yaml
from pydantic import BaseModel, Field


class DemucsConfig(BaseModel):
    """Demucs model configuration."""
    model: str = "htdemucs_ft"
    device: str = "cpu"
    shifts: int = 1
    overlap: float = 0.25


class ProcessingConfig(BaseModel):
    """Audio processing configuration."""
    max_duration: float = 5.0
    batch_size: int = 1
    num_workers: int = 2


class TriggerConfig(BaseModel):
    """Trigger conditions configuration."""
    min_overlap_duration: float = 0.5
    confidence_threshold: float = 0.6


class NATSSubjectsConfig(BaseModel):
    """NATS subjects configuration."""
    input: str = "audio.overlap_detected"
    output: str = "audio.separated"


class NATSConnectionConfig(BaseModel):
    """NATS connection configuration."""
    max_reconnect_attempts: int = 10
    reconnect_time_wait: int = 2


class NATSConfig(BaseModel):
    """NATS messaging configuration."""
    servers: List[str] = Field(default_factory=lambda: ["nats://localhost:4222"])
    subjects: NATSSubjectsConfig = Field(default_factory=NATSSubjectsConfig)
    connection: NATSConnectionConfig = Field(default_factory=NATSConnectionConfig)


class MetricsConfig(BaseModel):
    """Prometheus metrics configuration."""
    port: int = 9090
    enabled: bool = True


class Config(BaseModel):
    """Main configuration for Source Separation service."""
    demucs: DemucsConfig = Field(default_factory=DemucsConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    trigger: TriggerConfig = Field(default_factory=TriggerConfig)
    nats: NATSConfig = Field(default_factory=NATSConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file. Defaults to config/config.yaml
        
    Returns:
        Config object with loaded settings
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    
    if not config_path.exists():
        # Return default config if file doesn't exist
        return Config()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
    
    return Config(**config_dict)


def get_config() -> Config:
    """Get singleton config instance."""
    if not hasattr(get_config, '_config'):
        get_config._config = load_config()
    return get_config._config
