"""
Script para gravar amostras de voz para enrollment
Grava múltiplas amostras curtas da sua voz
"""
import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
from pathlib import Path
import time

SAMPLE_RATE = 16000
DURATION = 3  # segundos
NUM_SAMPLES = 5  # número de amostras

def record_sample(sample_num: int, output_dir: Path) -> str:
    """
    Grava uma amostra de áudio
    
    Args:
        sample_num: Número da amostra
        output_dir: Diretório para salvar
    
    Returns:
        Caminho do arquivo gravado
    """
    print(f"\n🎤 Amostra {sample_num}/{NUM_SAMPLES}")
    print("   Preparando...")
    time.sleep(1)
    
    print(f"   🔴 GRAVANDO {DURATION} segundos... FALE AGORA!")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), 
                   samplerate=SAMPLE_RATE, 
                   channels=1, 
                   dtype=np.int16)
    sd.wait()
    print("   ✅ Gravação concluída!")
    
    # Salva arquivo
    output_file = output_dir / f"sample_{sample_num}.wav"
    wavfile.write(output_file, SAMPLE_RATE, audio)
    
    return str(output_file)


def main():
    print("=" * 60)
    print("🎙️  GRAVAÇÃO DE AMOSTRAS DE VOZ PARA ENROLLMENT")
    print("=" * 60)
    print()
    print(f"Vamos gravar {NUM_SAMPLES} amostras de {DURATION} segundos cada.")
    print("Fale frases diferentes em cada gravação, como:")
    print("  - 'Olá Mordomo, como você está?'")
    print("  - 'Mordomo, qual é a previsão do tempo?'")
    print("  - 'Mordomo, me acorde às sete da manhã'")
    print("  - 'Mordomo, toque música relaxante'")
    print("  - 'Mordomo, desligue as luzes da sala'")
    print()
    
    # Cria diretório
    output_dir = Path("data/samples/user_1")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    input("Pressione ENTER quando estiver pronto para começar...")
    
    samples = []
    for i in range(1, NUM_SAMPLES + 1):
        try:
            sample_file = record_sample(i, output_dir)
            samples.append(sample_file)
            
            if i < NUM_SAMPLES:
                print("   Preparando próxima gravação...")
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n\n❌ Gravação cancelada!")
            return
        except Exception as e:
            print(f"\n❌ Erro na gravação: {e}")
            return
    
    print("\n" + "=" * 60)
    print("✅ GRAVAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"\n{len(samples)} amostras gravadas em: {output_dir}")
    print("\nArquivos criados:")
    for sample in samples:
        print(f"  - {Path(sample).name}")
    
    print("\n📝 Próximo passo: Executar enrollment")
    print("\nComando:")
    print(f'python scripts/enroll_speaker.py --user-id user_1 --name "Você" --audio-samples "{output_dir}/*.wav"')


if __name__ == "__main__":
    main()
