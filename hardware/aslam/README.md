# Ecossistemas do Projeto Aslam

Este projeto é dividido em **3 ecossistemas principais**, cada um com seus containers e responsabilidades específicas.

## Estrutura de Ecossistemas

### 🏠 [Mordomo](./mordomo/)
Sistema principal de assistente de voz inteligente com processamento de áudio, reconhecimento de fala, LLM, síntese de voz e OpenClaw Agent (comunicação + RPA).

**Componentes:** 14 containers
- STT (6), TTS (2), Core (5), OpenClaw Agent (1)

### 🔧 [Infraestrutura](./infraestrutura/)
Serviços de base para comunicação, descoberta de serviços e armazenamento de dados.

**Componentes:** 5 containers
- NATS (message broker), Consul (discovery), Qdrant (vetores), PostgreSQL (persistência), Aslam App (UI)

### 📊 [Monitoramento](./monitoramento/)
Observabilidade completa do sistema com métricas, logs e dashboards.

**Componentes:** 4 containers
- Prometheus, Grafana, Loki, Promtail

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
