# Speaker Verification - Desenvolvimento

## Estrutura do Projeto
```
speaker-verification/
├── src/
│   ├── main.py              # Serviço principal NATS
│   └── speaker_verifier.py  # Módulo de verificação
├── tests/
│   ├── test_speaker_verifier.py  # Testes unitários
│   └── test_simple.py            # Teste simples
├── scripts/
│   └── enroll_speaker.py    # Script para cadastrar vozes
├── config/
│   └── config.yaml          # Configurações
├── data/
│   └── embeddings/          # Embeddings de usuários
├── requirements.txt
├── Dockerfile
└── README.md
```

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

### 1. Cadastrar Vozes (Enrollment)

Primeiro, você precisa cadastrar as vozes autorizadas:

```bash
python scripts/enroll_speaker.py \
  --user-id user_1 \
  --name "Você" \
  --audio-samples samples/user1/*.wav
```

Isso irá:
- Processar múltiplas amostras de áudio
- Gerar embedding médio
- Salvar em `data/embeddings/user_1.npy`

### 2. Executar Testes

Teste simples (sem dependências externas):
```bash
python tests/test_simple.py
```

Testes completos com pytest:
```bash
pytest tests/test_speaker_verifier.py -v
```

### 3. Executar Serviço

```bash
python src/main.py
```

O serviço irá:
- Conectar ao NATS (localhost:4222)
- Subscrever ao tópico `wake_word.detected`
- Verificar falantes
- Publicar resultados em `speaker.verified` ou `speaker.rejected`

## Docker

Build:
```bash
docker build -t speaker-verification .
```

Run standalone:
```bash
docker run -d \
  --name speaker-verification \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/data/embeddings:/app/data/embeddings \
  -v $(pwd)/data/samples:/app/data/samples \
  --network mordomo-network \
  speaker-verification
```

Run with docker-compose:
```bash
docker-compose up -d
```

**Volumes montados:**
- `./config` → Configurações (read-only)
- `./data/embeddings` → Embeddings persistentes
- `./data/samples` → Amostras de áudio (backup)

## Configuração

Edite `config/config.yaml` para ajustar:
- Threshold de similaridade
- Usuários cadastrados
- URLs do NATS
- Drift adaptation

## Testes

Execute o teste simples para validar:
```bash
python tests/test_simple.py
```

Saída esperada:
```
🧪 Testing Speaker Verification Basic Functionality

1️⃣  Initializing SpeakerVerifier...
   ✅ Initialized with threshold: 0.75

2️⃣  Testing cosine similarity...
   Similarity between identical vectors: 1.000
   ✅ Cosine similarity working correctly

3️⃣  Testing audio duration validation...
   Short audio (0.5s): verified=False, user=None, confidence=0.000
   ✅ Duration validation working correctly

4️⃣  Testing normal audio (without enrolled users)...
   Normal audio (1.5s): verified=False, user=None, confidence=0.000
   ✅ Verification working correctly

5️⃣  Testing get_stats()...
   Stats: {...}
   ✅ Stats working correctly

============================================================
✅ All basic tests passed!
============================================================
```
