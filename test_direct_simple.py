#!/usr/bin/env python3
"""
Simple test of DirectProcessor without API dependencies
"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_document_discovery():
    """Test document discovery and basic document loading"""
    print("=== Testing Document Discovery ===")
    
    from src.direct_processor import DirectProcessor
    from langchain_community.document_loaders import TextLoader
    
    docs_path = Path("./docs")
    if not docs_path.exists():
        print("ERROR: Docs directory not found")
        return False
        
    # Find .md files
    md_files = list(docs_path.glob("**/*.md"))
    print(f"Found {len(md_files)} .md files")
    
    if not md_files:
        print("No .md files found")
        return False
        
    # Test loading the first document
    test_file = md_files[0]
    print(f"Testing document: {test_file.name}")
    
    try:
        loader = TextLoader(str(test_file), encoding='utf-8')
        documents = loader.load()
        
        if documents:
            document = documents[0]
            print(f"OK: Document loaded successfully")
            print(f"   Content length: {len(document.page_content)} characters")
            print(f"   Has page markers: {'[START OF PAGE:' in document.page_content}")
            return True
        else:
            print("ERROR: No content found in document")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to load document: {e}")
        return False

def test_document_processor():
    """Test document processor without embeddings"""
    print("\n=== Testing Document Processor ===")
    
    try:
        from src.document_processor import DocumentProcessor
        from langchain_community.document_loaders import TextLoader
        
        processor = DocumentProcessor()
        
        # Load a test document
        test_file = Path("./docs/Programa_Jose_Antonio_Kast.md")
        if not test_file.exists():
            print("ERROR: Test document not found")
            return False
            
        loader = TextLoader(str(test_file), encoding='utf-8')
        documents = loader.load()
        document = documents[0]
        
        # Process document into chunks
        chunks = processor.process_markdown_document(document)
        print(f"OK: Generated {len(chunks)} chunks")
        
        if chunks:
            # Test metadata creation
            metadata = processor.create_chunk_metadata(chunks[0], 0, len(chunks))
            print(f"OK: Metadata created for candidate: {metadata.candidate}")
            print(f"   Topic category: {metadata.topic_category}")
            print(f"   Chunk ID: {metadata.chunk_id}")
            return True
        else:
            print("ERROR: No chunks generated")
            return False
            
    except Exception as e:
        print(f"ERROR: Document processing failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing DirectProcessor without API dependencies\n")
    
    success = True
    success &= test_document_discovery()
    success &= test_document_processor()
    
    if success:
        print("\nSUCCESS: All tests passed! DirectProcessor basic functionality is working.")
        print("\nTo test with real Qdrant Cloud:")
        print("   1. Set environment variables:")
        print("      export OPENAI_API_KEY=your_openai_api_key")
        print("      export QDRANT_API_KEY=your_qdrant_api_key") 
        print("      export QDRANT_URL=https://your-cluster.qdrant.tech")
        print("   2. Run: python -m src.cli process-direct")
    else:
        print("\nERROR: Some tests failed")
        sys.exit(1)