# 💼 Portfolio Manager

**Container:** `portfolio-manager`  
**Stack:** Python + pandas  
**Propósito:** Gestão e rebalanceamento de carteira

---

## 📋 Propósito

Gerenciar portfolio de investimentos. Rebalanceamento automático, cálculo de risk/return, diversificação.

---

## 🎯 Features

- ✅ Rebalanceamento automático (mensal)
- ✅ Cálculo de Sharpe Ratio
- ✅ Diversificação por asset class
- ✅ Relatórios de performance
- ✅ Tax-loss harvesting

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "investimentos.portfolio.rebalance"
Payload: {
  "target_allocation": {
    "stocks": 0.60,
    "crypto": 0.20,
    "bonds": 0.15,
    "cash": 0.05
  }
}
```

### Publish
```javascript
Topic: "investimentos.portfolio.summary"
Payload: {
  "total_value": 50000.00,
  "daily_return": 0.015,  // 1.5%
  "ytd_return": 0.23,  // 23%
  "sharpe_ratio": 1.8,
  "max_drawdown": -0.12,
  "allocation": {
    "stocks": 0.62,
    "crypto": 0.18,
    "bonds": 0.15,
    "cash": 0.05
  }
}
```

---

## 🚀 Docker Compose

```yaml
portfolio-manager:
  build: ./portfolio-manager
  environment:
    - DATABASE_URL=postgresql://postgres:password@mordomo-postgres:5432/mordomo
    - REBALANCE_FREQUENCY=monthly
  deploy:
    resources:
      limits:
        cpus: '0.4'
        memory: 1536M
```

---

## 🧪 Código (Rebalancing)

```python
import pandas as pd

def rebalance_portfolio(current_holdings, target_allocation, total_value):
    """
    Rebalance portfolio to target allocation.
    """
    rebalance_orders = []
    
    for asset_class, target_pct in target_allocation.items():
        current_value = sum([h['value'] for h in current_holdings if h['class'] == asset_class])
        current_pct = current_value / total_value
        
        target_value = total_value * target_pct
        diff = target_value - current_value
        
        if abs(diff) > total_value * 0.05:  # Rebalance if > 5% deviation
            rebalance_orders.append({
                'asset_class': asset_class,
                'action': 'buy' if diff > 0 else 'sell',
                'amount': abs(diff)
            })
    
    return rebalance_orders

# Calculate Sharpe Ratio
def sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Automatic rebalancing
- ✅ Sharpe ratio calculation
- ✅ Monthly reports
