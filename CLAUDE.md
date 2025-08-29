# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) system specialized for processing Chilean political documents. It extracts political program content, generates embeddings using OpenAI's API, and exports data to Qdrant Cloud for web chatbot integration.

## Environment Setup

### Required Environment Variables
```bash
# Required for embeddings generation
OPENAI_API_KEY=your_openai_api_key_here

# Optional configuration overrides
EMBEDDING_MODEL=text-embedding-3-small  # OpenAI model (1536 dimensions)
CHUNK_SIZE=512
CHUNK_OVERLAP=64
MAX_CHUNKS_RETURN=5
BATCH_SIZE=32
DEVICE=cpu
```

## Development Commands

### Core Operations
```bash
# Install dependencies
pip install -r requirements.txt

# Index political documents (main operation)
python -m src.cli index

# Search the index
python -m src.cli search "¿qué propone para pensiones?"

# View system statistics
python -m src.cli stats

# Run performance benchmarks
python -m src.cli benchmark

# Interactive chat mode for testing
python -m src.cli chat

# Export to Qdrant Cloud format
python -m src.cli export-qdrant
```

### Testing
```bash
# Simple integration test
python test_rag.py
```

### Entry Points
- Main CLI: `python -m src.cli`
- Alternative CLI: `rag-cli` (after `pip install -e .`)
- Direct testing: `python test_rag.py`

## Architecture

### Core Components

**RAGSystem** (`src/rag_system.py`): Main orchestrator coordinating all components
- Manages complete document indexing workflow from political docs to searchable vectors
- Coordinates between DocumentProcessor → EmbeddingGenerator → FAISSVectorStore → QdrantExporter
- Handles search operations with rich political metadata filtering
- Exports complete system to Qdrant Cloud format for production deployment
- **Critical limitation**: `search_with_content()` method only returns placeholder content - actual chunk text retrieval not implemented

**DocumentProcessor** (`src/document_processor.py`): Specialized political document processor
- **Page-aware parsing**: Extracts content using `[START OF PAGE: ##]` and `[END OF PAGE: ##]` markers for precise citation
- **Political metadata extraction**: Candidate/party info from filename pattern `Programa_[Candidate_Name].md`
- **Automatic content classification**: 
  - Topics: pensiones, salud, educación, economía, seguridad, vivienda, transporte, medio_ambiente
  - Proposal types: propuesta_especifica, meta_cuantitativa, diagnostico, descripcion_general
- **Hierarchical chunking**: Combines Markdown header splitting with size-based text splitting within page boundaries
- **Hardcoded candidate mapping**: Limited candidate/party mapping requires manual updates

**EmbeddingGenerator** (`src/embeddings.py`): OpenAI API integration for embeddings
- **Model**: text-embedding-3-small generating 1536-dimensional embeddings (NOT Sentence Transformers)
- **API dependency**: Requires `OPENAI_API_KEY` environment variable - system fails without it
- **Batch processing**: Configurable batch size (default: 32) with progress tracking and error handling
- **Cost considerations**: OpenAI API calls for every embedding generation

**FAISSVectorStore** (`src/vector_store.py`): Local vector search engine
- **Index types**: IndexFlatIP (cosine similarity), IndexFlatL2 (Euclidean), IndexIVFFlat (approximate)
- **Dual storage**: FAISS index (.faiss) + pickled metadata (.pkl) for complete chunk information
- **Search capabilities**: Configurable k-nearest neighbor with similarity score filtering
- **Performance benchmarking**: Built-in search performance testing across different k values

**QdrantExporter** (`src/qdrant_exporter.py`): Production deployment preparation
- **Dual output**: JSON data export + Python upload scripts for Qdrant Cloud integration
- **Rich political metadata**: Preserves all political classifications and page references in Qdrant payloads
- **Filter guide generation**: Creates comprehensive filter examples for political document queries
- **Batch upload optimization**: 100-point batches for efficient cloud deployment

### Dual Architecture Pattern

This system implements a **hybrid local-to-cloud architecture**:

