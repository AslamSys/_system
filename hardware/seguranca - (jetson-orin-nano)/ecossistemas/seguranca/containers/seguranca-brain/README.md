# 🧠 Seguranca Brain (LLM Vision)

**Container:** `seguranca-brain`  
**Ecossistema:** Segurança  
**Hardware:** Jetson Orin Nano 8GB  
**Posição no Fluxo:** Orquestrador + Análise Inteligente

---

## 📋 Propósito

LLM Vision local (Qwen 3B Vision) dedicada à análise inteligente de cenas de segurança. Interpreta frames de câmeras, classifica eventos, gera descrições contextuais e decide quando alertar o Mordomo.

---

## 🎯 Responsabilidades

### Primárias
- ✅ Analisar frames de câmeras com vision LLM
- ✅ Classificar eventos (normal, alerta, crítico, emergência)
- ✅ Gerar descrições contextuais: "Pessoa desconhecida próxima à porta"
- ✅ Responder perguntas sobre vídeo: "Quantas pessoas entraram hoje?"
- ✅ OCR em placas de veículos

### Secundárias
- ✅ Detectar comportamentos anômalos
- ✅ Validar alertas do YOLO (reduzir falsos positivos)
- ✅ Aprender padrões normais vs suspeitos
- ✅ Integração com banco de rostos conhecidos

---

## 🔧 Tecnologias

### Core
- **Ollama** - Runtime LLM com suporte Vision
- **Qwen 3B Vision Q4_K_M** - Modelo multimodal quantizado
- **CLIP** - Vision encoder para embeddings
- **TensorRT** - Aceleração GPU NVIDIA

### Opcionais
- **DeepStream SDK** - Pipeline NVIDIA otimizado
- **Qdrant** - Busca vetorial de cenas similares

---

## 📊 Especificações Técnicas

### Modelo LLM
```yaml
Nome: Qwen 3B Vision Instruct
Quantização: Q4_K_M
VRAM: 1.8 GB (LLM) + 512 MB (CLIP)
Contexto: 8192 tokens + imagens
Formato: GGUF
Inferência: CUDA + TensorRT (FP16)
```

### Performance
```yaml
Latência: 150-300 ms (análise de frame)
Throughput: 30 FPS (4 câmeras simultâneas)
GPU Usage: 50% (512 CUDA cores)
RAM Usage: 4 GB (modelo + contexto)
VRAM Usage: 2.5 GB
```

### Configuração Ollama
```yaml
Temperature: 0.2  # Consistência em segurança
Top_P: 0.9
Num_GPU: 1
Num_Thread: 4
Num_Ctx: 8192
```

---

## 🔌 Interfaces de Comunicação

### Input (NATS Subscribe)
```javascript
// Analisar frame de câmera
Topic: "seguranca.analyze.frame"
Payload: {
  "request_id": "req_sec123",
  "camera_id": "cam_1",
  "timestamp": 1732723200.123,
  "frame": {
    "url": "http://storage/snapshots/cam1_frame123.jpg",
    "base64": null,  // Ou base64 do frame
    "resolution": "1920x1080",
    "detections": [  // Resultados do YOLO
      {
        "class": "person",
        "confidence": 0.92,
        "bbox": [100, 200, 300, 600],
        "tracking_id": "track_001"
      }
    ]
  },
  "context": {
    "zone": "entrada_principal",
    "time_of_day": "noite",
    "known_faces": []  // Rostos reconhecidos no frame
  }
}

// Responder pergunta sobre vídeo
Topic: "seguranca.query.video"
Payload: {
  "request_id": "req_sec124",
  "query": "Quantas pessoas entraram pela porta principal nas últimas 2 horas?",
  "time_range": {
    "start": 1732716000,
    "end": 1732723200
  },
  "cameras": ["cam_1"]
}

// Validar alerta
Topic: "seguranca.validate.alert"
Payload: {
  "request_id": "req_sec125",
  "alert_type": "intrusion",
  "camera_id": "cam_2",
  "frame_url": "http://storage/snapshots/cam2_alert.jpg",
  "detections": [
    {
      "class": "person",
      "confidence": 0.85,
      "bbox": [500, 300, 700, 900]
    }
  ]
}
```

