# 🏠 Ecossistema Mordomo (Aslam)

> 📍 **Navegação:** [🏠 Início](../../../../README.md) > [🔧 Hardware](../../../README.md) > [🎯 Mordomo](../../README.md) > [🌐 Ecossistemas](../README.md) > [🏠 Mordomo](README.md)

Sistema principal de assistente de voz inteligente multiusuário com processamento completo de áudio, reconhecimento de fala, LLM local/cloud e síntese de voz.

---

## 📁 Estrutura de Ambientes

```
ecossistemas/mordomo/containers/
│
├─ 🎤 stt/                          (6 containers - Speech-to-Text)
│  ├─ audio-capture-vad/           ✅ Implementado
│  ├─ wake-word-detector/          ✅ Implementado
│  ├─ speaker-verification/        ✅ Implementado
│  ├─ whisper-asr/                 ✅ Implementado
│  ├─ speaker-id-diarization/      ⏳ Em desenvolvimento
│  └─ source-separation/           ⏳ Pendente
│
├─ 🔊 tts/                          (2 containers - Text-to-Speech)
│  ├─ tts-engine/                  ✅ Implementado
│  └─ audio-bridge/                ✅ Especificado (Rust)
│
├─ 💡 visual-feedback/              (1 container - LED Ring WS2812B)
│  └─ visual-feedback/             📋 Especificado (Feedback sensorial via GPIO)
│
├─ 🤖 openclaw/                     (1 container - OpenClaw Agent)
│  └─ openclaw-agent               ⏳ Especificado (Gateway + Browser RPA + Skills + NATS Bridge)
│
└─ 🧠 core/                         (5 containers - Orquestração + Brain)
   ├─ mordomo-orchestrator/        ✅ Implementado (Session + LLM + Dispatcher + Events + Cache)
   ├─ skills-runner/               ⏳ Especificado (Python Sandbox)
   ├─ mordomo-brain/               ⏳ Pendente (RAG + Advanced reasoning)
   ├─ system-watchdog/             ✅ Implementado (DEFCON + Thermal protection)
   ├─ core-gateway/                ⏳ Pendente
   └─ dashboard-ui/                ⏳ Pendente (Canvas A2UI)

Total: 15 containers | Implementados: 7/15 (47%)

NOTAS:
- action-dispatcher foi integrado ao mordomo-orchestrator
- Comunicação/RPA integrados via OpenClaw Agent (1 container, substitui 2 hardwares separados)
- OpenClaw tem 4 módulos internos (gateway, browser-rpa, skills-hub, brain-bridge) rodando em 1 container
```

**📖 Documentação por Ambiente:**
- [🎤 STT - Speech-to-Text](./containers/stt/README.md)
- [🔊 TTS - Text-to-Speech](./containers/tts/README.md)
- [💡 Visual Feedback - LED Ring WS2812B](./containers/visual-feedback/README.md)
- [🤖 OpenClaw Agent - Comunicação + RPA](./containers/openclaw/README.md)
- [🧠 CORE - Orquestração + Brain](./containers/core/README.md)

---

## Visão Geral

O **Mordomo** é o ecossistema central do projeto Aslam. Responsável por toda a interação de voz com os usuários, desde a captura de áudio até a resposta sintetizada.

### Características Principais

- ✅ Ativação via **wake word** ("ASLAM")
- ✅ **Multiusuário** com contextos separados por falante
- ✅ **LLM local-first** (Ollama) com fallback cloud
- ✅ Detecção de **interrupções** e sobreposição de fala
- ✅ **TTS pausável** e streaming de baixa latência
- ✅ **Speaker Verification** (apenas usuários autorizados)
- ✅ Interface em **tablet/dashboard** web
- ✅ **Processamento paralelo** (latência otimizada ~500ms)

---

## Arquitetura por Ambientes (14 containers)

