# 🧠 Ambiente CORE (Orquestração + Brain)

**Propósito:** Gerenciamento de conversas, permissões, LLM, ações e interface

---

## 📦 Containers (7 total)

### 1. **mordomo-orchestrator** ✅ IMPLEMENTADO
**Função:** Núcleo central (Session + LLM Gateway + Event Handling + Memory).

**Responsabilidades:**
- ✅ **LLM Gateway**: LiteLLM com fallback Cloud → Local (qwen2.5:1.5b)
- ✅ **Event System**: Processa notificações assíncronas com fila de prioridade (4 níveis)
- ✅ **Event Memory**: Armazena histórico de eventos para consultas contextuais do LLM
- ✅ **Semantic Cache**: Bypass de LLM para comandos frequentes (FAISS)
- ✅ **REST API**: Endpoints para consulta de eventos e contexto
- ⏳ **Session Controller**: Gerencia estado de conversas (a implementar)

**Stack:** Python 3.11 + FastAPI + NATS + LiteLLM
**Status:** 🟢 Operacional (5/6 módulos implementados)

### 2. **action-dispatcher** ⏳ ESPECIFICADO
**Função:** Roteamento de ações via Service Discovery.

**Responsabilidades:**
- Service Discovery via Consul
- Roteamento NATS para módulos externos
- Circuit breaker e retry logic
- Validação de ações por schema

**Stack:** Python 3.11 + Consul + NATS
**Status:** Estrutura criada, não implementado

### 3. **skills-runner** ⏳ ESPECIFICADO
**Função:** Execução tática de scripts Python (Nível 1).

**Responsabilidades:**
- Execução de código Python efêmero gerado pela IA
- Sandbox isolado com timeout
- Gerenciamento de ambientes virtuais (Venv Cache)
- Instalação dinâmica de dependências (pip)

**Stack:** Python 3.11-slim + NATS
**Recursos:** Variável (Sob demanda)

### 3. **mordomo-brain** ⏳ ESPECIFICADO
**Função:** Inteligência (LLM) e raciocínio avançado.

**Responsabilidades:**
- RAG (Retrieval Augmented Generation) via Qdrant
- Processamento multi-step reasoning
- Detecção de intenções complexas
- Geração de respostas contextuais

**Stack:** Python 3.11 + Ollama + Qdrant Client
**Status:** Estrutura criada, não implementado

### 4. **system-watchdog** ✅ IMPLEMENTADO
**Função:** Proteção de hardware e gerenciamento térmico.

**Responsabilidades:**
- ✅ Monitoramento de CPU/RAM/Temperatura
- ✅ Controle de ventoinha (PWM)
- ✅ Sacrifício de containers não-essenciais em sobrecarga
- ✅ Sistema DEFCON (4 níveis: Normal/Alerta/Crítico/Emergência)
- ✅ Publicação de métricas via NATS (system.health.status)
- ✅ Shutdown automático se temperatura > 90°C

**Stack:** Python 3.11 + psutil + docker-py + NATS
**Recursos:** ~20MB RAM, <1% CPU
**Status:** 🟢 Operacional

### 5. **core-gateway** ⏳ ESPECIFICADO
**Função:** Gateway reverso e balanceamento de carga.

**Responsabilidades:**
- Roteamento HTTP/WebSocket
- Rate limiting
- CORS e autenticação

**Stack:** Nginx ou Traefik
**Status:** Estrutura criada, não implementado

### 6. **dashboard-ui** ⏳ ESPECIFICADO
**Função:** Interface web para monitoramento.

**Responsabilidades:**
- Visualização de conversas
- Gerenciamento de usuários
- Monitoramento de métricas

**Stack:** React + TypeScript
**Status:** Estrutura criada, não implementado

---

## 📊 Fluxo Completo (Atualizado)

