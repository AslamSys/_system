# 🔍 Consul (Infraestrutura)

**Container:** `consul`  
**Ecossistema:** Infraestrutura  
**Papel:** Service Discovery & Configuration

---

## 📋 Propósito

Consul cluster para service registry, health monitoring, KV store e service mesh em produção.

---

## 🎯 Responsabilidades

- ✅ Service registry distribuído
- ✅ Health checking automático
- ✅ DNS-based service discovery
- ✅ Distributed KV store (RAFT)
- ✅ Service mesh (Connect)
- ✅ Multi-datacenter federation

---

## 🔧 Tecnologias

**HashiCorp Consul** v1.17+
- Service catalog
- Health checks (HTTP, TCP, gRPC, Docker)
- KV store (512KB/key)
- DNS & HTTP API
- Consul Connect (service mesh)
- Web UI

**Imagem:** `hashicorp/consul:1.17`

---

## 📊 Especificações

```yaml
Cluster (3 servers + N clients):
  Servers:
    CPU: 10-15% cada
    RAM: 200-500 MB cada
    Storage: 1-5 GB (raft)
  
  Clients:
    CPU: 5-10%
    RAM: 50-100 MB
  
Performance:
  KV Reads: 50K ops/s
  KV Writes: 10K ops/s
  Service Queries: 100K ops/s
  Latency: < 10ms (local)
  
Limits:
  Max Services: 10K
  Max Nodes: 5K
  Max KV Keys: 100K
  KV Value Size: 512 KB
```

---

## 🏗️ Cluster Architecture

```
╔══════════════════════════════════════════════════════╗
║               Consul Cluster (RAFT)                  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ ║
║  │  Server 1   │←→│  Server 2   │←→│  Server 3   │ ║
║  │   (Leader)  │  │  (Follower) │  │  (Follower) │ ║
║  └─────────────┘  └─────────────┘  └─────────────┘ ║
║         ↑                ↑                ↑          ║
╠═════════╪════════════════╪════════════════╪═════════╣
║  ┌──────┴──┐      ┌──────┴──┐      ┌──────┴──┐     ║
║  │ Client  │      │ Client  │      │ Client  │     ║
║  │ Agent 1 │      │ Agent 2 │      │ Agent 3 │     ║
║  └─────────┘      └─────────┘      └─────────┘     ║
║       │                │                │           ║
║   Container        Container        Container      ║
║   Services         Services         Services       ║
╚═══════════════════════════════════════════════════════╝
```

---

## ⚙️ Server Configuration

### Consul Server 1 (Bootstrap)
```hcl
# consul-server-1.hcl
datacenter = "mordomo-dc1"
data_dir = "/consul/data"
log_level = "INFO"

# Server mode
server = true
bootstrap_expect = 3

# Networking
bind_addr = "0.0.0.0"
client_addr = "0.0.0.0"
advertise_addr = "172.20.0.10"

# Ports
ports {
  dns = 8600
  http = 8500
  https = -1
  grpc = 8502
  serf_lan = 8301
  serf_wan = 8302
  server = 8300
}

# Cluster join
retry_join = [
  "consul-server-2",
  "consul-server-3"
]

# UI
ui_config {
  enabled = true
  metrics_provider = "prometheus"
  metrics_proxy {
    base_url = "http://prometheus:9090"
  }
}

# Performance
performance {
  raft_multiplier = 1
}

# Autopilot (cluster health)
autopilot {
  cleanup_dead_servers = true
  last_contact_threshold = "200ms"
  max_trailing_logs = 250
}

# DNS
recursors = ["8.8.8.8", "8.8.4.4"]
dns_config {
  allow_stale = true
  max_stale = "5s"
  node_ttl = "30s"
  service_ttl = {
    "*" = "10s"
  }
}

# Telemetry
telemetry {
  prometheus_retention_time = "60s"
  disable_hostname = false
}

# ACL (Produção)
acl {
  enabled = true
  default_policy = "deny"
  enable_token_persistence = true
  tokens {
    initial_management = "bootstrap-token-secret"
  }
}
```

### Consul Servers 2 & 3
```hcl
# consul-server-2.hcl / consul-server-3.hcl
# Idêntico ao server-1, apenas mude:
advertise_addr = "172.20.0.11"  # ou 172.20.0.12

retry_join = [
  "consul-server-1",
  "consul-server-3"  # ou consul-server-2
]
```

---

## 🖥️ Client Configuration

