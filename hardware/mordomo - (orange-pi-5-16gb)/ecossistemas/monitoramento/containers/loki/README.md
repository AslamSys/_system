# 📝 Loki

**Container:** `loki`  
**Ecossistema:** Monitoramento  
**Papel:** Log Aggregation & Querying

---

## 📋 Propósito

Sistema de agregação de logs otimizado para armazenar e consultar logs de todos os containers com integração Grafana.

---

## 🎯 Responsabilidades

- ✅ Receber logs via Promtail (agent)
- ✅ Indexar por labels (não conteúdo)
- ✅ Armazenar logs comprimidos
- ✅ Query via LogQL
- ✅ Integração com Grafana
- ✅ Alertas baseados em logs

---

## 🔧 Tecnologias

**Grafana Loki** v2.9+
- Log aggregation system
- Label-based indexing
- LogQL query language
- Promtail (log shipper)
- Compressão eficiente

**Imagens:**
- `grafana/loki:2.9.0`
- `grafana/promtail:2.9.0`

---

## 📊 Especificações

```yaml
Performance:
  CPU: 5-15%
  RAM: 200-500 MB
  Storage: 2-10 GB (compressed)
  
Ingestion:
  Rate: 1MB/s (pico)
  Batch Size: 1MB
  Timeout: 10s
  
Retention:
  Time: 30 dias
  Compaction: Diária
  
Query:
  Max Range: 24h (recomendado)
  Parallelism: 10
```

---

## ⚙️ Configuração Loki

```yaml
# loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    cache_ttl: 24h
    shared_store: filesystem
  
  filesystem:
    directory: /loki/chunks

compactor:
  working_directory: /loki/boltdb-shipper-compactor
  shared_store: filesystem
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  retention_delete_worker_count: 150

limits_config:
  retention_period: 720h  # 30 dias
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h  # 7 dias
  max_query_length: 721h
  max_query_parallelism: 10
  max_streams_per_user: 10000
  max_global_streams_per_user: 50000

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h

ruler:
  storage:
    type: local
    local:
      directory: /loki/rules
  rule_path: /loki/rules-temp
  alertmanager_url: http://alertmanager:9093
  ring:
    kvstore:
      store: inmemory
  enable_api: true
```

---

