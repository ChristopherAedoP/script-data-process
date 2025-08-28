"""
Vector store module for RAG MVP
Handles FAISS index creation, storage, and retrieval
"""
import os
import pickle
import time
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path

import numpy as np
import faiss

from .config import config
from .document_processor import ChunkMetadata


class FAISSVectorStore:
    """FAISS-based vector store for document embeddings"""
    
    def __init__(self, embedding_dim: int):
        self.embedding_dim = embedding_dim
        self.index = None
        self.metadata = []
        self.is_trained = False
        
    def create_index(self, index_type: str = "IndexFlatL2") -> None:
        """Create FAISS index"""
        try:
            if index_type == "IndexFlatL2":
                # Exact search with L2 distance
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                print(f"Created IndexFlatL2 with dimension {self.embedding_dim}")
                
            elif index_type == "IndexFlatIP":
                # Exact search with inner product (cosine similarity)
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                print(f"Created IndexFlatIP with dimension {self.embedding_dim}")
                
            elif index_type.startswith("IndexIVFFlat"):
                # For larger datasets - approximate search
                nlist = 100  # number of clusters
                quantizer = faiss.IndexFlatL2(self.embedding_dim)
                self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, nlist)
                print(f"Created IndexIVFFlat with {nlist} clusters")
                
            else:
                raise ValueError(f"Unsupported index type: {index_type}")
                
            self.is_trained = getattr(self.index, 'is_trained', True)
            
        except Exception as e:
            print(f"Error creating index: {e}")
            raise
    
    def add_embeddings(
        self, 
        embeddings: np.ndarray, 
        metadata: List[ChunkMetadata]
    ) -> None:
        """Add embeddings to the index"""
        if self.index is None:
            raise ValueError("Index not created. Call create_index() first.")
        
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata items")
        
        try:
            print(f"Adding {len(embeddings)} embeddings to index...")
            start_time = time.time()
            
            # Ensure embeddings are float32 (FAISS requirement)
            embeddings = embeddings.astype(np.float32)
            
            # Train index if needed (for IVF indexes)
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                print("Training index...")
                self.index.train(embeddings)
                print("Index trained")
            
            # Add embeddings to index
            self.index.add(embeddings)
            
            # Store metadata
            self.metadata.extend(metadata)
            
            add_time = time.time() - start_time
            print(f"Added embeddings in {add_time:.2f}s")
            print(f"Index now contains {self.index.ntotal} vectors")
            
        except Exception as e:
            print(f"Error adding embeddings: {e}")
            raise
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        k: int = 5,
        return_metadata: bool = True
    ) -> Tuple[List[float], List[int], List[ChunkMetadata]]:
        """Search for similar embeddings"""
        if self.index is None:
            raise ValueError("Index not created or loaded")
        
        try:
            # Ensure query is float32 and correct shape
            query_embedding = query_embedding.astype(np.float32)
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Search
            start_time = time.time()
            distances, indices = self.index.search(query_embedding, k)
            search_time = time.time() - start_time
            
            # Convert to lists
            distances = distances[0].tolist()  # First query only
            indices = indices[0].tolist()    # First query only
            
            # Filter out invalid indices (-1)
            valid_results = [(d, i) for d, i in zip(distances, indices) if i != -1]
            distances = [d for d, i in valid_results]
            indices = [i for d, i in valid_results]
            
            # Get metadata if requested
            metadata_results = []
            if return_metadata:
                metadata_results = [self.metadata[i] for i in indices if i < len(self.metadata)]
            
            print(f"Search completed in {search_time*1000:.2f}ms")
            print(f"Found {len(valid_results)} results")
            
            return distances, indices, metadata_results
            
        except Exception as e:
            print(f"Error during search: {e}")
            raise
    
    def save_index(self, index_path: str, metadata_path: str) -> None:
        """Save FAISS index and metadata to disk"""
        if self.index is None:
            raise ValueError("No index to save")
        
        try:
            # Ensure directory exists
            Path(index_path).parent.mkdir(parents=True, exist_ok=True)
            Path(metadata_path).parent.mkdir(parents=True, exist_ok=True)
            
            print(f"Saving index to {index_path}...")
            start_time = time.time()
            
            # Save FAISS index
            faiss.write_index(self.index, index_path)
            
            # Save metadata
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            save_time = time.time() - start_time
            print(f"Index saved in {save_time:.2f}s")
            
        except Exception as e:
            print(f"Error saving index: {e}")
            raise
    
    def load_index(self, index_path: str, metadata_path: str) -> None:
        """Load FAISS index and metadata from disk"""
        try:
            print(f"Loading index from {index_path}...")
            start_time = time.time()
            
            # Load FAISS index
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"Index file not found: {index_path}")
            
            self.index = faiss.read_index(index_path)
            
            # Load metadata
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            else:
                print(f"Warning: Metadata file not found: {metadata_path}")
                self.metadata = []
            
            load_time = time.time() - start_time
            print(f"Index loaded in {load_time:.2f}s")
            print(f"Index contains {self.index.ntotal} vectors")
            print(f"Loaded {len(self.metadata)} metadata entries")
            
        except Exception as e:
            print(f"Error loading index: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if self.index is None:
            return {"status": "No index loaded"}
        
        stats = {
            "index_type": type(self.index).__name__,
            "dimension": self.embedding_dim,
            "total_vectors": self.index.ntotal,
            "metadata_count": len(self.metadata),
            "is_trained": getattr(self.index, 'is_trained', True),
            "memory_usage_mb": self._estimate_memory_usage()
        }
        
        # Add specific stats for different index types
        if hasattr(self.index, 'nlist'):
            stats["nlist"] = self.index.nlist
        if hasattr(self.index, 'nprobe'):
            stats["nprobe"] = self.index.nprobe
            
        return stats
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        if self.index is None:
            return 0.0
        
        # Basic estimation: vectors * dimension * 4 bytes (float32)
        vector_memory = self.index.ntotal * self.embedding_dim * 4
        
        # Add metadata memory (rough estimate)
        metadata_memory = len(self.metadata) * 1000  # ~1KB per metadata entry
        
        return (vector_memory + metadata_memory) / (1024 * 1024)
    
    def benchmark_search(self, query_embedding: np.ndarray, k_values: List[int] = None) -> Dict[str, Any]:
        """Benchmark search performance"""
        if k_values is None:
            k_values = [1, 5, 10, 20]
        
        results = {}
        
        for k in k_values:
            if k > self.index.ntotal:
                continue
                
            # Multiple search runs for average
            times = []
            for _ in range(5):  # 5 runs for averaging
                start_time = time.time()
                distances, indices, _ = self.search(query_embedding, k, return_metadata=False)
                times.append(time.time() - start_time)
            
            results[f"k={k}"] = {
                "avg_time_ms": np.mean(times) * 1000,
                "min_time_ms": min(times) * 1000,
                "max_time_ms": max(times) * 1000,
                "results_found": len([i for i in indices if i != -1])
            }
        
        return results