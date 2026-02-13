"""
Script de teste para diarization com múltiplos falantes.
Grava áudio com dois ou mais falantes e testa a separação.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
from resemblyzer import VoiceEncoder
from pathlib import Path
import argparse
import json
from datetime import datetime

SAMPLE_RATE = 16000


def record_audio(duration: int) -> np.ndarray:
    """Grava áudio do microfone."""
    print(f"\n🎤 Gravando {duration} segundos de áudio...")
    print("   📢 IMPORTANTE: Duas ou mais pessoas devem falar durante a gravação!")
    print("   💡 Dica: Revezem ou falem ao mesmo tempo para testar overlap")
    print("\n   Começando em:")
    
    for i in range(3, 0, -1):
        print(f"   {i}...")
        sd.sleep(1000)
    
    print("   🔴 GRAVANDO!")
    
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    print("✅ Gravação concluída!")
    return audio.flatten()


def load_enrolled_embeddings(embeddings_dir: Path) -> dict:
    """Carrega embeddings cadastrados."""
    embeddings = {}
    
    print(f"\n📂 Carregando embeddings de: {embeddings_dir}")
    
    for embedding_file in embeddings_dir.glob("*.npy"):
        user_id = embedding_file.stem
        embedding = np.load(embedding_file)
        embeddings[user_id] = embedding
        print(f"   ✅ {user_id} (shape: {embedding.shape})")
    
    if not embeddings:
        print("   ⚠️  Nenhum embedding encontrado!")
        print(f"   💡 Execute: python test_data/create_embedding.py user_1")
    
    return embeddings


def simple_diarization(
    audio: np.ndarray,
    encoder: VoiceEncoder,
    enrolled_embeddings: dict,
    threshold: float = 0.70,
    segment_duration: float = 2.0
) -> list:
    """
    Diarization simplificado para teste.
    Divide áudio em segmentos e identifica cada um.
    """
    results = []
    segment_samples = int(segment_duration * SAMPLE_RATE)
    total_samples = len(audio)
    
    print(f"\n🔬 Processando áudio...")
    print(f"   Duração total: {total_samples / SAMPLE_RATE:.1f}s")
    print(f"   Segmentos de: {segment_duration}s")
    print(f"   Threshold: {threshold}\n")
    
    for start_sample in range(0, total_samples, segment_samples):
        end_sample = min(start_sample + segment_samples, total_samples)
        segment = audio[start_sample:end_sample]
        
        # Skip segments too short
        if len(segment) < SAMPLE_RATE * 0.5:
            continue
        
        start_time = start_sample / SAMPLE_RATE
        end_time = end_sample / SAMPLE_RATE
        
        # Create embedding
        segment_embedding = encoder.embed_utterance(segment)
        
        # Compare with enrolled
        similarities = {}
        for user_id, enrolled_emb in enrolled_embeddings.items():
            sim = np.dot(segment_embedding, enrolled_emb) / (
                np.linalg.norm(segment_embedding) * np.linalg.norm(enrolled_emb)
            )
            similarities[user_id] = sim
        
        # Find best match
        if similarities:
            best_user = max(similarities, key=similarities.get)
            confidence = similarities[best_user]
            
            if confidence >= threshold:
                speaker_id = best_user
                recognized = True
            else:
                speaker_id = f"unknown_{start_sample}"
                recognized = False
        else:
            speaker_id = "unknown"
            confidence = 0.0
            recognized = False
        
        result = {
            "start_time": float(start_time),
            "end_time": float(end_time),
            "speaker_id": speaker_id,
            "recognized": bool(recognized),
            "confidence": float(confidence),
            "similarities": {k: float(v) for k, v in similarities.items()}
        }
        
        results.append(result)
        
        # Print result
        emoji = "✅" if recognized else "⚠️"
        print(f"{emoji} [{start_time:.1f}s - {end_time:.1f}s] "
              f"{speaker_id} (conf: {confidence:.2f})")
        
        if similarities:
            for user_id, sim in similarities.items():
                print(f"      {user_id}: {sim:.3f}")
    
    return results


def analyze_results(results: list):
    """Analisa resultados da diarization."""
    print(f"\n{'='*60}")
    print("📊 ANÁLISE DOS RESULTADOS")
    print(f"{'='*60}\n")
    
    # Count speakers
    speakers = {}
    for r in results:
        speaker_id = r["speaker_id"]
        speakers[speaker_id] = speakers.get(speaker_id, 0) + 1
    
    print(f"🗣️  Falantes detectados: {len(speakers)}")
    for speaker_id, count in sorted(speakers.items(), key=lambda x: -x[1]):
        recognized = "cadastrado" if not speaker_id.startswith("unknown") else "desconhecido"
        print(f"   • {speaker_id} ({recognized}): {count} segmentos")
    
    # Check for speaker changes
    changes = 0
    for i in range(1, len(results)):
        if results[i]["speaker_id"] != results[i-1]["speaker_id"]:
            changes += 1
    
    print(f"\n🔄 Trocas de falante: {changes}")
    
    # Recognition rate
    recognized_count = sum(1 for r in results if r["recognized"])
    recognition_rate = recognized_count / len(results) * 100 if results else 0
    
    print(f"📈 Taxa de reconhecimento: {recognition_rate:.1f}%")
    print(f"   Reconhecidos: {recognized_count}/{len(results)} segmentos")


def main():
    parser = argparse.ArgumentParser(description="Testar diarization com múltiplos falantes")
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Duração da gravação em segundos (default: 10)"
    )
    parser.add_argument(
        "--embeddings-dir",
        type=str,
        default="./test_data/embeddings",
        help="Diretório com embeddings cadastrados"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./test_data/audio",
        help="Diretório para salvar áudio gravado"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.70,
        help="Threshold de reconhecimento (default: 0.70)"
    )
    parser.add_argument(
        "--segment-duration",
        type=float,
        default=2.0,
        help="Duração dos segmentos em segundos (default: 2.0)"
    )
    
    args = parser.parse_args()
    
    # Setup
    embeddings_dir = Path(args.embeddings_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print("🎯 TESTE DE DIARIZATION COM MÚLTIPLOS FALANTES")
    print(f"{'='*60}")
    
    # Load enrolled embeddings
    enrolled_embeddings = load_enrolled_embeddings(embeddings_dir)
    
    if not enrolled_embeddings:
        print("\n❌ Nenhum embedding cadastrado!")
        print("   Execute primeiro:")
        print("   python test_data/create_embedding.py user_1")
        print("   python test_data/create_embedding.py user_2")
        return
    
    # Initialize encoder
    print(f"\n🔧 Inicializando Voice Encoder...")
    encoder = VoiceEncoder()
    print("✅ Encoder inicializado!")
    
    # Record audio
    audio = record_audio(args.duration)
    
    # Save audio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = output_dir / f"test_multi_speaker_{timestamp}.wav"
    sf.write(audio_path, audio, SAMPLE_RATE)
    print(f"💾 Áudio salvo: {audio_path}")
    
    # Process diarization
    results = simple_diarization(
        audio,
        encoder,
        enrolled_embeddings,
        threshold=args.threshold,
        segment_duration=args.segment_duration
    )
    
    # Save results
    results_path = output_dir / f"results_{timestamp}.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"💾 Resultados salvos: {results_path}")
    
    # Analyze
    analyze_results(results)
    
    print(f"\n{'='*60}")
    print("✅ TESTE CONCLUÍDO!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
