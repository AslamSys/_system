from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações do Wake Word Detector"""
    
    # OpenWakeWord
    wake_word_model_path: str = "models/"  # Diretório com modelos .tflite ou .onnx
    wake_word_keyword: str = "alexa"  # Nome do modelo (sem extensão)
    wake_word_threshold: float = 0.5  # 0.0 a 1.0 (maior = menos falsos positivos)
    inference_framework: str = "onnx"  # "onnx" ou "tflite"
    
    # ZeroMQ
    zeromq_endpoint: str = "tcp://localhost:5555"
    zeromq_topic: str = "audio.raw"
    
    # NATS
    nats_url: str = "nats://localhost:4222"
    nats_publish_subject: str = "wake_word.detected"
    nats_subscribe_subject: str = "conversation.ended"
    
    # Audio
    sample_rate: int = 16000
    frame_length: int = 512
    
    # Metrics
    prometheus_port: int = 8001
    
    # Cooldown/Suppression
    max_suppression_timeout: int = 60  # segundos
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
