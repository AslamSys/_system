import asyncio
from typing import Dict, Callable, Optional
from enum import IntEnum
import json

class EventPriority(IntEnum):
    """Prioridade dos eventos (maior = mais urgente)."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class Event:
    def __init__(self, module: str, event_type: str, data: Dict, priority: EventPriority = EventPriority.NORMAL):
        self.module = module
        self.event_type = event_type
        self.data = data
        self.priority = priority
        self.timestamp = asyncio.get_event_loop().time()

    def __lt__(self, other):
        # Para PriorityQueue: maior prioridade primeiro, depois mais antigo
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.timestamp < other.timestamp

    def __repr__(self):
        return f"Event({self.module}.{self.event_type}, Priority={self.priority.name})"

class EventQueue:
    def __init__(self, max_size: int = 1000):
        self.queue = asyncio.PriorityQueue(maxsize=max_size)
        self.handlers: Dict[str, Callable] = {}
        self.running = False

    async def push(self, event: Event):
        """Adiciona evento à fila."""
        await self.queue.put(event)
        print(f"📥 Evento enfileirado: {event}")

    def register_handler(self, event_type: str, handler: Callable):
        """
        Registra um handler para um tipo de evento.
        Ex: register_handler("intrusion_detected", handle_intrusion)
        """
        self.handlers[event_type] = handler
        print(f"🔧 Handler registrado para: {event_type}")

    async def start_processing(self):
        """Inicia o loop de processamento de eventos."""
        self.running = True
        print("🚀 Event Queue iniciada. Processando eventos...")
        
        while self.running:
            try:
                # Pega evento com maior prioridade
                event = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue # Nenhum evento, continua aguardando
            except Exception as e:
                print(f"Erro ao processar evento: {e}")

    async def _process_event(self, event: Event):
        """Processa um evento, chamando o handler apropriado."""
        print(f"⚙️ Processando: {event}")
        
        handler = self.handlers.get(event.event_type)
        if handler:
            try:
                await handler(event)
            except Exception as e:
                print(f"❌ Erro no handler de '{event.event_type}': {e}")
        else:
            print(f"⚠️ Nenhum handler registrado para '{event.event_type}'")

    async def stop(self):
        """Para o processamento de eventos."""
        self.running = False
        print("🛑 Event Queue parada.")
