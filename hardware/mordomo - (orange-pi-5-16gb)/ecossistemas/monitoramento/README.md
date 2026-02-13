# 📊 Ecossistema Monitoramento
> 📍 **Navegação:** [🏠 Início](../../../../README.md) > [🔧 Hardware](../../../README.md) > [🎯 Mordomo](../../README.md) > [🌐 Ecossistemas](../README.md) > [📁 Monitoramento](README.md)
Observabilidade completa do sistema com coleta de métricas, logs centralizados e dashboards visuais.

---

## Visão Geral

O ecossistema de **Monitoramento** fornece visibilidade total sobre o funcionamento do sistema:

- 📈 **Métricas em tempo real** (CPU, RAM, latência, requests)
- 📝 **Logs centralizados** de todos os containers
- 📊 **Dashboards visuais** para análise e debug
- 🔔 **Alertas** para anomalias e erros

---

## Arquitetura de Containers (2 containers)

```
┌────────────────────────────────────────────────┐
│         ECOSSISTEMA MONITORAMENTO              │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────┐                             │
│  │  Prometheus  │◄────┐                       │
│  │   Métricas   │     │                       │
│  └──────┬───────┘     │                       │
│         │             │                       │
│         │             │                       │
│  ┌──────▼───────┐  ┌──┴──────────┐           │
│  │   Grafana    │  │    Loki     │           │
│  │  Dashboards  │  │    Logs     │           │
│  └──────────────┘  └─────────────┘           │
│         ▲                  ▲                   │
│         │                  │                   │
│    (visualização)    (coleta logs)            │
│                                                │
└────────────────────────────────────────────────┘
         ▲
         │
    [Todos os containers do sistema]
```

---

## 📦 Lista de Containers

### 1. **prometheus**

**Função:** Coleta e armazenamento de métricas time-series

