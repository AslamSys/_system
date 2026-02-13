# 🤖 OpenClaw Agent - Comunicação Inteligente + RPA

**Agente autônomo** de comunicação multi-canal e automação web, integrado ao ecossistema Mordomo.

---

## 📋 Filosofia: Dois Agentes, Responsabilidades Claras

```
┌─────────────────────────────────────────────────┐
│ OpenClaw Agent (Smart Gateway + RPA)           │
├─────────────────────────────────────────────────┤
│                                                 │
│ Responsabilidades:                              │
│ ✅ Comunicação multi-canal (WhatsApp, Telegram) │
│ ✅ RPA/Browser tasks simples (scraping, forms)  │
│ ✅ Queries diretas respondíveis localmente      │
│                                                 │
│ LLM Brain: Gemini Flash 2.0 / GPT-4o-mini      │
│ Decisão: "Isso é pra mim ou pro Mordomo?"      │
│                                                 │
│ Quando repassa pro Mordomo:                     │
│ ❌ Multi-módulo (IoT + Segurança + NAS)         │
│ ❌ Contexto histórico (RAG conversação)         │
│ ❌ Automações complexas (triggers + actions)    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Mordomo Brain (Orchestrator)                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ Responsabilidades:                              │
│ ✅ Orquestração cross-módulos (IoT, Invest, etc)│
│ ✅ RAG + histórico conversacional               │
│ ✅ Automações complexas (if-then, schedules)    │
│ ✅ Processamento de voz (STT → TTS pipeline)    │
│                                                 │
│ LLM Brain: Claude Sonnet 3.5 / GPT-4o          │
│ Decisão: Qual módulo acionar? Como coordenar?  │
└─────────────────────────────────────────────────┘
```

**Princípio:** OpenClaw Agent **decide sozinho** se pode resolver ou se precisa escalar para o Mordomo Orchestrator.

---

## 🏗️ Arquitetura Interna (4 módulos, 1 container)

> **Importante:** OpenClaw roda como **1 container Docker** (`openclaw-agent`). Os 4 módulos abaixo são componentes internos do código-fonte, não containers separados.

```
src/                              # Código-fonte interno do container openclaw-agent
│
├─ gateway/                       # Multi-channel dispatcher
│  ├─ channels/
│  │  ├─ whatsapp/               # Baileys (WhatsApp Web)
│  │  ├─ telegram/               # grammY (Bot API)
│  │  ├─ discord/                # discord.js
│  │  ├─ email/                  # IMAP/SMTP
│  │  └─ sms/                    # Twilio
│  └─ session-manager/           # Contextos por usuário/canal
│
├─ browser-rpa/                   # Browser automation
│  ├─ chromium/                  # Headless Chrome (spawna on-demand)
│  ├─ cdp-controller/            # Chrome DevTools Protocol
│  ├─ actions/                   # Scraping, forms, screenshots
│  └─ ocr-engine/                # Tesseract (quando necessário)
│
├─ skills-hub/                    # MordomoHub registry
│  ├─ local-skills/              # Skills instaladas
│  ├─ remote-mirror/             # ClawHub featured (opcional)
│  └─ api/                       # Install, search, execute
│
└─ brain-bridge/                  # NATS bridge to Orchestrator
   ├─ publisher/                 # Publica quando precisa escalar
   ├─ subscriber/                # Subscreve respostas do Mordomo
   └─ router/                    # Request-reply pattern
```

---

## 🧠 OpenClaw Brain: Decisão Nativa via LLM

### System Prompt (Exemplo)

```markdown
Você é o OpenClaw Agent, responsável por comunicação e RPA no sistema Mordomo.

**Suas capacidades:**
- Enviar/receber mensagens: WhatsApp, Telegram, Discord, Email, SMS
- Automação web: Abrir páginas, extrair dados, preencher formulários
- Skills locais: Executar tarefas pre-programadas via MordomoHub

**Quando VOCÊ resolve diretamente:**
1. Queries simples respondíveis com web scraping
   - Exemplo: "Preço do café na Amazon"
   - Ação: Browser → amazon.com.br → extrai preço → responde
   
2. Envios de mensagem diretos
   - Exemplo: "Manda WhatsApp pro João dizendo que vou atrasar"
   - Ação: WhatsApp API → envia → confirma
   
3. RPA básico
   - Exemplo: "Me tira print do Dashboard X"
   - Ação: Browser → screenshot → envia imagem

**Quando ESCALAR pro Mordomo Brain:**
1. Multi-módulo (precisa IoT, Segurança, Investimentos, etc)
   - Exemplo: "Acende a luz E me avisa quando Bitcoin > $100k"
   - Ação: NATS pub → mordomo.orchestrator.request
   
2. Contexto histórico/RAG
   - Exemplo: "Lembra o que discutimos ontem sobre investimentos?"
   - Ação: NATS pub (Mordomo tem RAG conversacional)
   
3. Automações complexas (triggers, schedules, if-then)
   - Exemplo: "Todo dia às 7h, se temperatura > 25°C, liga o ar"
   - Ação: NATS pub (Mordomo coordena IoT + Scheduler)

**Formato de resposta quando escala:**
```json
{
  "decision": "escalate",
  "reason": "multi_module|rag_needed|complex_automation",
  "nats_topic": "mordomo.orchestrator.request",
  "payload": {
    "user_message": "...",
    "context": {...},
    "required_modules": ["iot", "investimentos"]
  }
}
```

**Formato de resposta quando resolve local:**
```json
{
  "decision": "handle_local",
  "action": "browser_scrape|send_message|run_skill",
  "response": "..."
}
```
```

