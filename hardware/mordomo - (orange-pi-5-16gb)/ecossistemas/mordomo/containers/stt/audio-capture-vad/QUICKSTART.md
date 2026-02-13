# 🎤 Audio Capture + VAD - Guia de Execução Local

## 📦 Instalação

### 1. Instalar dependências Python

```powershell
# Criar ambiente virtual (recomendado)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 2. Descobrir seu microfone

```powershell
python list_devices.py
```

Isso vai mostrar todos os microfones disponíveis. Copie o número `[X]` do microfone desejado.

### 2.5. **IMPORTANTE: Testar nível do microfone**

```powershell
python test_microphone.py [número_do_dispositivo]
```

**Fale no microfone por 5 segundos**. O script vai te dizer se o volume está adequado.

📊 **Resultados esperados:**
- ✅ RMS entre 500-2000 = **IDEAL**
- ⚠️ RMS entre 100-500 = Funciona, mas pode melhorar
- ❌ RMS < 100 = **MUITO BAIXO** - VAD não vai detectar!

Se o RMS estiver baixo:
1. Vá em **Configurações de Som do Windows**
2. Propriedades do Microfone → **Aumentar volume para 70-80%**
3. Ative **"Boost do microfone"** se disponível
4. Teste novamente até RMS ficar > 500

### 3. Configurar microfone

Edite `config/audio.yaml` e coloque o número do dispositivo:

```yaml
audio:
  device:
    index: 0  # ← Coloque o número aqui (ou null para usar padrão)
```

## 🚀 Rodar

### Modo básico (apenas console)

```powershell
python src/main.py
```

Você vai ver:
- 🎤 Barras de áudio quando detectar voz
- 🔇 Mensagem de silêncio quando não houver voz
- 📊 Estatísticas a cada 10 segundos

### Parar

Pressione `Ctrl+C`

## 🔧 Configurações

### Ajustar sensibilidade do VAD

Edite `config/audio.yaml`:

```yaml
vad:
  mode: 3  # 0=menos sensível, 3=mais sensível
```

- **0** = Melhor qualidade (só detecta voz clara)
- **1** = Low bitrate
- **2** = Agressivo (detecta mais fácil)
- **3** = Muito agressivo (detecta tudo)

### Habilitar ZeroMQ (para distribuir áudio)

```yaml
output:
  zeromq:
    enabled: true  # ← Mude para true
```

**Nota:** Isso vai publicar áudio em `tcp://*:5555` para outros componentes consumirem.

## 🐛 Problemas Comuns

### "No module named sounddevice"

```powershell
pip install sounddevice
```

### "PortAudio library not found" (Windows)

Baixe e instale: http://www.portaudio.com/download.html

Ou instale via pip:
```powershell
pip install pipwin
pipwin install pyaudio
```

### "No devices found"

Verifique se o microfone está conectado e funcionando no Windows.

### VAD muito sensível (detecta tudo)

```yaml
vad:
  mode: 0  # Menos sensível
```

### VAD pouco sensível (não detecta nada)

```yaml
vad:
  mode: 3  # Mais sensível
```

## 📊 O que você vai ver

```
2025-12-03 10:30:45 - __main__ - INFO - Carregando configuração...
2025-12-03 10:30:45 - __main__ - INFO - Iniciando Audio Capture + VAD...
2025-12-03 10:30:45 - audio_capture - INFO - VAD inicializado com modo 3
2025-12-03 10:30:45 - audio_capture - INFO - Audio Capture configurado:
2025-12-03 10:30:45 - audio_capture - INFO -   Sample Rate: 16000 Hz
2025-12-03 10:30:45 - audio_capture - INFO -   Channels: 1
2025-12-03 10:30:45 - audio_capture - INFO -   Frame Size: 480 samples (30ms)
2025-12-03 10:30:45 - __main__ - INFO - ✅ Sistema iniciado. Pressione Ctrl+C para parar.
🎤 VOZ: [████████████████░░░░░░░░░░] 0.345
```

Quando você falar, vai mostrar a barra de energia da voz!
