# 📊 Investimentos Brain

**Container:** `investimentos-brain`  
**LLM:** Ollama Qwen 3B Q4_K_M  
**Hardware:** Raspberry Pi 5 16GB

---

## 📋 Propósito

LLM para análise de notícias financeiras, sentiment analysis, recomendações de trades e interpretação de comandos de investimento.

---

## 🎯 Responsabilidades

- ✅ Analisar notícias e sentimento de mercado
- ✅ Recomendar trades baseado em análise técnica + sentiment
- ✅ Interpretar comandos ("Compra 100 ações da Petrobras")
- ✅ Gerar relatórios de portfolio
- ✅ Alertar sobre eventos relevantes

---

## 🔧 Tecnologias

```yaml
Core:
  - Ollama (Qwen 3B Q4_K_M)
  - NATS (comandos de trading)
  - PostgreSQL (histórico de trades)
  - Redis (cache de análises)

Optional:
  - FinBERT (sentiment analysis)
  - NewsAPI (notícias financeiras)
  - yfinance (dados de mercado)
```

---

## 📊 Especificações

```yaml
VRAM: 1.8GB (Qwen 3B Q4)
RAM: 3GB (modelo + contexto)
CPU: 150% (inferência)
Latência: 600-900ms
Context: 16384 tokens
Temperature: 0.2  # Análise financeira conservadora
```

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "investimentos.analyze.news"
Payload: {
  "ticker": "PETR4",
  "news_text": "Petrobras anuncia dividendos recordes...",
  "source": "InfoMoney"
}

Topic: "investimentos.trade.request"
Payload: {
  "user_input": "Compra 100 ações da Vale",
  "user_id": "user_123"
}
```

### Publish
```javascript
Topic: "investimentos.sentiment.analyzed"
Payload: {
  "ticker": "PETR4",
  "sentiment": "positive",  // positive, neutral, negative
  "score": 0.85,
  "summary": "Notícias indicam forte valorização no curto prazo"
}

Topic: "investimentos.trade.execute"
Payload: {
  "action": "buy",
  "ticker": "VALE3",
  "quantity": 100,
  "order_type": "market"
}
```

---

## 🧠 System Prompt

```markdown
# SISTEMA: Analista Financeiro Mordomo

## FUNÇÃO
Você é o módulo de investimentos do assistente Mordomo.
Analisa notícias, recomenda trades e interpreta comandos.

## CAPACIDADES
1. Sentiment Analysis
   - Positivo (+1.0), Neutro (0.0), Negativo (-1.0)
   - Resumo de notícias financeiras
2. Recomendação de Trades
   - Baseado em análise técnica + sentiment
   - Considerar risk/reward ratio
3. Interpretação de Comandos
   - "Compra X ações de Y"
   - "Vende tudo de Z"
   - "Quanto tenho investido em cripto?"

## FORMATO DE SAÍDA
{
  "intent": "buy | sell | analyze | report",
  "ticker": "PETR4",
  "quantity": 100,
  "order_type": "market | limit",
  "sentiment": "positive | neutral | negative",
  "score": 0.85,
  "reasoning": "Explicação da decisão"
}

## REGRAS DE SEGURANÇA
- Nunca recomendar all-in em um ativo
- Stop loss obrigatório em trades
- Alertar sobre alta volatilidade
- Máximo 10% do portfolio por trade
```

---

## 🚀 Docker Compose

```yaml
investimentos-brain:
  build: ./investimentos-brain
  environment:
    - OLLAMA_API_URL=http://localhost:11434
    - MODEL_NAME=qwen:3b-q4_K_M
    - NATS_URL=nats://mordomo-nats:4222
    - DATABASE_URL=postgresql://postgres:password@mordomo-postgres:5432/mordomo
    - REDIS_URL=redis://mordomo-redis:6379/4
    - TEMPERATURE=0.2
    - MAX_TOKENS=1024
    - NEWS_API_KEY=${NEWS_API_KEY}
  volumes:
    - ollama-models:/root/.ollama
  deploy:
    resources:
      limits:
        cpus: '1.5'
        memory: 3072M
  networks:
    - investimentos-net
    - shared-nats
```

---

## 🧪 Código de Exemplo

```python
from ollama import Client
import asyncio, nats, json, yfinance as yf

ollama = Client(host='http://localhost:11434')
nc = await nats.connect('nats://mordomo-nats:4222')

SYSTEM_PROMPT = open('system_prompt.md').read()

async def analyze_news(msg):
    data = json.loads(msg.data.decode())
    
    # Get market data context
    ticker = yf.Ticker(data['ticker'])
    info = ticker.info
    
    # LLM sentiment analysis
    response = ollama.chat(model='qwen:3b-q4_K_M', messages=[
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': f"""
Analise o sentimento desta notícia sobre {data['ticker']}:

Notícia: {data['news_text']}

Contexto de mercado:
- Preço atual: R$ {info.get('currentPrice', 'N/A')}
- P/L: {info.get('trailingPE', 'N/A')}
- Dividend Yield: {info.get('dividendYield', 0) * 100:.2f}%

Retorne JSON com sentiment (positive/neutral/negative), score (0-1) e summary.
        """}
    ], options={'temperature': 0.2, 'num_predict': 1024})
    
    result = json.loads(response['message']['content'])
    
    # Publish analysis
    await nc.publish('investimentos.sentiment.analyzed', json.dumps({
        'ticker': data['ticker'],
        'sentiment': result['sentiment'],
        'score': result['score'],
        'summary': result['summary']
    }).encode())

await nc.subscribe('investimentos.analyze.news', cb=analyze_news)
```

---

## 📊 Monitoramento

```yaml
Prometheus Metrics:
  - investment_llm_latency_ms (p50, p95, p99)
  - investment_sentiment_analyzed_total
  - investment_trade_recommendations_total
  - investment_news_processed_total
```

---

## 🔒 Segurança

```yaml
1. API Keys criptografadas (brokers)
2. Limite de ordem: R$ 10.000 por trade sem confirmação
3. Stop loss obrigatório (5-10%)
4. Máximo 30% do portfolio em risco simultâneo
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Ollama Qwen 3B Q4_K_M
- ✅ Sentiment analysis com FinBERT fallback
- ✅ Trade command interpretation
- ✅ yfinance integration