```
┌─────────────────────────────────────────────────────────────────┐
│                   AMBIENTE CORE (Atualizado)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📥 FLUXO 1: REQUEST-REPLY (Usuário → Mordomo → Módulos)       │
│                                                                 │
│     STT: speech.transcribed                                     │
│     └─ {text, speaker_id, confidence}                           │
│                          │                                      │
│                          ▼                                      │
│  1️⃣ Mordomo Orchestrator                                        │
│     ├─ Verifica Semantic Cache (FAISS)                         │
│     │   ├─ HIT (>0.95) → Executa ação diretamente              │
│     │   └─ MISS → Continua para LLM                            │
│     ├─ Consulta PostgreSQL (contexto do usuário)               │
│     ├─ Valida permissões (níveis 0-10)                         │
│     └─ Publica: brain.request                                  │
│                          │                                      │
│                          ▼                                      │
│  2️⃣ Mordomo Brain (LLM)                                          │
│     ├─ LiteLLM: Cloud API → Fallback Local (qwen2.5:1.5b)      │
│     ├─ RAG: Qdrant (busca semântica)                           │
│     └─ Retorna: {intent, action, params}                       │
│                          │                                      │
│                          ▼                                      │
│  3️⃣ Action Dispatcher (dentro do Orchestrator)                  │
│     ├─ Consulta Consul: Descobre módulo (iot, rpa, etc.)       │
│     ├─ Valida ação no schema do módulo                         │
│     ├─ Publica NATS: {module}.command                          │
│     └─ Aguarda resposta: {module}.response                     │
│                          │                                      │
│                          ▼                                      │
│     📤 TTS: tts.generate_request                               │
│                                                                 │
│  📡 FLUXO 2: EVENT-DRIVEN (Módulos → Mordomo)                  │
│                                                                 │
│     Módulo publica evento espontâneo:                           │
│     └─ security.event.intrusion_detected (priority=CRITICAL)    │
│                          │                                      │
│                          ▼                                      │
│  4️⃣ Event Queue (PriorityQueue)                                 │
│     └─ Enfileira por prioridade (CRITICAL > HIGH > NORMAL)     │
│                          │                                      │
│                          ▼                                      │
│  5️⃣ Event Handler + Event Memory                                 │
│     ├─ Executa política automática:                            │
│     │   ├─ Liga luzes (via Action Dispatcher)                  │
│     │   ├─ Toca sirene                                         │
│     │   ├─ Envia notificação push                              │
│     │   └─ TTS: "Intruso detectado!"                           │
│     └─ Armazena evento na memória (consultas futuras):         │
│         └─ "Quem me mandou mensagem há 10 minutos?"           │
│                                                                 │
│  6️⃣ System Watchdog (Monitoramento)                             │
│     ├─ Monitora CPU/RAM/Temperatura                            │
│     ├─ Ajusta ventoinha (PWM)                                  │
│     └─ Mata containers não-essenciais se necessário            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Sistema de Permissões (Níveis 0-10)

### Tabela de Níveis

```yaml
0-2: GUEST (Convidados)
  ✅ Consultas: clima, hora, notícias
  ✅ Entretenimento: música, piadas
  ❌ Controle de dispositivos
  ❌ Acesso a câmeras
  
3-5: USER (Usuários comuns)
  ✅ Tudo do GUEST +
  ✅ Controle de luzes/AC do próprio cômodo
  ✅ Câmeras de áreas comuns
  ❌ Alarme, trancas
  
6-8: POWER_USER (Família)
  ✅ Tudo do USER +
  ✅ Controle total de dispositivos
  ✅ Todas as câmeras
  ✅ Criar automações simples
  ❌ Configurações de sistema
  
9-10: ADMIN (Administrador)
  ✅ Acesso irrestrito
  ✅ Gerenciar usuários
  ✅ Modificar configurações
  ✅ Executar scripts
```

### Fluxo de Validação

```
1. Speaker ID identifica: user_id="user_1", recognized=true
   ↓
2. Conversation Manager busca: User.findOne(user_id)
   └─ user.level = 9 (ADMIN)
   ↓
3. Usuário pede: "desligar o alarme"
   └─ Brain identifica: action="alarm.disable"
   ↓
4. Manager busca: Module.findOne(name="alarm")
   └─ module.required_level = 6 (POWER_USER)
   ↓
5. Valida: user.level (9) >= required_level (6) ✅
   ↓
6. Action Dispatcher executa e loga:
   └─ ActionLog {user_id, action, allowed=true, speaker_mismatch=false}
```

### Segurança Anti-Escalação

**Cenário:** Admin inicia conversa, convidado tenta comando privilegiado

```
1. Admin: "ASLAM, qual a temperatura?"
   └─ Speaker ID: user_id="admin", recognized=true ✅
   └─ Conversa ativa com contexto admin
   
