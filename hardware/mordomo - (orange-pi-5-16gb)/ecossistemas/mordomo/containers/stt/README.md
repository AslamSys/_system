# 🎤 Ambiente STT (Speech-to-Text)

**Propósito:** Captura de áudio → Detecção de wake word → Transcrição → Identificação de falantes

---

## 📊 Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    AMBIENTE STT (6 containers)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1️⃣ Audio Capture VAD (Produtor ZeroMQ)                         │
│     └─ Captura contínua + filtro VAD → ZeroMQ PUB tcp://*:5555 │
│                          │                                      │
│                          ▼                                      │
│  2️⃣ Wake Word Detector (Consumer ZeroMQ → Trigger NATS)         │
│     └─ Detecta "ASLAM" → NATS: wake_word.detected              │
│                          │                                      │
│              ┌───────────┴───────────┐                          │
│              ▼                       ▼                          │
│  ┌─────────────────────┐   ┌─────────────────────┐             │
│  │ 3️⃣ Speaker          │   │ 4️⃣ Whisper ASR      │             │
│  │    Verification     │   │                     │             │
│  │    (GATE)           │   │    BUFFERING        │             │
│  │    200ms            │   │    (não publica)    │             │
│  └──────┬──────────────┘   └──────┬──────────────┘             │
│         │ speaker.verified        │                            │
│         └──────────┬──────────────┘                            │
│                    │ GATE ABRE                                 │
│                    ▼                                           │
│  5️⃣ Whisper ASR → TRANSCRIBING                                 │
│     └─ Publica buffer + chunks → speech.transcribed            │
│         └─ gRPC → Speaker ID (áudio + texto)                   │
│                    │                                           │
│                    ▼                                           │
│  6️⃣ Speaker ID/Diarization                                      │
│     ├─ Identifica: user_id, recognized flag                   │
│     ├─ Detecta overlap_detected                               │
│     └─ NATS: speech.diarized                                  │
│                    │                                           │
│                    ▼ (SE overlap_detected=true)               │
│  ⚠️ Source Separation (Opcional/Condicional)                   │
│     └─ Separa vozes → reenvia para Whisper (loop refinamento) │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Otimização: Processamento Paralelo

**Problema Original (Sequencial):**
```
wake → verification (200ms) → whisper inicia → first chunk (500ms)
Total: 700ms até primeira transcrição
```

**Solução (Paralelo com GATE):**
```
wake → [verification + whisper + speakerID] paralelos (200ms) 
     → gate abre → resultados prontos
Total: ~500ms até primeira transcrição ✅
```

**Ganho:** 30% redução de latência

---

## 🔒 Segurança (3 Camadas)

1. **Speaker Verification** (GATE 1): Autoriza wake do sistema
2. **Speaker ID/Diarization** (GATE 2): Re-autenticação contínua
3. **Conversation Manager** (GATE 3): Validação de permissões

**Prevenção de Escalação:** Se admin inicia sessão mas convidado tenta comando privilegiado, Speaker ID detecta troca de falante (recognized=false) e Conversation Manager bloqueia.

---

## 📦 Containers

| Container | Tecnologia | Latência | CPU | RAM | Por quê? |
|-----------|-----------|----------|-----|-----|----------|
| **audio-capture-vad** | Python (Sounddevice + WebRTC VAD) | <10ms | <5% | ~50MB | Ecossistema audio Python |
| **wake-word-detector** | Python (OpenWakeWord + PyTorch) | ~50ms | <3% | ~80MB | ML - PyTorch obrigatório |
| **speaker-verification** | Python (Resemblyzer) | ~200ms | <10% | ~100MB | ML embeddings |
| **whisper-asr** | C++ (whisper.cpp) + Python wrapper | 300-500ms | 30-50% | ~500MB | Core C++, wrapper leve |
| **speaker-id-diarization** | Python (pyannote.audio + PyTorch) | ~300ms | 20-30% | ~400MB | ML - PyTorch obrigatório |
| **source-separation** | Python (Demucs + PyTorch) | 1-3s | 60-80% | ~1.5GB | ML - PyTorch obrigatório |

**Total (sem separation):** ~1.13GB RAM, ~70% CPU  
**Total (com separation ativo):** ~2.63GB RAM, ~150% CPU (usa <5% do tempo)

**Escolha de Tecnologia:** Python obrigatório para todo ambiente STT devido ao ecossistema ML (PyTorch, NumPy, scikit-learn). Processamento pesado roda em **C/C++ nativo** (libtorch, OpenBLAS), Python apenas orquestra.

---

## 🔗 Integrações

**Recebe de:**
- Hardware: Microfone (ALSA/PulseAudio)
- Infraestrutura: NATS (eventos)

**Envia para:**
- Ambiente CORE: Conversation Manager (via NATS)
- Próprio ambiente: Comunicação interna (ZeroMQ, gRPC, NATS)

**Compartilha:**
- Volume: `/data/embeddings/` (Verification RW, Diarization RO)

---

## 🚀 Ordem de Implementação

1. ✅ Audio Capture VAD (base de tudo)
2. ✅ Wake Word Detector (trigger)
3. ✅ Whisper ASR (transcrição)
4. ✅ Speaker Verification (autenticação)
5. ⏳ Speaker ID/Diarization (identificação contínua) **← PRÓXIMO**
6. ⏳ Source Separation (overlap handling)

---

**Versão:** 1.0
