# 🤖 ML Price Predictor

**Container:** `ml-predictor`  
**Stack:** Python + LSTM + LightGBM  
**Propósito:** Predição de preços com Machine Learning

---

## 📋 Propósito

Modelo LSTM para predição de preços de ações/cripto. Treina offline, prediz diariamente.

---

## 🎯 Features

- ✅ LSTM (TensorFlow/Keras)
- ✅ LightGBM (tree-based ensemble)
- ✅ Features: preço, volume, indicators, sentiment
- ✅ Backtesting com walk-forward validation

---

## 🔌 NATS Topics

### Publish
```javascript
Topic: "investimentos.prediction.new"
Payload: {
  "ticker": "BTCUSDT",
  "predicted_price_24h": 97500.00,
  "confidence": 0.78,
  "direction": "up|down",
  "features_importance": {
    "rsi": 0.25,
    "news_sentiment": 0.20,
    "volume": 0.15
  }
}
```

---

## 🚀 Docker Compose

```yaml
ml-predictor:
  build: ./ml-predictor
  environment:
    - MODEL_PATH=/models/lstm_btc.h5
    - RETRAIN_DAYS=30  # Retrain every 30 days
  volumes:
    - ./models:/models
  deploy:
    resources:
      limits:
        cpus: '1.5'
        memory: 3072M
```

---

## 🧪 Código (LSTM)

```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import numpy as np

# Prepare data
def create_sequences(data, seq_length=60):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])  # Predict next price
    return np.array(X), np.array(y)

# Build LSTM model
model = Sequential([
    LSTM(128, return_sequences=True, input_shape=(60, 8)),  # 8 features
    Dropout(0.2),
    LSTM(64, return_sequences=False),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(1)  # Price prediction
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Train
X_train, y_train = create_sequences(scaled_data)
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

# Predict
last_60_days = scaled_data[-60:]
prediction = model.predict(last_60_days.reshape(1, 60, 8))
predicted_price = scaler.inverse_transform(prediction)[0][0]
```

---

## 🔄 Changelog

### v1.0.0
- ✅ LSTM model
- ✅ 8-feature input
- ✅ Daily predictions