```
┌─────────────────────────────────────────────────────────────┐
│                    ECOSSISTEMA MORDOMO                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎤 AMBIENTE STT (6 containers)                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Audio Capture VAD → Wake Word → Whisper ASR          │  │
│  │                           ↓                           │  │
│  │ Speaker Verification → Speaker ID/Diarization        │  │
│  │                           ↓                           │  │
│  │                   Source Separation (condicional)     │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ↓ speech.diarized                 │
│                                                             │
  🧠 AMBIENTE CORE (6 containers)                            │
  ┌───────────────────────────────────────────────────────┐  │
  │ Mordomo Orchestrator (Unificado)                      │  │
  │   ├─ Session Controller                               │  │
  │   ├─ LLM Service (Cloud + Local Fallback)            │  │
  │   ├─ Semantic Cache (FAISS)                          │  │
  │   ├─ Action Dispatcher (Consul + NATS)               │  │
  │   └─ Event System (Priority Queue + Handlers)        │  │
  │        ↓                                ↓             │  │
  │ Skills Runner (Python Sandbox) ← Orchestrator        │  │
  │        ↓                                ↓             │  │
  │ Brain (RAG) ← Core Gateway ← Dashboard UI            │  │
  │                                                       │  │
  │ System Watchdog (DEFCON + Thermal Control)           │  │
  └───────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ↓ tts.generate                    │
│                                                             │
│  🔊 AMBIENTE TTS (2 containers)                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TTS Engine (Azure/Piper) → Audio Bridge               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Estrutura de Diretórios:
containers/
├─ stt/       (Speech-to-Text)
├─ tts/       (Text-to-Speech)
├─ core/      (Orquestração + Brain)
└─ openclaw/  (OpenClaw Agent - Comunicação + RPA)
```

---

## 🔄 Ciclo de Vida do Gate (Paralelização)

```
1. wake_word.detected
   ↓
   [GATE FECHA] → Processamento paralelo inicia
   ├─ Speaker Verification (200ms)
   ├─ Whisper ASR (buffering)
   └─ Speaker ID (buffering)
   
2. speaker.verified ✅
   ↓
   [GATE ABRE] → Libera resultados downstream
   
3. conversation.ended
   ↓
   [GATE RESETA] → Todos voltam ao IDLE
   ├─ Buffers limpos
   ├─ Contextos descartados
   └─ Pronto para próxima detecção
```

**Latência:** ~500ms até primeira transcrição (vs ~1000ms sequencial)

---

## 🔐 Sistema de Permissões (Níveis)

**Arquitetura:**
```
Speaker Verification:  WHO (quem é?)
       ↓
Conversation Manager:  CAN (pode fazer?)
       ↓
Action Dispatcher:     DO (executa)
```

### Níveis de Acesso

```yaml
Nível 0-2: GUEST (convidados)
  ✅ Consultar clima, hora, notícias
  ✅ Tocar música
  ❌ Controlar dispositivos
  ❌ Ver câmeras
  ❌ Executar scripts

Nível 3-5: USER (usuários comuns)
  ✅ Tudo do GUEST +
  ✅ Controlar luzes/AC próprios cômodos
  ✅ Ver câmeras áreas comuns
  ❌ Desligar alarme
  ❌ Criar automações

Nível 6-8: POWER_USER (família)
  ✅ Tudo do USER +
  ✅ Controlar todos dispositivos
  ✅ Ver todas câmeras
  ✅ Criar automações simples
  ❌ Modificar configurações sistema
  ❌ Adicionar/remover usuários

Nível 9-10: ADMIN (administrador)
  ✅ Acesso total irrestrito
  ✅ Gerenciar usuários
  ✅ Configurar sistema
  ✅ Executar scripts Python/shell
```

### Gestão de Usuários

**Usuários Permanentes:**
- Cadastrados no PostgreSQL via Conversation Manager
- Voz registrada no Speaker Verification
- Nível de acesso fixo

**Convidados Temporários:**
- Criados via API com expiração (24h-7d)
- Auto-cleanup ao expirar
- Módulos específicos permitidos
- Opcional: cadastro rápido de voz

**Exemplo:**
```python
# Criar convidado temporário
POST /users/guest/create
{
  "name": "João (amigo)",
  "level": 2,
  "expires_at": "2025-12-04T00:00:00Z",
  "allowed_modules": ["weather", "music"]
}
```

