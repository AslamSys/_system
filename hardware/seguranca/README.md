# Jetson Orin Nano 8GB - Módulo de Segurança

## 📋 Especificações do Hardware

### NVIDIA Jetson Orin Nano 8GB
- **SoC**: NVIDIA Orin (Cortex-A78AE 6-core 2.0GHz)
- **GPU**: 1024 CUDA cores, 32 Tensor cores
- **RAM**: 8GB LPDDR5
- **AI Performance**: 40 TOPS (INT8)
- **Armazenamento**: MicroSD 128GB + NVMe SSD 256GB (opcional)
- **Rede**: Gigabit Ethernet
- **USB**: 4x USB 3.2 Gen2
- **CSI**: 4x MIPI CSI-2 (4 câmeras simultâneas)
- **Alimentação**: 12V/2A DC Barrel (24W)
- **Cabo Ethernet Cat6**: $3
- **TOTAL**: **$312**

## 🎯 Função no Sistema

Este hardware executa o **Módulo de Segurança**, responsável por:
- Monitorar câmeras de segurança em tempo real
- Detecção de pessoas, veículos, objetos suspeitos (YOLOv8)
- Reconhecimento facial (FaceNet)
- Análise de comportamento suspeito
- Alertas inteligentes ao Mordomo
- LLM Vision Brain (Qwen 3B Vision + CLIP) para compreensão de cenas

## 🧠 LLM - Qwen 3B Vision

### Especificações do Modelo
- **Parâmetros**: 3 bilhões (LLM) + CLIP Vision Encoder
- **Quantização**: Q4_K_M (1.8GB VRAM)
- **Contexto**: 8K tokens + imagens
- **Formato**: GGUF (Ollama com vision)
- **Inferência**: CUDA-accelerated (TensorRT otimizado)

### Requisitos de Recursos
- **RAM necessária**: 2GB (modelo) + 1.5GB (contexto + imagem) = **3.5GB**
- **VRAM (GPU)**: 2GB para visão + inferência
- **RAM disponível**: 8GB
- **Margem de segurança**: **4.5GB livres** (56% disponível)
- **GPU CUDA**: 512 cores dedicados para LLM, 512 para YOLO
- **Latência**: ~150ms por frame (30 FPS nas 4 câmeras)

### Capacidades Vision
- Descrever cenas em linguagem natural
- Responder perguntas sobre vídeo: "Quantas pessoas entraram?"
- Identificar atividades suspeitas: "Pessoa pulando o muro"
- OCR em placas de carros
- Classificação de eventos: normal, alerta, emergência

## 📦 Ecossistema: Segurança

### Containers (7 total)

#### 1. **seguranca-brain** (LLM Vision)
- Ollama + Qwen 3B Vision Q4_K_M
- Interpreta frames de câmeras
- Classifica eventos (normal, alerta, crítico)
- Gera descrições contextuais
- **Recursos**: 4GB RAM, 2GB VRAM, 200% CPU

#### 2. **camera-stream-manager**
- RTSP server (mediamtx)
- Gerencia 4 streams RTSP simultâneos
- Re-encoding H.264 (NVENC hardware)
- Buffer circular 24h (SSD)
- **Recursos**: 1GB RAM, 256MB VRAM, 80% CPU

#### 3. **yolo-detector**
- YOLOv8n (nano) otimizado TensorRT
- Detecção: pessoas, carros, pets, objetos
- 30 FPS em 4 câmeras 1080p
- Bounding boxes + tracking (DeepSORT)
- **Recursos**: 512MB RAM, 1.5GB VRAM, 150% CPU

#### 4. **face-recognition**
- FaceNet + ArcFace (embeddings 512D)
- Banco de rostos conhecidos (Qdrant)
- Identificação < 200ms
- Anti-spoofing (liveness detection)
- **Recursos**: 768MB RAM, 512MB VRAM, 100% CPU

#### 5. **event-analyzer**
- Analisa sequências de detecções
- Comportamentos suspeitos: loitering, intrusion, fall detection
- Zone intrusion (áreas restritas)
- Heatmaps de movimento
- **Recursos**: 384MB RAM, 50% CPU

#### 6. **alert-manager**
- Envia alertas ao Mordomo via NATS
- Priorização: normal < alerta < crítico < emergência
- Cooldown anti-spam (máx 1 alerta/min por câmera)
- Snapshots + clips de vídeo
- **Recursos**: 256MB RAM, 40% CPU

#### 7. **storage-manager**
- Gravação contínua 24/7 (H.264 NVENC)
- Retenção: 7 dias (eventos), 24h (normal)
- **Recursos**: 512MB RAM, 60% CPU

