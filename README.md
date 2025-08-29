# Chatbot Político RAG - Sistema de Búsqueda de Documentos Políticos

Sistema RAG especializado para procesar programas políticos de candidatos presidenciales. Extrae información estructurada, genera embeddings con OpenAI API y permite deploy directo a Qdrant Cloud para chatbots web.

## 🚀 Características

- ✅ **Procesamiento político especializado**: Metadatos de candidatos, partidos, temas y páginas
- ✅ **Chunking inteligente por páginas**: Respeta marcadores `[START OF PAGE: ##]` y `[END OF PAGE: ##]`
- ✅ **Clasificación automática**: Detecta temas (salud, pensiones, educación) y tipos de propuestas
- ✅ **Embeddings OpenAI**: text-embedding-3-small API (1536 dimensiones)
- ✅ **Búsqueda vectorial**: FAISS IndexFlatIP para cosine similarity
- ✅ **Export a Qdrant Cloud**: Formato compatible con deploy en cloud para chatbots web
- ✅ **Upload directo**: Comando CLI integrado para subir a Qdrant Cloud
- ✅ **CLI completa**: Interface para indexar, buscar, exportar y subir

## 📁 Estructura del Proyecto

```
script-data-process/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuración del sistema
│   ├── document_processor.py  # Procesamiento político con metadatos dinámicos
│   ├── embeddings.py         # Generación de embeddings con OpenAI API  
│   ├── vector_store.py       # FAISS vector store
│   ├── rag_system.py         # Sistema RAG principal con contenido real
│   ├── qdrant_exporter.py    # Export a formato Qdrant Cloud
│   └── cli.py               # Interface CLI completa con upload integrado
├── docs/                    # 6 programas políticos (.md con page markers)
│   ├── Programa_Eduardo_Artes.md
│   ├── Programa_Evelyn_Matthei.md  
│   ├── Programa_Harold_Mayne-Nicholls.md
│   ├── Programa_Jeannette_Jara.md
│   ├── Programa_Johannes_Kaiser.md
│   └── Programa_Jose_Antonio_Kast_R.md
├── data/
│   ├── faiss_index.faiss    # Índice vectorial FAISS
│   ├── faiss_index_metadata.pkl  # Metadatos vectoriales
│   ├── metadata.json        # Metadatos de chunks con info política
│   ├── original_texts.json  # Textos originales para recuperación de contenido
│   └── qdrant_export/       # Archivos para Qdrant Cloud
│       ├── political_documents.json           # Datos vectoriales (3274 puntos, 1536 dims)
│       └── political_documents_filters_guide.md  # Guía de filtros y queries
├── upload_to_qdrant_cloud.py  # Script manual para Qdrant Cloud (movido del data/)
├── models/                # Cache de modelos (legacy Sentence Transformers)
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

# Dependencias adicionales para Qdrant Cloud
pip install qdrant-client openai

# O instalar en modo desarrollo
pip install -e .
```

### 3. Configuración requerida

```bash
# Variables de entorno requeridas
export OPENAI_API_KEY=tu_openai_api_key_aquí

# Para upload a Qdrant Cloud (opcional)
export QDRANT_API_KEY=tu_qdrant_api_key_aquí
export QDRANT_URL=https://tu-cluster-url.qdrant.tech
```

## 🚀 Flujo de Uso Completo

### 1. Procesar Documentos Políticos

```bash
# PASO 1: Indexar documentos políticos (requiere OPENAI_API_KEY)
python -m src.cli index

# Resultado: 
# - Extrae candidatos dinámicamente de nombres de archivo
# - Extrae páginas usando [START OF PAGE: ##] markers
# - Clasifica automáticamente 9 temas (salud, pensiones, educación, etc.)
# - Detecta 4 tipos de propuestas (específicas, diagnósticos, metas)
# - Genera embeddings de 1536 dimensiones con OpenAI API
# - Crea índice FAISS local + almacena contenido original

# PASO 2: Verificar procesamiento
python -m src.cli stats
# Muestra: 6 candidatos, 3274 chunks, 9 temas detectados automáticamente
```

### 2. Deploy a Qdrant Cloud

