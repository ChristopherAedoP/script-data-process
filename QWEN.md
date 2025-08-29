# Chatbot Político RAG - Sistema de Búsqueda de Documentos Políticos

## Project Overview

This is a Retrieval-Augmented Generation (RAG) system specialized for processing political programs of Chilean presidential candidates. The system extracts structured information, generates embeddings locally, and enables deployment to Qdrant Cloud for web-based chatbots.

### Key Features

- **Political Specialization**: Extracts metadata from candidates, parties, topics, and pages
- **Intelligent Chunking**: Respects page markers `[START OF PAGE: ##]` and `[END OF PAGE: ##]`
- **Automatic Classification**: Detects topics (health, pensions, education) and proposal types
- **Local Embeddings**: Uses Sentence Transformers all-MiniLM-L6-v2 (384 dimensions)
- **Vector Search**: FAISS IndexFlatIP for cosine similarity
- **Qdrant Cloud Export**: Compatible format for cloud deployment in web chatbots
- **Complete CLI**: Interface for indexing, searching, and exporting

## Project Structure

```
script-data-process/
├── src/
│   ├── __init__.py
│   ├── config.py              # System configuration
│   ├── document_processor.py  # Political document processing with metadata
│   ├── embeddings.py          # Embedding generation
│   ├── vector_store.py        # FAISS vector store
│   ├── rag_system.py          # Main RAG system
│   ├── qdrant_exporter.py     # Export to Qdrant Cloud format
│   └── cli.py                # Complete CLI interface
├── docs/                     # Political documents (.md with page markers)
├── data/
│   ├── faiss_index.faiss     # FAISS vector index
│   ├── metadata.json         # Chunk metadata with political information
│   └── qdrant_export/        # Files for Qdrant Cloud
│       ├── political_documents.json           # Vector data (3274 points)
│       ├── upload_to_qdrant_cloud.py         # Script to upload to cloud
│       ├── upload_political_documents.py     # Local script (legacy)
│       ├── political_documents_filters_guide.md  # Filters and queries guide
│       └── QDRANT_CLOUD_SETUP.md             # Step-by-step cloud setup
├── models/                   # Sentence Transformers model cache
├── requirements.txt          # Python dependencies
└── setup.py                 # Package configuration
```

## Installation

### 1. Clone and Set Up Environment

```bash
cd chatbot-politico
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### 3. Configuration (Optional)

```bash
cp .env.example .env
# Edit .env with your configurations
```

## Usage Flow

### 1. Process Political Documents

```bash
# STEP 1: Index political documents (with automatic metadata)
python -m src.cli index

# Results:
# - Extracts pages using [START OF PAGE: ##] markers
# - Automatically classifies topics (health, pensions, education, etc.)
# - Detects proposal types (specific, diagnostic, goals)
# - Generates 384-dimensional embeddings
# - Creates local FAISS index

# STEP 2: Verify processing
python -m src.cli stats
# Shows: processed documents, chunks, candidates, detected topics
```

### 2. Export for Web Chatbot (Qdrant Cloud)

```bash
# STEP 3: Export data to Qdrant Cloud format
python -m src.cli export-qdrant

# This generates 5 files in data/qdrant_export/:
```

**Generated Files Explained:**

1. **`political_documents.json`** (~35MB)
   - Contains 3,274 vector points with embeddings
   - Each point includes: vector (384 dims), political metadata, content
   - Format compatible with Qdrant Cloud

2. **`upload_to_qdrant_cloud.py`**
   - Optimized script to upload to Qdrant Cloud
   - Uses API key and cluster URL
   - Uploads in batches of 64 points
   - Error handling and progress tracking

3. **`upload_political_documents.py`** (legacy)
   - Script for local Qdrant (localhost:6333)
   - Used for local testing with Docker

4. **`political_documents_filters_guide.md`**
   - Guide on how to make queries with political filters
   - Real examples with "Jeannette Jara" and "Partido Socialista"
   - Patterns for comparing candidates, searching by topic, etc.

5. **`QDRANT_CLOUD_SETUP.md`**
   - Step-by-step guide to create account in Qdrant Cloud
   - Credential configuration
   - Complete deployment instructions

### 3. Deploy to Qdrant Cloud

```bash
# STEP 4: Configure credentials (after creating account at cloud.qdrant.io)
set QDRANT_API_KEY=qdt_your_api_key_here
set QDRANT_URL=https://your-cluster-url.qdrant.tech

# STEP 5: Upload data to cloud
cd data/qdrant_export
python upload_to_qdrant_cloud.py
```

### 4. Local Testing (Optional)

```bash
# Local search in FAISS
python -m src.cli search "¿qué propone para pensiones?"

# Interactive chat
python -m src.cli chat
```

## Configuration

### Environment Variables (.env)

```bash
# Embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Chunking parameters
CHUNK_SIZE=512
CHUNK_OVERLAP=64

