# 🔧 Ecossistema Infraestrutura

> 🗂️ **Navegação:** [🏠 Início](../../../../README.md) > [🔧 Hardware](../../../README.md) > [🎯 Mordomo](../../README.md) > [🌐 Ecossistemas](../README.md) > [🔧 Infraestrutura](README.md)

Serviços de base essenciais para comunicação, descoberta, armazenamento de dados e vetores. Compartilhados por todos os ecossistemas.

---

## Visão Geral

O ecossistema de **Infraestrutura** fornece os pilares fundamentais para o funcionamento do sistema:

- 🔄 **Comunicação assíncrona** (event bus NATS)
- 🔍 **Descoberta de serviços** (Consul)
- 💾 **Persistência de dados** (PostgreSQL)
- 🧠 **Armazenamento vetorial** (Qdrant para RAG)
- 🔴 **Cache e Sessão** (Redis)

---

## Arquitetura de Containers (5 containers)

```
┌────────────────────────────────────────────────┐
│          ECOSSISTEMA INFRAESTRUTURA            │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────┐         ┌──────────────┐   │
│  │     NATS     │◄────────│   Consul     │   │
│  │  Event Bus   │         │  Discovery   │   │
│  └──────────────┘         └──────────────┘   │
│         ▲                                      │
│         │                                      │
│  ┌──────┴───────┐         ┌──────────────┐   │
│  │   Qdrant     │         │  PostgreSQL  │   │
│  │   Vetores    │         │  Relacionais │   │
│  └──────────────┘         └──────────────┘   │
│                                                │
│  ┌──────────────────────────────────────┐    │
│  │              Redis                   │    │
│  │         Cache & Session              │    │
│  └──────────────────────────────────────┘    │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 📦 Lista de Containers

### 1. **event-bus (NATS)**

**Função:** Sistema de mensageria ultra leve para comunicação entre containers

**Tecnologia:** [NATS.io](https://nats.io/)

**Por que NATS?**
- ✅ **Ultra leve:** 12MB de RAM, perfeito para ARM
- ✅ **Rápido:** Milhões de mensagens/segundo
- ✅ **Pub/Sub:** Comunicação assíncrona desacoplada
- ✅ **Request/Reply:** Chamadas síncronas quando necessário
- ✅ **Jetstream:** Persistência de mensagens (opcional)

**Responsabilidades:**
- Publicação de eventos entre containers
- Request/Reply para chamadas síncronas
- Garantia de entrega (com Jetstream)
- Roteamento de mensagens por tópicos

**Tópicos (Subjects):**
```
wake_word.detected
speech.started
speech.ended
speech.transcription.{speaker_id}
llm.request
llm.response.{request_id}
tts.generate
tts.playing
tts.paused
user.interrupted
iot.command.{device_id}
```

**Comunicação:**
- **Porta:** 4222 (client), 8222 (monitoring)
- **Protocolo:** NATS native protocol
- **Segurança:** TLS opcional

**Exemplo de uso:**
```javascript
// Publicar evento
nats.publish('wake_word.detected', { speaker_id: 'user_1', timestamp: Date.now() });

// Subscrever evento
nats.subscribe('speech.transcription.*', (msg) => {
  console.log('Transcrição:', msg.data);
});

// Request/Reply
const response = await nats.request('llm.request', { text: 'Olá' });
```

**Docker Compose:**
```yaml
nats:
  image: nats:alpine
  container_name: event-bus-nats
  ports:
    - "4222:4222"
    - "8222:8222"
  command: ["-js", "-m", "8222"]  # Jetstream + monitoring
  volumes:
    - nats-data:/data
  restart: unless-stopped
```

---

### 2. **consul**

**Função:** Auto-descoberta de serviços e health checks

**Tecnologias:**
- **Consul** (robusto, com UI)
- **CoreDNS** (super leve, apenas DNS)

**Por que Service Discovery?**
- ✅ Containers encontram-se automaticamente
- ✅ Não precisa hardcode de IPs/portas
- ✅ Health checks automáticos
- ✅ Load balancing interno

**Responsabilidades:**
- Registro automático de containers ao iniciar
- Resolução de nomes (DNS interno)
- Health checks periódicos
- Desregistro automático de containers offline

**Opção 1: Consul (Recomendado)**

**Recursos:**
- UI web para visualização
- KV store para configurações
- Health checks HTTP/TCP/gRPC
- Multi-datacenter (futuro)

**Docker Compose:**
```yaml
consul:
  image: consul:latest
  container_name: discovery-consul
  ports:
    - "8500:8500"  # UI web
    - "8600:8600/udp"  # DNS
  command: agent -server -ui -bootstrap-expect=1 -client=0.0.0.0
  volumes:
    - consul-data:/consul/data
  restart: unless-stopped
