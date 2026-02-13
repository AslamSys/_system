"""
Testes para o módulo de Speaker Verification
"""
import sys
import numpy as np
import pytest
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from speaker_verifier import SpeakerVerifier


@pytest.fixture
def mock_config():
    """Configuração mock para testes"""
    return {
        'verification': {
            'threshold': 0.75,
            'min_audio_duration': 1.0,
            'max_audio_duration': 3.0
        },
        'users': [
            {
                'id': 'user_1',
                'name': 'Test User 1',
                'embedding_path': 'data/embeddings/user_1.npy'
            },
            {
                'id': 'user_2',
                'name': 'Test User 2',
                'embedding_path': 'data/embeddings/user_2.npy'
            }
        ],
        'drift_adaptation': {
            'enabled': True,
            'update_threshold': 0.85,
            'max_updates_per_day': 10
        }
    }


@pytest.fixture
def sample_audio():
    """Gera áudio de teste (1 segundo de ruído branco)"""
    sample_rate = 16000
    duration = 1.0
    num_samples = int(sample_rate * duration)
    return np.random.randn(num_samples).astype(np.float32) * 0.1


def test_cosine_similarity():
    """Testa cálculo de similaridade cosine"""
    config = {
        'verification': {'threshold': 0.75, 'min_audio_duration': 1.0, 'max_audio_duration': 3.0},
        'users': [],
        'drift_adaptation': {'enabled': False}
    }
    
    verifier = SpeakerVerifier(config)
    
    # Embeddings idênticos
    emb1 = np.array([1.0, 0.0, 0.0])
    similarity = verifier._cosine_similarity(emb1, emb1)
    assert abs(similarity - 1.0) < 0.001, "Embeddings idênticos devem ter similaridade 1.0"
    
    # Embeddings ortogonais
    emb2 = np.array([0.0, 1.0, 0.0])
    similarity = verifier._cosine_similarity(emb1, emb2)
    assert abs(similarity - 0.0) < 0.001, "Embeddings ortogonais devem ter similaridade 0.0"
    
    # Embeddings opostos
    emb3 = np.array([-1.0, 0.0, 0.0])
    similarity = verifier._cosine_similarity(emb1, emb3)
    assert abs(similarity - (-1.0)) < 0.001, "Embeddings opostos devem ter similaridade -1.0"


def test_audio_duration_validation(mock_config, sample_audio):
    """Testa validação de duração do áudio"""
    verifier = SpeakerVerifier(mock_config)
    
    # Áudio muito curto (0.5s)
    short_audio = sample_audio[:8000]
    is_verified, user_id, confidence = verifier.verify(short_audio)
    assert not is_verified, "Áudio muito curto deve ser rejeitado"
    assert user_id is None
    assert confidence == 0.0
    
    # Áudio muito longo (4s)
    long_audio = np.concatenate([sample_audio] * 4)
    is_verified, user_id, confidence = verifier.verify(long_audio)
    assert not is_verified, "Áudio muito longo deve ser rejeitado"
    assert user_id is None
    assert confidence == 0.0


def test_verification_with_embeddings(mock_config, tmp_path):
    """Testa verificação com embeddings reais"""
    # Cria embeddings temporários
    embedding_dir = tmp_path / 'data' / 'embeddings'
    embedding_dir.mkdir(parents=True)
    
    # Cria embeddings aleatórios
    embedding_1 = np.random.randn(256).astype(np.float32)
    embedding_1 = embedding_1 / np.linalg.norm(embedding_1)
    
    embedding_2 = np.random.randn(256).astype(np.float32)
    embedding_2 = embedding_2 / np.linalg.norm(embedding_2)
    
    np.save(embedding_dir / 'user_1.npy', embedding_1)
    np.save(embedding_dir / 'user_2.npy', embedding_2)
    
    # Atualiza config com paths temporários
    mock_config['users'][0]['embedding_path'] = str(embedding_dir / 'user_1.npy')
    mock_config['users'][1]['embedding_path'] = str(embedding_dir / 'user_2.npy')
    
    verifier = SpeakerVerifier(mock_config)
    
    # Verifica que embeddings foram carregados
    assert len(verifier.embeddings) == 2
    assert 'user_1' in verifier.embeddings
    assert 'user_2' in verifier.embeddings


def test_get_stats(mock_config):
    """Testa obtenção de estatísticas"""
    verifier = SpeakerVerifier(mock_config)
    stats = verifier.get_stats()
    
    assert 'users_enrolled' in stats
    assert 'threshold' in stats
    assert 'embedding_updates' in stats
    assert 'timestamp' in stats
    assert stats['threshold'] == 0.75


def test_speaker_verifier_initialization(mock_config):
    """Testa inicialização do verificador"""
    verifier = SpeakerVerifier(mock_config)
    
    assert verifier.threshold == 0.75
    assert verifier.encoder is not None
    assert isinstance(verifier.embeddings, dict)
    assert isinstance(verifier.update_counters, dict)


def test_verification_returns_tuple(mock_config, sample_audio, tmp_path):
    """Testa que verify() retorna tupla correta"""
    # Cria embedding temporário
    embedding_dir = tmp_path / 'data' / 'embeddings'
    embedding_dir.mkdir(parents=True)
    
    embedding = np.random.randn(256).astype(np.float32)
    embedding = embedding / np.linalg.norm(embedding)
    np.save(embedding_dir / 'user_1.npy', embedding)
    
    mock_config['users'][0]['embedding_path'] = str(embedding_dir / 'user_1.npy')
    mock_config['users'][1]['embedding_path'] = 'nonexistent.npy'  # Não existe
    
    verifier = SpeakerVerifier(mock_config)
    result = verifier.verify(sample_audio)
    
    assert isinstance(result, tuple)
    assert len(result) == 3
    is_verified, user_id, confidence = result
    assert isinstance(is_verified, bool)
    assert user_id is None or isinstance(user_id, str)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
