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
    
    # Text processing
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "64"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "32"))
    
    # Search configuration
    MAX_CHUNKS_RETURN: int = int(os.getenv("MAX_CHUNKS_RETURN", "5"))
    
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

# Global config instance
config = Config()