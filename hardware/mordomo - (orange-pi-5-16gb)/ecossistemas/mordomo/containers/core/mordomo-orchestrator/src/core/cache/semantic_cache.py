import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
from typing import Optional, Dict, Tuple

class SemanticCache:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', threshold: float = 0.90):
        """
        Inicializa o Semantic Cache.
        :param model_name: Modelo de embeddings (HuggingFace).
        :param threshold: Limiar de similaridade (0.0 a 1.0) para considerar um HIT.
        """
        print(f"Carregando modelo de embeddings: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.threshold = threshold
        
        # Inicializa índice FAISS (FlatIP = Inner Product, bom para similaridade de cosseno se normalizado)
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Armazena mapeamento ID -> Resposta/Ação (em memória por enquanto, idealmente SQLite/Redis)
        self.cache_data: Dict[int, Dict] = {}
        self.next_id = 0
        
        print("Semantic Cache inicializado.")

    def _get_embedding(self, text: str) -> np.ndarray:
        """Gera embedding normalizado para o texto."""
        embedding = self.model.encode([text])[0]
        faiss.normalize_L2(embedding.reshape(1, -1))
        return embedding

    def search(self, text: str) -> Optional[Dict]:
        """
        Busca no cache por um comando similar.
        :return: O objeto de ação/resposta se encontrar (HIT), ou None (MISS).
        """
        if self.index.ntotal == 0:
            return None

        embedding = self._get_embedding(text)
        
        # Busca o vizinho mais próximo (k=1)
        D, I = self.index.search(np.array([embedding]), k=1)
        
        score = D[0][0]
        idx = I[0][0]
        
        if score >= self.threshold:
            print(f"CACHE HIT: '{text}' (Score: {score:.4f}) -> ID {idx}")
            return self.cache_data.get(idx)
        
        print(f"CACHE MISS: '{text}' (Melhor Score: {score:.4f})")
        return None

    def add(self, text: str, action_data: Dict):
        """
        Adiciona um novo comando ao cache.
        """
        embedding = self._get_embedding(text)
        
        self.index.add(np.array([embedding]))
        self.cache_data[self.next_id] = action_data
        self.next_id += 1
        print(f"Adicionado ao cache: '{text}' -> ID {self.next_id - 1}")

    def save_to_disk(self, path: str):
        """Persiste o índice e dados em disco."""
        faiss.write_index(self.index, f"{path}/semantic_cache.index")
        with open(f"{path}/semantic_cache_data.json", 'w') as f:
            json.dump(self.cache_data, f)

    def load_from_disk(self, path: str):
        """Carrega índice e dados do disco."""
        if os.path.exists(f"{path}/semantic_cache.index"):
            self.index = faiss.read_index(f"{path}/semantic_cache.index")
            with open(f"{path}/semantic_cache_data.json", 'r') as f:
                # JSON keys are strings, convert back to int
                data = json.load(f)
                self.cache_data = {int(k): v for k, v in data.items()}
                self.next_id = max(self.cache_data.keys()) + 1 if self.cache_data else 0
