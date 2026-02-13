# Raspberry Pi 5 16GB - Módulo de Investimentos

> 📍 **Navegação:** [🏠 Início](../../README.md) > [🔧 Hardware](../README.md) > [📈 Investimentos (RPi 5 16GB)](README.md)

## 📋 Especificações do Hardware

### Raspberry Pi 5 16GB
- **SoC**: Broadcom BCM2712 (Cortex-A76 quad-core 2.4GHz)
- **RAM**: 16GB LPDDR4X-4267
- **Armazenamento**: MicroSD 128GB
- **Rede**: Gigabit Ethernet + Wi-Fi 5 + Bluetooth 5.0
- **Alimentação**: 5V/5A USB-C (27W)
- **Preço**: **$120** + periféricos $20 = **$140 TOTAL**

## 🎯 Função no Sistema

Módulo responsável por:
- Trading automatizado (ações, cripto, forex)
- Análise técnica (indicadores, padrões)
- Bots de apostas esportivas (value betting)
- Backtesting de estratégias
- Machine Learning para predição
- Portfolio management

## 🧠 LLM - Qwen 3B Q4_K_M

- **Modelo**: 3B parâmetros, 1.8GB VRAM
- **Função**: Análise de notícias financeiras, sentiment analysis, recomendações
- **Recursos**: 3GB RAM necessária / 16GB disponível = **19% uso** ✅ (sobra muito)

## 📦 Containers e Repositórios

Este hardware executa **7 containers** especializados em investimentos:

### 📈 Ecossistema Investimentos (7 containers)

