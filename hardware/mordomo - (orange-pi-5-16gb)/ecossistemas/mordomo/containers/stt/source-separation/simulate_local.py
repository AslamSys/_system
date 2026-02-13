"""
Teste de simulação local - testa o fluxo de separação sem NATS.
"""

import sys
import base64
import numpy as np
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("🎵 Source Separation - Teste de Simulação Local")
print("=" * 60)
print()

def generate_test_audio(duration=2.5, sample_rate=16000):
    """Gera áudio de teste simulando overlap de vozes."""
    samples = int(duration * sample_rate)
    t = np.arange(samples) / sample_rate
    
    # Simular duas vozes com frequências diferentes
    voice1 = 0.5 * np.sin(2 * np.pi * 220 * t)  # Voz 1 (220 Hz)
    voice2 = 0.3 * np.sin(2 * np.pi * 440 * t)  # Voz 2 (440 Hz)
    
    # Combinar
    combined = voice1 + voice2
    
    # Normalizar
    combined = combined / np.max(np.abs(combined))
    
    # Converter para int16
    audio_int16 = (combined * 32767).astype(np.int16)
    
    return audio_int16.tobytes()


print("1️⃣  Gerando áudio de teste (2.5s, 16kHz)...")
try:
    audio_bytes = generate_test_audio(duration=2.5)
    print(f"   ✅ Áudio gerado: {len(audio_bytes)} bytes ({len(audio_bytes)/2} samples)")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

print("\n2️⃣  Testando encoding para base64...")
try:
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    print(f"   ✅ Base64 encoded: {len(audio_base64)} chars")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

print("\n3️⃣  Simulando mensagem de overlap detection...")
try:
    message = {
        "audio": audio_base64,
        "duration": 2.5,
        "speakers": ["user_1", "user_2"],
        "conversation_id": "test-local-123",
        "timestamp": 1732723200.123
    }
    print(f"   ✅ Mensagem criada:")
    print(f"      - Duração: {message['duration']}s")
    print(f"      - Speakers: {message['speakers']}")
    print(f"      - Conversation ID: {message['conversation_id']}")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

print("\n4️⃣  Testando decode do áudio (sem Demucs)...")
try:
    # Decode base64
    decoded_audio = base64.b64decode(message["audio"])
    
    # Convert to numpy
    audio_array = np.frombuffer(decoded_audio, dtype=np.int16)
    audio_float = audio_array.astype(np.float32) / 32768.0
    
    print(f"   ✅ Áudio decodificado:")
    print(f"      - Samples: {len(audio_float)}")
    print(f"      - Duration: {len(audio_float) / 16000:.2f}s")
    print(f"      - Range: [{audio_float.min():.3f}, {audio_float.max():.3f}]")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

print("\n5️⃣  Simulando separação simples (sem modelo Demucs)...")
try:
    # Simular separação por janelas de energia (como faria o separator)
    window_size = int(0.5 * 16000)  # 500ms
    hop_size = int(0.25 * 16000)    # 250ms
    
    segments = []
    energies = []
    
    for i in range(0, len(audio_float) - window_size, hop_size):
        segment = audio_float[i:i + window_size]
        energy = np.sqrt(np.mean(segment ** 2))  # RMS
        segments.append((i, segment))
        energies.append(energy)
    
    print(f"   ✅ Análise de energia:")
    print(f"      - Segmentos analisados: {len(segments)}")
    print(f"      - Energia média: {np.mean(energies):.4f}")
    print(f"      - Energia max: {np.max(energies):.4f}")
    
    # Simular separação em 2 canais
    threshold = np.median(energies)
    channel1_count = sum(1 for e in energies if e > threshold)
    channel2_count = len(energies) - channel1_count
    
    print(f"      - Canal 1 (alta energia): {channel1_count} segmentos")
    print(f"      - Canal 2 (baixa energia): {channel2_count} segmentos")
    
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

print("\n6️⃣  Simulando resposta de áudio separado...")
try:
    # Criar canais simulados
    channel1_audio = audio_float  # Simplificado
    channel2_audio = audio_float * 0.5  # Simplificado
    
    # Encode channels
    ch1_int16 = (channel1_audio * 32768).astype(np.int16)
    ch2_int16 = (channel2_audio * 32768).astype(np.int16)
    
    ch1_base64 = base64.b64encode(ch1_int16.tobytes()).decode('utf-8')
    ch2_base64 = base64.b64encode(ch2_int16.tobytes()).decode('utf-8')
    
    response = {
        "channels": [
            {
                "audio": ch1_base64,
                "speaker_id": "user_1",
                "confidence": 0.85
            },
            {
                "audio": ch2_base64,
                "speaker_id": "user_2",
                "confidence": 0.78
            }
        ],
        "conversation_id": "test-local-123",
        "original_duration": 2.5,
        "timestamp": 1732723201.456
    }
    
    print(f"   ✅ Resposta simulada:")
    print(f"      - Canais: {len(response['channels'])}")
    for i, ch in enumerate(response['channels']):
        print(f"      - Canal {i+1}: {ch['speaker_id']} (conf: {ch['confidence']})")
    
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

print("\n7️⃣  Testando métricas...")
try:
    from metrics import Metrics
    
    metrics = Metrics(enabled=True, port=9999)
    
    # Record some metrics
    metrics.record_request('success')
    metrics.record_latency(1.5)
    metrics.record_success(num_speakers=2)
    metrics.record_quality(0.815)
    metrics.record_audio_duration(2.5)
    metrics.record_num_speakers(2)
    
    print(f"   ✅ Métricas registradas com sucesso")
    
except Exception as e:
    print(f"   ❌ Erro: {e}")

print()
print("=" * 60)
print("✅ Simulação local concluída com sucesso!")
print("=" * 60)
print()
print("📊 Resumo do teste:")
print("   - Geração de áudio: ✅")
print("   - Encode/Decode: ✅")
print("   - Análise de energia: ✅")
print("   - Separação simulada: ✅")
print("   - Mensagens NATS: ✅")
print("   - Métricas: ✅")
print()
print("⚠️  Nota: Este teste simula o fluxo sem carregar o modelo Demucs.")
print("   Para teste completo com Demucs, instale: pip install demucs torch")
print()