**Tecnologia:** [Prometheus](https://prometheus.io/)

**Por que Prometheus?**
- ✅ **Padrão de mercado** para métricas
- ✅ **Pull-based:** Scrape automático de endpoints
- ✅ **PromQL:** Linguagem poderosa de queries
- ✅ **Alerting:** Integração com Alertmanager
- ✅ **Leve:** Roda bem em ARM

**Responsabilidades:**
- Coletar métricas de todos containers a cada 15s
- Armazenar time-series localmente
- Processar queries PromQL
- Avaliar regras de alerta
- Expor dados para Grafana

**Métricas Coletadas:**

**Sistema:**
- CPU usage por container
- Memória (RAM) usada/disponível
- I/O de disco
- Network throughput

**Aplicação (Mordomo):**
- `wake_word_detections_total` - Total de ativações
- `stt_latency_seconds` - Latência do STT
- `llm_requests_total` - Requisições ao LLM
- `llm_latency_seconds` - Latência do LLM
- `tts_generation_seconds` - Tempo de síntese TTS
- `speaker_identification_accuracy` - Precisão Speaker ID
- `active_conversations` - Conversas ativas
- `events_published_total{subject}` - Eventos no NATS

**Infraestrutura:**
- `nats_messages_total` - Mensagens no NATS
- `qdrant_vectors_count` - Vetores no Qdrant
- `postgres_connections_active` - Conexões PostgreSQL

**Configuração (prometheus.yml):**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # NATS metrics
  - job_name: 'nats'
    static_configs:
      - targets: ['nats:8222']

  # Qdrant metrics
  - job_name: 'qdrant'
    static_configs:
      - targets: ['qdrant-vectors:6333']

  # PostgreSQL exporter
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Containers do Mordomo
  - job_name: 'mordomo-core-api'
    static_configs:
      - targets: ['mordomo-core-api:3000']

  - job_name: 'mordomo-brain'
    static_configs:
      - targets: ['mordomo-brain:8080']

  # Outros containers...
```

**Regras de Alerta (alerts.yml):**
```yaml
groups:
  - name: sistema
    interval: 30s
    rules:
      # Alta latência no STT
      - alert: STT_HighLatency
        expr: stt_latency_seconds > 1.0
        for: 1m
        annotations:
          summary: "STT com latência alta: {{ $value }}s"

      # LLM offline
      - alert: LLM_Down
        expr: up{job="mordomo-brain"} == 0
        for: 30s
        annotations:
          summary: "LLM Brain está offline!"

      # Memória alta
      - alert: HighMemoryUsage
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.85
        for: 2m
        annotations:
          summary: "Container {{ $labels.name }} usando >85% RAM"
```

**Docker Compose:**
```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
    - ./alerts.yml:/etc/prometheus/alerts.yml
    - prometheus-data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=30d'  # Retenção de 30 dias
  restart: unless-stopped
  networks:
    - monitoring-net
```

**Acesso UI:** http://localhost:9090

**Queries Úteis (PromQL):**
```promql
# Latência média do STT nos últimos 5min
rate(stt_latency_seconds_sum[5m]) / rate(stt_latency_seconds_count[5m])

# Total de wake words detectadas hoje
increase(wake_word_detections_total[24h])

# CPU usage por container
rate(container_cpu_usage_seconds_total[5m]) * 100

# Requisições por segundo no Core API
rate(http_requests_total{job="mordomo-core-api"}[1m])
```

---

### 2. **loki**

**Função:** Agregação e indexação de logs distribuídos

**Tecnologia:** [Grafana Loki](https://grafana.com/oss/loki/)

**Por que Loki?**
- ✅ **Leve:** Não indexa todo conteúdo, só labels
- ✅ **Integração perfeita** com Grafana
- ✅ **LogQL:** Query language similar ao PromQL
- ✅ **Multi-tenant:** Separação por namespace
- ✅ **Roda bem em ARM**

**Responsabilidades:**
- Coletar logs de todos containers
- Indexar por labels (container, level, source)
- Armazenar logs comprimidos
- Processar queries LogQL
- Expor dados para Grafana

**Componentes:**
- **Loki:** Server de logs

**Configuração (loki-config.yml):**
```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb:
    directory: /loki/index
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h  # 1 semana

chunk_store_config:
  max_look_back_period: 720h  # 30 dias
```



**Docker Compose:**
```yaml
loki:
  image: grafana/loki:latest
  container_name: loki
  ports:
    - "3100:3100"
  volumes:
    - ./loki-config.yml:/etc/loki/local-config.yaml
    - loki-data:/loki
  command: -config.file=/etc/loki/local-config.yaml
  restart: unless-stopped
  networks:
    - monitoring-net
```

**Queries Úteis (LogQL):**
```logql
# Todos os logs do Core API
{container="mordomo-core-api"}

# Erros nos últimos 5min
{level="error"} |= "" | logfmt | __error__="" 

# Logs do STT com palavra "timeout"
{container="whisper-asr"} |= "timeout"

# Taxa de erros por minuto
rate({level="error"}[1m])

# Top 10 mensagens de erro
topk(10, count_over_time({level="error"}[24h]))
```

---

### 3. **grafana**

**Função:** Dashboards visuais e análise de dados

**Tecnologia:** [Grafana](https://grafana.com/)

**Por que Grafana?**
- ✅ **Visualização poderosa** de métricas e logs
- ✅ **Dashboards customizáveis**
- ✅ **Alerting visual**
- ✅ **Multi-datasource:** Prometheus + Loki
- ✅ **Mobile-friendly**

**Responsabilidades:**
- Visualizar métricas do Prometheus
- Visualizar logs do Loki
- Criar dashboards customizados
- Alertas visuais
- Correlação de métricas + logs

**Dashboards Pré-configurados:**

**1. Sistema Geral**
- CPU/RAM por container
- Network I/O
- Disk usage
- Container health

**2. Mordomo Overview**
- Wake word detections (gráfico de linha)
- Active conversations (gauge)
- Latência média STT/LLM/TTS (heatmap)
- Precisão Speaker ID (%)
- Eventos NATS por segundo

**3. LLM Brain**
- Requests por segundo
- Latência p50/p95/p99
- Local vs Cloud ratio
- Tokens consumidos
- Cache hit rate

**4. Logs Centralizados**
- Stream em tempo real
- Filtros por container/level
- Search full-text
- Error patterns

**Configuração (datasources.yml):**
```yaml
apiVersion: 1

datasources:
  # Prometheus
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

  # Loki
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
```

**Docker Compose:**
```yaml
grafana:
  image: grafana/grafana:latest
  container_name: grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    - GF_USERS_ALLOW_SIGN_UP=false
  volumes:
    - grafana-data:/var/lib/grafana
    - ./datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    - ./dashboards:/etc/grafana/provisioning/dashboards
  restart: unless-stopped
  networks:
    - monitoring-net
```

**Acesso UI:** http://localhost:3000
- **User:** admin
- **Password:** definido em `.env`

**Exemplo de Dashboard JSON (Sistema):**
```json
{
  "dashboard": {
    "title": "Mordomo - Sistema Geral",
    "panels": [
      {
        "title": "CPU Usage",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total[5m]) * 100"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Wake Word Detections",
        "targets": [
          {
            "expr": "increase(wake_word_detections_total[1h])"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

---

## 🔗 Integração Completa

### Fluxo de Dados

```
[Containers] 
    ├─► logs → Loki → Grafana
    └─► metrics → Prometheus → Grafana

[Grafana]
    ├─► Dashboards visuais
    ├─► Alertas (email/Slack)
    └─► Correlação métricas + logs
```

---

## 🛠️ Deploy Completo

**docker-compose.yml (Monitoramento):**
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alerts.yml:/etc/prometheus/alerts.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
    restart: unless-stopped
    networks:
      - monitoring-net

  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    restart: unless-stopped
    networks:
      - monitoring-net

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    restart: unless-stopped
    networks:
      - monitoring-net

volumes:
  prometheus-data:
  loki-data:
  grafana-data:

networks:
  monitoring-net:
    driver: bridge
```

**Comandos:**
```bash
# Subir stack de monitoramento
docker-compose up -d

# Ver logs
docker-compose logs -f grafana

# Recarregar config do Prometheus
curl -X POST http://localhost:9090/-/reload
```

---

## 📊 Portas e Acesso

| Serviço | Porta | Acesso |
|---------|-------|--------|
| Prometheus | 9090 | http://localhost:9090 |
| Loki | 3100 | http://localhost:3100 (API) |
| Grafana | 3000 | http://localhost:3000 |

---

## 🔔 Alertas

**Configuração de notificações (Grafana):**

**Slack:**
```yaml
notifiers:
  - name: Slack
    type: slack
    settings:
      url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
      recipient: "#alerts"
```

**Email:**
```yaml
notifiers:
  - name: Email
    type: email
    settings:
      addresses: "admin@example.com"
```

**Telegram:**
```yaml
notifiers:
  - name: Telegram
    type: telegram
    settings:
      bottoken: "YOUR_BOT_TOKEN"
      chatid: "YOUR_CHAT_ID"
```

---

## 📈 Métricas Importantes

| Métrica | Threshold | Ação |
|---------|-----------|------|
| STT Latency | >1s | Alerta |
| LLM Latency | >2s | Alerta |
| CPU Usage | >80% | Warning |
| RAM Usage | >85% | Alerta |
| Disk Usage | >90% | Alerta Crítico |
| Container Down | - | Alerta Imediato |

---

## 🚀 Boas Práticas

1. **Retenção de Dados:**
   - Prometheus: 30 dias
   - Loki: 30 dias
   - Grafana: Backups semanais

2. **Labels Consistentes:**
   - `container`, `job`, `instance`, `level`

3. **Dashboards:**
   - Um dashboard por ecossistema
   - Alertas visíveis no topo

4. **Performance:**
   - Scrape interval: 15s (não <10s)
   - Log sampling em produção

---

**Documentação atualizada:** 27/11/2025