### 🔒 Re-autenticação Contínua (Anti-Escalação)

**Problema:** Sessão iniciada por admin, outro usuário tenta comandos privilegiados

**Solução:** Diarization com embeddings cadastrados re-autentica a cada comando

```yaml
Fluxo de Segurança:
  1. Wake Word + Verification:
     - Identifica quem INICIOU sessão (embedding match)
     - Cria conversation_id
     
  2. Diarization (contínuo com embeddings):
     - Identifica quem está FALANDO AGORA
     - Compara embedding atual vs database cadastrado
     - Output: user_id (recognized=true) OU unknown (recognized=false)
     
  3. Conversation Manager:
     - BLOQUEIA se recognized=false (voz desconhecida)
     - Compara session_owner vs current_speaker
     - Previne escalação de privilégios

Exemplo de Bloqueio (Voz Desconhecida):
  Admin: "ASLAM" → Session: user_1 (level 10)
  Vizinho: "Desliga o alarme!"
  → Diarization: embedding match 0.38 (< 0.70)
  → Output: unknown_xyz, recognized=false
  → Manager: IGNORA SILENCIOSAMENTE ❌

Exemplo de Bloqueio (Permissão):
  Admin: "ASLAM" → Session: user_1 (level 10)
  Esposa: "Execute script"
  → Diarization: user_2, recognized=true ✅
  → Manager: level 8 < required 10 ❌ NEGADO
```

**Auditoria:**
- Flag `speaker_mismatch` e `recognized=false`
- Metadata: quem iniciou vs quem tentou

---

## 📦 Lista Completa de Containers

### 1. **audio-bridge**
- **Função:** Ponte entre Aslam App (tablet) e pipeline de áudio
- **Tecnologia:** Node.js + WebRTC + WebSocket
- **Responsabilidades:**
  - Receber stream de áudio do tablet via WebSocket
  - Converter WebM/Opus → PCM 16kHz
  - Aplicar VAD (filtrar silêncio)
  - Publicar chunks no NATS
  - Enviar áudio TTS de volta para tablet
  - Gerenciar estados visuais (idle, listening, processing, speaking)
- **Comunicação:** WebSocket (Aslam App) + NATS
- **Porta:** 3100
- **Futuro:** Suportar microfones USB pela casa

---

### 2. **audio-capture-vad**
- **Função:** Captura contínua de áudio do microfone
- **Tecnologia:** Sounddevice, WebRTC VAD
- **Responsabilidades:**
  - Captura em frames de 10-30ms
  - Filtra silêncio e ruído de fundo
  - Cancelamento de eco (AEC)
  - Detecção de atividade de voz
- **Comunicação:** ZeroMQ PUB → Wake Word
- **Formato:** PCM 16kHz mono 16-bit

---

### 2. **wake-word-detector**
- **Função:** Detecta palavra-chave "ASLAM"
- **Tecnologia:** OpenWakeWord (Open Source)
- **Responsabilidades:**
  - Detecção em tempo real
  - Baixo consumo de recursos
  - Publica evento de ativação
  - Supressão baseada em eventos
- **Comunicação:** 
  - Entrada: áudio do audio-capture-vad (ZeroMQ SUB)
  - Saída: evento NATS `wake_word.detected`
- **Trigger:** Inicia processamento paralelo (Verification + Whisper + Speaker ID)

---

### 3. **speaker-verification**
- **Função:** Valida usuários autorizados
- **Tecnologia:** Resemblyzer ou pyannote.audio
- **Responsabilidades:**
  - Verifica se é você ou sua esposa
  - Rejeita vozes desconhecidas
  - Cria embeddings de voz
- **Comunicação:** gRPC
- **Segurança:** Apenas vozes cadastradas podem ativar

---

### 4. **whisper-asr (STT)**
- **Função:** Speech-to-Text em streaming
- **Tecnologia:** Whisper.cpp (otimizado ARM)
- **Responsabilidades:**
  - Transcrição em chunks de 200-300ms
  - Baixa latência
  - Streaming contínuo
  - Timestamp por chunk
