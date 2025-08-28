# Chatbot Político RAG - Sistema de Búsqueda de Documentos Políticos

Sistema RAG especializado para procesar programas políticos de candidatos presidenciales. Extrae información estructurada, genera embeddings localmente y permite deploy a Qdrant Cloud para chatbots web.

## 🚀 Características

- ✅ **Procesamiento político especializado**: Metadatos de candidatos, partidos, temas y páginas
- ✅ **Chunking inteligente por páginas**: Respeta marcadores `[START OF PAGE: ##]` y `[END OF PAGE: ##]`
- ✅ **Clasificación automática**: Detecta temas (salud, pensiones, educación) y tipos de propuestas
- ✅ **Embeddings locales**: Sentence Transformers all-MiniLM-L6-v2 (384 dimensiones)
- ✅ **Búsqueda vectorial**: FAISS IndexFlatIP para cosine similarity
- ✅ **Export a Qdrant Cloud**: Formato compatible con deploy en cloud para chatbots web
- ✅ **CLI completa**: Interface para indexar, buscar y exportar

## 📁 Estructura del Proyecto

```
script-data-process/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuración del sistema
│   ├── document_processor.py  # Procesamiento político con metadatos
│   ├── embeddings.py         # Generación de embeddings  
│   ├── vector_store.py       # FAISS vector store
│   ├── rag_system.py         # Sistema RAG principal
│   ├── qdrant_exporter.py    # Export a formato Qdrant Cloud
│   └── cli.py               # Interface CLI completa
├── docs/                    # Documentos políticos (.md con page markers)
├── data/
│   ├── faiss_index.faiss    # Índice vectorial FAISS
│   ├── metadata.json        # Metadatos de chunks con info política
│   └── qdrant_export/       # Archivos para Qdrant Cloud
│       ├── political_documents.json           # Datos vectoriales (3274 puntos)
│       ├── upload_to_qdrant_cloud.py         # Script para subir a cloud
│       ├── upload_political_documents.py     # Script local (legacy)
│       ├── political_documents_filters_guide.md  # Guía de filtros y queries
│       └── QDRANT_CLOUD_SETUP.md            # Guía paso a paso setup cloud
├── models/                # Cache de modelos Sentence Transformers
├── requirements.txt    # Dependencias Python
└── setup.py          # Configuración del paquete
```

## 🔧 Instalación

### 1. Clonar y configurar entorno

```bash
cd chatbot-politico
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt

# O instalar en modo desarrollo
pip install -e .
```

### 3. Configuración (opcional)

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## 🚀 Flujo de Uso Completo

### 1. Procesar Documentos Políticos

```bash
# PASO 1: Indexar documentos políticos (con metadatos automáticos)
python -m src.cli index

# Resultado: 
# - Extrae páginas usando [START OF PAGE: ##] markers
# - Clasifica automáticamente temas (salud, pensiones, educación, etc.)
# - Detecta tipos de propuestas (específicas, diagnósticos, metas)
# - Genera embeddings de 384 dimensiones
# - Crea índice FAISS local

# PASO 2: Verificar procesamiento
python -m src.cli stats
# Muestra: documentos procesados, chunks, candidatos, temas detectados
```

### 2. Exportar para Chatbot Web (Qdrant Cloud)

```bash
# PASO 3: Exportar datos a formato Qdrant Cloud
python -m src.cli export-qdrant

# Esto genera 5 archivos en data/qdrant_export/:
```

**Archivos Generados Explicados:**

1. **`political_documents.json`** (35MB aprox.)
   - Contiene los 3,274 puntos vectoriales con embeddings
   - Cada punto incluye: vector (384 dims), metadatos políticos, contenido
   - Formato compatible con Qdrant Cloud

2. **`upload_to_qdrant_cloud.py`** 
   - Script optimizado para subir a Qdrant Cloud
   - Usa API key y cluster URL
   - Upload en batches de 64 puntos
   - Manejo de errores y progreso

3. **`upload_political_documents.py`** (legacy)
   - Script para Qdrant local (localhost:6333)
   - Usado para testing local con Docker

4. **`political_documents_filters_guide.md`**
   - Guía de cómo hacer queries con filtros políticos
   - Ejemplos reales con "Jeannette Jara" y "Partido Socialista"
   - Patterns para comparar candidatos, buscar por tema, etc.

5. **`QDRANT_CLOUD_SETUP.md`**
   - Guía paso a paso para crear cuenta en Qdrant Cloud
   - Configuración de credenciales
   - Instrucciones de deploy completas

### 3. Deploy a Qdrant Cloud

