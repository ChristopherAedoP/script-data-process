# Fase 1 Detallada: Procesamiento de PDFs → Convex

## PROBLEMA TÉCNICO PRINCIPAL

**Challenge**: ¿Cómo convertir 7 PDFs de 50-200 páginas cada uno en datos que Convex pueda usar para vector search?

**Solución**: Pipeline Python → API de Convex

---

## FLUJO TÉCNICO COMPLETO

### PASO 1: Extracción de Texto (Python)
**Herramienta**: pymupdf4llm
**Input**: `kast_programa.pdf`, `jara_programa.pdf`, etc.
**Output**: Texto estructurado en markdown

**¿Por qué pymupdf4llm?**
- Preserva headers (# ## ###) 
- Mantiene tablas como markdown tables
- Detecta listas automáticamente
- Mejor que PyMuPDF básico para documentos complejos

**¿Qué pasa si un PDF es ilegible?**
- Backup: Tesseract OCR
- Manual: Transcripción de secciones críticas

### PASO 2: Chunking Inteligente (Python)
**Input**: Texto markdown completo
**Output**: Array de chunks con metadata

**Lógica de chunking**:
1. Detectar secciones por headers (#, ##, ###)
2. Dividir cada sección en chunks de 800-1200 tokens
3. Overlap de 200 tokens entre chunks consecutivos
4. Agregar metadata: candidato, sección, página, keywords

**Metadata por chunk**:
```
{
  chunk_id: "kast_economia_03",
  candidate: "José Antonio Kast", 
  section: "Economía",
  subsection: "Política Fiscal",
  content: "texto del chunk...",
  page_number: 15,
  token_count: 1050,
  keywords: ["impuestos", "fiscal"],
  importance_score: 0.85
}
```

### PASO 3: Generar Embeddings (Python + OpenAI)
**Input**: Array de chunks
**Output**: Vector embeddings (1536 dimensiones cada uno)

**Proceso**:
1. Batch de 100 chunks por request (más eficiente)
2. OpenAI text-embedding-3-small API
3. Rate limiting: 3000 RPM máximo
4. Costo estimado: $20 total para 7 PDFs

### PASO 4: Subir a Convex (Python → Convex API)
**Challenge**: ¿Cómo enviar los embeddings desde Python a Convex?

**Solución**: Convex HTTP API

**Flujo**:
1. Python hace HTTP POST a Convex deployment URL
2. Convex function recibe chunks + embeddings
3. Convex almacena en table con vector index automático

---

## INTEGRACIÓN PYTHON → CONVEX

### CONVEX SETUP
**Paso 1**: Crear proyecto Convex
```bash
npx convex init
```

**Paso 2**: Definir schema en `convex/schema.ts`
- Table `chunks` con vector index
- Dimensiones: 1536 (OpenAI embedding size)
- Filter fields: candidate, section

**Paso 3**: Crear función de upload en `convex/uploadChunks.ts`
- Recibe array de chunks via HTTP
- Valida formato
- Inserta en database con vector index

### PYTHON → CONVEX CONNECTION
**Método**: HTTP API calls desde Python a Convex

**Flujo técnico**:
1. Python procesa 1 PDF completamente
2. Genera todos los embeddings
3. HTTP POST batch a Convex function
4. Convex confirma inserción exitosa
5. Python procesa siguiente PDF

**¿Por qué HTTP y no SDK directo?**
- Convex es TypeScript nativo
- Python SDK no existe oficialmente
- HTTP API es simple y confiable

---

## ARQUITECTURA DE DATOS EN CONVEX

### CONVEX COMO "BACKEND ALL-IN-ONE"
**Lo que maneja Convex automáticamente**:
- Database (NoSQL document store)
- Vector indexing (HNSW algorithm)
- API endpoints (auto-generated)
- Real-time subscriptions
- TypeScript type safety

### VECTOR SEARCH NATIVO
**Cómo funciona en Convex**:
1. Define vector index en schema
2. Convex builds HNSW index automáticamente  
3. Query con `ctx.vectorSearch()` 
4. Filtering por metadata (candidate, section)
5. Cosine similarity scoring

### VENTAJAS vs ALTERNATIVES
**vs PostgreSQL + pgvector**:
- Setup: 5 minutos vs 2-3 horas
- Scaling: Automático vs manual
- TypeScript: Nativo vs ORM

**vs Pinecone**:
- Costo: $0 hasta 1GB vs $70/mes
- Integration: Todo en uno vs múltiples servicios

---

## FLUJO DE PROCESAMIENTO COMPLETO

### CRONOLOGÍA TÉCNICA

**Day 1-2: Setup**
1. Setup Convex project
2. Define schema con vector index
3. Create upload function
4. Test con 1 PDF pequeño

**Day 3-4: Python Processing**
1. Script de extracción funcionando
2. Chunking logic validada
3. OpenAI embeddings generándose
4. Test de 1 PDF completo end-to-end

**Day 5-7: Batch Processing**
1. Procesar los 7 PDFs
2. Validar calidad de chunks
3. Vector search testing
4. Performance optimization

### VALIDATION CHECKPOINTS

**Checkpoint 1**: Text Extraction
- ¿Se ve bien el texto extraído?
- ¿Tablas preservadas correctamente?
- ¿Headers detectados?

**Checkpoint 2**: Chunking Quality  
- ¿Chunks mantienen contexto?
- ¿Metadata es precisa?
- ¿No hay duplicación?

**Checkpoint 3**: Vector Search
- ¿Query "pensiones Kast" retorna chunks relevantes?
- ¿Filtering por candidato funciona?
- ¿Resultados hacen sentido?

---

## RIESGOS TÉCNICOS Y MITIGACIONES

### ALTO RIESGO: PDFs Complejos
**Problemas potenciales**:
- Texto en columnas → extracción desordenada
- Tablas complejas → información perdida  
- Gráficos con texto → no detectados
- Headers inconsistentes → chunking malo

**Mitigación**:
- Test manual de extracción de cada PDF
- OCR backup para PDFs problemáticos
- Validación humana de chunks críticos

### MEDIO RIESGO: OpenAI Rate Limits
**Problema**: 3000 RPM límite
**Mitigación**: Batch processing + retry logic

### BAJO RIESGO: Convex Integration
**Problema**: HTTP API fails
**Mitigación**: Local JSON backup + retry

---

## DELIVERABLES FASE 1

### OUTPUTS ESPERADOS
1. **Convex Database**: 500-1000 chunks indexed
2. **Vector Search**: Functioning queries 
3. **Validation Report**: Quality check de cada PDF
4. **Documentation**: Process replicable

### CRITERIOS DE ÉXITO
- ✅ 5/7 PDFs procesados exitosamente
- ✅ Vector search retorna resultados relevantes
- ✅ Metadata permite filtering efectivo
- ✅ Performance <2s para queries simples

**Si falla cualquiera → STOP y debug antes de Fase 2**

---

## ¿ESTÁ CLARO EL FLUJO TÉCNICO?

**Key Points**:
1. **Python separado** para processing (mejor herramientas PDF)
2. **HTTP API** para conectar Python → Convex (simple y confiable)  
3. **Convex maneja todo el backend** (DB + vector search + API)
4. **Validation en cada paso** (no procesar todo y descubrir errores al final)

**Python** (local) → **Procesa PDFs** → **Genera embeddings** → **HTTP POST** → **Convex** (cloud)

## **¿POR QUÉ ESTE APPROACH?**

1. **Python es mejor para PDFs**: pymupdf4llm, chunking, OpenAI APIs
2. **Convex es mejor para backend**: Vector search nativo, TypeScript, APIs automáticas  
3. **HTTP API es simple**: Una vez procesado, no necesitas Python más

## **EL MAYOR RIESGO:**
PDFs políticos son una mierda - tablas complejas, formatos inconsistentes, texto en columnas.

**Solución**: Test de 1 PDF primero, validar que el texto extraído se ve bien antes de procesar los 7.

## **¿ESTÁ CLARO AHORA?**
- ¿Python → HTTP → Convex pipeline?
- ¿Por qué Convex maneja "all-in-one backend"?
- ¿El riesgo de procesamiento de PDFs?

**¿Qué parte necesita más clarificación?**