#!/usr/bin/env python3
"""
Script de teste para enviar mensagem de overlap detection via NATS.
"""

import asyncio
import json
import base64
import numpy as np
from nats.aio.client import Client as NATS


async def generate_test_audio(duration: float = 2.5, sample_rate: int = 16000) -> bytes:
    """
    Gera áudio de teste com duas frequências simulando overlap.
    
    Args:
        duration: Duração em segundos
        sample_rate: Taxa de amostragem
        
    Returns:
        Áudio em bytes (PCM 16-bit)
    """
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


async def test_overlap_detection():
    """Testa o serviço enviando mensagem de overlap detection."""
    print("🔌 Conectando ao NATS...")
    
    nc = NATS()
    try:
        await nc.connect("nats://localhost:4222")
        print("✅ Conectado ao NATS")
        
        # Gerar áudio de teste
        print("🎵 Gerando áudio de teste...")
        audio_bytes = await generate_test_audio(duration=2.5)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Criar mensagem
        message = {
            "audio": audio_base64,
            "duration": 2.5,
            "speakers": ["user_1", "user_2"],
            "conversation_id": "test-overlap-123",
            "timestamp": 1732723200.123
        }
        
        print(f"📤 Enviando mensagem de overlap ({len(audio_bytes)} bytes)...")
        
        # Publicar
        await nc.publish(
            "audio.overlap_detected",
            json.dumps(message).encode()
        )
        
        print("✅ Mensagem enviada!")
        print("\n⏳ Aguardando resposta do serviço de separação...")
        
        # Subscrever ao resultado
        responses = []
        
        async def handler(msg):
            data = json.loads(msg.data.decode())
            responses.append(data)
            
            print("\n📥 Resposta recebida:")
            print(f"   Conversation ID: {data['conversation_id']}")
            print(f"   Duração original: {data['original_duration']}s")
            print(f"   Número de canais: {len(data['channels'])}")
            
            for i, channel in enumerate(data['channels']):
                print(f"\n   Canal {i + 1}:")
                print(f"      Speaker ID: {channel['speaker_id']}")
                print(f"      Confidence: {channel['confidence']:.2f}")
                print(f"      Audio size: {len(channel['audio'])} chars (base64)")
        
        await nc.subscribe("audio.separated", cb=handler)
        
        # Aguardar processamento (máximo 10 segundos)
        for i in range(10):
            await asyncio.sleep(1)
            if responses:
                break
            print(f"   Aguardando... {i + 1}s")
        
        if not responses:
            print("\n⚠️  Nenhuma resposta recebida. Verifique se o serviço está rodando.")
        else:
            print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    finally:
        await nc.close()
        print("\n🔌 Desconectado do NATS")


if __name__ == "__main__":
    print("=" * 60)
    print("  Source Separation - Script de Teste")
    print("=" * 60)
    print()
    
    asyncio.run(test_overlap_detection())
