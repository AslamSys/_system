# Hardware - Arquitetura Modular Distribuída

> 📍 **Navegação:** [🏠 Início](../README.md) > [🔧 Hardware](README.md)

Este diretório organiza todos os hardwares do sistema Mordomo, cada um dedicado a um módulo específico com LLM própria.

## 📊 Resumo da Infraestrutura

| Hardware | Módulo | RAM | LLM | NPU/GPU | Preço | Consumo |
|----------|--------|-----|-----|---------|-------|---------|-----|
| Orange Pi 5 16GB | ✅ Mordomo (Central + OpenClaw) | 16GB | Cloud (fallback 1.5B) | 6 TOPS | $130 | 10-15W |
| Jetson Orin Nano | Segurança (Vision) | 8GB | Qwen 3B Vision | 1024 CUDA | $249 | 10-15W |
| RPi 3B+ | ✅ IoT (Sem LLM) | 1GB | - | - | $83 | 2-3W |
| RPi 5 4GB | Pagamentos | 4GB | Qwen 1.5B | - | $60 | 5-7W |
| RPi 5 16GB | Investimentos | 16GB | Qwen 3B | - | $120 | 8-12W |
| RPi 5 8GB | Entretenimento | 8GB | Qwen 1.5B | - | $80 | 6-10W |
| RPi 5 8GB | NAS (Storage) | 8GB | Qwen 1.5B | - | $355 | 6-10W |

**TOTAL**: **7 hardwares** | **$1.077** | **47-75W**

## 🎯 Justificativa Técnica

### **Por que não usar Orange Pi em todos os módulos?**

1. **Preço**: Orange Pi 5 16GB ($130) vs RPi 5 8GB ($80) = **$50 de diferença**
2. **NPU não utilizada**: Módulos simples (Pagamentos, NAS) não precisam de NPU 6 TOPS
3. **Ecossistema**: Raspberry Pi tem suporte melhor, mais documentação, mais confiável
4. **Disponibilidade**: RPi tem estoque mais estável e fornecimento global

### **Quando usar Orange Pi?**

- **Mordomo + OpenClaw**: Sistema central precisa de NPU para inferência rápida + OpenClaw Agent (Comunicação + RPA integrados)

### **Quando usar Jetson?**

- **Segurança**: 1024 CUDA cores são essenciais para visão AI em tempo real (múltiplas câmeras)

## 📁 Estrutura de Diretórios

```
hardware/
├── ✅ mordomo - (orange-pi-5-16gb)/             # Mordomo (Central + OpenClaw) - 16GB RAM
│   └── ecossistemas/
│       ├── mordomo/              # 14 containers (13 core + 1 OpenClaw)
│       ├── infraestrutura/       # 5 containers
│       └── monitoramento/        # 4 containers
│
├── seguranca - (jetson-orin-nano)/   # Módulo de Segurança
│   └── ecossistemas/
│       └── seguranca/            # 7 containers + LLM Vision
│
├── ✅ iot - (raspberry-pi-3b)/          # Módulo IoT (sem LLM, ESP32 DIY)
│   └── ecossistemas/
│       └── iot/                  # 4 containers (Access Point + MQTT)
│
├── pagamentos - (raspberry-pi-5-4gb)/    # Módulo de Pagamentos
│   └── ecossistemas/
│       └── pagamentos/           # 6 containers + LLM
│
├── investimentos - (raspberry-pi-5-16gb)/ # Módulo de Investimentos
│   └── ecossistemas/
│       └── investimentos/        # 7 containers + LLM
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

1. **Fase 1**: ✅ Mordomo + OpenClaw (Orange Pi 5 16GB) - Sistema central (23 containers)
2. **Fase 2**: ✅ IoT (RPi 3B+) - ESP32 DIY + Access Point auditado (4 containers)
3. **Fase 3**: NAS (RPi 5 8GB) - Armazenamento e backup de fotos/arquivos
4. **Fase 4**: Segurança (Jetson Orin) - Câmeras e monitoramento
5. **Fase 5**: Entretenimento (RPi 5 8GB) - Media center
6. **Fase 6**: Pagamentos (RPi 5 4GB) - Integração financeira
7. **Fase 7**: Investimentos (RPi 5 16GB) - Trading bots

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
