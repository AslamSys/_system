# 📊 Grafana

**Container:** `grafana`  
**Ecossistema:** Monitoramento  
**Papel:** Visualization & Dashboards

---

## 📋 Propósito

Plataforma de visualização unificada para métricas (Prometheus) e logs (Loki) com dashboards interativos e alertas.

---

## 🎯 Responsabilidades

- ✅ Dashboards customizados
- ✅ Visualização de métricas e logs
- ✅ Alertas visuais
- ✅ Explore (ad-hoc queries)
- ✅ User management
- ✅ Plugins e integrações

---

## 🔧 Tecnologias

**Grafana** v10.2+
- Dashboards as code (JSON)
- Multi-datasource (Prometheus, Loki)
- Alerting engine
- Variables & templates
- Plugins ecosystem
- RBAC

**Imagem:** `grafana/grafana:10.2.0`

---

## 📊 Especificações

```yaml
Performance:
  CPU: 5-10%
  RAM: 100-300 MB
  Storage: 100 MB - 1 GB (configs + dashboards)
  
Users:
  Max: 50 (concurrent)
  RBAC: Sim
  SSO: Suportado
  
Dashboards:
  Count: ~10-20
  Refresh: 5s - 1m
  Retention: Infinito (JSON)
```

---

## ⚙️ Configuração

```ini
# grafana.ini
[server]
protocol = http
http_port = 3000
domain = localhost
root_url = %(protocol)s://%(domain)s:%(http_port)s/

[database]
type = sqlite3
path = /var/lib/grafana/grafana.db

[security]
admin_user = admin
admin_password = ${GF_SECURITY_ADMIN_PASSWORD}
allow_embedding = true
cookie_samesite = lax

[auth]
disable_login_form = false

[auth.anonymous]
enabled = false

[auth.basic]
enabled = true

[users]
allow_sign_up = false
default_theme = dark

[analytics]
reporting_enabled = false
check_for_updates = false

[alerting]
enabled = true
execute_alerts = true

[log]
mode = console
level = info

[metrics]
enabled = true
interval_seconds = 10

[panels]
disable_sanitize_html = false

[plugins]
enable_alpha = false
```

---

## 📊 Datasources

```yaml
# provisioning/datasources/datasources.yaml
apiVersion: 1

datasources:
  # Prometheus
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: 15s
      queryTimeout: 60s
      httpMethod: POST
  
  # Loki
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
    jsonData:
      maxLines: 1000
      derivedFields:
        - datasourceUid: Prometheus
          matcherRegex: "trace_id=(\\w+)"
          name: TraceID
          url: "$${__value.raw}"
```

---

## 📊 Dashboards

### 1. Mordomo Overview
```json
{
  "dashboard": {
    "title": "Mordomo Overview",
    "panels": [
      {
        "title": "Conversations per Minute",
        "targets": [
          {
            "expr": "rate(conversations_total[5m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Pipeline Latency (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(conversation_latency_seconds_bucket[5m]))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Service Status",
        "targets": [
          {
            "expr": "up"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

### 2. Audio Pipeline
```json
{
  "title": "Audio Pipeline",
  "panels": [
    {
      "title": "Wake Word Detection Rate",
      "targets": [{"expr": "rate(wake_word_detected_total[5m])"}]
    },
    {
      "title": "Speaker Verification Success",
      "targets": [{
        "expr": "rate(speaker_verification_success_total[5m]) / rate(speaker_verification_attempts_total[5m])"
      }]
    },
    {
      "title": "Whisper ASR Latency",
      "targets": [{
        "expr": "histogram_quantile(0.95, rate(whisper_transcription_duration_seconds_bucket[5m]))"
      }]
    }
  ]
}
```

### 3. Brain Performance
```json
{
  "title": "Brain (LLM)",
  "panels": [
    {
      "title": "Tokens/sec",
      "targets": [{"expr": "rate(brain_tokens_used_total[5m])"}]
    },
    {
      "title": "Inference Time P95",
      "targets": [{
        "expr": "histogram_quantile(0.95, rate(brain_inference_duration_seconds_bucket[5m]))"
      }]
    },
    {
      "title": "Intent Distribution",
      "targets": [{
        "expr": "sum by (intent) (rate(brain_intents_detected_total[5m]))"
      }]
    }
  ]
}
```

### 4. Infrastructure
```json
{
  "title": "Infrastructure",
  "panels": [
    {
      "title": "NATS Messages/sec",
      "targets": [{"expr": "rate(nats_core_messages_in_total[5m])"}]
    },
    {
      "title": "PostgreSQL Connections",
      "targets": [{"expr": "pg_stat_database_numbackends"}]
    },
    {
      "title": "Qdrant Search Latency",
      "targets": [{
        "expr": "histogram_quantile(0.95, rate(qdrant_search_duration_seconds_bucket[5m]))"
      }]
    }
  ]
}
```

### 5. Logs Explorer
```json
{
  "title": "Logs",
  "panels": [
    {
      "title": "Error Logs",
      "targets": [{
        "expr": "{level=\"ERROR\"}"
      }],
      "datasource": "Loki",
      "type": "logs"
    },
    {
      "title": "Log Rate by Container",
      "targets": [{
        "expr": "sum by (container) (rate({job=\"containers\"}[1m]))"
      }],
      "datasource": "Loki"
    }
  ]
}
```

---

## 🐳 Docker

```dockerfile
FROM grafana/grafana:10.2.0

