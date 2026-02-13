# 🍊 Orange Pi 5 (16GB RAM)

> 📍 **Navegação:** [🏠 Início](../../README.md) > [🔧 Hardware](../README.md) > [🎯 Mordomo (Orange Pi 5 16GB)](README.md)

**Hardware:** Orange Pi 5  
**RAM:** 16GB LPDDR4/4x  
**CPU:** Rockchip RK3588S (4x Cortex-A76 @ 2.4GHz + 4x Cortex-A55 @ 1.8GHz)  
**Arquitetura:** ARM64  
**Storage:** eMMC / NVMe SSD  
**OS:** Ubuntu 22.04 Server ARM64

---

## 📋 Visão Geral

Este hardware hospeda **todos os 3 ecossistemas** do assistente de voz Aslam em um único dispositivo auto-contido.

```
┌─────────────────────────────────────────────────┐
│         Orange Pi 5 (16GB RAM, ARM64)           │
├─────────────────────────────────────────────────┤
│                                                 │
│  📦 Ecossistema MORDOMO (14 containers)         │
│  🎤 STT (6 containers):                          │
│  ├─ audio-capture-vad                           │
│  ├─ wake-word-detector                          │
│  ├─ speaker-verification                        │
│  ├─ whisper-asr                                 │
│  ├─ speaker-id-diarization                      │
│  └─ source-separation                           │
│  🔊 TTS (2 containers):                          │
│  ├─ audio-bridge (Rust - WebRTC ↔ Pipeline)     │
│  └─ tts-engine                                  │
│  🤖 OPENCLAW (1 container):                      │
│  └─ openclaw-agent (Gateway + Browser RPA +     │
│     Skills Hub + Brain Bridge — LLM próprio)    │
│  🧠 CORE (5 containers):                         │
│  ├─ mordomo-orchestrator (Unified Session+Core) │
│  ├─ mordomo-brain (LLM + RAG)                   │
│  ├─ system-watchdog (Thermal + DEFCON)          │
│  ├─ core-gateway (REST + WebSocket)             │
│  └─ dashboard-ui                                │
│                                                 │
│  🏗️ Ecossistema INFRAESTRUTURA (5 containers)   │
│  ├─ nats (message broker)                       │
│  ├─ consul (service discovery)                  │
│  ├─ qdrant (vectors)                            │
│  ├─ postgres (database)                         │
│  └─ aslam-app (tablet interface)                │
│                                                 │
│  📊 Ecossistema MONITORAMENTO (4 containers)    │
│  ├─ prometheus                                  │
│  ├─ loki                                        │
│  ├─ grafana                                     │
│  └─ promtail (log collector)                    │
│                                                 │
│  Total: 23 containers                           │
│  Implementados: 7/14 (Mordomo: 50%)             │
└─────────────────────────────────────────────────┘
```

---

## 📦 Containers e Repositórios

Este hardware executa **23 containers** distribuídos em 3 ecossistemas:

