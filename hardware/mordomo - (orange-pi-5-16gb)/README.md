# 🍊 Orange Pi 5 Ultra (16GB RAM)

> 📍 **Navegação:** [🏠 Início](../../README.md) > [🔧 Hardware](../README.md) > [🎯 Mordomo + IoT (Orange Pi 5 Ultra 16GB)](README.md)

**Hardware:** Orange Pi 5 Ultra  
**RAM:** 16GB LPDDR4/4x  
**CPU:** Rockchip RK3588S (4x Cortex-A76 @ 2.4GHz + 4x Cortex-A55 @ 1.8GHz)  
**Arquitetura:** ARM64  
**Storage:** eMMC / NVMe SSD  
**OS:** Ubuntu 22.04 Server ARM64

---

## 📋 Visão Geral

Este hardware hospeda **todos os 4 ecossistemas** do núcleo do sistema em um único dispositivo auto-contido.

```
┌─────────────────────────────────────────────────┐
│         Orange Pi 5 Ultra (16GB RAM, ARM64)       │
├─────────────────────────────────────────────────┤
│                                                 │
│  📦 Ecossistema MORDOMO (21 containers)         │
│  🎤 STT (6 containers):                          │
│  ├─ audio-capture-vad                           │
│  ├─ wake-word-detector                          │
│  ├─ speaker-verification                        │
│  ├─ whisper-asr                                 │
│  ├─ speaker-id-diarization                      │
│  └─ source-separation                           │
│  🔊 Output (3 containers):                       │
│  ├─ audio-bridge (Rust - WebRTC ↔ Pipeline)     │
│  ├─ tts-engine                                  │
│  └─ visual-feedback (LEDs GPIO)                 │
│  🤖 OPENCLAW (1 container):                      │
│  └─ openclaw-agent (Gateway + Browser RPA +     │
│     Skills Hub + Brain Bridge — LLM próprio)    │
│  🧠 CORE (7 containers):                         │
│  ├─ mordomo-orchestrator (Unified Session+Core) │
│  ├─ mordomo-brain (LLM + RAG)                   │
│  ├─ system-watchdog (Thermal + DEFCON)          │
│  ├─ core-gateway (REST + WebSocket)             │
│  ├─ skills-runner (Python Sandbox)              │
│  ├─ action-dispatcher (Ação → Executor)         │
│  └─ dashboard-ui                                │
│  👤 IDENTIDADE (2 containers):                   │
│  ├─ mordomo-people (Perfis + Auth)              │
│  └─ mordomo-vault (Secrets + Keys)              │
│  💳 FINANCAS (2 containers):                     │
│  ├─ mordomo-financas-pix (PIX Gateway)          │
│  └─ mordomo-financas-contas (Contas/Saldo)      │
│                                                 │
│  📱 Ecossistema IoT (4 containers)               │
│  ├─ iot-orchestrator (NATS → MQTT)              │
│  ├─ iot-mqtt-broker (Mosquitto - ESP32 AP)      │
│  ├─ iot-state-cache (Redis < 5ms)               │
│  └─ iot-tv-connector (TV/HDMI control)          │
│                                                 │
│  🏗️ Ecossistema INFRAESTRUTURA (5 containers)   │
│  ├─ nats (message broker)                       │
│  ├─ consul (service discovery)                  │
│  ├─ qdrant (vectors)                            │
│  ├─ postgres (database)                         │
│  └─ llm-gateway (LiteLLM Proxy :4000)           │
│                                                 │
│  📊 Ecossistema MONITORAMENTO (4 containers)    │
│  ├─ prometheus                                  │
│  ├─ loki                                        │
│  ├─ grafana                                     │
│  └─ promtail (log collector)                    │
│                                                 │
│  Total: 34 containers                           │
│  📊 Status: Todos em planejamento (📋)           │
└─────────────────────────────────────────────────┘
```

---

## 📦 Containers e Repositórios

Este hardware executa **34 containers** distribuídos em 4 ecossistemas:

