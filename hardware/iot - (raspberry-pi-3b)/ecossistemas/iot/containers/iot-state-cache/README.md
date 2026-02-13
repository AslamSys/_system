# 🗄️ IoT State Cache

**Container:** `iot-state-cache`  
**Stack:** Redis 7 Alpine  
**Propósito:** Cache local de estados de dispositivos IoT

---

## 📋 Propósito

Cache Redis local para estados de dispositivos IoT. Latência < 5ms para consultas críticas ("luz está acesa?"). Sincroniza com PostgreSQL do Mordomo para persistência.

---

## 🎯 Responsabilidades

- ✅ Cache de estados atuais (50-100 dispositivos)
- ✅ Consultas ultra-rápidas (< 5ms)
- ✅ TTL automático (5 minutos)
- ✅ Pub/Sub para mudanças de estado
- ✅ Fallback: PostgreSQL do Mordomo

---

## 📊 Estrutura de Dados

### Schemas Redis

```redis
# Estado de dispositivo (Hash)
HSET device:luz_sala power ON
HSET device:luz_sala brightness 80
HSET device:luz_sala color_r 255
HSET device:luz_sala color_g 200
HSET device:luz_sala color_b 150
HSET device:luz_sala last_update 1732723200
EXPIRE device:luz_sala 300  # TTL 5min

# Estado de sensor (Hash)
HSET device:sensor_temp_quarto temperature 23.5
HSET device:sensor_temp_quarto humidity 65
HSET device:sensor_temp_quarto last_update 1732723200
EXPIRE device:sensor_temp_quarto 300

# Presença BLE (String)
SET presence:smartphone_renan home EX 300

# Lista de dispositivos online (Set)
SADD devices:online luz_sala
SADD devices:online sensor_temp_quarto

# Registro de Dispositivo (Hash)
HSET registry:luz_sala_esp32 ip "10.0.0.15"
HSET registry:luz_sala_esp32 type "light"
HSET registry:luz_sala_esp32 last_seen 1732723200

# Lista de todos os IDs conhecidos (Set)
SADD registry:all_devices luz_sala_esp32
```

### Operações Típicas

```javascript
// Atualizar estado (após comando MQTT)
await redis.hset('device:luz_sala', {
  power: 'ON',
  brightness: 80,
  last_update: Date.now()
});
await redis.expire('device:luz_sala', 300);

// Pub/Sub: Notificar mudança
await redis.publish('device:state_changed', JSON.stringify({
  device_id: 'luz_sala',
  state: { power: 'ON', brightness: 80 }
}));

// Consultar estado (ultra rápido)
const state = await redis.hgetall('device:luz_sala');
// Retorna: { power: 'ON', brightness: '80', ... }

// Listar dispositivos online
const online = await redis.smembers('devices:online');
```

---

## 🔄 Sincronização com PostgreSQL

### Fluxo de Escrita

```
iot-orchestrator executa comando
    ↓
1. MQTT publish → zigbee2mqtt (dispositivo executa)
    ↓
2. Redis local: HSET (< 1ms) - estado atualizado
    ↓
3. NATS publish → iot.device.state_changed
    ↓
4. Mordomo PostgreSQL: INSERT async (background)
```

### Fluxo de Leitura

```
Mordomo: "Qual a temperatura do quarto?"
    ↓
1. Tenta Redis local (< 5ms)
    ↓
2. Se miss (TTL expirou): PostgreSQL (10-50ms)
    ↓
3. Atualiza Redis (warm cache)
```

**Resultado**: 95% das consultas via Redis (< 5ms), 5% via PostgreSQL (fallback).

---

## 🚀 Docker

```yaml
iot-state-cache:
  image: redis:7-alpine
  container_name: iot-state-cache
  volumes:
    - ./data/redis:/data
  command: >
    redis-server
    --appendonly yes
    --maxmemory 64mb
    --maxmemory-policy allkeys-lru
    --save 60 1
  networks:
    - iot-net
  deploy:
    resources:
      limits:
        memory: 80M
        cpus: '0.1'
  restart: unless-stopped
```

---

## ⚙️ Configuração Redis

### Parâmetros Otimizados

