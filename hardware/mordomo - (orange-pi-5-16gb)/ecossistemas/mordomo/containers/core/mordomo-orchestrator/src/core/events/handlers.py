from .event_queue import Event, EventPriority, EventQueue
from .event_memory import EventMemory
from ..dispatcher.action_dispatcher import ActionDispatcher
from datetime import datetime

class EventHandlers:
    """
    Define os handlers (políticas de reação) para eventos dos módulos.
    Agora com Event Memory para permitir queries contextuais do LLM.
    """
    def __init__(self, dispatcher: ActionDispatcher, event_memory: EventMemory):
        self.dispatcher = dispatcher
        self.memory = event_memory

    async def handle_intrusion_detected(self, event: Event):
        """
        EVENTO CRÍTICO: Intruso detectado no módulo Security.
        
        Ações:
        1. Ligar todas as luzes da casa.
        2. Tocar sirene.
        3. Enviar notificação push.
        4. Avisar por voz.
        """
        print(f"🚨 ALERTA DE SEGURANÇA: {event.data}")
        
        # Armazena na memória para consultas posteriores
        self.memory.store({
            "timestamp": datetime.utcnow().isoformat(),
            "module": event.module,
            "event_type": event.event_type,
            "priority": event.priority.name,
            "data": event.data,
            "handler_response": "Acionei luzes, sirene e notificações de emergência"
        })
        
        # 1. Ligar todas as luzes
        try:
            await self.dispatcher.dispatch(
                module="iot",
                action="turn_on_all_lights",
                params={},
                timeout=3.0
            )
        except Exception as e:
            print(f"Erro ao ligar luzes: {e}")
        
        # 2. Tocar sirene
        try:
            await self.dispatcher.dispatch(
                module="iot",
                action="activate_siren",
                params={"duration": 30},
                timeout=2.0
            )
        except Exception as e:
            print(f"Erro ao tocar sirene: {e}")
        
        # 3. Enviar notificação (se módulo de mensagens existir)
        try:
            await self.dispatcher.dispatch(
                module="mensagens",
                action="send_push",
                params={
                    "title": "⚠️ INTRUSO DETECTADO",
                    "body": f"Câmera: {event.data.get('camera_id')}",
                    "priority": "high"
                },
                timeout=5.0
            )
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
        
        # 4. Avisar por voz (publica evento para TTS)
        # await self.dispatcher.nats.publish(
        #     "tts.urgent.speak",
        #     json.dumps({"text": "Atenção! Intruso detectado na câmera externa!"}).encode()
        # )

    async def handle_message_received(self, event: Event):
        """
        Evento de prioridade ALTA: Nova mensagem recebida (WhatsApp, SMS, etc.).
        
        Ações:
        1. Verificar se o usuário está em casa (via Bluetooth Scanner).
        2. Se estiver, avisar por voz.
        3. Se não estiver, apenas logar.
        """
        sender = event.data.get("sender", "Desconhecido")
        platform = event.data.get("platform", "mensagem")
        preview = event.data.get("preview", "")
        
        print(f"💬 Nova mensagem de {sender}: {preview[:50]}...")
        
        # Armazena na memória com detalhes completos
        self.memory.store({
            "timestamp": datetime.utcnow().isoformat(),
            "module": event.module,
            "event_type": event.event_type,
            "priority": event.priority.name,
            "data": {
                "sender": sender,
                "platform": platform,
                "preview": preview,
                "full_message": event.data.get("full_message", preview)
            },
            "handler_response": f"Avisei sobre mensagem de {sender} via {platform}"
        })
        
        # TODO: Checar presença do usuário
        # user_home = await check_user_presence()
        
        # Se estiver em casa, avisar
        # if user_home:
        #     await dispatcher.nats.publish(
        #         "tts.speak",
        #         json.dumps({"text": f"Você recebeu uma mensagem de {sender}"}).encode()
        #     )

    async def handle_temperature_alert(self, event: Event):
        """
        Evento de prioridade NORMAL: Temperatura anormal detectada.
        """
        temp = event.data.get("temperature")
        location = event.data.get("location", "desconhecido")
        
        print(f"🌡️ Alerta de temperatura: {temp}°C em {location}")
        
        action_taken = "Nenhuma"
        
        # Se muito quente, ligar ar-condicionado
        if temp > 28:
            try:
                await self.dispatcher.dispatch(
                    module="iot",
                    action="set_ac_temperature",
                    params={"location": location, "target_temp": 24},
                    timeout=5.0
                )
                action_taken = f"Ajustei ar-condicionado para 24°C"
            except Exception as e:
                print(f"Erro ao ajustar AC: {e}")
                action_taken = f"Tentei ajustar AC mas houve erro"
        
        # Armazena na memória
        self.memory.store({
            "timestamp": datetime.utcnow().isoformat(),
            "module": event.module,
            "event_type": event.event_type,
            "priority": event.priority.name,
            "data": {
                "temperature": temp,
                "location": location
            },
            "handler_response": action_taken
        })

    async def handle_package_delivered(self, event: Event):
        """
        Evento de prioridade BAIXA: Encomenda entregue (sensor de porta).
        """
        print(f"📦 Encomenda entregue: {event.data}")
        
        # Armazena na memória para consultas posteriores
        self.memory.store({
            "timestamp": datetime.utcnow().isoformat(),
            "module": event.module,
            "event_type": event.event_type,
            "priority": event.priority.name,
            "data": event.data,
            "handler_response": "Encomenda registrada, sem ação imediata"
        })
        # Apenas logar, sem ação imediata
