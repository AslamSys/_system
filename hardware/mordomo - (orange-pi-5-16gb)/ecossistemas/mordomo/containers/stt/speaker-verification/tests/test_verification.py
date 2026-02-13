"""
Teste de verificação com voz cadastrada
Grava um novo áudio e testa se você é reconhecido
"""
import sys
import sounddevice as sd
import numpy as np
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from speaker_verifier import SpeakerVerifier
import yaml

SAMPLE_RATE = 16000
DURATION = 4  # segundos (Resemblyzer remove silêncios, então gravamos mais)

def record_test_audio():
    """Grava áudio de teste"""
    print("\n🎤 Preparando gravação de teste...")
    time.sleep(1)
    
    print(f"🔴 GRAVANDO {DURATION} segundos... FALE BASTANTE!")
    print("   (Continue falando durante toda a gravação)")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), 
                   samplerate=SAMPLE_RATE, 
                   channels=1, 
                   dtype=np.int16)
    sd.wait()
    print("✅ Gravação concluída!\n")
    
    # Converte para float32
    audio_float = audio.flatten().astype(np.float32) / 32768.0
    return audio_float


def main():
    print("=" * 60)
    print("🔐 TESTE DE VERIFICAÇÃO DE VOZ")
    print("=" * 60)
    
    # Carrega configuração
    print("\n1️⃣  Carregando configuração...")
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print(f"   Threshold: {config['verification']['threshold']}")
    print(f"   Usuários cadastrados: {len(config['users'])}")
    
    # Inicializa verificador
    print("\n2️⃣  Inicializando verificador...")
    verifier = SpeakerVerifier(config)
    stats = verifier.get_stats()
    print(f"   Embeddings carregados: {stats['users_enrolled']}")
    
    if stats['users_enrolled'] == 0:
        print("\n❌ ERRO: Nenhum embedding encontrado!")
        print("   Execute primeiro: python scripts/enroll_speaker.py")
        return
    
    print("\n3️⃣  Gravando sua voz para teste...")
    input("   Pressione ENTER quando estiver pronto...")
    
    audio = record_test_audio()
    
    # Verifica
    print("4️⃣  Verificando identidade...")
    is_verified, user_id, confidence = verifier.verify(audio, SAMPLE_RATE)
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO DA VERIFICAÇÃO")
    print("=" * 60)
    
    if is_verified:
        print(f"✅ VERIFICADO - Usuário reconhecido!")
        print(f"   User ID: {user_id}")
        print(f"   Confidence: {confidence:.3f}")
        
        # Encontra nome do usuário
        user = next((u for u in config['users'] if u['id'] == user_id), None)
        if user:
            print(f"   Nome: {user['name']}")
        
        print(f"\n🎉 Você foi autorizado a usar o sistema!")
    else:
        print(f"❌ REJEITADO - Voz não reconhecida")
        print(f"   Melhor similaridade: {confidence:.3f}")
        print(f"   Threshold necessário: {config['verification']['threshold']}")
        
        if confidence > 0:
            diff = config['verification']['threshold'] - confidence
            print(f"   Diferença: {diff:.3f} (faltou {diff:.1%} para passar)")
        
        print(f"\n⚠️  Acesso negado!")
    
    print("=" * 60)
    
    # Teste adicional
    print("\n\n🔄 Quer fazer outro teste? (s/n): ", end='')
    if input().lower() == 's':
        main()


if __name__ == "__main__":
    main()
