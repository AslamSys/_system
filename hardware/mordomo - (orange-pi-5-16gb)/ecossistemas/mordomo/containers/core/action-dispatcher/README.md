# 🎬 Action Dispatcher

> ⚠️ **DEPRECATED / INTEGRADO**
>
> Este serviço foi **integrado ao `mordomo-orchestrator`** e não deve ser executado como um container isolado.
> Esta documentação é mantida apenas para referência histórica da lógica de despacho de ações.
> Consulte `../mordomo-orchestrator/README.md` para a implementação atual.

**Container:** `action-dispatcher`  
**Ecossistema:** Mordomo  
**Posição no Fluxo:** Executor de Ações Cross-Module

---

## 📋 Propósito

Detecta intenções nas respostas do Brain e despacha comandos para outros módulos (IoT, Comunicação, Pagamentos, RPA, etc) via NATS. Centraliza integração cross-module.

---

## 🎯 Responsabilidades

### Primárias
- ✅ Parsear actions do Brain LLM
- ✅ Validar parâmetros de ações
- ✅ Despachar comandos para módulos externos via NATS
- ✅ Aguardar confirmações (request/reply)
- ✅ Tratar erros e timeouts
- ✅ Notificar usuário sobre resultado

### Secundárias
- ✅ Retry logic com exponential backoff
- ✅ Circuit breaker por módulo
- ✅ Log de todas as ações executadas
- ✅ Métricas de sucesso/falha por módulo

---

## 🔧 Tecnologias

**Stack:** Node.js + TypeScript

```json
{
  "nats": "^2.18.0",
  "zod": "^3.22.4",
  "winston": "^3.11.0",
  "prom-client": "^15.1.0",
  "opossum": "^8.1.3"
}
```

---

## 📊 Especificações

```yaml
Performance:
  CPU: 5-10%
  RAM: ~ 100 MB
  Actions/second: 10
  Dispatch Latency: < 100ms
  
Reliability:
  Retry: 3 tentativas
  Timeout: 5s por módulo
  Circuit Breaker: 5 falhas = open (30s)
```

---

## 🎯 Tipos de Ações Suportadas

### 1. IoT (Controle de Dispositivos)

```typescript
{
  type: "iot.control",
  device_id: "light_sala",
  action: "turn_on" | "turn_off" | "set_brightness" | "set_color",
  params: {
    brightness?: 0-100,
    color?: { r, g, b }
  }
}

// Despacha para: iot.device.control
```

### 2. Comunicação (WhatsApp, Email, SMS)

```typescript
{
  type: "comunicacao.whatsapp.send",
  to: "+5511999999999",
  message: "Lembrete: Reunião às 15h"
}

{
  type: "comunicacao.email.send",
  to: "email@example.com",
  subject: "Lembrete",
  body: "Sua reunião é às 15h"
}

// Despacha para: comunicacao.whatsapp.send ou comunicacao.email.send
```

### 3. Pagamentos (PIX, Boletos)

```typescript
{
  type: "pagamentos.pix.send",
  to_key: "email@example.com",
  amount: 50.00,
  description: "Pagamento teste"
}

{
  type: "pagamentos.boleto.generate",
  amount: 100.00,
  due_date: "2025-12-01",
  description: "Conta de luz"
}

// Despacha para: pagamentos.pix.send ou pagamentos.boleto.generate
```

### 4. RPA (Automações)

```typescript
{
  type: "rpa.task.execute",
  task_name: "scrape_price",
  params: {
    url: "https://example.com/product",
    selector: ".price"
  }
}

// Despacha para: rpa.task.execute
```

### 5. Investimentos (Ordens de Compra/Venda)

```typescript
{
  type: "investimentos.order.create",
  symbol: "PETR4",
  side: "buy" | "sell",
  quantity: 100,
  price: 32.50
}

// Despacha para: investimentos.order.create
```

### 6. Entretenimento (Música, Vídeos)

```typescript
{
  type: "entretenimento.music.play",
  query: "Jazz",
  service: "spotify" | "youtube"
}

{
  type: "entretenimento.video.play",
  query: "Matrix",
  service: "netflix" | "youtube"
}

// Despacha para: entretenimento.music.play ou entretenimento.video.play
```

### 7. Segurança (Câmeras, Alarmes)

```typescript
{
  type: "seguranca.camera.snapshot",
  camera_id: "cam_entrada"
}

{
  type: "seguranca.alarm.arm",
  mode: "away" | "home" | "disarm"
}

// Despacha para: seguranca.camera.snapshot ou seguranca.alarm.arm
```

### 8. NAS (Busca de Arquivos)

```typescript
{
  type: "nas.file.search",
  query: "fotos da praia 2024"
}

{
  type: "nas.backup.start",
  target: "cloud" | "local"
}

// Despacha para: nas.file.search ou nas.backup.start
```

---

## 🔌 Interfaces