### Exemplo de Decisão Real

```typescript
// OpenClaw Brain LLM completion
const userMessage = "Qual o preço do café na Amazon?";

const completion = await llm.complete({
  system: OPENCLAW_SYSTEM_PROMPT,
  messages: [
    {role: "user", content: userMessage}
  ]
});

// LLM retorna:
{
  decision: "handle_local",
  action: "browser_scrape",
  steps: [
    "navigate to amazon.com.br",
    "search for 'café'",
    "extract first 3 prices",
    "format as list"
  ],
  response_template: "Café na Amazon: {prices}"
}

// OpenClaw executa localmente
const prices = await browserRPA.scrape("amazon.com.br/cafe");
return `Café na Amazon: ${prices.join(', ')}`;
// Latência: ~3s, $0.001 LLM call, sem envolver Mordomo
```

**Caso Multi-Módulo:**

```typescript
const userMessage = "Acende a luz da sala";

const completion = await llm.complete({
  system: OPENCLAW_SYSTEM_PROMPT,
  messages: [{role: "user", content: userMessage}]
});

// LLM retorna:
{
  decision: "escalate",
  reason: "multi_module",
  required_modules: ["iot"],
  nats_topic: "mordomo.orchestrator.request",
  payload: {
    intent: "iot.device.control",
    params: {device: "luz", room: "sala", action: "on"}
  }
}

// OpenClaw publica no NATS
await nats.publish("mordomo.orchestrator.request", payload);
// Aguarda resposta
const ack = await nats.requestReply("mordomo.orchestrator.request", payload, {timeout: 5000});
return ack.message; // "Luz da sala acesa"
```

---

## 🔄 Fluxo Completo por Cenário

### Cenário 1: Query Simples (OpenClaw resolve)

```
User WhatsApp: "Qual o preço do café na Amazon?"
  ↓
┌───────────────────────────────────────────────────┐
│ 1. Gateway recebe (Baileys)                      │
│    {channel: "whatsapp", from: "+55...",          │
│     text: "Qual o preço do café na Amazon?"}     │
└──────────────────┬────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────┐
│ 2. OpenClaw Brain (LLM)                           │
│    System: [system prompt acima]                  │
│    User: "Qual o preço do café na Amazon?"        │
│                                                   │
│    ◄── LLM DECISION ──►                           │
│    {                                              │
│      decision: "handle_local",                    │
│      action: "browser_scrape",                    │
│      steps: ["navigate amazon", "extract price"], │
│      capabilities_check: {                        │
│        needs_iot: false,                          │
│        needs_history: false,                      │
│        needs_multi_module: false                  │
│      }                                            │
│    }                                              │
└──────────────────┬────────────────────────────────┘
                   │ Execute local
┌──────────────────▼────────────────────────────────┐
│ 3. Browser RPA Module                             │
│    - Spawna Chromium headless                     │
│    - Navega amazon.com.br/cafe                    │
│    - Selector: .a-price-whole                     │
│    - Extrai: "R$ 12,90"                           │
│    - Kill browser                                 │
└──────────────────┬────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────┐
│ 4. Resposta (WhatsApp)                            │
│    "Café Pilão 500g: R$ 12,90"                    │
└───────────────────────────────────────────────────┘

Latência: ~3.5s (100ms LLM + 3s browser + 400ms network)
Custo: $0.002 (1 LLM call Gemini Flash)
```

**Decisão 100% nativa do LLM:** Nenhum regex, nenhum pattern matching. O agente analisa a query e decide que pode resolver localmente via browser.

---

### Cenário 2: Multi-Módulo (OpenClaw escalona)

