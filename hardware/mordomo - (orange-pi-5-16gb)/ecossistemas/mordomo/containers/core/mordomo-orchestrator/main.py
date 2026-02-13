import os
import json
import asyncio
from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
import uvicorn
from nats.aio.client import Client as NATS
from src.core.dispatcher.service_discovery import ServiceDiscovery
from src.core.dispatcher.action_dispatcher import ActionDispatcher
from src.core.events.event_queue import EventQueue, Event, EventPriority
from src.core.events.event_memory import EventMemory
from src.core.events.handlers import EventHandlers

# Variáveis globais para os serviços
nats_client = None
dispatcher = None
event_queue = None
event_memory = None
event_processor_task = None

# Configuração do ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    global nats_client, dispatcher, event_queue, event_memory, event_processor_task
    
    # Startup: Conectar NATS, Carregar Cache, Inicializar LiteLLM
    print("Iniciando Mordomo Orchestrator...")
    print(f"LLM Primária: {os.getenv('LLM_PRIMARY_MODEL', 'Não definida')}")
    print(f"LLM Fallback: {os.getenv('LLM_FALLBACK_MODEL', 'ollama/qwen2.5:1.5b')}")
    
    # Conectar ao NATS
    nats_url = os.getenv("NATS_URL", "nats://nats:4222")
    nats_client = NATS()
    await nats_client.connect(nats_url)
    print(f"Conectado ao NATS em {nats_url}")
    
    # Inicializar Service Discovery e Dispatcher
    discovery = ServiceDiscovery()
    dispatcher = ActionDispatcher(nats_client, discovery)
    await dispatcher.initialize()
    
    # Inicializar Event Memory (armazena últimos 500 eventos, 24h de retenção)
    event_memory = EventMemory(max_events=500, retention_hours=24)
    print("Event Memory inicializada (500 eventos, 24h de retenção)")
    
    # Inicializar Event Queue e Handlers
    event_queue = EventQueue()
    handlers = EventHandlers(dispatcher, event_memory)  # Passa event_memory para os handlers
    
    # Registrar handlers para eventos
    event_queue.register_handler("intrusion_detected", handlers.handle_intrusion_detected)
    event_queue.register_handler("message_received", handlers.handle_message_received)
    event_queue.register_handler("temperature_alert", handlers.handle_temperature_alert)
    event_queue.register_handler("package_delivered", handlers.handle_package_delivered)
    
    # Subscrever aos eventos dos módulos (wildcard: todos os eventos)
    async def handle_module_event(msg):
        """Callback para eventos assíncronos dos módulos."""
        try:
            data = json.loads(msg.data.decode())
            
            # Determina prioridade baseado no tipo de evento
            priority = EventPriority.NORMAL
            if data.get('priority') == 'critical':
                priority = EventPriority.CRITICAL
            elif data.get('priority') == 'high':
                priority = EventPriority.HIGH
            elif data.get('priority') == 'low':
                priority = EventPriority.LOW
            
            # Extrai módulo do subject (ex: "security.event.intrusion" -> "security")
            module = msg.subject.split('.')[0]
            event_type = data.get('event_type', msg.subject.split('.')[-1])
            
            event = Event(
                module=module,
                event_type=event_type,
                data=data,
                priority=priority
            )
            
            await event_queue.push(event)
        except Exception as e:
            print(f"Erro ao processar evento de módulo: {e}")
    
    await nats_client.subscribe("*.event.>", cb=handle_module_event)
    
    # Iniciar processamento de eventos em background
    event_processor_task = asyncio.create_task(event_queue.start_processing())
    
    yield
    
    # Shutdown: Desconectar NATS, Salvar estados
    print("Desligando Mordomo Orchestrator...")
    if event_queue:
        await event_queue.stop()
    if event_processor_task:
        event_processor_task.cancel()
    if nats_client:
        await nats_client.close()
    print("NATS desconectado.")

app = FastAPI(
    title="Mordomo Orchestrator",
    description="Núcleo unificado de orquestração do Mordomo (Session + Core)",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "component": "mordomo-orchestrator"}

@app.get("/api/events/recent")
async def get_recent_events(
    minutes: int = Query(30, description="Janela de tempo em minutos"),
    module: str = Query(None, description="Filtrar por módulo (ex: mensagens, iot, rpa)"),
    event_type: str = Query(None, description="Filtrar por tipo de evento")
):
    """
    Retorna eventos recentes para consulta do LLM ou Dashboard.
    
    Exemplos:
    - GET /api/events/recent?minutes=10
    - GET /api/events/recent?module=mensagens&minutes=30
    - GET /api/events/recent?event_type=message_received
    """
    if not event_memory:
        return {"error": "Event Memory não inicializada"}
    
    events = event_memory.query_recent(minutes=minutes, module=module, event_type=event_type)
    return {
        "total": len(events),
        "query": {
            "minutes": minutes,
            "module": module,
            "event_type": event_type
        },
        "events": events
    }

@app.get("/api/events/context")
async def get_event_context(
    query: str = Query(..., description="Query do usuário (ex: 'quem me mandou mensagem há 10 minutos?')"),
    max_events: int = Query(5, description="Máximo de eventos a retornar")
):
    """
    Gera contexto formatado para o LLM com base em uma query do usuário.
    
    Exemplo:
    - GET /api/events/context?query=quem me mandou mensagem no whatsapp há 10 minutos?
    """
    if not event_memory:
        return {"error": "Event Memory não inicializada"}
    
    context = event_memory.get_context_for_llm(query, max_events=max_events)
    return {
        "query": query,
        "context": context,
        "stats": event_memory.get_stats()
    }

@app.get("/api/events/stats")
async def get_event_stats():
    """Retorna estatísticas da Event Memory."""
    if not event_memory:
        return {"error": "Event Memory não inicializada"}
    
    return event_memory.get_stats()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
