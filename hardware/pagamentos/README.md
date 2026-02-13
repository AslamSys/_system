# Raspberry Pi 5 4GB - Módulo de Pagamentos

> 📍 **Navegação:** [🏠 Início](../../README.md) > [🔧 Hardware](../README.md) > [💳 Pagamentos (RPi 5 4GB)](README.md)

## 📋 Especificações do Hardware

### Raspberry Pi 5 4GB
- **SoC**: Broadcom BCM2712 (Cortex-A76 quad-core 2.4GHz)
- **RAM**: 4GB LPDDR4X-4267
- **Armazenamento**: MicroSD 64GB
- **Rede**: Gigabit Ethernet + Wi-Fi 5 + Bluetooth 5.0
- **Alimentação**: 5V/5A USB-C (27W)
- **Preço**: **$60** + periféricos $15 = **$75 TOTAL**

## 🎯 Função no Sistema

Módulo responsável por:
- PIX (pagamentos e recebimentos)
- Integração bancária (OFX, Open Banking)
- Conciliação automática de transações
- Detecção de fraudes (ML)
- Emissão de boletos/notas fiscais
- Carteiras digitais (PicPay, Mercado Pago)

## 🧠 LLM - Qwen 1.5B Q4_K_M

- **Modelo**: 1.5B parâmetros, 0.9GB VRAM
- **Função**: Interpretar solicitações financeiras, categorizar despesas, gerar relatórios
- **Recursos**: 2.5GB RAM necessária / 4GB disponível = **62% uso** ✅

## 📦 Containers e Repositórios

Este hardware executa **6 containers** especializados em pagamentos:

