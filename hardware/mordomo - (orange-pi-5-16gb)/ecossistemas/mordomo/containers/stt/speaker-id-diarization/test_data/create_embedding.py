"""
Script para criar embeddings de teste.
Grava áudio do microfone e cria embeddings para usuários.
"""

import numpy as np
import sounddevice as sd
from resemblyzer import VoiceEncoder
from pathlib import Path
import argparse

SAMPLE_RATE = 16000
DURATION = 5  # segundos


def record_audio(duration: int = DURATION) -> np.ndarray:
    """Grava áudio do microfone."""
    print(f"🎤 Gravando {duration} segundos de áudio...")
    print("   Comece a falar!")
    
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    print("✅ Gravação concluída!")
    return audio.flatten()


def create_embedding(audio: np.ndarray, encoder: VoiceEncoder) -> np.ndarray:
    """Cria embedding do áudio."""
    print("🧠 Criando embedding...")
    embedding = encoder.embed_utterance(audio)
    print(f"✅ Embedding criado (shape: {embedding.shape})")
    return embedding


def save_embedding(embedding: np.ndarray, user_id: str, output_dir: Path):
    """Salva embedding em arquivo .npy."""
    output_path = output_dir / f"{user_id}.npy"
    np.save(output_path, embedding)
    print(f"💾 Embedding salvo: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Criar embedding de usuário")
    parser.add_argument(
        "user_id",
        type=str,
        help="ID do usuário (ex: user_1, user_2)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=DURATION,
        help="Duração da gravação em segundos"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./test_data/embeddings",
        help="Diretório de saída para embeddings"
    )
    
    args = parser.parse_args()
    
    # Setup
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"🎯 Criando embedding para: {args.user_id}")
    print(f"{'='*60}\n")
    
    # Initialize encoder
    print("🔧 Inicializando Voice Encoder...")
    encoder = VoiceEncoder()
    print("✅ Encoder inicializado!\n")
    
    # Record audio
    audio = record_audio(args.duration)
    
    # Create embedding
    embedding = create_embedding(audio, encoder)
    
    # Save embedding
    save_embedding(embedding, args.user_id, output_dir)
    
    print(f"\n{'='*60}")
    print(f"✅ Embedding criado com sucesso!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
