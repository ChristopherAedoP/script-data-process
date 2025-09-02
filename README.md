# Chatbot Político RAG - Sistema de Procesamiento de Documentos Políticos

Sistema RAG (Retrieval-Augmented Generation) especializado para procesar programas políticos de candidatos presidenciales chilenos. Procesamiento file-by-file con logs independientes por candidato y deploy directo a Qdrant Cloud.

## 🚀 Características Principales

- ✅ **DirectProcessor**: Procesamiento file-by-file con persistencia inmediata por candidato
- ✅ **Chunking**: 800 caracteres con overlap 100, merge automático de fragmentos pequeños
- ✅ **Logs independientes**: Estructura de carpetas separada por candidato
- ✅ **Clasificación automática**: 10 categorías temáticas y 4 tipos de propuestas
- ✅ **Embeddings OpenAI**: text-embedding-3-small API (1536 dimensiones)
- ✅ **Upload directo**: Deploy inmediato a Qdrant Cloud desde CLI
- ✅ **Estructura organizacional**: Carpetas individuales por candidato con logs detallados

## 📁 Estructura del Proyecto

```
script-data-process/
├── src/
│   ├── __init__.py
│   ├── config.py              # CHUNK_SIZE=800, CHUNK_OVERLAP=100
│   ├── document_processor.py  # Chunking + merge_small_chunks()
│   ├── embeddings.py         # OpenAI API text-embedding-3-small
│   ├── direct_processor.py   # Procesador file-by-file principal
│   ├── vector_store.py       # FAISS vector store local
│   ├── rag_system.py         # Sistema RAG orchestrator
│   ├── qdrant_exporter.py    # Export a Qdrant Cloud
│   ├── taxonomy.py           # Clasificador taxonomía política
│   └── cli.py               # Interface CLI
├── docs/                    # Documentos políticos (.md)
├── DATA/                    # Datos DirectProcessor
│   └── direct_export/
│       ├── Jose_Antonio_Kast/
│       │   ├── chunks_preview.txt
│       │   ├── processing_log.json
│       │   └── payload.json
│       ├── Johannes_Kaiser/
│       └── session_summary.json
├── data/                    # Datos sistema legacy
│   ├── faiss_index.faiss
│   ├── metadata.json
│   └── qdrant_export/
├── taxonomy.json            # 10 categorías, 43 subcategorías
├── requirements.txt
└── setup.py
```

## 🏗️ Arquitectura RAG Completa

### Flujo de Procesamiento

```
📄 Documentos Políticos (.md)
          ↓
🔧 DirectProcessor (procesamiento file-by-file)
          ├── 🔄 DocumentProcessor (chunking 800 chars, overlap 100)
          ├── 🧠 OpenAI Embeddings (text-embedding-3-small, 1536D)
          ├── ✅ Validación y merge de chunks pequeños
          ├── 💾 Escritura inmediata por candidato
          └── 📝 Logs independientes por candidato
          ↓
📁 Estructura por Candidato (DATA/direct_export/)
          ├── chunks_preview.txt (vista previa chunks)
          ├── processing_log.json (métricas detalladas)
          ├── payload.json (datos para Qdrant)
          └── failed_chunks.json (solo si hay errores)
          ↓
☁️ Upload Directo a Qdrant Cloud
          ↓
🌐 Chatbot Web (@qdrant/js-client-rest)
```

### Estructura de Metadatos

```json
{
  "source_file": "Programa_Jose_Antonio_Kast_R.md",
  "chunk_id": "Programa_Jose_Antonio_Kast_R_0_e4324e8a",
  "chunk_index": 0,
  "candidate": "Jose Antonio Kast R",
  "party": "Partido Republicano",
  "page_number": 1,
  "topic_category": "Institucionalidad", 
  "proposal_type": "propuesta_especifica",
  "taxonomy_path": "Institucionalidad > Probidad",
  "tags": ["institucionalidad", "gobierno"],
  "embedding_metadata": {
    "language": "es",
    "model": "text-embedding-3-small",
    "dimensions": 1536,
    "generated_date": "2025-01-15"
  }
}
```

