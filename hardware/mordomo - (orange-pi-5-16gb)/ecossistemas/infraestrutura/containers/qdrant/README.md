# 🔍 Qdrant Vector Database

**Container:** `qdrant`  
**Ecossistema:** Infraestrutura  
**Papel:** Vector Storage & Similarity Search

---

## 📋 Propósito

Banco de dados vetorial para armazenar embeddings de texto/áudio e realizar buscas de similaridade para RAG (Retrieval-Augmented Generation).

---

## 🎯 Responsabilidades

- ✅ Armazenamento de embeddings vetoriais
- ✅ Busca por similaridade (cosine, dot product, euclidean)
- ✅ Filtros com metadados
- ✅ Collections para diferentes tipos de dados
- ✅ Snapshots e backup
- ✅ Clustering (replicação)

---

## 🔧 Tecnologias

**Qdrant** v1.7+
- Vector storage otimizado
- HNSW indexing (alta performance)
- Filtros com payloads JSON
- gRPC e HTTP API
- Replicação multi-node
- Web UI integrada

**Imagem:** `qdrant/qdrant:v1.7.4`

---

## 📊 Especificações

```yaml
Performance:
  CPU: 10-25%
  RAM: 500 MB - 2 GB (depende do dataset)
  Storage: 1-10 GB (embeddings + índices)
  
Limites:
  Max Vector Dimensions: 65536
  Max Vectors/Collection: Ilimitado (limitado por storage)
  Max Payload Size: 10 MB
  
Indexing:
  Algorithm: HNSW (Hierarchical Navigable Small World)
  Search Speed: < 5ms (100K vectors)
  Precision: > 95%
```

---

## 🗄️ Collections

### 1. Knowledge Base (RAG)
```python
# Embeddings de documentos, FAQs, contexto do usuário
collection_name: "knowledge_base"
vector_size: 384  # all-MiniLM-L6-v2
distance: Cosine

payload_schema:
  - content: str  # Texto original
  - source: str   # URL, file, user_input
  - timestamp: int
  - category: str  # faq, documentation, user_context
  - tags: list[str]
```

### 2. Speaker Embeddings
```python
# Embeddings de voz dos usuários (Resemblyzer)
collection_name: "speaker_embeddings"
vector_size: 256  # Resemblyzer
distance: Cosine

payload_schema:
  - user_id: str
  - user_name: str
  - enrollment_date: str
  - audio_samples: int  # Quantas amostras usadas
  - quality_score: float
```

### 3. Conversation History
```python
# Embeddings de conversas passadas
collection_name: "conversation_history"
vector_size: 384
distance: Cosine

payload_schema:
  - conversation_id: str
  - user_id: str
  - timestamp: int
  - user_text: str
  - assistant_response: str
  - intent: str
  - satisfaction_score: float
```

---

## ⚙️ Configuração

```yaml
# config/production.yaml
service:
  host: 0.0.0.0
  http_port: 6333
  grpc_port: 6334

storage:
  storage_path: /qdrant/storage
  
  # Performance
  optimizers:
    deleted_threshold: 0.2
    vacuum_min_vector_number: 1000
    default_segment_number: 0
    max_segment_size_kb: 20000
    memmap_threshold_kb: 50000
    indexing_threshold_kb: 20000
    flush_interval_sec: 5
  
  # WAL (Write-Ahead Log)
  wal:
    wal_capacity_mb: 32
    wal_segments_ahead: 0

# Cluster (opcional)
cluster:
  enabled: false  # Single node para Orange Pi
  
# Telemetry
telemetry:
  enabled: false
```

---

## 🔌 API Examples

### Collection Creation
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(host="qdrant", port=6333)

# Criar collection Knowledge Base
client.create_collection(
    collection_name="knowledge_base",
    vectors_config=VectorParams(
        size=384,  # all-MiniLM-L6-v2 dimension
        distance=Distance.COSINE
    )
)
```

### Insert Vectors
```python
from qdrant_client.models import PointStruct
import uuid

# Embeddings do modelo de embedding
embeddings = embed_text("Como funciona o assistente Aslam?")

