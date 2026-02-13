"""
Speaker Verification Module
Usa Resemblyzer para verificar identidade de falante
"""
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
from typing import Tuple, Optional, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SpeakerVerifier:
    """
    Verifica se o áudio pertence a um usuário cadastrado
    """
    
    def __init__(self, config: Dict):
        """
        Inicializa o verificador de falante
        
        Args:
            config: Dicionário com configurações (threshold, users, etc)
        """
        self.config = config
        self.threshold = config['verification']['threshold']
        self.encoder = VoiceEncoder()
        self.embeddings = {}
        self.update_counters = {}
        
        # Carrega embeddings dos usuários cadastrados
        self._load_user_embeddings()
        
        logger.info(f"SpeakerVerifier initialized with {len(self.embeddings)} users")
    
    def _load_user_embeddings(self):
        """Carrega embeddings de todos os usuários cadastrados"""
        for user in self.config['users']:
            user_id = user['id']
            embedding_path = Path(user['embedding_path'])
            
            if embedding_path.exists():
                self.embeddings[user_id] = np.load(embedding_path)
                self.update_counters[user_id] = 0
                logger.info(f"Loaded embedding for {user['name']} ({user_id})")
            else:
                logger.warning(f"Embedding not found for {user['name']}: {embedding_path}")
    
    def verify(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Tuple[bool, Optional[str], float]:
        """
        Verifica se o áudio pertence a um usuário autorizado
        
        Args:
            audio_data: Array numpy com áudio (PCM 16-bit mono)
            sample_rate: Taxa de amostragem (default: 16000 Hz)
        
        Returns:
            Tuple (is_verified, user_id, confidence)
            - is_verified: True se autorizado, False caso contrário
            - user_id: ID do usuário identificado (None se rejeitado)
            - confidence: Score de similaridade (0.0 - 1.0)
        """
        try:
            # Preprocessa áudio
            wav = preprocess_wav(audio_data, sample_rate)
            
            # Verifica duração mínima
            min_duration = self.config['verification']['min_audio_duration']
            max_duration = self.config['verification']['max_audio_duration']
            duration = len(wav) / sample_rate
            
            if duration < min_duration or duration > max_duration:
                logger.warning(f"Audio duration {duration}s out of range [{min_duration}, {max_duration}]")
                return False, None, 0.0
            
            # Gera embedding do áudio
            embedding = self.encoder.embed_utterance(wav)
            
            # Compara com embeddings cadastrados
            best_match = None
            best_similarity = 0.0
            
            for user_id, user_embedding in self.embeddings.items():
                similarity = self._cosine_similarity(embedding, user_embedding)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = user_id
            
            # Verifica se passa o threshold
            is_verified = best_similarity >= self.threshold
            
            if is_verified:
                logger.info(f"Speaker verified: {best_match} (confidence: {best_similarity:.2f})")
                
                # Drift adaptation - atualiza embedding se muito similar
                if self.config.get('drift_adaptation', {}).get('enabled', False):
                    self._update_embedding_if_needed(best_match, embedding, best_similarity)
            else:
                logger.info(f"Speaker rejected: best match {best_match} with {best_similarity:.2f}")
            
            return is_verified, best_match if is_verified else None, best_similarity
            
        except Exception as e:
            logger.error(f"Error during verification: {e}")
            return False, None, 0.0
    
    def _cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcula similaridade cosine entre dois embeddings
        
        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding
        
        Returns:
            Similaridade (0.0 - 1.0)
        """
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _update_embedding_if_needed(self, user_id: str, new_embedding: np.ndarray, similarity: float):
        """
        Atualiza embedding do usuário se similaridade muito alta (drift adaptation)
        
        Args:
            user_id: ID do usuário
            new_embedding: Novo embedding capturado
            similarity: Similaridade com embedding atual
        """
        drift_config = self.config.get('drift_adaptation', {})
        update_threshold = drift_config.get('update_threshold', 0.85)
        max_updates = drift_config.get('max_updates_per_day', 10)
        
        # Só atualiza se similaridade muito alta e dentro do limite diário
        if similarity >= update_threshold and self.update_counters[user_id] < max_updates:
            # Média ponderada: 90% antigo, 10% novo
            old_embedding = self.embeddings[user_id]
            updated_embedding = 0.9 * old_embedding + 0.1 * new_embedding
            
            # Normaliza
            updated_embedding = updated_embedding / np.linalg.norm(updated_embedding)
            
            self.embeddings[user_id] = updated_embedding
            self.update_counters[user_id] += 1
            
            logger.info(f"Updated embedding for {user_id} (count: {self.update_counters[user_id]})")
            
            # Salva embedding atualizado
            user = next(u for u in self.config['users'] if u['id'] == user_id)
            np.save(user['embedding_path'], updated_embedding)
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas do verificador
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            'users_enrolled': len(self.embeddings),
            'threshold': self.threshold,
            'embedding_updates': dict(self.update_counters),
            'timestamp': datetime.now().isoformat()
        }
