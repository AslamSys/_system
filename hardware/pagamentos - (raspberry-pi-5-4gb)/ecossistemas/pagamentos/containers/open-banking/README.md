# 🏦 Open Banking API

**Container:** `open-banking`  
**Stack:** Pluggy / Belvo  
**Propósito:** Agregação bancária multi-contas

---

## 📋 Propósito

Integração com Open Banking (Pluggy/Belvo) para sincronizar transações de múltiplas contas bancárias. Atualização automática de saldo e extratos.

---

## 🎯 Features

- ✅ Conexão com 200+ bancos brasileiros
- ✅ Sincronização automática de transações
- ✅ Consulta de saldo em tempo real
- ✅ Categorização automática de despesas
- ✅ Armazenamento seguro de credenciais

---

## 🔌 NATS Topics

### Publish
```javascript
Topic: "pagamentos.transaction.new"
Payload: {
  "account_id": "nubank_123",
  "amount": -35.50,
  "description": "UBER *TRIP",
  "date": "2025-11-27",
  "category": "transporte"
}

Topic: "pagamentos.balance.updated"
Payload: {
  "account_id": "nubank_123",
  "balance": 1250.75
}
```

---

## 🚀 Docker Compose

```yaml
open-banking:
  build: ./open-banking
  environment:
    - PLUGGY_CLIENT_ID=${PLUGGY_CLIENT_ID}
    - PLUGGY_CLIENT_SECRET=${PLUGGY_CLIENT_SECRET}
    - DATABASE_URL=postgresql://postgres:password@mordomo-postgres:5432/mordomo
    - SYNC_INTERVAL_MINUTES=60
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
```

---

## 🧪 Código

```javascript
const { PluggyClient } = require('pluggy-sdk');
const cron = require('node-cron');

const pluggy = new PluggyClient({
    clientId: process.env.PLUGGY_CLIENT_ID,
    clientSecret: process.env.PLUGGY_CLIENT_SECRET
});

// Sync every hour
cron.schedule('0 * * * *', async () => {
    const items = await pluggy.fetchItems(); // Connected accounts
    
    for (const item of items) {
        const accounts = await pluggy.fetchAccounts(item.id);
        
        for (const account of accounts) {
            // Update balance
            await nc.publish('pagamentos.balance.updated', sc.encode(JSON.stringify({
                account_id: account.id,
                balance: account.balance
            })));
            
            // Fetch new transactions
            const transactions = await pluggy.fetchTransactions(account.id);
            
            for (const tx of transactions.filter(t => !t.synced)) {
                await nc.publish('pagamentos.transaction.new', sc.encode(JSON.stringify({
                    account_id: account.id,
                    amount: tx.amount,
                    description: tx.description,
                    date: tx.date,
                    category: categorize(tx.description)
                })));
            }
        }
    }
});
```

---

## 🏦 Bancos Suportados

```yaml
Principais:
  - Nubank, Inter, C6, PicPay
  - Banco do Brasil, Itaú, Bradesco
  - Santander, Caixa

Total: 200+ instituições brasileiras
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Pluggy SDK integration
- ✅ Hourly sync
- ✅ Multi-account support
