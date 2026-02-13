# 🗄️ PostgreSQL Database

**Container:** `postgres`  
**Ecossistema:** Infraestrutura  
**Papel:** Relational Data Storage

---

## 📋 Propósito

Banco de dados relacional para persistência de dados estruturados: usuários, conversas, configurações, logs e histórico.

---

## 🎯 Responsabilidades

- ✅ Armazenamento de dados relacionais
- ✅ Transações ACID
- ✅ Índices e otimização de queries
- ✅ Backup e replicação
- ✅ Full-text search (pt_BR)
- ✅ JSON/JSONB storage

---

## 🔧 Tecnologias

**PostgreSQL** 16+
- ACID compliance
- JSON/JSONB support
- Full-text search
- Partitioning
- Replication (streaming)
- Extensions (pg_trgm, uuid-ossp)

**Imagem:** `postgres:16-alpine`

---

## 📊 Especificações

```yaml
Performance:
  CPU: 10-20%
  RAM: 256 MB - 1 GB
  Storage: 5-20 GB
  
Connections:
  Max: 100
  Pool Size: 20 (por aplicação)
  
Backup:
  Frequency: Diária (2h AM)
  Retention: 7 dias
  Type: pg_dump + WAL archiving
```

---

## 🗃️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    voice_enrolled BOOLEAN DEFAULT FALSE,
    speaker_embedding_id VARCHAR(255),  -- Qdrant vector ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_voice ON users(voice_enrolled) WHERE voice_enrolled = TRUE;
CREATE INDEX idx_users_metadata ON users USING GIN(metadata);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    message_count INTEGER DEFAULT 0,
    satisfaction_score FLOAT CHECK (satisfaction_score BETWEEN 0 AND 1),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_started ON conversations(started_at DESC);
CREATE INDEX idx_conversations_metadata ON conversations USING GIN(metadata);
```

### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Métricas
    latency_ms INTEGER,
    intent VARCHAR(100),
    confidence FLOAT,
    
    -- RAG context usado
    rag_context JSONB,
    
    -- Audio metadata
    audio_duration_ms INTEGER,
    transcription_model VARCHAR(50),
    
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, timestamp);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_intent ON messages(intent);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);

-- Partitioning por mês (opcional para alta carga)
-- CREATE TABLE messages_y2024m11 PARTITION OF messages
--     FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
```

### Actions Table
```sql
CREATE TABLE actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,  -- iot_control, reminder, query
    action_name VARCHAR(255) NOT NULL,  -- turn_on, create_reminder
    parameters JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'executing', 'success', 'failed')),
    result JSONB,
    executed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actions_conversation ON actions(conversation_id);
CREATE INDEX idx_actions_type ON actions(action_type);
CREATE INDEX idx_actions_status ON actions(status);
```

### Reminders Table
```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    scheduled_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'triggered', 'cancelled')),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_reminders_user ON reminders(user_id);
CREATE INDEX idx_reminders_scheduled ON reminders(scheduled_at) WHERE status = 'pending';
CREATE INDEX idx_reminders_status ON reminders(status);
```

### System Logs Table
```sql
CREATE TABLE system_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(10) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARN', 'ERROR')),
    source VARCHAR(100) NOT NULL,  -- container name
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_logs_timestamp ON system_logs(timestamp DESC);
CREATE INDEX idx_logs_level ON system_logs(level);
CREATE INDEX idx_logs_source ON system_logs(source);

-- Partitioning por dia
CREATE TABLE system_logs_y2024m11d27 PARTITION OF system_logs
    FOR VALUES FROM ('2024-11-27') TO ('2024-11-28');

-- Auto-cleanup logs > 30 dias
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM system_logs
    WHERE timestamp < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;
```

### Config Table
```sql
CREATE TABLE config (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Seed default config
INSERT INTO config (key, value, description) VALUES
    ('wake_word.sensitivity', '0.7', 'Porcupine sensitivity'),
    ('tts.voice', '"pt_BR-faber-medium"', 'Piper TTS voice'),
    ('brain.model', '"qwen2.5:3b"', 'Ollama model'),
    ('brain.temperature', '0.7', 'LLM temperature'),
    ('brain.max_tokens', '200', 'Max response tokens');
```

---

## ⚙️ Configuração PostgreSQL

```conf
# postgresql.conf

# Connections
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# WAL (Write-Ahead Log)
wal_level = replica
max_wal_size = 1GB
min_wal_size = 80MB
wal_keep_size = 512MB

# Checkpoints
checkpoint_completion_target = 0.9

# Logging
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d.log'
log_statement = 'mod'  # Log INSERT, UPDATE, DELETE
log_min_duration_statement = 1000  # Log queries > 1s

# Autovacuum
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min

# Locale (PT-BR)
lc_messages = 'pt_BR.UTF-8'
lc_monetary = 'pt_BR.UTF-8'
lc_numeric = 'pt_BR.UTF-8'
lc_time = 'pt_BR.UTF-8'

# Full-text search
default_text_search_config = 'pg_catalog.portuguese'
```

---

## 🐳 Docker

```dockerfile
FROM postgres:16-alpine

# Install extensions
RUN apk add --no-cache postgresql-contrib

# Init scripts
COPY init.sql /docker-entrypoint-initdb.d/

# Custom config
COPY postgresql.conf /etc/postgresql/postgresql.conf

EXPOSE 5432

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
```

### Docker Compose
```yaml
postgres:
  image: postgres:16-alpine
  container_name: postgres
  ports:
    - "5432:5432"
  environment:
    POSTGRES_DB: mordomo
    POSTGRES_USER: mordomo
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    PGDATA: /var/lib/postgresql/data/pgdata
  volumes:
    - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    - ./postgresql.conf:/etc/postgresql/postgresql.conf
    - postgres-data:/var/lib/postgresql/data
    - postgres-logs:/var/log/postgresql
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U mordomo"]
    interval: 10s
    timeout: 3s
    retries: 3
  networks:
    - mordomo-net
  restart: unless-stopped

volumes:
  postgres-data:
  postgres-logs:
```

