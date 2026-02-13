# 🚀 NATS Server (Infraestrutura)

**Container:** `nats`  
**Ecossistema:** Infraestrutura  
**Papel:** Message Broker Principal

---

## 📋 Propósito

Servidor NATS central com configurações avançadas de cluster, persistência JetStream e monitoramento para produção.

---

## 🎯 Responsabilidades

- ✅ Message broker de alta performance
- ✅ JetStream para persistência
- ✅ Clustering multi-node (HA)
- ✅ Autenticação e autorização
- ✅ Monitoring e observabilidade
- ✅ Key-Value e Object Store

---

## 🔧 Tecnologias

**NATS Server** v2.10+
- Core messaging (Pub/Sub, Request/Reply)
- JetStream (streams, consumers, KV)
- Clustering (RAFT consensus)
- Leaf Nodes (federação)
- Super Cluster (geo-distribuição)

**Imagem:** `nats:2.10-alpine`

---

## 📊 Especificações

```yaml
Cluster (3 nodes):
  CPU: 10-20% por node
  RAM: 100-200 MB por node
  Storage: 1-5 GB (JetStream)
  
Performance:
  Messages/sec: > 10M
  Latency: < 1ms (intra-cluster)
  Max Connections: 100K
  Max Subscriptions: ilimitado
  
JetStream:
  Max Storage: 10 GB
  Retention: 30 dias
  Replicas: 3 (quorum)
  Sync Replication: true
```

---

## 🔌 Clustering

### 3-Node Cluster
```
nats-1 (seed)  ←→  nats-2  ←→  nats-3
   ↓                 ↓            ↓
Clients         Clients      Clients
```

### Configuração NATS 1
```conf
# nats-1.conf
server_name: nats-1
port: 4222
http_port: 8222

# Cluster
cluster {
  name: mordomo-cluster
  listen: 0.0.0.0:6222
  
  # Seed node
  routes = [
    nats-route://nats-2:6222
    nats-route://nats-3:6222
  ]
}

# JetStream
jetstream {
  store_dir: "/data/jetstream"
  max_memory_store: 1GB
  max_file_store: 10GB
  
  # Cluster config
  domain: "mordomo"
}

# Auth
authorization {
  users = [
    {
      user: "admin"
      password: "$2a$11$..." # bcrypt hash
      permissions: {
        publish: [">"]
        subscribe: [">"]
      }
    },
    {
      user: "mordomo"
      password: "$2a$11$..."
      permissions: {
        publish: ["audio.>", "brain.>", "tts.>", "discovery.>"]
        subscribe: ["audio.>", "brain.>", "tts.>", "discovery.>"]
      }
    }
  ]
}

# Limits
max_payload: 2MB
max_connections: 10000
max_subscriptions: 0

# Logging
debug: false
trace: false
logtime: true
log_file: "/logs/nats-1.log"
```

### Configuração NATS 2 & 3
```conf
# nats-2.conf / nats-3.conf
server_name: nats-2  # ou nats-3
port: 4222
http_port: 8222

cluster {
  name: mordomo-cluster
  listen: 0.0.0.0:6222
  
  routes = [
    nats-route://nats-1:6222
    nats-route://nats-3:6222  # ou nats-2
  ]
}

# ... resto igual ao nats-1
```

---

## 🗄️ JetStream Configuration

### Streams de Produção
```bash
# Audio Stream (alta frequência, baixa retenção)
nats stream add AUDIO \
  --subjects "audio.>" \
  --storage file \
  --replicas 3 \
  --max-age 1h \
  --max-msgs 100000 \
  --discard old \
  --retention limits

# Brain Stream (workqueue, processamento único)
nats stream add BRAIN \
  --subjects "brain.>" \
  --storage file \
  --replicas 3 \
  --max-age 24h \
  --max-msgs 10000 \
  --retention work \
  --discard old

# TTS Stream
nats stream add TTS \
  --subjects "tts.>" \
  --storage file \
  --replicas 3 \
  --max-age 1h \
  --max-msgs 50000 \
  --retention limits

# Logs Stream (longa retenção)
nats stream add LOGS \
  --subjects "logs.>" \
  --storage file \
  --replicas 3 \
  --max-age 30d \
  --max-bytes 5GB \
  --retention limits

# Metrics Stream
nats stream add METRICS \
  --subjects "metrics.>" \
  --storage file \
  --replicas 3 \
  --max-age 7d \
  --max-msgs 1000000 \
  --retention limits
```