```bash
# PASO 4: Configurar credenciales (después de crear cuenta en cloud.qdrant.io)
set QDRANT_API_KEY=qdt_tu_api_key_aquí
set QDRANT_URL=https://tu-cluster-url.qdrant.tech

# PASO 5: Subir datos a cloud
cd data/qdrant_export
python upload_to_qdrant_cloud.py
```

### 4. Testing Local (Opcional)

```bash
# Búsqueda local en FAISS
python -m src.cli search "¿qué propone para pensiones?"

# Chat interactivo
python -m src.cli chat
```

## ⚙️ Configuración

### Variables de entorno (.env)

```bash
# Modelo de embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Parámetros de chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=64

# Búsqueda
MAX_CHUNKS_RETURN=5

# Rutas
DOCUMENTS_PATH=./docs
INDEX_PATH=./data/faiss_index
METADATA_PATH=./data/metadata.json

# Rendimiento
BATCH_SIZE=32
DEVICE=cpu
```

### Parámetros del sistema

- **CHUNK_SIZE**: Tamaño máximo de chunk en tokens (default: 512)
- **CHUNK_OVERLAP**: Solapamiento entre chunks (default: 64) 
- **EMBEDDING_MODEL**: Modelo Sentence Transformers (default: all-MiniLM-L6-v2)
- **MAX_CHUNKS_RETURN**: Resultados máximos por búsqueda (default: 5)

## 📊 Modelos Soportados

### Sentence Transformers recomendados:

- **all-MiniLM-L6-v2**: Rápido, 384 dim, buena calidad general
- **all-mpnet-base-v2**: Mejor calidad, 768 dim, más lento
- **multi-qa-mpnet-base-dot-v1**: Optimizado para Q&A
- **paraphrase-multilingual-MiniLM-L12-v2**: Soporte multiidioma

## 🔍 Tipos de Índice FAISS

- **IndexFlatIP**: Búsqueda exacta con inner product (cosine similarity)
- **IndexFlatL2**: Búsqueda exacta con distancia L2
- **IndexIVFFlat**: Búsqueda aproximada para datasets grandes

## 📈 Métricas de Rendimiento

### Objetivo del MVP:
- ⚡ Indexing: < 1 min por 100 documentos
- ⚡ Búsqueda: < 100ms por query
- 🎯 Relevancia: Top-3 accuracy > 70%
- 💾 Memoria: < 500MB para 10K chunks

### Benchmark típico:
```bash
python -m src.cli benchmark

# Ejemplo con datos reales:
# ✅ 3,274 documentos procesados
# ✅ Candidato: Jeannette Jara (Partido Socialista)
# ✅ 9 temas: salud, pensiones, educación, etc.
# ✅ 4 tipos propuestas detectados automáticamente
```

## 🧪 Testing

### Documentos de ejemplo incluidos:
- `docs/ejemplo_politica.md`: Política de transformación digital
- `docs/inteligencia_artificial.md`: IA en el gobierno

### Queries de prueba políticas:
- "¿Qué propone Jara para pensiones?"
- "Políticas de salud pública"  
- "Propuestas de vivienda"
- "Medidas de seguridad ciudadana"
- "Educación pública y reformas"

## 📊 Qué Datos Procesa

**Input**: Documentos .md de programas políticos con:
- Marcadores de página: `[START OF PAGE: ##]` y `[END OF PAGE: ##]`
- Headers jerárquicos (##, ###, ####)
- Contenido de propuestas políticas

**Output Procesado**:
- **3,274 chunks** vectorizados
- **Metadatos políticos**: candidato, partido, página, tema, tipo propuesta  
- **9 temas detectados**: salud, pensiones, educación, seguridad, etc.
- **4 tipos propuestas**: específicas, diagnósticos, metas, descripciones

## 🔄 Flujo de Procesamiento Político

1. **Extracción Páginas**: Detecta marcadores `[START/END OF PAGE: ##]` 
2. **Chunking Inteligente**: Respeta límites de página + headers semánticos
3. **Clasificación Automática**: Asigna temas y tipos según contenido
4. **Embeddings**: Sentence Transformers (384 dimensiones)
5. **Export Qdrant**: Formato cloud-ready con metadatos políticos
6. **Deploy**: Upload a Qdrant Cloud para chatbot web

## 🌐 Para tu Chatbot Web

Una vez en Qdrant Cloud, puedes hacer queries como:

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

## 🚀 Roadmap

### ✅ Completado:
- Procesamiento político especializado
- Export a Qdrant Cloud
- Metadatos ricos con páginas y temas

### 🔄 Siguiente (Tu Chatbot Web):
1. **Frontend**: React/Vue con interface de chat
2. **Backend**: API que conecte a Qdrant Cloud
3. **LLM Integration**: OpenAI/Anthropic para generar respuestas
4. **Deploy**: Vercel/Netlify para el chatbot web