- **Comunicação:** 
  - Entrada: PCM via gRPC
  - Saída: JSON `{text, timestamp}` → Core API
- **Alternativa:** Coqui STT

---

### 5. **speaker-id-diarization**
- **Função:** Identifica QUEM está falando
- **Tecnologia:** pyannote.audio
- **Responsabilidades:**
  - Separação por falante
  - Detecção de sobreposição de vozes
  - Criação de embeddings por speaker
  - Metadados `{text, speaker_id, confidence}`
- **Comunicação:** REST/gRPC streaming
- **Trigger condicional:** Se sobreposição → aciona Source Separation

---

### 6. **source-separation** (Opcional/Condicional)
- **Função:** Separa vozes sobrepostas
- **Tecnologia:** Demucs
- **Responsabilidades:**
  - Ativado APENAS quando detecta sobreposição
  - Separa canais por falante
  - Reenvia para STT refinado
- **Comunicação:** gRPC
- **Nota:** Não afeta latência em conversas normais

---

### 7. **core-gateway**
- **Função:** Gateway REST + WebSocket para Dashboard UI
- **Tecnologia:** Node.js + Express + WS
- **Responsabilidades:**
  - Expor API REST para Dashboard
  - WebSocket para updates em tempo real
  - Rate limiting por speaker_id
  - Roteamento para serviços internos
  - Health checks de containers
- **Comunicação:** REST + WebSocket + NATS
- **Porta:** 3000

---

### 8. **conversation-manager**
- **Função:** Gerencia estado e contexto de conversações
- **Tecnologia:** Node.js + Prisma + Qdrant Client
- **Responsabilidades:**
  - Criar/atualizar/encerrar conversações
  - Manter contexto por speaker_id
  - Persistir no PostgreSQL
  - Buscar contexto semântico (RAG) no Qdrant
  - Coordenar pipeline STT → Brain → TTS
- **Comunicação:** NATS + gRPC + PostgreSQL + Qdrant

---

### 9. **action-dispatcher**
- **Função:** Despacha comandos para outros módulos
- **Tecnologia:** Node.js + NATS + Circuit Breaker
- **Responsabilidades:**
  - Parsear actions do Brain
  - Enviar comandos via NATS para IoT, Comunicação, Pagamentos, etc
  - Aguardar confirmações (request/reply)
  - Retry logic com exponential backoff
  - Circuit breaker por módulo
- **Comunicação:** NATS request/reply
- **Integrações:** Todos os 8 módulos externos

---

### 10. **mordomo-brain (LLM)**
- **Função:** Cérebro do assistente
- **Tecnologia:** 
  - **Primário (Cloud):** Claude, GPT-4, Gemini, Groq via LiteLLM
  - **Fallback (Local):** Ollama (Qwen 2.5 1.5B quantizado)
- **Responsabilidades:**
  - Processamento de linguagem natural
  - Manutenção de contexto por speaker
  - Detecção de intenções
  - Roteamento de tarefas (IoT, clima, etc)
  - Estratégias LiteLLM:
    - `cloud-first` (padrão: Claude/GPT → fallback 1.5B local)
    - `cloud-only` (sem fallback, mais confiável)
    - `local-only` (offline mode, Qwen 1.5B)
- **Comunicação:** gRPC
- **Entrada:** `{text, speaker_id, timestamp, context}`
- **Saída:** `{response_text, speaker_id, actions[]}`

---

### 11. **tts-engine**
- **Função:** Text-to-Speech em streaming
- **Tecnologia:** 
  - **Principal:** Piper TTS (super leve, ARM)
  - **Alternativa:** Coqui TTS
- **Responsabilidades:**
  - Síntese de voz natural
  - Streaming em chunks
  - Pausável/interrompível
  - Baixa latência (<500ms)
- **Comunicação:** REST/gRPC
- **Formato:** PCM 16kHz mono → alto-falante

---

## 🔄 Fluxo de Dados Completo