# Provisioning (datasources, dashboards)
COPY provisioning/ /etc/grafana/provisioning/

# Custom config
COPY grafana.ini /etc/grafana/grafana.ini

# Dashboards JSON
COPY dashboards/ /var/lib/grafana/dashboards/

# Plugins (opcional)
# RUN grafana-cli plugins install grafana-piechart-panel

EXPOSE 3000

USER grafana
```

### Docker Compose
```yaml
grafana:
  image: grafana/grafana:10.2.0
  container_name: grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
    - GF_INSTALL_PLUGINS=grafana-piechart-panel
  volumes:
    - ./config/grafana.ini:/etc/grafana/grafana.ini
    - ./provisioning:/etc/grafana/provisioning
    - ./dashboards:/var/lib/grafana/dashboards
    - grafana-data:/var/lib/grafana
  networks:
    - mordomo-net
  depends_on:
    - prometheus
    - loki
  restart: unless-stopped

volumes:
  grafana-data:
```

---

## 📁 Provisioning Structure

```
provisioning/
├── datasources/
│   └── datasources.yaml
├── dashboards/
│   └── dashboard-provider.yaml
├── notifiers/
│   └── notifiers.yaml
└── plugins/
    └── plugins.yaml

dashboards/
├── overview.json
├── audio-pipeline.json
├── brain.json
├── infrastructure.json
└── logs.json
```

### Dashboard Provider
```yaml
# provisioning/dashboards/dashboard-provider.yaml
apiVersion: 1

providers:
  - name: 'Mordomo Dashboards'
    orgId: 1
    folder: 'Mordomo'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

---

## 🚨 Alertas

```json
{
  "alert": {
    "name": "High Error Rate",
    "conditions": [
      {
        "evaluator": {
          "type": "gt",
          "params": [10]
        },
        "operator": {
          "type": "and"
        },
        "query": {
          "params": ["A", "5m", "now"]
        },
        "type": "query"
      }
    ],
    "executionErrorState": "alerting",
    "for": "5m",
    "frequency": "1m",
    "handler": 1,
    "message": "Error rate > 10/s for 5 minutes",
    "name": "High Error Rate",
    "noDataState": "no_data",
    "notifications": [
      {
        "uid": "webhook-notification"
      }
    ]
  }
}
```

### Notification Channels
```yaml
# provisioning/notifiers/notifiers.yaml
notifiers:
  - name: Webhook
    type: webhook
    uid: webhook-notification
    org_id: 1
    is_default: true
    settings:
      url: http://mordomo-core-api:8000/webhooks/grafana-alerts
      httpMethod: POST
  
  # Slack (opcional)
  - name: Slack
    type: slack
    uid: slack-alerts
    org_id: 1
    settings:
      url: https://hooks.slack.com/services/XXX/YYY/ZZZ
      recipient: '#alerts'
```

---

## 🔌 HTTP API

```bash
# Health
curl http://localhost:3000/api/health

# Dashboards
curl -u admin:admin http://localhost:3000/api/dashboards/home

# Search dashboards
curl -u admin:admin http://localhost:3000/api/search

# Create dashboard
curl -u admin:admin -X POST \
  -H "Content-Type: application/json" \
  -d @dashboard.json \
  http://localhost:3000/api/dashboards/db

# Users
curl -u admin:admin http://localhost:3000/api/users

# Create API key
curl -u admin:admin -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"automation","role":"Admin"}' \
  http://localhost:3000/api/auth/keys
```

---

## 📊 Panel Types

```json
{
  "panels": [
    // Time series graph
    {
      "type": "timeseries",
      "title": "CPU Usage"
    },
    
    // Stat (single value)
    {
      "type": "stat",
      "title": "Total Users"
    },
    
    // Gauge
    {
      "type": "gauge",
      "title": "Memory Usage %"
    },
    
    // Table
    {
      "type": "table",
      "title": "Top Services"
    },
    
    // Logs panel
    {
      "type": "logs",
      "datasource": "Loki",
      "title": "Recent Errors"
    },
    
    // Heatmap
    {
      "type": "heatmap",
      "title": "Latency Distribution"
    },
    
    // Pie chart
    {
      "type": "piechart",
      "title": "Intent Distribution"
    }
  ]
}
```

---

## 🎨 Variables

