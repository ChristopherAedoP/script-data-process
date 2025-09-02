# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## IMPORTANT
  - Never add sensitive or private information in comments or code.
    - Always review and sanitize input data to prevent code injection.
    - Maintain consistency in coding style and follow best practices.
    - Document code clearly and concisely.
    - Never add emoticons, emojis, or informal language in comments or code.
    - Never add emoticons or emojis in logs.
    - Use descriptive and consistent variable and function names.
    - Avoid redundant or unnecessary comments.
    - Group related code into functions or classes.
    - Use consistent naming conventions.
    - Keep logs clear and concise to aid debugging, but avoid excessive verbosity or logging in all cases.
    - Whenever a significant change is made to the code, update the corresponding documentation, README.md, or similar.
    - Do not maintain legacy code; if an improvement is implemented, modify the existing code instead of adding new code.
    - README.md must always reflect the current state of the system. Do not add comparisons such as "before it was like this, now it is like that," or comments like "previously it worked this way, now it works this way," "X optimized," "Z improved."

## Project Overview

This is a RAG (Retrieval-Augmented Generation) system specialized for processing Chilean political documents. It extracts political program content, generates embeddings using OpenAI's API, and exports data to Qdrant Cloud for web chatbot integration.

## Environment Setup

### Method 1: Using .env file (Recommended)
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
# Required for DirectProcessor:
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=https://your-cluster-url.qdrant.tech

# Configuration already included:
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=512
CHUNK_OVERLAP=64
MAX_CHUNKS_RETURN=5
BATCH_SIZE=32
DEVICE=cpu
```

### Method 2: Manual environment variables
```bash
# Required for DirectProcessor
export OPENAI_API_KEY=your_openai_api_key_here
export QDRANT_API_KEY=your_qdrant_api_key_here
export QDRANT_URL=https://your-cluster-url.qdrant.tech

# Optional configuration overrides
export EMBEDDING_MODEL=text-embedding-3-small
export CHUNK_SIZE=512
export CHUNK_OVERLAP=64
export MAX_CHUNKS_RETURN=5
export BATCH_SIZE=32
export DEVICE=cpu
```

## Development Commands

### Core Operations
```bash
# Install dependencies
pip install -r requirements.txt

# Process documents directly to Qdrant Cloud (recommended)
python -m src.cli process-direct

# OR: Index political documents locally first (legacy)
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
- **Fallback model**: Config defaults to "all-MiniLM-L6-v2" but system expects OpenAI format

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

The system uses `src/config.py` for centralized configuration management with environment variable overrides.

### Environment Variables

**Required for DirectProcessor**:
```bash
OPENAI_API_KEY=your_openai_api_key_here     # Required for embeddings generation
QDRANT_API_KEY=your_qdrant_api_key_here     # Required for Qdrant Cloud upload  
QDRANT_URL=https://your-cluster-url.qdrant.tech # Qdrant cluster URL
```

**Optional configuration overrides**:
```bash
EMBEDDING_MODEL=text-embedding-3-small      # OpenAI model (1536 dimensions)
CHUNK_SIZE=512                              # Text chunk size for processing
CHUNK_OVERLAP=64                            # Overlap between chunks
MAX_CHUNKS_RETURN=5                         # Maximum results returned by search
BATCH_SIZE=32                               # Batch size for API calls
DEVICE=cpu                                  # Processing device (legacy, not used with OpenAI)
```

### File Paths (automatically managed)
- Documents: `./docs/` (political program .md files)
- Index: `./data/faiss_index.faiss` 
- Metadata: `./data/metadata.json`
- Original texts: `./data/original_texts.json` (for content retrieval)
- Qdrant Export: `./data/qdrant_export/`

## Development Workflows

### CLI Commands Detail

**Primary workflow**: `process-direct` → deploy to cloud (recommended)
**Legacy workflow**: `index` → `search` → `export-qdrant` → `upload-cloud` → deploy to cloud

- `python -m src.cli process-direct [--docs-path PATH] [--collection-name NAME]`: **Direct processing (recommended)**
  - Processes .md files individually for optimal data quality
  - Direct upload to Qdrant Cloud (no local storage)  
  - Requires: OPENAI_API_KEY, QDRANT_API_KEY, QDRANT_URL
  - File-by-file processing ensures coherent embeddings per candidate
  - Single command from documents to production

