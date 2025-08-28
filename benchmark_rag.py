#!/usr/bin/env python3
"""
Benchmark script for RAG system performance testing
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag_system import RAGSystem
from src.config import config

def benchmark_rag_system():
    """Benchmark the RAG system performance"""
    print("=== RAG System Performance Benchmark ===")
    
    # Initialize RAG system
    rag = RAGSystem()
    
    # Load existing index
    index_path = config.INDEX_PATH + ".faiss"
    if os.path.exists(index_path):
        print("Loading system for benchmark...")
        rag._load_existing_index(index_path, config.METADATA_PATH)
        
        # Run built-in benchmarks
        print("\n=== Running Built-in Benchmarks ===")
        benchmark_results = rag.benchmark_system()
        
        print("\n--- Embedding Performance ---")
        emb_bench = benchmark_results['embedding_benchmark']
        print(f"Texts processed: {emb_bench['texts_processed']}")
        print(f"Encoding time: {emb_bench['encoding_time']:.3f}s")
        print(f"Avg time per text: {emb_bench['avg_encoding_time']*1000:.2f}ms")
        print(f"Query encoding: {emb_bench['query_encoding_time']*1000:.2f}ms")
        print(f"Similarity calc: {emb_bench['similarity_calculation_time']*1000:.2f}ms")
        print(f"Memory usage: {emb_bench['memory_usage_mb']:.2f}MB")
        
        print("\n--- Search Performance ---")
        search_bench = benchmark_results['search_benchmark']
        for k, stats in search_bench.items():
            print(f"{k}: avg={stats['avg_time_ms']:.2f}ms, min={stats['min_time_ms']:.2f}ms, max={stats['max_time_ms']:.2f}ms")
            
        print("\n--- End-to-End Performance ---")
        e2e_bench = benchmark_results['end_to_end']
        print(f"Queries tested: {e2e_bench['queries_tested']}")
        print(f"Average time: {e2e_bench['avg_time_ms']:.2f}ms")
        print(f"Min time: {e2e_bench['min_time_ms']:.2f}ms")
        print(f"Max time: {e2e_bench['max_time_ms']:.2f}ms")
        
        # Custom performance test
        print("\n=== Custom Performance Test ===")
        test_queries = [
            "inteligencia artificial",
            "transformación digital", 
            "política pública",
            "machine learning",
            "gobierno digital",
            "ciberseguridad",
            "innovación tecnológica",
            "datos abiertos"
        ]
        
        times = []
        for query in test_queries:
            start = time.time()
            results = rag.search(query, k=5, min_similarity_score=0.1)
            elapsed = time.time() - start
            times.append(elapsed * 1000)  # Convert to ms
            
        print(f"Custom benchmark results:")
        print(f"  Queries: {len(test_queries)}")
        print(f"  Avg time: {sum(times)/len(times):.2f}ms")
        print(f"  Min time: {min(times):.2f}ms")
        print(f"  Max time: {max(times):.2f}ms")
        print(f"  Throughput: {1000*len(test_queries)/sum(times):.1f} queries/sec")
        
        # Performance targets validation
        print("\n=== Performance Targets Validation ===")
        avg_search_time = sum(times) / len(times)
        targets = {
            "Search < 100ms": avg_search_time < 100,
            "Memory < 500MB": emb_bench['memory_usage_mb'] < 500,
            "Query encoding < 50ms": emb_bench['query_encoding_time'] * 1000 < 50
        }
        
        for target, passed in targets.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {target}: {status}")
            
    else:
        print("No index found. Please run indexing first.")
        return False
    
    print("\n=== Benchmark Completed ===")
    return True

if __name__ == "__main__":
    benchmark_rag_system()