# Inserir
client.upsert(
    collection_name="knowledge_base",
    points=[
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embeddings.tolist(),
            payload={
                "content": "O Aslam é um assistente de voz...",
                "source": "faq",
                "category": "about",
                "timestamp": int(time.time()),
                "tags": ["assistant", "features"]
            }
        )
    ]
)
```

### Search (RAG)
```python
# Buscar contexto relevante
query_embedding = embed_text("Como cadastrar minha voz?")

results = client.search(
    collection_name="knowledge_base",
    query_vector=query_embedding.tolist(),
    limit=5,
    score_threshold=0.7,  # Apenas > 70% similaridade
    query_filter={
        "must": [
            {"key": "category", "match": {"value": "faq"}}
        ]
    }
)

for result in results:
    print(f"Score: {result.score:.2f}")
    print(f"Content: {result.payload['content']}")
    print("---")
```

### Search with Filters
```python
# Buscar conversas de usuário específico
results = client.search(
    collection_name="conversation_history",
    query_vector=query_embedding.tolist(),
    limit=10,
    query_filter={
        "must": [
            {"key": "user_id", "match": {"value": "user_123"}},
            {
                "key": "timestamp",
                "range": {
                    "gte": int(time.time()) - 86400  # Últimas 24h
                }
            }
        ]
    }
)
```

---

## 🧠 RAG Integration

```python
class RAGRetriever:
    def __init__(self):
        self.client = QdrantClient(host="qdrant", port=6333)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def retrieve_context(self, query: str, top_k: int = 3) -> list:
        """Busca contexto relevante para query"""
        
        # 1. Criar embedding da query
        query_vector = self.embedder.encode(query).tolist()
        
        # 2. Buscar no Qdrant
        results = self.client.search(
            collection_name="knowledge_base",
            query_vector=query_vector,
            limit=top_k,
            score_threshold=0.6
        )
        
        # 3. Compilar contexto
        contexts = []
        for result in results:
            contexts.append({
                'content': result.payload['content'],
                'score': result.score,
                'source': result.payload['source']
            })
        
        return contexts
    
    def add_knowledge(self, content: str, metadata: dict):
        """Adiciona novo conhecimento"""
        
        vector = self.embedder.encode(content).tolist()
        
        self.client.upsert(
            collection_name="knowledge_base",
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "content": content,
                        "timestamp": int(time.time()),
                        **metadata
                    }
                )
            ]
        )

# Uso no Brain
rag = RAGRetriever()
context = rag.retrieve_context("Como controlar as luzes?")

# Usar no prompt LLM
prompt = f"""
Context: {json.dumps(context, indent=2)}

User Query: Como controlar as luzes?

Answer based on the context above.
"""
```

---

## 📈 Métricas

```python
# Qdrant expõe métricas via /metrics (Prometheus)

# Collections
qdrant_collections_total
qdrant_collection_vectors_total{collection}
qdrant_collection_segments_total{collection}

# Performance
qdrant_search_duration_seconds{collection}
qdrant_upsert_duration_seconds{collection}
qdrant_requests_total{method,endpoint}

# Storage
qdrant_storage_size_bytes{collection}
qdrant_wal_size_bytes
```

---

## 🐳 Docker

```dockerfile
FROM qdrant/qdrant:v1.7.4

# Config customizada (opcional)
COPY config/production.yaml /qdrant/config/production.yaml

# Storage
VOLUME ["/qdrant/storage"]

EXPOSE 6333 6334

CMD ["./qdrant", "--config-path", "/qdrant/config/production.yaml"]
```

### Docker Compose
```yaml
qdrant:
  image: qdrant/qdrant:v1.7.4
  container_name: qdrant
  ports:
    - "6333:6333"  # HTTP API
    - "6334:6334"  # gRPC
  volumes:
    - ./config/production.yaml:/qdrant/config/production.yaml
    - qdrant-data:/qdrant/storage
  environment:
    - QDRANT__SERVICE__GRPC_PORT=6334
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:6333/"]
    interval: 10s
    timeout: 3s
    retries: 3
  networks:
    - mordomo-net
  restart: unless-stopped

volumes:
  qdrant-data:
