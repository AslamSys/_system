# 🎵 Source Separation Service

Serviço de separação de vozes sobrepostas usando Demucs para o ecossistema Mordomo.

## 📁 Estrutura do Projeto

```
source-separation/
├── src/
│   ├── __init__.py           # Módulo principal
│   ├── main.py               # Aplicação principal
│   ├── config.py             # Configuração
│   ├── separator.py          # Serviço de separação (Demucs)
│   ├── nats_client.py        # Cliente NATS
│   └── metrics.py            # Métricas Prometheus
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_separator.py
│   ├── test_nats_client.py
│   └── test_metrics.py
├── config/
│   └── config.yaml           # Configuração YAML
├── requirements.txt          # Dependências Python
├── Dockerfile                # Container otimizado para ARM
├── docker-compose.yml        # Desenvolvimento local
├── prometheus.yml            # Config Prometheus
└── README.md                 # Este arquivo
```

## 🚀 Início Rápido

### Desenvolvimento Local

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Executar com Docker Compose:**
```bash
docker-compose up -d
```

Serviços disponíveis:
- **NATS:** `localhost:4222` (cliente), `localhost:8222` (monitoring)
- **Source Separation:** `localhost:9090` (métricas)
- **Prometheus:** `localhost:9091`
- **Grafana:** `localhost:3000` (admin/admin)

### Executar Testes

```bash
# Instalar dependências de teste
pip install -r requirements.txt

# Rodar todos os testes
pytest tests/ -v

# Rodar com cobertura
pytest tests/ --cov=src --cov-report=html

# Rodar testes específicos
pytest tests/test_config.py -v
```

## 🔧 Configuração

Edite `config/config.yaml`:

```yaml
demucs:
  model: "htdemucs_ft"      # Modelo Demucs
  device: "cpu"              # cpu ou cuda
  shifts: 1
  overlap: 0.25

processing:
  max_duration: 5.0          # Máximo 5 segundos
  batch_size: 1
  num_workers: 2

trigger:
  min_overlap_duration: 0.5  # Mínimo 500ms
  confidence_threshold: 0.6

nats:
  servers:
    - "nats://localhost:4222"
  subjects:
    input: "audio.overlap_detected"
    output: "audio.separated"
```

## 📊 Fluxo de Dados

```
1. Speaker ID detecta overlap
   ↓
2. Publica em: audio.overlap_detected
   {
     "audio": "base64 PCM",
     "duration": 2.5,
     "speakers": ["user_1", "user_2"],
     "conversation_id": "uuid"
   }
   ↓
3. Source Separation processa (1-3s)
   - Demucs separa vozes
   - Atribui canais aos speakers
   ↓
4. Publica em: audio.separated
   {
     "channels": [
       {"audio": "base64", "speaker_id": "user_1", "confidence": 0.85},
       {"audio": "base64", "speaker_id": "user_2", "confidence": 0.78}
     ],
     "conversation_id": "uuid"
   }
   ↓
5. Whisper ASR retranscribe cada canal
```

## 📈 Métricas

Acesse: `http://localhost:9090/metrics`

Métricas disponíveis:
- `source_separation_requests_total` - Total de requisições
- `source_separation_latency_seconds` - Latência de processamento
- `source_separation_success_total` - Separações bem-sucedidas
- `source_separation_quality_score` - Score de confiança médio
- `source_separation_processing_current` - Processamentos em andamento
- `source_separation_audio_duration_seconds_total` - Duração total processada

## 🧪 Testando o Serviço

### Testar Separação Manualmente

```python
import asyncio
import json
import base64
from nats.aio.client import Client as NATS

async def test_separation():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    # Simular áudio de overlap
    audio_data = b"..." # Seus dados de áudio PCM
    
    message = {
        "audio": base64.b64encode(audio_data).decode(),
        "duration": 2.5,
        "speakers": ["user_1", "user_2"],
        "conversation_id": "test-123",
        "timestamp": 1732723200.0
    }
    
    # Publicar
    await nc.publish(
        "audio.overlap_detected",
        json.dumps(message).encode()
    )
    
    # Subscrever resultado
    async def handler(msg):
        data = json.loads(msg.data.decode())
        print(f"Received {len(data['channels'])} separated channels")
    
    await nc.subscribe("audio.separated", cb=handler)
    await asyncio.sleep(5)  # Aguardar processamento

asyncio.run(test_separation())
```

## 🐳 Produção

### Build da Imagem

```bash
docker build -t source-separation:latest .
```

### Deploy

```bash
docker run -d \
  --name source-separation \
  -p 9090:9090 \
  -v $(pwd)/config:/app/config \
  -e PYTHONUNBUFFERED=1 \
  source-separation:latest
```

## ⚠️ Notas Importantes

1. **Performance ARM:** Otimizado para Orange Pi 5 (CPU-only)
2. **Uso de Recursos:** 60-80% CPU spike, ~1.5GB RAM durante separação
3. **Latência:** 1-3 segundos por processamento
4. **Modelo:** Download automático na primeira execução (~500MB)
5. **Uso:** Apenas quando overlap detectado (<5% do tempo)

## 🔍 Troubleshooting

### Modelo não carrega
```bash
# Baixar modelo manualmente
python -c "from demucs.pretrained import get_model; get_model('htdemucs_ft')"
```

### NATS não conecta
```bash
# Verificar se NATS está rodando
docker-compose ps
docker-compose logs nats
```

### Testes falhando
```bash
# Verificar dependências
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

## 📝 Desenvolvimento

### Adicionar Novos Testes

Crie arquivos em `tests/` seguindo o padrão:
- `test_*.py` para módulos de teste
- Use fixtures do pytest
- Mock modelos pesados (Demucs)

### Adicionar Métricas

Edite `src/metrics.py` e adicione novos contadores/histogramas.

## 📚 Referências

- [Demucs](https://github.com/facebookresearch/demucs)
- [NATS](https://nats.io/)
- [Prometheus](https://prometheus.io/)
- [Orange Pi 5](https://orangepi.com/)
