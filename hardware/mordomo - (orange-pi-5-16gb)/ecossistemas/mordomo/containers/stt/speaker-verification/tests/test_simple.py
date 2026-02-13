"""
Teste simples para validar funcionamento básico
Pode ser executado sem NATS
"""
import sys
import numpy as np
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from speaker_verifier import SpeakerVerifier


def test_basic_functionality():
    """Teste básico de funcionamento"""
    print("🧪 Testing Speaker Verification Basic Functionality\n")
    
    # Configuração de teste
    config = {
        'verification': {
            'threshold': 0.75,
            'min_audio_duration': 1.0,
            'max_audio_duration': 3.0
        },
        'users': [],
        'drift_adaptation': {
            'enabled': False
        }
    }
    
    print("1️⃣  Initializing SpeakerVerifier...")
    verifier = SpeakerVerifier(config)
    print(f"   ✅ Initialized with threshold: {verifier.threshold}\n")
    
    print("2️⃣  Testing cosine similarity...")
    emb1 = np.array([1.0, 0.0, 0.0])
    emb2 = np.array([1.0, 0.0, 0.0])
    similarity = verifier._cosine_similarity(emb1, emb2)
    print(f"   Similarity between identical vectors: {similarity:.3f}")
    assert abs(similarity - 1.0) < 0.001, "Failed: identical vectors should have similarity 1.0"
    print("   ✅ Cosine similarity working correctly\n")
    
    print("3️⃣  Testing audio duration validation...")
    # Áudio muito curto (0.5s @ 16kHz)
    short_audio = np.random.randn(8000).astype(np.float32) * 0.1
    is_verified, user_id, confidence = verifier.verify(short_audio)
    print(f"   Short audio (0.5s): verified={is_verified}, user={user_id}, confidence={confidence:.3f}")
    assert not is_verified, "Failed: short audio should be rejected"
    print("   ✅ Duration validation working correctly\n")
    
    print("4️⃣  Testing normal audio (without enrolled users)...")
    # Áudio normal (1.5s @ 16kHz)
    normal_audio = np.random.randn(24000).astype(np.float32) * 0.1
    is_verified, user_id, confidence = verifier.verify(normal_audio)
    print(f"   Normal audio (1.5s): verified={is_verified}, user={user_id}, confidence={confidence:.3f}")
    assert not is_verified, "Failed: should be rejected (no enrolled users)"
    print("   ✅ Verification working correctly\n")
    
    print("5️⃣  Testing get_stats()...")
    stats = verifier.get_stats()
    print(f"   Stats: {stats}")
    assert 'users_enrolled' in stats
    assert 'threshold' in stats
    print("   ✅ Stats working correctly\n")
    
    print("=" * 60)
    print("✅ All basic tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_basic_functionality()