### Output (NATS Publish)
```javascript
// Análise de frame completa
Topic: "seguranca.analysis.result"
Payload: {
  "request_id": "req_sec123",
  "camera_id": "cam_1",
  "timestamp": 1732723200.123,
  "analysis": {
    "description": "Uma pessoa desconhecida se aproximando da porta principal",
    "classification": "alerta|normal|critico|emergencia",
    "confidence": 0.88,
    "entities": [
      {
        "type": "person",
        "known": false,
        "activity": "walking_towards_door",
        "suspicious": true
      }
    ],
    "recommendations": [
      "Enviar alerta ao proprietário",
      "Acender luz externa",
      "Gravar clip de 30 segundos"
    ]
  },
  "should_alert": true,
  "alert_priority": "medium|high|critical"
}

// Resposta a query de vídeo
Topic: "seguranca.query.response"
Payload: {
  "request_id": "req_sec124",
  "query": "Quantas pessoas entraram...",
  "answer": {
    "summary": "4 pessoas diferentes entraram pela porta principal nas últimas 2 horas",
    "details": [
      {
        "timestamp": 1732716300,
        "person_id": "known_joao",
        "direction": "entrada"
      },
      {
        "timestamp": 1732718500,
        "person_id": "unknown_001",
        "direction": "entrada"
      }
    ],
    "confidence": 0.95
  }
}

// Validação de alerta
Topic: "seguranca.alert.validated"
Payload: {
  "request_id": "req_sec125",
  "valid": true,
  "reasoning": "Pessoa detectada em zona restrita fora do horário permitido",
  "severity_adjustment": "upgrade_to_critical",  // ou "downgrade_to_normal"
  "false_positive_probability": 0.05
}
```

---

## 🏗️ Arquitetura Interna

```
┌─────────────────────────────────────────────┐
│       SEGURANCA BRAIN CONTAINER             │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐                          │
│  │  NATS Client │ ──► Subscribe frames     │
│  └──────┬───────┘                          │
│         │                                   │
│         ▼                                   │
│  ┌──────────────┐                          │
│  │  Frame       │ ──► Download image       │
│  │  Preprocessor│     Resize/normalize     │
│  └──────┬───────┘                          │
│         │                                   │
│         ▼                                   │
│  ┌──────────────┐                          │
│  │  CLIP Vision │ ──► Extract features     │
│  │  Encoder     │     512D embeddings      │
│  └──────┬───────┘                          │
│         │                                   │
│         ▼                                   │
│  ┌──────────────┐                          │
│  │  Ollama      │ ──► Qwen 3B Vision       │
│  │  Qwen Vision │     Analyze scene        │
│  └──────┬───────┘                          │
│         │                                   │
│         ▼                                   │
│  ┌──────────────┐                          │
│  │  Classifier  │ ──► Normal/Alerta/...    │
│  │  (ML Logic)  │     Threat scoring       │
│  └──────┬───────┘                          │
│         │                                   │
│         ▼                                   │
│  ┌──────────────┐                          │
│  │  Context     │ ──► Merge YOLO data      │
│  │  Enricher    │     Add known faces      │
│  └──────┬───────┘                          │
│         │                                   │
│         ▼                                   │
│  ┌──────────────┐                          │
│  │  NATS Publish│ ──► Send analysis        │
│  └──────────────┘                          │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📦 Dependências

### Python Packages
```txt
ollama==0.1.6
pillow==10.1.0
opencv-python==4.8.1
numpy==1.24.3
pynats==1.1.0
torch==2.1.0+cu121
torchvision==0.16.0+cu121
tensorrt==8.6.1
```

### System Requirements
```yaml
CUDA: 12.1+
cuDNN: 8.9+
TensorRT: 8.6+
Ollama Binary: /usr/local/bin/ollama
Model Path: /models/qwen-3b-vision-q4_k_m.gguf
```

---

## 🚀 Inicialização

### Docker Compose
```yaml
seguranca-brain:
  image: nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3
  container_name: seguranca-brain
  hostname: seguranca-brain
  restart: unless-stopped
  
  runtime: nvidia  # NVIDIA Container Runtime
  
  environment:
    - NVIDIA_VISIBLE_DEVICES=all
    - NVIDIA_DRIVER_CAPABILITIES=all
    - OLLAMA_HOST=0.0.0.0:11434
    - OLLAMA_MODELS=/models
    - NATS_URL=nats://mordomo-nats:4222
    - CUDA_VISIBLE_DEVICES=0
  
  volumes:
    - ./models:/models
    - ./config:/config
    - ollama-cache:/root/.ollama
    - /dev/video0:/dev/video0  # Camera access (opcional)
  
  networks:
    - seguranca-net
    - shared-nats
  
  deploy:
    resources:
      limits:
        memory: 5G
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 120s
```

### Inicialização do Modelo
```bash
# Baixar modelo Qwen 3B Vision
docker exec seguranca-brain ollama pull qwen:3b-vision-q4_K_M