- `python -m src.cli index [--force] [--model MODEL] [--index-type TYPE]`: Legacy local processing
  - Processes all .md files in docs/ directory  
  - Generates OpenAI embeddings (requires API key)
  - Creates local FAISS index with political metadata
  - Use `--force` to reindex existing data
  - Index types: IndexFlatIP (default/recommended), IndexFlatL2, IndexIVFFlat

- `python -m src.cli search "query" [--k N] [--min-score 0.0]`: Test search functionality
  - Returns ranked results with political metadata
  - Shows similarity scores, page numbers, section headers
  - **Limitation**: Content preview shows placeholder text only

- `python -m src.cli export-qdrant [--output-dir DIR] [--collection-name NAME]`: Prepare for production deployment
  - Generates JSON export files in `./data/qdrant_export/` 
  - Creates comprehensive filter guides for political queries
  - Outputs political_documents.json and filters guide

- `python -m src.cli upload-cloud [--data-file FILE] [--collection-name NAME]`: Direct upload to Qdrant Cloud
  - Uploads processed data directly to Qdrant Cloud
  - Requires QDRANT_API_KEY and QDRANT_URL environment variables
  - Supports batch uploading with retry logic
  - Creates collection automatically if it doesn't exist

- `python -m src.cli chat`: Interactive chat mode for testing
  - Tests search functionality with conversational interface
  - Supports `/quit`, `/stats`, `/help` commands
  - Useful for validating search results and system performance

- `python -m src.cli benchmark`: Performance testing
  - Runs comprehensive benchmarks on the indexed system
  - Tests search performance across different k values
  - Measures system response times and accuracy

- `python -m src.cli stats`: System information and statistics
  - Shows indexing status, model information, vector store details
  - Displays processed document counts and metadata statistics
  - Useful for system health checks and debugging

### Testing Strategy

The system has minimal automated testing:
- **Integration test**: `python test_rag.py` - validates end-to-end search workflow
- **Manual validation**: Use CLI commands to test political document processing
- **No unit tests**: Individual component testing requires manual verification

### Current System Limitations

1. **Content Retrieval Gap**: `search_with_content()` method only returns placeholder content in search results - actual chunk text mapping may not be fully implemented
2. **Hardcoded Political Mapping**: Candidate/party mappings in document processor may have incomplete coverage for new candidates
3. **No Development Tooling**: No lint, typecheck, or formatting commands found in codebase - manual code quality management
4. **API Dependency**: Complete dependency on OpenAI API for embeddings - no offline fallback mechanism
5. **Configuration Mismatch**: Config defaults to Sentence Transformers model but system expects OpenAI API format

### Political Document Requirements

- **File Format**: Markdown files with mandatory page markers
- **Naming Convention**: `Programa_[Candidate_Name].md` (underscores critical for parsing)
- **Page Markers**: `[START OF PAGE: ##]` and `[END OF PAGE: ##]` required for citation accuracy
- **Content Structure**: Hierarchical Markdown headers for automatic topic classification

### Production Deployment Pattern

The system follows a **local-to-cloud deployment pattern**:
1. **Local development and testing** with FAISS index for rapid iteration
2. **Export to Qdrant format** using `export-qdrant` command 
3. **Direct upload to Qdrant Cloud** using integrated `upload-cloud` command
4. **Production chatbot integration** using political metadata filters for targeted responses

### Key Development Commands

**Setup and direct processing** (recommended):
```bash
# Install dependencies (including OpenAI and Qdrant clients)  
pip install -r requirements.txt
# OR install in development mode with console scripts
pip install -e .

# Setup environment variables using .env
cp .env.example .env
# Edit .env file with your API keys

# Process all documents directly to Qdrant Cloud
python -m src.cli process-direct

# Check system status
python -m src.cli stats
```

**Legacy setup and indexing**:
```bash
# Set environment variables manually
export OPENAI_API_KEY=your_key_here
export QDRANT_API_KEY=your_key_here  
export QDRANT_URL=https://your-cluster-url.qdrant.tech

# Index all political documents locally (legacy)
python -m src.cli index

# Check system status
python -m src.cli stats
```

**Testing and validation**:
```bash
# Test search functionality
python -m src.cli search "¿qué propone para pensiones?"

# Interactive testing mode
python -m src.cli chat

# Performance benchmarks  
python -m src.cli benchmark

# Integration test
python test_rag.py
```

**Production deployment**:
```bash
# Direct processing (recommended - all-in-one)
python -m src.cli process-direct

# Legacy approach (local processing then upload)
python -m src.cli export-qdrant
python -m src.cli upload-cloud
```