### Repositórios
- [seguranca-brain](https://github.com/AslamSys/seguranca-brain)
- [seguranca-camera-stream-manager](https://github.com/AslamSys/seguranca-camera-stream-manager)
- [seguranca-yolo-detector](https://github.com/AslamSys/seguranca-yolo-detector)
- [seguranca-face-recognition](https://github.com/AslamSys/seguranca-face-recognition)
- [seguranca-event-analyzer](https://github.com/AslamSys/seguranca-event-analyzer)
- [seguranca-alert-manager](https://github.com/AslamSys/seguranca-alert-manager)
- [seguranca-storage-manager](https://github.com/AslamSys/seguranca-storage-manager)
- Compressão inteligente (motion-based)
- Exportação de clips
- **Recursos**: 512MB RAM, 256MB VRAM, 60% CPU

### Análise de Recursos

| Container | RAM | VRAM | CPU | Disco |
|-----------|-----|------|-----|-------|
| seguranca-brain | 4GB | 2GB | 200% | 3GB |
| camera-stream-manager | 1GB | 256MB | 80% | 10GB |
| yolo-detector | 512MB | 1.5GB | 150% | 1GB |
| face-recognition | 768MB | 512MB | 100% | 2GB |
| event-analyzer | 384MB | - | 50% | 512MB |
| alert-manager | 256MB | - | 40% | 256MB |
| storage-manager | 512MB | 256MB | 60% | 100GB |
| **TOTAL** | **7.43GB** | **4.52GB** | **680%** | **~117GB** |

### Viabilidade
- **RAM**: 7.43GB / 8GB = **93% utilizado** ⚠️ (margem apertada, aceitável)
- **VRAM**: 4.52GB / 8GB shared = **57% VRAM dedicada** ✅
- **CPU**: 680% / 600% = **113% utilizado** ⚠️ (picos tolerados, média 85%)
- **Disco**: 117GB / 256GB SSD = **46% utilizado** ✅

**Observação**: GPU Jetson é altamente eficiente para inferência paralela. NVENC/NVDEC offload libera CPU.

## 🔌 Integração com Mordomo

### Protocolo NATS

#### Tópicos Subscritos
```
seguranca.camera.configure    # Configurar câmera
seguranca.face.register       # Cadastrar rosto conhecido
seguranca.zone.define         # Definir zona restrita
seguranca.recording.export    # Exportar vídeo
```

#### Tópicos Publicados
```
seguranca.alert.person        # Pessoa detectada
seguranca.alert.vehicle       # Veículo detectado
seguranca.alert.face          # Rosto reconhecido
seguranca.alert.intrusion     # Invasão de zona
seguranca.alert.behavior      # Comportamento suspeito
seguranca.status              # Status do módulo
```

### Fluxo de Detecção

```
Câmera 1: Frame 1080p @ 30 FPS
    ↓
camera-stream-manager: Recebe RTSP
    ↓
yolo-detector: Detecta pessoa (bbox: x=450, y=320, w=180, h=420)
    ↓
face-recognition: Extrai rosto → embedding 512D
    ↓
Busca no Qdrant: Match 92% com "João Silva" (morador)
    ↓
event-analyzer: Pessoa conhecida entrando (zona permitida) → Evento NORMAL
    ↓
(Não gera alerta)

---

Câmera 3: Frame 1080p @ 30 FPS (03:45 AM)
    ↓
camera-stream-manager: Recebe RTSP
    ↓
yolo-detector: Detecta pessoa desconhecida + movimento zona restrita
    ↓
face-recognition: Nenhum match no banco
    ↓
event-analyzer: Pessoa desconhecida em zona restrita + horário suspeito → ALERTA CRÍTICO
    ↓
seguranca-brain (Vision LLM): Analisa frame
    Input: "Descreva o que está acontecendo nesta imagem"
    Output: "Uma pessoa vestindo capuz preto está próxima à janela dos fundos da casa às 3h45 da manhã"
    ↓
alert-manager: NATS publish → seguranca.alert.intrusion
    {
      "level": "critical",
      "camera": "camera_3_fundos",
      "timestamp": "2025-11-27T03:45:12Z",
      "detections": [{
        "type": "person",
        "confidence": 0.96,
        "bbox": [720, 400, 200, 480],
        "face_match": null
      }],
      "description": "Pessoa desconhecida com capuz próxima à janela dos fundos",
      "snapshot": "s3://snapshots/cam3_20251127_034512.jpg",
      "clip": "s3://clips/cam3_20251127_034500_034520.mp4"
    }
    ↓
Mordomo: Recebe via NATS
    ↓
Decide ação: Aciona sirene + Liga luzes externas + Notifica via WhatsApp
    ↓
NATS publish → iot.alarm.trigger + comunicacao.send.whatsapp
    {
      "recipient": "Renan (dono da casa)",
      "message": "🚨 ALERTA CRÍTICO: Pessoa desconhecida detectada próxima à janela dos fundos às 03:45. Sirene acionada. Veja a imagem:",
      "attachment": "snapshot_url"
    }
```

## 🗄️ Banco de Dados

### Qdrant Collections (no Mordomo)

#### Collection: `security_faces`
```python
{
  "name": "security_faces",
  "vectors": {
    "face_embedding": {
      "size": 512,  # FaceNet embeddings
      "distance": "Cosine"
    }
  },
  "payload_schema": {
    "person_id": "uuid",
    "name": "string",
    "relation": "string",  # morador, visitante, entregador, desconhecido
    "photo_url": "string",
    "registered_at": "datetime",
    "access_level": "integer"  # 0=bloqueado, 1=visitante, 2=morador
  }
}
```

#### Collection: `security_events`
```python
{
  "name": "security_events",
  "vectors": {
    "scene_embedding": {
      "size": 768,  # CLIP embeddings para busca semântica
      "distance": "Cosine"
    }
  },
  "payload_schema": {
    "camera_id": "string",
    "timestamp": "datetime",
    "event_type": "string",  # person, vehicle, intrusion, fall, etc.
    "level": "string",  # normal, alert, critical, emergency
    "description": "string",  # gerado pela Vision LLM
    "detections": "json",
    "snapshot_url": "string",
    "clip_url": "string"
  }
}
```

### PostgreSQL Schemas (no Mordomo)

#### Tabela: `security_cameras`
```sql
CREATE TABLE security_cameras (
  id UUID PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  location VARCHAR(255),
  rtsp_url TEXT NOT NULL,
  resolution VARCHAR(20) DEFAULT '1920x1080',
  fps INTEGER DEFAULT 30,
  enabled BOOLEAN DEFAULT TRUE,
  zones JSONB,  -- áreas de interesse/restrição
  settings JSONB,  -- motion sensitivity, recording quality
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Tabela: `security_alerts`
```sql
CREATE TABLE security_alerts (
  id UUID PRIMARY KEY,
  camera_id UUID REFERENCES security_cameras(id),
  event_type VARCHAR(50) NOT NULL,
  level VARCHAR(20) NOT NULL,
  description TEXT,
  detections JSONB,
  snapshot_url TEXT,
  clip_url TEXT,
  acknowledged BOOLEAN DEFAULT FALSE,
  acknowledged_by UUID,
  acknowledged_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🐳 Docker Compose

```yaml
version: '3.8'

services:
  seguranca-brain:
    image: dustynv/ollama:r36.2.0  # Jetson-optimized
    container_name: seguranca-brain
    runtime: nvidia
    volumes:
      - ./models:/root/.ollama
    environment:
      - OLLAMA_MODELS=/root/.ollama/models
      - NVIDIA_VISIBLE_DEVICES=all
    command: serve
    networks:
      - seguranca-net
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  camera-stream-manager:
    image: bluenviron/mediamtx:latest
    container_name: camera-stream-manager
    runtime: nvidia
    ports:
      - "8554:8554"  # RTSP
      - "8888:8888"  # HLS
      - "8889:8889"  # WebRTC
    volumes:
      - ./config/mediamtx.yml:/mediamtx.yml
      - ./recordings:/recordings
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    networks:
      - seguranca-net
    deploy:
      resources:
        limits:
          memory: 1G
    restart: unless-stopped

  yolo-detector:
    build: 
      context: ./containers/yolo-detector
      args:
        - JETSON_PLATFORM=orin-nano
    container_name: yolo-detector
    runtime: nvidia
    volumes:
      - ./models/yolov8n.engine:/app/model.engine
    environment:
      - NATS_URL=nats://mordomo-nats:4222
      - RTSP_URLS=rtsp://camera-stream-manager:8554/cam1,rtsp://camera-stream-manager:8554/cam2
      - NVIDIA_VISIBLE_DEVICES=all
    depends_on:
      - camera-stream-manager
    networks:
      - seguranca-net
    deploy:
      resources:
        limits:
          memory: 512M
    restart: unless-stopped

  face-recognition:
    build: ./containers/face-recognition
    container_name: face-recognition
    runtime: nvidia
    environment:
      - NATS_URL=nats://mordomo-nats:4222
      - QDRANT_URL=http://mordomo-qdrant:6333
      - NVIDIA_VISIBLE_DEVICES=all
    depends_on:
      - yolo-detector
    networks:
      - seguranca-net
    deploy:
      resources:
        limits:
          memory: 768M
    restart: unless-stopped

  event-analyzer:
    build: ./containers/event-analyzer
    container_name: event-analyzer
    environment:
      - NATS_URL=nats://mordomo-nats:4222
      - BRAIN_URL=http://seguranca-brain:11434
    depends_on:
      - seguranca-brain
    networks:
      - seguranca-net
    deploy:
      resources:
        limits:
          memory: 384M
          cpus: '0.5'
    restart: unless-stopped

  alert-manager:
    build: ./containers/alert-manager
    container_name: alert-manager
    environment:
      - NATS_URL=nats://mordomo-nats:4222
      - POSTGRES_URL=postgresql://mordomo-db:5432/mordomo
    networks:
      - seguranca-net
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.4'
    restart: unless-stopped

  storage-manager:
    build: ./containers/storage-manager
    container_name: storage-manager
    runtime: nvidia
    volumes:
      - /mnt/ssd/recordings:/recordings
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - RETENTION_DAYS_NORMAL=1
      - RETENTION_DAYS_EVENTS=7
    networks:
      - seguranca-net
    deploy:
      resources:
        limits:
          memory: 512M
    restart: unless-stopped

networks:
  seguranca-net:
    driver: bridge
```

## 🚀 Deploy e Configuração

### Pré-requisitos Jetson
```bash
# Instalar JetPack 6.0 (L4T 36.2)
sudo apt update && sudo apt upgrade -y

# Instalar NVIDIA Container Runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-container-runtime

# Configurar Docker para usar NVIDIA runtime
sudo nano /etc/docker/daemon.json
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
sudo systemctl restart docker
```

### Otimizar YOLOv8 com TensorRT
```bash
# Converter modelo ONNX para TensorRT engine
docker run --rm -it --runtime nvidia \
  -v $(pwd)/models:/models \
  nvcr.io/nvidia/pytorch:23.10-py3 \
  python3 -c "
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.export(format='engine', device=0, half=True, workspace=2)
"
# Gera: yolov8n.engine (otimizado FP16 para Jetson)
```

### Configurar Câmeras
```yaml
# config/mediamtx.yml
paths:
  cam1_entrada:
    source: rtsp://192.168.1.50:554/stream1
    sourceProtocol: rtsp
    sourceOnDemand: no
    runOnReady: ffmpeg -i rtsp://localhost:$RTSP_PORT/$MTX_PATH -c copy -f flv rtmp://localhost:1935/live/cam1
  
  cam2_garagem:
    source: rtsp://192.168.1.51:554/stream1
  
  cam3_fundos:
    source: rtsp://192.168.1.52:554/stream1
  
  cam4_sala:
    source: rtsp://192.168.1.53:554/stream1
```

## 📊 Monitoramento

### Métricas Prometheus
- `seguranca_fps{camera="cam1"}` - FPS de processamento por câmera
- `seguranca_detections_total{type="person"}` - Total de detecções
- `seguranca_alerts_total{level="critical"}` - Total de alertas por nível
- `seguranca_face_recognition_duration_seconds` - Latência reconhecimento facial
- `seguranca_gpu_utilization_percent` - Uso da GPU
- `seguranca_disk_usage_bytes` - Espaço usado em gravações

### Alertas Grafana
- **FPS Baixo**: FPS < 25 em qualquer câmera por > 1min
- **GPU Saturada**: GPU > 95% por > 5min
- **Disco Cheio**: Gravações > 90% do SSD
- **Câmera Offline**: Sem frames por > 30s

## 🔒 Segurança e Privacidade

### LGPD Compliance
- **Opt-in**: Visitantes informados sobre câmeras (placas visíveis)
- **Retenção limitada**: 7 dias eventos, 24h normal
- **Anonimização**: Rostos borrados em exportações não-autorizadas
- **Acesso auditado**: Logs de quem visualizou gravações

### Criptografia
- **Em repouso**: Gravações criptografadas AES-256
- **Em trânsito**: RTSP sobre TLS, NATS com autenticação
- **Backups**: S3 com encryption at rest

## 💡 Casos de Uso Avançados

1. **Reconhecimento de Placa** (OCR + ALPR):
   - Detecta veículos → Extrai placa → Consulta banco
   - Portão abre automaticamente para moradores
   
2. **Detecção de Queda** (Fall Detection):
   - Monitora idosos → Detecta queda → Alerta emergência

3. **Análise de Comportamento**:
   - Pessoa parada > 5min na frente da casa → Alerta "loitering"

4. **Busca Semântica em Vídeos**:
   - "Mostre quando o cachorro entrou no jardim ontem" → Busca em CLIP embeddings

5. **Relatórios Automáticos**:
   - "Quantas pessoas entraram hoje?" → Brain consulta eventos e responde
