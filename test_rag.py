#!/usr/bin/env python3
"""
Simple test script for RAG system without Rich UI components
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag_system import RAGSystem
from src.config import config

def test_rag_system():
    """Test the RAG system end-to-end"""
    print("=== RAG System Test ===")
    
    # Initialize RAG system
    rag = RAGSystem()
    
    # Load existing index
    index_path = config.INDEX_PATH + ".faiss"
    if os.path.exists(index_path):
        print("Loading existing index...")
        rag._load_existing_index(index_path, config.METADATA_PATH)
        
        # Test search queries
        test_queries = [
            "inteligencia artificial",
            "transformación digital", 
            "política pública",
            "machine learning",
            "gobierno digital"
        ]
        
        print("\n=== Testing Search Queries ===")
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = rag.search(query, k=3, min_similarity_score=0.1)
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['source_file']} (score: {result['similarity_score']:.3f})")
                print(f"     Chunk: {result['chunk_id']}")
                if result['headers']:
                    headers = " > ".join(result['headers'].values())
                    print(f"     Headers: {headers}")
                    
        # Get system stats
        print("\n=== System Statistics ===")
        stats = rag.get_system_stats()
        print(f"Indexed: {stats['is_indexed']}")
        if stats.get('model_info'):
            model = stats['model_info']
            print(f"Model: {model['model_name']}")
            print(f"Dimensions: {model['embedding_dimension']}")
            print(f"Device: {model['device']}")
        if stats.get('vector_store'):
            vs = stats['vector_store']
            print(f"Index type: {vs['index_type']}")
            print(f"Vectors: {vs['total_vectors']}")
            print(f"Memory: {vs['memory_usage_mb']:.2f} MB")
            
    else:
        print("No index found. Please run indexing first.")
        return False
    
    print("\n=== Test Completed Successfully ===")
    return True

if __name__ == "__main__":
    test_rag_system()