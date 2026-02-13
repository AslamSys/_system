# 📈 Trading Bot

**Container:** `trading-bot`  
**Stack:** Python + ccxt (Binance/Bybit)  
**Estratégias:** Mean Reversion, Momentum, Grid Trading

---

## 📋 Propósito

Bot de trading automatizado para ações (B3), criptomoedas (Binance) e forex (Bybit). Suporte a múltiplas estratégias.

---

## 🎯 Features

- ✅ Exchanges: Binance, Bybit, B3 (via MetaTrader5)
- ✅ Estratégias: Mean Reversion, Momentum, Grid
- ✅ Stop Loss / Take Profit automáticos
- ✅ Backtesting histórico
- ✅ Paper trading (simulação)

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "investimentos.trade.execute"
Payload: {
  "action": "buy|sell",
  "ticker": "BTCUSDT",
  "quantity": 0.01,
  "order_type": "market|limit",
  "limit_price": 95000.00,
  "stop_loss": 90000.00,
  "take_profit": 100000.00
}
```

### Publish
```javascript
Topic: "investimentos.trade.executed"
Payload: {
  "order_id": "BTC_ORDER_123",
  "status": "filled",
  "filled_price": 95500.00,
  "fee": 0.00001
}

Topic: "investimentos.alert.stop_loss"
Payload: {
  "ticker": "BTCUSDT",
  "trigger_price": 90000.00,
  "loss": -500.00
}
```

---

## 🚀 Docker Compose

```yaml
trading-bot:
  build: ./trading-bot
  environment:
    - BINANCE_API_KEY=${BINANCE_API_KEY}
    - BINANCE_SECRET=${BINANCE_SECRET}
    - BYBIT_API_KEY=${BYBIT_API_KEY}
    - MODE=live  # live | paper
    - STRATEGY=mean_reversion
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 2048M
```

---

## 🧪 Código (Mean Reversion)

```python
import ccxt, numpy as np
from talib import BBANDS, RSI

exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_SECRET')
})

async def mean_reversion_strategy(ticker):
    # Fetch OHLCV (1h candles, 100 periods)
    ohlcv = exchange.fetch_ohlcv(ticker, '1h', limit=100)
    closes = np.array([x[4] for x in ohlcv])
    
    # Bollinger Bands
    upper, middle, lower = BBANDS(closes, timeperiod=20)
    
    # RSI
    rsi = RSI(closes, timeperiod=14)
    
    current_price = closes[-1]
    
    # BUY signal: price < lower band + RSI < 30 (oversold)
    if current_price < lower[-1] and rsi[-1] < 30:
        order = exchange.create_market_buy_order(ticker, 0.01)
        
        # Set stop loss and take profit
        await nc.publish('investimentos.trade.executed', json.dumps({
            'order_id': order['id'],
            'action': 'buy',
            'price': order['price'],
            'stop_loss': current_price * 0.95,
            'take_profit': middle[-1]
        }).encode())
    
    # SELL signal: price > upper band + RSI > 70 (overbought)
    elif current_price > upper[-1] and rsi[-1] > 70:
        order = exchange.create_market_sell_order(ticker, 0.01)
        await nc.publish('investimentos.trade.executed', json.dumps({
            'order_id': order['id'],
            'action': 'sell',
            'price': order['price']
        }).encode())

# Run every 5 minutes
while True:
    await mean_reversion_strategy('BTC/USDT')
    await asyncio.sleep(300)
```

---

## 📊 Supported Strategies

```yaml
1. Mean Reversion:
   - Bollinger Bands + RSI
   - Buy oversold, sell overbought

2. Momentum:
   - MACD + ADX
   - Ride strong trends

3. Grid Trading:
   - Buy/sell at fixed price intervals
   - Profit from volatility
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Binance/Bybit integration
- ✅ Mean Reversion strategy
- ✅ Stop loss/take profit