1. **Local Development Pipeline**: 
   - Documents → DocumentProcessor → EmbeddingGenerator (OpenAI API) → FAISSVectorStore
   - Local FAISS index for fast development, testing, and experimentation
   - Rich CLI tools for debugging and validation

2. **Production Cloud Pipeline**: 
   - Complete local system → QdrantExporter → Qdrant Cloud deployment
   - Maintains all political metadata and search capabilities
   - Optimized for web chatbot integration

### Political RAG Specializations

**Page-Aware Document Processing**: Unlike generic RAG systems, this processor respects document page boundaries using `[START/END OF PAGE: ##]` markers, enabling precise citations like "Según Candidate X (Página 15)".

**Political Metadata Pipeline**: Each text chunk gets automatically enriched with:
- **Candidate/Party**: Extracted from filename patterns (`Programa_[Name].md`)
- **Topic Classification**: Rule-based classification into 8 political domains
- **Proposal Type Detection**: Identifies 4 types (specific proposals, quantitative goals, diagnoses, descriptions)
- **Section Hierarchy**: Preserves Markdown header structure for navigation

**Multi-Modal Search Architecture**: Supports both:
- **Semantic similarity**: Vector search for meaning-based retrieval
- **Political filtering**: Metadata-based filtering by candidate, party, topic, page range
- **Hybrid queries**: Combined semantic + political filter queries for precise results

## Configuration

The system uses `src/config.py` for centralized configuration management with environment variable overrides:

### File Paths (automatically managed)
- Documents: `./docs/` (political program .md files)
- Index: `./data/faiss_index.faiss` 
- Metadata: `./data/metadata.json`
- Qdrant Export: `./data/qdrant_export/`

## Development Workflows

### CLI Commands Detail

**Primary workflow**: `index` → `search` → `export-qdrant` → deploy to cloud

- `python -m src.cli index [--force] [--model MODEL] [--index-type TYPE]`: Main processing command
  - Processes all .md files in docs/ directory  
  - Generates OpenAI embeddings (requires API key)
  - Creates local FAISS index with political metadata
  - Use `--force` to reindex existing data
  - Index types: IndexFlatIP (default/recommended), IndexFlatL2, IndexIVFFlat

- `python -m src.cli search "query" [--k N] [--min-score 0.0]`: Test search functionality
  - Returns ranked results with political metadata
  - Shows similarity scores, page numbers, section headers
  - **Limitation**: Content preview shows placeholder text only

- `python -m src.cli export-qdrant`: Prepare for production deployment
  - Generates 5 files in `./data/qdrant_export/`
  - Creates upload scripts for Qdrant Cloud integration
  - Includes comprehensive filter guides for political queries

### Testing Strategy

The system has minimal automated testing:
- **Integration test**: `python test_rag.py` - validates end-to-end search workflow
- **Manual validation**: Use CLI commands to test political document processing
- **No unit tests**: Individual component testing requires manual verification

### Current System Limitations

1. **Content Retrieval Gap**: `search_with_content()` in `src/rag_system.py:171` only returns placeholder content - actual chunk text mapping not implemented
2. **Hardcoded Political Mapping**: `src/document_processor.py:112` has incomplete candidate/party mappings
3. **No Development Tooling**: No lint, typecheck, or formatting commands found in codebase
4. **API Dependency**: Complete dependency on OpenAI API for embeddings - no offline fallback

### Political Document Requirements

- **File Format**: Markdown files with mandatory page markers
- **Naming Convention**: `Programa_[Candidate_Name].md` (underscores critical for parsing)
- **Page Markers**: `[START OF PAGE: ##]` and `[END OF PAGE: ##]` required for citation accuracy
- **Content Structure**: Hierarchical Markdown headers for automatic topic classification

### Production Deployment Pattern

The system follows a **local-to-cloud deployment pattern**:
1. Local development and testing with FAISS
2. Export to Qdrant-compatible JSON format  
3. Upload to Qdrant Cloud for web chatbot integration
4. Chatbot uses political filters for targeted responses