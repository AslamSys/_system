"""
Script para criar embeddings com contexto expandido.
Grava 15 segundos com texto guiado para melhor qualidade.
"""

import numpy as np
import sounddevice as sd
from resemblyzer import VoiceEncoder
from pathlib import Path
import argparse
import time

SAMPLE_RATE = 16000


def print_script(user_id: str):
    """Mostra o texto para ser lido durante a gravação."""
    scripts = {
        "user_1": """
╔══════════════════════════════════════════════════════════════════╗
║                  TEXTO PARA LEITURA - USER_1                     ║
╔══════════════════════════════════════════════════════════════════╗

📖 Leia o seguinte texto de forma NATURAL e CLARA:

   "Olá, meu nome é [SEU NOME] e estou criando meu perfil de voz
    para o sistema Mordomo. Este assistente virtual vai me ajudar
    a controlar a casa através de comandos de voz. É importante que
    eu fale de forma natural, variando o tom e a velocidade, para
    que o sistema aprenda a reconhecer minha voz em diferentes
    situações. Vou falar alguns comandos comuns como: qual é a
    temperatura, desliga a luz da sala, toca música no quarto."

╚══════════════════════════════════════════════════════════════════╝
        """,
        "user_2": """
╔══════════════════════════════════════════════════════════════════╗
║                  TEXTO PARA LEITURA - USER_2                     ║
╔══════════════════════════════════════════════════════════════════╗

📖 Leia o seguinte texto de forma NATURAL e CLARA:

   "Oi, eu sou [SEU NOME] e também vou usar o sistema Mordomo.
    Estou gravando minha voz para que o assistente me reconheça
    quando eu falar com ele. É legal poder controlar as coisas da
    casa só com a voz. Vou testar comandos como: aumenta o volume,
    qual o clima para amanhã, acende a luz do jardim, e outras
    coisas do dia a dia. Quanto mais natural eu falar, melhor o
    sistema vai me entender."

╚══════════════════════════════════════════════════════════════════╝
        """
    }
    
    print(scripts.get(user_id, scripts["user_1"]))


def record_audio_with_countdown(duration: int = 15) -> np.ndarray:
    """Grava áudio com countdown e instruções."""
    print(f"\n{'='*60}")
    print(f"🎤 Gravação de {duration} segundos")
    print(f"{'='*60}\n")
    
    print("📋 INSTRUÇÕES:")
    print("   1. Leia o texto acima de forma NATURAL")
    print("   2. Não precisa gritar, tom de conversa normal")
    print("   3. Varie o tom e velocidade (evite monotonia)")
    print("   4. Se terminar antes, continue falando naturalmente\n")
    
    print("⏱️  Preparação:\n")
    for i in range(5, 0, -1):
        print(f"   Começando em {i}...")
        time.sleep(1)
    
    print("\n   🔴 GRAVANDO! Comece a ler agora!\n")
    
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32'
    )
    
    # Progress indicator
    for i in range(duration):
        time.sleep(1)
        remaining = duration - i - 1
        if remaining > 0:
            print(f"   ⏱️  {remaining}s restantes...", end='\r')
    
    sd.wait()
    print("\n\n   ✅ Gravação concluída!")
    
    return audio.flatten()


def create_embedding(audio: np.ndarray, encoder: VoiceEncoder) -> np.ndarray:
    """Cria embedding do áudio."""
    print("\n🧠 Criando embedding...")
    embedding = encoder.embed_utterance(audio)
    print(f"✅ Embedding criado (shape: {embedding.shape})")
    return embedding


def save_embedding(embedding: np.ndarray, user_id: str, output_dir: Path):
    """Salva embedding em arquivo .npy."""
    output_path = output_dir / f"{user_id}.npy"
    
    # Backup do anterior se existir
    if output_path.exists():
        backup_path = output_dir / f"{user_id}_backup.npy"
        output_path.rename(backup_path)
        print(f"📦 Backup do embedding anterior: {backup_path}")
    
    np.save(output_path, embedding)
    print(f"💾 Embedding salvo: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Criar embedding com contexto expandido")
    parser.add_argument(
        "user_id",
        type=str,
        help="ID do usuário (ex: user_1, user_2)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=15,
        help="Duração da gravação em segundos (default: 15)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./embeddings",
        help="Diretório de saída para embeddings"
    )
    
    args = parser.parse_args()
    
    # Setup
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"🎯 CRIANDO EMBEDDING EXPANDIDO PARA: {args.user_id}")
    print(f"{'='*70}\n")
    
    # Mostra o texto para leitura
    print_script(args.user_id)
    
    input("\n⏸️  Pressione ENTER quando estiver pronto para começar...")
    
    # Initialize encoder
    print("\n🔧 Inicializando Voice Encoder...")
    encoder = VoiceEncoder()
    print("✅ Encoder inicializado!\n")
    
    # Record audio
    audio = record_audio_with_countdown(args.duration)
    
    # Create embedding
    embedding = create_embedding(audio, encoder)
    
    # Save embedding
    save_embedding(embedding, args.user_id, output_dir)
    
    print(f"\n{'='*70}")
    print(f"✅ EMBEDDING EXPANDIDO CRIADO COM SUCESSO!")
    print(f"{'='*70}\n")
    print(f"📊 Qualidade esperada: ALTA (15s de contexto)")
    print(f"🎯 Próximo passo: Criar embedding do outro usuário")
    print(f"💡 Depois: python test_diarization.py --duration 10\n")


if __name__ == "__main__":
    main()
