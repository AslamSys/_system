"""
Demonstração completa do sistema de verificação de voz
"""
import sys
import sounddevice as sd
import numpy as np
from pathlib import Path
import time
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from speaker_verifier import SpeakerVerifier

SAMPLE_RATE = 16000
DURATION = 4


def test_with_recorded_sample(sample_path: str, verifier: SpeakerVerifier, config: dict):
    """Testa com uma amostra gravada"""
    from scipy.io import wavfile
    
    print(f"\n🔍 Testando com: {Path(sample_path).name}")
    
    # Carrega áudio
    sr, audio = wavfile.read(sample_path)
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    
    # Verifica
    is_verified, user_id, confidence = verifier.verify(audio, sr)
    
    # Resultado
    if is_verified:
        user = next((u for u in config['users'] if u['id'] == user_id), None)
        user_name = user['name'] if user else user_id
        print(f"   ✅ AUTORIZADO - {user_name} (confidence: {confidence:.3f})")
    else:
        print(f"   ❌ REJEITADO (confidence: {confidence:.3f})")
    
    return is_verified, confidence


def test_live_recording(verifier: SpeakerVerifier, config: dict):
    """Testa com gravação ao vivo"""
    print("\n🎤 Gravação ao vivo...")
    print(f"   🔴 Gravando {DURATION}s... FALE BASTANTE!")
    
    audio = sd.rec(int(DURATION * SAMPLE_RATE), 
                   samplerate=SAMPLE_RATE, 
                   channels=1, 
                   dtype=np.int16)
    sd.wait()
    
    # Converte
    audio_float = audio.flatten().astype(np.float32) / 32768.0
    
    # Verifica
    is_verified, user_id, confidence = verifier.verify(audio_float, SAMPLE_RATE)
    
    # Resultado
    if is_verified:
        user = next((u for u in config['users'] if u['id'] == user_id), None)
        user_name = user['name'] if user else user_id
        print(f"   ✅ AUTORIZADO - {user_name} (confidence: {confidence:.3f})")
    else:
        print(f"   ❌ REJEITADO (confidence: {confidence:.3f})")
    
    return is_verified, confidence


def main():
    print("=" * 70)
    print("🔐 DEMONSTRAÇÃO DO SISTEMA DE VERIFICAÇÃO DE VOZ")
    print("=" * 70)
    
    # Carrega configuração
    print("\n📋 Configuração:")
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"   Threshold de aceitação: {config['verification']['threshold']}")
    print(f"   Duração mínima: {config['verification']['min_audio_duration']}s")
    print(f"   Duração máxima: {config['verification']['max_audio_duration']}s")
    
    # Inicializa
    print("\n🚀 Inicializando verificador...")
    verifier = SpeakerVerifier(config)
    stats = verifier.get_stats()
    
    print(f"   Usuários cadastrados: {stats['users_enrolled']}")
    for user in config['users']:
        if user['id'] in verifier.embeddings:
            print(f"      ✅ {user['name']} ({user['id']})")
        else:
            print(f"      ⚠️  {user['name']} ({user['id']}) - sem embedding")
    
    # Testa com amostras existentes
    sample_dir = Path("data/samples/user_1")
    if sample_dir.exists():
        samples = list(sample_dir.glob("*.wav"))
        if samples:
            print(f"\n\n{'=' * 70}")
            print(f"📁 TESTE 1: Validando com amostras de enrollment ({len(samples)} arquivos)")
            print("=" * 70)
            
            verified_count = 0
            confidences = []
            
            for i, sample in enumerate(samples[:3], 1):  # Testa primeiras 3
                is_verified, confidence = test_with_recorded_sample(
                    str(sample), verifier, config
                )
                if is_verified:
                    verified_count += 1
                confidences.append(confidence)
                time.sleep(0.5)
            
            avg_confidence = np.mean(confidences)
            print(f"\n   📊 Resumo: {verified_count}/{len(samples[:3])} verificadas")
            print(f"   📈 Confiança média: {avg_confidence:.3f}")
    
    # Teste ao vivo
    print(f"\n\n{'=' * 70}")
    print("🎙️  TESTE 2: Gravação ao vivo")
    print("=" * 70)
    print("\nAgora vamos gravar sua voz em tempo real e verificar.")
    input("Pressione ENTER quando estiver pronto...")
    
    test_live_recording(verifier, config)
    
    # Estatísticas finais
    print(f"\n\n{'=' * 70}")
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 70)
    final_stats = verifier.get_stats()
    print(f"   Threshold: {final_stats['threshold']}")
    print(f"   Usuários: {final_stats['users_enrolled']}")
    print(f"   Updates de embeddings: {final_stats['embedding_updates']}")
    
    print(f"\n{'=' * 70}")
    print("✅ DEMONSTRAÇÃO CONCLUÍDA")
    print("=" * 70)


if __name__ == "__main__":
    main()