```

**Acesso UI:** http://localhost:8500

**Opção 2: CoreDNS (Minimalista)**

**Recursos:**
- Extremamente leve (<10MB RAM)
- Apenas DNS, sem extras
- Configuração via Corefile

**Docker Compose:**
```yaml
coredns:
  image: coredns/coredns:latest
  container_name: discovery-coredns
  ports:
    - "53:53/udp"
  volumes:
    - ./Corefile:/Corefile
  command: -conf /Corefile
  restart: unless-stopped
```

**Exemplo de Corefile:**
```
.:53 {
    forward . 8.8.8.8
    log
    errors
    file /etc/coredns/db.local local
}
```

---

### 3. **qdrant (Banco Vetorial)**

**Função:** Armazenamento de embeddings e busca por similaridade

**Tecnologia:** [Qdrant](https://qdrant.tech/)

**Por que Qdrant?**
- ✅ **Otimizado para ARM:** Roda perfeitamente em Raspberry Pi
- ✅ **Alta performance:** Busca vetorial ultra rápida
- ✅ **Persistência:** Dados salvos em disco
- ✅ **API REST + gRPC:** Fácil integração
- ✅ **Collections:** Separação lógica de dados

**Responsabilidades:**
- Armazenar embeddings de:
  - Conversas anteriores (RAG)
  - Perfis de speakers (voz)
  - Contextos semânticos
  - Documentos do usuário
- Busca por similaridade vetorial
- Filtragem por metadados
- CRUD de vetores

**Collections:**
```
conversations      # Histórico de conversas
speaker_profiles   # Embeddings de voz
knowledge_base     # RAG - documentos do usuário
intents           # Intenções mapeadas
```

**Docker Compose:**
```yaml
qdrant:
  image: qdrant/qdrant:latest
  container_name: qdrant-vectors
  ports:
    - "6333:6333"  # REST API
    - "6334:6334"  # gRPC
  volumes:
    - qdrant-data:/qdrant/storage
  environment:
    - QDRANT__SERVICE__GRPC_PORT=6334
  restart: unless-stopped
```

**Exemplo de uso (Python):**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient("localhost", port=6333)

# Criar collection
client.create_collection(
    collection_name="conversations",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Inserir vetor
client.upsert(
    collection_name="conversations",
    points=[{
        "id": 1,
        "vector": embedding_vector,
        "payload": {
            "speaker_id": "user_1",
            "text": "Qual a temperatura?",
            "timestamp": "2025-11-27T10:00:00Z"
        }
    }]
)

# Buscar similar
results = client.search(
    collection_name="conversations",
    query_vector=query_embedding,
    limit=5
)
```

**Acesso UI:** http://localhost:6333/dashboard

---

## 🎯 NATS Namespace Global (Todos os Módulos)

### Padrão de Tópicos

**Formato:** `{modulo}.{recurso}.{acao}`

```yaml
# Módulo Mordomo
mordomo.speech.transcribed
mordomo.brain.response_generated
mordomo.conversation.message_received
mordomo.tts.generate_request
mordomo.action.completed

# Módulo IoT
iot.device.control
iot.device.state_changed
iot.device.discovered
iot.scene.activate

# Módulo Comunicação
comunicacao.whatsapp.send
comunicacao.whatsapp.message_received
comunicacao.email.send
comunicacao.sms.send

# Módulo Pagamentos
pagamentos.pix.send
pagamentos.pix.received
pagamentos.boleto.generate
pagamentos.card.charge

# Módulo Investimentos
investimentos.order.create
investimentos.order.filled
investimentos.portfolio.balance
investimentos.market.price_alert

# Módulo Entretenimento
entretenimento.music.play
entretenimento.music.pause
entretenimento.video.play
entretenimento.playlist.create

# Módulo Segurança
seguranca.camera.snapshot
seguranca.alarm.arm
seguranca.motion.detected
seguranca.face.recognized

# Módulo RPA
rpa.task.execute
rpa.task.completed
rpa.browser.navigate
rpa.scrape.data

# Módulo NAS
nas.file.search
nas.file.found
nas.backup.start
nas.photo.backed_up
```

