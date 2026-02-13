from nats.aio.client import Client as NATS
import json
import asyncio
import uuid
from typing import Dict, Optional, Callable
from .service_discovery import ServiceDiscovery

class ActionDispatcher:
    def __init__(self, nats_client: NATS, service_discovery: ServiceDiscovery):
        self.nats = nats_client
        self.discovery = service_discovery
        
        # Armazena callbacks de resposta pendentes (request-reply pattern)
        self.pending_requests: Dict[str, asyncio.Future] = {}
        
        # Cache local de ações disponíveis (atualiza do Consul)
        self.actions_cache: Dict[str, Dict] = {}
        
    async def initialize(self):
        """
        Inicializa o dispatcher:
        1. Carrega ações de todos os módulos registrados.
        2. Subscreve aos tópicos de resposta.
        """
        print("Inicializando Action Dispatcher...")
        
        # Descobre módulos registrados
        modules = self.discovery.list_registered_modules()
        print(f"Módulos descobertos: {modules}")
        
        # Carrega ações de cada módulo
        for module in modules:
            actions = self.discovery.get_module_actions(module.replace('-module', ''))
            if actions:
                self.actions_cache[module.replace('-module', '')] = actions
                print(f"  [{module}] {len(actions)} ações carregadas.")
        
        # Subscreve aos tópicos de resposta genéricos
        await self.nats.subscribe("*.response", cb=self._handle_response)
        print("Dispatcher pronto para despachar ações!")

    async def dispatch(self, module: str, action: str, params: Dict, timeout: float = 10.0) -> Dict:
        """
        Despacha uma ação para um módulo e aguarda resposta.
        
        :param module: Nome do módulo (ex: "iot", "rpa", "mensagens")
        :param action: Nome da ação (ex: "turn_on", "send_message")
        :param params: Parâmetros da ação
        :param timeout: Tempo máximo de espera pela resposta
        :return: Resposta do módulo
        """
        # 1. Valida se a ação existe
        if module not in self.actions_cache:
            raise ValueError(f"Módulo '{module}' não está registrado no Consul.")
        
        if action not in self.actions_cache[module]:
            raise ValueError(f"Ação '{action}' não existe no módulo '{module}'.")
        
        # 2. Gera ID único para rastrear a resposta
        request_id = str(uuid.uuid4())
        
        # 3. Cria Future para aguardar resposta
        response_future = asyncio.Future()
        self.pending_requests[request_id] = response_future
        
        # 4. Monta payload
        payload = {
            "request_id": request_id,
            "action": action,
            "params": params
        }
        
        # 5. Publica no NATS
        subject = f"{module}.command"
        await self.nats.publish(subject, json.dumps(payload).encode())
        print(f"📤 Despachado: {subject} | {action} | ID: {request_id[:8]}...")
        
        # 6. Aguarda resposta (com timeout)
        try:
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            del self.pending_requests[request_id]
            raise TimeoutError(f"Módulo '{module}' não respondeu em {timeout}s.")

    async def _handle_response(self, msg):
        """
        Callback para processar respostas dos módulos.
        Formato esperado: {"request_id": "...", "status": "success/error", "data": {...}}
        """
        try:
            response = json.loads(msg.data.decode())
            request_id = response.get("request_id")
            
            if request_id and request_id in self.pending_requests:
                future = self.pending_requests.pop(request_id)
                if not future.done():
                    future.set_result(response)
                    print(f"📥 Resposta recebida: ID {request_id[:8]}... | Status: {response.get('status')}")
        except Exception as e:
            print(f"Erro ao processar resposta: {e}")

    def get_available_actions(self, module: Optional[str] = None) -> Dict:
        """
        Retorna ações disponíveis (útil para o LLM/Brain conhecer capabilities).
        """
        if module:
            return {module: self.actions_cache.get(module, {})}
        return self.actions_cache
