# 🔊 Ambiente TTS (Text-to-Speech)

**Propósito:** Síntese de voz → Reprodução de áudio com streaming e interrupção

---

## 📊 Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    AMBIENTE TTS (2 containers)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1️⃣ TTS Engine (Síntese)                                         │
│     ├─ Recebe: NATS tts.generate.{speaker_id}                  │
│     │  └─ payload: {text, speaker_id, voice}                   │
│     ├─ Processa: Azure Speech (291ms) ou Piper (108ms)         │
│     └─ Publica: NATS tts.audio_chunk.{speaker_id}              │
│        └─ payload: {data (base64), chunk_index, is_final}      │
│                          │                                      │
│                          ▼                                      │
│  2️⃣ Audio Bridge (Reprodução)                                   │
│     ├─ Recebe: NATS tts.audio_chunk.{speaker_id}               │
│     ├─ Decodifica: base64 → PCM 16-bit                         │
│     └─ Reproduz: ALSA/PulseAudio (streaming)                   │
│                                                                 │
│  ⚠️ Interrupção (quando usuário fala)                           │
│     ├─ STT detecta voz → NATS: tts.interrupt.{speaker_id}      │
│     ├─ TTS Engine para síntese imediatamente                   │
│     └─ Audio Bridge descarta buffer                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎙️ Engines Disponíveis

### **Azure Cognitive Services** (Primário)
```yaml
Vozes PT-BR Neural:
  - pt-BR-FranciscaNeural (♀ 212ms - mais rápida)
  - pt-BR-DonatoNeural    (♂ 291ms - padrão)
  - pt-BR-ThalitaNeural   (♀ 788ms)
  
Free Tier: 500k caracteres/mês
Streaming: Sim (em memória)
Qualidade: Excelente (neural)
```

### **Piper TTS** (Fallback Offline)
```yaml
Modelo: pt_BR-faber-medium.onnx (60MB)
Voz: Masculina grave
Latência: ~108ms (mais rápido!)
Offline: Funciona sem internet
Qualidade: Boa
```

---

## ⚡ Performance

| Engine | Latência | Qualidade | Requisitos |
|--------|----------|-----------|------------|
| **Azure Francisca** | 212ms | ⭐⭐⭐⭐⭐ | Internet |
| **Azure Donato** | 291ms | ⭐⭐⭐⭐⭐ | Internet |
| **Piper Faber** | 108ms | ⭐⭐⭐⭐ | Offline |

**Recomendação:** Azure Donato (padrão) com fallback Piper (quando offline)

---

## 🔄 Casos de Uso

### **1. Resposta Normal**
```
Brain → NATS: tts.generate.user_1
TTS → processa → NATS: tts.audio_chunk (streaming)
Audio Bridge → reproduz em tempo real
TTS → NATS: tts.status (completed)
```

### **2. Interrupção pelo Usuário**
```
TTS sintetizando "A temperatura atual é..."
↓
Usuário: "PARE!" (fala durante resposta)
↓
STT detecta voz → NATS: tts.interrupt.user_1
↓
TTS para imediatamente → NATS: tts.status (interrupted)
↓
Audio Bridge descarta buffer
↓
Sistema processa novo comando "PARE"
```

### **3. Fallback Offline**
```
Brain → NATS: tts.generate (engine=azure)
↓
Azure Speech API timeout (sem internet)
↓
TTS detecta falha → auto-fallback para Piper
↓
Piper processa offline → NATS: tts.audio_chunk
↓
Usuário recebe resposta (latência menor!)
```

---

## 📦 Containers

| Container | Tecnologia | Latência | CPU | RAM | Por quê? |
|-----------|-----------|----------|-----|-----|----------|
| **tts-engine** | Python (FastAPI + Azure/Piper) | 108-291ms | 10-20% | ~200MB | Gargalo é API/modelo (não código) |
| **audio-bridge** | Rust (tokio + NATS) | <5ms | <3% | ~30MB | Latência crítica para reprodução |

**Total:** ~230MB RAM, ~23% CPU (durante síntese)

**Escolha de Tecnologia:**
- **TTS Engine:** Python aceitável - latência dominada por Azure API (200ms) ou Piper model (100ms), overhead Python <5ms desprezível
- **Audio Bridge:** **Rust** para latência mínima (<5ms) na reprodução, zero-copy streaming via tokio

---

## 🔗 Integrações

**Recebe de:**
- Ambiente CORE: Conversation Manager / Brain (via NATS)
- Ambiente STT: Comandos de interrupção (via NATS)

**Envia para:**
- Hardware: Alto-falantes (ALSA/PulseAudio)
- Ambiente CORE: Status de síntese (via NATS)

**Eventos NATS:**
```
Subscreve:
  - tts.generate.{speaker_id}
  - tts.interrupt.{speaker_id}

Publica:
  - tts.audio_chunk.{speaker_id}
  - tts.status.{speaker_id}
```

---

## 🚀 Ordem de Implementação

1. ✅ TTS Engine (síntese com Azure e Piper)
2. ⏳ Audio Bridge (reprodução streaming) **← PRÓXIMO**

---

**Versão:** 1.0