### Padrões de Comunicação

**1. Pub/Sub (Fire-and-forget)**
```typescript
// Publisher (não aguarda resposta)
nats.publish('iot.device.state_changed', {
  device_id: 'light_sala',
  state: 'on',
  timestamp: Date.now()
});

// Subscriber
nats.subscribe('iot.device.state_changed', (msg) => {
  console.log('Device changed:', msg.data);
});
```

**2. Request/Reply (Aguarda confirmação)**
```typescript
// Requester
const response = await nats.request(
  'iot.device.control',
  { device_id: 'light_sala', action: 'turn_on' },
  { timeout: 5000 }
);

// Responder
nats.subscribe('iot.device.control', async (msg) => {
  const result = await controlDevice(msg.data);
  msg.respond({ success: true, result });
});
```

### Formato de Mensagens (JSON Schema)

```typescript
// Request padrão
interface ActionRequest {
  speaker_id: string;           // Quem solicitou
  conversation_id?: string;     // Contexto da conversa
  params: Record<string, any>;  // Parâmetros específicos
  timestamp: number;            // Unix timestamp
  request_id: string;           // UUID para tracking
}

// Response padrão
interface ActionResponse {
  success: boolean;
  request_id: string;
  result?: any;                 // Dados específicos da ação
  error?: string;               // Mensagem de erro
  timestamp: number;
}
```

### Segurança NATS

**Autenticação via Token (Recomendado)**

```yaml
# docker-compose.yml
services:
  nats:
    command: [
      "-js",
      "-m", "8222",
      "--auth", "$$(cat /run/secrets/nats_token)"
    ]
    secrets:
      - nats_token

secrets:
  nats_token:
    file: ./secrets/nats_token.txt
```

```bash
# Gerar token
openssl rand -base64 32 > secrets/nats_token.txt
chmod 600 secrets/nats_token.txt
```

**Conectar com Token**

```typescript
import { connect } from 'nats';
import { readFileSync } from 'fs';

const token = readFileSync('/run/secrets/nats_token', 'utf8').trim();

const nc = await connect({
  servers: 'nats://nats:4222',
  token
});
```

---

### 4. **postgres (Banco Relacional)**

**Função:** Persistência de dados estruturados

**Tecnologia:** PostgreSQL 16

**Por que PostgreSQL?**
- ✅ **Confiável:** Banco maduro e robusto
- ✅ **Roda bem em ARM:** Com tuning adequado
- ✅ **Extensível:** PostGIS, pg_vector, etc.
- ✅ **ACID:** Transações garantidas

**Responsabilidades:**
- Armazenar dados relacionais:
  - Usuários e perfis
  - Histórico de conversas
  - Logs de eventos
  - Configurações de dispositivos IoT
  - Tasks e lembretes
  - Métricas agregadas

**Schema Principal:**
```sql
-- Usuários autorizados
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    speaker_embedding BYTEA,  -- embedding de voz
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversas
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    speaker_id VARCHAR(50),
    text TEXT NOT NULL,
    response TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Dispositivos IoT
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50),  -- light, thermostat, etc.
    protocol VARCHAR(20),  -- zigbee, matter, mqtt
    config JSONB,
    status VARCHAR(20) DEFAULT 'offline'
);

-- Logs de eventos
CREATE TABLE event_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    container VARCHAR(50),
    payload JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Tasks e lembretes
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title TEXT,
    description TEXT,
    due_date TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Docker Compose:**
```yaml
postgres:
  image: postgres:16-alpine
  container_name: postgres-db
  ports:
    - "5432:5432"
  environment:
    POSTGRES_USER: aslam
    POSTGRES_PASSWORD: ${DB_PASSWORD}
    POSTGRES_DB: mordomo
  volumes:
    - postgres-data:/var/lib/postgresql/data
    - ./init.sql:/docker-entrypoint-initdb.d/init.sql
  restart: unless-stopped
  command: 
    - "postgres"
    - "-c"
    - "shared_buffers=256MB"  # Tuning para ARM
    - "-c"
    - "max_connections=50"
