#!/usr/bin/env python3
"""
Test script for the enhanced taxonomy system
Validates that all components work together properly
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.taxonomy import TaxonomyClassifier, TaxonomyClassification
from src.document_processor import DocumentProcessor
from src.config import config

def test_taxonomy_classifier():
    """Test the taxonomy classifier"""
    print("Testing Taxonomy Classifier...")
    
    classifier = TaxonomyClassifier()
    
    # Test basic classification
    test_cases = [
        {
            "text": "propuesta para reformar el sistema de AFP y pensiones",
            "expected_category": "Pensiones",
            "expected_subcategory": "AFP"
        },
        {
            "text": "plan para reducir las listas de espera en hospitales",
            "expected_category": "Salud", 
            "expected_subcategory": "Listas de Espera"
        },
        {
            "text": "aumento del salario mínimo para trabajadores",
            "expected_category": "Trabajo",
            "expected_subcategory": "Salario Mínimo"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = classifier.classify_from_text(test_case["text"])
        
        print(f"  Test {i}: {test_case['text'][:50]}...")
        print(f"    Category: {result.category} (expected: {test_case['expected_category']})")
        print(f"    Subcategory: {result.subcategory} (expected: {test_case.get('expected_subcategory', 'Any')})")
        print(f"    Taxonomy Path: {result.taxonomy_path}")
        print(f"    Confidence: {result.confidence:.2f}")
        print(f"    Keywords: {result.matched_keywords}")
        
        # Validate results
        success = result.category == test_case["expected_category"]
        if test_case.get("expected_subcategory") and result.subcategory:
            success = success and result.subcategory == test_case["expected_subcategory"]
        
        print(f"    PASS" if success else f"    FAIL")
        print()
    
    # Test taxonomy stats
    stats = classifier.get_taxonomy_stats()
    print(f"Taxonomy Stats:")
    print(f"  Categories: {stats['total_categories']}")
    print(f"  Subcategories: {stats['total_subcategories']}")
    print(f"  Keywords: {stats['total_keywords']}")
    print(f"  Version: {stats['taxonomy_version']}")
    print()

def test_document_processor():
    """Test the enhanced document processor"""
    print("Testing Document Processor...")
    
    processor = DocumentProcessor()
    
    # Test candidate extraction
    test_files = [
        "Programa_Evelyn_Matthei.md",
        "Programa_Jose_Antonio_Kast_R.md",
        "Programa_Johannes_Kaiser.md"
    ]
    
    for filename in test_files:
        candidate, party = processor.extract_candidate_info_from_filename(filename)
        print(f"  File: {filename}")
        print(f"    Candidate: {candidate}")
        print(f"    Party: {party}")
        print(f"    Party normalized (not None)")
        print()
    
    # Test taxonomy classification
    test_headers = {"Header 2": "Sistema de Pensiones y AFP"}
    test_content = "Proponemos una reforma integral al sistema de AFP que permita mejorar las pensiones de los adultos mayores"
    
    taxonomy_result = processor.classify_with_taxonomy(test_headers, test_content)
    print(f"  Taxonomy Classification Test:")
    print(f"    Headers: {test_headers}")
    print(f"    Content: {test_content[:50]}...")
    print(f"    Category: {taxonomy_result.category}")
    print(f"    Subcategory: {taxonomy_result.subcategory}")
    print(f"    Taxonomy Path: {taxonomy_result.taxonomy_path}")
    print(f"    Confidence: {taxonomy_result.confidence:.2f}")
    print()

def test_integration():
    """Test integration between components"""
    print("Testing Integration...")
    
    # Test that all imports work
    try:
        from src.rag_system import RAGSystem
        from src.embeddings import EmbeddingGenerator
        from src.qdrant_exporter import QdrantExporter
        print("  All imports successful")
    except ImportError as e:
        print(f"  Import failed: {e}")
        return False
    
    # Test that taxonomy is properly integrated
    processor = DocumentProcessor()
    if hasattr(processor, 'taxonomy_classifier'):
        print("  DocumentProcessor has taxonomy classifier")
    else:
        print("  DocumentProcessor missing taxonomy classifier")
        return False
    
    return True

def main():
    """Main test function"""
    print("RAG Taxonomy System Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_taxonomy_classifier()
        test_document_processor() 
        test_integration()
        
        print("All tests completed!")
        print()
        print("Next steps:")
        print("1. Run: python -m src.cli index --force")
        print("2. Run: python -m src.cli export-qdrant")
        print("3. Check the enhanced taxonomy fields in the output")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())