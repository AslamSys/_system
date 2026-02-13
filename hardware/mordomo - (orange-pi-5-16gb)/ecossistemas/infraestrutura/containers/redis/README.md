# 🔴 Redis Cache & Session Store

**Container:** `redis`  
**Ecossistema:** Infraestrutura  
**Função:** Cache distribuído e armazenamento de sessões

---

## 📋 Propósito

Cache em memória de alta performance para acelerar consultas, armazenar sessões ativas e coordenar estado distribuído entre containers.

---

## 🎯 Responsabilidades

### Primárias
- ✅ Cache de consultas frequentes (conversas, contexto)
- ✅ Session store para conversas ativas
- ✅ Rate limiting counters
- ✅ Pub/Sub para eventos internos
- ✅ Locks distribuídos (prevent race conditions)

### Secundárias
- ✅ TTL automático para expiração de dados
- ✅ Persistência opcional (RDB snapshots)
- ✅ Replicação (futuro)

---

## 🔧 Tecnologias

**Stack:** Redis 7.x

```yaml
Image: redis:7-alpine
Size: ~30MB
RAM: 50-100MB (depende do cache)
```

---

## 📊 Especificações

```yaml
Performance:
  CPU: < 5%
  RAM: ~ 50-100 MB
  Latency: < 1ms (GET/SET)
  Throughput: 100k ops/sec
  
Persistence:
  RDB: Snapshots a cada 5 min (se houver mudanças)
  AOF: Desabilitado (não crítico para cache)
  
Max Memory:
  Limit: 256MB
  Policy: allkeys-lru (remove menos usados)
```

---

## 🔌 Casos de Uso

### 1. Cache de Conversas

```typescript
// Conversation Manager
import Redis from 'ioredis';

const redis = new Redis({
  host: 'redis',
  port: 6379,
  password: process.env.REDIS_PASSWORD
});

// Cachear lista de conversas
const cacheKey = `conversations:${speaker_id}:list`;
const cached = await redis.get(cacheKey);

if (cached) {
  return JSON.parse(cached);
}

// Query PostgreSQL
const conversations = await prisma.conversation.findMany(...);

// Cache por 5 minutos
await redis.setex(cacheKey, 300, JSON.stringify(conversations));
```

### 2. Session Store (Conversas Ativas)

```typescript
// Armazenar conversa ativa
await redis.hset(`session:${conversation_id}`, {
  speaker_id: 'user_1',
  started_at: Date.now(),
  last_activity: Date.now(),
  state: 'waiting_for_llm'
});

// Setar TTL de 5 minutos
await redis.expire(`session:${conversation_id}`, 300);

// Recuperar
const session = await redis.hgetall(`session:${conversation_id}`);
```

### 3. Rate Limiting

```typescript
// Core Gateway
const key = `rate_limit:${speaker_id}`;
const current = await redis.incr(key);

if (current === 1) {
  // Primeira requisição, setar TTL de 1 minuto
  await redis.expire(key, 60);
}

if (current > 100) {
  throw new Error('Rate limit exceeded');
}
```

### 4. Distributed Locks

```typescript
// Evitar processamento duplicado
const lockKey = `lock:conversation:${conversation_id}`;
const acquired = await redis.set(lockKey, 'locked', 'EX', 10, 'NX');

if (!acquired) {
  throw new Error('Conversation already being processed');
}

try {
  // Processar conversa
  await processConversation(conversation_id);
} finally {
  // Liberar lock
  await redis.del(lockKey);
}
```

### 5. Pub/Sub (Eventos Internos)

```typescript
// Publisher
await redis.publish('conversation:updates', JSON.stringify({
  conversation_id: 'uuid',
  event: 'message_received',
  data: { ... }
}));

// Subscriber (Core Gateway)
const subscriber = redis.duplicate();
await subscriber.subscribe('conversation:updates');

subscriber.on('message', (channel, message) => {
  const event = JSON.parse(message);
  // Enviar via WebSocket para Dashboard
  wsBroadcast(event);
});
```

