# 🧠 NAS Brain

**Container:** `nas-brain`  
**LLM:** Ollama Qwen 1.5B Q4_K_M  
**Hardware:** Raspberry Pi 5 8GB

---

## 📋 Propósito

LLM para busca semântica de arquivos, organização inteligente, sugestões de categorias e interpretação de comandos naturais.

---

## 🎯 Responsabilidades

- ✅ Busca semântica ("encontre fotos da praia do ano passado")
- ✅ Sugerir categorias para arquivos novos
- ✅ Detectar duplicatas semanticamente similares
- ✅ Resolver ambiguidades ("aquele PDF de investimentos")
- ✅ Gerar descrições de fotos/vídeos

---

## 🔧 Tecnologias

```yaml
Core:
  - Ollama (Qwen 1.5B Q4_K_M)
  - NATS (comandos de storage)
  - PostgreSQL (metadata de arquivos)
  - Redis (cache de buscas)

Optional:
  - CLIP (embeddings de imagens)
  - Sentence Transformers (embeddings de texto)
  - ChromaDB (vector database)
```

---

## 📊 Especificações

```yaml
VRAM: 0.9GB (Qwen 1.5B Q4)
RAM: 2.5GB (modelo + cache)
CPU: 120%
Latência: 400-600ms
Temperature: 0.3  # Busca requer alguma criatividade
Context: 8192 tokens
```

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "nas.file.search"
Payload: {
  "query": "fotos da praia do ano passado",
  "user_id": "user_123",
  "file_types": ["jpg", "heic", "png"]
}

Topic: "nas.file.categorize"
Payload: {
  "filename": "contrato_aluguel_2025.pdf",
  "path": "/documents/temp/",
  "content_preview": "CONTRATO DE LOCAÇÃO..."
}
```

### Publish
```javascript
Topic: "nas.search.results"
Payload: {
  "query": "fotos da praia",
  "results": [
    {
      "path": "/photos/2024/07/IMG_1234.HEIC",
      "date": "2024-07-15",
      "tags": ["praia", "família", "verão"],
      "confidence": 0.95
    }
  ],
  "count": 47
}

Topic: "nas.file.categorized"
Payload: {
  "filename": "contrato_aluguel_2025.pdf",
  "suggested_path": "/documents/Moradia/Contratos/",
  "category": "contrato",
  "confidence": 0.88
}
```

---

## 🧠 System Prompt

```markdown
# SISTEMA: Assistente de Storage NAS Mordomo

## FUNÇÃO
Você é o módulo de armazenamento do Mordomo.
Busca arquivos semanticamente e organiza bibliotecas.

## CAPACIDADES
1. Busca Semântica
   - "fotos da praia" → tags:beach OR location:praia
   - "documentos de imposto de 2024" → path:/Impostos/ AND date:2024
   - "aquele PDF sobre investimentos" → type:pdf AND content:investimentos
2. Categorização Automática
   - Analisar nome + conteúdo → sugerir pasta
   - Detectar tipo de documento (contrato, nota fiscal, etc)
3. Detecção de Duplicatas
   - Comparar nomes similares
   - Verificar conteúdo (hash já calculado externamente)

## FORMATO DE SAÍDA
Busca:
{
  "search_query": "tags:beach AND date:2024",
  "reasoning": "Usuário quer fotos da praia do ano passado",
  "confidence": 0.95
}

Categorização:
{
  "suggested_path": "/documents/Moradia/Contratos/",
  "category": "contrato_aluguel",
  "confidence": 0.88,
  "reasoning": "Documento contém termos de locação"
}

## REGRAS
- Priorizar precisão sobre recall
- Confiança < 0.7 = pedir confirmação
- Nunca mover/deletar sem confirmação
```

---

## 🚀 Docker Compose

```yaml
nas-brain:
  build: ./nas-brain
  environment:
    - OLLAMA_API_URL=http://localhost:11434
    - MODEL_NAME=qwen:1.5b-q4_K_M
    - NATS_URL=nats://mordomo-nats:4222
    - DATABASE_URL=postgresql://postgres:password@mordomo-postgres:5432/mordomo
    - REDIS_URL=redis://mordomo-redis:6379/6
    - TEMPERATURE=0.3
    - VECTOR_DB_URL=chromadb://nas-chromadb:8000
  volumes:
    - ollama-models:/root/.ollama
  deploy:
    resources:
      limits:
        cpus: '1.2'
        memory: 2560M
  networks:
    - nas-net
    - shared-nats
```

---

## 🧪 Código de Exemplo

```python
from ollama import Client
import chromadb

ollama = Client(host='http://localhost:11434')
chroma = chromadb.HttpClient(host='nas-chromadb', port=8000)
collection = chroma.get_or_create_collection('file_metadata')

async def semantic_search(msg):
    data = json.loads(msg.data.decode())
    
    # LLM interpreta query
    response = ollama.chat(model='qwen:1.5b-q4_K_M', messages=[
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': f"Traduza para busca: '{data['query']}'"}
    ], options={'temperature': 0.3})
    
    parsed = json.loads(response['message']['content'])
    
    # Vector search no ChromaDB
    results = collection.query(
        query_texts=[data['query']],
        n_results=50,
        where={
            'date': {'$gte': '2024-01-01'} if '2024' in parsed['search_query'] else {}
        }
    )
    
    # Publish results
    await nc.publish('nas.search.results', json.dumps({
        'query': data['query'],
        'results': [
            {
                'path': r['path'],
                'date': r['date'],
                'tags': r['tags'],
                'confidence': r['distance']
            }
            for r in results['metadatas'][0]
        ],
        'count': len(results['ids'][0])
    }).encode())

await nc.subscribe('nas.file.search', cb=semantic_search)
```

---

## 📊 Monitoramento

```yaml
Prometheus Metrics:
  - nas_search_latency_ms (p50, p95, p99)
  - nas_searches_total
  - nas_files_categorized_total
  - nas_vector_db_size_mb
```

---

## 🔒 Segurança

```yaml
1. Busca limitada por usuário (ACLs)
2. Conteúdo sensível não indexado (senhas, cartões)
3. Rate limiting: 20 buscas/minuto
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Ollama Qwen 1.5B Q4_K_M
- ✅ Semantic search com ChromaDB
- ✅ Auto categorization
- ✅ Duplicate detection
