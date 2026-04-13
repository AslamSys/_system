# Hardware - Arquitetura Modular Distribuída

> 📍 **Navegação:** [🏠 Início](../README.md) > [🔧 Hardware](README.md)

Este diretório organiza todos os hardwares do sistema Mordomo. Cada hardware é dedicado a um módulo específico. **LLM roda exclusivamente via Cloud API (LiteLLM)** em todos os módulos — sem modelos locais nos hardwares de aplicação.

## 📊 Resumo da Infraestrutura

| Hardware | Módulo | RAM | LLM | NPU/GPU | Preço | Consumo |
|----------|--------|-----|-----|---------|-------|---------|
| Orange Pi 5 Ultra 16GB | ✅ Mordomo Central + OpenClaw + **IoT** | 16GB | Cloud API (LiteLLM) | 6 TOPS | $130 | 10-18W |
| Jetson Orin Nano | Segurança (Vision) | 8GB | Qwen 3B Vision (local, necessário para RT) | 1024 CUDA | $249 | 10-15W |
| RPi 5 8GB | Entretenimento | 8GB | Cloud API (LiteLLM) | - | $80 | 6-10W |
| RPi 5 8GB | NAS (Storage) | 8GB | Cloud API (LiteLLM) | - | $355 | 6-10W |

**TOTAL**: **4 hardwares** | **$814** | **32-53W**

_Nota: IoT migrado para o Orange Pi 5 Ultra (Wi-Fi 6 como Access Point + eth0 para rede doméstica). Pagamentos e Investimentos também consolidados no Orange Pi._

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
├── ✅ mordomo - (orange-pi-5-ultra-16gb)/       # Central: Mordomo + OpenClaw + IoT - 16GB RAM
│   └── ecossistemas/
│       ├── mordomo/              # 15 containers (14 core + 1 OpenClaw)
│       ├── iot/                  # 4 containers (Wi-Fi AP + MQTT + BLE)
│       ├── infraestrutura/       # 6 containers (+ llm-gateway LiteLLM Proxy)
│       └── monitoramento/        # 4 containers
│
├── seguranca - (jetson-orin-nano)/   # Módulo de Segurança
│   └── ecossistemas/
│       └── seguranca/            # 7 containers + LLM Vision
│
├── entretenimento - (raspberry-pi-5-8gb)/ # Módulo de Entretenimento
│   └── ecossistemas/
│       └── entretenimento/       # 6 containers + LLM
│
└── nas - (raspberry-pi-5-8gb)/       # Módulo NAS (Storage)
    └── ecossistemas/
        └── nas/                  # 8 containers + LLM
```

## 🔌 Requisitos de Energia

### Fonte de Alimentação Total
- **Consumo Médio**: ~70W
- **Consumo Pico**: ~85W
- **Recomendação**: Fonte ATX 400W ou UPS 1000VA

### Por Hardware
- **Orange Pi 5**: 5V/4A (20W) - USB-C PD
- **RPi 5**: 5V/5A (27W) - USB-C PD
- **Jetson Orin**: 12V/2A (24W) - DC Barrel
- **RPi 3B+**: 5V/2.5A (12.5W) - Micro USB

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
- **Mordomo**: MicroSD 128GB (Samsung EVO Plus ~$20) + **SSD NVMe 256GB** (~$35)
- **Segurança**: MicroSD 128GB (~$20) - armazena vídeos temporariamente
- **IoT**: MicroSD 32GB (~$8)
- **Pagamentos**: MicroSD 64GB (~$12) - logs financeiros
- **Investimentos**: MicroSD 128GB (~$20) - dados históricos
- **Entretenimento**: MicroSD 128GB (~$20) + **HD Externo 2TB** (~$65)
- **NAS**: MicroSD 64GB (~$12) + **2x HDD 4TB RAID 1** (~$180) + **SSD NVMe 1TB** (~$70)

**Total Armazenamento**: ~$462

## 📦 Custo Total do Projeto

| Categoria | Custo |
|-----------|-------|
| Hardwares | $1.077 |
| Armazenamento | $462 |
| Rede (switch + cabos) | $40 |
| Fontes de Alimentação | $80 |
| Cases e Refrigeração | $60 |
| **TOTAL** | **$1.719** |

## 🚀 Roadmap de Implementação

1. **Fase 1**: ✅ Mordomo + OpenClaw + IoT (Orange Pi 5 Ultra 16GB) - Sistema central (28 containers)
2. **Fase 2**: NAS (RPi 5 8GB) - Armazenamento e backup de fotos/arquivos
3. **Fase 3**: Segurança (Jetson Orin Nano) - Câmeras e monitoramento
4. **Fase 4**: Entretenimento (RPi 5 8GB) - Media center

_Nota: Pagamentos e Investimentos consolidados no Orange Pi 5 Ultra. RPi 3B+ eliminado (IoT migrado para o hardware central)._

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