---

## 🔌 Connection (Prisma ORM)

```typescript
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id                   String         @id @default(uuid())
  name                 String
  email                String?        @unique
  voiceEnrolled        Boolean        @default(false) @map("voice_enrolled")
  speakerEmbeddingId   String?        @map("speaker_embedding_id")
  createdAt            DateTime       @default(now()) @map("created_at")
  updatedAt            DateTime       @updatedAt @map("updated_at")
  lastInteractionAt    DateTime?      @map("last_interaction_at")
  isActive             Boolean        @default(true) @map("is_active")
  metadata             Json           @default("{}")
  
  conversations        Conversation[]
  reminders            Reminder[]
  
  @@index([email])
  @@map("users")
}

model Conversation {
  id                   String      @id @default(uuid())
  userId               String      @map("user_id")
  startedAt            DateTime    @default(now()) @map("started_at")
  endedAt              DateTime?   @map("ended_at")
  durationSeconds      Int?        @map("duration_seconds")
  messageCount         Int         @default(0) @map("message_count")
  satisfactionScore    Float?      @map("satisfaction_score")
  metadata             Json        @default("{}")
  
  user                 User        @relation(fields: [userId], references: [id], onDelete: Cascade)
  messages             Message[]
  actions              Action[]
  
  @@index([userId])
  @@index([startedAt(sort: Desc)])
  @@map("conversations")
}

// ... outros models
```

### Uso
```typescript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// Criar conversação
const conversation = await prisma.conversation.create({
  data: {
    userId: user.id,
    messages: {
      create: [
        {
          role: 'user',
          content: 'Olá',
          latencyMs: 1200
        }
      ]
    }
  },
  include: {
    user: true,
    messages: true
  }
})

// Buscar histórico do usuário
const history = await prisma.message.findMany({
  where: {
    conversation: {
      userId: user.id
    },
    timestamp: {
      gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // 7 dias
    }
  },
  orderBy: {
    timestamp: 'desc'
  },
  take: 50
})
```

---

## 📈 Métricas

```sql
-- Via pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Queries mais lentas
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Tabelas maiores
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Índices não utilizados
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## 🧪 Testes

```python
# test_database.py
import pytest
from prisma import Prisma

@pytest.fixture
async def db():
    prisma = Prisma()
    await prisma.connect()
    yield prisma
    await prisma.disconnect()

async def test_create_user(db):
    user = await db.user.create(
        data={
            'name': 'Test User',
            'email': 'test@example.com'
        }
    )
    
    assert user.id is not None
    assert user.name == 'Test User'

async def test_create_conversation(db):
    user = await db.user.create(data={'name': 'User'})
    
    conversation = await db.conversation.create(
        data={
            'userId': user.id,
            'messages': {
                'create': [
                    {'role': 'user', 'content': 'Hello'},
                    {'role': 'assistant', 'content': 'Hi!'}
                ]
            }
        },
        include={'messages': True}
    )
    
    assert len(conversation.messages) == 2
    assert conversation.messageCount == 0  # Será atualizado por trigger
```

---

## 🔧 Maintenance

### Backup
```bash
# Dump completo
pg_dump -U mordomo -h localhost mordomo > backup_$(date +%Y%m%d).sql

# Dump apenas schema
pg_dump -U mordomo -h localhost -s mordomo > schema.sql

# Restore
psql -U mordomo -h localhost mordomo < backup.sql
```

### Vacuum & Analyze
```sql
-- Manual vacuum
VACUUM ANALYZE;

-- Vacuum específico
VACUUM ANALYZE messages;

-- Reindex
REINDEX TABLE messages;
```

### Monitoring Queries
```sql
-- Queries em execução
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Bloquear query
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid = 12345;
```

---

## 🚨 Backup Automation

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7

# Criar backup
pg_dump -U mordomo -h postgres mordomo | gzip > "$BACKUP_DIR/mordomo_$DATE.sql.gz"

# Remover backups antigos
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$KEEP_DAYS -delete

echo "Backup completed: mordomo_$DATE.sql.gz"
```

Cron:
```bash
0 2 * * * /backup/backup.sh >> /var/log/postgres-backup.log 2>&1
```

---

## 🔗 Integração

**Usado por:**
- Core API (Prisma ORM)
- Brain (armazenar conversas)
- Dashboard UI (queries de relatórios)

**Expõe:**
- 5432: PostgreSQL protocol

**Monitora:** Prometheus (pg_exporter), Grafana

---

## 📚 Useful Queries

```sql
-- Usuários mais ativos (últimos 7 dias)
SELECT
    u.name,
    COUNT(DISTINCT c.id) as conversations,
    COUNT(m.id) as messages
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.started_at > NOW() - INTERVAL '7 days'
GROUP BY u.id, u.name
ORDER BY messages DESC
LIMIT 10;

-- Intents mais comuns
SELECT
    intent,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence
FROM messages
WHERE intent IS NOT NULL
    AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY intent
ORDER BY count DESC;

-- Latência média por container
SELECT
    metadata->>'source' as container,
    AVG(latency_ms) as avg_latency,
    MAX(latency_ms) as max_latency
FROM messages
WHERE latency_ms IS NOT NULL
GROUP BY metadata->>'source'
ORDER BY avg_latency DESC;
```

---

**Versão:** 1.0  
**Última atualização:** 27/11/2025  
**ORM:** Prisma (TypeScript) / SQLAlchemy (Python)