### 🎤 Ecossistema Mordomo (14 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **audio-capture-vad** | Captura de áudio com VAD | ✅ | [AslamSys/audio-capture-vad](https://github.com/AslamSys/audio-capture-vad) |
| **wake-word-detector** | Detecção de "ASLAM" | ✅ | [AslamSys/wake-word-detector](https://github.com/AslamSys/wake-word-detector) |
| **speaker-verification** | Autenticação por voz | ✅ | [AslamSys/speaker-verification](https://github.com/AslamSys/speaker-verification) |
| **whisper-asr** | Speech-to-Text | ✅ | [AslamSys/whisper-asr](https://github.com/AslamSys/whisper-asr) |
| **speaker-id-diarization** | Identificação de usuário | ⏳ | [AslamSys/speaker-id-diarization](https://github.com/AslamSys/speaker-id-diarization) |
| **source-separation** | Separação de vozes | ⏳ | [AslamSys/source-separation](https://github.com/AslamSys/source-separation) |
| **audio-bridge** | WebRTC ↔ NATS streaming | ✅ | [AslamSys/audio-bridge](https://github.com/AslamSys/audio-bridge) |
| **tts-engine** | Text-to-Speech | ✅ | [AslamSys/tts-engine](https://github.com/AslamSys/tts-engine) |
| **openclaw-agent** | Comunicação + RPA + Skills | ⏳ | [AslamSys/openclaw-agent](https://github.com/AslamSys/openclaw-agent) |
| **mordomo-orchestrator** | Estado + Contexto + Dispatcher | ✅ | [AslamSys/mordomo-orchestrator](https://github.com/AslamSys/mordomo-orchestrator) |
| **mordomo-brain** | LLM + RAG + Reasoning | ⏳ | [AslamSys/mordomo-brain](https://github.com/AslamSys/mordomo-brain) |
| **system-watchdog** | DEFCON + Thermal protection | ✅ | [AslamSys/system-watchdog](https://github.com/AslamSys/system-watchdog) |
| **core-gateway** | REST + WebSocket API | ✅ | [AslamSys/core-gateway](https://github.com/AslamSys/core-gateway) |
| **dashboard-ui** | Interface Canvas A2UI | ⏳ | [AslamSys/dashboard-ui](https://github.com/AslamSys/dashboard-ui) |

### 🏗️ Ecossistema Infraestrutura (5 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **nats** | Message broker | ✅ | [AslamSys/nats](https://github.com/AslamSys/nats) |
| **consul** | Service discovery | ✅ | [AslamSys/consul](https://github.com/AslamSys/consul) |
| **qdrant** | Vector database (RAG) | ✅ | [AslamSys/qdrant](https://github.com/AslamSys/qdrant) |
| **postgres** | Banco relacional | ✅ | [AslamSys/postgres](https://github.com/AslamSys/postgres) |
| **aslam-app** | Tablet interface (React) | ⏳ | [AslamSys/aslam-app](https://github.com/AslamSys/aslam-app) |

### 📊 Ecossistema Monitoramento (4 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **prometheus** | Coleta de métricas | ✅ | [AslamSys/prometheus](https://github.com/AslamSys/prometheus) |
| **loki** | Agregação de logs | ✅ | [AslamSys/loki](https://github.com/AslamSys/loki) |
| **grafana** | Dashboards visuais | ✅ | [AslamSys/grafana](https://github.com/AslamSys/grafana) |
| **promtail** | Coleta de logs | ✅ | [AslamSys/promtail](https://github.com/AslamSys/promtail) |

**💡 Status:**
- ✅ **Implementado** - Container funcionando
- ⏳ **Em desenvolvimento** - Em progresso  
- 📋 **Especificado** - Documentado, aguardando implementação

---

## 🎙️ Hardware Físico Conectado

### Periféricos do Orange Pi 5

```yaml
Áudio:
  Microfone: USB (entrada primária de voz)
  Speaker: USB (saída TTS)
  Formato: PCM 16kHz mono

Feedback Visual:
  LEDs GPIO (Raspberry Pi hat ou similar):
    - LED Azul: Idle (aguardando "ASLAM")
    - LED Verde: Ouvindo (após wake word)
    - LED Amarelo: Processando (LLM)
    - LED Vermelho: Erro

Interface Visual (Opcional):
  Tablet na parede:
    - Acesso: http://orange-pi-ip:3000
    - Função: Display secundário
    - Uso: Quando Mordomo precisa MOSTRAR algo
    - Exemplos: Gráficos, vídeos de câmera, mapas
    - NÃO é entrada de voz primária

Rede:
  Ethernet: Gigabit (recomendado)
  Wi-Fi 6: Backup
```

**Interação Principal:** Voz (mic USB) + LEDs (feedback visual)
**Tablet:** Apenas quando Mordomo precisa exibir informação visual complexa

---

## 💾 Especificações do Hardware

```yaml
CPU:
  SoC: Rockchip RK3588S
  Cores: 8 (big.LITTLE)
    - 4x Cortex-A76 @ 2.4 GHz (performance)
    - 4x Cortex-A55 @ 1.8 GHz (efficiency)
  GPU: Mali-G610 MP4
  NPU: 6 TOPS (AI acceleration)

Memória:
  RAM: 16GB LPDDR4/4x
  Velocidade: 2112 MHz

Storage:
  eMMC: até 256GB (opcional)
  NVMe: M.2 2280 (recomendado para produção)
  microSD: Suportado (não recomendado para produção)

Conectividade:
  Ethernet: Gigabit (1000 Mbps)
  Wi-Fi: Wi-Fi 6 (802.11ax)
  Bluetooth: 5.0

Áudio:
  Output: HDMI, 3.5mm jack
  Input: USB Audio ou I2S

USB:
  2x USB 3.0
  2x USB 2.0

Energia:
  Input: USB-C PD (5V/9V/12V)
  Consumo: 5-15W (idle-load)
```

---

## 📊 Análise de Recursos

### Estimativa de Consumo por Ecossistema

#### 🎙️ Mordomo (Containers de Aplicação)
```yaml
# STT Pipeline:
audio-capture-vad:      CPU: 5-10%  | RAM: 50MB
wake-word-detector:     CPU: 3-8%   | RAM: 80MB
speaker-verification:   CPU: 5-10%  | RAM: 150MB
whisper-asr:            CPU: 20-40% | RAM: 400MB
speaker-id-diarization: CPU: 10-15% | RAM: 300MB
source-separation:      CPU: 15-25% | RAM: 400MB (quando ativo)

# TTS Pipeline:
audio-bridge:           CPU: <1%    | RAM: 15MB (Rust - zero-copy)
tts-engine:             CPU: 10-20% | RAM: 80MB

# OpenClaw Agent (Comunicação + RPA):
openclaw-agent:         CPU: 30-50% | RAM: 1.2GB (2.0GB quando browser ativo)

# CORE:
mordomo-orchestrator:   CPU: 15-20% | RAM: 350MB (Unified: Session+LLM+Cache+Dispatcher+Events)
mordomo-brain:          CPU: 10-20% | RAM: 500MB (RAG + Advanced reasoning)
system-watchdog:        CPU: <1%    | RAM: 20MB
core-gateway:           CPU: 5-10%  | RAM: 150MB
dashboard-ui:           CPU: 2-5%   | RAM: 100MB (Canvas A2UI)

Total Mordomo:          CPU: ~130-235% (1.3-2.4 cores) | RAM: ~3.7GB (4.5GB browser ativo)
```

#### 🏗️ Infraestrutura
```yaml
nats:                   CPU: 5-10%  | RAM: 50MB
consul:                 CPU: 5-10%  | RAM: 100MB
qdrant:                 CPU: 10-20% | RAM: 500MB
postgres:               CPU: 5-10%  | RAM: 256MB
aslam-app:              CPU: 3-5%   | RAM: 50MB

Total Infraestrutura:   CPU: ~28-55% | RAM: ~956MB
```

#### 📊 Monitoramento
```yaml
prometheus:             CPU: 10-15% | RAM: 500MB
loki:                   CPU: 5-10%  | RAM: 200MB
grafana:                CPU: 5-10%  | RAM: 150MB
promtail:               CPU: 2-5%   | RAM: 30MB

Total Monitoramento:    CPU: ~22-40% | RAM: ~880MB
```

### 📈 Total Estimado

```yaml
CPU Total:  180-330% de uso (1.8-3.3 cores de 8 disponíveis)
RAM Total:  ~5.5GB de 16GB disponíveis (6.3GB browser ativo)
Storage:    18-33GB (containers + data)
Network:    Baixo (LAN local, < 10 Mbps)

Margem de Segurança:
  CPU: ✅ Sobra 4.7-6.2 cores (59-78% livre)
  RAM: ✅ Sobra ~10.5GB (66% livre, 61% com browser)
```

**Conclusão:** ✅ **VIÁVEL** - Orange Pi 5 16GB suporta confortavelmente os 23 containers (14 Mordomo + 5 Infra + 4 Monitor) com ampla margem de RAM

---

## ⚙️ Otimizações para ARM64

### 1. Modelos ML Otimizados
```yaml
Whisper ASR:
  Modelo: whisper.cpp (base ou small)
  Quantização: Q4 ou Q5
  VRAM: < 400MB

Brain (LLM):
  Modelo Primário: Cloud APIs (Claude, GPT-4, Gemini) via LiteLLM
  Fallback Local: Qwen 2.5 1.5B (quantizado Q4)
  Framework: LiteLLM + Ollama
  RAM: ~500MB (local fallback)

Speaker Verification:
  Modelo: Resemblyzer (leve)
  RAM: ~150MB
```

### 2. Containers Alpine
```dockerfile
# Usar base images menores
FROM python:3.11-alpine  # ~50MB vs ~900MB (debian)
FROM node:20-alpine      # ~120MB vs ~1GB
```

### 3. Resource Limits (Docker)
```yaml
services:
  whisper-asr:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 500M
        reservations:
          cpus: '0.5'
          memory: 300M
  
  mordomo-brain:
    deploy:
      resources:
        limits:
          cpus: '3.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1.5G
```

---

## 🚀 Deployment

### Pré-requisitos
```bash
# Sistema operacional
Ubuntu 22.04 Server ARM64

# Docker
sudo apt update
sudo apt install docker.io docker-compose-plugin

# Habilitar Docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

### Instalação Completa
```bash
# Clone projeto
git clone https://github.com/seu-repo/mordomo.git
cd mordomo/hardware/orange-pi-5-16gb

# Configurar environment
cp .env.example .env
nano .env  # Ajustar variáveis

# Deploy completo (3 ecossistemas)
docker compose up -d

# Verificar status
docker compose ps
```

### Docker Compose Master
```yaml
# docker-compose.yml (referencia os 3 ecossistemas)
version: '3.8'

services:
  # Incluir todos containers de:
  # - ecossistemas/mordomo/containers/*/docker-compose.yml
  # - ecossistemas/infraestrutura/containers/*/docker-compose.yml
  # - ecossistemas/monitoramento/containers/*/docker-compose.yml

networks:
  mordomo-net:
    driver: bridge

volumes:
  # Volumes persistentes para cada container
```

---

## 📊 Monitoramento de Hardware

### Dashboards Grafana
- CPU usage por core (A76 vs A55)
- RAM usage + swap
- Storage I/O (eMMC/NVMe)
- Network throughput
- Temperature (SoC, RAM)
- Power consumption

### Alertas
```yaml
- CPU > 80% por 5 min
- RAM > 7GB (87.5%)
- Storage > 90%
- Temperature > 75°C
```

---

## 🔧 Troubleshooting

### Out of Memory
```bash
# Verificar consumo
docker stats

# Reduzir Brain para cloud fallback
BRAIN_STRATEGY=cloud-only

# Ou usar modelo menor
BRAIN_MODEL=qwen2.5:1.5b
```

### CPU Throttling
```bash
# Verificar frequência
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq

# Melhorar cooling (adicionar heatsink/fan)
```

### Storage Full
```bash
# Limpar containers parados
docker system prune -a

# Reduzir retention
PROMETHEUS_RETENTION=7d
LOKI_RETENTION=7d
```

---

## 📁 Estrutura de Diretórios

```
orange-pi-5-16gb/
├── README.md (este arquivo)
├── docker-compose.yml
├── .env
├── ecossistemas/
│   ├── mordomo/
│   │   ├── README.md
│   │   └── containers/
│   │       ├── audio-capture-vad/
│   │       ├── wake-word-detector/
│   │       ├── speaker-verification/
│   │       ├── whisper-asr/
│   │       ├── speaker-id-diarization/
│   │       ├── source-separation/
│   │       ├── mordomo-core-api/
│   │       ├── mordomo-brain/
│   │       ├── tts-engine/
│   │       ├── event-bus/
│   │       ├── discovery-service/
│   │       └── dashboard-ui/
│   ├── infraestrutura/
│   │   ├── README.md
│   │   └── containers/
│   │       ├── nats/
│   │       ├── consul/
│   │       ├── qdrant/
│   │       └── postgres/
│   └── monitoramento/
│       ├── README.md
│       └── containers/
│           ├── prometheus/
│           ├── loki/
│           └── grafana/
└── scripts/
    ├── deploy.sh
    ├── backup.sh
    └── monitor.sh
```

---

## 🎯 Próximos Passos

1. ✅ **Documentação completa** (19/19 containers)
2. ⏳ **Testes de carga** (validar estimativas)
3. ⏳ **Benchmarks ARM64** (performance real)
4. ⏳ **Otimizações finais** (tuning)
5. ⏳ **Deploy em produção**

---

**Hardware Owner:** Renan  
**Última atualização:** 27/11/2025  
**Status:** 📝 Documentação Completa