| Container | Função | Status | Repositório |
|-----------|--------|--------|-------------|
| **investimentos-brain** | LLM financeiro (Qwen 3B) | 📋 | [AslamSys/investimentos-brain](https://github.com/AslamSys/investimentos-brain) |
| **stock-trading-bot** | Trading automatizado | 📋 | [AslamSys/investimentos-trading-bot](https://github.com/AslamSys/investimentos-trading-bot) |
| **technical-analysis** | Análise técnica (TA-Lib) | 📋 | [AslamSys/investimentos-technical-analysis](https://github.com/AslamSys/investimentos-technical-analysis) |
| **news-sentiment** | Sentiment analysis (FinBERT) | 📋 | [AslamSys/investimentos-news-sentiment](https://github.com/AslamSys/investimentos-news-sentiment) |
| **betting-bot** | Apostas esportivas | 📋 | [AslamSys/investimentos-betting-bot](https://github.com/AslamSys/investimentos-betting-bot) |
| **ml-predictor** | Machine Learning (LSTM/LightGBM) | 📋 | [AslamSys/investimentos-ml-predictor](https://github.com/AslamSys/investimentos-ml-predictor) |
| **portfolio-manager** | Gestão de portfolio | 📋 | [AslamSys/investimentos-portfolio-manager](https://github.com/AslamSys/investimentos-portfolio-manager) |

**💡 Status:**
- ✅ **Implementado** - Container funcionando em produção
- ⏳ **Em desenvolvimento** - Código em progresso ativo
- 📋 **Especificado** - Documentado, repositório criado, aguardando implementação

**📊 Fase atual:** Todos os containers estão em **fase de estudo/planejamento** (📋)

**📁 Recursos do Hardware:**
- **RAM Total**: 16GB / 16GB = **100% uso** ⚠️ (limite, mas aceitável)
- **CPU Total**: 700% / 400% = **175% uso** ❌ (execução por turnos)
- **CPU Ajustada**: 450% / 400% = **113% uso** ✅ (4-5 containers ativos)
- **LLM**: Qwen 3B Q4_K_M (3GB RAM, 150% CPU)

---

## 🔌 Integração NATS

### Comandos Recebidos
```
investimentos.stock.buy           # Comprar ação
investimentos.stock.sell          # Vender ação
investimentos.crypto.trade        # Trade cripto
investimentos.bet.place           # Fazer aposta
investimentos.portfolio.rebalance # Rebalancear carteira
investimentos.strategy.backtest   # Testar estratégia
```

### Eventos Publicados
```
investimentos.trade.executed      # Trade executado
investimentos.alert.target        # Meta atingida
investimentos.alert.stop_loss     # Stop loss acionado
investimentos.bet.win             # Aposta vencedora
investimentos.portfolio.summary   # Resumo diário
```

## 📈 Estratégias de Trading

### 1. Mean Reversion (Reversão à Média)
```python
# Bollinger Bands + RSI
if price < lower_band and RSI < 30:
  buy_signal = True  # Sobrevendido

if price > upper_band and RSI > 70:
  sell_signal = True  # Sobrecomprado
```

### 2. Momentum (Tendência)
```python
# MACD + ADX
if MACD_cross_up and ADX > 25:
  buy_signal = True  # Tendência de alta forte

if MACD_cross_down:
  sell_signal = True  # Reversão
```

### 3. Machine Learning (LSTM)
```python
# Predição de preço para próximas 24h
features = [
  'price_history_60d',
  'volume',
  'RSI', 'MACD', 'ATR',
  'news_sentiment',
  'btc_correlation'
]

predicted_price = lstm_model.predict(features)
if predicted_price > current_price * 1.02:  # +2%
  buy_signal = True
```

## 🎲 Bots de Apostas Esportivas

### Value Betting
```python
# Encontrar odds desvalorizadas
fair_odds = calculate_fair_odds(match_data)
bookmaker_odds = get_bookmaker_odds()

edge = (fair_odds - bookmaker_odds) / fair_odds

if edge > 0.05:  # 5% de vantagem
  place_bet(amount=kelly_criterion(edge))
```

### Supported Bookmakers
- **Bet365** (API via scraping)
- **Pinnacle** (API oficial - sharp bookmaker)
- **Betfair** (Exchange, API oficial)

## 🗄️ Banco de Dados (PostgreSQL + TimescaleDB)

### Tabela: `stock_prices` (TimescaleDB hypertable)
```sql
CREATE TABLE stock_prices (
  time TIMESTAMPTZ NOT NULL,
  symbol VARCHAR(10) NOT NULL,
  open DECIMAL(12,4),
  high DECIMAL(12,4),
  low DECIMAL(12,4),
  close DECIMAL(12,4),
  volume BIGINT,
  PRIMARY KEY (time, symbol)
);

SELECT create_hypertable('stock_prices', 'time');
```

### Tabela: `trades`
```sql
CREATE TABLE trades (
  id UUID PRIMARY KEY,
  strategy VARCHAR(50),
  symbol VARCHAR(10),
  type VARCHAR(10), -- buy, sell
  quantity DECIMAL(18,8),
  price DECIMAL(12,4),
  total DECIMAL(15,2),
  fees DECIMAL(10,4),
  profit_loss DECIMAL(15,2),
  executed_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `ml_predictions`
```sql
CREATE TABLE ml_predictions (
  id UUID PRIMARY KEY,
  symbol VARCHAR(10),
  model VARCHAR(50), -- lstm, lightgbm
  predicted_price DECIMAL(12,4),
  actual_price DECIMAL(12,4),
  confidence DECIMAL(3,2),
  horizon VARCHAR(10), -- 1h, 24h, 7d
  predicted_at TIMESTAMP,
  realized_at TIMESTAMP
);
```

## 🤖 Machine Learning Pipeline

### Treinamento (Offline - 1x/dia)
```bash
# 02:00 AM (mercado fechado)
docker-compose run --rm ml-predictor python train.py \
  --model lstm \
  --symbol PETR4 \
  --lookback 60 \
  --horizon 24h \
  --epochs 50
```

### Inferência (Tempo Real)
```python
# A cada 15 minutos durante pregão
predictions = model.predict(latest_features)

NATS.publish('investimentos.alert.target', {
  'symbol': 'PETR4',
  'current': 38.50,
  'predicted_24h': 39.80,
  'confidence': 0.87,
  'action': 'BUY'
})
```

## 📊 APIs Integradas

### Mercado Brasileiro (B3)
- **Yahoo Finance** (dados históricos grátis)
- **Alpha Vantage** (API grátis 500 req/dia)
- **Investing.com** (scraping via selenium)

### Criptomoedas
- **Binance API** (WebSocket real-time)
- **Bybit API** (futures trading)
- **CoinGecko** (preços + marketcap)

### Notícias Financeiras
- **NewsAPI** (headlines gerais)
- **Valor Econômico** (scraping RSS)
- **InfoMoney** (scraping)
- **Twitter/X** (sentiment de traders)

## 💰 Gestão de Risco

### Position Sizing (Kelly Criterion)
```python
# Percentual do capital a investir
win_rate = 0.55  # 55% de trades vencedores
avg_win = 0.03   # Ganho médio 3%
avg_loss = 0.02  # Perda média 2%

kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
# kelly ≈ 0.15 → investir 15% do capital por trade

# Aplicar fracionário (1/4 Kelly para segurança)
position_size = capital * kelly * 0.25
```

### Stop Loss Automático
```python
# Stop loss de 2% + trailing stop
if price < entry_price * 0.98:
  sell('stop_loss')

if price > highest_price * 0.98:  # Trailing
  update_stop(highest_price * 0.98)
```

## 🔒 Segurança

### API Keys
- Armazenadas criptografadas (Vault)
- Permissões mínimas (read-only quando possível)
- Rotação trimestral

### Rate Limiting
- Respeitar limites das exchanges (evitar ban)
- Binance: 1200 req/min
- Bybit: 120 req/min

### Auditoria
- Todos trades logados (imutável)
- Reconciliação diária com exchange
- Alertas de atividades suspeitas

## 💡 Casos de Uso

1. **Trade Automático**: 
   - "Compra R$ 1000 em PETR4 se cair 5%" → Order programada

2. **Alerta de Meta**:
   - PETR4 atinge R$ 40 → Notifica + vende automaticamente

3. **Diversificação**:
   - "Investe R$ 5000 em small caps" → Brain seleciona 10 ações com ML

4. **Arbitragem Cripto**:
   - BTC Binance $43.500 / Bybit $43.800 → Compra/vende (lucro $300)

5. **Betting Value**:
   - Flamengo x Palmeiras → Odds desvalorizadas → Aposta R$ 200 (edge 8%)

## 📈 Métricas de Performance

- **Sharpe Ratio**: Retorno ajustado ao risco
- **Max Drawdown**: Maior queda do capital
- **Win Rate**: % de trades vencedores
- **Profit Factor**: Lucro bruto / Prejuízo bruto
- **ROI Mensal**: Retorno sobre investimento