### Consumers
```bash
# Consumer para processamento de áudio
nats consumer add AUDIO audio-processor \
  --filter "audio.transcription" \
  --deliver all \
  --ack explicit \
  --max-deliver 3 \
  --wait 30s

# Consumer para actions do Brain
nats consumer add BRAIN brain-actions \
  --filter "brain.action.>" \
  --deliver new \
  --ack explicit \
  --max-deliver 5
```

---

## 🔑 Key-Value Stores

```bash
# Embeddings cache
nats kv add EMBEDDINGS \
  --replicas 3 \
  --ttl 24h \
  --history 5 \
  --max-value-size 100KB

# Conversation state
nats kv add CONVERSATIONS \
  --replicas 3 \
  --ttl 1h \
  --history 10 \
  --max-value-size 10KB

# System config
nats kv add CONFIG \
  --replicas 3 \
  --history 20 \
  --max-value-size 1KB

# User profiles
nats kv add USERS \
  --replicas 3 \
  --history 10 \
  --max-value-size 50KB
```

---

## 📈 Métricas Prometheus

```yaml
# /metrics endpoint expõe:

# Conexões
nats_core_connection_count{server_id}
nats_core_total_connections{server_id}
nats_core_routes{server_id}

# Mensagens
nats_core_messages_in_total{server_id}
nats_core_messages_out_total{server_id}
nats_core_messages_in_bytes_total{server_id}
nats_core_messages_out_bytes_total{server_id}

# JetStream
nats_jetstream_enabled{server_id}
nats_jetstream_server_store_used_bytes{server_id}
nats_jetstream_server_messages_total{server_id}
nats_jetstream_stream_messages_total{stream,server_id}
nats_jetstream_stream_bytes_total{stream,server_id}

# Cluster
nats_cluster_size
nats_cluster_leader{server_id}
```

---

## 🐳 Docker Compose (Cluster)

```yaml
version: '3.8'

services:
  nats-1:
    image: nats:2.10-alpine
    container_name: nats-1
    hostname: nats-1
    ports:
      - "4222:4222"
      - "6222:6222"
      - "8222:8222"
    volumes:
      - ./config/nats-1.conf:/etc/nats/nats.conf
      - nats-1-data:/data
      - nats-1-logs:/logs
    command: ["-c", "/etc/nats/nats.conf", "-js"]
    networks:
      - mordomo-net
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

  nats-2:
    image: nats:2.10-alpine
    container_name: nats-2
    hostname: nats-2
    ports:
      - "4223:4222"
      - "6223:6222"
      - "8223:8222"
    volumes:
      - ./config/nats-2.conf:/etc/nats/nats.conf
      - nats-2-data:/data
      - nats-2-logs:/logs
    command: ["-c", "/etc/nats/nats.conf", "-js"]
    networks:
      - mordomo-net
    depends_on:
      - nats-1
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

  nats-3:
    image: nats:2.10-alpine
    container_name: nats-3
    hostname: nats-3
    ports:
      - "4224:4222"
      - "6224:6222"
      - "8224:8222"
    volumes:
      - ./config/nats-3.conf:/etc/nats/nats.conf
      - nats-3-data:/data
      - nats-3-logs:/logs
    command: ["-c", "/etc/nats/nats.conf", "-js"]
    networks:
      - mordomo-net
    depends_on:
      - nats-1
      - nats-2
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

volumes:
  nats-1-data:
  nats-2-data:
  nats-3-data:
  nats-1-logs:
  nats-2-logs:
  nats-3-logs:

networks:
  mordomo-net:
    external: true
```

---

## 🔒 Autenticação

### Bcrypt Password Hash
```bash
# Gerar senha bcrypt
nats server passwd
# Insira a senha: mordomo123
# Output: $2a$11$xyz...

# Usar no config
user: "mordomo"
password: "$2a$11$xyz..."
```

