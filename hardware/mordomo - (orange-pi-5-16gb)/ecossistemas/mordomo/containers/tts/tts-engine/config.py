from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """TTS Engine Configuration"""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8007
    
    # TTS Engine Selection
    tts_engine: Literal["piper", "coqui", "azure", "openai", "edge"] = "piper"
    
    # Azure Speech
    azure_speech_key1: str = ""
    azure_speech_key2: str = ""
    azure_speech_region: str = "brazilsouth"
    azure_speech_endpoint: str = ""
    azure_voice_name: str = "pt-BR-FranciscaNeural"  # Voz feminina BR
    
    # OpenAI TTS
    openai_api_key: str = ""
    openai_voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova"
    openai_model: str = "tts-1"  # tts-1 or tts-1-hd
    
    # Piper TTS (local)
    piper_model: str = "pt_BR-faber-medium"
    piper_speaker_id: int = 0
    
    # Coqui TTS (local)
    coqui_model: str = "tts_models/pt/cv/vits"
    
    # Audio output settings
    sample_rate: int = 22050
    channels: int = 1
    bit_depth: int = 16
    
    # Performance
    streaming_enabled: bool = True
    chunk_size: int = 4096
    max_latency_ms: int = 500
    
    # NATS
    nats_url: str = "nats://localhost:4222"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
