# 🎬 Entretenimento Brain

**Container:** `entretenimento-brain`  
**LLM:** Ollama Qwen 1.5B Q4_K_M  
**Hardware:** Raspberry Pi 5 8GB

---

## 📋 Propósito

LLM para interpretar comandos de entretenimento ("coloca aquele filme do Tom Hanks na ilha"), buscar conteúdo e recomendar filmes/séries baseado no histórico.

---

## 🎯 Responsabilidades

- ✅ Interpretar comandos vagos ("aquele filme do Tom Hanks na ilha" → "Cast Away")
- ✅ Buscar conteúdo no Jellyfin (fuzzy matching)
- ✅ Recomendar filmes/séries baseado em histórico
- ✅ Resolver ambiguidades ("tem 3 filmes do Batman, qual você quer?")

---

## 🔧 Tecnologias

```yaml
Core:
  - Ollama (Qwen 1.5B Q4_K_M)
  - NATS (comandos de mídia)
  - PostgreSQL (histórico de reprodução)
  - Jellyfin API (busca de conteúdo)

Optional:
  - scikit-learn (recomendação colaborativa)
  - IMDb API (metadata)
```

---

## 📊 Especificações

```yaml
VRAM: 0.9GB (Qwen 1.5B Q4)
RAM: 2.5GB (modelo + contexto)
CPU: 120%
Latência: 400-600ms
Temperature: 0.3  # Criatividade moderada
```

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "entretenimento.search.content"
Payload: {
  "user_input": "aquele filme do Tom Hanks na ilha",
  "type": "movie|series|music"
}

Topic: "entretenimento.recommend"
Payload: {
  "user_id": "user_123",
  "context": "noite de sexta, família"
}
```

### Publish
```javascript
Topic: "entretenimento.play.movie"
Payload: {
  "title": "Cast Away",
  "file_path": "/media/movies/Cast Away (2000).mkv",
  "jellyfin_id": "abc123",
  "device": "tv_sala"
}

Topic: "entretenimento.recommendation"
Payload: {
  "title": "O Terminal",
  "reason": "Outro filme do Tom Hanks, gênero drama",
  "rating": 8.1
}
```

---

## 🧠 System Prompt

```markdown
# SISTEMA: Assistente de Entretenimento Mordomo

## FUNÇÃO
Você é o módulo de entretenimento do Mordomo.
Interpreta comandos de mídia e recomenda conteúdo.

## CAPACIDADES
1. Resolver conteúdo vago
   - "aquele filme do Tom Hanks na ilha" → "Cast Away"
   - "série de médico com House" → "House M.D."
2. Recomendar conteúdo
   - Baseado em histórico do usuário
   - Considerar contexto (noite, família, etc)
3. Buscar no Jellyfin
   - Fuzzy matching de títulos
   - Filtrar por gênero, ano, ator

## FORMATO DE SAÍDA
{
  "intent": "play | search | recommend",
  "content_type": "movie | series | music",
  "title": "Cast Away",
  "year": 2000,
  "confidence": 0.95,
  "alternatives": ["The Terminal", "Forrest Gump"]
}

## REGRAS
- Se múltiplos resultados, perguntar ao usuário
- Priorizar dublado português se disponível
- Sugerir legendas se necessário
```

---

## 🚀 Docker Compose

```yaml
entretenimento-brain:
  build: ./entretenimento-brain
  environment:
    - OLLAMA_API_URL=http://localhost:11434
    - MODEL_NAME=qwen:1.5b-q4_K_M
    - NATS_URL=nats://mordomo-nats:4222
    - JELLYFIN_URL=http://media-server:8096
    - JELLYFIN_API_KEY=${JELLYFIN_API_KEY}
    - TEMPERATURE=0.3
  volumes:
    - ollama-models:/root/.ollama
  deploy:
    resources:
      limits:
        cpus: '1.2'
        memory: 2560M
```

---

## 🧪 Código

```python
from ollama import Client
import requests, json

ollama = Client(host='http://localhost:11434')
jellyfin_url = os.getenv('JELLYFIN_URL')
jellyfin_api_key = os.getenv('JELLYFIN_API_KEY')

async def search_content(msg):
    data = json.loads(msg.data.decode())
    
    # LLM resolve query vaga
    response = ollama.chat(model='qwen:1.5b-q4_K_M', messages=[
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': f"Identifique o filme/série: '{data['user_input']}'"}
    ], options={'temperature': 0.3})
    
    parsed = json.loads(response['message']['content'])
    
    # Buscar no Jellyfin
    search_results = requests.get(f"{jellyfin_url}/Items", params={
        'searchTerm': parsed['title'],
        'IncludeItemTypes': 'Movie' if data['type'] == 'movie' else 'Series',
        'api_key': jellyfin_api_key
    }).json()
    
    if search_results['Items']:
        best_match = search_results['Items'][0]
        
        await nc.publish('entretenimento.play.movie', json.dumps({
            'title': best_match['Name'],
            'file_path': best_match['Path'],
            'jellyfin_id': best_match['Id'],
            'device': 'tv_sala'
        }).encode())
    else:
        await nc.publish('entretenimento.error', json.dumps({
            'error': 'content_not_found',
            'query': parsed['title']
        }).encode())

await nc.subscribe('entretenimento.search.content', cb=search_content)
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Ollama Qwen 1.5B
- ✅ Jellyfin integration
- ✅ Fuzzy content matching
- ✅ Recommendation system