```json
{
  "templating": {
    "list": [
      {
        "name": "container",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(up, job)",
        "refresh": 1,
        "multi": true,
        "includeAll": true
      },
      {
        "name": "interval",
        "type": "interval",
        "query": "1m,5m,10m,30m,1h",
        "current": {
          "text": "5m",
          "value": "5m"
        }
      },
      {
        "name": "user",
        "type": "custom",
        "query": "user_1,user_2,user_3",
        "multi": false
      }
    ]
  }
}
```

---

## 🧪 Testes

```python
# test_grafana.py
import requests

GRAFANA_URL = "http://localhost:3000"
AUTH = ("admin", "admin")

def test_grafana_up():
    response = requests.get(f"{GRAFANA_URL}/api/health")
    assert response.status_code == 200
    assert response.json()['database'] == 'ok'

def test_datasources():
    response = requests.get(
        f"{GRAFANA_URL}/api/datasources",
        auth=AUTH
    )
    
    datasources = response.json()
    names = [ds['name'] for ds in datasources]
    
    assert 'Prometheus' in names
    assert 'Loki' in names

def test_dashboards():
    response = requests.get(
        f"{GRAFANA_URL}/api/search",
        auth=AUTH
    )
    
    dashboards = response.json()
    assert len(dashboards) > 0

def test_query_prometheus():
    # Testar query via Grafana
    query = {
        "queries": [
            {
                "refId": "A",
                "expr": "up",
                "datasource": {"type": "prometheus", "uid": "prometheus"}
            }
        ],
        "from": "now-1h",
        "to": "now"
    }
    
    response = requests.post(
        f"{GRAFANA_URL}/api/ds/query",
        auth=AUTH,
        json=query
    )
    
    assert response.status_code == 200
```

---

## 🔧 Troubleshooting

### Dashboard não carrega
```bash
# Verificar logs
docker logs grafana

# Verificar datasource
curl -u admin:admin http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=up

# Reload provisioning
docker restart grafana
```

### Query lenta
```ini
# Aumentar timeout
[dataproxy]
timeout = 120
```

### Permissões
```bash
# Corrigir ownership
chown -R 472:472 /var/lib/grafana
```

---

## 🌐 Web UI

Acesso: **http://localhost:3000**

**Login Padrão:**
- User: `admin`
- Password: `admin` (alterar no primeiro login)

**Principais Seções:**
- **Home**: Dashboards recentes
- **Dashboards**: Organização por pastas
- **Explore**: Ad-hoc queries (Prometheus/Loki)
- **Alerting**: Gerenciar alertas
- **Configuration**: Datasources, Users, Plugins

---

## 📚 Plugins

```bash
# Instalar plugin
grafana-cli plugins install grafana-piechart-panel

# Listar plugins instalados
grafana-cli plugins ls

# Atualizar plugin
grafana-cli plugins update grafana-piechart-panel

# Via Docker environment
environment:
  - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-clock-panel
```

**Plugins Úteis:**
- `grafana-piechart-panel` - Gráficos de pizza
- `grafana-worldmap-panel` - Mapas
- `grafana-clock-panel` - Relógio
- `grafana-simple-json-datasource` - JSON datasource

---

## 🔗 Integração

**Datasources:**
- Prometheus (métricas)
- Loki (logs)
- PostgreSQL (opcional - tabelas/relatórios)

**Notificações:**
- Webhook (Core API)
- Slack (opcional)
- Email (opcional)

**Expõe:**
- 3000: Web UI + API

**Monitora:** Próprio Grafana (self-monitoring via Prometheus)

---

## 📊 Dashboard as Code

```bash
# Exportar dashboard
curl -u admin:admin \
  http://localhost:3000/api/dashboards/uid/abc123 \
  | jq '.dashboard' > dashboard.json

# Importar dashboard
curl -u admin:admin -X POST \
  -H "Content-Type: application/json" \
  -d @dashboard.json \
  http://localhost:3000/api/dashboards/db
```

---

## 🚀 Best Practices

```yaml
Dashboards:
  - Use variables para reutilização
  - Organize em folders lógicos
  - Documente panels com descriptions
  - Use links entre dashboards
  - Versione JSONs no Git

Performance:
  - Limite time range (max 24h)
  - Use $__interval no step
  - Cache queries quando possível
  - Minimize panels por dashboard (<15)

Alertas:
  - Test alerts antes de produção
  - Use for: para evitar flapping
  - Configure notification routing
  - Document alert conditions
```

---

## 📱 Mobile App

Grafana tem app mobile (iOS/Android):
- Ver dashboards
- Receber notificações de alertas
- Explore queries básicas

---

**Versão:** 1.0  
**Última atualização:** 27/11/2025  
**Login:** admin/admin (alterar!)  
**Datasources:** Prometheus, Loki  
**Dashboards:** Mordomo (Overview, Pipeline, Brain, Infra, Logs)
