#!/usr/bin/env python3
"""
Script helper para listar todos os dispositivos de áudio disponíveis.
Rode isso primeiro para descobrir qual microfone usar.

Uso:
    python list_devices.py
"""

import sounddevice as sd

def list_audio_devices():
    print("=" * 70)
    print("DISPOSITIVOS DE ÁUDIO DISPONÍVEIS")
    print("=" * 70)
    print()
    
    devices = sd.query_devices()
    
    # Dispositivos de entrada (microfones)
    print("📥 DISPOSITIVOS DE ENTRADA (Microfones):")
    print("-" * 70)
    input_found = False
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            input_found = True
            default_marker = " ⭐ (DEFAULT)" if i == sd.default.device[0] else ""
            print(f"[{i}] {dev['name']}{default_marker}")
            print(f"    Canais de entrada: {dev['max_input_channels']}")
            print(f"    Sample rate padrão: {dev['default_samplerate']} Hz")
            print(f"    Host API: {sd.query_hostapis(dev['hostapi'])['name']}")
            print()
    
    if not input_found:
        print("❌ Nenhum dispositivo de entrada encontrado!")
        print()
    
    # Dispositivos de saída (alto-falantes)
    print("📤 DISPOSITIVOS DE SAÍDA (Alto-falantes):")
    print("-" * 70)
    output_found = False
    for i, dev in enumerate(devices):
        if dev['max_output_channels'] > 0:
            output_found = True
            default_marker = " ⭐ (DEFAULT)" if i == sd.default.device[1] else ""
            print(f"[{i}] {dev['name']}{default_marker}")
            print(f"    Canais de saída: {dev['max_output_channels']}")
            print(f"    Sample rate padrão: {dev['default_samplerate']} Hz")
            print(f"    Host API: {sd.query_hostapis(dev['hostapi'])['name']}")
            print()
    
    if not output_found:
        print("❌ Nenhum dispositivo de saída encontrado!")
        print()
    
    # Informações do sistema
    print("=" * 70)
    print("CONFIGURAÇÃO DO SISTEMA:")
    print("-" * 70)
    print(f"Dispositivo de entrada padrão: {sd.default.device[0]}")
    print(f"Dispositivo de saída padrão: {sd.default.device[1]}")
    print(f"Sample rate padrão: {sd.default.samplerate} Hz")
    print(f"Canais padrão: {sd.default.channels}")
    print("=" * 70)
    
    # Dica
    print()
    print("💡 COMO USAR:")
    print("   Copie o número [X] do microfone desejado")
    print("   Cole em config/audio.yaml → audio.device.index")
    print()

if __name__ == "__main__":
    try:
        list_audio_devices()
    except Exception as e:
        print(f"❌ Erro ao listar dispositivos: {e}")
        print()
        print("Possíveis soluções:")
        print("  1. Instale as dependências: pip install sounddevice")
        print("  2. No Windows: Instale PortAudio")
        print("  3. No Linux: sudo apt-get install portaudio19-dev")
