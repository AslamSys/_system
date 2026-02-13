"""
Teste de diarization com segmentação dinâmica (baseada em pausas/silêncio).
Não corta em intervalos fixos - respeita o fluxo natural da fala.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
from resemblyzer import VoiceEncoder
from pathlib import Path
import argparse
import json
from datetime import datetime
import webrtcvad

SAMPLE_RATE = 16000


def record_audio(duration: int) -> np.ndarray:
    """Grava áudio do microfone."""
    print(f"\n🎤 Gravando {duration} segundos de áudio...")
    print("   💬 Conversem naturalmente - sem se preocupar com tempo!")
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
        if user_id.endswith("_backup"):
            continue
        embedding = np.load(embedding_file)
        embeddings[user_id] = embedding
        print(f"   ✅ {user_id} (shape: {embedding.shape})")
    
    return embeddings


def detect_speech_segments(audio: np.ndarray, aggressiveness: int = 2) -> list:
    """
    Detecta segmentos de fala usando VAD (Voice Activity Detection).
    Retorna lista de (start_time, end_time) para cada segmento de fala.
    """
    vad = webrtcvad.Vad(aggressiveness)  # 0-3, quanto maior mais agressivo
    
    # Converte para int16 para o VAD
    audio_int16 = (audio * 32768).astype(np.int16)
    
    # Frame de 30ms (480 samples a 16kHz)
    frame_duration_ms = 30
    frame_size = int(SAMPLE_RATE * frame_duration_ms / 1000)
    
    segments = []
    is_speech = False
    segment_start = None
    
    print(f"\n🔍 Detectando segmentos de fala (VAD)...")
    
    for i in range(0, len(audio_int16) - frame_size, frame_size):
        frame = audio_int16[i:i + frame_size].tobytes()
        
        try:
            voice_detected = vad.is_speech(frame, SAMPLE_RATE)
            
            if voice_detected and not is_speech:
                # Início de fala
                segment_start = i / SAMPLE_RATE
                is_speech = True
            elif not voice_detected and is_speech:
                # Fim de fala
                segment_end = i / SAMPLE_RATE
                if segment_end - segment_start > 0.5:  # Mínimo 0.5s
                    segments.append((segment_start, segment_end))
                is_speech = False
        except:
            pass
    
    # Último segmento se terminou falando
    if is_speech and segment_start is not None:
        segments.append((segment_start, len(audio_int16) / SAMPLE_RATE))
    
    print(f"   ✅ {len(segments)} segmentos de fala detectados")
    
    return segments


def dynamic_diarization(
    audio: np.ndarray,
    encoder: VoiceEncoder,
    enrolled_embeddings: dict,
    threshold: float = 0.70
) -> list:
    """
    Diarization com segmentação dinâmica baseada em VAD.
    """
    results = []
    
    # Detecta segmentos de fala
    speech_segments = detect_speech_segments(audio)
    
    if not speech_segments:
        print("\n⚠️  Nenhum segmento de fala detectado!")
        return results
    
    print(f"\n🔬 Processando {len(speech_segments)} segmentos...")
    print(f"   Threshold: {threshold}\n")
    
    for idx, (start_time, end_time) in enumerate(speech_segments, 1):
        start_sample = int(start_time * SAMPLE_RATE)
        end_sample = int(end_time * SAMPLE_RATE)
        segment = audio[start_sample:end_sample]
        
        duration = end_time - start_time
        
        # Cria embedding do segmento
        try:
            segment_embedding = encoder.embed_utterance(segment)
        except:
            print(f"⚠️  Segmento {idx} muito curto, ignorando...")
            continue
        
        # Compara com embeddings cadastrados
        similarities = {}
        for user_id, enrolled_emb in enrolled_embeddings.items():
            sim = np.dot(segment_embedding, enrolled_emb) / (
                np.linalg.norm(segment_embedding) * np.linalg.norm(enrolled_emb)
            )
            similarities[user_id] = sim
        
        # Encontra melhor match
        if similarities:
            best_user = max(similarities, key=similarities.get)
            confidence = similarities[best_user]
            
            if confidence >= threshold:
                speaker_id = best_user
                recognized = True
            else:
                speaker_id = f"unknown_{int(start_time * 1000)}"
                recognized = False
        else:
            speaker_id = "unknown"
            confidence = 0.0
            recognized = False
        
        result = {
            "segment": idx,
            "start_time": float(start_time),
            "end_time": float(end_time),
            "duration": float(duration),
            "speaker_id": speaker_id,
            "recognized": bool(recognized),
            "confidence": float(confidence),
            "similarities": {k: float(v) for k, v in similarities.items()}
        }
        
        results.append(result)
        
        # Print resultado
        emoji = "✅" if recognized else "⚠️"
        print(f"{emoji} Seg {idx}: [{start_time:.1f}s - {end_time:.1f}s] ({duration:.1f}s) "
              f"→ {speaker_id} (conf: {confidence:.2f})")
        
        if similarities:
            for user_id, sim in similarities.items():
                indicator = "👉" if user_id == speaker_id else "  "
                print(f"      {indicator} {user_id}: {sim:.3f}")
    
    return results


def analyze_results(results: list):
    """Analisa resultados da diarization."""
    print(f"\n{'='*60}")
    print("📊 ANÁLISE DOS RESULTADOS")
    print(f"{'='*60}\n")
    
    if not results:
        print("⚠️  Nenhum resultado para analisar")
        return
    
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
            print(f"\n   🔄 Troca {changes}: {results[i-1]['speaker_id']} → {results[i]['speaker_id']}")
            print(f"      Tempo: {results[i]['start_time']:.1f}s")
    
    print(f"\n🔄 Total de trocas de falante: {changes}")
    
    # Recognition rate
    recognized_count = sum(1 for r in results if r["recognized"])
    recognition_rate = recognized_count / len(results) * 100 if results else 0
    
    print(f"📈 Taxa de reconhecimento: {recognition_rate:.1f}%")
    print(f"   Reconhecidos: {recognized_count}/{len(results)} segmentos")
    
    # Duração total por falante
    print(f"\n⏱️  Tempo de fala por pessoa:")
    speaker_time = {}
    for r in results:
        speaker_id = r["speaker_id"]
        duration = r["duration"]
        speaker_time[speaker_id] = speaker_time.get(speaker_id, 0) + duration
    
    for speaker_id, total_time in sorted(speaker_time.items(), key=lambda x: -x[1]):
        print(f"   • {speaker_id}: {total_time:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="Teste de diarization com segmentação dinâmica")
    parser.add_argument(
        "--duration",
        type=int,
        default=15,
        help="Duração da gravação em segundos (default: 15)"
    )
    parser.add_argument(
        "--embeddings-dir",
        type=str,
        default="./embeddings",
        help="Diretório com embeddings cadastrados"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./audio",
        help="Diretório para salvar áudio gravado"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.70,
        help="Threshold de reconhecimento (default: 0.70)"
    )
    parser.add_argument(
        "--vad-aggressiveness",
        type=int,
        default=2,
        choices=[0, 1, 2, 3],
        help="Agressividade do VAD (0=permissivo, 3=agressivo, default: 2)"
    )
    
    args = parser.parse_args()
    
    # Setup
    embeddings_dir = Path(args.embeddings_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print("🎯 TESTE DE DIARIZATION COM SEGMENTAÇÃO DINÂMICA")
    print(f"{'='*60}")
    
    # Load enrolled embeddings
    enrolled_embeddings = load_enrolled_embeddings(embeddings_dir)
    
    if not enrolled_embeddings:
        print("\n❌ Nenhum embedding cadastrado!")
        return
    
    # Initialize encoder
    print(f"\n🔧 Inicializando Voice Encoder...")
    encoder = VoiceEncoder()
    print("✅ Encoder inicializado!")
    
    # Record audio
    audio = record_audio(args.duration)
    
    # Save audio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = output_dir / f"test_dynamic_{timestamp}.wav"
    sf.write(audio_path, audio, SAMPLE_RATE)
    print(f"💾 Áudio salvo: {audio_path}")
    
    # Process diarization with dynamic segmentation
    results = dynamic_diarization(
        audio,
        encoder,
        enrolled_embeddings,
        threshold=args.threshold
    )
    
    # Save results
    results_path = output_dir / f"results_dynamic_{timestamp}.json"
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