### 🎤 Ecossistema Mordomo (21 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **audio-capture-vad** | Captura de áudio com VAD | 📋 | [AslamSys/mordomo-audio-capture-vad](https://github.com/AslamSys/mordomo-audio-capture-vad) |
| **wake-word-detector** | Detecção de "ASLAM" | 📋 | [AslamSys/mordomo-wake-word-detector](https://github.com/AslamSys/mordomo-wake-word-detector) |
| **speaker-verification** | Autenticação por voz | 📋 | [AslamSys/mordomo-speaker-verification](https://github.com/AslamSys/mordomo-speaker-verification) |
| **whisper-asr** | Speech-to-Text | 📋 | [AslamSys/mordomo-whisper-asr](https://github.com/AslamSys/mordomo-whisper-asr) |
| **speaker-id-diarization** | Identificação de usuário | 📋 | [AslamSys/mordomo-speaker-id-diarization](https://github.com/AslamSys/mordomo-speaker-id-diarization) |
| **source-separation** | Separação de vozes | 📋 | [AslamSys/mordomo-source-separation](https://github.com/AslamSys/mordomo-source-separation) |
| **audio-bridge** | WebRTC ↔ NATS streaming | 📋 | [AslamSys/mordomo-audio-bridge](https://github.com/AslamSys/mordomo-audio-bridge) |
| **tts-engine** | Text-to-Speech | 📋 | [AslamSys/mordomo-tts-engine](https://github.com/AslamSys/mordomo-tts-engine) |
| **openclaw-agent** | Comunicação + RPA + Skills | 📋 | [AslamSys/mordomo-openclaw-agent](https://github.com/AslamSys/mordomo-openclaw-agent) |
| **mordomo-orchestrator** | Estado + Contexto + Dispatcher | 📋 | [AslamSys/mordomo-orchestrator](https://github.com/AslamSys/mordomo-orchestrator) |
| **mordomo-brain** | LLM + RAG + Reasoning | 📋 | [AslamSys/mordomo-brain](https://github.com/AslamSys/mordomo-brain) |
| **system-watchdog** | DEFCON + Thermal protection | ✅ | [AslamSys/mordomo-system-watchdog](https://github.com/AslamSys/mordomo-system-watchdog) |
| **core-gateway** | REST + WebSocket API | 📋 | [AslamSys/mordomo-core-gateway](https://github.com/AslamSys/mordomo-core-gateway) |
| **skills-runner** | Executor Python Sandbox | 📋 | [AslamSys/mordomo-skills-runner](https://github.com/AslamSys/mordomo-skills-runner) |
| **action-dispatcher** | Despacho de ações | 📋 | [AslamSys/mordomo-action-dispatcher](https://github.com/AslamSys/mordomo-action-dispatcher) |
| **dashboard-ui** | Interface Canvas A2UI | 📋 | [AslamSys/mordomo-dashboard-ui](https://github.com/AslamSys/mordomo-dashboard-ui) |
| **visual-feedback** | LEDs GPIO + feedback visual | 📋 | [AslamSys/mordomo-visual-feedback](https://github.com/AslamSys/mordomo-visual-feedback) |
| **mordomo-people** | Perfis de usuário + Auth | 📋 | [AslamSys/mordomo-people](https://github.com/AslamSys/mordomo-people) |
| **mordomo-vault** | Secrets + Chaves criptografadas | 📋 | [AslamSys/mordomo-vault](https://github.com/AslamSys/mordomo-vault) |
| **mordomo-financas-pix** | Gateway PIX | 📋 | [AslamSys/mordomo-financas-pix](https://github.com/AslamSys/mordomo-financas-pix) |
| **mordomo-financas-contas** | Contas + Saldo | 📋 | [AslamSys/mordomo-financas-contas](https://github.com/AslamSys/mordomo-financas-contas) |

### 📱 Ecossistema IoT (4 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **iot-orchestrator** | Tradução NATS → MQTT para ESP32 | 📋 | [AslamSys/mordomo-iot-orchestrator](https://github.com/AslamSys/mordomo-iot-orchestrator) |
| **iot-mqtt-broker** | Broker MQTT local (Mosquitto) | ✅ | [AslamSys/mordomo-iot-mqtt-broker](https://github.com/AslamSys/mordomo-iot-mqtt-broker) |
| **iot-state-cache** | Cache Redis para estados IoT | ✅ | [AslamSys/mordomo-iot-state-cache](https://github.com/AslamSys/mordomo-iot-state-cache) |
| **iot-tv-connector** | Controle de TV via HDMI/IP | 📋 | [AslamSys/mordomo-iot-tv-connector](https://github.com/AslamSys/mordomo-iot-tv-connector) |

_Nota: O Wi-Fi 6 do Orange Pi 5 Ultra opera como **Access Point dedicado** (hostapd + interface virtual) para os dispositivos ESP32 na rede `10.0.0.x`. A conexão com a rede doméstica/internet é feita exclusivamente via **eth0** (Gigabit Ethernet)._

### 🏗️ Ecossistema Infraestrutura (5 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **nats** | Message broker | ✅ | *Repositório aguardando criação* |
| **consul** | Service discovery | ✅ | *Repositório aguardando criação* |
| **qdrant** | Vector database (RAG) | ✅ | *Repositório aguardando criação* |
| **postgres** | Banco relacional | ✅ | *Repositório aguardando criação* |
| **llm-gateway** | LiteLLM Proxy — roteamento LLM cloud/local | ✅ | *Repositório aguardando criação* |

### 📊 Ecossistema Monitoramento (4 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **prometheus** | Coleta de métricas | ✅ | *Repositório aguardando criação* |
| **loki** | Agregação de logs | ✅ | *Repositório aguardando criação* |
| **grafana** | Dashboards visuais | ✅ | *Repositório aguardando criação* |
| **promtail** | Coleta de logs | ✅ | *Repositório aguardando criação* |

**💡 Status:**
- ✅ **Implementado** - Container funcionando em produção
- ⏳ **Em desenvolvimento** - Código em progresso ativo
- 📋 **Especificado** - Documentado, repositório criado, aguardando implementação

**📊 Fase atual:** Infra + Monitoramento + IoT pull-and-run ✅ prontos | Mordomo custom services 📋 aguardando implementação
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
    - Acesso: http://orange-pi-ip:3000  (dashboard-ui)
    - Função: Display secundário via browser
    - Uso: Quando Mordomo precisa MOSTRAR algo
    - Exemplos: Gráficos, vídeos de câmera, mapas
    - NÃO é entrada de voz primária
    - Nota: sem app dedicado — usa o dashboard-ui direto no browser

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
mordomo-brain:          CPU: 5-10%  | RAM: 200MB (RAG + LiteLLM client — sem modelo local)
system-watchdog:        CPU: <1%    | RAM: 20MB
core-gateway:           CPU: 5-10%  | RAM: 150MB
dashboard-ui:           CPU: 2-5%   | RAM: 100MB (Canvas A2UI)

Total Mordomo:          CPU: ~125-225% (1.2-2.2 cores) | RAM: ~3.4GB (4.2GB browser ativo)
```

#### 🏗️ Infraestrutura
```yaml
nats:                   CPU: 5-10%  | RAM: 50MB
consul:                 CPU: 5-10%  | RAM: 100MB
qdrant:                 CPU: 10-20% | RAM: 500MB
postgres:               CPU: 5-10%  | RAM: 256MB
llm-gateway:            CPU: <2%    | RAM: 100-200MB (LiteLLM Proxy, I/O bound)

Total Infraestrutura:   CPU: ~25-52% | RAM: ~1.0GB
```

#### 📊 Monitoramento
```yaml
prometheus:             CPU: 10-15% | RAM: 500MB
loki:                   CPU: 5-10%  | RAM: 200MB
grafana:                CPU: 5-10%  | RAM: 150MB
promtail:               CPU: 2-5%   | RAM: 30MB

Total Monitoramento:    CPU: ~22-40% | RAM: ~880MB
```

#### 📱 IoT
```yaml
iot-orchestrator:       CPU: 5-10%  | RAM: 180MB  (NATS→MQTT bridge, Python)
mqtt-broker:            CPU: 1-3%   | RAM: 100MB  (Mosquitto, extremamente leve)
iot-state-cache:        CPU: 1-2%   | RAM: 80MB   (Redis — estados ESP32, TTL 5min)
bluetooth-scanner:      CPU: 3-5%   | RAM: 100MB  (BlueZ + Python, scan contínuo)

Total IoT:              CPU: ~10-20% (0.1-0.2 core) | RAM: ~460MB
```

_Nota: O IoT **não tem IA**. Zero inferência, zero modelo. É puro roteamento de mensagens — NATS↔MQTT — e espelho de estado em Redis._

---

### 📈 Total Consolidado (34 containers)

```
┌─────────────────────────────────────────────────────────────────┐
│              RESUMO DE CONSUMO — Orange Pi 5 Ultra              │
├──────────────────────┬─────────────┬─────────────┬─────────────┤
│ Ecossistema          │ Containers  │ RAM (idle)  │ RAM (pico)  │
├──────────────────────┼─────────────┼─────────────┼─────────────┤
│ 🏠 Mordomo           │ 21          │ ~3.9 GB     │ ~4.7 GB     │
│ 📱 IoT               │ 4           │ ~460 MB     │ ~460 MB     │
│ 🔧 Infraestrutura    │ 5           │ ~1.0 GB     │ ~1.0 GB     │
│ 📊 Monitoramento     │ 4           │ ~880 MB     │ ~1.0 GB     │
├──────────────────────┼─────────────┼─────────────┼─────────────┤
│ Subtotal containers  │ 34          │ ~6.3 GB     │ ~7.2 GB     │
│ OS + Docker runtime  │ —           │ ~1.5 GB     │ ~1.5 GB     │
├──────────────────────├─────────────├─────────────├─────────────┤
│ TOTAL                │ —           │ ~7.8 GB     │ ~8.7 GB     │
│ DISPONÍVEL (16GB)    │ —           │ ~8.2 GB     │ ~7.3 GB     │
│ MARGEM LIVRE         │ —           │ 51%         │ 46%         │
└──────────────────────┴─────────────┴─────────────┴─────────────┘
```

```yaml
CPU Total (pico):  200-390% (2.0-3.9 cores de 8 disponíveis)
RAM Total (pico):  ~8.7GB de 16GB
Storage:           20-35GB (containers + data)
Margem CPU:        ✅ Sobra 4.1-5.8 cores (51-73% livre)
Margem RAM:        ✅ Sobra ~7.2GB no pico (45% livre)
```

> **Pico** = browser do openclaw-agent ativo simultaneamente com todos os containers.  
> O Whisper ASR e o browser são os dois maiores consumidores individuais (~1.5GB e ~2GB respectivamente).

**Conclusão:** ✅ **VIÁVEL** — 34 containers rodam com ~46% de RAM livre mesmo no pico. O `llm-gateway` centraliza todo o controle de inferência; os 7 novos containers (visual-feedback, action-dispatcher, people, vault, financas) adicionam apenas ~500MB.

---

## ⚙️ Otimizações para ARM64

### 1. Modelos ML Otimizados
```yaml
Whisper ASR:
  Modelo: whisper.cpp (base ou small)
  Quantização: Q4 ou Q5
  VRAM: < 400MB

Brain (LLM):
  Estratégia: Cloud APIs exclusivamente via LiteLLM
  Provedores: Claude (Anthropic), GPT-4 (OpenAI), Gemini (Google)
  Framework: LiteLLM (abstração unificada)
  RAM: ~200MB (sem modelo local)
  Nota: LLM local futura → Jetson Orin Nano Super dedicado (hardware separado)

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
├── docker-compose.yml              # Master: inclui todos os ecossistemas via extends/include
├── .env                            # Variáveis globais (API keys, IPs, portas)
│
├── ecossistemas/
│   ├── mordomo/                    # 21 containers
│   │   ├── README.md
│   │   ├── docker-compose.yml      # Todos os 21 containers mordomo-*
│   │   └── containers/
│   │       ├── audio-capture-vad/
│   │       ├── wake-word-detector/
│   │       ├── speaker-verification/
│   │       ├── whisper-asr/
│   │       ├── speaker-id-diarization/
│   │       ├── source-separation/
│   │       ├── audio-bridge/
│   │       ├── tts-engine/
│   │       ├── visual-feedback/
│   │       ├── openclaw-agent/
│   │       ├── mordomo-orchestrator/
│   │       ├── mordomo-brain/
│   │       ├── system-watchdog/
│   │       ├── core-gateway/
│   │       ├── skills-runner/
│   │       ├── action-dispatcher/
│   │       ├── dashboard-ui/
│   │       ├── mordomo-people/
│   │       ├── mordomo-vault/
│   │       ├── mordomo-financas-pix/
│   │       └── mordomo-financas-contas/
│   │
│   ├── iot/                        # 4 containers
│   │   ├── README.md
│   │   ├── docker-compose.yml      # iot-orchestrator, mqtt-broker, state-cache, tv-connector
│   │   └── containers/
│   │       ├── iot-orchestrator/
│   │       ├── iot-mqtt-broker/
│   │       ├── iot-state-cache/
│   │       └── iot-tv-connector/
│   │
│   ├── infraestrutura/             # 5 containers
│   │   ├── README.md
│   │   ├── docker-compose.yml      # nats, consul, qdrant, postgres, llm-gateway
│   │   └── containers/
│   │       ├── nats/
│   │       ├── consul/
│   │       ├── qdrant/
│   │       ├── postgres/
│   │       └── llm-gateway/
│   │
│   └── monitoramento/              # 4 containers
│       ├── README.md
│       ├── docker-compose.yml      # prometheus, loki, grafana, promtail
│       └── containers/
│           ├── prometheus/
│           ├── loki/
│           ├── grafana/
│           └── promtail/
│
└── scripts/
    ├── deploy.sh                   # docker compose up -d (todos os ecossistemas)
    ├── backup.sh                   # dump postgres + volumes
    └── monitor.sh                  # docker stats + alertas
```

> **Hierarquia dos Compose:**  
> O `docker-compose.yml` raiz referencia os 4 arquivos de ecossistema via `include:`.  
> Cada ecossistema pode ser iniciado de forma independente com `docker compose -f ecossistemas/mordomo/docker-compose.yml up -d`.  
> Todos os containers compartilham a rede `mordomo-net` definida no Compose raiz.

---

## 🎯 Próximos Passos

1. ✅ **Documentação completa** (34/34 containers)
2. ⏳ **Testes de carga** (validar estimativas)
3. ⏳ **Benchmarks ARM64** (performance real)
4. ⏳ **Otimizações finais** (tuning)
5. ⏳ **Deploy em produção**

---

**Hardware Owner:** Renan  
**Última atualização:** 14/04/2026  
**Status:** 📝 Documentação Completa