2. Convidado: "desligar o alarme" (enquanto conversa ativa)
   └─ Speaker ID detecta voz diferente:
      ├─ user_id="unknown_xyz", recognized=false ❌
      └─ NATS: speech.diarized {recognized: false}
   
3. Conversation Manager recebe recognized=false:
   └─ IGNORA comando completamente (nem processa)
   └─ ActionLog {speaker_mismatch=true, allowed=false}
   
4. Sistema permanece seguro ✅
```

---

## 💾 Banco de Dados (PostgreSQL)

### Schema Principal

```sql
-- Usuários
User {
  user_id: string (PK)
  name: string
  level: int (0-10)
  is_guest: boolean
  expires_at: timestamp?
  created_at: timestamp
}

-- Conversações
Conversation {
  id: uuid (PK)
  user_id: string (FK)
  started_at: timestamp
  ended_at: timestamp?
  messages_count: int
}

-- Mensagens
Message {
  id: uuid (PK)
  conversation_id: uuid (FK)
  speaker_id: string
  text: string
  is_user: boolean
  timestamp: timestamp
}

-- Módulos (permissões)
Module {
  name: string (PK)
  required_level: int (0-10)
  description: string
  enabled: boolean
}

-- Auditoria de Ações
ActionLog {
  id: uuid (PK)
  user_id: string (FK)
  action: string
  allowed: boolean
  speaker_mismatch: boolean
  timestamp: timestamp
}
```

---

## � Containers

| Container | Status | Tecnologia | CPU | RAM | Responsabilidade |
|-----------|--------|-----------|-----|-----|------------------|
| **mordomo-orchestrator** | ✅ | Python 3.11 + FastAPI | 15-20% | ~360MB | LLM Gateway + Events + Cache + Memory |
| **action-dispatcher** | ⏳ | Python + Consul | 5-10% | ~100MB | Service Discovery + Action Routing |
| **mordomo-brain** | ⏳ | Python + Qdrant | 10-20% | ~500MB | RAG + Raciocínio avançado |
| **system-watchdog** | ✅ | Python 3.11 + psutil | <1% | ~20MB | Proteção térmica + DEFCON |
| **skills-runner** | ⏳ | Python | 0-30% | 0-200MB | Python Sandbox (sob demanda) |
| **core-gateway** | ⏳ | Nginx ou Traefik | <5% | ~50MB | Reverse proxy + rate limiting |
| **dashboard-ui** | ⏳ | React + TS | 2-5% | ~100MB | Interface web |

**Total Implementado:** ~380MB RAM, ~20% CPU (2 containers)
**Total Planejado:** ~1.33GB RAM, ~50% CPU (7 containers)

**Progresso:** 2/7 containers (29%)

---

## 🔗 Integrações

**Recebe de:**
- Ambiente STT: `speech.diarized` (via NATS)
- Ambiente TTS: `tts.status` (via NATS)

**Envia para:**
- Ambiente TTS: `tts.generate` (via NATS)
- Infraestrutura: PostgreSQL, Qdrant, Redis, Consul

**Eventos NATS:**
```
Subscreve:
  - speech.diarized
  - brain.response.{user_id}
  - tts.status.{speaker_id}
  - action.completed.{action_id}

Publica:
  - brain.request.{user_id}
  - tts.generate.{speaker_id}
  - action.dispatch.{action_id}
  - conversation.ended
```

---

## 🚀 Status de Implementação

### ✅ Concluído
1. ✅ **Mordomo Orchestrator** - LLM Gateway + Events operacional
   - ✅ LLM Service (Cloud + Fallback local)   
   - ✅ Event System (PriorityQueue + Handlers)
   - ✅ Event Memory (Consultas contextuais)
   - ✅ Semantic Cache (FAISS)
   - ✅ REST API (endpoints de eventos)
   - ⏳ Session Controller (a implementar)
2. ✅ **System Watchdog** - Proteção térmica com DEFCON

### ⏳ Pendente
3. ⏳ **Action Dispatcher** - Service Discovery modular
4. ⏳ **Mordomo Brain** - RAG + Raciocínio avançado
5. ⏳ **Skills Runner** - Python sandbox
6. ⏳ **Core Gateway** - Reverse proxy
7. ⏳ **Dashboard UI** - Interface web

**Progresso:** 2/7 containers (29%)
**Funcionalidades:** 5/6 módulos do orchestrator (83%)

---

**Versão:** 1.0
