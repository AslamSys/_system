"""
Sistema de controle de interrupção para síntese TTS
Permite cancelar síntese quando usuário começa a falar
"""
import asyncio
from typing import Dict, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TTSInterruptionManager:
    """Gerencia interrupções de síntese TTS por speaker"""
    
    def __init__(self):
        self._interrupted: Dict[str, bool] = {}
        self._active_syntheses: Set[str] = set()
        self._lock = asyncio.Lock()
    
    async def start_synthesis(self, speaker_id: str):
        """Marca início de síntese para um speaker"""
        async with self._lock:
            self._interrupted[speaker_id] = False
            self._active_syntheses.add(speaker_id)
            logger.info(f"Started synthesis for {speaker_id}")
    
    async def interrupt(self, speaker_id: str):
        """Interrompe síntese em andamento"""
        async with self._lock:
            if speaker_id in self._active_syntheses:
                self._interrupted[speaker_id] = True
                logger.info(f"Interrupted synthesis for {speaker_id}")
                return True
            return False
    
    async def is_interrupted(self, speaker_id: str) -> bool:
        """Verifica se síntese foi interrompida"""
        return self._interrupted.get(speaker_id, False)
    
    async def end_synthesis(self, speaker_id: str):
        """Marca fim de síntese"""
        async with self._lock:
            self._active_syntheses.discard(speaker_id)
            self._interrupted.pop(speaker_id, None)
            logger.info(f"Ended synthesis for {speaker_id}")
    
    async def get_active_syntheses(self) -> Set[str]:
        """Retorna speakers com síntese ativa"""
        async with self._lock:
            return self._active_syntheses.copy()


# Instância global
interruption_manager = TTSInterruptionManager()