```hcl
# consul-client.hcl
datacenter = "mordomo-dc1"
data_dir = "/consul/data"
log_level = "INFO"

# Client mode
server = false

bind_addr = "{{ GetInterfaceIP \"eth0\" }}"
client_addr = "0.0.0.0"

# Join cluster
retry_join = [
  "consul-server-1",
  "consul-server-2",
  "consul-server-3"
]

# Service registration
services = [
  {
    name = "whisper-asr"
    tags = ["asr", "stt", "ml"]
    port = 50051
    
    checks = [
      {
        name = "gRPC Health"
        grpc = "localhost:50051"
        interval = "10s"
        timeout = "5s"
      }
    ]
    
    meta = {
      version = "1.0"
      model = "whisper-medium"
    }
  }
]

# Telemetry
telemetry {
  prometheus_retention_time = "60s"
}
```

---

## 🐳 Docker Compose (Cluster)

```yaml
version: '3.8'

services:
  consul-server-1:
    image: hashicorp/consul:1.17
    container_name: consul-server-1
    hostname: consul-server-1
    ports:
      - "8500:8500"  # HTTP API + UI
      - "8600:8600/udp"  # DNS
    volumes:
      - ./config/consul-server-1.hcl:/consul/config/consul.hcl
      - consul-server-1-data:/consul/data
    command: agent -config-file=/consul/config/consul.hcl
    networks:
      mordomo-net:
        ipv4_address: 172.20.0.10
    restart: unless-stopped

  consul-server-2:
    image: hashicorp/consul:1.17
    container_name: consul-server-2
    hostname: consul-server-2
    ports:
      - "8501:8500"
      - "8601:8600/udp"
    volumes:
      - ./config/consul-server-2.hcl:/consul/config/consul.hcl
      - consul-server-2-data:/consul/data
    command: agent -config-file=/consul/config/consul.hcl
    networks:
      mordomo-net:
        ipv4_address: 172.20.0.11
    depends_on:
      - consul-server-1
    restart: unless-stopped

  consul-server-3:
    image: hashicorp/consul:1.17
    container_name: consul-server-3
    hostname: consul-server-3
    ports:
      - "8502:8500"
      - "8602:8600/udp"
    volumes:
      - ./config/consul-server-3.hcl:/consul/config/consul.hcl
      - consul-server-3-data:/consul/data
    command: agent -config-file=/consul/config/consul.hcl
    networks:
      mordomo-net:
        ipv4_address: 172.20.0.12
    depends_on:
      - consul-server-1
    restart: unless-stopped

volumes:
  consul-server-1-data:
  consul-server-2-data:
  consul-server-3-data:

networks:
  mordomo-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## 🔑 ACL Setup (Produção)

```bash
# 1. Bootstrap ACL system
consul acl bootstrap
# Retorna: Initial Management Token

# 2. Criar policy para serviços
consul acl policy create \
  -name "service-policy" \
  -description "Policy for Mordomo services" \
  -rules @service-policy.hcl

# service-policy.hcl:
service_prefix "" {
  policy = "write"
}
node_prefix "" {
  policy = "write"
}
key_prefix "" {
  policy = "write"
}

# 3. Criar token para serviços
consul acl token create \
  -description "Token for Mordomo services" \
  -policy-name "service-policy"
```

---

## 📈 Service Registration

### Via Config File
```hcl
services {
  name = "mordomo-core-api"
  id = "core-api-1"
  port = 8000
  tags = ["api", "http", "v1"]
  
  meta = {
    version = "1.0.0"
    env = "production"
  }
  
  checks = [
    {
      name = "HTTP Health"
      http = "http://localhost:8000/health"
      interval = "10s"
      timeout = "2s"
    },
    {
      name = "Critical Memory"
      script = "test $(free -m | awk '/^Mem:/{print $3}') -lt 3000"
      interval = "30s"
    }
  ]
}
```

### Via HTTP API
```bash
curl -X PUT http://localhost:8500/v1/agent/service/register \
  -d '{
    "ID": "whisper-asr-1",
    "Name": "whisper-asr",
    "Tags": ["ml", "stt"],
    "Address": "172.20.0.50",
    "Port": 50051,
    "Meta": {
      "version": "1.0",
      "model": "whisper-medium"
    },
    "Check": {
      "GRPC": "172.20.0.50:50051",
      "Interval": "10s",
      "Timeout": "5s"
    }
  }'
```

---

## 🗄️ KV Store

```bash
# Criar chaves
consul kv put config/mordomo/brain/model "qwen2.5:3b"
consul kv put config/mordomo/tts/voice "pt_BR-faber-medium"
consul kv put config/mordomo/wake_word/sensitivity "0.7"

# Ler
consul kv get config/mordomo/brain/model

# Listar
consul kv get -recurse config/mordomo/