**Características de la estructura:**
- ✅ **Campos condicionales**: `headers`, `section_hierarchy` (solo si no están vacíos)  
- ✅ **Source file simplificado**: Solo filename, sin path completo
- ✅ **Embedding metadata técnica**: Modelo, dimensiones y lenguaje
- ✅ **Campos críticos para RAG**: `taxonomy_path`, `candidate`, `party`, `tags`

## 🔧 Instalación y Configuración

### 1. Clonar y configurar entorno

```bash
cd chatbot-politico/script-data-process
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt

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

## 🚀 Uso del Sistema

### DirectProcessor (Principal)

```bash
# Procesar documentos file-by-file
python -m src.cli process-direct

# Resultado:
# - Carpeta por candidato en DATA/direct_export/
# - chunks_preview.txt, processing_log.json, payload.json
# - Logs independientes por candidato
# - Upload directo a Qdrant disponible
```

### Sistema Legacy

```bash
# Indexar documentos (sistema original)
python -m src.cli index

# Export y upload
python -m src.cli export-qdrant
python -m src.cli upload-cloud
```

### Paso 3: Implementar Chatbot Web

Una vez los datos están en Qdrant Cloud, puedes implementar consultas desde tu aplicación web:

#### Frontend: Consulta desde JavaScript/TypeScript

```javascript
import { QdrantClient } from '@qdrant/js-client-rest';

// Configuración del cliente
const client = new QdrantClient({
  url: 'https://tu-cluster-url.qdrant.tech',
  apiKey: 'tu_qdrant_api_key_aquí'
});

// Función para consultar políticas específicas
async function consultarPolitica(pregunta, candidato = null, tema = null) {
  // 1. Generar embedding de la pregunta (usando OpenAI API)
  const embedding = await generarEmbedding(pregunta);
  
  // 2. Construir filtros políticos
  const filtros = [];
  if (candidato) {
    filtros.push({
      key: "candidate",
      match: { value: candidato }
    });
  }
  if (tema) {
    filtros.push({
      key: "topic_category", 
      match: { value: tema }
    });
  }

  // 3. Ejecutar búsqueda vectorial con filtros
  const resultados = await client.search('political_documents', {
    vector: embedding,
    filter: filtros.length > 0 ? { must: filtros } : undefined,
    limit: 5,
    with_payload: true
  });

  return resultados.map(result => ({
    contenido: result.payload.content,
    candidato: result.payload.candidate,
    partido: result.payload.party,
    tema: result.payload.topic_category,
    pagina: result.payload.page_number,
    relevancia: result.score,
    taxonomia: result.payload.taxonomy_path
  }));
}

// Ejemplo de uso
async function ejemploConsulta() {
  // Pregunta específica por candidato
  const pensiones = await consultarPolitica(
    "¿Qué propone para el sistema de pensiones?",
    "Jose Antonio Kast R"
  );
  
  // Pregunta temática comparativa
  const salud = await consultarPolitica(
    "reforma del sistema de salud",
    null,
    "Salud"
  );
  
  // Pregunta abierta con taxonomía
  const economia = await consultarPolitica(
    "crecimiento económico e inflación"
  );
  
  return { pensiones, salud, economia };
}
```

#### Backend: API Node.js/Express

```javascript
const express = require('express');
const { QdrantClient } = require('@qdrant/js-client-rest');
const OpenAI = require('openai');