```bash
# PASO 3: Exportar datos a formato Qdrant Cloud
python -m src.cli export-qdrant

# PASO 4: Upload directo a Qdrant Cloud (requiere credenciales)
python -m src.cli upload-cloud

# Alternativamente, usar script manual:
python upload_to_qdrant_cloud.py
```

### 3. Comandos CLI Disponibles

```bash
# Ver todos los comandos
python -m src.cli --help

# Comandos disponibles:
python -m src.cli index         # Indexar documentos con OpenAI embeddings
python -m src.cli search        # Buscar en índice local  
python -m src.cli stats         # Estadísticas del sistema
python -m src.cli benchmark     # Pruebas de rendimiento
python -m src.cli chat          # Modo chat interactivo
python -m src.cli export-qdrant # Exportar a formato Qdrant Cloud
python -m src.cli upload-cloud  # Upload directo a Qdrant Cloud
```

**Archivos de Export Generados:**

1. **`political_documents.json`** (40MB aprox.)
   - 3,274 puntos vectoriales con embeddings de 1536 dimensiones
   - Contenido real de documentos (no placeholders)
   - Metadatos políticos: 6 candidatos extraídos dinámicamente, 9 temas, 4 tipos de propuestas

2. **`political_documents_filters_guide.md`**
   - Guía de queries con filtros políticos específicos
   - Ejemplos de búsqueda por candidato, tema, página
   - Patterns para análisis político comparativo

**Scripts de Upload:**

- **CLI integrado**: `python -m src.cli upload-cloud` (recomendado)
- **Script manual**: `python upload_to_qdrant_cloud.py` (alternativo)

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
# ⚠️ REQUERIDO: OpenAI API Key
OPENAI_API_KEY=tu_openai_api_key_aquí

# ⚠️ REQUERIDO para upload a Qdrant Cloud:
QDRANT_API_KEY=qdt_tu_api_key_aquí
QDRANT_URL=https://tu-cluster-url.qdrant.tech

# Configuraciones opcionales:
EMBEDDING_MODEL=text-embedding-3-small  # OpenAI model (1536 dims)
CHUNK_SIZE=512                          # Tamaño de chunk
CHUNK_OVERLAP=64                        # Solapamiento entre chunks
MAX_CHUNKS_RETURN=5                     # Resultados por búsqueda
BATCH_SIZE=32                           # Batch size para API calls
```

## 📊 Datos Procesados Actuales

### Estadísticas del Sistema:
- **6 candidatos**: Jose Antonio Kast R, Harold Mayne-Nicholls, Eduardo Artes, Johannes Kaiser, Evelyn Matthei, Jeannette Jara
- **3,274 chunks** procesados con contenido real
- **9 temas detectados**: medio_ambiente, educación, seguridad, vivienda, economía, pensiones, salud, general, transporte
- **4 tipos de propuestas**: meta_cuantitativa, diagnostico, descripcion_general, propuesta_especifica
- **Embeddings**: 1536 dimensiones (OpenAI text-embedding-3-small)

### Extracción Dinámica:
- **Candidatos**: Extraídos automáticamente de nombres de archivo `Programa_[Nombre].md`
- **Temas**: Clasificación automática basada en contenido
- **Páginas**: Procesamiento respetando marcadores de página
- **Contenido**: Almacenamiento y recuperación de texto original completo

## 🔍 Tipos de Índice FAISS

- **IndexFlatIP**: Búsqueda exacta con inner product (cosine similarity)
- **IndexFlatL2**: Búsqueda exacta con distancia L2
- **IndexIVFFlat**: Búsqueda aproximada para datasets grandes

## 📈 Estado Actual del Sistema

### Datos Reales Procesados:
- ✅ **6 candidatos presidenciales** procesados automáticamente
- ✅ **3,274 chunks** con contenido real (no placeholders)
- ✅ **9 categorías temáticas** detectadas automáticamente
- ✅ **4 tipos de propuestas** clasificadas por contenido
- ✅ **Embeddings 1536D** generados con OpenAI API
- ✅ **Upload directo** a Qdrant Cloud integrado en CLI

### Benchmark con datos reales:
```bash
python -m src.cli benchmark

