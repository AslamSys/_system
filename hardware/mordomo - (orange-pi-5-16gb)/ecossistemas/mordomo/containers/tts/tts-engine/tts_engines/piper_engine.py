"""
Piper TTS Engine - Fallback offline
Modelo: pt_BR-faber-medium.onnx (60.3 MB)
Latência: ~108ms (90-131ms)
"""
import io
import wave
from pathlib import Path
from typing import Optional
from piper import PiperVoice

class PiperTTSEngine:
    """Piper TTS Engine (offline fallback)"""
    
    # Modelo padrão
    MODELO_PADRAO = "pt_BR-faber-medium.onnx"
    SAMPLE_RATE = 22050
    
    def __init__(self, modelo_path: Optional[str] = None):
        """
        Inicializa Piper TTS Engine
        
        Args:
            modelo_path: Caminho para arquivo .onnx (opcional)
        """
        if modelo_path is None:
            modelo_path = str(Path.home() / f".local/share/piper-voices/{self.MODELO_PADRAO}")
        
        self.modelo_path = modelo_path
        self.voice = None
    
    def _load_voice(self):
        """Carrega o modelo de voz (lazy loading)"""
        if self.voice is None:
            self.voice = PiperVoice.load(self.modelo_path)
    
    async def synthesize_stream(self, text: str):
        """
        Sintetiza texto para áudio em streaming (memória)
        
        Args:
            text: Texto para sintetizar
            
        Yields:
            Chunks de áudio em bytes (WAV format)
        """
        self._load_voice()
        
        # Sintetiza o áudio
        chunks = [c.audio_int16_bytes for c in self.voice.synthesize(text)]
        audio_bytes = b''.join(chunks)
        
        # Cria WAV na memória
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.voice.config.sample_rate)
            wf.writeframes(audio_bytes)
        
        # Retorna áudio como stream
        wav_io.seek(0)
        chunk_size = 4096
        
        while True:
            chunk = wav_io.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
    async def synthesize(self, text: str) -> bytes:
        """
        Sintetiza texto completo e retorna áudio
        
        Args:
            text: Texto para sintetizar
            
        Returns:
            Áudio completo em bytes (WAV format)
        """
        chunks = []
        async for chunk in self.synthesize_stream(text):
            chunks.append(chunk)
        return b''.join(chunks)