```text
[Usuário fala no tablet]
         ↓
[1. audio-capture-vad] → filtra ruído/silêncio
         ↓
[2. wake-word-detector] → detecta "ASLAM"
         ↓
[3. speaker-verification] → autorizado?
         ├─ Não → descarta
         └─ Sim → continua
                 ↓
         [4. whisper-asr] → transcreve em chunks
                 ↓
         [5. speaker-id-diarization] → identifica falante
                 ↓
         (se sobreposição → [6. source-separation])
                 ↓
         [7. mordomo-core-api] → orquestra
                 ↓
         [8. mordomo-brain] → processa com LLM
                 │
                 ├─► Qdrant (busca vetorial)
                 ├─► PostgreSQL (histórico)
                 └─► NATS (eventos)
                 ↓
         [9. tts-engine] → sintetiza resposta
                 ↓
         [Alto-falante] → reproduz
                 ↓
         [12. dashboard-ui] → mostra log
```

---

## 🔗 Integração com Outros Ecossistemas

### Infraestrutura
- **NATS:** Message broker compartilhado (substitui o antigo event-bus local)
- **Consul:** Service discovery compartilhado
- **Qdrant:** Armazena embeddings de conversas e speakers
- **PostgreSQL:** Persiste histórico, usuários, configurações
- **Aslam App:** Interface tablet/web

### Monitoramento
- **Prometheus:** Métricas de latência, uso de CPU/RAM, chamadas
- **Loki:** Logs centralizados de todos containers
- **Grafana:** Dashboard visual de saúde do sistema
- **Promtail:** Coleta logs de todos containers

---

## ⚙️ Configuração e Deploy

### Docker Compose
Todos os containers rodando em uma rede:
```yaml
networks:
  mordomo-net:
    driver: bridge
```

### Variáveis de Ambiente
```env
WAKE_WORD=ASLAM
LLM_MODE=cloud-first  # cloud-first | cloud-only | local-only
LLM_CLOUD_MODEL=claude-3-5-sonnet-20241022  # ou gpt-4o, gemini-2.0-flash
LLM_LOCAL_FALLBACK=qwen2.5:1.5b
CLOUD_API_KEY=sk-...
SPEAKER_VERIFICATION=enabled
MAX_SPEAKERS=2
```

### Hardware Mínimo
- **RAM:** 4GB (ideal 8GB)
- **CPU:** ARM64 quad-core
- **Storage:** 32GB (modelos LLM locais)

---

## 📊 Métricas Importantes

- **Latência STT:** <300ms
- **Latência LLM:** <500ms (local) / <1s (cloud)
- **Latência TTS:** <200ms
- **Latência Total:** <1.5s (wake word → primeira palavra falada)
- **Precisão Speaker ID:** >95%
- **Uptime:** 99.9%

---

## 🚀 Casos de Uso

1. **Controle de Casa Inteligente**
   - "Aslam, acende a luz da sala"
   - "Aumenta o ar condicionado"

2. **Consultas Contextuais**
   - Você: "Qual a temperatura?"
   - Aslam: "23°C"
   - Você: "E na sala?" (mantém contexto)

3. **Multiusuário**
   - Você: "Toca jazz"
   - Esposa (interrompe): "Não, toca clássica"
   - Aslam processa ambos pedidos separadamente

4. **Interrupções Naturais**
   - Aslam: "A previsão do tempo é..."
   - Você: "Espera, só me diz de amanhã"
   - Aslam: *para e responde sobre amanhã*

---

## 🔒 Segurança

- ✅ **Speaker Verification:** Apenas vozes autorizadas
- ✅ **Local-first:** Dados sensíveis não saem da rede local
- ✅ **Encryption:** TLS para comunicação externa
- ✅ **Isolamento:** Containers em rede privada

---

## 📝 Próximos Passos

- [ ] Implementar plugins para IoT (Zigbee, Matter)
- [ ] Adicionar suporte a mais idiomas
- [ ] Melhorar Source Separation com modelo mais leve
- [ ] Criar modo "silencioso" (apenas texto, sem TTS)
- [ ] Integração com calendário e lembretes

---

**Documentação atualizada:** 27/11/2025