### NATS Subscriptions (Recebe)

```yaml
# Resposta do Brain com ações
mordomo.brain.response_generated:
  payload:
    conversation_id: uuid
    speaker_id: user_1
    response: "Ok, luz acesa!"
    actions: [
      {
        type: "iot.control",
        device_id: "light_sala",
        action: "turn_on"
      }
    ]
```

### NATS Publications (Despacha)

```yaml
# Para módulo IoT
iot.device.control:
  payload:
    device_id: light_sala
    action: turn_on
    speaker_id: user_1
    conversation_id: uuid
    params: {}

# Para módulo Comunicação
comunicacao.whatsapp.send:
  payload:
    to: "+5511999999999"
    message: "Lembrete: Reunião às 15h"
    speaker_id: user_1

# Para módulo Pagamentos
pagamentos.pix.send:
  payload:
    to_key: "email@example.com"
    amount: 50.00
    description: "Pagamento teste"
    speaker_id: user_1
```

### NATS Request/Reply (Aguarda resposta)

```typescript
// Enviar comando e aguardar confirmação
const response = await nats.request(
  'iot.device.control',
  {
    device_id: 'light_sala',
    action: 'turn_on',
    speaker_id: 'user_1'
  },
  { timeout: 5000 }
);

// Response esperada:
{
  success: true,
  device_id: "light_sala",
  new_state: "on",
  timestamp: 1732723200.123
}

// Em caso de erro:
{
  success: false,
  error: "Device offline",
  device_id: "light_sala"
}
```

---

## ⚙️ Configuração

```yaml
nats:
  url: "nats://nats:4222"
  token_file: "/run/secrets/nats_token"
  max_reconnect: 10

timeouts:
  iot: 5000  # ms
  comunicacao: 10000
  pagamentos: 15000
  rpa: 30000
  investimentos: 10000
  entretenimento: 5000
  seguranca: 5000
  nas: 10000

retry:
  max_attempts: 3
  backoff_ms: [1000, 2000, 4000]  # Exponential
  
circuit_breaker:
  # Opossum config
  timeout: 5000
  error_threshold_percentage: 50
  reset_timeout: 30000  # 30s
  
logging:
  level: "info"
  actions_log_file: "/var/log/actions.json"
```

---

## 🔒 Segurança (Secrets)

```yaml
# docker-compose.yml
services:
  action-dispatcher:
    secrets:
      - nats_token

secrets:
  nats_token:
    file: ./secrets/nats_token.txt
```

```typescript
import { readFileSync } from 'fs';

const natsToken = readFileSync('/run/secrets/nats_token', 'utf8').trim();
```

---

## 📡 Protocolo de Comunicação Inter-Módulos

### Namespace Global NATS

**Padrão:** `{modulo}.{recurso}.{acao}`

```yaml
# Módulo Mordomo
mordomo.speech.transcribed
mordomo.brain.response_generated
mordomo.conversation.message_received

# Módulo IoT
iot.device.control
iot.device.state_changed
iot.device.discovered

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

# Módulo Entretenimento
entretenimento.music.play
entretenimento.music.pause
entretenimento.video.play

# Módulo Segurança
seguranca.camera.snapshot
seguranca.alarm.arm
seguranca.motion.detected

# Módulo RPA
rpa.task.execute
rpa.task.completed
rpa.browser.navigate

# Módulo NAS
nas.file.search
nas.file.found
nas.backup.start
```

### Formato de Mensagens (JSON Schema)

```typescript
// Request padrão
interface ActionRequest {
  speaker_id: string;           // Quem solicitou
  conversation_id?: string;     // Contexto da conversa
  action: string;               // Nome da ação
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

### Exemplo Completo (IoT)

```typescript
// 1. Dispatcher envia
await nats.request('iot.device.control', {
  speaker_id: 'user_1',
  conversation_id: 'abc123',
  action: 'turn_on',
  params: {
    device_id: 'light_sala',
    brightness: 80
  },
  timestamp: Date.now(),
  request_id: 'req-xyz789'
});

// 2. Módulo IoT processa e responde
{
  success: true,
  request_id: 'req-xyz789',
  result: {
    device_id: 'light_sala',
    previous_state: 'off',
    new_state: 'on',
    brightness: 80
  },
  timestamp: Date.now()
}

// 3. Módulo IoT publica evento de mudança de estado
nats.publish('iot.device.state_changed', {
  device_id: 'light_sala',
  state: 'on',
  brightness: 80,
  changed_by: 'user_1',
  timestamp: Date.now()
});
```

---

## 📝 Exemplo de Código

```typescript
// src/dispatcher.ts
import { connect, NatsConnection, StringCodec } from 'nats';
import CircuitBreaker from 'opossum';
import { z } from 'zod';
import { readFileSync } from 'fs';

const sc = StringCodec();

// Schema de validação
const ActionSchema = z.object({
  type: z.string(),
  params: z.record(z.any())
});

