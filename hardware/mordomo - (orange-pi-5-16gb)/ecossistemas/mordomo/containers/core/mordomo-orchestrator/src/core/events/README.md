# Event System - Sistema de Notificações Assíncronas

## 📋 Propósito
Permite que módulos externos notifiquem o Mordomo de eventos importantes **sem requisição prévia**, com processamento por prioridade, reações automáticas e **memória contextual** para consultas posteriores.

## 🔔 Como os Módulos Publicam Eventos

### Padrão de Subject NATS
```
{module}.event.{event_type}

Exemplos:
- security.event.intrusion_detected
- mensagens.event.message_received
- iot.event.temperature_alert
```

### Formato de Payload
```json
{
  "event_type": "intrusion_detected",
  "priority": "critical",  // critical, high, normal, low
  "data": {
    "camera_id": "cam_front_door",
    "timestamp": "2025-12-03T15:30:00Z",
    "snapshot_url": "http://..."
  }
}
```

### Exemplo (Módulo Security)
```python
import nats
import json

nc = await nats.connect("nats://nats:4222")

# Publica evento crítico
event = {
    "event_type": "intrusion_detected",
    "priority": "critical",
    "data": {
        "camera_id": "cam_front_door",
        "confidence": 0.95
    }
}

await nc.publish("security.event.intrusion_detected", json.dumps(event).encode())
```

## ⚙️ Handlers Registrados

| Evento | Prioridade | Ações |
|--------|-----------|-------|
| `intrusion_detected` | CRITICAL | Ligar luzes, sirene, notificação push, TTS |
| `message_received` | HIGH | Avisar por voz (se usuário em casa) |
| `temperature_alert` | NORMAL | Ajustar AC se > 28°C |
| `package_delivered` | LOW | Apenas logar |

## 🚨 Sistema de Prioridades

### CRITICAL (4)
- Eventos de segurança (intruso, incêndio, vazamento de gás).
- Processamento imediato, interrompe outras tarefas.

### HIGH (3)
- Mensagens importantes, chamadas perdidas.
- Processado antes de eventos normais.

### NORMAL (2)
- Alertas de temperatura, lembretes.
- Processamento padrão.

### LOW (1)
- Notificações triviais (encomenda entregue, atualização de status).
- Processado quando a fila está vazia.

## 📝 Como Adicionar Novos Handlers

1. Adicionar método em `src/core/events/handlers.py`:
```python
async def handle_gas_leak(self, event: Event):
    print("🔥 VAZAMENTO DE GÁS DETECTADO!")
    await self.dispatcher.dispatch("iot", "cut_gas_valve", {})
    # TTS urgente, etc.
```

2. Registrar no `main.py`:
```python
event_queue.register_handler("gas_leak", handlers.handle_gas_leak)
```

## 🔄 Fluxo Completo

```
┌─────────────────────────────────────────────┐
│  Módulo Security (intruso detectado)        │
│  NATS publish: security.event.intrusion     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Orchestrator recebe via wildcard *.event.> │
│  Cria Event(priority=CRITICAL)              │
│  Adiciona na PriorityQueue                  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Event Processor pega evento com maior      │
│  prioridade e chama handler                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  handle_intrusion_detected():               │
│  1. Liga luzes (via Dispatcher)             │
│  2. Toca sirene                             │
│  3. Envia push notification                 │
│  4. TTS: "Intruso detectado!"               │
└─────────────────────────────────────────────┘
```

## 💡 Benefícios

1. **Desacoplamento**: Módulos não precisam conhecer o Orchestrator, apenas publicam eventos.
2. **Priorização**: Eventos críticos nunca esperam.
3. **Escalabilidade**: Fila pode processar milhares de eventos sem perder ordem.
4. **Extensibilidade**: Adicionar novo evento = criar handler + registrar.
5. **Memória Contextual**: Todos os eventos são armazenados para consultas posteriores.

---

## 🧠 Event Memory - Consultas Contextuais

### Propósito
Armazena histórico de eventos processados para permitir que o LLM responda perguntas sobre notificações passadas.

### Exemplos de Queries
```
"Quem me mandou mensagem no WhatsApp há 10 minutos?"
"Sobre o que estávamos falando quanto aos RPAs?"
"Qual foi a última encomenda entregue?"
"Por que você ligou as luzes?"
"Houve algum alerta de segurança hoje?"
```

### Como Funciona
1. **Armazenamento Automático**: Cada handler salva o evento na Event Memory
2. **Indexação**: Eventos indexados por módulo, tipo e timestamp
3. **API REST**: LLM consulta via `/api/events/context?query=...`
4. **Contexto Formatado**: Event Memory retorna texto pronto para o prompt do LLM

### Estrutura Armazenada
```json
{
  "timestamp": "2025-12-04T15:30:00Z",
  "module": "mensagens",
  "event_type": "message_received",
  "priority": "HIGH",
  "data": {
    "sender": "João Silva",
    "platform": "whatsapp",
    "preview": "Confirma reunião amanhã?"
  },
  "handler_response": "Avisei sobre mensagem de João Silva"
}
```

### Capacidade
- **Max Events**: 500 (FIFO circular)
- **Retenção**: 24 horas
- **RAM**: ~5-10MB
- **Latência**: <5ms

📖 **Documentação completa**: [EVENT_MEMORY.md](EVENT_MEMORY.md)
