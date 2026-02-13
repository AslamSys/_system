"""
Script para cadastrar (enroll) vozes de usuários
Gera embeddings médios de múltiplas amostras de áudio
"""
import argparse
import numpy as np
from pathlib import Path
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.io import wavfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def enroll_speaker(user_id: str, name: str, audio_samples: list, output_path: str):
    """
    Cadastra um falante gerando embedding médio de múltiplas amostras
    
    Args:
        user_id: ID do usuário (ex: user_1)
        name: Nome do usuário
        audio_samples: Lista de caminhos para arquivos .wav
        output_path: Caminho para salvar o embedding (.npy)
    """
    logger.info(f"🎙️  Enrolling speaker: {name} ({user_id})")
    logger.info(f"   Audio samples: {len(audio_samples)}")
    
    # Inicializa encoder
    encoder = VoiceEncoder()
    embeddings = []
    
    # Processa cada amostra
    for i, audio_path in enumerate(audio_samples, 1):
        try:
            logger.info(f"   Processing sample {i}/{len(audio_samples)}: {Path(audio_path).name}")
            
            # Carrega áudio
            sample_rate, wav_data = wavfile.read(audio_path)
            
            # Converte para float32
            if wav_data.dtype == np.int16:
                wav_data = wav_data.astype(np.float32) / 32768.0
            
            # Preprocessa
            wav = preprocess_wav(wav_data, sample_rate)
            
            # Gera embedding
            embedding = encoder.embed_utterance(wav)
            embeddings.append(embedding)
            
            logger.info(f"      ✅ Embedding shape: {embedding.shape}")
            
        except Exception as e:
            logger.error(f"      ❌ Error processing {audio_path}: {e}")
            continue
    
    if not embeddings:
        raise ValueError("No valid embeddings generated!")
    
    # Calcula embedding médio
    mean_embedding = np.mean(embeddings, axis=0)
    
    # Normaliza
    mean_embedding = mean_embedding / np.linalg.norm(mean_embedding)
    
    # Salva
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_file, mean_embedding)
    
    logger.info(f"✅ Enrollment completed!")
    logger.info(f"   Samples used: {len(embeddings)}")
    logger.info(f"   Embedding shape: {mean_embedding.shape}")
    logger.info(f"   Saved to: {output_file}")
    
    # Estatísticas
    embedding_array = np.array(embeddings)
    mean_similarity = np.mean([
        np.dot(embeddings[i], embeddings[j]) / 
        (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]))
        for i in range(len(embeddings))
        for j in range(i + 1, len(embeddings))
    ]) if len(embeddings) > 1 else 1.0
    
    logger.info(f"   Inter-sample similarity: {mean_similarity:.3f}")
    
    return mean_embedding


def main():
    parser = argparse.ArgumentParser(description='Enroll speaker for verification')
    parser.add_argument('--user-id', required=True, help='User ID (e.g., user_1)')
    parser.add_argument('--name', required=True, help='User name')
    parser.add_argument('--audio-samples', required=True, nargs='+', help='Audio sample files (.wav)')
    parser.add_argument('--output', help='Output path for embedding (.npy)')
    
    args = parser.parse_args()
    
    # Define output path se não fornecido
    if not args.output:
        args.output = f"data/embeddings/{args.user_id}.npy"
    
    # Verifica se arquivos existem
    audio_files = []
    for pattern in args.audio_samples:
        path = Path(pattern)
        if path.is_file():
            audio_files.append(str(path))
        elif '*' in pattern:
            # Glob pattern
            parent = path.parent
            audio_files.extend([str(p) for p in parent.glob(path.name)])
        else:
            logger.warning(f"File not found: {pattern}")
    
    if not audio_files:
        logger.error("No valid audio files found!")
        return
    
    # Cadastra falante
    enroll_speaker(args.user_id, args.name, audio_files, args.output)


if __name__ == "__main__":
    main()