### 💳 Ecossistema Pagamentos (6 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **pagamentos-brain** | LLM financeiro (Qwen 1.5B) | ⏳ | [AslamSys/pagamentos-brain](https://github.com/AslamSys/pagamentos-brain) |
| **pix-gateway** | API PIX com Banco Central | ⏳ | [AslamSys/pix-gateway](https://github.com/AslamSys/pix-gateway) |
| **open-banking** | Integração bancária (Pluggy/Belvo) | ⏳ | [AslamSys/open-banking](https://github.com/AslamSys/open-banking) |
| **fraud-detector** | Detecção ML de fraudes | ⏳ | [AslamSys/fraud-detector](https://github.com/AslamSys/fraud-detector) |
| **invoice-generator** | Boletos/NFe/NFSe | ⏳ | [AslamSys/invoice-generator](https://github.com/AslamSys/invoice-generator) |
| **wallet-integrator** | PicPay, Mercado Pago, PayPal | ⏳ | [AslamSys/wallet-integrator](https://github.com/AslamSys/wallet-integrator) |

**💡 Status:**
- ✅ **Implementado** - Container funcionando
- ⏳ **Em desenvolvimento** - Em progresso
- 📋 **Especificado** - Documentado, aguardando implementação

**📊 Recursos do Hardware:**
- **RAM Total**: 4.1GB / 4GB = **103% uso** ⚠️ (swap 1GB resolve)
- **CPU Total**: 335% / 400% = **84% uso** ✅
- **LLM**: Qwen 1.5B Q4_K_M (2.5GB RAM, 120% CPU)

---

## 🔌 Integração NATS

### Comandos Recebidos
```
pagamentos.pix.send          # Enviar PIX
pagamentos.pix.receive       # Consultar recebimentos
pagamentos.invoice.generate  # Gerar boleto/NFe
pagamentos.balance.check     # Consultar saldo
pagamentos.transaction.list  # Listar transações
```

### Eventos Publicados
```
pagamentos.pix.sent          # PIX enviado
pagamentos.pix.received      # PIX recebido
pagamentos.fraud.detected    # Transação suspeita
pagamentos.balance.low       # Saldo baixo
```

## 💳 Integrações PIX

### PSPs Suportados
- **Banco do Brasil** (API Pix BB)
- **Inter** (API Pix Inter)
- **Sicoob** (API Pix)
- **Asaas** (Gateway pagamento)
- **Mercado Pago** (Pix via SDK)

### Fluxo PIX
```
Usuário: "Faz um PIX de R$ 150 pro João"
    ↓
Mordomo Brain: Identifica valor (R$ 150) + destinatário ("João")
    ↓
NATS → pagamentos.pix.send
    {
      "recipient": "João Silva",
      "amount": 150.00,
      "key_hint": "telefone ou email"
    }
    ↓
pagamentos-brain: Busca chave PIX do João no banco de contatos
    → Encontra: +5511999998888
    ↓
pix-gateway: Chama API do Banco (POST /pix/payment)
    {
      "key": "+5511999998888",
      "value": 150.00,
      "description": "Pagamento via Mordomo"
    }
    ↓
Banco processa (< 10s)
    ↓
NATS → pagamentos.pix.sent
    {
      "status": "success",
      "txid": "E123456789202511271530",
      "recipient": "João Silva",
      "amount": 150.00
    }
    ↓
Mordomo: "PIX de R$ 150 enviado para João Silva. ID: E123..."
```

## 🗄️ Banco de Dados (PostgreSQL no Mordomo)

### Tabela: `payment_accounts`
```sql
CREATE TABLE payment_accounts (
  id UUID PRIMARY KEY,
  bank_name VARCHAR(100),
  account_type VARCHAR(20), -- checking, savings, pix
  psp VARCHAR(50), -- bb, inter, asaas
  api_key_encrypted TEXT,
  balance DECIMAL(15,2),
  last_sync TIMESTAMP,
  active BOOLEAN DEFAULT TRUE
);
```

### Tabela: `payment_transactions`
```sql
CREATE TABLE payment_transactions (
  id UUID PRIMARY KEY,
  account_id UUID REFERENCES payment_accounts(id),
  type VARCHAR(20), -- pix_in, pix_out, boleto, ted
  amount DECIMAL(15,2),
  counterparty VARCHAR(255),
  description TEXT,
  txid VARCHAR(100) UNIQUE,
  status VARCHAR(20), -- pending, completed, failed
  fraud_score DECIMAL(3,2), -- 0.00 a 1.00
  category VARCHAR(50), -- alimentação, transporte, etc
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `payment_contacts`
```sql
CREATE TABLE payment_contacts (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  pix_keys JSONB, -- {"phone": "+55...", "email": "..."}
  bank_details JSONB,
  last_transaction TIMESTAMP
);
```

## 🔒 Segurança Financeira

### Autenticação Bancária
- **API Keys criptografadas** (AES-256 + KMS)
- **Certificados digitais** (A1/A3 para NFe)
- **2FA/MFA** para aprovação de pagamentos > R$ 500

### Detecção de Fraudes (ML)
```python
# Isolation Forest para detectar anomalias
features = [
  'amount',              # Valor atípico?
  'hour_of_day',         # Horário incomum?
  'day_of_week',         # Final de semana?
  'frequency_last_24h',  # Muitas transações?
  'new_recipient'        # Destinatário novo?
]

if fraud_score > 0.7:
  # Bloquear transação + notificar
  NATS.publish('pagamentos.fraud.detected')
```

### Compliance
- **LGPD**: Dados bancários criptografados, acesso auditado
- **PCI-DSS**: Não armazenar CVV, tokens em vez de cartões
- **Bacen**: Logs de todas transações PIX (5 anos)

## 💡 Casos de Uso

1. **Pagamento por Voz**: "Paga a conta de luz" → Busca boleto no email → Paga PIX
2. **Conciliação Automática**: Recebe PIX → Identifica pagador → Atualiza planilha
3. **Alerta Saldo Baixo**: Saldo < R$ 500 → Notifica + sugere transferência de investimentos
4. **Categorização Inteligente**: Transação "Uber" → Categoria "Transporte"
5. **Split de Pagamento**: "Divide a conta do restaurante com 3 amigos" → 3 PIX automáticos
