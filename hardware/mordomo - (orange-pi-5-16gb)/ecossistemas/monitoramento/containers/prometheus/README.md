# 📊 Prometheus

**Container:** `prometheus`  
**Ecossistema:** Monitoramento  
**Papel:** Metrics Collection & Storage

---

## 📋 Propósito

Sistema de monitoramento e alerta baseado em time-series para coletar, armazenar e consultar métricas de todos os containers.

---

## 🎯 Responsabilidades

- ✅ Coletar métricas via scraping (pull model)
- ✅ Armazenar time-series data
- ✅ Executar queries PromQL
- ✅ Alertas baseados em regras
- ✅ Service discovery (Consul integration)
- ✅ Exportar métricas para Grafana

---

## 🔧 Tecnologias

**Prometheus** v2.48+
- Time-series database
- PromQL query language
- Alertmanager integration
- Service discovery
- HTTP API
- Web UI

**Imagem:** `prom/prometheus:v2.48.0`

---

## 📊 Especificações

```yaml
Performance:
  CPU: 10-20%
  RAM: 500 MB - 2 GB
  Storage: 5-20 GB (retention dependent)
  
Scraping:
  Interval: 15s (default)
  Timeout: 10s
  
Retention:
  Time: 15 dias
  Size: 10 GB (max)
  
Targets:
  Total: ~20 containers
  Concurrent: Unlimited
```

---

## ⚙️ Configuração

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'mordomo-prod'
    environment: 'production'

# Alertmanager (opcional)
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Rules para alertas
rule_files:
  - '/etc/prometheus/rules/*.yml'

# Scrape configs
scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  # NATS cluster
  - job_name: 'nats'
    static_configs:
      - targets:
          - 'nats-1:8222'
          - 'nats-2:8222'
          - 'nats-3:8222'
    metrics_path: '/metrics'
  
  # Consul cluster
  - job_name: 'consul'
    static_configs:
      - targets:
          - 'consul-server-1:8500'
          - 'consul-server-2:8500'
          - 'consul-server-3:8500'
    metrics_path: '/v1/agent/metrics'
    params:
      format: ['prometheus']
  
  # Qdrant
  - job_name: 'qdrant'
    static_configs:
      - targets: ['qdrant:6333']
    metrics_path: '/metrics'
  
  # PostgreSQL (via pg_exporter)
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  # Mordomo containers (auto-discovery via Consul)
  - job_name: 'mordomo-services'
    consul_sd_configs:
      - server: 'consul-server-1:8500'
        services: []
    relabel_configs:
      - source_labels: [__meta_consul_service]
        target_label: service
      - source_labels: [__meta_consul_node]
        target_label: node
      - source_labels: [__meta_consul_tags]
        target_label: tags
      - source_labels: [__meta_consul_service_address]
        target_label: __address__
        replacement: '${1}:${2}'
        action: replace
        regex: '([^:]+)'
      - source_labels: [__meta_consul_service_metadata_metrics_port]
        target_label: __address__
        replacement: '${1}:${2}'
        action: replace
  
  # Node Exporter (system metrics - opcional)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
  
  # Loki (logs metrics)
  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
  
  # Grafana
  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
    metrics_path: '/metrics'