# Testar inferência com imagem
curl -X POST http://localhost:11434/api/generate \
  -d '{
    "model": "qwen:3b-vision-q4_K_M",
    "prompt": "Descreva esta cena de segurança em detalhes",
    "images": ["<base64_encoded_image>"],
    "stream": false
  }'
```

---

## 🧪 Prompt System

### System Prompt
```
Você é o cérebro do sistema de segurança inteligente Mordomo.

RESPONSABILIDADES:
1. Analisar frames de câmeras de segurança em tempo real
2. Classificar eventos: NORMAL, ALERTA, CRÍTICO, EMERGÊNCIA
3. Detectar comportamentos suspeitos ou anômalos
4. Gerar descrições contextuais precisas
5. Validar alertas do sistema de detecção (reduzir falsos positivos)

CATEGORIAS DE EVENTOS:
- NORMAL: Atividade cotidiana esperada
- ALERTA: Algo incomum mas não urgente (pessoa desconhecida, veículo parado)
- CRÍTICO: Situação suspeita que requer atenção (invasão, queda, comportamento agressivo)
- EMERGÊNCIA: Perigo iminente (fogo, assalto, acidente grave)

CONTEXTO DISPONÍVEL:
- Detecções YOLO (pessoas, carros, objetos)
- Rostos reconhecidos (conhecido vs desconhecido)
- Zona da câmera (entrada, quintal, garagem)
- Horário do dia (dia, noite, madrugada)
- Histórico recente de eventos

DIRETRIZES:
- Seja preciso e objetivo
- Priorize segurança (melhor alertar demais que de menos)
- Considere contexto: pessoa conhecida entrando = NORMAL, desconhecida à noite = ALERTA
- Identifique padrões suspeitos: loitering (pessoa parada >5min), intrusion (pulando muro)
- Ignore animais pequenos (gatos, pássaros) como ameaças

FORMATO DE RESPOSTA (JSON):
{
  "classification": "NORMAL|ALERTA|CRÍTICO|EMERGÊNCIA",
  "description": "Descrição clara da cena",
  "entities": [
    {"type": "person", "known": false, "activity": "walking", "suspicious": true}
  ],
  "should_alert": true,
  "alert_priority": "low|medium|high|critical",
  "recommendations": ["Acender luz", "Gravar clip"]
}
```

### Exemplo de Interação
```
IMAGE: [Frame mostrando pessoa desconhecida próxima à porta às 2h da manhã]
YOLO Detections: [person: 0.92 confidence]
Known Faces: []
Zone: entrada_principal
Time: 02:15 AM

