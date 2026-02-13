# 📁 Estrutura do Projeto - Speaker ID/Diarization

```
speaker-id-diarization/
│
├── 📄 README.md                      # Documentação completa do serviço
├── 📄 Dockerfile                     # Imagem Docker
├── 📄 docker-compose.yml             # Orquestração do container
├── 📄 requirements.txt               # Dependências Python
├── 📄 .env.example                   # Variáveis de ambiente
├── 📄 .gitignore                     # Arquivos ignorados
│
├── 📂 proto/                         # Protocol Buffers (gRPC)
│   └── speaker_id.proto              # Definições de mensagens
│
├── 📂 src/                           # Código fonte
│   ├── __init__.py                   # Package marker
│   ├── main.py                       # Entry point principal
│   ├── config.py                     # Configurações
│   ├── speaker_identifier.py        # Lógica híbrida (diarization + recognition)
│   ├── grpc_server.py                # Servidor gRPC
│   ├── nats_client.py                # Cliente NATS com gate mechanism
│   └── metrics.py                    # Métricas Prometheus
│
├── 📂 test_data/                     # Scripts e dados de teste
│   ├── README.md                     # Documentação dos testes
│   ├── requirements.txt              # Dependências de teste
│   ├── create_embedding.py           # Criar embeddings de usuários
│   ├── test_diarization.py           # Testar separação de falantes
│   ├── embeddings/                   # Embeddings cadastrados (*.npy)
│   └── audio/                        # Áudios e resultados de teste
│
├── 📂 data/                          # Dados (criado em runtime)
│   └── embeddings/                   # Compartilhado com Speaker Verification (RO)
│
└── 📂 logs/                          # Logs estruturados (criado em runtime)
```

## 🔑 Componentes Principais

### 1. **speaker_identifier.py** - Core Logic
- ✅ Diarization com pyannote.audio
- ✅ Recognition com Resemblyzer
- ✅ Comparação com embeddings cadastrados
- ✅ Detecção de overlap
- ✅ Hot reload de embeddings

### 2. **nats_client.py** - Gate Mechanism
- ✅ Buffering até `speaker.verified`
- ✅ Descarte em `speaker.rejected`
- ✅ Reset em `conversation.ended`
- ✅ Publicação de resultados

### 3. **grpc_server.py** - Interface gRPC
- ✅ Recebe áudio + transcript do Whisper ASR
- ✅ Processa diarization
- ✅ Retorna segmentos identificados
- ✅ Suporte a streaming

### 4. **metrics.py** - Observabilidade
- ✅ Latência de processamento
- ✅ Taxa de reconhecimento
- ✅ Detecções de unknown
- ✅ Detecções de overlap

## 🧪 Testes

### Scripts Disponíveis

1. **create_embedding.py**
   - Grava áudio do microfone
   - Cria embedding (256D)
   - Salva em `.npy`

2. **test_diarization.py**
   - Grava áudio com múltiplos falantes
   - Processa diarization simplificada
   - Mostra resultados e estatísticas

### Fluxo de Teste

```
1. Criar embeddings
   └─> python test_data/create_embedding.py user_1
   └─> python test_data/create_embedding.py user_2

2. Testar separação
   └─> python test_data/test_diarization.py
   
3. Analisar resultados
   └─> test_data/audio/results_*.json
```

## 🐳 Docker

### Build
```bash
docker-compose build
```

### Run
```bash
docker-compose up -d
```

### Logs
```bash
docker-compose logs -f speaker-id-diarization
```

## 🔗 Integrações

- **Input:** Whisper ASR (gRPC port 50053)
- **Output:** Conversation Manager (NATS)
- **Shared:** Embeddings com Speaker Verification (volume mount)
- **Monitoring:** Prometheus (port 8003)

## 📊 Portas

- `50053` - gRPC server
- `8003` - Prometheus metrics

## 🔐 Segurança

**Re-autenticação contínua:**
- Detecta troca de falante durante conversação
- Previne escalação de privilégios
- Marca vozes desconhecidas como `recognized: false`
- Conversation Manager ignora comandos de unknowns
