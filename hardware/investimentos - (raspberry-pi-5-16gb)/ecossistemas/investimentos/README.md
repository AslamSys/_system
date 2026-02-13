# 📈 Ecossistema Investimentos

> 🗂️ **Navegação:** [🏠 Início](../../../../README.md) > [🔧 Hardware](../../../README.md) > [📈 Investimentos](../../README.md) > [🌐 Ecossistema Investimentos](README.md)

Sistema completo de trading automatizado, análise técnica, apostas esportivas e machine learning para predição financeira.

---

## 📋 Visão Geral

O ecossistema de **Investimentos** oferece capacidades avançadas para:

- 📊 **Trading Automatizado** - Ações, criptomoedas, forex
- 📈 **Análise Técnica** - Indicadores, padrões, sinais
- 🎲 **Apostas Esportivas** - Value betting, arbitragem
- 🤖 **Machine Learning** - Predição de preços, sentiment analysis
- 📋 **Gestão de Portfolio** - Balanceamento, rebalancing

---

## 🏗️ Arquitetura de Containers (7 containers)

```
┌─────────────────────────────────────────────────┐
│          ECOSSISTEMA INVESTIMENTOS              │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────┐    ┌──────────────────┐   │
│  │investimentos-   │    │ stock-trading-   │   │
│  │brain (Qwen 3B)  │    │ bot (B3/Crypto)  │   │
│  └─────────────────┘    └──────────────────┘   │
│                                                 │
│  ┌─────────────────┐    ┌──────────────────┐   │
│  │technical-       │    │ news-sentiment   │   │
│  │analysis (TA-Lib)│    │ (FinBERT + AI)   │   │
│  └─────────────────┘    └──────────────────┘   │
│                                                 │
│  ┌─────────────────┐    ┌──────────────────┐   │
│  │ betting-bot     │    │ ml-predictor     │   │
│  │ (Sports API)    │    │ (LSTM/LightGBM)  │   │
│  └─────────────────┘    └──────────────────┘   │
│                                                 │
│  ┌─────────────────┐                           │
│  │ portfolio-      │                           │
│  │ manager         │                           │
│  └─────────────────┘                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📦 Lista de Containers

### 1. **investimentos-brain**
- **Função:** LLM para análise financeira e decisões de investimento
- **Modelo:** Qwen 3B Q4_K_M (1.8GB VRAM)
- **RAM:** 3GB
- **CPU:** 150%
- **Recursos:** Análise de notícias, sentiment analysis, recomendações

### 2. **stock-trading-bot**
- **Função:** Trading automatizado em múltiplas exchanges
- **Integrações:** Binance, Bybit, B3 (ações brasileiras)
- **RAM:** 2GB
- **CPU:** 100%
- **Estratégias:** Grid trading, DCA, swing trading

### 3. **technical-analysis**
- **Função:** Análise técnica avançada com indicadores
- **Bibliotecas:** TA-Lib, pandas, numpy
- **RAM:** 3GB
- **CPU:** 120%
- **Indicadores:** RSI, MACD, Bollinger Bands, Fibonacci

### 4. **news-sentiment**
- **Função:** Análise de sentimento de notícias financeiras
- **Modelo:** FinBERT + web scraping
- **RAM:** 2.5GB
- **CPU:** 80%
- **Fontes:** InfoMoney, Valor Econômico, Reuters, Bloomberg

### 5. **betting-bot**
- **Função:** Apostas esportivas automatizadas (value betting)
- **Integrações:** Bet365, Pinnacle, APIs de odds
- **RAM:** 1GB
- **CPU:** 60%
- **Esportes:** Futebol, tênis, basquete, e-sports

### 6. **ml-predictor**
- **Função:** Machine Learning para predição de preços
- **Algoritmos:** LSTM, LightGBM, Random Forest
- **RAM:** 3GB
- **CPU:** 150%
- **Datasets:** Histórico de preços, indicadores, sentiment

### 7. **portfolio-manager**
- **Função:** Gestão e balanceamento de portfolio
- **Recursos:** Rebalancing automático, diversificação, risk management
- **RAM:** 1.5GB
- **CPU:** 40%
- **Métricas:** Sharpe Ratio, Max Drawdown, volatilidade

---

## 🔌 Integração NATS

### Comandos Recebidos
```bash
investimentos.trade.buy           # Comprar ativo
investimentos.trade.sell          # Vender ativo
investimentos.analysis.technical  # Análise técnica
investimentos.portfolio.balance   # Consultar portfolio
investimentos.news.sentiment      # Análise de sentiment
investimentos.bet.place           # Fazer aposta
```

### Eventos Publicados
```bash
investimentos.trade.executed      # Trade executado
investimentos.signal.generated    # Sinal de compra/venda
investimentos.bet.placed         # Aposta realizada
investimentos.portfolio.updated   # Portfolio atualizado
investimentos.alert.risk         # Alerta de risco
```

---

## 📊 Recursos do Hardware

| Container | RAM | CPU | Função Principal |
|-----------|-----|-----|------------------|
| **investimentos-brain** | 3GB | 150% | LLM financeiro |
| **stock-trading-bot** | 2GB | 100% | Trading automatizado |
| **technical-analysis** | 3GB | 120% | Indicadores técnicos |
| **news-sentiment** | 2.5GB | 80% | Sentiment analysis |
| **betting-bot** | 1GB | 60% | Apostas esportivas |
| **ml-predictor** | 3GB | 150% | ML predição |
| **portfolio-manager** | 1.5GB | 40% | Gestão portfolio |
| **TOTAL** | **16GB** | **700%** | RPi 5 16GB (limite) |

### ⚡ Otimização de Recursos
- **Execução por turnos:** Apenas 4-5 containers ativos simultaneamente
- **ml-predictor:** Executa offline (1x/dia à noite)
- **CPU ajustada:** 450%/400% = 113% uso (picos tolerados)

---

## 🌐 Links Relacionados

- **Hardware:** [Raspberry Pi 5 16GB - Investimentos](../../README.md)
- **Containers:** [Lista Detalhada](containers/)
- **Infraestrutura:** [NATS, PostgreSQL, Qdrant](../../mordomo%20-%20(orange-pi-5-16gb)/ecossistemas/infraestrutura/README.md)
- **Monitoramento:** [Métricas e Dashboards](../../mordomo%20-%20(orange-pi-5-16gb)/ecossistemas/monitoramento/README.md)

---

## 📈 Estratégias de Trading

### Análise Técnica
- **Indicadores:** RSI, MACD, Bollinger Bands, Stochastic
- **Padrões:** Head & Shoulders, Flag, Triangle
- **Timeframes:** 1m, 5m, 15m, 1h, 4h, 1d

### Machine Learning
- **Features:** Preço, volume, indicadores, sentiment, volatilidade
- **Modelos:** LSTM (temporal), LightGBM (tabular), Ensemble
- **Backtesting:** 2+ anos históricos, walk-forward validation

### Risk Management
- **Stop Loss:** 2-5% por trade
- **Position Size:** 1-3% do capital por posição
- **Max Drawdown:** 15% do portfolio
- **Diversificação:** Máximo 20% em um ativo

---

## 📝 Status de Implementação

- [x] Documentação completa
- [x] Especificação de containers
- [ ] Implementação investimentos-brain
- [ ] Trading bots (Binance, B3)
- [ ] Análise técnica (TA-Lib)
- [ ] ML predictor (LSTM)
- [ ] Betting bot (APIs)
- [ ] Portfolio manager
- [ ] Backtesting framework
- [ ] Testes em paper trading
- [ ] Deploy em produção

---

**Hardware:** Raspberry Pi 5 16GB  
**Ecossistema:** Investimentos  
**Última atualização:** 13/02/2026