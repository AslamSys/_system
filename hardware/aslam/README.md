# Ecossistemas do Projeto Aslam

Este projeto é dividido em **3 ecossistemas principais**, cada um com seus containers e responsabilidades específicas.

## Estrutura de Ecossistemas

### 🏠 Mordomo
Sistema principal de assistente de voz inteligente com processamento de áudio, reconhecimento de fala, LLM, síntese de voz e OpenClaw Agent (comunicação + RPA).

**Componentes:** 14 containers
- STT (6), TTS (2), Core (5), OpenClaw Agent (1)

**Repositórios:**
- [mordomo-audio-bridge](https://github.com/AslamSys/mordomo-audio-bridge)
- [mordomo-audio-capture-vad](https://github.com/AslamSys/mordomo-audio-capture-vad)
- [mordomo-wake-word-detector](https://github.com/AslamSys/mordomo-wake-word-detector)
- [mordomo-speaker-verification](https://github.com/AslamSys/mordomo-speaker-verification)
- [mordomo-whisper-asr](https://github.com/AslamSys/mordomo-whisper-asr)
- [mordomo-speaker-id-diarization](https://github.com/AslamSys/mordomo-speaker-id-diarization)
- [mordomo-source-separation](https://github.com/AslamSys/mordomo-source-separation)
- [mordomo-core-gateway](https://github.com/AslamSys/mordomo-core-gateway)
- [mordomo-orchestrator](https://github.com/AslamSys/mordomo-orchestrator)
- [mordomo-brain](https://github.com/AslamSys/mordomo-brain)
- [mordomo-tts-engine](https://github.com/AslamSys/mordomo-tts-engine)
- [mordomo-system-watchdog](https://github.com/AslamSys/mordomo-system-watchdog)
- [mordomo-dashboard-ui](https://github.com/AslamSys/mordomo-dashboard-ui)
- [mordomo-openclaw-agent](https://github.com/AslamSys/mordomo-openclaw-agent)

### 🔧 Infraestrutura
Serviços de base para comunicação, descoberta de serviços e armazenamento de dados.

**Componentes:** 5 containers
- NATS (message broker), Consul (discovery), Qdrant (vetores), PostgreSQL (persistência), Aslam App (UI)

**Repositórios:**
- NATS, Consul, Qdrant, PostgreSQL, Aslam App (configurações em _system)

### 📊 Monitoramento
Observabilidade completa do sistema com métricas, logs e dashboards.

**Componentes:** 4 containers
- Prometheus, Grafana, Loki, Promtail

**Repositórios:**
- Prometheus, Grafana, Loki, Promtail (configurações em _system)

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

Consulte os repositórios de cada container listados acima para documentação detalhada.