const app = express();
const qdrant = new QdrantClient({
  url: process.env.QDRANT_URL,
  apiKey: process.env.QDRANT_API_KEY
});

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Endpoint para consultas políticas RAG
app.post('/api/consulta-politica', async (req, res) => {
  try {
    const { pregunta, candidato, tema, limite = 5 } = req.body;
    
    // 1. Generar embedding con OpenAI (mismo modelo del procesamiento)
    const response = await openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: pregunta
    });
    const embedding = response.data[0].embedding;
    
    // 2. Construir filtros basados en taxonomía optimizada
    const filtros = [];
    if (candidato) {
      filtros.push({
        key: "candidate",
        match: { value: candidato }
      });
    }
    if (tema) {
      filtros.push({
        key: "topic_category",
        match: { value: tema }
      });
    }
    
    // 3. Buscar en Qdrant con estructura optimizada
    const resultados = await qdrant.search('political_documents', {
      vector: embedding,
      filter: filtros.length > 0 ? { must: filtros } : undefined,
      limit: limite,
      with_payload: true,
      score_threshold: 0.7  // Filtrar resultados poco relevantes
    });
    
    // 4. Formatear respuesta con metadata política
    const respuestaFormateada = resultados.map(result => ({
      contenido: result.payload.content,
      metadata: {
        candidato: result.payload.candidate,
        partido: result.payload.party,
        tema: result.payload.topic_category,
        tipoProuesta: result.payload.proposal_type,
        taxonomia: result.payload.taxonomy_path,
        pagina: result.payload.page_number,
        tags: result.payload.tags
      },
      relevancia: result.score,
      fuente: result.payload.source_file
    }));
    
    // 5. Generar respuesta contextual con LLM
    const contexto = respuestaFormateada.map(r => 
      `**${r.metadata.candidato}** (${r.metadata.partido}): ${r.contenido}`
    ).join('\n\n');
    
    const respuestaIA = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'Eres un asistente político que responde preguntas basándote únicamente en la información proporcionada de programas políticos oficiales.'
        },
        {
          role: 'user', 
          content: `Pregunta: ${pregunta}\n\nInformación de programas políticos:\n${contexto}\n\nPor favor responde basándote únicamente en esta información.`
        }
      ]
    });
    
    res.json({
      pregunta,
      respuesta: respuestaIA.choices[0].message.content,
      fuentes: respuestaFormateada,
      filtros: { candidato, tema }
    });
    
  } catch (error) {
    console.error('Error en consulta política:', error);
    res.status(500).json({ error: 'Error procesando consulta' });
  }
});

app.listen(3000, () => {
  console.log('API RAG Político ejecutándose en puerto 3000');
});
```

#### Frontend: React Component

```jsx
import React, { useState } from 'react';