# Métricas actuales:
# ✅ 3,274 chunks procesados exitosamente
# ✅ Contenido real almacenado y recuperable
# ✅ Metadatos políticos completos para todos los candidatos
# ✅ Sistema listo para producción en Qdrant Cloud
```

## 🧪 Testing y Ejemplos

### Documentos procesados:
- 6 programas presidenciales completos en `docs/`
- Formato: `Programa_[Nombre_Candidato].md`
- Con marcadores de página y estructura jerárquica

### Queries de prueba con datos reales:
```bash
# Búsquedas temáticas
python -m src.cli search "pensiones sistema previsional"
python -m src.cli search "salud pública atención primaria"
python -m src.cli search "seguridad ciudadana delincuencia"
python -m src.cli search "educación reforma universitaria"

# Búsquedas por candidato (en chat mode)
python -m src.cli chat
Query: ¿Qué propone Evelyn Matthei para pensiones?
Query: Propuestas de Jeannette Jara en salud
```

## 📊 Arquitectura de Datos

**Input**: 6 programas políticos (.md) con:
- Marcadores de página: `[START OF PAGE: ##]` y `[END OF PAGE: ##]`
- Headers jerárquicos (##, ###, ####)
- Contenido de propuestas políticas estructuradas

**Output Procesado**:
- **3,274 chunks** con contenido real recuperable
- **Metadatos políticos**: candidato extraído dinámicamente, página, tema, tipo propuesta  
- **6 candidatos**: Procesados automáticamente desde nombres de archivo
- **9 temas detectados**: medio_ambiente, educación, seguridad, vivienda, economía, pensiones, salud, general, transporte
- **4 tipos propuestas**: meta_cuantitativa, diagnostico, descripcion_general, propuesta_especifica

## 🔄 Flujo de Procesamiento Político

1. **Extracción Dinámica**: Candidatos desde nombres `Programa_[Nombre].md`
2. **Chunking por Páginas**: Respeta marcadores `[START/END OF PAGE: ##]`
3. **Clasificación Automática**: Detecta 9 temas y 4 tipos de propuestas
4. **Embeddings OpenAI**: text-embedding-3-small (1536 dimensiones)
5. **Almacenamiento**: FAISS + contenido original para recuperación
6. **Export Qdrant**: JSON cloud-ready con metadatos completos
7. **Upload Cloud**: Deploy directo a Qdrant Cloud con CLI integrado

## 🌐 Para tu Chatbot Web

Una vez en Qdrant Cloud, puedes hacer queries como:

```python
# ¿Qué propone Jara para pensiones?
from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

results = client.search(
    collection_name="political_documents",
    query_vector=embedding("pensiones sistema previsional"),
    query_filter=models.Filter(must=[
        models.FieldCondition(key="candidate", match=models.MatchValue(value="Jeannette Jara")),
        models.FieldCondition(key="topic_category", match=models.MatchValue(value="pensiones"))
    ]),
    limit=5
)

# Cada resultado incluye:
# - result.payload["content"]: Texto original completo
# - result.payload["candidate"]: Candidato extraído dinámicamente  
# - result.payload["page_number"]: Página del documento original
# - result.score: Similitud semántica (0-1)
```

## 🚀 Estado del Proyecto

### ✅ Completado (Sistema RAG Funcional):
- ✅ **Extracción dinámica de candidatos** - No más hardcoding
- ✅ **Contenido real recuperable** - Sin placeholders
- ✅ **OpenAI embeddings** - 1536 dimensiones production-ready
- ✅ **Upload integrado** - CLI comando para Qdrant Cloud
- ✅ **6 candidatos procesados** - Sistema completamente funcional
- ✅ **3,274 chunks** con metadatos políticos completos

### 🔄 Siguiente (Tu Chatbot Web):
1. **Frontend**: React/Vue con interface de chat
2. **Backend**: API que conecte a Qdrant Cloud 
3. **LLM Integration**: OpenAI/Anthropic para generar respuestas contextuales
4. **Deploy**: Vercel/Netlify para el chatbot web

### 📋 Cambios Recientes:
- Migración de Sentence Transformers a OpenAI API
- Extracción dinámica de candidatos (elimina limitaciones hardcoded)
- Almacenamiento de contenido original para recuperación completa
- CLI integrado para upload directo a Qdrant Cloud
- Limpieza de scripts duplicados y archivos legacy


