# 🔍 Technical Analysis

**Container:** `technical-analysis`  
**Stack:** Python + TA-Lib + pandas  
**Propósito:** Cálculo de indicadores técnicos

---

## 📋 Propósito

Calcular indicadores técnicos (RSI, MACD, Bollinger Bands, etc) para suporte a decisões de trading.

---

## 🎯 Indicators

- ✅ RSI, MACD, Stochastic
- ✅ Bollinger Bands, ATR
- ✅ Moving Averages (SMA, EMA)
- ✅ Fibonacci retracements
- ✅ Support/Resistance levels

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "investimentos.analyze.ticker"
Payload: {
  "ticker": "BTCUSDT",
  "timeframe": "1h",
  "indicators": ["rsi", "macd", "bb"]
}
```

### Publish
```javascript
Topic: "investimentos.analysis.complete"
Payload: {
  "ticker": "BTCUSDT",
  "rsi": 45.2,
  "macd": {"macd": 120, "signal": 115, "histogram": 5},
  "bb": {"upper": 96000, "middle": 95000, "lower": 94000},
  "trend": "bullish"
}
```

---

## 🚀 Docker Compose

```yaml
technical-analysis:
  build: ./technical-analysis
  environment:
    - NATS_URL=nats://mordomo-nats:4222
    - REDIS_URL=redis://mordomo-redis:6379/4
  deploy:
    resources:
      limits:
        cpus: '1.2'
        memory: 3072M
```

---

## 🧪 Código

```python
import talib, ccxt, numpy as np

exchange = ccxt.binance()

async def calculate_indicators(ticker, timeframe='1h'):
    ohlcv = exchange.fetch_ohlcv(ticker, timeframe, limit=100)
    closes = np.array([x[4] for x in ohlcv])
    highs = np.array([x[2] for x in ohlcv])
    lows = np.array([x[3] for x in ohlcv])
    
    # RSI
    rsi = talib.RSI(closes, timeperiod=14)[-1]
    
    # MACD
    macd, signal, hist = talib.MACD(closes)
    
    # Bollinger Bands
    upper, middle, lower = talib.BBANDS(closes, timeperiod=20)
    
    # Trend detection
    sma_50 = talib.SMA(closes, timeperiod=50)[-1]
    sma_200 = talib.SMA(closes, timeperiod=200)[-1]
    trend = 'bullish' if sma_50 > sma_200 else 'bearish'
    
    return {
        'rsi': round(rsi, 2),
        'macd': {'macd': round(macd[-1], 2), 'signal': round(signal[-1], 2)},
        'bb': {'upper': round(upper[-1], 2), 'middle': round(middle[-1], 2)},
        'trend': trend
    }
```

---

## 🔄 Changelog

### v1.0.0
- ✅ TA-Lib integration
- ✅ 10+ indicators
- ✅ Trend detection
