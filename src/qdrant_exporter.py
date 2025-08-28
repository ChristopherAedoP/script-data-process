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
        
        # Build payload with all metadata
        payload = {
            # Original metadata
            "source_file": metadata.source_file,
            "chunk_id": metadata.chunk_id,
            "chunk_index": metadata.chunk_index,
            "headers": metadata.headers,
            "char_count": metadata.char_count,
            
            # Political metadata
            "candidate": metadata.candidate,
            "party": metadata.party,
            "page_number": metadata.page_number,
            "topic_category": metadata.topic_category,
            "proposal_type": metadata.proposal_type,
            "section_hierarchy": metadata.section_hierarchy,
            
            # Content for retrieval
            "content": chunk_text,
            
            # Additional searchable fields
            "content_preview": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
            "has_page_number": metadata.page_number is not None,
            "section_depth": len(metadata.section_hierarchy) if metadata.section_hierarchy else 0,
        }
        
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
            "proposal_types": set(),
            "pages_with_content": set(),
            "embedding_dimension": len(embeddings[0]) if len(embeddings) > 0 else 0
        }
        
        # Create points
        for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
            point = self.create_qdrant_point(text, embedding, meta)
            points.append(point)
            
            # Collect stats
            if meta.candidate:
                stats["candidates"].add(meta.candidate)
            if meta.party:
                stats["parties"].add(meta.party)
            if meta.topic_category:
                stats["topics"].add(meta.topic_category)
            if meta.proposal_type:
                stats["proposal_types"].add(meta.proposal_type)
            if meta.page_number:
                stats["pages_with_content"].add(f"{meta.source_file}:p{meta.page_number}")
        
        # Convert sets to lists for JSON serialization
        for key in ["candidates", "parties", "topics", "proposal_types", "pages_with_content"]:
            stats[key] = list(stats[key])
        
        # Create Qdrant collection config
        qdrant_data = {
            "collection_name": collection_name,
            "vector_config": {
                "size": stats["embedding_dimension"],
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
        print(f"Vector dimension: {stats['embedding_dimension']}")
        print(f"Candidates: {len(stats['candidates'])}")
        print(f"Topics: {len(stats['topics'])}")
        
        return qdrant_data
    
    def create_qdrant_collection_script(
        self, 
        collection_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """Create Python script to upload data to Qdrant"""
        
        script_content = f'''#!/usr/bin/env python3
"""
Auto-generated script to upload political documents to Qdrant
Generated by RAG Political System
"""
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models

def upload_to_qdrant(qdrant_url="http://localhost:6333", collection_name="{collection_data['collection_name']}"):
    """Upload data to Qdrant instance"""
    
    # Initialize client
    client = QdrantClient(url=qdrant_url)
    
    # Create collection if it doesn't exist
    try:
        client.get_collection(collection_name)
        print(f"Collection {{collection_name}} already exists")
    except:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size={collection_data['vector_config']['size']},
                distance=models.Distance.COSINE
            )
        )
        print(f"Created collection {{collection_name}}")
    
    # Load points from JSON file
    with open("{output_path.replace('.py', '.json')}", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    points = data["points"]
    
    # Upload points in batches
    batch_size = 100
    total_points = len(points)
    
    for i in range(0, total_points, batch_size):
        batch = points[i:i + batch_size]
        
        qdrant_points = [
            models.PointStruct(
                id=point["id"],
                vector=point["vector"],
                payload=point["payload"]
            )
            for point in batch
        ]
        
        client.upsert(
            collection_name=collection_name,
            points=qdrant_points
        )
        
        print(f"Uploaded batch {{i//batch_size + 1}}/{{(total_points + batch_size - 1)//batch_size}}")
    
    print(f"Successfully uploaded {{total_points}} points to Qdrant")
    
    # Print collection stats
    collection_info = client.get_collection(collection_name)
    print(f"Collection info: {{collection_info}}")

if __name__ == "__main__":
    upload_to_qdrant()
'''
        
        # Save script
        script_path = Path(output_path)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"Created upload script: {script_path}")
        return script_content
    
    def export_search_filters_guide(self, stats: Dict[str, Any], output_path: str) -> str:
        """Generate guide for Qdrant search filters"""
        
        first_candidate = stats['candidates'][0] if stats['candidates'] else 'CANDIDATE_NAME'
        guide_content = f'''# Qdrant Search Filters Guide for Political Documents

## Collection Stats
- Total documents: {stats['total_points']}
- Vector dimension: {stats['embedding_dimension']}
- Candidates: {len(stats['candidates'])}
- Parties: {len(stats['parties'])}  
- Topics: {len(stats['topics'])}
- Proposal types: {len(stats['proposal_types'])}

## Available Filter Fields

### Political Filters
- **candidate**: {', '.join(stats['candidates'])}
- **party**: {', '.join(stats['parties'])}
- **topic_category**: {', '.join(stats['topics'])}
- **proposal_type**: {', '.join(stats['proposal_types'])}

### Document Structure
- **page_number**: Integer (page number in original document)
- **section_depth**: Integer (0-4, depth of section hierarchy)
- **source_file**: String (original filename)

## Example Qdrant Queries

### 1. Find candidate's pension proposals
```python
results = client.search(
    collection_name="political_documents",
    query_vector=query_embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="candidate", match=models.MatchValue(value="{first_candidate}")),
            models.FieldCondition(key="topic_category", match=models.MatchValue(value="pensiones"))
        ]
    ),
    limit=5
)
```

### 2. Compare candidates on health policy
```python
results = client.search(
    collection_name="political_documents", 
    query_vector=query_embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="topic_category", match=models.MatchValue(value="salud")),
            models.FieldCondition(key="proposal_type", match=models.MatchValue(value="propuesta_especifica"))
        ]
    ),
    limit=10
)
```

### 3. Find specific page references
```python
results = client.search(
    collection_name="political_documents",
    query_vector=query_embedding, 
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="candidate", match=models.MatchValue(value="{first_candidate}")),
            models.FieldCondition(key="page_number", range=models.Range(gte=10, lte=20))
        ]
    ),
    limit=5
)
```

### 4. Search by document section depth
```python
# Find main section headers (depth 1-2)
results = client.search(
    collection_name="political_documents",
    query_vector=query_embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="section_depth", range=models.Range(gte=1, lte=2))
        ]
    )
)
```

## Political Analysis Patterns

### Candidate Comparison
1. Search same topic across candidates
2. Filter by proposal_type for comparable content
3. Use page_number for precise citations

### Policy Deep-dive  
1. Filter by topic_category + specific candidate
2. Use section_hierarchy for structured navigation
3. Filter by proposal_type for different content types

### Citation Generation
Use payload fields: candidate, page_number, section_hierarchy for precise citations:
"Según {first_candidate} (Página 45, Políticas Sociales > Sistema Previsional)"
'''
        
        guide_path = Path(output_path)
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"Created search filters guide: {guide_path}")
        return guide_content