# Watch (bloqueia até mudança)
consul watch -type=key -key=config/mordomo/brain/model \
  bash -c 'echo "Model changed to: $(consul kv get config/mordomo/brain/model)"'

# Delete
consul kv delete config/mordomo/brain/model
```

### KV em Python
```python
import consul

c = consul.Consul(host='consul-server-1', port=8500)

# Escrever
c.kv.put('config/brain/temperature', '0.7')

# Ler
index, data = c.kv.get('config/brain/temperature')
temperature = float(data['Value'].decode('utf-8'))

# Watch (blocking)
last_index = None
while True:
    index, data = c.kv.get('config/brain/model', index=last_index)
    if data:
        print(f"Model changed: {data['Value'].decode('utf-8')}")
        last_index = index
```

---

## 🧪 Health Checks

### Tipos Suportados
```hcl
# HTTP
checks = [
  {
    http = "http://localhost:8000/health"
    interval = "10s"
    timeout = "2s"
  }
]

# TCP
checks = [
  {
    tcp = "localhost:5432"
    interval = "15s"
  }
]

# gRPC
checks = [
  {
    grpc = "localhost:50051"
    grpc_use_tls = false
    interval = "10s"
  }
]

# Script
checks = [
  {
    args = ["/usr/local/bin/health-check.sh"]
    interval = "30s"
  }
]

# TTL (app reporta)
checks = [
  {
    ttl = "30s"
    deregister_critical_service_after = "90s"
  }
]

# Docker
checks = [
  {
    docker_container_id = "container-id"
    shell = "/bin/bash"
    args = ["curl", "-f", "http://localhost/health"]
    interval = "10s"
  }
]
```

---

## 📊 Métricas

```python
# Prometheus metrics via /v1/agent/metrics?format=prometheus

# Cluster
consul_raft_leader{datacenter}
consul_raft_peers
consul_serf_member_status{member}

# Services
consul_catalog_services
consul_catalog_service_node_healthy{service}

# KV
consul_kvs_apply
consul_kvs_get

# HTTP API
consul_http_request{method,path}
consul_http_request_duration_seconds
```

---

## 🧪 Testes

```bash
# Cluster status
consul members
consul operator raft list-peers

# Leader election
consul info | grep leader

# Service discovery
consul catalog services
consul catalog service whisper-asr

# Health
consul watch -type=checks -service=whisper-asr

# KV
consul kv get -recurse config/

# DNS
dig @localhost -p 8600 whisper-asr.service.consul
dig @localhost -p 8600 whisper-asr.service.consul SRV
```

---

## 🔧 Troubleshooting

### Split Brain
```bash
# Verificar peers
consul operator raft list-peers

# Se necessário, remover peer problemático
consul operator raft remove-peer -address="172.20.0.11:8300"
```

### Service não aparece
```bash
# Verificar logs
consul monitor -log-level=debug

# Recarregar config
consul reload

# Forçar re-sync
consul catalog register -
```

### KV lento
```bash
# Compactar raft log
consul snapshot save backup.snap
consul snapshot restore backup.snap
```

---

## 🌐 Web UI

Acesso: **http://localhost:8500/ui**

**Features:**
- Service catalog com health status
- Node topology
- KV browser (CRUD)
- Intentions (service mesh ACLs)
- ACL management

---

## 📚 CLI Avançado

```bash
# Cluster
consul members -detailed
consul operator raft list-peers
consul operator autopilot get-config

# Services
consul catalog services -tags
consul catalog service whisper-asr -detailed
consul watch -type=service -service=whisper-asr

# KV
consul kv export config/ > backup.json
consul kv import @backup.json

# Snapshot
consul snapshot save backup-$(date +%Y%m%d).snap
consul snapshot inspect backup.snap
```

---

## 🚨 Backup & Restore

```bash
# Snapshot (inclui services, KV, ACLs)
consul snapshot save backup.snap

# Verificar snapshot
consul snapshot inspect backup.snap

# Restore
consul snapshot restore backup.snap

# Automated backup (cron)
0 2 * * * consul snapshot save /backup/consul-$(date +\%Y\%m\%d).snap
```

---

## 🔗 Integração

**Usado por:**
- Discovery Service (wrapper)
- Todos containers (auto-registration)
- Prometheus (service discovery)
- Core API (config KV)

**Expõe:**
- 8500: HTTP API + UI
- 8600: DNS
- 8502: gRPC

**Monitora:** Prometheus, Grafana

---

**Versão:** 1.0  
**Última atualização:** 27/11/2025  
**Nota:** Este é o único service discovery do sistema - usado por todos os ecossistemas