### JWT (Produção)
```bash
# Instalar nsc
go install github.com/nats-io/nsc@latest

# Criar operator
nsc add operator MORDOMO

# Criar account
nsc add account SYSTEM

# Criar user
nsc add user MORDOMO_SERVICE

# Gerar seed
nsc describe jwt --account SYSTEM
```

---

## 🧪 Testes

### Cluster Health
```bash
# Verificar cluster status
nats server list

# Output:
╭─────────────────────────────────────────────────────╮
│                    Server Overview                  │
├────────┬─────────┬────────┬─────────┬──────────────┤
│ Name   │ Cluster │ Host   │ Version │ Connections  │
├────────┼─────────┼────────┼─────────┼──────────────┤
│ nats-1 │ mordomo │ 1.2.3  │ 2.10.0  │ 42          │
│ nats-2 │ mordomo │ 1.2.4  │ 2.10.0  │ 38          │
│ nats-3 │ mordomo │ 1.2.5  │ 2.10.0  │ 45          │
╰────────┴─────────┴────────┴─────────┴──────────────╯
```

### Failover Test
```bash
# Parar nats-1 (leader)
docker stop nats-1

# Verificar nova eleição
nats server list
# nats-2 ou nats-3 deve assumir como leader

# Reiniciar nats-1
docker start nats-1

# Verificar re-integração
nats server list
```

### Stream Replication
```bash
# Verificar replicas
nats stream info AUDIO

# Output:
Replicas: 3
  nats-1: current, seen 0.1s ago
  nats-2: current, seen 0.1s ago
  nats-3: current, seen 0.1s ago
```

---

## 🔧 Troubleshooting

### Split Brain
```bash
# Verificar rotas
nats server report jetstream

# Forçar re-sync (último recurso)
nats stream purge STREAM_NAME --force
```

### High Memory
```yaml
# Limitar JetStream
jetstream {
  max_memory_store: 512MB
  max_file_store: 5GB
}

# Configurar retenção agressiva
max_age: 1h
max_msgs: 10000
```

### Slow Consumers
```bash
# Identificar
curl http://localhost:8222/connz?subs=detail

# Configurar timeout
write_deadline: "10s"
```

---

## 📊 Dashboards

### NATS Surveyor (Web UI)
```yaml
nats-surveyor:
  image: natsio/nats-surveyor:latest
  ports:
    - "7777:7777"
  environment:
    NATS_SURVEYOR_SERVERS: "nats://nats-1:4222,nats://nats-2:4222,nats://nats-3:4222"
  depends_on:
    - nats-1
    - nats-2
    - nats-3
```

Acesso: http://localhost:7777

---

## 🔗 Integração

**Usado por:**
- Todos containers Mordomo (messaging)
- Core API (pub/sub, request/reply)
- Monitoring (coleta de métricas)

**Expõe:**
- 4222: Client connections
- 6222: Cluster routes
- 8222: HTTP monitoring

**Monitora:** Prometheus, Grafana

---

## 📚 CLI Avançado

```bash
# Cluster info
nats server list
nats server report jetstream
nats server report connections

# Streams
nats stream ls
nats stream info AUDIO --json
nats stream backup AUDIO backup.tar

# Consumers
nats consumer ls AUDIO
nats consumer info AUDIO audio-processor

# KV
nats kv ls
nats kv status EMBEDDINGS

# Benchmark
nats bench audio.raw --msgs 100000 --size 1024
```

---

## 🚨 Backup & Restore

```bash
# Backup stream
nats stream backup AUDIO /backup/audio.tar.gz

# Restore
nats stream restore AUDIO /backup/audio.tar.gz

# Backup KV
nats kv get EMBEDDINGS --raw > /backup/embeddings.json

# Snapshot JetStream (filesystem)
tar -czf jetstream-backup.tar.gz /data/jetstream/
```

---

**Versão:** 1.0  
**Última atualização:** 27/11/2025  
**Nota:** Este é o único NATS Server do sistema - usado por todos os ecossistemas (Mordomo, Infraestrutura, Monitoramento)
