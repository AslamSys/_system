# Test Data Directory

Este diretório contém scripts e dados para testar o Speaker ID/Diarization.

## 📁 Estrutura

```
test_data/
├── embeddings/          # Embeddings de usuários cadastrados
│   ├── user_1.npy
│   └── user_2.npy
├── audio/               # Áudios de teste gravados
│   ├── test_multi_speaker_*.wav
│   └── results_*.json
├── create_embedding.py  # Script para criar embeddings
└── test_diarization.py  # Script para testar diarization
```

## 🚀 Como Usar

### 1. Instalar dependências

```bash
pip install numpy sounddevice soundfile resemblyzer
```

### 2. Criar embeddings de usuários

**Usuário 1:**
```bash
python test_data/create_embedding.py user_1
```

**Usuário 2:**
```bash
python test_data/create_embedding.py user_2
```

Durante a gravação (5 segundos por padrão), fale naturalmente para criar seu embedding.

### 3. Testar diarization com múltiplos falantes

```bash
python test_data/test_diarization.py --duration 10
```

**Durante a gravação:**
- Duas ou mais pessoas devem falar
- Podem revezar ou falar simultaneamente (testar overlap)
- O script dividirá o áudio em segmentos e identificará cada falante

### 4. Resultados

O script mostrará:
- ✅ Segmentos reconhecidos (user_1, user_2)
- ⚠️ Segmentos desconhecidos
- 📊 Estatísticas: falantes detectados, trocas de falante, taxa de reconhecimento
- 💾 Áudio e resultados salvos em `audio/`

## 🎯 Exemplo de Output

```
🔬 Processando áudio...
   Duração total: 10.0s
   Segmentos de: 2.0s
   Threshold: 0.70

✅ [0.0s - 2.0s] user_1 (conf: 0.85)
      user_1: 0.854
      user_2: 0.623

✅ [2.0s - 4.0s] user_2 (conf: 0.78)
      user_1: 0.591
      user_2: 0.783

⚠️ [4.0s - 6.0s] unknown_32000 (conf: 0.65)
      user_1: 0.612
      user_2: 0.654

📊 ANÁLISE DOS RESULTADOS
🗣️  Falantes detectados: 3
   • user_1 (cadastrado): 2 segmentos
   • user_2 (cadastrado): 1 segmento
   • unknown_32000 (desconhecido): 1 segmento

🔄 Trocas de falante: 2
📈 Taxa de reconhecimento: 75.0%
```

## ⚙️ Opções Avançadas

### Ajustar duração da gravação
```bash
python test_data/test_diarization.py --duration 15
```

### Ajustar threshold
```bash
python test_data/test_diarization.py --threshold 0.65
```

### Ajustar duração dos segmentos
```bash
python test_data/test_diarization.py --segment-duration 1.5
```

## 🔧 Troubleshooting

**Erro: "No module named 'sounddevice'"**
```bash
pip install sounddevice soundfile
```

**Erro: "No module named 'resemblyzer'"**
```bash
pip install resemblyzer
```

**Nenhum embedding encontrado:**
- Execute `create_embedding.py` para criar embeddings primeiro

**Taxa de reconhecimento baixa:**
- Aumente a duração do embedding (--duration 10)
- Reduza o threshold (--threshold 0.65)
- Grave em ambiente silencioso
- Fale mais próximo ao microfone
