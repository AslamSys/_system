# Event Memory - Memória Contextual de Eventos

## 📋 Propósito
Armazena histórico de eventos recentes em memória para permitir que o LLM responda perguntas contextuais sobre notificações passadas.

## 🎯 Casos de Uso

### Perguntas sobre Eventos Passados
```
Usuário: "Aslam, sobre o que estávamos falando agora mesmo quanto aos RPAs?"
LLM consulta: GET /api/events/context?query=sobre o que estávamos falando quanto aos RPAs
Resposta: Eventos recentes com contexto de tarefas RPA executadas

Usuário: "Quem me mandou mensagem no WhatsApp há 10 minutos quando você me avisou?"
LLM consulta: GET /api/events/context?query=quem me mandou mensagem no whatsapp há 10 minutos
Resposta: Detalhes da mensagem (remetente, plataforma, preview)

Usuário: "Qual foi a última encomenda entregue?"
LLM consulta: GET /api/events/recent?event_type=package_delivered&minutes=1440
Resposta: Dados da última entrega (tracking, timestamp)
```

## 🧠 Arquitetura

### Estrutura de Dados Armazenada
```json
{
  "timestamp": "2025-12-04T15:30:00Z",
  "module": "mensagens",
  "event_type": "message_received",
  "priority": "HIGH",
  "data": {
    "sender": "João Silva",
    "platform": "whatsapp",
    "preview": "Confirma reunião amanhã às 14h?",
    "full_message": "Oi! Confirma reunião amanhã às 14h? Abraço"
  },
  "handler_response": "Avisei você por voz sobre a mensagem de João Silva via whatsapp"
}
```

### Indexação
- **Deque Circular:** FIFO automático (máx 500 eventos)
- **Índice por Módulo:** `events_by_module["mensagens"]`
- **Índice por Tipo:** `events_by_type["message_received"]`
- **Retenção:** 24 horas (configurável)

## 🔌 API REST

### 1. Eventos Recentes
```http
GET /api/events/recent?minutes=30&module=mensagens

Response:
{
  "total": 3,
  "query": {
    "minutes": 30,
    "module": "mensagens",
    "event_type": null
  },
  "events": [
    {
      "timestamp": "2025-12-04T15:30:00Z",
      "module": "mensagens",
      "event_type": "message_received",
      "data": {...},
      "handler_response": "..."
    }
  ]
}
```

### 2. Contexto para LLM
```http
GET /api/events/context?query=quem me mandou mensagem há 10 minutos

Response:
{
  "query": "quem me mandou mensagem há 10 minutos",
  "context": "Eventos recentes (últimos 10 minutos):\n\n1. [2025-12-04T15:30:00Z] mensagens.message_received\n   De: João Silva (whatsapp)\n   Mensagem: Confirma reunião amanhã?\n\n",
  "stats": {
    "total_events": 45,
    "modules": ["mensagens", "iot", "security"],
    "event_types": ["message_received", "temperature_alert", "intrusion_detected"]
  }
}
```

### 3. Estatísticas
```http
GET /api/events/stats

Response:
{
  "total_events": 45,
  "modules": ["mensagens", "iot", "security", "rpa"],
  "event_types": ["message_received", "package_delivered", "intrusion_detected", "temperature_alert"],
  "oldest_event": "2025-12-03T16:00:00Z",
  "newest_event": "2025-12-04T15:30:00Z"
}
```

## 💡 Integração com LLM

### Fluxo de Consulta Contextual
```
1. Usuário pergunta: "Quem me mandou mensagem há 10 minutos?"
   ↓
2. STT transcreve → Orchestrator recebe
   ↓
3. LLM detecta que é uma query sobre eventos passados
   ↓
4. LLM faz chamada: GET /api/events/context?query=...
   ↓
5. Event Memory retorna contexto formatado
   ↓
6. LLM usa contexto para responder: "Foi João Silva via WhatsApp, ele perguntou sobre a reunião de amanhã"
   ↓
7. TTS sintetiza resposta
```

### Exemplo de Prompt com Contexto
```
SYSTEM: Você é o Mordomo Aslam, assistente de voz inteligente.

USER: Quem me mandou mensagem no WhatsApp há 10 minutos?

CONTEXT (da Event Memory):
Eventos recentes (últimos 10 minutos):

1. [2025-12-04T15:30:00Z] mensagens.message_received
   De: João Silva (whatsapp)
   Mensagem: Confirma reunião amanhã às 14h?

ASSISTANT: Foi o João Silva. Ele enviou uma mensagem pelo WhatsApp perguntando se você pode confirmar a reunião de amanhã às 14h.
```

## 🔧 Configuração

### Parâmetros do Constructor
```python
event_memory = EventMemory(
    max_events=500,        # Máximo de eventos em memória
    retention_hours=24     # Tempo de retenção (cleanup automático)
)
```

### Variáveis de Ambiente
```bash
EVENT_MEMORY_MAX_EVENTS=500      # Default: 500
EVENT_MEMORY_RETENTION_HOURS=24  # Default: 24
```

## 📊 Performance

### Recursos
- **RAM:** ~5-10MB (500 eventos com dados médios)
- **CPU:** <1% (operações de busca em memória são O(n) mas n é pequeno)
- **Latência de Busca:** <5ms para consultas típicas

### Limitações
- **In-Memory:** Dados perdidos em restart (futuramente pode persistir em Redis/PostgreSQL)
- **Max Events:** 500 eventos (configurável, mas consumo de RAM cresce)
- **Busca por Keyword:** Simples (JSON serializado), não é busca semântica

## 🚀 Melhorias Futuras

### 1. Persistência (Redis/PostgreSQL)
```python
# Salvar eventos no Redis com TTL automático
await redis.setex(
    f"event:{event_id}",
    86400,  # 24h TTL
    json.dumps(event)
)
```

### 2. Busca Semântica (Qdrant)
```python
# Armazenar embeddings de eventos para busca por similaridade
embedding = await embedder(event_description)
await qdrant.upsert("events", {
    "id": event_id,
    "vector": embedding,
    "payload": event_data
})

# Query semântica
results = await qdrant.search("events", query_vector=user_query_embedding)
```

### 3. Agregação e Resumo
```python
# Resumir eventos relacionados
summary = await llm.summarize(
    events=event_memory.query_recent(minutes=60, module="mensagens"),
    prompt="Resuma as mensagens recebidas na última hora"
)
```

## 📝 Exemplos de Queries Suportadas

### Temporais
- "O que aconteceu nos últimos 10 minutos?"
- "Alguém me mandou mensagem hoje?"
- "Qual foi a última encomenda entregue?"

### Por Módulo
- "Teve algum alerta de segurança?"
- "Quais tarefas de RPA foram executadas?"
- "Houve algum problema com IoT?"

### Por Tipo de Evento
- "Recebi alguma mensagem do João?"
- "Teve alguma encomenda hoje?"
- "O ar-condicionado foi acionado?"

### Contextuais
- "Sobre o que estávamos falando?"
- "Por que você ligou as luzes?"
- "Quem tocou a campainha?"