```
User Telegram: "Acende a luz da sala"
  ↓
┌───────────────────────────────────────────────────┐
│ 1. Gateway recebe (grammY)                        │
│    {channel: "telegram", chat_id: 123,            │
│     text: "Acende a luz da sala"}                 │
└──────────────────┬────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────┐
│ 2. OpenClaw Brain (LLM)                           │
│    System: [system prompt]                        │
│    User: "Acende a luz da sala"                   │
│                                                   │
│    ◄── LLM DECISION ──►                           │
│    {                                              │
│      decision: "escalate",                        │
│      reason: "multi_module",                      │
│      required_modules: ["iot"],                   │
│      capabilities_check: {                        │
│        needs_iot: TRUE,                           │
│        needs_history: false,                      │
│        can_handle_local: FALSE                    │
│      },                                           │
│      nats_payload: {                              │
│        intent: "iot.device.control",              │
│        params: {device: "luz", room: "sala",      │
│                 action: "on"},                    │
│        reply_to: "openclaw.response.{id}"         │
│      }                                            │
│    }                                              │
└──────────────────┬────────────────────────────────┘
                   │ NATS pub
┌──────────────────▼────────────────────────────────┐
│ 3. NATS: mordomo.orchestrator.request             │
│    {                                              │
│      from: "openclaw",                            │
│      user_id: "telegram:123",                     │
│      intent: "iot.device.control",                │
│      params: {...},                               │
│      reply_to: "openclaw.response.abc123"         │
│    }                                              │
└──────────────────┬────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────┐
│ 4. Mordomo Brain (Orchestrator)                   │
│    - LLM classifica: IoT domain                   │
│    - Valida device existe (Consul registry)       │
│    - NATS pub → iot.device.control                │
└──────────────────┬────────────────────────────────┘
                   │ NATS cross-network
┌──────────────────▼────────────────────────────────┐
│ 5. IoT Orchestrator (RPi 3B+)                     │
│    - MQTT pub → luz_sala_esp32                    │
│    - ESP32 faz GPIO HIGH → relay ON               │
│    - MQTT ACK                                     │
│    - NATS pub → openclaw.response.abc123          │
└──────────────────┬────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────┐
│ 6. OpenClaw recebe ACK via NATS                   │
│    subscriber.on("openclaw.response.abc123")      │
│    → "Luz da sala acesa"                          │
└──────────────────┬────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────┐
│ 7. Resposta (Telegram)                            │
│    bot.sendMessage(123, "Luz da sala acesa ✅")   │
└───────────────────────────────────────────────────┘

Latência: ~900ms (100ms LLM + 200ms NATS + 400ms IoT + 200ms reply)
Custo: $0.003 (1 call OpenClaw + 1 call Mordomo Brain)
```

**Decisão autônoma:** OpenClaw detecta que precisa de IoT (fora das suas capacidades), escalona automaticamente via NATS.

---

### Cenário 3: RAG Conversacional (OpenClaw escalona)

```
User Discord: "Lembra aquela conversa sobre investimentos de ontem?"
  ↓
┌──────────────────▼────────────────────────────────┐
│ OpenClaw Brain (LLM)                              │
│    User: "Lembra aquela conversa..."              │
│                                                   │
│    ◄── LLM DECISION ──►                           │
│    {                                              │
│      decision: "escalate",                        │
│      reason: "rag_needed",                        │
│      capabilities_check: {                        │
│        needs_iot: false,                          │
│        needs_history: TRUE,  ← RAG!               │
│        can_handle_local: FALSE                    │
│      },                                           │
│      explanation: "Preciso do histórico de        │
│                    conversas armazenado no        │
│                    Mordomo RAG (Qdrant)"          │
│    }                                              │
└──────────────────┬────────────────────────────────┘
                   │ NATS pub
┌──────────────────▼────────────────────────────────┐
│ Mordomo Brain → RAG Query                         │
│    - Qdrant search: user_id + "investimentos"     │
│    - Retorna últimas 5 conversas                  │
│    - LLM sintetiza resposta com contexto          │
│    - NATS pub → openclaw.response.xyz             │
└──────────────────┬────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────┐
│ OpenClaw responde (Discord)                       │
│    "Ontem você mencionou investir em ETFs de      │
│     S&P 500 e diversificar em renda fixa..."      │
└───────────────────────────────────────────────────┘

Latência: ~1.2s (100ms OpenClaw LLM + 400ms Qdrant + 500ms Mordomo LLM + 200ms reply)
```

**Decisão nativa:** OpenClaw detecta que precisa de histórico conversacional (RAG), que está no Mordomo, então escalona.

