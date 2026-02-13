# 🎲 Sports Betting Bot

**Container:** `betting-bot`  
**Stack:** Python + Bet365 API (scraping)  
**Estratégia:** Value Betting

---

## 📋 Propósito

Bot de apostas esportivas usando Value Betting. Identifica odds desvalorizadas e calcula Kelly Criterion para stake.

---

## 🎯 Features

- ✅ Value Betting (edge > 5%)
- ✅ Kelly Criterion para stake
- ✅ Scraping de odds (Bet365, Pinnacle)
- ✅ Modelo de probabilidade (Poisson para futebol)

---

## 🔌 NATS Topics

### Publish
```javascript
Topic: "investimentos.bet.placed"
Payload: {
  "match": "Flamengo vs Palmeiras",
  "bet_type": "home_win",
  "odds": 2.10,
  "fair_odds": 1.90,
  "edge": 0.10,  // 10%
  "stake": 50.00
}

Topic: "investimentos.bet.result"
Payload: {
  "bet_id": "BET_123",
  "result": "win|loss",
  "profit": 55.00
}
```

---

## 🚀 Docker Compose

```yaml
betting-bot:
  build: ./betting-bot
  environment:
    - BET365_USERNAME=${BET365_USERNAME}
    - BET365_PASSWORD=${BET365_PASSWORD}
    - KELLY_FRACTION=0.25  # Conservative Kelly
    - MIN_EDGE=0.05  # 5% minimum edge
  deploy:
    resources:
      limits:
        cpus: '0.6'
        memory: 1024M
```

---

## 🧪 Código (Poisson Model)

```python
from scipy.stats import poisson
import numpy as np

def calculate_fair_odds(home_goals_avg, away_goals_avg):
    # Poisson distribution for goals
    home_probs = [poisson.pmf(i, home_goals_avg) for i in range(10)]
    away_probs = [poisson.pmf(i, away_goals_avg) for i in range(10)]
    
    # P(home win)
    p_home_win = sum([
        home_probs[i] * sum(away_probs[:i])
        for i in range(1, 10)
    ])
    
    fair_odds = 1 / p_home_win
    return fair_odds

def kelly_criterion(odds, prob_win, fraction=0.25):
    # Kelly formula: (odds * prob_win - 1) / (odds - 1)
    kelly = (odds * prob_win - 1) / (odds - 1)
    return max(0, kelly * fraction)  # Conservative fraction

# Example
fair_odds = calculate_fair_odds(1.8, 1.2)  # Home avg 1.8 goals, Away 1.2
bookmaker_odds = 2.10
edge = (fair_odds - bookmaker_odds) / fair_odds

if edge > 0.05:  # 5% minimum
    stake = kelly_criterion(bookmaker_odds, 1/fair_odds) * bankroll
    place_bet(stake)
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Poisson model
- ✅ Kelly Criterion
- ✅ Bet365 scraping