## 📤 Promtail Configuration

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Docker containers
  - job_name: containers
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    
    relabel_configs:
      # Container name
      - source_labels: ['__meta_docker_container_name']
        target_label: 'container'
        regex: '/(.*)'
      
      # Container image
      - source_labels: ['__meta_docker_container_image']
        target_label: 'image'
      
      # Docker labels como Loki labels
      - source_labels: ['__meta_docker_container_label_com_docker_compose_service']
        target_label: 'service'
    
    pipeline_stages:
      # Parse JSON logs
      - json:
          expressions:
            level: level
            message: message
            timestamp: timestamp
            source: source
      
      # Extract level
      - labels:
          level:
          source:
      
      # Parse timestamp
      - timestamp:
          source: timestamp
          format: RFC3339Nano
      
      # Output apenas message
      - output:
          source: message

  # System logs (opcional)
  - job_name: syslog
    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          __path__: /var/log/syslog

  # Application logs (arquivos específicos)
  - job_name: mordomo
    static_configs:
      - targets:
          - localhost
        labels:
          job: mordomo
          __path__: /var/log/mordomo/*.log
    
    pipeline_stages:
      # Parse formato customizado
      - regex:
          expression: '^\[(?P<timestamp>.*?)\] \[(?P<level>.*?)\] \[(?P<source>.*?)\] (?P<message>.*)'
      
      - labels:
          level:
          source:
      
      - timestamp:
          source: timestamp
          format: '2006-01-02 15:04:05'
```

---

## 🐳 Docker

```yaml
# docker-compose.yml
loki:
  image: grafana/loki:2.9.0
  container_name: loki
  ports:
    - "3100:3100"
  volumes:
    - ./config/loki-config.yaml:/etc/loki/loki-config.yaml
    - loki-data:/loki
  command: -config.file=/etc/loki/loki-config.yaml
  networks:
    - mordomo-net
  restart: unless-stopped

promtail:
  image: grafana/promtail:2.9.0
  container_name: promtail
  ports:
    - "9080:9080"
  volumes:
    - ./config/promtail-config.yaml:/etc/promtail/config.yaml
    - /var/log:/var/log:ro
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - promtail-positions:/tmp
  command: -config.file=/etc/promtail/config.yaml
  networks:
    - mordomo-net
  depends_on:
    - loki
  restart: unless-stopped

volumes:
  loki-data:
  promtail-positions:
```

---

## 🔍 LogQL Queries

### Basic Queries
```logql
# Todos logs de um container
{container="mordomo-core-api"}

# Logs por level
{container="whisper-asr", level="ERROR"}

# Múltiplos containers
{container=~"whisper-asr|speaker-verification"}

# Regex no conteúdo
{container="mordomo-brain"} |= "exception"

# Negação
{container="postgres"} != "checkpoint"

# Case insensitive
{container="tts-engine"} |~ "(?i)error"
```

### Filters & Parsing
```logql
# Parse JSON
{container="mordomo-core-api"} | json

# Parse fields específicos
{container="mordomo-core-api"} 
  | json 
  | latency_ms > 1000

# Label filter
{container="whisper-asr"} 
  | json 
  | model="whisper-medium"

# Line format
{container="mordomo-brain"} 
  | json 
  | line_format "{{.timestamp}} - {{.message}}"
```

### Aggregations
```logql
# Count logs por segundo
rate({container="whisper-asr"}[1m])

# Total de erros
count_over_time({level="ERROR"}[5m])

# Latência média (se estiver no log)
avg_over_time({container="core-api"} 
  | json 
  | unwrap latency_ms [5m])

# P95 latência
quantile_over_time(0.95, {container="whisper-asr"} 
  | json 
  | unwrap duration_ms [5m])

# Logs agrupados
sum by (container) (rate({job="containers"}[1m]))

# Top 5 containers com mais erros
topk(5, sum by (container) (
  count_over_time({level="ERROR"}[1h])
))
```

### Patterns
```logql
# Buscar padrão
{container="mordomo-brain"} 
  |= `User "` 
  | regexp `User "(?P<user>.*?)"`

# Extract IP
{container="core-api"} 
  | regexp `(?P<ip>\d+\.\d+\.\d+\.\d+)`

# Extract valores numéricos
{container="whisper-asr"} 
  | regexp `latency: (?P<latency>\d+)ms` 
  | latency > 1000
```

---

## 🚨 Alert Rules

```yaml
# rules/loki_alerts.yml
groups:
  - name: loki_alerts
    interval: 1m
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          sum by (container) (
            rate({level="ERROR"}[5m])
          ) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate in {{ $labels.container }}"
          description: "Error rate > 0.1/s for 2 minutes"
      
      # Exceptions in Brain
      - alert: BrainException
        expr: |
          count_over_time({container="mordomo-brain"} 
            |= "exception" [5m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "Exception detected in Brain"
          description: "Brain container logged exceptions"
      
      # High latency logs
      - alert: HighLatencyLogs
        expr: |
          count_over_time({container="whisper-asr"} 
            |= "latency" 
            | regexp `latency: (?P<latency>\d+)` 
            | latency > 3000 [5m]) > 10
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected in Whisper ASR"
          description: "> 10 requests with latency > 3s in 5 minutes"
      
      # Container not logging
      - alert: ContainerNotLogging
        expr: |
          absent_over_time({container="mordomo-core-api"}[10m])
        labels:
          severity: warning
        annotations:
          summary: "Core API not producing logs"
          description: "No logs from Core API for 10 minutes"
```

---

## 🔌 HTTP API

```bash
# Query logs
curl -G -s "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={container="whisper-asr"}' \
  --data-urlencode 'limit=10'

# Query range
curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={container="mordomo-brain"}' \
  --data-urlencode 'start=1700000000' \
  --data-urlencode 'end=1700100000'

# Labels
curl "http://localhost:3100/loki/api/v1/labels"

# Label values
curl "http://localhost:3100/loki/api/v1/label/container/values"

# Tail (streaming)
curl -s "http://localhost:3100/loki/api/v1/tail?query={container=\"core-api\"}"
```

---

## 🧪 Testes

```python
# test_loki.py
import requests
import time

def test_loki_ready():
    response = requests.get('http://localhost:3100/ready')
    assert response.status_code == 200

def test_push_logs():
    # Push log via API
    log_entry = {
        "streams": [
            {
                "stream": {
                    "container": "test",
                    "level": "INFO"
                },
                "values": [
                    [str(int(time.time() * 1e9)), "Test log message"]
                ]
            }
        ]
    }
    
    response = requests.post(
        'http://localhost:3100/loki/api/v1/push',
        json=log_entry
    )
    assert response.status_code == 204

def test_query_logs():
    query = '{container="whisper-asr"}'
    
    response = requests.get(
        'http://localhost:3100/loki/api/v1/query',
        params={'query': query, 'limit': 10}
    )
    
    data = response.json()
    assert data['status'] == 'success'

def test_labels():
    response = requests.get('http://localhost:3100/loki/api/v1/labels')
    data = response.json()
    
    assert 'container' in data['data']
    assert 'level' in data['data']
```

---

## 📊 Python Client

```python
# loki_client.py
import requests
import time
import json

class LokiClient:
    def __init__(self, url="http://localhost:3100"):
        self.url = url
    
    def push(self, labels: dict, message: str):
        """Push log para Loki"""
        payload = {
            "streams": [
                {
                    "stream": labels,
                    "values": [
                        [str(int(time.time() * 1e9)), message]
                    ]
                }
            ]
        }
        
        requests.post(f"{self.url}/loki/api/v1/push", json=payload)
    
    def query(self, logql: str, limit: int = 100):
        """Query logs"""
        response = requests.get(
            f"{self.url}/loki/api/v1/query",
            params={'query': logql, 'limit': limit}
        )
        
        return response.json()['data']['result']
    
    def tail(self, logql: str, callback):
        """Stream logs em tempo real"""
        import sseclient
        
        response = requests.get(
            f"{self.url}/loki/api/v1/tail",
            params={'query': logql},
            stream=True
        )
        
        client = sseclient.SSEClient(response)
        for event in client.events():
            callback(json.loads(event.data))

# Uso
loki = LokiClient()

# Push log
loki.push(
    labels={"container": "my-app", "level": "INFO"},
    message="Application started"
)

# Query
results = loki.query('{container="whisper-asr", level="ERROR"}')
for result in results:
    print(result['values'])

# Tail
def print_log(log):
    print(log['streams'][0]['values'][0][1])

loki.tail('{container="core-api"}', print_log)
```

---

## 🔧 Troubleshooting

### Logs não aparecem
```bash
# Verificar Promtail
docker logs promtail

# Testar push manual
curl -X POST "http://localhost:3100/loki/api/v1/push" \
  -H "Content-Type: application/json" \
  -d '{
    "streams": [
      {
        "stream": {"container": "test"},
        "values": [["'$(date +%s%N)'", "test message"]]
      }
    ]
  }'
```

### Query lenta
```yaml
# Reduzir time range
# ❌ Lento
{container="core-api"} [7d]

# ✅ Rápido
{container="core-api"} [1h]

# Aumentar paralelismo
limits_config:
  max_query_parallelism: 20
```

### Disco cheio
```yaml
# Reduzir retention
retention_period: 168h  # 7 dias

# Compactar mais frequentemente
compaction_interval: 5m
```

---

## 🔗 Integração

**Recebe de:**
- Promtail (Docker containers logs)
- Aplicações (via HTTP push)

**Exporta para:**
- Grafana (visualização, Explore)
- Alertmanager (alertas baseados em logs)

**Monitora:** Prometheus (métricas do próprio Loki)

---

## 📚 LogQL Cheat Sheet

```logql
# Operators
|=    # Line contains
!=    # Line doesn't contain
|~    # Regex match
!~    # Regex doesn't match

# Filters
| json                      # Parse JSON
| logfmt                    # Parse logfmt
| regexp "pattern"          # Extract with regex
| line_format "{{.field}}"  # Format output
| label_format new=old      # Rename label

# Aggregations
rate()                      # Rate per second
count_over_time()          # Count logs
sum()                      # Sum values
avg()                      # Average
max/min()                  # Max/Min
quantile_over_time()       # Percentile

# Grouping
by (label)                 # Group by label
without (label)            # Group without label
```

---

**Versão:** 1.0  
**Última atualização:** 27/11/2025  
**Query Language:** LogQL  
**Retention:** 30 dias  
**Shipper:** Promtail