---

## 📦 Recursos e Capacidade

### OpenClaw Agent Container

```yaml
CPU: 30-50% (2-4 threads ativos)
  ├── Node.js runtime: 1 thread
  ├── Gateway (multi-channel): 1 thread
  ├── LLM Brain (Gemini Flash API): network-bound
  ├── Browser RPA (quando ativo): 1-2 threads
  └── NATS client: network-bound

RAM: 1.2GB base + 800MB browser ativo = 2.0GB total
  ├── Node.js: 300MB
  ├── Gateway channels: 400MB
  ├── LLM context cache: 200MB
  ├── Session manager: 300MB
  └── Browser (on-demand): +800MB

Storage: 2.5GB
  ├── Code + dependencies: 1.5GB
  ├── Browser cache: 500MB
  ├── Session states: 300MB
  └── Skills registry: 200MB

Network:
  Inbound:
    - WhatsApp: WebSocket (Baileys)
    - Telegram: Long Polling / Webhook (grammY)
    - Discord: WebSocket (discord.js)
    - Email: IMAP/SMTP
  Outbound:
    - NATS: nats://nats:4222 (localhost, <5ms)
    - LLM API: Gemini Flash 2.0 / GPT-4o-mini (HTTP)
    - Browser: HTTP/HTTPS (scraping on-demand)

Latência decisão LLM: 80-150ms
Latência scraping: 2-5s
Latência NATS round-trip: 200-500ms
```

**Nota:** OpenClaw usa **LLM próprio** (modelo leve e rápido). Todas as decisões são 100% nativas do modelo — zero regex, zero pattern matching.

---

## 🧩 Componentes Detalhados

### 1. Gateway (Multi-Channel Dispatcher)

Recebe mensagens de qualquer canal, normaliza para formato único e encaminha para o OpenClaw Brain.

```typescript
interface NormalizedMessage {
  id: string;
  channel: "whatsapp" | "telegram" | "discord" | "email" | "sms";
  from: string;           // ID único do usuário
  text: string;
  media?: MediaAttachment;
  timestamp: number;
  session_id: string;
}
```

**Canais suportados:**

| Canal | SDK | Auth | Features |
|-------|-----|------|----------|
| WhatsApp | Baileys | QR Code | Texto, mídia, grupos, reações |
| Telegram | grammY | Bot Token | Texto, mídia, inline keyboards |
| Discord | discord.js | Bot Token | Texto, embeds, threads, slash commands |
| Email | nodemailer + IMAP | SMTP/IMAP | Leitura, envio, filtros |
| SMS | Twilio | API Key | Envio/recebimento básico |

### 2. Browser RPA (Automação Web)

Chromium headless on-demand via CDP (Chrome DevTools Protocol).

```yaml
Capacidades:
  - Navegação: Abre qualquer URL
  - Scraping: Extrai dados via selectors CSS/XPath
  - Screenshots: Captura visual de páginas
  - Form filling: Preenche formulários automaticamente
  - OCR: Tesseract para imagens (quando necessário)

Ciclo de vida:
  1. OpenClaw Brain decide: "preciso do browser"
  2. Spawna instância Chromium headless
  3. Executa ações CDP
  4. Coleta resultado
  5. Kill browser (libera 800MB RAM)
  
Timeout: 30s máximo por operação
Pool: 1 instância simultânea (limite RAM)
```

### 3. Skills Hub (MordomoHub Registry)

Registry de skills reutilizáveis que OpenClaw pode executar.

```
skills-hub/
├── local-skills/           # Skills instaladas no sistema
│   ├── google-search/      # Busca otimizada via API
│   ├── weather/            # Consulta clima (OpenWeatherMap)
│   ├── translator/         # Tradução rápida
│   └── calculator/         # Cálculos e conversões
│
├── remote-mirror/          # Skills do ClawHub (opcional)
│   └── featured/
│       ├── google-calendar/
│       ├── notion-sync/
│       └── smart-home/
│
└── api/
    ├── registry.ts         # Lista skills disponíveis
    ├── install.ts          # Instala nova skill
    └── execute.ts          # Executa skill
```

O OpenClaw Brain tem acesso ao registry no system prompt — ele sabe quais skills existem e quando usá-las.

### 4. Brain Bridge (NATS Communication)

Ponte de comunicação bidirecional com o Mordomo Orchestrator via NATS.

