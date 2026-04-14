# Hardware - Arquitetura Modular Distribuída

> 📍 **Navegação:** [🏠 Início](../README.md) > [🔧 Hardware](README.md)

Este diretório organiza todos os hardwares do sistema Mordomo. Cada hardware é dedicado a um módulo específico. **LLM roda exclusivamente via Cloud API (LiteLLM)** em todos os módulos — sem modelos locais nos hardwares de aplicação.

## 📊 Resumo da Infraestrutura

| Hardware | Módulo | RAM | LLM | NPU/GPU | Preço | Consumo |
|----------|--------|-----|-----|---------|-------|---------|
| Orange Pi 5 Ultra 16GB | ✅ Mordomo Central + OpenClaw + **IoT** (34 containers) | 16GB | Cloud API (LiteLLM) | 6 TOPS | $130 | 10-18W |
| Jetson Orin Nano 8GB | Segurança (Vision) (7 containers) | 8GB | Qwen 3B Vision (local, necessário para RT) | 1024 CUDA | $312 | 10-15W |
| RPi 5 16GB | Investimentos (7 containers) | 16GB | Cloud API (LiteLLM) | - | $140 | 6-10W |
| NAS (RPi 5 8GB) | NAS + Entretenimento (9 containers) | 8GB | Cloud API (LiteLLM) | - | $355 | 6-10W |

**TOTAL**: **4 hardwares** | **$937** | **32-53W**

_Nota: IoT migrado para o Orange Pi 5 Ultra (Wi-Fi 6 como Access Point + eth0 para rede doméstica). Pagamentos eliminado — absorvido pelo Mordomo (mordomo-financas-pix + mordomo-financas-contas). Entretenimento eliminado — Jellyfin migrado para o NAS._

## 🎯 Justificativa Técnica

### **Por que Cloud API em vez de LLM local?**

1. **Hardware leve**: RPi 5 8GB não é feito para inferir LLMs — 2.5GB ocupados por Qwen 1.5B é desperdício de RAM que outros containers precisam
2. **Qualidade**: Claude / GPT-4 / Gemini Flash são ordens de magnitude melhores que Qwen 1.5B
3. **Latência aceitável**: Para comandos de entretenimento, NAS e IoT, 300-800ms via API é imperceptivel
4. **Escalabilidade**: Quando quiser local, **um único Jetson Orin Nano Super serve todos os módulos** via Ollama API

### **Quando usar LLM local? (futuro)**

Se privacidade total ou offline for necessário: **Jetson Orin Nano Super** ($249, 67 TOPS, 8GB unificado) roda como servidor Ollama centralizado — todos os brains do sistema apontam para `http://jetson-llm:11434`. Modelos possíveis: Llama 3.1 8B Q4, Qwen 2.5 7B Q4 (~4GB cada).

### **Quando usar Jetson para Segurança?**

- **Segurança**: 1024 CUDA cores são essenciais para YOLO + reconhecimento facial em tempo real em múltiplas câmeras. Aqui LLM Vision local é **necessária** (baixa latência, sem enviar frames para cloud)

## 📁 Estrutura de Diretórios

```
hardware/
├── mordomo - (orange-pi-5-16gb)/         # Central: Mordomo + IoT — 34 containers
│   └── ecossistemas/
│       ├── mordomo/              # 21 containers (STT + Output + OpenClaw + Core + Identity + Financas)
│       ├── iot/                  # 4 containers (Wi-Fi AP + MQTT + Redis + TV)
│       ├── infraestrutura/       # 6 containers (NATS, Consul, Qdrant, Postgres, App, LLM Gateway)
│       └── monitoramento/        # 4 containers (Prometheus, Loki, Grafana, Promtail)
│
├── seguranca - (jetson-orin-nano)/       # Segurança — 7 containers + LLM Vision
│   └── ecossistemas/
│       └── seguranca/
│
├── investimentos - (raspberry-pi-5-16gb)/ # Investimentos — 7 containers
│   └── ecossistemas/
│       └── investimentos/
│
└── nas - (raspberry-pi-5-8gb)/           # NAS + Jellyfin — 9 containers
    └── ecossistemas/
        └── nas/
```

## 🔌 Requisitos de Energia

### Fonte de Alimentação Total
- **Consumo Médio**: ~32W
- **Consumo Pico**: ~53W
- **Recomendação**: UPS 650VA ou fonte 12V estabilizada

### Por Hardware
- **Orange Pi 5 Ultra**: 5V/4A (10-18W) - USB-C PD
- **Jetson Orin Nano**: 12V/2A (10-15W) - DC Barrel
- **RPi 5 16GB (Investimentos)**: 5V/5A (6-10W) - USB-C PD
- **RPi 5 8GB (NAS)**: 5V/5A (6-10W) - USB-C PD

## 🌐 Rede e Comunicação

### Requisitos de Rede
- **Switch Gigabit**: 8+ portas (TPLink TL-SG108 ~$25)
- **Roteador**: Suporte VLAN para segmentação
- **Cabo Cat6**: 1m por dispositivo

### Infraestrutura Compartilhada
- **NATS Cluster**: Roda no Mordomo (Orange Pi 5 16GB)
- **Consul Cluster**: Roda no Mordomo (Orange Pi 5 16GB)
- **Qdrant Vector DB**: Roda no Mordomo (Orange Pi 5 16GB)
- **PostgreSQL**: Roda no Mordomo (Orange Pi 5 16GB)

### Por Hardware
- **Mordomo (Orange Pi)**: MicroSD 128GB (~$20) + **SSD NVMe 256GB** (~$35)
- **Segurança (Jetson)**: MicroSD 128GB (~$20) - vídeos temporários
- **Investimentos (RPi 5 16GB)**: MicroSD 128GB (~$20) - dados históricos
- **NAS (RPi 5 8GB)**: MicroSD 64GB (~$12) + **2x HDD 4TB RAID 1** (~$180) + **SSD NVMe 1TB** (~$70)

**Total Armazenamento**: ~$357

## 📦 Custo Total do Projeto

| Categoria | Custo |
|-----------|-------|
| Hardwares | $937 |
| Armazenamento | $357 |
| Rede (switch + cabos) | $40 |
| Fontes de Alimentação | $60 |
| Cases e Refrigeração | $50 |
| **TOTAL** | **$1.444** |

## 🚀 Roadmap de Implementação

1. **Fase 1**: ✅ Mordomo + OpenClaw + IoT (Orange Pi 5 Ultra 16GB) - Sistema central (34 containers)
2. **Fase 2**: NAS + Jellyfin (RPi 5 8GB) - Armazenamento e media
3. **Fase 3**: Segurança (Jetson Orin Nano) - Câmeras e monitoramento
4. **Fase 4**: Investimentos (RPi 5 16GB) - Trading e análise financeira

_Nota: Pagamentos eliminado — absorvido pelo Mordomo. Entretenimento eliminado — Jellyfin migrado para o NAS. IoT integrado ao Orange Pi 5 Ultra. RPi 3B+ eliminado._

## 📈 Escalabilidade

### Adicionar Novos Módulos
1. Provisionar hardware (RPi 5 ou Orange Pi)
2. Instalar Docker + NATS client
3. Registrar no Consul (auto-discovery)
4. Implementar containers do ecossistema
5. Brain do Mordomo aprende novos comandos automaticamente

### Migração Cloud (Futuro)
- Módulos podem migrar para VPS/Cloud mantendo protocolo NATS
- Híbrido: Hardware local + Cloud para módulos pesados