const ChatbotPolitico = () => {
  const [pregunta, setPregunta] = useState('');
  const [candidato, setCandidato] = useState('');
  const [tema, setTema] = useState('');
  const [respuesta, setRespuesta] = useState(null);
  const [cargando, setCargando] = useState(false);

  const candidatos = [
    'Jose Antonio Kast R',
    'Evelyn Matthei', 
    'Jeannette Jara'
  ];

  const temas = [
    'Pensiones', 'Salud', 'Educación', 'Seguridad',
    'Economía', 'Vivienda', 'Trabajo', 'Medio Ambiente'
  ];

  const consultar = async () => {
    setCargando(true);
    try {
      const response = await fetch('/api/consulta-politica', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pregunta, candidato, tema })
      });
      const data = await response.json();
      setRespuesta(data);
    } catch (error) {
      console.error('Error:', error);
    }
    setCargando(false);
  };

  return (
    <div className="chatbot-politico">
      <h2>Consulta Programas Políticos</h2>
      
      <div className="filtros">
        <select value={candidato} onChange={(e) => setCandidato(e.target.value)}>
          <option value="">Todos los candidatos</option>
          {candidatos.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        
        <select value={tema} onChange={(e) => setTema(e.target.value)}>
          <option value="">Todos los temas</option>
          {temas.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
      
      <div className="consulta">
        <input
          type="text"
          value={pregunta}
          onChange={(e) => setPregunta(e.target.value)}
          placeholder="¿Qué propone para pensiones?"
          className="input-pregunta"
        />
        <button onClick={consultar} disabled={cargando || !pregunta}>
          {cargando ? 'Consultando...' : 'Preguntar'}
        </button>
      </div>
      
      {respuesta && (
        <div className="respuesta">
          <h3>Respuesta</h3>
          <p>{respuesta.respuesta}</p>
          
          <h4>Fuentes ({respuesta.fuentes.length})</h4>
          {respuesta.fuentes.map((fuente, i) => (
            <div key={i} className="fuente">
              <strong>{fuente.metadata.candidato}</strong> 
              ({fuente.metadata.partido}) - 
              Página {fuente.metadata.pagina} - 
              Relevancia: {(fuente.relevancia * 100).toFixed(1)}%
              <p>{fuente.contenido.substring(0, 200)}...</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatbotPolitico;
```

## 📊 Estructura de Datos Optimizada

### Metadatos por Chunk (actual)
```json
{
  "source_file": "Programa_Jose_Antonio_Kast_R.md",
  "chunk_id": "Programa_Jose_Antonio_Kast_R_0_e4324e8a",
  "chunk_index": 0,
  "candidate": "Jose Antonio Kast R",
  "party": "Partido Republicano", 
  "page_number": 1,
  "topic_category": "Institucionalidad",
  "proposal_type": "propuesta_especifica",
  "sub_category": "Probidad",
  "taxonomy_path": "Institucionalidad > Probidad",
  "tags": ["institucionalidad", "gobierno", "probidad"],
  "headers": {
    "Header 1": "LA FUERZA DEL CAMBIO",
    "Header 2": "Bases programáticas"
  },
  "section_hierarchy": [
    "LA FUERZA DEL CAMBIO",
    "Bases programáticas"
  ],
  "embedding_metadata": {
    "language": "es",
    "model": "text-embedding-3-small", 
    "dimensions": 1536,
    "generated_date": "2025-01-15"
  }
}
```

### Características de la Estructura

**Campos Condicionales:**
- `headers`: Solo incluido si no está vacío (56/274 chunks = 20.4%)
- `section_hierarchy`: Solo incluido si no está vacío (56/274 chunks = 20.4%)

**Estructura Web-Optimizada:**
- ✅ `source_file`: Solo filename (no path completo)
- ✅ `embedding_metadata`: Info técnica del modelo
- ✅ Campos críticos para RAG: `taxonomy_path`, `candidate`, `party`, `tags`

## 🧪 Testing y Ejemplos de Consultas

### Comandos CLI Disponibles

```bash
# Ver todos los comandos
python -m src.cli --help

# Comandos principales
python -m src.cli index         # Indexar documentos políticos
python -m src.cli search        # Buscar en índice local  
python -m src.cli stats         # Estadísticas del sistema
python -m src.cli benchmark     # Pruebas de rendimiento
python -m src.cli chat          # Modo chat interactivo
python -m src.cli export-qdrant # Exportar formato web-compatible
python -m src.cli upload-cloud  # Upload directo a Qdrant Cloud
python -m src.cli process-direct # DirectProcessor: file-by-file processing
```

### Consultas de Ejemplo

```bash
# Búsquedas temáticas específicas
python -m src.cli search "pensiones sistema previsional AFP"
python -m src.cli search "salud pública lista de espera"
python -m src.cli search "seguridad ciudadana narcotráfico"
python -m src.cli search "educación gratuidad universitaria"

# Chat interactivo con contexto
python -m src.cli chat
Query: ¿Qué propone Kast para pensiones?
Query: Compara propuestas de salud entre candidatos
Query: /stats  # Ver estadísticas del sistema
Query: /quit   # Salir
```

### Ejemplos de Filtros Qdrant

```python
# Filtro por candidato específico
filter = {
    "must": [
        {"key": "candidate", "match": {"value": "Jose Antonio Kast R"}}
    ]
}

# Filtro por tema y tipo de propuesta
filter = {
    "must": [
        {"key": "topic_category", "match": {"value": "Pensiones"}},
        {"key": "proposal_type", "match": {"value": "propuesta_especifica"}}
    ]
}

# Filtro por taxonomía específica
filter = {
    "must": [
        {"key": "taxonomy_path", "match": {"value": "Pensiones > Sistema de Reparto"}}
    ]
}

# Filtro por página específica (para citas exactas)
filter = {
    "must": [
        {"key": "candidate", "match": {"value": "Evelyn Matthei"}},
        {"key": "page_number", "range": {"gte": 10, "lte": 15}}
    ]
}

# Filtro por tags múltiples
filter = {
    "must": [
        {"key": "tags", "match": {"any": ["pensiones", "seguridad social"]}}
    ]
}
```

## ⚙️ Configuración Avanzada

### Variables de entorno (.env)

```bash
# ⚠️ REQUERIDO: OpenAI API Key
OPENAI_API_KEY=tu_openai_api_key_aquí

# ⚠️ REQUERIDO para Qdrant Cloud:
QDRANT_API_KEY=qdt_tu_api_key_aquí
QDRANT_URL=https://tu-cluster-url.qdrant.tech

# Configuraciones opcionales:
EMBEDDING_MODEL=text-embedding-3-small  # OpenAI model (1536 dims)
CHUNK_SIZE=800                          # Tamaño de chunk
CHUNK_OVERLAP=100                       # Solapamiento entre chunks
MAX_CHUNKS_RETURN=5                     # Resultados por búsqueda
BATCH_SIZE=32                           # Batch size para API calls
```

### Configuración de Taxonomía

El sistema usa `taxonomy.json` con:
- **10 categorías principales**: Pensiones, Salud, Educación, Seguridad, etc.
- **43 subcategorías específicas**: Sistema de Reparto, Lista de Espera, etc.
- **Clasificación automática**: Basada en keywords y contexto
- **Tags dinámicos**: Generados automáticamente por categoría

## 📈 Estado Actual del Sistema

## 📊 Estado Actual

### DirectProcessor 
- José Antonio Kast: 51 chunks procesados, 0 errores
- Johannes Kaiser: Procesado con logs independientes
- Estructura organizada por candidato
- Upload directo a Qdrant Cloud funcional

### Sistema Legacy
- 274 chunks procesados exitosamente  
- Metadata estructurada para RAG web
- Compatible @qdrant/js-client-rest
- 10 categorías taxonomía detectadas

### Comandos Disponibles

```bash
# DirectProcessor (recomendado)
python -m src.cli process-direct

# Sistema Legacy
python -m src.cli index
python -m src.cli benchmark

# Consultas y exports
python -m src.cli search "consulta"
python -m src.cli upload-cloud
```

## 🌐 Arquitectura del Sistema

### Componentes

**DirectProcessor** (`src/direct_processor.py`):
- Procesamiento file-by-file de documentos .md
- Escritura inmediata por candidato
- Logs independientes en DATA/direct_export/
- Upload directo a Qdrant Cloud

**DocumentProcessor** (`src/document_processor.py`):
- Chunking: 800 caracteres, overlap 100
- Merge automático de chunks pequeños (<50 chars)
- Clasificación taxonomía + tipo propuesta
- Extracción metadata candidato/partido

**EmbeddingGenerator** (`src/embeddings.py`):
- OpenAI API text-embedding-3-small
- 1536 dimensiones
- Batch processing (32 chunks)
- Validación robusta de chunks

**Sistema Legacy** (`src/rag_system.py`, `src/qdrant_exporter.py`):
- FAISS vector store local
- Export web-compatible
- Compatible @qdrant/js-client-rest

### Estructura de Datos

**Por candidato** (DirectProcessor):
```
DATA/direct_export/[Candidate_Name]/
├── chunks_preview.txt      # Vista previa chunks
├── processing_log.json     # Métricas detalladas
├── payload.json           # Datos Qdrant
└── failed_chunks.json     # Solo si hay errores
```

**Global** (Sistema Legacy):
```
data/
├── faiss_index.faiss      # Índice vectorial
├── metadata.json          # Metadata estructurada
└── qdrant_export/         # Export web
```

## 🔧 Configuración

### Variables Requeridas
```bash
OPENAI_API_KEY=tu_openai_api_key
QDRANT_API_KEY=tu_qdrant_key    # Para upload-cloud
QDRANT_URL=https://cluster.qdrant.tech
```

### Configuración del Sistema
- CHUNK_SIZE=800 caracteres
- CHUNK_OVERLAP=100 caracteres  
- Modelo: text-embedding-3-small (1536D)
- Batch size: 32 chunks por API call
- Taxonomía: 10 categorías, 43 subcategorías