```typescript
// Protocolo de mensagem
interface BrainBridgeMessage {
  id: string;                // UUID
  timestamp: number;
  source: "openclaw";
  reply_to: string;          // Topic para resposta
  
  // Contexto do usuário
  user_id: string;
  channel: string;
  session_id: string;
  
  // Payload
  intent: string;            // "iot.device.control"
  params: Record<string, any>;
  priority: "emergency" | "interactive" | "background";
  
  // Contexto conversacional (últimas N mensagens)
  conversation_context?: {
    messages: Array<{role: string; content: string}>;
    summary?: string;
  };
}

// NATS Topics
const TOPICS = {
  // OpenClaw → Mordomo
  REQUEST: "mordomo.orchestrator.request",
  
  // Mordomo → OpenClaw
  RESPONSE: "openclaw.response.{request_id}",
  
  // Broadcast (Mordomo → OpenClaw)
  NOTIFICATION: "openclaw.notification",
  ALERT: "openclaw.alert.{priority}",
};
```

**Request-Reply Pattern:**
```
OpenClaw pub → "mordomo.orchestrator.request" (com reply_to)
Mordomo sub → processa → orquestra módulos
Mordomo pub → "openclaw.response.{id}"
OpenClaw sub → recebe resposta → envia para canal do usuário
```

---

## 🔐 Segurança

### Modelo de Confiança (Single-User)

Como Mordomo é **single-user doméstico**, o modelo de segurança é simplificado:

```yaml
security:
  mode: "single_user"
  dm_pairing: false              # Sem pairing (single-user)
  trust_upstream: true            # Confia em Speaker Verification
  
  # Todos os canais autorizados por padrão
  channels:
    whatsapp: {authorized: true}
    telegram: {authorized: true}
    discord:
      authorized: true
      sandbox_public_servers: true  # Sandbox em servers públicos
```

### Sandbox (Discord Público)

Para servidores Discord públicos, browser e comandos system ficam isolados:

```yaml
sandbox:
  discord_public:
    allowed: ["search", "read", "weather", "calculator"]
    denied: ["browser", "system", "iot", "payments"]
```

---

## 📊 Métricas Esperadas

```yaml
Volume:
  Mensagens/dia: ~500-2000
  Canais simultâneos: 3-5

Performance:
  Decisão LLM (handle_local vs escalate): 80-150ms
  Resposta local (sem browser): 200-500ms
  Resposta com browser: 2-5s
  Resposta via Mordomo (NATS round-trip): 500ms-2s

Custo LLM:
  Modelo: Gemini Flash 2.0 (grátis tier) ou GPT-4o-mini ($0.15/1M tokens)
  Custo estimado: $5-15/mês (com ~1000 msgs/dia)

Distribuição esperada:
  handle_local: ~60% (comunicação + RPA simples)
  escalate: ~40% (multi-módulo + RAG + automações)

Taxa de erro: <1%
```

---

## 🚀 Deployment

### Docker Compose

```yaml
services:
  openclaw-agent:
    image: openclaw/openclaw:latest
    container_name: openclaw-agent
    environment:
      - NODE_ENV=production
      - NATS_URL=nats://nats:4222
      - CONSUL_URL=http://consul:8500
      - LLM_PROVIDER=gemini          # ou openai
      - LLM_MODEL=gemini-2.0-flash   # ou gpt-4o-mini
      - LLM_API_KEY=${LLM_API_KEY}
    volumes:
      - ./config:/app/config
      - ./skills:/app/.openclaw/workspace/skills
      - ./data:/app/data
    ports:
      - "18789:18789"     # WebSocket gateway
    deploy:
      resources:
        limits:
          cpus: '3.0'
          memory: 2.5G
        reservations:
          cpus: '1.0'
          memory: 1.5G
    depends_on:
      - nats
      - consul

  browser-rpa:
    image: browserless/chromium:latest
    container_name: browser-rpa
    environment:
      - MAX_CONCURRENT_SESSIONS=1
      - CONNECTION_TIMEOUT=30000
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 256M
```

### Consul Service Registration

```json
{
  "service": {
    "name": "openclaw-agent",
    "tags": ["communication", "rpa", "gateway"],
    "port": 18789,
    "check": {
      "http": "http://localhost:18789/health",
      "interval": "10s"
    },
    "meta": {
      "version": "1.0",
      "channels": "whatsapp,telegram,discord,email,sms",
      "capabilities": "messaging,browser,skills"
    }
  }
}
```

---

## 📚 Referências

- [OpenClaw GitHub](https://github.com/anthropics/openclaw)
- [OpenClaw Docs](https://docs.openclaw.ai)
- [NATS Protocol](https://docs.nats.io)
- [Consul Service Discovery](https://www.consul.io/docs)
- [Baileys WhatsApp](https://github.com/WhiskeySockets/Baileys)
- [grammY Telegram](https://grammy.dev)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
