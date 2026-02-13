# 🎓 Como Treinar Modelo "ASLAM"

Guia prático para criar modelo de wake word customizado para "ASLAM" usando OpenWakeWord.

---

## 📋 O que você vai precisar

- ✅ Python environment configurado (já feito)
- ✅ Microfone funcionando
- ✅ ~30 minutos de tempo
- ✅ Ambiente silencioso para gravação

---

## 🎯 Passo a Passo Completo

### 1️⃣ Gravar Amostras Positivas (palavra "ASLAM")

Execute o script de gravação:

```powershell
# Ative o venv
.venv\Scripts\Activate.ps1

# Instale dependências de treinamento
pip install openwakeword[train]
pip install librosa soundfile
```

### Passo 2: Coletar amostras de áudio

Você precisa de 2 tipos de áudio:

#### A) Amostras POSITIVAS (com "ASLAM"):
- **Quantidade:** 50-200 amostras
- **Duração:** 1-2 segundos cada
- **Conteúdo:** Você falando "ASLAM" de diferentes formas
- **Variações:** 
  - Diferentes tons de voz
  - Diferentes velocidades
  - Diferentes volumes
  - Com/sem ruído de fundo leve

#### B) Amostras NEGATIVAS (sem "ASLAM"):
- **Quantidade:** 100-500 amostras
- **Duração:** 1-5 segundos cada
- **Conteúdo:** 
  - Você falando outras coisas
# Gravar amostras positivas (com "ASLAM")
python gravar_amostras_aslam.py
```

O script vai perguntar:
- **Quantas amostras?** Digite 100 (mínimo 50, recomendado 100+)
- **Fale "ASLAM"** quando aparecer a contagem regressiva

**Dicas importantes:**
- 📢 Varie a entonação: normal, questionando, afirmando
- 🗣️ Varie a velocidade: rápido, normal, devagar
- 📏 Varie a distância: perto, longe do microfone
- 🔊 Varie o volume: normal, mais alto, mais baixo

### 2️⃣ Gravar Amostras Negativas (sem "ASLAM")

Grave sons do ambiente **SEM falar "ASLAM"**:

```powershell
python gravar_amostras_aslam.py --negative
```

**O que gravar (200+ amostras):**
- 💬 Conversas normais (fale sobre qualquer coisa)
- 📺 TV/Rádio ao fundo
- 🎵 Música
- 🏠 Ruído ambiente (ar condicionado, geladeira, etc.)
- 🤐 Silêncio
- 🗣️ Palavras parecidas: "Islam", "Assim", "Assalto"

### 3️⃣ Treinar o Modelo

Após gravar amostras, execute:

```powershell
python treinar_modelo_aslam.py
```

O script vai:
- ✅ Validar quantidade de amostras (mínimo 20 positivas, 50 negativas)
- ✅ Treinar modelo (30 epochs, ~10-20 minutos)
- ✅ Salvar modelo em `models/aslam_v0.1.onnx`

### 4️⃣ Testar o Modelo

Depois de treinar, teste o modelo:

```powershell
# Configure o ambiente para usar seu modelo
$env:WAKE_WORD_MODEL_PATH = "models/aslam_v0.1.onnx"
$env:WAKE_WORD_THRESHOLD = "0.5"

# Execute o serviço e teste
docker-compose up
```

Fale "ASLAM" e veja se detecta! 🎯

---

## 📊 Quantidade Recomendada de Amostras

| Tipo | Mínimo | Recomendado | Ideal |
|------|--------|-------------|-------|
| **Positivas** (ASLAM) | 20 | 100 | 500+ |
| **Negativas** (sem ASLAM) | 50 | 200 | 2000+ |

**Regra de ouro:** Quanto mais amostras, melhor o modelo!

---

## 🎯 Ajustando o Threshold

Após treinar, você pode precisar ajustar o threshold:

- **0.3** = Mais sensível (detecta mais facilmente, mais falsos positivos)
- **0.5** = Balanceado (recomendado para começar)
- **0.7** = Menos sensível (detecta só quando tem certeza)

Teste e ajuste no arquivo `.env`:

```bash
WAKE_WORD_THRESHOLD=0.5
```

---

## 🎤 Dicas para Gravação de Qualidade

### Amostras POSITIVAS:

1. **Varie a entonação:**
   - Normal: "Aslam"
   - Questionando: "Aslam?"
   - Afirmando: "Aslam!"
   - Chamando: "Aslaaam"

2. **Varie a velocidade:**
   - Rápido: "Aslam"
   - Normal: "As-lam"
   - Rápido: "Aslam" (1 seg)
   - Normal: "Aslam" (1.5 seg)
   - Devagar: "Aaaas-laaaaam" (2+ seg)

3. **Varie a distância:**
   - Perto (30cm)
   - Médio (1m)
   - Longe (2-3m)

4. **Varie o ambiente:**
   - Silêncio
   - Com ruído leve de fundo

### Amostras NEGATIVAS:

1. **Palavras similares:**
   - "Islam", "Assalam", "Assim", "Assalto"
   - Outras palavras que rimam ou soam parecido

2. **Conversas normais:**
   - Fale sobre qualquer assunto
   - NÃO mencione "ASLAM"

3. **Ruídos ambiente:**
   - TV, música, ventilador
   - Eletrodomésticos
   - Pessoas conversando

---

## 🔧 Problemas Comuns

### Detecta pouco (falsos negativos)
- ✅ Diminua threshold: `WAKE_WORD_THRESHOLD=0.3`
- ✅ Grave mais amostras positivas variadas

### Detecta demais (falsos positivos)
- ✅ Aumente threshold: `WAKE_WORD_THRESHOLD=0.7`
- ✅ Grave mais amostras negativas com palavras similares

### Erro ao treinar
- ✅ Verifique quantidade mínima (20 positivas, 50 negativas)
- ✅ Verifique formato dos arquivos (WAV)

---

## 📋 Estrutura de Arquivos

Após gravação, você terá:

```
training_data/
├── positive/          # Amostras com "ASLAM"
│   ├── aslam_001.wav
│   ├── aslam_002.wav
│   └── ... (100+)
└── negative/          # Amostras sem "ASLAM"
    ├── negative_001.wav
    ├── negative_002.wav
    └── ... (200+)

models/
└── aslam_v0.1.onnx   # Modelo treinado
```

---

## ⏱️ Tempo Estimado

- **Gravação:** 20-30 minutos
- **Treinamento:** 10-20 minutos (depende do hardware)
- **Testes:** 10 minutos
- **Total:** ~1 hora

---

## 🎯 Próximos Passos

Após treinar seu modelo "ASLAM":

1. Configure o `.env`:
```bash
WAKE_WORD_MODEL_PATH=models/aslam_v0.1.onnx
WAKE_WORD_THRESHOLD=0.5
INFERENCE_FRAMEWORK=onnx
```

2. Execute o serviço:
```powershell
docker-compose up
```

3. Integre com o restante do ecossistema Mordomo! 🚀
