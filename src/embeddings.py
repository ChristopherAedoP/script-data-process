"""
Embeddings module for RAG MVP
Handles text embedding generation using Sentence Transformers
"""
import time
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

from .config import config


class EmbeddingGenerator:
    """Generate embeddings using Sentence Transformers"""
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        self.model_name = model_name or config.EMBEDDING_MODEL
        self.device = device or config.DEVICE
        self.model = None
        self.embedding_dim = None
        
        # Ensure model cache directory exists
        config.ensure_directories()
        
    def load_model(self) -> None:
        """Load the sentence transformer model"""
        if self.model is not None:
            return
            
        try:
            print(f"Loading embedding model: {self.model_name}")
            start_time = time.time()
            
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=config.get_model_cache_dir()
            )
            
            # Get embedding dimension
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            
            load_time = time.time() - start_time
            print(f"Model loaded in {load_time:.2f}s")
            print(f"Embedding dimension: {self.embedding_dim}")
            print(f"Device: {self.device}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def encode_texts(
        self, 
        texts: List[str], 
        batch_size: Optional[int] = None,
        show_progress: bool = True
    ) -> np.ndarray:
        """Encode list of texts to embeddings"""
        if not texts:
            return np.array([])
            
        self.load_model()
        
        batch_size = batch_size or config.BATCH_SIZE
        
        try:
            print(f"Generating embeddings for {len(texts)} texts...")
            start_time = time.time()
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True  # Important for cosine similarity
            )
            
            generation_time = time.time() - start_time
            avg_time_per_text = generation_time / len(texts) * 1000  # ms
            
            print(f"Generated {len(embeddings)} embeddings")
            print(f"Total time: {generation_time:.2f}s")
            print(f"Average: {avg_time_per_text:.2f}ms per text")
            
            return embeddings
            
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise
    
    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query text"""
        self.load_model()
        
        try:
            embedding = self.model.encode(
                [query],
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embedding[0]  # Return single embedding
            
        except Exception as e:
            print(f"Error encoding query: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """Get model information"""
        self.load_model()
        
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "device": self.device,
            "max_seq_length": getattr(self.model, 'max_seq_length', 'Unknown'),
            "model_card": getattr(self.model, 'model_card', {})
        }
    
    def calculate_similarity(self, query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and document embeddings"""
        try:
            # Ensure embeddings are normalized
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            doc_norms = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
            
            # Calculate cosine similarity
            similarities = np.dot(doc_norms, query_norm)
            return similarities
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            raise
    
    def benchmark_model(self, sample_texts: List[str]) -> dict:
        """Benchmark model performance"""
        if not sample_texts:
            sample_texts = [
                "This is a sample text for benchmarking.",
                "Another example sentence to test the model performance.",
                "Machine learning models require careful evaluation.",
            ]
        
        self.load_model()
        
        # Test encoding speed
        start_time = time.time()
        embeddings = self.encode_texts(sample_texts, show_progress=False)
        encoding_time = time.time() - start_time
        
        # Test query encoding
        query_start = time.time()
        query_embedding = self.encode_query("test query")
        query_time = time.time() - query_start
        
        # Test similarity calculation
        sim_start = time.time()
        similarities = self.calculate_similarity(query_embedding, embeddings)
        similarity_time = time.time() - sim_start
        
        return {
            "texts_processed": len(sample_texts),
            "encoding_time": encoding_time,
            "avg_encoding_time": encoding_time / len(sample_texts),
            "query_encoding_time": query_time,
            "similarity_calculation_time": similarity_time,
            "embedding_shape": embeddings.shape,
            "similarities_shape": similarities.shape,
            "memory_usage_mb": self._get_memory_usage()
        }
    
    def _get_memory_usage(self) -> float:
        """Get approximate memory usage in MB"""
        try:
            if torch.cuda.is_available() and self.device.startswith('cuda'):
                return torch.cuda.memory_allocated() / 1024 / 1024
            else:
                # Approximate CPU memory usage
                import psutil
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0