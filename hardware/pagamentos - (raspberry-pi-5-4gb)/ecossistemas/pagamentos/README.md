# 💳 Ecossistema Pagamentos

> 🗂️ **Navegação:** [🏠 Início](../../../../README.md) > [🔧 Hardware](../../../README.md) > [💳 Pagamentos](../../README.md) > [🌐 Ecossistema Pagamentos](README.md)

Sistema completo de processamento financeiro com PIX, Open Banking, detecção de fraudes e integração com carteiras digitais.

---

## 📋 Visão Geral

O ecossistema de **Pagamentos** fornece capacidades financeiras completas:

- 💸 **PIX** - Pagamentos e recebimentos instantâneos
- 🏦 **Open Banking** - Integração bancária via APIs
- 🔍 **Detecção de Fraudes** - ML para análise de transações
- 📄 **Geração de Documentos** - Boletos, NFe, NFSe
- 💰 **Carteiras Digitais** - PicPay, Mercado Pago, PayPal

---

## 🏗️ Arquitetura de Containers (6 containers)

```
┌────────────────────────────────────────────────┐
│         ECOSSISTEMA PAGAMENTOS                 │
├────────────────────────────────────────────────┤
│                                                │
│  ┌─────────────────┐    ┌─────────────────┐   │
│  │ pagamentos-brain│    │   pix-gateway   │   │
│  │  (Qwen 1.5B)    │    │  (API Bacen)    │   │
│  └─────────────────┘    └─────────────────┘   │
│                                                │
│  ┌─────────────────┐    ┌─────────────────┐   │
│  │  open-banking   │    │ fraud-detector  │   │
│  │(Pluggy/Belvo)   │    │ (ML Detection)  │   │
│  └─────────────────┘    └─────────────────┘   │
│                                                │
│  ┌─────────────────┐    ┌─────────────────┐   │
│  │invoice-generator│    │wallet-integrator│   │
│  │ (Boletos/NFe)   │    │(PicPay, MP, etc)│   │
│  └─────────────────┘    └─────────────────┘   │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 📦 Lista de Containers

### 1. **pagamentos-brain**
- **Função:** LLM para processamento de solicitações financeiras
- **Modelo:** Qwen 1.5B Q4_K_M (0.9GB VRAM)
- **RAM:** 2.5GB
- **CPU:** 120%

### 2. **pix-gateway**
- **Função:** API PIX com integração Banco Central
- **Integrações:** Bacen, PSPs (Mercado Pago, PagBank)
- **RAM:** 384MB
- **CPU:** 40%

### 3. **open-banking**
- **Função:** Conexão bancária via Open Banking
- **Integrações:** Pluggy, Belvo, APIs bancárias
- **RAM:** 512MB
- **CPU:** 50%

### 4. **fraud-detector**
- **Função:** Detecção de fraudes com ML
- **Algoritmo:** Isolation Forest, Anomaly Detection
- **RAM:** 256MB
- **CPU:** 60%

### 5. **invoice-generator**
- **Função:** Geração de documentos fiscais
- **Recursos:** Boletos, NFe, NFSe, recibos
- **RAM:** 192MB
- **CPU:** 30%

### 6. **wallet-integrator**
- **Função:** Integração com carteiras digitais
- **Suporte:** PicPay, Mercado Pago, PayPal, Nubank
- **RAM:** 256MB
- **CPU:** 35%

---

## 🔌 Integração NATS

### Comandos Recebidos
```bash
pagamentos.pix.send          # Enviar PIX
pagamentos.pix.receive       # Consultar recebimentos  
pagamentos.invoice.generate  # Gerar boleto/NFe
pagamentos.balance.check     # Consultar saldo
pagamentos.transaction.list  # Listar transações
pagamentos.fraud.analyze     # Analisar transação
```

### Eventos Publicados
```bash
pagamentos.transaction.completed    # Transação concluída
pagamentos.fraud.detected          # Fraude detectada
pagamentos.invoice.generated       # Documento gerado
pagamentos.balance.updated          # Saldo atualizado
```

---

## 📊 Recursos do Hardware

| Container | RAM | CPU | Função Principal |
|-----------|-----|-----|------------------|
| **pagamentos-brain** | 2.5GB | 120% | LLM financeiro |
| **pix-gateway** | 384MB | 40% | API PIX |
| **open-banking** | 512MB | 50% | Integração bancária |
| **fraud-detector** | 256MB | 60% | ML antifraude |
| **invoice-generator** | 192MB | 30% | Documentos fiscais |
| **wallet-integrator** | 256MB | 35% | Carteiras digitais |
| **TOTAL** | **4.1GB** | **335%** | RPi 5 4GB (swap 1GB) |

---

## 🌐 Links Relacionados

- **Hardware:** [Raspberry Pi 5 4GB - Pagamentos](../../README.md)
- **Containers:** [Lista Detalhada](containers/)
- **Infraestrutura:** [NATS, PostgreSQL](../../mordomo%20-%20(orange-pi-5-16gb)/ecossistemas/infraestrutura/README.md)
- **Monitoramento:** [Métricas e Logs](../../mordomo%20-%20(orange-pi-5-16gb)/ecossistemas/monitoramento/README.md)

---

## 📝 Status de Implementação

- [x] Documentação completa
- [x] Especificação de containers
- [ ] Implementação do pagamentos-brain
- [ ] Integração PIX (Bacen)
- [ ] APIs Open Banking
- [ ] ML fraud detection
- [ ] Testes de integração
- [ ] Deploy em produção

---

**Hardware:** Raspberry Pi 5 4GB  
**Ecossistema:** Pagamentos  
**Última atualização:** 13/02/2026