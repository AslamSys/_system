"""
Script de validação local - testa a estrutura sem dependências pesadas.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("🧪 Source Separation - Testes Locais")
print("=" * 60)
print()

# Test 1: Import config module
print("1️⃣  Testando imports do módulo de configuração...")
try:
    from config import Config, DemucsConfig, ProcessingConfig, NATSConfig
    print("   ✅ Imports de config OK")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

# Test 2: Create default config
print("2️⃣  Testando criação de configuração padrão...")
try:
    config = Config()
    assert config.demucs.model == "htdemucs_ft"
    assert config.processing.max_duration == 5.0
    assert config.nats.subjects.input == "audio.overlap_detected"
    print("   ✅ Config padrão OK")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

# Test 3: Load config from file
print("3️⃣  Testando carregamento de config.yaml...")
try:
    from config import load_config
    config_file = Path(__file__).parent / "config" / "config.yaml"
    if config_file.exists():
        config = load_config(config_file)
        print(f"   ✅ Config carregado de {config_file.name}")
        print(f"      - Modelo Demucs: {config.demucs.model}")
        print(f"      - Device: {config.demucs.device}")
        print(f"      - Max duration: {config.processing.max_duration}s")
    else:
        print("   ⚠️  config.yaml não encontrado, usando defaults")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

# Test 4: Test NATS message classes
print("4️⃣  Testando classes de mensagem NATS...")
try:
    import base64
    # Can't import nats_client without nats-py, so we skip for now
    print("   ⚠️  NATS client requer nats-py instalado (skip)")
except Exception as e:
    print(f"   ⚠️  {e}")

# Test 5: Test metrics module
print("5️⃣  Testando módulo de métricas...")
try:
    from metrics import Metrics
    metrics = Metrics(enabled=False)  # Disabled to avoid starting server
    print("   ✅ Metrics module OK")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

# Test 6: Test separator imports (without loading model)
print("6️⃣  Testando imports do separator...")
try:
    import numpy as np
    print("   ✅ NumPy disponível")
    
    # Test basic audio operations
    audio = np.random.randn(16000).astype(np.float32)
    audio_int16 = (audio * 32768).astype(np.int16)
    audio_bytes = audio_int16.tobytes()
    print(f"   ✅ Operações de áudio básicas OK ({len(audio_bytes)} bytes)")
    
except ImportError as e:
    print(f"   ⚠️  NumPy não instalado: {e}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Test 7: Validate file structure
print("7️⃣  Validando estrutura de arquivos...")
try:
    base_path = Path(__file__).parent
    required_files = [
        "src/__init__.py",
        "src/main.py",
        "src/config.py",
        "src/separator.py",
        "src/nats_client.py",
        "src/metrics.py",
        "tests/__init__.py",
        "config/config.yaml",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
    ]
    
    missing = []
    for file in required_files:
        if not (base_path / file).exists():
            missing.append(file)
    
    if missing:
        print(f"   ⚠️  Arquivos faltando: {missing}")
    else:
        print(f"   ✅ Todos os {len(required_files)} arquivos essenciais presentes")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print()
print("=" * 60)
print("✅ Validação local concluída!")
print("=" * 60)
print()
print("📝 Próximos passos:")
print("   1. Instalar deps completas: pip install -r requirements.txt")
print("   2. Rodar testes unitários: python -m pytest tests/ -v")
print("   3. Testar com Docker: docker-compose up -d")
print()
