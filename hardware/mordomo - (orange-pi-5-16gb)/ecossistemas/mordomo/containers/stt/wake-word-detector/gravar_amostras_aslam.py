"""
Script para gravar amostras de áudio para treinar modelo "ASLAM"
Facilita a coleta de amostras positivas e negativas
"""
import os
import time
import wave
import argparse
from datetime import datetime
import pyaudio
import numpy as np


class GravadorAmostras:
    """Grava amostras de áudio para treinamento"""
    
    def __init__(self, tipo: str, duracao: int = 2):
        self.tipo = tipo  # 'positive' ou 'negative'
        self.duracao = duracao
        self.sample_rate = 16000
        self.channels = 1
        self.chunk = 1024
        
        # Cria diretórios
        self.output_dir = f"training_data/{tipo}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # PyAudio
        self.pa = pyaudio.PyAudio()
        
    def gravar_amostra(self, numero: int):
        """Grava uma amostra de áudio"""
        
        # Nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.tipo == "positive":
            filename = f"aslam_{numero:03d}_{timestamp}.wav"
        else:
            filename = f"background_{numero:03d}_{timestamp}.wav"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Abre stream
        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        print(f"\n{'='*60}")
        if self.tipo == "positive":
            print(f"🎤 AMOSTRA #{numero} - Fale 'ASLAM' quando começar a gravar")
        else:
            print(f"🎤 AMOSTRA #{numero} - Fale qualquer coisa EXCETO 'ASLAM'")
        print(f"{'='*60}")
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"   {i}...", end='\r')
            time.sleep(1)
        
        print("   🔴 GRAVANDO...", end='\r')
        
        # Grava
        frames = []
        for _ in range(0, int(self.sample_rate / self.chunk * self.duracao)):
            data = stream.read(self.chunk, exception_on_overflow=False)
            frames.append(data)
        
        print("   ✅ GRAVADO!   ")
        
        # Para stream
        stream.stop_stream()
        stream.close()
        
        # Salva WAV
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Calcula volume (para validar)
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        volume_rms = np.sqrt(np.mean(audio_data**2))
        
        print(f"   💾 Salvo: {filename}")
        print(f"   📊 Volume RMS: {volume_rms:.0f}")
        
        if volume_rms < 500:
            print("   ⚠️  AVISO: Volume muito baixo! Fale mais alto ou chegue mais perto.")
        
        return filepath
    
    def gravar_multiplas(self, quantidade: int, intervalo: int = 2):
        """Grava múltiplas amostras"""
        
        print("\n" + "🎙️ "*30)
        print("GRAVAÇÃO DE AMOSTRAS PARA TREINAMENTO")
        print("🎙️ "*30)
        print(f"\nTipo: {'POSITIVAS (com ASLAM)' if self.tipo == 'positive' else 'NEGATIVAS (sem ASLAM)'}")
        print(f"Quantidade: {quantidade}")
        print(f"Duração cada: {self.duracao}s")
        print(f"Intervalo: {intervalo}s")
        print(f"Diretório: {self.output_dir}")
        
        if self.tipo == "positive":
            print("\n📝 DICAS para amostras POSITIVAS:")
            print("   - Fale 'ASLAM' claramente")
            print("   - Varie a entonação (normal, pergunta, exclamação)")
            print("   - Varie a velocidade (rápido, normal, devagar)")
            print("   - Varie a distância do microfone")
        else:
            print("\n📝 DICAS para amostras NEGATIVAS:")
            print("   - Fale qualquer coisa MENOS 'ASLAM'")
            print("   - Converse naturalmente")
            print("   - Inclua palavras similares (Islam, slam, etc)")
            print("   - Deixe silêncio também")
            print("   - Deixe ruído ambiente")
        
        input("\n👉 Pressione ENTER para começar...")
        
        gravados = 0
        erros = 0
        
        try:
            for i in range(1, quantidade + 1):
                try:
                    self.gravar_amostra(i)
                    gravados += 1
                    
                    # Intervalo entre amostras (exceto na última)
                    if i < quantidade:
                        print(f"\n⏱️  Próxima amostra em {intervalo}s...", end='')
                        for j in range(intervalo):
                            print(f" {intervalo - j}", end='', flush=True)
                            time.sleep(1)
                        print()
                    
                except KeyboardInterrupt:
                    print("\n\n🛑 Gravação interrompida pelo usuário")
                    break
                except Exception as e:
                    print(f"\n❌ Erro ao gravar amostra {i}: {e}")
                    erros += 1
                    time.sleep(1)
        
        finally:
            self.pa.terminate()
            
            print("\n" + "="*60)
            print("📊 RESUMO")
            print("="*60)
            print(f"   Amostras gravadas: {gravados}")
            print(f"   Erros: {erros}")
            print(f"   Diretório: {self.output_dir}")
            print("="*60)
            
            if gravados > 0:
                print(f"\n✅ {gravados} amostras salvas com sucesso!")
                
                if self.tipo == "positive" and gravados < 50:
                    print(f"\n💡 DICA: Recomendado ter pelo menos 50 amostras positivas.")
                    print(f"         Você tem {gravados}. Grave mais {50 - gravados}.")
                
                if self.tipo == "negative" and gravados < 100:
                    print(f"\n💡 DICA: Recomendado ter pelo menos 100 amostras negativas.")
                    print(f"         Você tem {gravados}. Grave mais {100 - gravados}.")


def main():
    """Função principal com interface interativa"""
    print("="*70)
    print("🎤 GRAVADOR DE AMOSTRAS PARA MODELO ASLAM")
    print("="*70)
    
    # Pergunta tipo
    print("\n📋 Tipo de amostra:")
    print("   1. Positiva (falar 'ASLAM')")
    print("   2. Negativa (falar qualquer coisa EXCETO 'ASLAM')")
    
    tipo_input = input("\nEscolha [1]: ").strip() or "1"
    tipo = "positive" if tipo_input == "1" else "negative"
    
    # Pergunta quantidade
    if tipo == "positive":
        print(f"\n📊 Quantidade de amostras (recomendado: 100+)")
    else:
        print(f"\n📊 Quantidade de amostras (recomendado: 200+)")
    
    quantidade_input = input("Quantidade [100]: ").strip()
    quantidade = int(quantidade_input) if quantidade_input else 100
    
    # Confirmação
    print("\n" + "="*70)
    if tipo == "positive":
        print(f"🎯 Vou gravar {quantidade} amostras POSITIVAS (você falando 'ASLAM')")
    else:
        print(f"🎯 Vou gravar {quantidade} amostras NEGATIVAS (sem falar 'ASLAM')")
    print("="*70)
    
    input("\n▶️  Pressione ENTER para começar...")
    
    # Grava
    gravador = GravadorAmostras(tipo, duracao=2)
    gravador.gravar_multiplas(quantidade, intervalo=2)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