```

---

## 🧪 Testes

```python
# test_qdrant.py
def test_collection_creation():
    client = QdrantClient(host="localhost", port=6333)
    
    client.create_collection(
        collection_name="test_collection",
        vectors_config=VectorParams(size=128, distance=Distance.COSINE)
    )
    
    info = client.get_collection("test_collection")
    assert info.vectors_count == 0

def test_upsert_and_search():
    client = QdrantClient(host="localhost", port=6333)
    
    # Inserir
    client.upsert(
        collection_name="test_collection",
        points=[
            PointStruct(
                id="1",
                vector=[0.1] * 128,
                payload={"text": "test"}
            )
        ]
    )
    
    # Buscar
    results = client.search(
        collection_name="test_collection",
        query_vector=[0.1] * 128,
        limit=1
    )
    
    assert len(results) == 1
    assert results[0].id == "1"

def test_filter():
    client = QdrantClient(host="localhost", port=6333)
    
    results = client.search(
        collection_name="knowledge_base",
        query_vector=[0.1] * 384,
        query_filter={
            "must": [
                {"key": "category", "match": {"value": "faq"}}
            ]
        },
        limit=10
    )
    
    for result in results:
        assert result.payload['category'] == 'faq'
```

---

## 🔧 Troubleshooting

### Search muito lento
```yaml
# Aumentar HNSW m parameter (mais memória, mais rápido)
optimizers:
  indexing_threshold_kb: 10000  # Índice menor, mais rápido
```

### Out of Memory
```yaml
# Usar disk-backed storage
storage:
  optimizers:
    memmap_threshold_kb: 10000  # Usar disk mais cedo
```

### Snapshots
```bash
# Criar snapshot
curl -X POST 'http://localhost:6333/collections/knowledge_base/snapshots'

# Listar
curl http://localhost:6333/collections/knowledge_base/snapshots

# Baixar
curl -O http://localhost:6333/collections/knowledge_base/snapshots/snapshot_name
```

---

## 🌐 Web UI

Acesso: **http://localhost:6333/dashboard**

**Funcionalidades:**
- Visualizar collections
- Explorar vectors e payloads
- Testar searches
- Ver estatísticas

---

## 📚 CLI & Tools

```bash
# Python client
pip install qdrant-client

# Criar collection
python -c "
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
client = QdrantClient(host='localhost', port=6333)
client.create_collection('test', VectorParams(size=128, distance=Distance.COSINE))
"

# List collections
curl http://localhost:6333/collections
```

---

## 🚨 Backup & Restore

```python
# Snapshot collection
import requests

# Criar snapshot
response = requests.post(
    'http://localhost:6333/collections/knowledge_base/snapshots'
)
snapshot_name = response.json()['result']['name']

# Download snapshot
with open(f'{snapshot_name}.snapshot', 'wb') as f:
    snapshot = requests.get(
        f'http://localhost:6333/collections/knowledge_base/snapshots/{snapshot_name}'
    )
    f.write(snapshot.content)

# Restore (via upload)
files = {'snapshot': open(f'{snapshot_name}.snapshot', 'rb')}
requests.put(
    'http://localhost:6333/collections/knowledge_base/snapshots/upload',
    files=files
)
```

---

## 🔗 Integração

**Usado por:**
- Brain (RAG context retrieval)
- Core API (knowledge management)
- Speaker Verification (embedding storage)

**APIs:**
- HTTP REST: 6333
- gRPC: 6334

**Monitora:** Prometheus, Grafana

---

## 📝 Data Seeding

```python
# seed_knowledge.py
import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(host="qdrant", port=6333)
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Load FAQ data
with open('faq.json') as f:
    faqs = json.load(f)

# Seed
points = []
for i, faq in enumerate(faqs):
    vector = embedder.encode(faq['question']).tolist()
    
    points.append(PointStruct(
        id=str(i),
        vector=vector,
        payload={
            'content': faq['answer'],
            'question': faq['question'],
            'category': 'faq',
            'source': 'seed',
            'timestamp': int(time.time())
        }
    ))

client.upsert(
    collection_name="knowledge_base",
    points=points
)

print(f"Seeded {len(points)} FAQs")
```

---

**Versão:** 1.0  
**Última atualização:** 27/11/2025  
**Embedding Model:** all-MiniLM-L6-v2 (384 dimensions)