```conf
# Persistência (AOF para durabilidade)
appendonly yes
appendfsync everysec

# Limites de memória
maxmemory 64mb
maxmemory-policy allkeys-lru  # Remove keys antigas automaticamente

# Snapshots periódicos
save 60 1  # Salva se 1 mudança em 60s

# Evict keys antigas
lru-clock-resolution 1000
```

### Por que 64MB?

- **50 dispositivos** × ~1KB por device = **50KB**
- **Overhead Redis** (estruturas internas) = ~10MB
- **Pub/Sub buffers** = ~4MB
- **Total**: ~14MB usado (64MB comporta 200+ dispositivos)

---

## 📡 Integração com iot-orchestrator

### Client Node.js

```javascript
const Redis = require('ioredis');

const redis = new Redis({
  host: 'iot-state-cache',
  port: 6379,
  maxRetriesPerRequest: 3,
  retryStrategy(times) {
    return Math.min(times * 50, 2000);
  }
});

// Subscribe para mudanças
const subscriber = redis.duplicate();
subscriber.subscribe('device:state_changed');
subscriber.on('message', (channel, message) => {
  const event = JSON.parse(message);
  console.log(`Device ${event.device_id} changed:`, event.state);
});

// Atualizar estado após comando
async function updateDeviceState(deviceId, state) {
  const key = `device:${deviceId}`;
  await redis.hset(key, { ...state, last_update: Date.now() });
  await redis.expire(key, 300);
  
  // Notificar via Pub/Sub
  await redis.publish('device:state_changed', JSON.stringify({
    device_id: deviceId,
    state
  }));
}

// Consultar estado
async function getDeviceState(deviceId) {
  const key = `device:${deviceId}`;
  const state = await redis.hgetall(key);
  
  if (!state || Object.keys(state).length === 0) {
    // Cache miss → Consultar PostgreSQL via NATS
    return await fetchFromPostgreSQL(deviceId);
  }
  
  return state;
}
```

---

## 🔍 Monitoramento

### Métricas Redis

```bash
# Conectar ao container
docker exec -it iot-state-cache redis-cli

# Estatísticas
INFO stats
INFO memory

# Keys ativos
DBSIZE

# Ver keys por padrão
KEYS device:*

# Monitorar comandos em tempo real
MONITOR
```

### Prometheus Exporter (opcional)

```yaml
redis-exporter:
  image: oliver006/redis_exporter:latest
  environment:
    - REDIS_ADDR=redis://iot-state-cache:6379
  ports:
    - "9121:9121"
  networks:
    - iot-net
```

---

## 🧪 Testes

### Verificar Cache Funcionando

```bash
# Inserir estado manualmente
docker exec -it iot-state-cache redis-cli HSET device:test_luz power ON

# Consultar
docker exec -it iot-state-cache redis-cli HGETALL device:test_luz

# Pub/Sub test
# Terminal 1: Subscribe
docker exec -it iot-state-cache redis-cli SUBSCRIBE device:state_changed

# Terminal 2: Publish
docker exec -it iot-state-cache redis-cli PUBLISH device:state_changed '{"device_id":"luz_teste","state":"ON"}'
```

---

## 📊 Performance Esperada

| Operação | Latência | Justificativa |
|----------|----------|---------------|
| HSET | < 1ms | Escrita em memória |
| HGETALL | < 5ms | Leitura de hash pequeno |
| PUBLISH | < 2ms | Pub/Sub assíncrono |
| SMEMBERS | < 3ms | Set com < 100 itens |

**Rede local**: Adiciona ~1-2ms (Docker bridge)  
**Total**: < 10ms para qualquer operação

---

## 🔒 Segurança

### Não Precisa de Senha

- **Rede privada**: Apenas containers IoT têm acesso (`iot-net`)
- **Não exposto**: Sem bind para host (porta 6379 interna)
- **Dados não-sensíveis**: Estados temporários (TTL 5min)

### Se Precisar de Auth

```yaml
command: >
  redis-server
  --requirepass mysecretpassword
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Redis 7 Alpine
- ✅ AOF persistence
- ✅ LRU eviction (64MB)
- ✅ Pub/Sub para state changes
- ✅ TTL 5min (sincroniza PostgreSQL)
