# 💳 Pagamentos Brain

**Container:** `pagamentos-brain`  
**LLM:** Ollama Qwen 1.5B Q4_K_M  
**Hardware:** Raspberry Pi 5 4GB

---

## 📋 Propósito

LLM para interpretar solicitações financeiras, resolver contatos de pagamento, categorizar despesas e autorizar transações.

---

## 🎯 Responsabilidades

- ✅ Interpretar comandos de pagamento ("Faz um PIX pro João de R$ 150")
- ✅ Resolver destinatários (busca no banco de contatos)
- ✅ Categorizar transações (alimentação, transporte, etc)
- ✅ Autorizar ou bloquear transações suspeitas
- ✅ Gerar relatórios financeiros em linguagem natural

---

## 🔧 Tecnologias

```yaml
Core:
  - Ollama (Qwen 1.5B Q4_K_M)
  - NATS (comandos financeiros)
  - PostgreSQL (contatos + transações)
  - Redis (cache PIX keys)

Optional:
  - spaCy (NER para valores e nomes)
  - scikit-learn (categorização de despesas)
```

---

## 📊 Especificações

```yaml
VRAM: 0.9GB (Qwen 1.5B Q4)
RAM: 2.5GB (modelo + contexto)
CPU: 120% (inferência)
Latência: 400-600ms
Context: 8192 tokens
Temperature: 0.1  # Financeiro requer precisão
```

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "pagamentos.pix.request"
Payload: {
  "user_input": "Faz um PIX de R$ 150 pro João",
  "user_id": "user_123"
}

Topic: "pagamentos.transaction.categorize"
Payload: {
  "description": "UBER *TRIP SAO PAULO",
  "amount": -25.50
}
```

### Publish
```javascript
Topic: "pagamentos.pix.send"
Payload: {
  "recipient": "João Silva",
  "pix_key": "+5511999998888",
  "amount": 150.00,
  "description": "Pagamento via Mordomo"
}

Topic: "pagamentos.transaction.categorized"
Payload: {
  "category": "transporte",
  "confidence": 0.95
}
```

---

## 🧠 System Prompt

```markdown
# SISTEMA: Assistente Financeiro Mordomo

## FUNÇÃO
Você é o módulo financeiro do assistente doméstico Mordomo.
Interpreta comandos de pagamento e categoriza transações.

## CAPACIDADES
1. Resolver contatos de pagamento
   - Buscar chave PIX (telefone, email, CPF)
   - Validar destinatário
2. Extrair valores monetários
   - "R$ 150", "cento e cinquenta reais"
3. Categorizar despesas
   - Alimentação, Transporte, Moradia, Saúde, Lazer, etc.
4. Detectar intenção
   - Pagamento, Consulta saldo, Relatório

## FORMATO DE SAÍDA
Sempre responda em JSON:
{
  "intent": "pix_send | balance_check | report",
  "recipient": "Nome completo ou ID",
  "pix_key": "Chave PIX resolvida",
  "amount": 150.00,
  "category": "categoria",
  "confidence": 0.95
}

## SEGURANÇA
- Nunca envie > R$ 1000 sem confirmação
- Bloquear se destinatário desconhecido
- Alertar se transação fora do padrão
```

---

## 🚀 Docker Compose

```yaml
pagamentos-brain:
  build: ./pagamentos-brain
  environment:
    - OLLAMA_API_URL=http://localhost:11434
    - MODEL_NAME=qwen:1.5b-q4_K_M
    - NATS_URL=nats://mordomo-nats:4222
    - DATABASE_URL=postgresql://postgres:password@mordomo-postgres:5432/mordomo
    - REDIS_URL=redis://mordomo-redis:6379/3
    - TEMPERATURE=0.1
    - MAX_TOKENS=512
  volumes:
    - ollama-models:/root/.ollama
  deploy:
    resources:
      limits:
        cpus: '1.2'
        memory: 2560M
  networks:
    - pagamentos-net
    - shared-nats
```

---

## 🧪 Código de Exemplo

```python
from ollama import Client
import asyncio, nats, json, psycopg2

ollama = Client(host='http://localhost:11434')
nc = await nats.connect('nats://mordomo-nats:4222')
db = psycopg2.connect(os.getenv('DATABASE_URL'))

SYSTEM_PROMPT = open('system_prompt.md').read()

async def handle_payment_request(msg):
    data = json.loads(msg.data.decode())
    
    # Chamar LLM
    response = ollama.chat(model='qwen:1.5b-q4_K_M', messages=[
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': data['user_input']}
    ], options={'temperature': 0.1, 'num_predict': 512})
    
    parsed = json.loads(response['message']['content'])
    
    # Resolver chave PIX
    if parsed['intent'] == 'pix_send':
        cursor = db.cursor()
        cursor.execute(
            "SELECT pix_keys FROM payment_contacts WHERE name ILIKE %s",
            (f"%{parsed['recipient']}%",)
        )
        contact = cursor.fetchone()
        
        if contact:
            pix_key = contact[0].get('phone') or contact[0].get('email')
            
            # Publicar comando PIX
            await nc.publish('pagamentos.pix.send', json.dumps({
                'recipient': parsed['recipient'],
                'pix_key': pix_key,
                'amount': parsed['amount'],
                'description': 'Pagamento via Mordomo'
            }).encode())
        else:
            await nc.publish('pagamentos.error', json.dumps({
                'error': 'recipient_not_found',
                'hint': parsed['recipient']
            }).encode())

# Subscribe
await nc.subscribe('pagamentos.pix.request', cb=handle_payment_request)
```

---

## 📊 Monitoramento

```yaml
Prometheus Metrics:
  - payment_llm_latency_ms (p50, p95, p99)
  - payment_llm_requests_total
  - payment_contacts_resolved_total
  - payment_transactions_categorized_total
```

---

## 🔒 Segurança

```yaml
1. Valores > R$ 1000: Requer confirmação 2FA
2. Destinatário novo: Alertar usuário
3. API Keys criptografadas: AES-256 + KMS
4. Logs auditáveis: Todas transações armazenadas 5 anos (Bacen)
```

---

## 🐛 Troubleshooting

```yaml
"LLM não extrai valor corretamente":
  - Verificar temperature (deve ser 0.1, não 0.7)
  - Adicionar exemplos no prompt

"Contato não encontrado":
  - Popular payment_contacts com chaves PIX
  - Verificar ILIKE case-insensitive

"Latência > 1s":
  - Verificar VRAM (deve ser < 1GB)
  - Reduzir max_tokens para 256
```

---

## 📚 Referências

- [Qwen Models](https://github.com/QwenLM/Qwen)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [PIX API Bacen](https://www.bcb.gov.br/estabilidadefinanceira/pix)

---

## 🔄 Changelog

### v1.0.0
- ✅ Ollama Qwen 1.5B Q4_K_M
- ✅ Resolução de contatos PIX
- ✅ Categorização de despesas
- ✅ System prompt financeiro
