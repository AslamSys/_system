# 🏷️ Media Indexer

**Container:** `media-indexer`  
**Stack:** Python + CLIP + FaceNet  
**Propósito:** AI tagging e face recognition

---

## 📋 Propósito

Indexar mídia com AI. Tags automáticas (objetos, cenas), reconhecimento facial, busca por similaridade visual.

---

## 🎯 Features

- ✅ CLIP embeddings (busca semântica de imagens)
- ✅ FaceNet (reconhecimento facial)
- ✅ Auto-tagging (objetos, cenas, cores)
- ✅ Video thumbnails (frame extraction)
- ✅ EXIF metadata extraction

---

## 🚀 Docker Compose

```yaml
media-indexer:
  build: ./media-indexer
  environment:
    - WATCH_PATH=/photos
    - NATS_URL=nats://mordomo-nats:4222
    - CHROMADB_URL=http://nas-chromadb:8000
  volumes:
    - /hot-storage/photos:/photos:ro
    - ./models:/models
  deploy:
    resources:
      limits:
        cpus: '0.8'
        memory: 1024M
```

---

## 🧪 Código (CLIP Tagging)

```python
import torch, clip
from PIL import Image
import chromadb

device = "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

chroma = chromadb.HttpClient(host='nas-chromadb', port=8000)
collection = chroma.get_or_create_collection('photo_embeddings')

async def index_photo(image_path):
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    
    with torch.no_grad():
        image_features = model.encode_image(image)
        embedding = image_features.cpu().numpy()[0]
    
    # Auto-tag with CLIP
    text_prompts = ["beach", "sunset", "family", "food", "nature", "city"]
    text = clip.tokenize(text_prompts).to(device)
    
    with torch.no_grad():
        text_features = model.encode_text(text)
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)[0]
    
    tags = [text_prompts[i] for i, score in enumerate(similarity) if score > 0.3]
    
    # Store in vector DB
    collection.add(
        embeddings=[embedding.tolist()],
        documents=[image_path],
        metadatas=[{
            'path': image_path,
            'tags': tags,
            'indexed_at': datetime.now().isoformat()
        }],
        ids=[hashlib.sha256(image_path.encode()).hexdigest()]
    )
    
    # Publish to NATS
    await nc.publish('nas.photo.indexed', json.dumps({
        'path': image_path,
        'tags': tags
    }).encode())

# Watch for new photos
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PhotoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(('.jpg', '.heic', '.png')):
            asyncio.run(index_photo(event.src_path))

observer = Observer()
observer.schedule(PhotoHandler(), '/photos', recursive=True)
observer.start()
```

---

## 🔍 Visual Search

```python
# Search by text
query = "sunset on the beach"
text = clip.tokenize([query]).to(device)

with torch.no_grad():
    text_features = model.encode_text(text)
    query_embedding = text_features.cpu().numpy()[0]

# Query ChromaDB
results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=10
)

# Returns 10 most similar photos
```

---

## 🔄 Changelog

### v1.0.0
- ✅ CLIP ViT-B/32
- ✅ Auto-tagging
- ✅ ChromaDB vector storage
- ✅ Visual similarity search
