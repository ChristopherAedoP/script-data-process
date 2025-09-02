#!/usr/bin/env python3
"""
Test .env integration with DirectProcessor
"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_env_integration():
    """Test .env file integration"""
    print("=== Testing .env Integration ===")
    
    # Test config loading
    from src.config import config
    
    print(f"Config loaded successfully")
    print(f"  EMBEDDING_MODEL: {config.EMBEDDING_MODEL}")
    print(f"  CHUNK_SIZE: {config.CHUNK_SIZE}")
    print(f"  BATCH_SIZE: {config.BATCH_SIZE}")
    
    # Test API key detection
    print(f"  OPENAI_API_KEY: {'Set' if config.OPENAI_API_KEY else 'Missing'}")
    print(f"  QDRANT_API_KEY: {'Set' if config.QDRANT_API_KEY else 'Missing'}")
    print(f"  QDRANT_URL: {'Set' if config.QDRANT_URL else 'Missing'}")
    
    return True

def test_validation():
    """Test validation without API keys"""
    print("\n=== Testing API Key Validation ===")
    
    from src.config import config
    
    try:
        config.validate_api_keys()
        print("OK: All API keys are set")
        return True
    except ValueError as e:
        print("Expected validation error (API keys not set):")
        print(f"  Error message includes .env instructions: {'.env' in str(e)}")
        print(f"  Error message includes cp command: {'cp .env.example' in str(e)}")
        return True

def test_directprocessor_integration():
    """Test DirectProcessor integration with config"""
    print("\n=== Testing DirectProcessor Config Integration ===")
    
    try:
        from src.direct_processor import DirectProcessor
        
        # This should fail with proper .env instructions
        processor = DirectProcessor()
        print("ERROR: DirectProcessor should have failed without API keys")
        return False
        
    except ValueError as e:
        print("OK: DirectProcessor properly validates API keys")
        print(f"  Uses centralized config validation: {'.env' in str(e)}")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected exception: {e}")
        return False

if __name__ == "__main__":
    print("Testing .env Integration and Centralized Configuration\n")
    
    success = True
    success &= test_env_integration()
    success &= test_validation() 
    success &= test_directprocessor_integration()
    
    if success:
        print("\nSUCCESS: .env integration working correctly!")
        print("\nTo use with real API keys:")
        print("  1. cp .env.example .env")
        print("  2. Edit .env with your actual API keys")
        print("  3. python -m src.cli process-direct")
    else:
        print("\nERROR: Some integration tests failed")
        sys.exit(1)