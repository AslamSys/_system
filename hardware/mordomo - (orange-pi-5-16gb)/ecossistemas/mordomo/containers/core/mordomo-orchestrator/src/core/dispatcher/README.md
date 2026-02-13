# Action Dispatcher - Módulo de Roteamento Universal

## 📋 Propósito
Sistema de despacho genérico que roteia comandos do Orchestrator para módulos externos (IoT, RPA, Mensagens, etc.) usando **Service Discovery (Consul)** e **NATS Pub/Sub**.

## 🔌 Como os Módulos se Registram

Cada módulo externo ao iniciar deve:

### 1. Registrar Serviço no Consul
```python
import consul

c = consul.Consul(host="consul", port=8500)
c.agent.service.register(
    name="iot-module",
    service_id="iot-module-rpi3b",
    address="10.0.0.10",
    port=8001,
    tags=["mordomo", "iot"],
    check=consul.Check.http("http://10.0.0.10:8001/health", interval="10s")
)
```

### 2. Publicar Capabilities no Consul KV
```python
import json

actions = {
    "turn_on": {"params": ["device_id"], "timeout": 5},
    "turn_off": {"params": ["device_id"], "timeout": 5},
    "set_brightness": {"params": ["device_id", "level"], "timeout": 5}
}

c.kv.put("modules/iot/actions", json.dumps(actions))
```

### 3. Escutar Comandos no NATS
```python
import nats
import json

async def handle_command(msg):
    data = json.loads(msg.data.decode())
    request_id = data['request_id']
    action = data['action']
    params = data['params']
    
    # Executa ação...
    result = execute_action(action, params)
    
    # Responde
    response = {
        "request_id": request_id,
        "status": "success" if result else "error",
        "data": result
    }
    await nc.publish("iot.response", json.dumps(response).encode())

nc = await nats.connect("nats://nats:4222")
await nc.subscribe("iot.command", cb=handle_command)
```

## 📡 Protocolo de Comunicação

### Request (Orchestrator → Módulo)
```json
Subject: "{module}.command"
Payload: {
  "request_id": "uuid-v4",
  "action": "turn_on",
  "params": {
    "device_id": "luz_sala"
  }
}
```

### Response (Módulo → Orchestrator)
```json
Subject: "{module}.response"
Payload: {
  "request_id": "uuid-v4",
  "status": "success",
  "data": {
    "device_id": "luz_sala",
    "state": "ON"
  }
}
```

## 🔍 Exemplo de Uso (Orchestrator)

```python
from src.core.dispatcher.action_dispatcher import ActionDispatcher

# Despachar ação para IoT
response = await dispatcher.dispatch(
    module="iot",
    action="turn_on",
    params={"device_id": "luz_sala"},
    timeout=5.0
)

if response['status'] == 'success':
    print(f"Luz ligada: {response['data']}")
```

## 🗂️ Estrutura de Dados do Consul

```
consul/
└── kv/
    └── modules/
        ├── iot/
        │   └── actions = {"turn_on": {...}, "turn_off": {...}}
        ├── rpa/
        │   └── actions = {"open_browser": {...}, "click": {...}}
        └── mensagens/
            └── actions = {"send_whatsapp": {...}, "send_email": {...}}
```

## 🚀 Benefícios

1. **Plug-and-Play:** Novos módulos se auto-registram, sem código adicional no Orchestrator.
2. **Validação Automática:** O Dispatcher valida se a ação existe antes de enviar.
3. **Timeout Inteligente:** Cada ação pode ter timeout customizado.
4. **Request-Reply Pattern:** Garante que respostas cheguem ao chamador correto.