// Circuit breakers por módulo
const breakers = new Map<string, CircuitBreaker>();

function getBreaker(module: string) {
  if (!breakers.has(module)) {
    breakers.set(module, new CircuitBreaker(
      async (subject: string, data: any) => {
        return await nats.request(subject, sc.encode(JSON.stringify(data)), {
          timeout: config.timeouts[module] || 5000
        });
      },
      {
        timeout: config.timeouts[module] || 5000,
        errorThresholdPercentage: 50,
        resetTimeout: 30000
      }
    ));
  }
  return breakers.get(module)!;
}

// Main dispatcher
nats.subscribe('mordomo.brain.response_generated', async (msg) => {
  const data = JSON.parse(sc.decode(msg.data));
  const { conversation_id, speaker_id, actions } = data;
  
  if (!actions || actions.length === 0) return;
  
  for (const action of actions) {
    try {
      // Validar
      const validated = ActionSchema.parse(action);
      
      // Extrair módulo do tipo (ex: "iot.control" -> "iot")
      const [module, ...rest] = validated.type.split('.');
      const subject = validated.type;
      
      // Preparar payload
      const payload = {
        speaker_id,
        conversation_id,
        ...validated.params,
        timestamp: Date.now(),
        request_id: crypto.randomUUID()
      };
      
      // Despachar com circuit breaker
      const breaker = getBreaker(module);
      const response = await breaker.fire(subject, payload);
      
      const result = JSON.parse(sc.decode(response.data));
      
      if (result.success) {
        logger.info('Action executed', { action: validated.type, result });
        
        // Notificar usuário
        nats.publish(`mordomo.action.completed`, {
          conversation_id,
          speaker_id,
          action: validated.type,
          result: result.result
        });
      } else {
        logger.error('Action failed', { action: validated.type, error: result.error });
        
        // Notificar falha
        nats.publish(`mordomo.action.failed`, {
          conversation_id,
          speaker_id,
          action: validated.type,
          error: result.error
        });
      }
      
      // Métricas
      actionsCounter.labels(module, 'success').inc();
      
    } catch (error) {
      logger.error('Dispatch error', { action, error });
      actionsCounter.labels(module, 'error').inc();
      
      // Retry logic
      await retryAction(action, speaker_id, conversation_id);
    }
  }
});

// Retry com exponential backoff
async function retryAction(action: any, speaker_id: string, conversation_id: string, attempt = 0) {
  if (attempt >= config.retry.max_attempts) {
    logger.error('Max retries exceeded', { action });
    return;
  }
  
  const backoff = config.retry.backoff_ms[attempt] || 5000;
  await new Promise(resolve => setTimeout(resolve, backoff));
  
  try {
    // Tentar novamente...
  } catch (error) {
    await retryAction(action, speaker_id, conversation_id, attempt + 1);
  }
}
```

---

## 🐳 Docker

```yaml
services:
  action-dispatcher:
    build: ./action-dispatcher
    container_name: mordomo-action-dispatcher
    environment:
      - NODE_ENV=production
      - NATS_URL=nats://nats:4222
    secrets:
      - nats_token
    depends_on:
      - nats
    networks:
      - mordomo-net
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 150M
        reservations:
          cpus: '0.1'
          memory: 80M
    healthcheck:
      test: ["CMD", "node", "healthcheck.js"]
      interval: 30s
      timeout: 5s
      retries: 3
```

---

## 📊 Métricas (Prometheus)

```typescript
import client from 'prom-client';

const actionsCounter = new client.Counter({
  name: 'actions_dispatched_total',
  help: 'Total actions dispatched',
  labelNames: ['module', 'status']  // iot/success, pagamentos/error
});

const dispatchDuration = new client.Histogram({
  name: 'action_dispatch_duration_seconds',
  help: 'Time to dispatch and receive response',
  labelNames: ['module'],
  buckets: [0.1, 0.5, 1, 2, 5, 10]
});

const circuitBreakerState = new client.Gauge({
  name: 'circuit_breaker_state',
  help: 'Circuit breaker state (0=closed, 1=open, 2=half-open)',
  labelNames: ['module']
});
```

---

## 🔧 Troubleshooting

### Ação não executa
```bash
# Verificar logs
docker logs -f action-dispatcher | grep ERROR

# Verificar NATS connection
docker exec action-dispatcher nats sub "iot.>"
```

### Circuit breaker aberto
```bash
# Ver estado
curl http://action-dispatcher:3002/metrics | grep circuit_breaker_state

# Aguardar 30s para reset ou reiniciar
docker restart action-dispatcher
```

### Timeout em módulo específico
```bash
# Ajustar timeout
vim config/timeouts.yml
# Aumentar timeout do módulo lento
pagamentos: 20000  # 20s

docker restart action-dispatcher
```

---

**Documentação atualizada:** 27/11/2025
