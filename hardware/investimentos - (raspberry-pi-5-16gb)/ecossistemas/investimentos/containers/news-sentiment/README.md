# 📰 News Sentiment Analyzer

**Container:** `news-sentiment`  
**Stack:** FinBERT + NewsAPI  
**Propósito:** Análise de sentimento de notícias financeiras

---

## 📋 Propósito

Coletar notícias financeiras (NewsAPI, Google News) e analisar sentimento com FinBERT. Alimenta o investimentos-brain.

---

## 🎯 Features

- ✅ NewsAPI, Google News, Yahoo Finance
- ✅ FinBERT sentiment (positive/neutral/negative)
- ✅ Scraping de sites financeiros (InfoMoney, Valor)
- ✅ Alertas de notícias relevantes

---

## 🔌 NATS Topics

### Publish
```javascript
Topic: "investimentos.news.new"
Payload: {
  "ticker": "PETR4",
  "title": "Petrobras anuncia dividendos recordes",
  "sentiment": "positive",
  "score": 0.92,
  "url": "https://...",
  "published_at": "2025-11-27T10:30:00Z"
}
```

---

## 🚀 Docker Compose

```yaml
news-sentiment:
  build: ./news-sentiment
  environment:
    - NEWS_API_KEY=${NEWS_API_KEY}
    - NATS_URL=nats://mordomo-nats:4222
    - MODEL_PATH=/models/finbert
  volumes:
    - ./models:/models
  deploy:
    resources:
      limits:
        cpus: '0.8'
        memory: 2560M
```

---

## 🧪 Código

```python
from transformers import BertTokenizer, BertForSequenceClassification
from newsapi import NewsApiClient
import torch

# Load FinBERT
tokenizer = BertTokenizer.from_pretrained('ProsusAI/finbert')
model = BertForSequenceClassification.from_pretrained('ProsusAI/finbert')

newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

async def analyze_news(ticker):
    # Fetch news
    articles = newsapi.get_everything(q=ticker, language='pt', sort_by='publishedAt')
    
    for article in articles['articles'][:10]:
        # Sentiment analysis
        inputs = tokenizer(article['title'] + ' ' + article['description'], 
                          return_tensors='pt', truncation=True, max_length=512)
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        
        sentiment_map = {0: 'positive', 1: 'neutral', 2: 'negative'}
        sentiment = sentiment_map[probs.argmax().item()]
        score = probs.max().item()
        
        # Publish
        await nc.publish('investimentos.news.new', json.dumps({
            'ticker': ticker,
            'title': article['title'],
            'sentiment': sentiment,
            'score': score,
            'url': article['url'],
            'published_at': article['publishedAt']
        }).encode())
```

---

## 🔄 Changelog

### v1.0.0
- ✅ FinBERT sentiment
- ✅ NewsAPI integration
- ✅ Portuguese support