# Search
MAX_CHUNKS_RETURN=5

# Paths
DOCUMENTS_PATH=./docs
INDEX_PATH=./data/faiss_index
METADATA_PATH=./data/metadata.json

# Performance
BATCH_SIZE=32
DEVICE=cpu
```

### System Parameters

- **CHUNK_SIZE**: Maximum chunk size in tokens (default: 512)
- **CHUNK_OVERLAP**: Overlap between chunks (default: 64)
- **EMBEDDING_MODEL**: Sentence Transformers model (default: all-MiniLM-L6-v2)
- **MAX_CHUNKS_RETURN**: Maximum results per search (default: 5)

## Supported Models

### Recommended Sentence Transformers:

- **all-MiniLM-L6-v2**: Fast, 384 dim, good general quality
- **all-mpnet-base-v2**: Better quality, 768 dim, slower
- **multi-qa-mpnet-base-dot-v1**: Optimized for Q&A
- **paraphrase-multilingual-MiniLM-L12-v2**: Multilingual support

## FAISS Index Types

- **IndexFlatIP**: Exact search with inner product (cosine similarity)
- **IndexFlatL2**: Exact search with L2 distance
- **IndexIVFFlat**: Approximate search for large datasets

## Performance Metrics

### MVP Goals:
- ⚡ Indexing: < 1 min per 100 documents
- ⚡ Search: < 100ms per query
- 🎯 Relevance: Top-3 accuracy > 70%
- 💾 Memory: < 500MB for 10K chunks

### Typical Benchmark:
```bash
python -m src.cli benchmark

# Example with real data:
# ✅ 3,274 documents processed
# ✅ Candidate: Jeannette Jara (Partido Socialista)
# ✅ 9 topics: health, pensions, education, etc.
# ✅ 4 proposal types detected automatically
```

## Testing

### Example Documents Included:
- `docs/ejemplo_politica.md`: Digital transformation policy
- `docs/inteligencia_artificial.md`: AI in government

### Political Test Queries:
- "¿Qué propone Jara para pensiones?"
- "Políticas de salud pública"
- "Propuestas de vivienda"
- "Medidas de seguridad ciudadana"
- "Educación pública y reformas"

## Data Processing

**Input**: .md documents of political programs with:
- Page markers: `[START OF PAGE: ##]` and `[END OF PAGE: ##]`
- Hierarchical headers (##, ###, ####)
- Political proposal content

**Processed Output**:
- **3,274 chunks** vectorized
- **Political metadata**: candidate, party, page, topic, proposal type
- **9 detected topics**: health, pensions, education, security, etc.
- **4 proposal types**: specific, diagnostics, goals, descriptions

## Political Processing Flow

1. **Page Extraction**: Detects `[START/END OF PAGE: ##]` markers
2. **Intelligent Chunking**: Respects page boundaries + semantic headers
3. **Automatic Classification**: Assigns topics and types based on content
4. **Embeddings**: Sentence Transformers (384 dimensions)
5. **Qdrant Export**: Cloud-ready format with political metadata
6. **Deploy**: Upload to Qdrant Cloud for web chatbot

## For Your Web Chatbot

Once in Qdrant Cloud, you can make queries like:

```python
# ¿Qué propone Jara para pensiones?
client.search(
    collection_name="political_documents",
    query_vector=embedding("pensiones"),
    query_filter={"must": [
        {"key": "candidate", "match": {"value": "Jeannette Jara"}},
        {"key": "topic_category", "match": {"value": "pensiones"}}
    ]},
    limit=5
)
```

## Roadmap

### ✅ Completed:
- Political specialization processing
- Qdrant Cloud export
- Rich metadata with pages and topics

### 🔄 Next Steps (Your Web Chatbot):
1. **Frontend**: React/Vue with chat interface
2. **Backend**: API that connects to Qdrant Cloud
3. **LLM Integration**: OpenAI/Anthropic for generating responses
4. **Deploy**: Vercel/Netlify for the web chatbot

## CLI Commands

The system provides a comprehensive CLI interface:

```bash
# Main commands
rag-cli index          # Index documents from a directory
rag-cli search QUERY   # Search for relevant documents
rag-cli stats          # Show system statistics
rag-cli benchmark      # Run performance benchmarks
rag-cli chat           # Interactive chat mode
rag-cli export-qdrant  # Export data to Qdrant format
```

## Development Guidelines

### Code Structure
- Modular architecture with separate components for document processing, embeddings, vector storage, and RAG orchestration
- Clear separation between data processing and retrieval components
- Extensible design to support different embedding models and vector databases

### Testing Approach
- Unit tests for core components
- Integration tests for the full RAG pipeline
- Performance benchmarks for indexing and search operations
- Example queries for political content validation

### Extensibility
- Easy to add new embedding models through configuration
- Support for different FAISS index types
- Pluggable architecture for document processors
- Export modules for different vector databases