```

---

## 🚨 Alert Rules

```yaml
# rules/mordomo_alerts.yml
groups:
  - name: mordomo
    interval: 30s
    rules:
      # Container Down
      - alert: ContainerDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Container {{ $labels.job }} is down"
          description: "{{ $labels.instance }} has been down for > 1 minute"
      
      # High CPU
      - alert: HighCPU
        expr: rate(process_cpu_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU on {{ $labels.job }}"
          description: "CPU usage > 80% for 5 minutes"
      
      # High Memory
      - alert: HighMemory
        expr: process_resident_memory_bytes / 1024 / 1024 > 1024
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory on {{ $labels.job }}"
          description: "Memory usage > 1GB for 5 minutes"
      
      # NATS JetStream Storage
      - alert: JetStreamStorageFull
        expr: nats_jetstream_server_store_used_bytes / nats_jetstream_server_store_max_bytes > 0.9
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "JetStream storage almost full"
          description: "JetStream using > 90% of available storage"
      
      # Whisper ASR Latency
      - alert: WhisperHighLatency
        expr: histogram_quantile(0.95, rate(whisper_transcription_duration_seconds_bucket[5m])) > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Whisper ASR high latency"
          description: "P95 latency > 3s for 5 minutes"
      
      # PostgreSQL Connections
      - alert: PostgreSQLHighConnections
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL high connection usage"
          description: "Using > 80% of max connections"
      
      # Disk Space
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space low on {{ $labels.instance }}"
          description: "< 10% disk space available"
```

---

## 📈 Key Metrics

### Mordomo Pipeline
```promql
# Taxa de conversas por minuto
rate(conversations_total[5m])

# Latência end-to-end (P95)
histogram_quantile(0.95, rate(conversation_latency_seconds_bucket[5m]))

# Wake word detection rate
rate(wake_word_detected_total[5m])

# Taxa de sucesso de speaker verification
rate(speaker_verification_success_total[5m]) / rate(speaker_verification_attempts_total[5m])

# Whisper ASR accuracy
whisper_word_error_rate

# Brain token usage
rate(brain_tokens_used_total[5m])

# TTS synthesis time
histogram_quantile(0.50, rate(tts_synthesis_duration_seconds_bucket[5m]))
```

### Infrastructure
```promql
# NATS message rate
rate(nats_core_messages_in_total[5m])

# Consul services
consul_catalog_services

# Qdrant search latency
histogram_quantile(0.95, rate(qdrant_search_duration_seconds_bucket[5m]))

# PostgreSQL query time
pg_stat_statements_mean_exec_time_seconds
```

---

## 🐳 Docker

```dockerfile
FROM prom/prometheus:v2.48.0

# Config
COPY prometheus.yml /etc/prometheus/
COPY rules/ /etc/prometheus/rules/

# Storage
VOLUME ["/prometheus"]

EXPOSE 9090

CMD ["--config.file=/etc/prometheus/prometheus.yml", \
     "--storage.tsdb.path=/prometheus", \
     "--storage.tsdb.retention.time=15d", \
     "--storage.tsdb.retention.size=10GB", \
     "--web.enable-lifecycle", \
     "--web.enable-admin-api"]
```

### Docker Compose
```yaml
prometheus:
  image: prom/prometheus:v2.48.0
  container_name: prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
    - ./rules:/etc/prometheus/rules
    - prometheus-data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=15d'
    - '--storage.tsdb.retention.size=10GB'
    - '--web.enable-lifecycle'
    - '--web.console.libraries=/usr/share/prometheus/console_libraries'
    - '--web.console.templates=/usr/share/prometheus/consoles'
  networks:
    - mordomo-net
  restart: unless-stopped
  depends_on:
    - consul-server-1
    - nats-1

# Postgres Exporter (opcional)
postgres-exporter:
  image: prometheuscommunity/postgres-exporter:latest
  container_name: postgres-exporter
  environment:
    DATA_SOURCE_NAME: "postgresql://mordomo:${POSTGRES_PASSWORD}@postgres:5432/mordomo?sslmode=disable"
  ports:
    - "9187:9187"
  networks:
    - mordomo-net
  depends_on:
    - postgres

volumes:
  prometheus-data:
```

---

## 🔌 HTTP API

### Query
```bash
# Instant query
curl 'http://localhost:9090/api/v1/query?query=up'

# Range query
curl 'http://localhost:9090/api/v1/query_range?query=rate(nats_core_messages_in_total[5m])&start=2024-11-27T00:00:00Z&end=2024-11-27T23:59:59Z&step=15s'

# Metadata
curl 'http://localhost:9090/api/v1/metadata?metric=up'

# Targets
curl 'http://localhost:9090/api/v1/targets'

# Alerts
curl 'http://localhost:9090/api/v1/alerts'
```

### Reload Config
```bash
# Hot reload (sem restart)
curl -X POST http://localhost:9090/-/reload
```

---

## 🧪 Testes

```python
# test_prometheus.py
import requests

def test_prometheus_up():
    response = requests.get('http://localhost:9090/-/healthy')
    assert response.status_code == 200

def test_targets_up():
    response = requests.get('http://localhost:9090/api/v1/targets')
    data = response.json()
    
    active_targets = data['data']['activeTargets']
    
    # Verificar que todos targets estão UP
    for target in active_targets:
        assert target['health'] == 'up', f"{target['labels']['job']} is down"

def test_query():
    query = 'up'
    response = requests.get(
        'http://localhost:9090/api/v1/query',
        params={'query': query}
    )
    
    data = response.json()
    assert data['status'] == 'success'
    assert len(data['data']['result']) > 0

def test_alerts():
    response = requests.get('http://localhost:9090/api/v1/alerts')
    data = response.json()
    
    # Verificar se não há alertas críticos
    critical_alerts = [
        alert for alert in data['data']['alerts']
        if alert['labels'].get('severity') == 'critical'
        and alert['state'] == 'firing'
    ]
    
    assert len(critical_alerts) == 0, f"Critical alerts firing: {critical_alerts}"
```

---

## 📊 PromQL Examples

```promql
# Top 5 containers por CPU
topk(5, rate(process_cpu_seconds_total[5m]))

# Memória por container
sort_desc(process_resident_memory_bytes / 1024 / 1024)

# Taxa de erro (HTTP 5xx)
rate(http_requests_total{status=~"5.."}[5m])

# Disponibilidade (uptime %)
avg_over_time(up[24h]) * 100

# Throughput de mensagens NATS
sum(rate(nats_core_messages_in_total[5m])) by (server_id)

# Latência P99 Whisper
histogram_quantile(0.99, rate(whisper_transcription_duration_seconds_bucket[5m]))

# Taxa de sucesso de conversas
sum(rate(conversations_success_total[5m])) / sum(rate(conversations_total[5m])) * 100

# Crescimento de storage PostgreSQL
delta(pg_database_size_bytes[1h]) / 1024 / 1024
```

---

## 🔧 Troubleshooting

### High Cardinality
```yaml
# Evitar labels com muitos valores únicos
# ❌ Ruim
metric{user_id="123", session_id="abc..."}

# ✅ Bom
metric{service="api", endpoint="/users"}
```

### Storage Crescendo
```bash
# Verificar tamanho
du -sh /prometheus

# Reduzir retention
--storage.tsdb.retention.time=7d

# Limpar manualmente (CUIDADO!)
rm -rf /prometheus/data/*
```

### Targets Lentos
```yaml
# Aumentar timeout
scrape_configs:
  - job_name: 'slow-service'
    scrape_timeout: 30s
```

---

## 🌐 Web UI

Acesso: **http://localhost:9090**

**Funcionalidades:**
- Graph: Executar queries PromQL
- Alerts: Ver alertas ativos
- Targets: Status de scraping
- Service Discovery: Targets descobertos
- Configuration: Ver config atual
- Rules: Ver regras de alerta

---

## 📚 CLI Tools

```bash
# promtool (vem com Prometheus)

# Validar config
promtool check config prometheus.yml

# Validar rules
promtool check rules rules/*.yml

# Test query
promtool query instant http://localhost:9090 'up'

# Test range query
promtool query range http://localhost:9090 \
  --start=2024-11-27T00:00:00Z \
  --end=2024-11-27T23:59:59Z \
  'rate(nats_core_messages_in_total[5m])'

# TSDB stats
promtool tsdb analyze /prometheus
```

---

## 🚨 Alertmanager (Opcional)

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  
  routes:
    - match:
        severity: critical
      receiver: 'critical'
      continue: true
    
    - match:
        severity: warning
      receiver: 'warning'

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://mordomo-core-api:8000/webhooks/alerts'
  
  - name: 'critical'
    webhook_configs:
      - url: 'http://mordomo-core-api:8000/webhooks/alerts/critical'
    # Ou email, Slack, etc:
    # slack_configs:
    #   - api_url: 'https://hooks.slack.com/...'
    #     channel: '#alerts'
  
  - name: 'warning'
    webhook_configs:
      - url: 'http://mordomo-core-api:8000/webhooks/alerts/warning'
```

---

## 🔗 Integração

**Coleta de:**
- Todos containers Mordomo (métricas customizadas)
- NATS (mensagens, JetStream)
- Consul (serviços, health)
- Qdrant (searches, vectors)
- PostgreSQL (queries, connections)
- Loki (logs metrics)
- Grafana (dashboards usage)

**Exporta para:**
- Grafana (visualização)
- Alertmanager (alertas)
- Remote Write (opcional - Thanos, Cortex)

**Monitora:** Próprio Prometheus (self-monitoring)

---

## 📝 Best Practices

```yaml
# 1. Use labels consistentes
metric_name{service="api", environment="prod", version="1.0"}

# 2. Evite labels de alta cardinalidade
# ❌ user_id, session_id, request_id
# ✅ service, endpoint, status_code

# 3. Use histograms para latências
# Permite calcular P50, P95, P99
histogram_quantile(0.95, rate(duration_bucket[5m]))

# 4. Use counters para eventos
# Sempre crescem, use rate() ou increase()
rate(requests_total[5m])

# 5. Use gauges para valores instantâneos
# CPU, memória, connections
current_connections
```

---

**Versão:** 1.0  
**Última atualização:** 27/11/2025  
**Query Language:** PromQL  
**Retention:** 15 dias / 10 GB