```

**Tuning para Raspberry Pi:**
```conf
shared_buffers = 256MB
effective_cache_size = 512MB
work_mem = 4MB
maintenance_work_mem = 64MB
max_connections = 50
```

**Backup automático:**
```bash
# Cron job diário
0 3 * * * docker exec postgres-db pg_dump -U aslam mordomo > /backup/mordomo_$(date +\%Y\%m\%d).sql
```

---

### 5. **redis (Cache & Session)**

**Função:** Cache em memória e armazenamento de sessões

**Tecnologia:** Redis 7

**Por que Redis?**
- ✅ **Latência sub-milissegundo:** Essencial para estado de conversação
- ✅ **Estruturas de dados:** Lists, Sets, Hashes nativos
- ✅ **TTL:** Expiração automática de chaves (sessões)
- ✅ **Pub/Sub:** Canal rápido para eventos efêmeros

**Responsabilidades:**
- Cache de respostas frequentes do LLM
- Armazenamento de estado da sessão (contexto curto prazo)
- Rate limiting
- Filas de tarefas rápidas

**Docker Compose:**
```yaml
redis:
  image: redis:7-alpine
  container_name: redis-cache
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
  command: redis-server --appendonly yes
  restart: unless-stopped
```

---

## 🔗 Integração entre Containers

### NATS ↔ Todos os containers
- Todos publicam/escutam eventos via NATS
- Comunicação desacoplada e assíncrona

### Qdrant ↔ LLM (Brain)
- LLM busca contexto semântico em Qdrant
- RAG (Retrieval Augmented Generation)

### PostgreSQL ↔ Core API
- Core API persiste conversas, usuários, configs
- Consultas de histórico

### Discovery ↔ Todos os containers
- Containers se registram ao iniciar
- Descobrem outros serviços dinamicamente

---

## 🛠️ Deploy Completo

**docker-compose.yml (Infraestrutura):**
```yaml
version: '3.8'

services:
  nats:
    image: nats:alpine
    container_name: event-bus-nats
    ports:
      - "4222:4222"
      - "8222:8222"
    command: ["-js", "-m", "8222"]
    volumes:
      - nats-data:/data
    restart: unless-stopped
    networks:
      - infra-net

  consul:
    image: consul:latest
    container_name: discovery-consul
    ports:
      - "8500:8500"
      - "8600:8600/udp"
    command: agent -server -ui -bootstrap-expect=1 -client=0.0.0.0
    volumes:
      - consul-data:/consul/data
    restart: unless-stopped
    networks:
      - infra-net

  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant-vectors
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant-data:/qdrant/storage
    restart: unless-stopped
    networks:
      - infra-net

  postgres:
    image: postgres:16-alpine
    container_name: postgres-db
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: aslam
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: mordomo
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - infra-net

volumes:
  nats-data:
  consul-data:
  qdrant-data:
  postgres-data:

networks:
  infra-net:
    driver: bridge
```

**Comandos:**
```bash
# Subir infraestrutura
docker-compose up -d

# Ver logs
docker-compose logs -f

# Status
docker-compose ps

# Parar tudo
docker-compose down
```

---

## 📊 Portas e Acesso

| Serviço | Porta(s) | Acesso |
|---------|----------|--------|
| NATS | 4222, 8222 | Client: 4222, Monitoring: http://localhost:8222 |
| Consul | 8500, 8600 | UI: http://localhost:8500 |
| Qdrant | 6333, 6334 | REST: 6333, gRPC: 6334, UI: http://localhost:6333/dashboard |
| PostgreSQL | 5432 | psql -h localhost -U aslam -d mordomo |

---

## 🔒 Segurança

- ✅ **Rede isolada:** Containers em rede privada `infra-net`
- ✅ **Credenciais:** Via environment variables (`.env`)
- ✅ **Backup:** PostgreSQL com dumps diários
- ✅ **Volumes persistentes:** Dados sobrevivem a restarts

---

## 📈 Monitoramento

Todos os containers expõem métricas para Prometheus:
- NATS: http://localhost:8222/metrics
- Consul: http://localhost:8500/v1/agent/metrics
- Qdrant: http://localhost:6333/metrics
- PostgreSQL: Via postgres_exporter

---

**Documentação atualizada:** 27/11/2025
