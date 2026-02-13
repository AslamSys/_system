#!/usr/bin/env python3
"""
Script de diagnóstico do microfone.
Testa se o microfone está capturando áudio corretamente.

Uso:
    python test_microphone.py [device_index]
"""

import sys
import sounddevice as sd
import numpy as np
import time

def test_microphone(device_index=None, duration=5):
    """
    Testa captura de áudio do microfone por alguns segundos.
    
    Args:
        device_index: Índice do dispositivo (None = padrão)
        duration: Duração do teste em segundos
    """
    print("=" * 70)
    print("🎤 TESTE DE MICROFONE")
    print("=" * 70)
    print()
    
    # Configurações
    sample_rate = 16000
    block_size = 480  # 30ms @ 16kHz
    
    if device_index is not None:
        device_info = sd.query_devices(device_index)
        print(f"Dispositivo: [{device_index}] {device_info['name']}")
    else:
        device_info = sd.query_devices(sd.default.device[0])
        print(f"Dispositivo: [default] {device_info['name']}")
    
    print(f"Sample Rate: {sample_rate} Hz")
    print(f"Block Size: {block_size} samples (30ms)")
    print()
    print(f"🎙️  FALE NO MICROFONE POR {duration} SEGUNDOS...")
    print("=" * 70)
    print()
    
    # Estatísticas
    max_rms = 0
    min_rms = 999999
    total_rms = 0
    frame_count = 0
    
    def callback(indata, frames, time_info, status):
        nonlocal max_rms, min_rms, total_rms, frame_count
        
        if status:
            print(f"⚠️  Status: {status}")
        
        # Converter para int16
        audio_data = (indata * 32767).astype(np.int16)
        
        # Calcular RMS
        rms = np.sqrt(np.mean(audio_data.astype(float) ** 2))
        energy = rms / 32767.0
        
        # Atualizar stats
        max_rms = max(max_rms, rms)
        min_rms = min(min_rms, rms)
        total_rms += rms
        frame_count += 1
        
        # Visualizar
        bars = int(energy * 50)
        bar_str = '█' * bars + '░' * (50 - bars)
        
        # Classificar nível
        if rms < 50:
            level = "🔇 MUITO BAIXO (aumente o volume!)"
        elif rms < 200:
            level = "🔉 Baixo"
        elif rms < 1000:
            level = "🔊 Bom"
        elif rms < 5000:
            level = "📢 Alto"
        else:
            level = "⚡ MUITO ALTO (pode clipar!)"
        
        print(f"\r[{bar_str}] RMS: {rms:6.0f} | Energia: {energy:.3f} | {level}", end='', flush=True)
    
    try:
        # Capturar áudio
        with sd.InputStream(
            device=device_index,
            channels=1,
            samplerate=sample_rate,
            blocksize=block_size,
            callback=callback,
            dtype=np.float32
        ):
            time.sleep(duration)
        
        print("\n")
        print("=" * 70)
        print("📊 RESULTADOS:")
        print("-" * 70)
        print(f"RMS Máximo:  {max_rms:.0f}")
        print(f"RMS Mínimo:  {min_rms:.0f}")
        print(f"RMS Médio:   {total_rms/frame_count:.0f}")
        print()
        
        # Diagnóstico
        avg_rms = total_rms / frame_count
        print("🔍 DIAGNÓSTICO:")
        print("-" * 70)
        
        if avg_rms < 50:
            print("❌ Microfone MUITO BAIXO!")
            print("   Soluções:")
            print("   1. Aumentar volume do microfone no Windows")
            print("   2. Falar mais próximo do microfone")
            print("   3. Verificar se microfone está mutado")
        elif avg_rms < 200:
            print("⚠️  Microfone um pouco baixo")
            print("   Recomendado: Aumentar volume em ~20-30%")
        elif avg_rms < 1000:
            print("✅ Nível IDEAL para VAD!")
            print("   O WebRTC VAD deve detectar voz corretamente")
        elif avg_rms < 5000:
            print("✅ Nível bom (um pouco alto)")
            print("   Funciona, mas pode reduzir volume se quiser")
        else:
            print("⚠️  Nível MUITO ALTO - risco de clipping!")
            print("   Recomendado: Reduzir volume do microfone")
        
        print()
        print("💡 REFERÊNCIA:")
        print("   RMS < 100:     VAD provavelmente não vai detectar")
        print("   RMS 100-500:   VAD pode detectar em modo 3 (agressivo)")
        print("   RMS 500-2000:  Ideal para VAD")
        print("   RMS > 5000:    Pode ter distorção")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print()
        print("Possíveis causas:")
        print("  - Dispositivo não existe ou não está acessível")
        print("  - Sample rate não suportado pelo dispositivo")
        print("  - Permissões de acesso ao microfone")

if __name__ == "__main__":
    device = None
    
    if len(sys.argv) > 1:
        try:
            device = int(sys.argv[1])
        except ValueError:
            print("Uso: python test_microphone.py [device_index]")
            sys.exit(1)
    
    test_microphone(device)
