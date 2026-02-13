"""
Script wrapper para treinar modelo ASLAM
Facilita o processo de treinamento
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


def verificar_amostras(positive_dir: str, negative_dir: str):
    """Verifica se há amostras suficientes"""
    
    pos_path = Path(positive_dir)
    neg_path = Path(negative_dir)
    
    if not pos_path.exists():
        print(f"❌ Diretório de amostras positivas não encontrado: {positive_dir}")
        return False
    
    if not neg_path.exists():
        print(f"❌ Diretório de amostras negativas não encontrado: {negative_dir}")
        return False
    
    # Conta arquivos WAV
    pos_files = list(pos_path.glob("*.wav"))
    neg_files = list(neg_path.glob("*.wav"))
    
    print(f"\n📊 Amostras encontradas:")
    print(f"   Positivas (com ASLAM): {len(pos_files)}")
    print(f"   Negativas (sem ASLAM): {len(neg_files)}")
    
    # Valida quantidade mínima
    min_pos = 20
    min_neg = 50
    
    if len(pos_files) < min_pos:
        print(f"\n⚠️  AVISO: Poucas amostras positivas!")
        print(f"   Recomendado: {min_pos}+, Ideal: 100+")
        print(f"   Você tem: {len(pos_files)}")
        print(f"\n   Use: python gravar_amostras_aslam.py --tipo positive --quantidade {min_pos - len(pos_files)}")
        return False
    
    if len(neg_files) < min_neg:
        print(f"\n⚠️  AVISO: Poucas amostras negativas!")
        print(f"   Recomendado: {min_neg}+, Ideal: 200+")
        print(f"   Você tem: {len(neg_files)}")
        print(f"\n   Use: python gravar_amostras_aslam.py --tipo negative --quantidade {min_neg - len(neg_files)}")
        return False
    
    print(f"\n✅ Quantidade de amostras adequada!")
    return True


def treinar(positive_dir: str, negative_dir: str, output_dir: str, epochs: int):
    """Executa treinamento"""
    
    print("\n" + "🎓"*30)
    print("TREINAMENTO DO MODELO ASLAM")
    print("🎓"*30)
    
    print(f"\nParâmetros:")
    print(f"   Amostras positivas: {positive_dir}")
    print(f"   Amostras negativas: {negative_dir}")
    print(f"   Saída: {output_dir}")
    print(f"   Epochs: {epochs}")
    
    # Cria diretório de saída
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Comando de treinamento
    cmd = [
        sys.executable,
        "-m", "openwakeword.train",
        "--positive_dirs", positive_dir,
        "--negative_dirs", negative_dir,
        "--output_dir", output_dir,
        "--model_name", "aslam",
        "--epochs", str(epochs),
    ]
    
    print(f"\n🚀 Iniciando treinamento...")
    print(f"   Comando: {' '.join(cmd)}")
    print(f"\n{'='*60}")
    
    try:
        # Executa treinamento
        result = subprocess.run(cmd, check=True)
        
        print(f"\n{'='*60}")
        print(f"✅ Treinamento concluído com sucesso!")
        
        # Verifica se modelo foi criado
        model_path = Path(output_dir) / "aslam.onnx"
        if model_path.exists():
            print(f"\n📦 Modelo criado: {model_path}")
            print(f"   Tamanho: {model_path.stat().st_size / 1024:.1f} KB")
            
            # Copia para diretório de modelos
            models_dir = Path("models")
            models_dir.mkdir(exist_ok=True)
            
            dest = models_dir / "aslam.onnx"
            import shutil
            shutil.copy(model_path, dest)
            print(f"\n✅ Modelo copiado para: {dest}")
            
            print(f"\n🎯 Próximos passos:")
            print(f"   1. Testar: python test_standalone.py")
            print(f"   2. Configure WAKE_WORD_KEYWORD=aslam no .env")
            print(f"   3. Ajuste WAKE_WORD_THRESHOLD conforme necessário")
            
        else:
            print(f"\n⚠️  Modelo não encontrado em: {model_path}")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro durante treinamento!")
        print(f"   Código de saída: {e.returncode}")
        return 1
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Treina modelo customizado ASLAM para OpenWakeWord"
    )
    parser.add_argument(
        "--positive_dir",
        type=str,
        default="training_data/positive",
        help="Diretório com amostras positivas (padrão: training_data/positive)"
    )
    parser.add_argument(
        "--negative_dir",
        type=str,
        default="training_data/negative",
        help="Diretório com amostras negativas (padrão: training_data/negative)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="models/custom",
        help="Diretório de saída (padrão: models/custom)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
        help="Número de epochs (padrão: 30)"
    )
    parser.add_argument(
        "--skip_validation",
        action="store_true",
        help="Pular validação de amostras"
    )
    
    args = parser.parse_args()
    
    # Verifica amostras
    if not args.skip_validation:
        if not verificar_amostras(args.positive_dir, args.negative_dir):
            print("\n❌ Validação falhou. Use --skip_validation para forçar.")
            return 1
        
        input("\n👉 Pressione ENTER para iniciar treinamento...")
    
    # Treina
    return treinar(args.positive_dir, args.negative_dir, args.output_dir, args.epochs)


if __name__ == "__main__":
    sys.exit(main())
