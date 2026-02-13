# 🚀 GUIA RÁPIDO - Testar Speaker ID/Diarization

## 📋 Pré-requisitos

Você precisará de:
- ✅ Python 3.10+
- ✅ Microfone funcionando
- ✅ Duas pessoas para testar separação de vozes

## 🎯 Passo a Passo

### 1️⃣ Instalar Dependências de Teste

```powershell
cd test_data
pip install -r requirements.txt
```

Isso instalará:
- `sounddevice` - Gravação de áudio
- `soundfile` - Manipulação de arquivos de áudio
- `resemblyzer` - Encoder de voz (compatível com Speaker Verification)
- `numpy` - Operações numéricas

### 2️⃣ Criar Seu Embedding (Usuário 1)

```powershell
python create_embedding.py user_1
```

**O que vai acontecer:**
1. ⏱️ Contador de 3 segundos
2. 🎤 Gravação de 5 segundos
3. 🗣️ **Você deve falar naturalmente durante a gravação**
4. 💾 Embedding salvo em `embeddings/user_1.npy`

**Dicas:**
- Fale com tom natural e variado
- Evite ruído de fundo
- Fale por todo o período (5 segundos)

### 3️⃣ Criar Embedding do Segundo Usuário

```powershell
python create_embedding.py user_2
```

**Peça para outra pessoa:**
- Falar durante os 5 segundos
- Usar voz natural
- O embedding será salvo em `embeddings/user_2.npy`

### 4️⃣ Testar Separação de Vozes

```powershell
python test_diarization.py --duration 10
```

**Durante a gravação de 10 segundos:**

**Opção A - Revezar (testar troca de falante):**
```
0-3s:  Usuário 1 fala: "Olá, meu nome é Renan"
3-6s:  Usuário 2 fala: "E eu sou o João"
6-9s:  Usuário 1 fala: "Qual a temperatura?"
9-10s: Usuário 2 fala: "Desliga a luz"
```

**Opção B - Simultâneo (testar overlap):**
```
0-5s:  Ambos falam ao mesmo tempo
5-10s: Ambos falam juntos novamente
```

### 5️⃣ Analisar Resultados

O script mostrará em tempo real:

```
✅ [0.0s - 2.0s] user_1 (conf: 0.85)
      user_1: 0.854
      user_2: 0.623

✅ [2.0s - 4.0s] user_2 (conf: 0.78)
      user_1: 0.591
      user_2: 0.783

⚠️ [4.0s - 6.0s] unknown_32000 (conf: 0.65)
      user_1: 0.612
      user_2: 0.654
```

**Interpretação:**
- ✅ = Voz reconhecida (confidence ≥ 0.70)
- ⚠️ = Voz desconhecida (confidence < 0.70)
- Números = Similaridade com cada embedding cadastrado

### 6️⃣ Ver Estatísticas Finais

```
📊 ANÁLISE DOS RESULTADOS
🗣️  Falantes detectados: 3
   • user_1 (cadastrado): 2 segmentos
   • user_2 (cadastrado): 1 segmento
   • unknown_32000 (desconhecido): 1 segmento

🔄 Trocas de falante: 2
📈 Taxa de reconhecimento: 75.0%
   Reconhecidos: 3/4 segmentos
```

### 7️⃣ Arquivos Gerados

Verifique o diretório `audio/`:

```
audio/
├── test_multi_speaker_20231203_145623.wav  # Áudio gravado
└── results_20231203_145623.json            # Resultados detalhados
```

## 🔧 Opções Avançadas

### Gravar por mais tempo
```powershell
python test_diarization.py --duration 20
```

### Ajustar threshold (mais ou menos rigoroso)
```powershell
# Mais permissivo (aceita mais vozes)
python test_diarization.py --threshold 0.65

# Mais rigoroso (rejeita mais)
python test_diarization.py --threshold 0.75
```

### Segmentos menores (mais granular)
```powershell
python test_diarization.py --segment-duration 1.5
```

## ❓ Troubleshooting

### Erro: "No module named 'sounddevice'"
```powershell
pip install sounddevice soundfile
```

### Erro: "No module named 'resemblyzer'"
```powershell
pip install resemblyzer
```

### Taxa de reconhecimento baixa (<50%)

**Possíveis causas:**
1. Ambiente muito ruidoso → Grave em local silencioso
2. Microfone de baixa qualidade → Use microfone melhor
3. Fala muito baixa → Fale mais próximo ao microfone
4. Embedding de má qualidade → Recrie com melhor qualidade:

```powershell
# Recriar com mais tempo (10 segundos)
python create_embedding.py user_1 --duration 10
python create_embedding.py user_2 --duration 10
```

### Todos os segmentos como "unknown"

**Solução:**
1. Verifique se os embeddings foram criados:
```powershell
ls embeddings/
# Deve mostrar: user_1.npy, user_2.npy
```

2. Reduza o threshold:
```powershell
python test_diarization.py --threshold 0.60
```

### Não detecta troca de falante

**Solução:**
1. Use segmentos menores:
```powershell
python test_diarization.py --segment-duration 1.0
```

2. Certifique-se que cada pessoa fale por pelo menos 1-2 segundos

## 🎯 Próximos Passos

Após validar que a separação funciona:

1. ✅ Copiar embeddings para produção:
```powershell
# Copiar para diretório compartilhado com Speaker Verification
cp embeddings/*.npy ../data/embeddings/
```

2. ✅ Buildar container Docker:
```powershell
cd ..
docker-compose build
```

3. ✅ Executar serviço completo:
```powershell
docker-compose up -d
```

---

**🎉 Boa sorte com os testes!**