---

## ⚙️ Configuração

### redis.conf (Customizado)

```conf
# Memória
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistência (snapshots leves)
save 300 10  # Snapshot a cada 5min se 10+ keys mudarem
save 60 1000  # Ou a cada 1min se 1000+ keys mudarem
stop-writes-on-bgsave-error yes
rdbcompression yes

# Segurança
requirepass ${REDIS_PASSWORD}
protected-mode yes
bind 0.0.0.0

# Performance
tcp-backlog 511
timeout 0
tcp-keepalive 300
maxclients 100

# Logging
loglevel notice
logfile ""

# Desabilitar comandos perigosos
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

---

## 🔒 Segurança (Secrets)

### Docker Secrets

```yaml
# docker-compose.yml
services:
  redis:
    command: >
      sh -c "redis-server 
      --requirepass $$(cat /run/secrets/redis_password)
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru"
    secrets:
      - redis_password

secrets:
  redis_password:
    file: ./secrets/redis_password.txt
```

### Gerar Senha

```bash
# Gerar senha aleatória de 32 chars
openssl rand -base64 32 > secrets/redis_password.txt

# Ou manualmente
echo "sua_senha_super_secreta_aqui" > secrets/redis_password.txt
chmod 600 secrets/redis_password.txt
```

### Conectar com Senha

```typescript
// Node.js
import Redis from 'ioredis';
import { readFileSync } from 'fs';

const password = readFileSync('/run/secrets/redis_password', 'utf8').trim();

const redis = new Redis({
  host: 'redis',
  port: 6379,
  password,
  retryStrategy: (times) => Math.min(times * 50, 2000)
});
```

---

## 🐳 Docker

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: redis-cache
    command: >
      sh -c "redis-server 
      --requirepass $$(cat /run/secrets/redis_password)
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
      --save 300 10
      --save 60 1000
      --appendonly no"
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    secrets:
      - redis_password
    networks:
      - infra-net
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 300M
        reservations:
          cpus: '0.05'
          memory: 50M
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  redis-data:

secrets:
  redis_password:
    file: ./secrets/redis_password.txt
```

---

## 📊 Métricas (Prometheus)

### Redis Exporter

```yaml
services:
  redis-exporter:
    image: oliver006/redis_exporter:alpine
    container_name: redis-exporter
    environment:
      - REDIS_ADDR=redis:6379
      - REDIS_PASSWORD_FILE=/run/secrets/redis_password
    secrets:
      - redis_password
    ports:
      - "9121:9121"
    networks:
      - infra-net
    depends_on:
      - redis
```

### Métricas Expostas

```promql
# Memória usada
redis_memory_used_bytes

# Keys totais
redis_db_keys{db="db0"}

# Comandos por segundo
rate(redis_commands_total[1m])

# Hit rate do cache
rate(redis_keyspace_hits_total[5m]) / 
  (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))

# Clientes conectados
redis_connected_clients
```

---

## 🔧 Comandos Úteis

### Monitorar em Tempo Real

```bash
# Ver comandos executados
docker exec -it redis-cache redis-cli -a $(cat secrets/redis_password.txt) MONITOR

# Stats gerais
docker exec -it redis-cache redis-cli -a $(cat secrets/redis_password.txt) INFO stats

# Memória
docker exec -it redis-cache redis-cli -a $(cat secrets/redis_password.txt) INFO memory
```

### Debugging

```bash
# Ver todas as keys
docker exec -it redis-cache redis-cli -a $(cat secrets/redis_password.txt) KEYS '*'

# Ver conteúdo de key
docker exec -it redis-cache redis-cli -a $(cat secrets/redis_password.txt) GET "conversations:user_1:list"

# Ver hash completo
docker exec -it redis-cache redis-cli -a $(cat secrets/redis_password.txt) HGETALL "session:abc123"

# Ver TTL de key
docker exec -it redis-cache redis-cli -a $(cat secrets/redis_password.txt) TTL "rate_limit:user_1"
```