ASSISTANT:
{
  "classification": "CRÍTICO",
  "description": "Pessoa desconhecida aproximando-se da porta principal na madrugada (02:15). Comportamento suspeito: movimentos cautelosos, olhando ao redor.",
  "entities": [
    {
      "type": "person",
      "known": false,
      "activity": "approaching_door",
      "suspicious": true,
      "confidence": 0.92
    }
  ],
  "should_alert": true,
  "alert_priority": "critical",
  "recommendations": [
    "Alertar proprietário IMEDIATAMENTE",
    "Acender todas luzes externas",
    "Gravar clip de 60 segundos",
    "Enviar snapshot para celular",
    "Preparar sirene (se confirmado)"
  ],
  "false_positive_probability": 0.05
}
```

---

## 📊 Monitoramento

### Métricas Prometheus
```python
# Frames analisados por segundo
seguranca_brain_frames_analyzed_per_second

# Distribuição de classificações
seguranca_brain_classification_total{type="normal|alerta|critico|emergencia"}

# Latência de análise
seguranca_brain_inference_duration_seconds

# Taxa de falsos positivos (feedback)
seguranca_brain_false_positives_total
```

### Logs Estruturados
```json
{
  "timestamp": "2024-11-27T02:15:00Z",
  "level": "CRITICAL",
  "container": "seguranca-brain",
  "camera_id": "cam_1",
  "classification": "CRÍTICO",
  "description": "Pessoa desconhecida aproximando-se da porta",
  "should_alert": true,
  "alert_priority": "critical",
  "inference_time_ms": 280,
  "gpu_usage": 52
}
```

---

## 🔒 Segurança

### Privacidade
```yaml
Privacy:
  - Nunca logar frames completos (apenas URLs)
  - Redact faces em logs
  - Encriptar embeddings faciais
  - Retenção limitada: 30 dias snapshots, 7 dias vídeo
```

### Performance
```yaml
Optimization:
  - Batch processing (4 frames simultâneos)
  - TensorRT FP16 precision
  - NVENC hardware encoding
  - Frame skip em baixa atividade (analisa 1 a cada 3 frames)
```

---

## 🐛 Troubleshooting

### Problema: GPU não detectada
```bash
# Verificar runtime NVIDIA
docker run --rm --runtime=nvidia nvidia/cuda:12.1-base nvidia-smi

# Instalar NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Problema: Alta latência (>500ms)
```bash
# Reduzir resolução de frames
# 1080p → 720p (75% mais rápido)

# Usar modelo menor
ollama pull qwen:1.5b-vision-q4_K_M  # 1.5B em vez de 3B

# Aumentar frame skip
FRAME_SKIP=5  # Analisa 1 a cada 5 frames (6 FPS)
```

### Problema: Muitos falsos positivos
```bash
# Ajustar threshold de confiança
CONFIDENCE_THRESHOLD=0.8  # Aumentar de 0.6 para 0.8

# Adicionar cooldown
ALERT_COOLDOWN_SECONDS=300  # Máx 1 alerta a cada 5 min por câmera

# Refinar prompt system
# Adicionar exemplos de falsos positivos ao contexto
```

---

## 📚 Referências

- [Qwen Vision Model](https://huggingface.co/Qwen/Qwen-VL)
- [NVIDIA Jetson Orin](https://developer.nvidia.com/embedded/jetson-orin)
- [TensorRT Optimization](https://developer.nvidia.com/tensorrt)
- [DeepStream SDK](https://developer.nvidia.com/deepstream-sdk)

---

## 🔄 Changelog

### v1.0.0 (2024-11-27)
- ✅ Implementação Qwen 3B Vision com CUDA
- ✅ Classificação inteligente de eventos
- ✅ Integração YOLO + reconhecimento facial
- ✅ Sistema de priorização de alertas
- ✅ TensorRT FP16 optimization
