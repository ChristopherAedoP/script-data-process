"""
RAG System - Main orchestrator for the RAG MVP
Combines document processing, embeddings, and vector search
"""
import json
import time
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import numpy as np

from .config import config
from .document_processor import DocumentProcessor, ChunkMetadata
from .embeddings import EmbeddingGenerator
from .vector_store import FAISSVectorStore


class RAGSystem:
    """Main RAG system orchestrator"""
    
    def __init__(self, embedding_model: Optional[str] = None):
        self.document_processor = DocumentProcessor()
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.vector_store = None
        self.is_indexed = False
        self.original_texts = []  # Store original chunk texts for content retrieval
        
    def index_documents(
        self, 
        documents_path: str, 
        force_reindex: bool = False,
        index_type: str = "IndexFlatIP"  # Use inner product for cosine similarity
    ) -> Dict[str, Any]:
        """Index documents from the specified path"""
        
        index_path = config.INDEX_PATH + ".faiss"
        metadata_path = config.METADATA_PATH
        
        # Check if index already exists
        if not force_reindex and Path(index_path).exists():
            try:
                self._load_existing_index(index_path, metadata_path)
                return {"status": "loaded_existing", "message": "Loaded existing index"}
            except Exception as e:
                print(f"Warning: Failed to load existing index: {e}")
                print("Creating new index...")
        
        # Process documents
        print("Starting document indexing process...")
        start_time = time.time()
        
        texts, metadata = self.document_processor.process_documents(documents_path)
        
        if not texts:
            return {"status": "error", "message": "No documents found to index"}
        
        # Store original texts for content retrieval
        self.original_texts = texts.copy()
        
        # Generate embeddings
        embeddings = self.embedding_generator.encode_texts(texts)
        
        # Create vector store
        embedding_dim = self.embedding_generator.embedding_dim
        self.vector_store = FAISSVectorStore(embedding_dim)
        self.vector_store.create_index(index_type)
        
        # Add embeddings to index
        self.vector_store.add_embeddings(embeddings, metadata)
        
        # Save index and metadata
        self.vector_store.save_index(index_path, index_path.replace('.faiss', '_metadata.pkl'))
        self.document_processor.save_metadata(metadata, metadata_path)
        
        # Save original texts for content retrieval
        texts_path = metadata_path.replace('metadata.json', 'original_texts.json')
        with open(texts_path, 'w', encoding='utf-8') as f:
            json.dump(self.original_texts, f, ensure_ascii=False, indent=2)
        
        total_time = time.time() - start_time
        self.is_indexed = True
        
        stats = {
            "status": "success",
            "documents_processed": len(set(meta.source_file for meta in metadata)),
            "chunks_created": len(texts),
            "embeddings_generated": len(embeddings),
            "dimensions": embedding_dim,
            "index_type": index_type,
            "total_time_seconds": round(total_time, 2),
            "avg_time_per_chunk_ms": round((total_time / len(texts)) * 1000, 2)
        }
        
        print(f"Indexing completed in {total_time:.2f}s")
        print(f"Stats: {stats['chunks_created']} chunks from {stats['documents_processed']} documents")
        
        return stats
    
    def _load_existing_index(self, index_path: str, metadata_path: str) -> None:
        """Load existing index and metadata"""
        # Get embedding dimension directly
        embedding_dim = self.embedding_generator.embedding_dim
        
        # Create vector store and load index
        self.vector_store = FAISSVectorStore(embedding_dim)
        self.vector_store.load_index(index_path, index_path.replace('.faiss', '_metadata.pkl'))
        
        # Load original texts if available
        texts_path = metadata_path.replace('metadata.json', 'original_texts.json')
        if Path(texts_path).exists():
            with open(texts_path, 'r', encoding='utf-8') as f:
                self.original_texts = json.load(f)
            print(f"Loaded {len(self.original_texts)} original texts")
        else:
            self.original_texts = []
            print("Warning: Original texts not found - content retrieval will be limited")
        
        self.is_indexed = True
        print("Loaded existing index successfully")
    
    def search(
        self, 
        query: str, 
        k: Optional[int] = None, 
        min_similarity_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        
        if not self.is_indexed or self.vector_store is None:
            raise ValueError("System not indexed. Call index_documents() first.")
        
        k = k or config.MAX_CHUNKS_RETURN
        
        try:
            print(f"Searching for: '{query}'")
            start_time = time.time()
            
            # Generate query embedding
            query_embedding = self.embedding_generator.encode_query(query)
            
            # Search in vector store
            distances, indices, metadata_results = self.vector_store.search(
                query_embedding, 
                k=k, 
                return_metadata=True
            )
            
            search_time = time.time() - start_time
            
            # Format results
            results = []
            for i, (distance, idx, metadata) in enumerate(zip(distances, indices, metadata_results)):
                # Convert distance to similarity score (for inner product/cosine similarity)
                # Note: For IndexFlatIP, distance is actually the inner product
                similarity_score = float(distance)  
                
                if similarity_score >= min_similarity_score:
                    result = {
                        "rank": i + 1,
                        "similarity_score": similarity_score,
                        "chunk_id": metadata.chunk_id,
                        "source_file": Path(metadata.source_file).name,
                        "headers": metadata.headers,
                        "char_count": metadata.char_count,
                        "chunk_index": metadata.chunk_index,
                        # We'll add the actual text content in the full search
                    }
                    results.append(result)
            
            print(f"Search completed in {search_time*1000:.2f}ms")
            print(f"Found {len(results)} relevant results")
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            raise
    
    def search_with_content(
        self, 
        query: str, 
        k: Optional[int] = None,
        min_similarity_score: float = 0.0,
        max_content_length: int = 500
    ) -> List[Dict[str, Any]]:
        """Search and include content in results"""
        
        # Get search results
        results = self.search(query, k, min_similarity_score)
        
        # Add real content to results
        for result in results:
            chunk_index = result['chunk_index']
            if 0 <= chunk_index < len(self.original_texts):
                full_content = self.original_texts[chunk_index]
                # Truncate if too long
                if len(full_content) > max_content_length:
                    result["content_preview"] = full_content[:max_content_length] + "..."
                    result["content"] = full_content  # Include full content
                else:
                    result["content_preview"] = full_content
                    result["content"] = full_content
            else:
                result["content_preview"] = f"[Content not available for chunk {chunk_index}]"
                result["content"] = ""
        
        return results
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {
            "is_indexed": self.is_indexed,
            "model_info": self.embedding_generator.get_model_info(),
        }
        
        if self.vector_store:
            stats["vector_store"] = self.vector_store.get_stats()
        
        return stats
    
    def benchmark_system(self, test_queries: Optional[List[str]] = None) -> Dict[str, Any]:
        """Benchmark system performance"""
        if not self.is_indexed:
            return {"error": "System not indexed"}
        
        if test_queries is None:
            test_queries = [
                "What is machine learning?",
                "How does artificial intelligence work?",
                "Explain neural networks",
                "What are the benefits of automation?"
            ]
        
        print("Running system benchmark...")
        
        # Benchmark embeddings
        embedding_benchmark = self.embedding_generator.benchmark_model(test_queries)
        
        # Benchmark search
        query_embedding = self.embedding_generator.encode_query(test_queries[0])
        search_benchmark = self.vector_store.benchmark_search(query_embedding)
        
        # End-to-end benchmark
        e2e_times = []
        for query in test_queries:
            start_time = time.time()
            results = self.search(query, k=5)
            e2e_times.append(time.time() - start_time)
        
        return {
            "embedding_benchmark": embedding_benchmark,
            "search_benchmark": search_benchmark,
            "end_to_end": {
                "queries_tested": len(test_queries),
                "avg_time_ms": np.mean(e2e_times) * 1000,
                "min_time_ms": min(e2e_times) * 1000,
                "max_time_ms": max(e2e_times) * 1000,
            },
            "system_stats": self.get_system_stats()
        }
    
    def export_to_qdrant(
        self, 
        output_dir: str = "./data/qdrant_export",
        collection_name: str = "political_documents"
    ) -> Dict[str, Any]:
        """Export processed data to Qdrant format"""
        from .qdrant_exporter import QdrantExporter
        
        if not self.is_indexed or self.vector_store is None:
            raise ValueError("System not indexed. Call index_documents() first.")
        
        try:
            # Get embeddings and metadata
            print("Preparing data for Qdrant export...")
            
            # We need to reconstruct texts from the original processing
            # For now, we'll get the stored metadata
            metadata = self.document_processor.load_metadata(config.METADATA_PATH)
            if not metadata:
                raise ValueError("No metadata found. Please reindex documents.")
            
            # Get all embeddings from vector store
            total_vectors = self.vector_store.index.ntotal
            if total_vectors == 0:
                raise ValueError("No vectors in index")
            
            # Get all vectors (this is a simplification - in production you'd want batch processing)
            all_embeddings = []
            for i in range(total_vectors):
                vector = self.vector_store.index.reconstruct(i)
                all_embeddings.append(vector)
            
            all_embeddings = np.array(all_embeddings)
            
            # Use stored original texts or load from file
            if not self.original_texts:
                texts_path = config.METADATA_PATH.replace('metadata.json', 'original_texts.json')
                if Path(texts_path).exists():
                    with open(texts_path, 'r', encoding='utf-8') as f:
                        self.original_texts = json.load(f)
                    print(f"Loaded {len(self.original_texts)} original texts for export")
                else:
                    raise ValueError("Original texts not found. Please reindex documents with the updated system.")
            
            # Use real content and metadata
            texts = self.original_texts[:len(all_embeddings)]  # Ensure same length
            processed_metadata = metadata[:len(all_embeddings)]
            
            # Create exporter and export
            exporter = QdrantExporter()
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Export to JSON only
            json_path = output_path / f"{collection_name}.json"
            qdrant_data = exporter.export_to_qdrant_json(
                texts, all_embeddings, processed_metadata, 
                str(json_path), collection_name
            )
            
            print(f"Qdrant export completed:")
            print(f"  Data: {json_path}")
            print(f"  Use CLI command: python -m src.cli upload-cloud")
            
            return {
                "status": "success",
                "collection_name": collection_name,
                "total_points": len(texts),
                "output_files": {
                    "data": str(json_path)
                },
                "stats": qdrant_data["stats"]
            }
            
        except Exception as e:
            print(f"Export failed: {e}")
            raise