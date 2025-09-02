"""
Qdrant Exporter for RAG System
Exports processed chunks and embeddings in Qdrant-compatible format
"""
import json
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

import numpy as np

from .document_processor import ChunkMetadata


class QdrantExporter:
    """Export RAG data to Qdrant-compatible format"""
    
    def __init__(self):
        pass
    
    def _generate_content_preview(self, content: str, max_words: int = 20) -> str:
        """Generate clean content preview without cutting words"""
        words = content.strip().split()
        if len(words) <= max_words:
            return content.strip()
        
        # Take only complete words
        preview_words = words[:max_words]
        preview = " ".join(preview_words)
        
        # Add ellipsis if truncated
        if len(words) > max_words:
            preview += "..."
        
        return preview
    
    def create_qdrant_point(
        self, 
        chunk_text: str, 
        embedding: np.ndarray, 
        metadata: ChunkMetadata,
        point_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a Qdrant point from chunk data"""
        
        if point_id is None:
            point_id = str(uuid.uuid4())
        
        # Convert numpy array to list for JSON serialization
        vector = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        
        # Build optimized payload for web RAG queries
        payload = {
            # Core metadata
            "source_file": metadata.source_file,
            "chunk_id": metadata.chunk_id,
            "chunk_index": metadata.chunk_index,
            
            # Political metadata - critical for PDR filtering
            "candidate": metadata.candidate,
            "party": metadata.party or "Independiente",  # Ensure no null parties
            "page_number": metadata.page_number,
            "topic_category": metadata.topic_category,
            "proposal_type": metadata.proposal_type,
            
            # Enhanced taxonomy fields - critical for PDR queries
            "sub_category": metadata.sub_category,
            "taxonomy_path": metadata.taxonomy_path,
            "tags": metadata.tags or [],
            
            # Content for retrieval
            "content": chunk_text,
            
            # Content preview for display (generated here for Qdrant only)
            "content_preview": self._generate_content_preview(chunk_text),
            
            # Additional searchable fields
            "has_page_number": metadata.page_number is not None,
            
            # Embedding metadata - optimized
            "embedding_metadata": metadata.embedding_metadata or {
                "language": "es",
                "model": "text-embedding-3-small",
                "dimensions": 1536,
                "generated_date": __import__('datetime').date.today().strftime("%Y-%m-%d")
            }
        }
        
        # Add conditional fields only if they exist and are not empty
        if metadata.headers:
            payload["headers"] = metadata.headers
        if metadata.section_hierarchy:
            payload["section_hierarchy"] = metadata.section_hierarchy
            payload["section_depth"] = len(metadata.section_hierarchy)
        
        # Remove None values to keep payload clean
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return {
            "id": point_id,
            "vector": vector,
            "payload": payload
        }
    
    def export_to_qdrant_json(
        self, 
        texts: List[str], 
        embeddings: np.ndarray, 
        metadata: List[ChunkMetadata],
        output_path: str,
        collection_name: str = "political_documents"
    ) -> Dict[str, Any]:
        """Export all data to Qdrant JSON format"""
        
        if len(texts) != len(embeddings) != len(metadata):
            raise ValueError("Texts, embeddings, and metadata must have the same length")
        
        points = []
        stats = {
            "total_points": len(texts),
            "candidates": set(),
            "parties": set(),
            "topics": set(),
            "subcategories": set(),
            "taxonomy_paths": set(),
            "proposal_types": set(),
            "pages_with_content": set(),
            "dimensions": len(embeddings[0]) if len(embeddings) > 0 else 0,
            "export_date": __import__('datetime').date.today().strftime("%Y-%m-%d")
        }
        
        # Create points
        for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
            point = self.create_qdrant_point(text, embedding, meta)
            points.append(point)
            
            # Collect stats including taxonomy fields
            if meta.candidate:
                stats["candidates"].add(meta.candidate)
            if meta.party:
                stats["parties"].add(meta.party)
            if meta.topic_category:
                stats["topics"].add(meta.topic_category)
            if meta.sub_category:
                stats["subcategories"].add(meta.sub_category)
            if meta.taxonomy_path:
                stats["taxonomy_paths"].add(meta.taxonomy_path)
            if meta.proposal_type:
                stats["proposal_types"].add(meta.proposal_type)
            if meta.page_number:
                stats["pages_with_content"].add(f"{meta.source_file}:p{meta.page_number}")
        
        # Convert sets to lists for JSON serialization
        for key in ["candidates", "parties", "topics", "subcategories", "taxonomy_paths", "proposal_types", "pages_with_content"]:
            stats[key] = list(stats[key])
        
        # Create Qdrant collection config
        qdrant_data = {
            "collection_name": collection_name,
            "vector_config": {
                "size": stats["dimensions"],
                "distance": "Cosine"  # Using cosine distance for semantic similarity
            },
            "points": points,
            "stats": stats
        }
        
        # Save to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(qdrant_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(points)} points to {output_path}")
        print(f"Collection: {collection_name}")
        print(f"Vector dimension: {stats['dimensions']}")
        print(f"Candidates: {len(stats['candidates'])}")
        print(f"Topics: {len(stats['topics'])}")
        
        return qdrant_data
    
    
