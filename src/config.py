"""
Configuration management for RAG MVP
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for RAG MVP"""
    
    # Model configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    DEVICE: str = os.getenv("DEVICE", "cpu")
    
    # Text processing - optimized for political documents
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))  # Increased from 512 to reduce fragmentation
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))  # Increased from 64 for better context
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "32"))
    
    # Search configuration
    MAX_CHUNKS_RETURN: int = int(os.getenv("MAX_CHUNKS_RETURN", "5"))
    
    # API Keys for cloud services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY") 
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DOCUMENTS_PATH: str = os.getenv("DOCUMENTS_PATH", str(BASE_DIR / "docs"))
    INDEX_PATH: str = os.getenv("INDEX_PATH", str(BASE_DIR / "data" / "faiss_index"))
    METADATA_PATH: str = os.getenv("METADATA_PATH", str(BASE_DIR / "data" / "metadata.json"))
    
    # Markdown processing headers
    MARKDOWN_HEADERS = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist"""
        Path(cls.DOCUMENTS_PATH).mkdir(parents=True, exist_ok=True)
        Path(cls.INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(cls.METADATA_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod 
    def get_model_cache_dir(cls) -> str:
        """Get model cache directory"""
        return str(cls.BASE_DIR / "models")
    
    @classmethod
    def validate_api_keys(cls) -> None:
        """Validate required API keys for DirectProcessor"""
        missing_keys = []
        
        if not cls.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        if not cls.QDRANT_API_KEY:
            missing_keys.append("QDRANT_API_KEY") 
        if not cls.QDRANT_URL:
            missing_keys.append("QDRANT_URL")
            
        if missing_keys:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_keys)}\n\n"
                "Setup instructions:\n"
                "1. Copy .env.example to .env: cp .env.example .env\n"
                "2. Edit .env file with your API keys:\n"
                f"   {'OPENAI_API_KEY=your_openai_api_key' if 'OPENAI_API_KEY' in missing_keys else ''}\n"
                f"   {'QDRANT_API_KEY=your_qdrant_api_key' if 'QDRANT_API_KEY' in missing_keys else ''}\n"
                f"   {'QDRANT_URL=https://your-cluster-url.qdrant.tech' if 'QDRANT_URL' in missing_keys else ''}\n"
                "3. Run the command again\n\n"
                "Alternatively, set environment variables manually:\n"
                f"   {'export OPENAI_API_KEY=your_key' if 'OPENAI_API_KEY' in missing_keys else ''}\n"
                f"   {'export QDRANT_API_KEY=your_key' if 'QDRANT_API_KEY' in missing_keys else ''}\n"
                f"   {'export QDRANT_URL=your_url' if 'QDRANT_URL' in missing_keys else ''}"
            )
    
    @classmethod
    def get_api_credentials(cls) -> dict:
        """Get validated API credentials"""
        cls.validate_api_keys()
        return {
            "openai_api_key": cls.OPENAI_API_KEY,
            "qdrant_api_key": cls.QDRANT_API_KEY,
            "qdrant_url": cls.QDRANT_URL
        }

# Global config instance
config = Config()