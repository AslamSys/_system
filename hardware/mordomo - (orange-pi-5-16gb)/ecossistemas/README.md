# Ecossistemas do Projeto Aslam

> 📍 **Navegação:** [🏠 Início](../../../README.md) > [🔧 Hardware](../../README.md) > [🎯 Mordomo](../README.md) > [🌐 Ecossistemas](README.md)

Este projeto é dividido em **4 ecossistemas principais**, cada um com seus containers e responsabilidades específicas.

## Estrutura de Ecossistemas

### 🏠 [Mordomo](./mordomo/)
Sistema principal de assistente de voz inteligente com processamento de áudio, reconhecimento de fala, LLM, síntese de voz e OpenClaw Agent (comunicação + RPA).

**Componentes:** 15 containers
- STT (6), TTS (2), Core (6), OpenClaw Agent (1)

### 📱 [IoT](./iot/)
Gerenciamento de dispositivos ESP32 DIY via Wi-Fi Access Point (hostapd no wlan0) e Bluetooth BLE. Sem LLM — execução direta de comandos do Mordomo.

**Componentes:** 4 containers
- MQTT Broker, IoT Orchestrator, State Cache (Redis), Bluetooth Scanner

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

- **Orange Pi 5 Ultra 16GB** — ARM64, Wi-Fi 6 como AP para IoT, eth0 para rede doméstica
- 28 containers no total

---

## Comunicação entre Ecossistemas

```
┌─────────────────┐   ┌─────────────────┐
│    Mordomo      │   │      IoT        │
│ (15 containers) │   │ (4 containers)  │
└────────┬────────┘   └───────┬─────────┘
         │                    │ MQTT → ESP32 (wlan0 AP)
         │                    │ BLE  → Smartphones
         ├────────────────────┤
         │ NATS            📁 Infra
         │ Consul
         │ Qdrant
         │ PostgreSQL
         ▼
┌─────────────────┐
│ Monitoramento   │
│ (4 containers)  │
└─────────────────┘
```

---

## Visão Geral Rápida

| Ecossistema | Função Principal | Containers |
|-------------|------------------|------------|
| **Mordomo** | Assistente de voz IA + OpenClaw | 15 |
| **IoT** | ESP32 DIY + BLE Presence (wlan0 AP) | 4 |
| **Infraestrutura** | Comunicação e dados | 5 |
| **Monitoramento** | Observabilidade | 4 |

**Total:** 28 containers modulares e independentes

---

Consulte cada diretório para documentação detalhada de cada ecossistema.
