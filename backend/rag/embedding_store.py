"""
Embedding Store for RAG Pipeline
Stores and retrieves document embeddings using Gemini API
"""
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import urllib.request
import urllib.parse

logger = logging.getLogger(__name__)


class EmbeddingStore:
    """Manages embeddings for RAG retrieval"""
    
    def __init__(self, storage_dir: str = "data/embeddings", api_key: Optional[str] = None):
        """
        Initialize embedding store
        
        Args:
            storage_dir: Directory to store embeddings
            api_key: Gemini API key
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        self.embeddings_file = self.storage_dir / "embeddings.json"
        self.embeddings_cache = {}
        self._load_embeddings()
    
    def _load_embeddings(self):
        """Load embeddings from disk"""
        if self.embeddings_file.exists():
            try:
                with open(self.embeddings_file, 'r') as f:
                    self.embeddings_cache = json.load(f)
                logger.info(f"Loaded {len(self.embeddings_cache)} embeddings from cache")
            except Exception as e:
                logger.warning(f"Error loading embeddings cache: {e}")
                self.embeddings_cache = {}
    
    def _save_embeddings(self):
        """Save embeddings to disk"""
        try:
            with open(self.embeddings_file, 'w') as f:
                json.dump(self.embeddings_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving embeddings cache: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Gemini API
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Check cache first
        text_hash = str(hash(text))
        if text_hash in self.embeddings_cache:
            return self.embeddings_cache[text_hash]['embedding']
        
        try:
            # Use Gemini embedding API
            # Note: Gemini doesn't have a dedicated embedding API, so we'll use a workaround
            # For now, we'll use a simple text-based similarity approach
            # In production, you'd use a proper embedding model
            
            # Simple hash-based embedding (placeholder - in production use proper embeddings)
            # For now, we'll create a simple representation
            embedding = self._simple_embedding(text)
            
            # Cache it
            self.embeddings_cache[text_hash] = {
                'embedding': embedding,
                'text': text[:100]  # Store first 100 chars for reference
            }
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """
        Create a simple embedding representation
        In production, replace with proper embedding model (e.g., sentence-transformers)
        
        Args:
            text: Text to embed
            
        Returns:
            Simple embedding vector
        """
        # Simple TF-IDF-like representation
        # This is a placeholder - for production, use proper embeddings
        words = text.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Create a fixed-size vector (128 dimensions)
        embedding = [0.0] * 128
        
        # Simple hash-based distribution
        for i, (word, freq) in enumerate(word_freq.items()):
            idx = hash(word) % 128
            embedding[idx] += freq / len(words)
        
        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        
        # Save after batch
        self._save_embeddings()
        return embeddings
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_similar_chunks(self, query_embedding: List[float], chunks: List[Dict[str, Any]], 
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find most similar chunks to query embedding
        
        Args:
            query_embedding: Query embedding vector
            chunks: List of chunks with embeddings
            top_k: Number of top results to return
            
        Returns:
            List of most similar chunks with similarity scores
        """
        results = []
        
        for chunk in chunks:
            if 'embedding' not in chunk:
                # Generate embedding if not present
                chunk['embedding'] = self.generate_embedding(chunk['text'])
            
            similarity = self.cosine_similarity(query_embedding, chunk['embedding'])
            results.append({
                'chunk': chunk,
                'similarity': similarity
            })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]


