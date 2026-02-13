# 🚨 Fraud Detector

**Container:** `fraud-detector`  
**Stack:** Python + Isolation Forest (scikit-learn)  
**Propósito:** Detecção de transações suspeitas

---

## 📋 Propósito

ML model para detectar anomalias em transações financeiras. Bloqueia pagamentos suspeitos e notifica usuário.

---

## 🎯 Features

- ✅ Isolation Forest (unsupervised anomaly detection)
- ✅ Features: valor, hora, destinatário novo, frequência
- ✅ Score 0.0-1.0 (> 0.7 = suspeito)
- ✅ Bloqueio automático + notificação

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "pagamentos.pix.send"
Payload: {
  "pix_key": "+5511999998888",
  "amount": 5000.00,
  "timestamp": 1732723200
}
```

### Publish
```javascript
Topic: "pagamentos.fraud.detected"
Payload: {
  "pix_key": "+5511999998888",
  "amount": 5000.00,
  "fraud_score": 0.85,
  "reasons": ["high_amount", "new_recipient", "unusual_hour"]
}
```

---

## 🚀 Docker Compose

```yaml
fraud-detector:
  build: ./fraud-detector
  environment:
    - NATS_URL=nats://mordomo-nats:4222
    - MODEL_PATH=/models/isolation_forest.pkl
    - FRAUD_THRESHOLD=0.7
  volumes:
    - ./models:/models
  deploy:
    resources:
      limits:
        cpus: '0.6'
        memory: 256M
```

---

## 🧪 Código

```python
from sklearn.ensemble import IsolationForest
import joblib, nats, json, datetime

# Load model
model = joblib.load('/models/isolation_forest.pkl')

nc = await nats.connect('nats://mordomo-nats:4222')

async def detect_fraud(msg):
    data = json.loads(msg.data.decode())
    
    # Extract features
    features = [
        data['amount'],
        datetime.datetime.fromtimestamp(data['timestamp']).hour,
        is_new_recipient(data['pix_key']),  # 1 if new, 0 if known
        transactions_last_24h(data['pix_key'])
    ]
    
    # Predict anomaly score
    score = model.decision_function([features])[0]
    fraud_score = 1 / (1 + np.exp(score))  # Normalize to 0-1
    
    if fraud_score > 0.7:
        await nc.publish('pagamentos.fraud.detected', json.dumps({
            'pix_key': data['pix_key'],
            'amount': data['amount'],
            'fraud_score': round(fraud_score, 2),
            'reasons': get_reasons(features)
        }).encode())
    else:
        await nc.publish('pagamentos.fraud.approved', json.dumps({
            'fraud_score': round(fraud_score, 2)
        }).encode())

await nc.subscribe('pagamentos.pix.send', cb=detect_fraud)
```

---

## 📊 Features

```yaml
1. amount: Valor da transação
2. hour_of_day: 0-23 (madrugada é suspeito)
3. new_recipient: 1 se nunca transacionou antes
4. frequency_24h: Número de transações nas últimas 24h
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Isolation Forest model
- ✅ 4-feature detection
- ✅ Threshold 0.7
