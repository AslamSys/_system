# 🚀 Setup - Wake Word Detector

## 📋 Pré-requisitos

1. **Picovoice Access Key** (necessário para Porcupine)
   - Acesse: https://console.picovoice.ai/
   - Crie uma conta gratuita
   - Copie sua Access Key

2. **Python 3.11+** (para testes locais)

3. **Docker & Docker Compose** (para deploy em container)

---

## ⚡ Setup Rápido (Teste Local)

### 1. Configurar ambiente

```powershell
# Clone ou navegue até o diretório
cd "wake-word-detector"

# Copie o arquivo de exemplo
Copy-Item .env.example .env

# Edite o .env e adicione sua PORCUPINE_ACCESS_KEY
notepad .env
```

### 2. Instalar dependências

```powershell
# Crie ambiente virtual
python -m venv venv

# Ative o ambiente
.\venv\Scripts\Activate.ps1

# Instale dependências
pip install -r requirements.txt

# Para testes, instale também numpy
pip install numpy
```

### 3. Configurar .env

Edite o arquivo `.env` com suas configurações:

```env
# Obrigatório - Obtenha em https://console.picovoice.ai/
PORCUPINE_ACCESS_KEY=sua_chave_aqui

# Wake Word (Porcupine suporta: alexa, americano, blueberry, bumblebee, 
# computer, grapefruit, grasshopper, hey google, hey siri, jarvis, 
# ok google, picovoice, porcupine, terminator)
WAKE_WORD_KEYWORD=porcupine

# Sensibilidade (0.0 a 1.0 - quanto maior, mais sensível)
WAKE_WORD_SENSITIVITY=0.7

# Para testes locais
ZEROMQ_ENDPOINT=tcp://localhost:5555
NATS_URL=nats://localhost:4222
```

**IMPORTANTE:** Para palavra customizada "ASLAM", você precisará:
- Criar um modelo customizado no Picovoice Console
- Fazer download do arquivo `.ppn`
- Ajustar o código para carregar o modelo customizado

Por enquanto, use uma das palavras padrão como `porcupine` para testes.

---

## 🧪 Testando Localmente

### Terminal 1: Inicie o NATS (via Docker)

```powershell
docker run -p 4222:4222 -p 8222:8222 nats:2.10-alpine -js -m 8222
```

### Terminal 2: Inicie o script de teste (simula produtor de áudio)

```powershell
.\venv\Scripts\Activate.ps1
python test_detector.py
```

Este script irá:
- ✅ Criar um produtor ZeroMQ simulando frames de áudio
- ✅ Escutar eventos NATS do detector
- ✅ Simular fim de conversa após 5s

### Terminal 3: Inicie o Wake Word Detector

```powershell
.\venv\Scripts\Activate.ps1
python src/main.py
```

**Observação:** Como o `test_detector.py` envia apenas ruído branco, o Porcupine **não vai detectar** a wake word. 
Este teste serve para validar a comunicação entre componentes.

---

## 🎤 Testando com Áudio Real

Para testar com áudio real de microfone, você precisará:

1. **Conectar ao container `audio-capture-vad`** que captura áudio real
2. **Ou criar um produtor de teste** que lê arquivo de áudio WAV com a wake word falada

Exemplo de produtor com áudio real (arquivo WAV):

```python
import wave
import struct
import zmq
import time

# Carrega arquivo WAV (16kHz, mono, 16-bit)
wav = wave.open("porcupine_wake_word.wav", "rb")
frame_length = 512

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

time.sleep(1)  # Aguarda conexões

while True:
    audio_bytes = wav.readframes(frame_length)
    if not audio_bytes:
        break
    
    socket.send_multipart([b"audio.raw", audio_bytes])
    time.sleep(frame_length / 16000)  # 32ms
```

---

## 📊 Monitorando Métricas

Acesse as métricas Prometheus em:
```
http://localhost:8001
```

Métricas disponíveis:
- `wake_word_detections_total` - Total de detecções
- `wake_word_suppressed` - Estado atual (0=IDLE, 1=SUPPRESSED)
- `wake_word_confidence` - Histograma de confiança
- `wake_word_processing_latency_seconds` - Latência de processamento
- `wake_word_suppression_duration_seconds` - Duração de supressão

---

## 🐳 Deploy com Docker

### Build da imagem

```powershell
docker build -t wake-word-detector .
```

### Executar com Docker Compose

```powershell
# Edite o .env primeiro
docker-compose up -d

# Ver logs
docker-compose logs -f wake-word-detector

# Parar
docker-compose down
```

---

## 🔧 Troubleshooting

### Erro: "Invalid access key"
- ✅ Verifique se a `PORCUPINE_ACCESS_KEY` no `.env` está correta
- ✅ Acesse https://console.picovoice.ai/ para validar sua chave

### Erro: "Connection refused" (ZeroMQ)
- ✅ Certifique-se que o produtor de áudio está rodando
- ✅ Verifique o endpoint: `tcp://localhost:5555`

### Erro: "Connection refused" (NATS)
- ✅ Certifique-se que o NATS está rodando
- ✅ Teste: `curl http://localhost:8222/varz`

### Não detecta a wake word
- ✅ Verifique se está usando uma palavra suportada (veja lista no .env)
- ✅ Para "ASLAM" customizada, precisa criar modelo no Picovoice Console
- ✅ Ajuste a sensibilidade (aumente para mais detecções)
- ✅ Verifique se o áudio está em 16kHz, mono, 16-bit

---

## 📝 Próximos Passos

1. **Criar modelo customizado "ASLAM"** no Picovoice Console
2. **Integrar com audio-capture-vad** real
3. **Integrar com speaker-verification** (próximo componente)
4. **Ajustar sensibilidade** baseado em testes reais
5. **Configurar alertas** no Prometheus/Grafana

---

## 📚 Referências

- [Porcupine Documentation](https://picovoice.ai/docs/porcupine/)
- [Picovoice Console](https://console.picovoice.ai/)
- [Supported Keywords](https://github.com/Picovoice/porcupine#wake-words)
