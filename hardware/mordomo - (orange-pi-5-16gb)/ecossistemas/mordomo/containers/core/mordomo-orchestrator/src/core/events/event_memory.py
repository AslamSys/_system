from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import deque
import json

class EventMemory:
    """
    Armazena histórico de eventos recentes para consulta contextual pelo LLM.
    Permite que o usuário pergunte sobre notificações passadas.
    
    Exemplos:
    - "Sobre o que estávamos falando agora mesmo quanto aos RPAs?"
    - "Quem me mandou mensagem no WhatsApp há 10 minutos?"
    - "Qual foi a última encomenda entregue?"
    """
    
    def __init__(self, max_events: int = 500, retention_hours: int = 24):
        """
        :param max_events: Máximo de eventos mantidos em memória (FIFO)
        :param retention_hours: Tempo de retenção em horas (eventos mais antigos são descartados)
        """
        self.max_events = max_events
        self.retention_hours = retention_hours
        
        # Deque circular para armazenamento eficiente (FIFO automático)
        self.events: deque = deque(maxlen=max_events)
        
        # Índice por módulo para busca rápida
        self.events_by_module: Dict[str, List[Dict]] = {}
        
        # Índice por tipo de evento
        self.events_by_type: Dict[str, List[Dict]] = {}

    def store(self, event: Dict):
        """
        Armazena um evento no histórico.
        
        :param event: Dicionário com estrutura:
        {
            "timestamp": "2025-12-04T15:30:00Z",
            "module": "mensagens",
            "event_type": "message_received",
            "priority": "high",
            "data": {
                "sender": "João Silva",
                "platform": "whatsapp",
                "preview": "Confirma reunião amanhã?",
                "full_message": "...",
                ...
            },
            "handler_response": "Avisei você por voz sobre a mensagem de João Silva"
        }
        """
        # Adiciona timestamp se não existir
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow().isoformat()
        
        # Armazena no deque principal
        self.events.append(event)
        
        # Indexa por módulo
        module = event.get("module")
        if module:
            if module not in self.events_by_module:
                self.events_by_module[module] = []
            self.events_by_module[module].append(event)
        
        # Indexa por tipo
        event_type = event.get("event_type")
        if event_type:
            if event_type not in self.events_by_type:
                self.events_by_type[event_type] = []
            self.events_by_type[event_type].append(event)
        
        # Cleanup periódico (remove eventos antigos)
        self._cleanup_old_events()

    def query_recent(self, minutes: int = 30, module: Optional[str] = None, 
                     event_type: Optional[str] = None) -> List[Dict]:
        """
        Busca eventos recentes.
        
        :param minutes: Janela de tempo (últimos N minutos)
        :param module: Filtrar por módulo específico (ex: "mensagens", "rpa", "iot")
        :param event_type: Filtrar por tipo de evento (ex: "message_received", "package_delivered")
        :return: Lista de eventos ordenados por timestamp (mais recente primeiro)
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        results = []
        for event in self.events:
            event_time = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
            
            # Filtro de tempo
            if event_time < cutoff_time:
                continue
            
            # Filtro de módulo
            if module and event.get("module") != module:
                continue
            
            # Filtro de tipo
            if event_type and event.get("event_type") != event_type:
                continue
            
            results.append(event)
        
        # Ordena por timestamp decrescente (mais recente primeiro)
        results.sort(key=lambda e: e["timestamp"], reverse=True)
        return results

    def query_by_keyword(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        Busca eventos que contenham uma palavra-chave no conteúdo.
        Útil para perguntas como "sobre o que estávamos falando de RPA?"
        
        :param keyword: Palavra-chave (case-insensitive)
        :param max_results: Número máximo de resultados
        :return: Lista de eventos relevantes
        """
        keyword_lower = keyword.lower()
        results = []
        
        for event in reversed(self.events):  # Mais recentes primeiro
            # Busca na estrutura JSON inteira (serializa para string)
            event_str = json.dumps(event, ensure_ascii=False).lower()
            
            if keyword_lower in event_str:
                results.append(event)
                
                if len(results) >= max_results:
                    break
        
        return results

    def get_last_event_by_module(self, module: str) -> Optional[Dict]:
        """
        Retorna o último evento de um módulo específico.
        
        Exemplo: get_last_event_by_module("mensagens") para saber última mensagem.
        """
        module_events = self.events_by_module.get(module, [])
        return module_events[-1] if module_events else None

    def get_context_for_llm(self, query: str, max_events: int = 5) -> str:
        """
        Gera contexto formatado para o LLM com base em uma query do usuário.
        
        :param query: Pergunta do usuário (ex: "quem me mandou mensagem há 10 minutos?")
        :param max_events: Número máximo de eventos a incluir
        :return: String formatada para injetar no prompt do LLM
        """
        # Heurística simples: detecta menção a tempo
        minutes = self._extract_time_from_query(query)
        
        # Busca eventos recentes
        events = self.query_recent(minutes=minutes)[:max_events]
        
        if not events:
            return "Nenhum evento recente encontrado nos últimos {} minutos.".format(minutes)
        
        # Formata para o LLM
        context = f"Eventos recentes (últimos {minutes} minutos):\n\n"
        for i, event in enumerate(events, 1):
            timestamp = event.get("timestamp", "")
            module = event.get("module", "desconhecido")
            event_type = event.get("event_type", "")
            data = event.get("data", {})
            
            context += f"{i}. [{timestamp}] {module}.{event_type}\n"
            
            # Adiciona detalhes relevantes baseado no tipo
            if event_type == "message_received":
                sender = data.get("sender", "Desconhecido")
                platform = data.get("platform", "")
                preview = data.get("preview", "")
                context += f"   De: {sender} ({platform})\n"
                context += f"   Mensagem: {preview}\n"
            
            elif event_type == "package_delivered":
                tracking = data.get("tracking_code", "N/A")
                context += f"   Rastreio: {tracking}\n"
            
            elif event_type == "intrusion_detected":
                camera = data.get("camera_id", "")
                context += f"   Câmera: {camera}\n"
            
            elif event_type == "rpa_task_completed":
                task = data.get("task_name", "")
                status = data.get("status", "")
                context += f"   Tarefa: {task} ({status})\n"
            
            # Adiciona dados brutos se houver
            if data:
                context += f"   Dados: {json.dumps(data, ensure_ascii=False, indent=2)}\n"
            
            context += "\n"
        
        return context

    def _extract_time_from_query(self, query: str) -> int:
        """
        Extrai janela de tempo da query do usuário.
        
        Exemplos:
        - "há 10 minutos" -> 10
        - "agora mesmo" -> 5
        - "há uma hora" -> 60
        - "hoje" -> 1440 (24h)
        """
        query_lower = query.lower()
        
        # Padrões de tempo
        if "agora mesmo" in query_lower or "agora" in query_lower:
            return 5
        
        if "há 10 minutos" in query_lower or "10 minutos" in query_lower:
            return 10
        
        if "há 30 minutos" in query_lower or "30 minutos" in query_lower or "meia hora" in query_lower:
            return 30
        
        if "há uma hora" in query_lower or "1 hora" in query_lower:
            return 60
        
        if "hoje" in query_lower or "últimas horas" in query_lower:
            return 1440  # 24 horas
        
        # Default: última hora
        return 60

    def _cleanup_old_events(self):
        """
        Remove eventos mais antigos que o tempo de retenção.
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        # Limpa deque principal (já é automático por maxlen, mas filtramos por tempo)
        # Recria deque apenas com eventos válidos
        valid_events = deque(maxlen=self.max_events)
        for event in self.events:
            event_time = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
            if event_time >= cutoff_time:
                valid_events.append(event)
        
        self.events = valid_events
        
        # Limpa índices
        self.events_by_module = {}
        self.events_by_type = {}
        
        # Reconstrói índices
        for event in self.events:
            module = event.get("module")
            if module:
                if module not in self.events_by_module:
                    self.events_by_module[module] = []
                self.events_by_module[module].append(event)
            
            event_type = event.get("event_type")
            if event_type:
                if event_type not in self.events_by_type:
                    self.events_by_type[event_type] = []
                self.events_by_type[event_type].append(event)

    def clear(self):
        """Limpa toda a memória de eventos (útil para testes)."""
        self.events.clear()
        self.events_by_module.clear()
        self.events_by_type.clear()

    def get_stats(self) -> Dict:
        """Retorna estatísticas da memória de eventos."""
        return {
            "total_events": len(self.events),
            "modules": list(self.events_by_module.keys()),
            "event_types": list(self.events_by_type.keys()),
            "oldest_event": self.events[0]["timestamp"] if self.events else None,
            "newest_event": self.events[-1]["timestamp"] if self.events else None
        }
