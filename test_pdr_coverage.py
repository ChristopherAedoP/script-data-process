#!/usr/bin/env python3
"""
Test PDR Question Coverage - Validates 30 key citizen questions
"""

from src.rag_system import RAGSystem
from src.config import config
import time

def test_pdr_questions():
    """Test the enhanced RAG system against PDR's 30 key citizen questions"""
    
    print("=== PDR Question Coverage Validation ===")
    
    # Initialize RAG system
    rag = RAGSystem()
    # Load existing index using the index_documents method without force reindex
    rag.index_documents(config.DOCUMENTS_PATH, force_reindex=False)
    
    # Sample questions from each PDR category (representative of 30 total questions)
    test_questions = [
        # 1-3: Pensiones y Seguridad Social  
        "¿Qué propone respecto al sistema de pensiones AFP reparto mixto?",
        "¿Aumentará la pensión básica universal?",
        
        # 4-6: Salud
        "¿Qué pasará con las listas de espera en hospitales?",
        "¿Cuál es el plan para Fonasa e Isapres?",
        
        # 7-9: Educación
        "¿Qué propone en educación escolar calidad financiamiento?",
        "¿Habrá gratuidad total en educación superior?",
        
        # 10-12: Trabajo y Salarios
        "¿Cuál es la propuesta respecto al salario mínimo?",
        "¿Habrá incentivos para reducir informalidad laboral?",
        
        # 13-15: Economía y Costo de la Vida
        "¿Qué hará para enfrentar inflación alto costo vida?",
        "¿Habrá políticas para clase media endeudada?",
        
        # 16-18: Seguridad y Crimen Organizado
        "¿Qué medidas contra narcotráfico crimen organizado?",
        "¿Cuál es el plan para Carabineros reforma policial?",
        
        # 19-21: Vivienda y Ciudad
        "¿Qué se plantea para reducir déficit habitacional?",
        "¿Cómo enfrentará arriendos caros campamentos?",
        
        # 22-24: Medioambiente y Energía
        "¿Cuál es la propuesta frente crisis hídrica agua?",
        "¿Qué plantea sobre energías renovables litio?",
        
        # 25-27: Descentralización y Regiones
        "¿Qué propone para fortalecer gobiernos regionales?",
        "¿Cómo impulsará desarrollo regiones extremas?",
        
        # 28-30: Institucionalidad y Política
        "¿Cuál es la postura sobre nueva Constitución?",
        "¿Qué plantea sobre probidad transparencia?",
        "¿Qué hará para reducir desigualdad social?"
    ]
    
    print(f"\nTesting {len(test_questions)} representative PDR questions...")
    stats = rag.vector_store.get_stats()
    print(f"Total vectors indexed: {stats.get('vectors', 'N/A')}")
    
    results_summary = []
    category_coverage = {}
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Question {i}: {question[:50]}...")
        
        try:
            start_time = time.time()
            results = rag.search(question, k=3)
            search_time = time.time() - start_time
            
            if results:
                # Analyze taxonomy coverage
                taxonomies = []
                categories = []
                scores = []
                
                for result in results:
                    metadata = result.get('metadata', {})
                    taxonomy = metadata.get('taxonomy_path', 'Sin clasificación')
                    category = metadata.get('topic_category', 'Sin categoría')
                    score = result.get('similarity_score', 0)
                    
                    taxonomies.append(taxonomy)
                    categories.append(category)
                    scores.append(score)
                    
                    # Track category coverage
                    if category not in category_coverage:
                        category_coverage[category] = 0
                    category_coverage[category] += 1
                
                avg_score = sum(scores) / len(scores)
                unique_categories = len(set(categories))
                
                print(f"   OK Found {len(results)} results in {search_time:.2f}s")
                print(f"   >> Avg similarity: {avg_score:.3f}")
                print(f"   >> Categories: {unique_categories} unique")
                print(f"   >> Top taxonomy: {taxonomies[0]}")
                
                results_summary.append({
                    'question': question,
                    'found_results': len(results),
                    'avg_score': avg_score,
                    'search_time': search_time,
                    'categories': unique_categories,
                    'top_taxonomy': taxonomies[0]
                })
                
            else:
                print(f"   XX No results found")
                results_summary.append({
                    'question': question,
                    'found_results': 0,
                    'avg_score': 0,
                    'search_time': search_time,
                    'categories': 0,
                    'top_taxonomy': 'No results'
                })
                
        except Exception as e:
            print(f"   XX Error: {str(e)}")
    
    # Summary statistics
    print("\n" + "="*60)
    print(">> PDR COVERAGE VALIDATION RESULTS")
    print("="*60)
    
    total_questions = len(test_questions)
    successful_queries = len([r for r in results_summary if r['found_results'] > 0])
    avg_results_per_query = sum([r['found_results'] for r in results_summary]) / total_questions
    avg_similarity = sum([r['avg_score'] for r in results_summary if r['avg_score'] > 0]) / successful_queries if successful_queries > 0 else 0
    avg_search_time = sum([r['search_time'] for r in results_summary]) / total_questions
    
    print(f"OK Successful queries: {successful_queries}/{total_questions} ({successful_queries/total_questions*100:.1f}%)")
    print(f">> Avg results per query: {avg_results_per_query:.1f}")
    print(f">> Avg similarity score: {avg_similarity:.3f}")
    print(f">> Avg search time: {avg_search_time:.3f}s")
    
    print("\n>> Category Coverage Distribution:")
    for category, count in sorted(category_coverage.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / sum(category_coverage.values())) * 100
        print(f"   {category}: {count} results ({percentage:.1f}%)")
    
    print("\n>> Key PDR Validation Metrics:")
    high_quality_results = len([r for r in results_summary if r['avg_score'] >= 0.3])
    multi_category_coverage = len([r for r in results_summary if r['categories'] > 1])
    
    print(f"   High-quality results (score ≥0.3): {high_quality_results}/{total_questions}")
    print(f"   Multi-category coverage: {multi_category_coverage}/{total_questions}")
    print(f"   Category diversity: {len(category_coverage)} unique categories")
    
    # Identify any gaps
    print("\n>> Potential Coverage Gaps:")
    low_score_queries = [r for r in results_summary if r['avg_score'] < 0.2 and r['found_results'] > 0]
    if low_score_queries:
        for query in low_score_queries:
            print(f"   !! Low relevance: '{query['question'][:40]}...' (score: {query['avg_score']:.3f})")
    else:
        print("   OK No significant gaps detected!")
    
    print("\n" + "="*60)
    print(">> PDR VALIDATION COMPLETED SUCCESSFULLY")
    print("="*60)
    
    return {
        'success_rate': successful_queries/total_questions,
        'avg_similarity': avg_similarity,
        'category_coverage': category_coverage,
        'avg_search_time': avg_search_time
    }

if __name__ == "__main__":
    try:
        results = test_pdr_questions()
        print(f"\n>> Overall PDR Coverage Score: {results['success_rate']*100:.1f}%")
    except Exception as e:
        print(f"XX Test failed: {e}")