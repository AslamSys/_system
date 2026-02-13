# 🎵 Efeitos Sonoros (Earcons)

Este diretório contém os arquivos de áudio curtos para feedback sonoro do sistema (Earcons).
O `audio-bridge` carrega estes arquivos na memória na inicialização e os reproduz baseados em eventos do NATS.

## 📋 Requisitos dos Arquivos

- **Formato:** WAV (PCM 16-bit)
- **Sample Rate:** 16000Hz ou 44100Hz (será feito resample se necessário)
- **Canais:** Mono ou Stereo
- **Duração:** Curta (< 1 segundo idealmente)

## 📂 Arquivos Esperados

| Arquivo | Evento Gatilho (NATS) | Descrição |
| :--- | :--- | :--- |
| `wake.wav` | `wake_word.detected` | Som de "atenção" (ex: *Plim!*). Tocado quando o robô ouve seu nome. |
| `thinking.wav` | `llm.processing` | Som de processamento (ex: *Tudum...*). Tocado quando o STT finaliza e o Brain começa a pensar. |
| `success.wav` | `action.completed` | Som de confirmação (ex: *Bip!*). Tocado após uma ação bem sucedida (IoT). |
| `error.wav` | `system.error` | Som de falha (ex: *Bop.*). Tocado se houver erro no pipeline ou timeout. |
| `listening_end.wav` | `vad.silence_detected` | (Opcional) Som sutil indicando que o robô parou de ouvir. |

## 🛠️ Como Adicionar

1. Adicione seus arquivos `.wav` nesta pasta.
2. Reinicie o container `audio-bridge`.
3. O sistema detectará automaticamente os arquivos e habilitará os triggers.
