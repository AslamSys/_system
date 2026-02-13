# Raspberry Pi 5 4GB - Módulo de Pagamentos

## 📋 Especificações do Hardware

### Raspberry Pi 5 4GB
- **SoC**: Broadcom BCM2712 (Cortex-A76 quad-core 2.4GHz)
- **RAM**: 4GB LPDDR4X-4267
- **Armazenamento**: MicroSD 64GB
- **Rede**: Gigabit Ethernet + Wi-Fi 5 + Bluetooth 5.0
- **Alimentação**: 5V/5A USB-C (27W)

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

## 📦 Containers (6 total)

1. **pagamentos-brain** (Ollama Qwen 1.5B) - 2.5GB RAM, 120% CPU
2. **pix-gateway** (API Bacen + PSPs) - 384MB RAM, 40% CPU  
3. **open-banking** (Pluggy/Belvo integração) - 512MB RAM, 50% CPU
4. **fraud-detector** (Isolation Forest ML) - 256MB RAM, 60% CPU
5. **invoice-generator** (Boletos/NFe/NFSe) - 192MB RAM, 30% CPU
6. **wallet-integrator** (PicPay, MP, PayPal) - 256MB RAM, 35% CPU

**Total**: 4.1GB RAM / 4GB = **103% uso** ⚠️ (swap 1GB resolve)  
**CPU**: 335% / 400% = **84% uso** ✅

### Repositórios
- [pagamentos-brain](https://github.com/AslamSys/pagamentos-brain)
- [pagamentos-pix-gateway](https://github.com/AslamSys/pagamentos-pix-gateway)
- [pagamentos-open-banking](https://github.com/AslamSys/pagamentos-open-banking)
- [pagamentos-fraud-detector](https://github.com/AslamSys/pagamentos-fraud-detector)
- [pagamentos-invoice-generator](https://github.com/AslamSys/pagamentos-invoice-generator)
- [pagamentos-wallet-integrator](https://github.com/AslamSys/pagamentos-wallet-integrator)

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