### Limpeza

```bash
# Deletar keys por pattern
docker exec -it redis-cache redis-cli -a $(cat secrets/redis_password.txt) --scan --pattern "cache:*" | xargs redis-cli -a $(cat secrets/redis_password.txt) DEL

# Limpar TUDO (cuidado!)
# NOTA: Comandos FLUSHDB/FLUSHALL foram desabilitados no redis.conf
# Para limpar tudo, reinicie o container
docker restart redis-cache
```

---

## 🔧 Troubleshooting

### Memória cheia

```bash
# Ver uso
docker exec redis-cache redis-cli -a $(cat secrets/redis_password.txt) INFO memory | grep used_memory_human

# Ver política de eviction
docker exec redis-cache redis-cli -a $(cat secrets/redis_password.txt) CONFIG GET maxmemory-policy

# Limpar cache manualmente (keys antigas)
docker exec redis-cache redis-cli -a $(cat secrets/redis_password.txt) --scan --pattern "cache:*" | head -1000 | xargs redis-cli -a $(cat secrets/redis_password.txt) DEL
```

### Conexão recusada

```bash
# Verificar se está rodando
docker ps | grep redis

# Ver logs
docker logs -f redis-cache

# Testar conexão
docker exec redis-cache redis-cli -a $(cat secrets/redis_password.txt) PING
# Deve retornar: PONG
```

### Performance ruim

```bash
# Ver slow queries
docker exec redis-cache redis-cli -a $(cat secrets/redis_password.txt) SLOWLOG GET 10

# Ver comandos mais usados
docker exec redis-cache redis-cli -a $(cat secrets/redis_password.txt) INFO commandstats

# Aumentar memória se necessário (editar docker-compose.yml)
maxmemory 512mb
```

---

## 💡 Boas Práticas

### 1. Sempre usar TTL

```typescript
// ❌ Ruim (key nunca expira)
await redis.set('key', 'value');

// ✅ Bom (expira em 5 min)
await redis.setex('key', 300, 'value');
```

### 2. Prefixar keys por contexto

```typescript
// ✅ Organizado
await redis.set('cache:conversations:user_1', data);
await redis.set('session:conversation:abc123', data);
await redis.set('lock:conversation:abc123', '1');
```

### 3. Usar pipeline para múltiplas operações

```typescript
// ❌ Lento (3 round-trips)
await redis.set('key1', 'val1');
await redis.set('key2', 'val2');
await redis.set('key3', 'val3');

// ✅ Rápido (1 round-trip)
const pipeline = redis.pipeline();
pipeline.set('key1', 'val1');
pipeline.set('key2', 'val2');
pipeline.set('key3', 'val3');
await pipeline.exec();
```

### 4. Monitorar hit rate

```typescript
// Métrica de cache hit rate
const hits = await redis.get('cache_hits') || 0;
const misses = await redis.get('cache_misses') || 0;
const hitRate = hits / (hits + misses);

// Meta: >80% hit rate
```

---

## 📈 Monitoramento (Grafana Dashboard)

### Painel Redis

```yaml
Panels:
  - Memory Usage (gauge): redis_memory_used_bytes / redis_memory_max_bytes
  - Keys Total (stat): redis_db_keys
  - Commands/sec (graph): rate(redis_commands_total[1m])
  - Cache Hit Rate (gauge): hit_rate_calculation
  - Connected Clients (stat): redis_connected_clients
  - Evicted Keys (graph): rate(redis_evicted_keys_total[5m])
```

### Alertas

```yaml
- name: Redis High Memory
  expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.9
  for: 5m
  
- name: Redis Low Hit Rate
  expr: cache_hit_rate < 0.7
  for: 10m
  
- name: Redis Down
  expr: up{job="redis"} == 0
  for: 1m
```

---

**Documentação atualizada:** 27/11/2025
