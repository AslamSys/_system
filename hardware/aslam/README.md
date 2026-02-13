# Ecossistemas do Projeto Aslam

Este projeto é dividido em **3 ecossistemas principais**, cada um com seus containers e responsabilidades específicas.

## Estrutura de Ecossistemas

### 🏠 Mordomo
Sistema principal de assistente de voz inteligente com processamento de áudio, reconhecimento de fala, LLM, síntese de voz e OpenClaw Agent (comunicação + RPA).

**Componentes:** 14 containers
- STT (6), TTS (2), Core (5), OpenClaw Agent (1)

**Repositórios:**
- [aslam-audio-bridge](https://github.com/AslamSys/aslam-audio-bridge)
- [aslam-audio-capture-vad](https://github.com/AslamSys/aslam-audio-capture-vad)
- [aslam-wake-word-detector](https://github.com/AslamSys/aslam-wake-word-detector)
- [aslam-speaker-verification](https://github.com/AslamSys/aslam-speaker-verification)
- [aslam-whisper-asr](https://github.com/AslamSys/aslam-whisper-asr)
- [aslam-speaker-id-diarization](https://github.com/AslamSys/aslam-speaker-id-diarization)
- [aslam-source-separation](https://github.com/AslamSys/aslam-source-separation)
- [aslam-core-gateway](https://github.com/AslamSys/aslam-core-gateway)
- [aslam-orchestrator](https://github.com/AslamSys/aslam-orchestrator)
- [aslam-brain](https://github.com/AslamSys/aslam-brain)
- [aslam-tts-engine](https://github.com/AslamSys/aslam-tts-engine)
- [aslam-system-watchdog](https://github.com/AslamSys/aslam-system-watchdog)
- [aslam-dashboard-ui](https://github.com/AslamSys/aslam-dashboard-ui)
- [aslam-openclaw-agent](https://github.com/AslamSys/aslam-openclaw-agent)

### 🔧 Infraestrutura
Serviços de base para comunicação, descoberta de serviços e armazenamento de dados.

**Componentes:** 5 containers
- NATS (message broker), Consul (discovery), Qdrant (vetores), PostgreSQL (persistência), Aslam App (UI)

**Repositórios:**
- [aslam-nats](https://github.com/AslamSys/aslam-nats)
- [aslam-consul](https://github.com/AslamSys/aslam-consul)
- [aslam-qdrant](https://github.com/AslamSys/aslam-qdrant)
- [aslam-postgres](https://github.com/AslamSys/aslam-postgres)
- [aslam-app](https://github.com/AslamSys/aslam-app)

### 📊 Monitoramento
Observabilidade completa do sistema com métricas, logs e dashboards.

**Componentes:** 4 containers
- Prometheus, Grafana, Loki, Promtail

**Repositórios:**
- [aslam-prometheus](https://github.com/AslamSys/aslam-prometheus)
- [aslam-grafana](https://github.com/AslamSys/aslam-grafana)
- [aslam-loki](https://github.com/AslamSys/aslam-loki)
- [aslam-promtail](https://github.com/AslamSys/aslam-promtail)

---

## Hardware Alvo

- **Raspberry Pi** ou **Orange Pi 5 16GB**
- Otimizado para ARM64
- Foco em eficiência e baixo consumo

---

## Comunicação entre Ecossistemas

```
┌─────────────────┐
│    Mordomo      │
│  (14 containers)│
└────────┬────────┘
         │
         ├──► NATS (message broker - Infraestrutura)
         ├──► Consul (service discovery - Infraestrutura)
         ├──► Qdrant (vetores - Infraestrutura)
         └──► PostgreSQL (dados - Infraestrutura)
              │
              ▼
    ┌─────────────────┐
    │ Monitoramento   │
    │ (4 containers)  │
    │ Prometheus      │
    │ Grafana         │
    │ Loki            │
    │ Promtail        │
    └─────────────────┘
```

---

## Visão Geral Rápida

| Ecossistema | Função Principal | Containers |
|-------------|------------------|------------|
| **Mordomo** | Assistente de voz IA + OpenClaw | 14 |
| **Infraestrutura** | Comunicação e dados | 5 |
| **Monitoramento** | Observabilidade | 4 |

**Total:** 23 containers modulares e independentes

---

Consulte cada diretório para documentação detalhada de cada ecossistema.
