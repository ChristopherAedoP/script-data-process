# PDR: Chatbot Político MVP
## Preliminary Design Review

**Proyecto**: Sistema de consulta inteligente sobre programas presidenciales chilenos  
**Fecha**: Agosto 2025  
**Objetivo**: MVP funcional en 3-4 semanas  

---

## 1. RESUMEN EJECUTIVO

### Problema a Resolver
Los ciudadanos no pueden acceder fácilmente a información específica de los programas presidenciales. Los documentos son largos (50-200 páginas), técnicos y difíciles de comparar entre candidatos.

### Solución Propuesta
Chatbot inteligente que permite:
- Consultar propuestas específicas: *"¿Qué propone Kast sobre pensiones?"*
- Comparar candidatos: *"Compara las políticas económicas de Kast y Jara"*
- Análisis como científico político con respuestas comprensibles

### Success Metrics MVP
- Procesar 7+ programas presidenciales exitosamente
- Responder consultas específicas con >85% precisión
- Comparaciones multi-candidato funcionales
- Interfaz usable para cualquier persona (abuelas included)

---

## 2. ARQUITECTURA TÉCNICA

### Stack Tecnológico Final
```
Frontend: Next.js 14 + TypeScript + assistant-ui
Backend: Convex (all-in-one: DB + API + Vector Search)
Embeddings: OpenAI text-embedding-3-small
Chat: OpenAI GPT-4o-mini
UI Components: assistant-ui + shadcn/ui
Deployment: Vercel (frontend) + Convex (backend)
```

### Decisiones Arquitectónicas Clave

**¿Por qué Convex?**
- All-in-one: Database + Vector Search + API + Real-time
- Setup en minutos, no días
- TypeScript nativo end-to-end
- Vector search incluido sin configuración
- Plan gratuito generoso (1GB vector storage)

**¿Por qué assistant-ui?**
- Chat AI production-ready out-of-the-box
- Markdown + tablas automáticas
- JSON → React components
- Streaming nativo
- Multi-IA support

**¿Por qué OpenAI?**
- Embeddings: $20 total para procesar todos los PDFs
- GPT-4o-mini: Balance costo/calidad ($0.15/1K tokens)
- APIs maduras y confiables

---

## 3. FLUJO DE DATOS Y PROCESAMIENTO

### Fase 1: Procesamiento de PDFs (Una vez)

```
7 PDFs → PyMuPDF → Text Cleaning → Semantic Chunking → OpenAI Embeddings → Convex DB
```

**Detalles técnicos**:
- **Text Extraction**: pymupdf4llm para mantener estructura
- **Chunking**: 800-1200 tokens por chunk, overlap 200 tokens
- **Metadata**: candidato, sección, página, keywords, importancia
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Storage**: Convex con vector index automático

### Fase 2: Consulta en Tiempo Real

```
User Query → Convex Vector Search → Context Assembly → OpenAI Chat → assistant-ui Rendering
```

**Detalles técnicos**:
- **Query Processing**: Embedding de la consulta del usuario
- **Vector Search**: Convex native vector search (cosine similarity)
- **Context Assembly**: Top 5 chunks relevantes, máximo 3000 tokens
- **AI Generation**: OpenAI GPT-4o-mini con prompt optimizado
- **UI Rendering**: assistant-ui con markdown/tablas automáticas

---

## 4. SCHEMA DE DATOS

### Convex Schema

```typescript
export default defineSchema({
  // Chunks de texto con embeddings
  chunks: defineTable({
    candidate: v.string(),        // "José Antonio Kast"
    section: v.string(),          // "Economía", "Seguridad", etc.
    subsection: v.optional(v.string()), // "Política Fiscal"
    content: v.string(),          // Texto del chunk
    page_number: v.number(),      // Página original
    token_count: v.number(),      // Número de tokens
    keywords: v.array(v.string()), // ["pensiones", "AFP"]
    importance_score: v.number(), // 0.0 - 1.0
    document_title: v.string(),   // "Programa Presidencial 2025"
  }).vectorIndex("by_content", {
    vectorField: "embedding",
    dimensions: 1536,
    filterFields: ["candidate", "section"]
  }),

  // Conversaciones para analytics (opcional)
  conversations: defineTable({
    query: v.string(),
    response: v.string(),
    sources: v.array(v.string()),
    response_time_ms: v.number(),
    created_at: v.number(),
  })
});
```

---

## 5. CASOS DE USO PRINCIPALES

### UC1: Consulta Específica de Candidato
**Input**: *"¿Qué propone Kast sobre delincuencia?"*

**Flujo**:
1. Extract entities: [Kast, delincuencia]
2. Vector search filtered by candidate="Kast"
3. Expand terms: [delincuencia, criminalidad, seguridad ciudadana]
4. Return top 3 chunks + metadata
5. Generate response with sources

**Expected Output**: 
- Propuesta específica de Kast sobre delincuencia
- Citas: "Basado en programa de Kast, página 23, sección Seguridad"

### UC2: Comparación Multi-Candidato
**Input**: *"Compara las políticas de pensiones de Kast y Jara"*

**Flujo**:
1. Extract entities: [Kast, Jara, pensiones]
2. Parallel vector search for each candidate
3. Assemble comparative context
4. Generate structured comparison

**Expected Output**:
```
Propuesta de Kast:
- [específicos de Kast]

Propuesta de Jara:
- [específicos de Jara]

Principales diferencias:
- [análisis comparativo]
```

### UC3: Análisis General
**Input**: *"¿Qué candidatos proponen bajar impuestos?"*

**Flujo**:
1. Broad vector search across all candidates
2. Filter by tax-related content
3. Cross-candidate analysis
4. Structured summary

**Expected Output**: Lista de candidatos con sus propuestas fiscales específicas

---

## 6. IMPLEMENTACIÓN POR FASES

### Semana 1: Procesamiento de Documentos
**Objetivos**:
- Script de procesamiento de PDFs funcionando
- 7 programas presidenciales procesados y en Convex
- Vector search básico validado

**Entregables**:
- `process_pdfs.py` script
- Convex schema implementado
- ~500-1000 chunks en base de datos
- Test queries funcionando

**Riesgos**:
- PDFs mal estructurados o ilegibles
- Chunking que pierda contexto importante

### Semana 2: Backend de Consultas
**Objetivos**:
- API de consultas en Convex funcionando
- Integración con OpenAI Chat
- Respuestas básicas a consultas específicas

**Entregables**:
- Convex functions para search y chat
- Prompt engineering optimizado
- Testing con 20+ consultas tipo

**Riesgos**:
- Respuestas alucinadas o imprecisas
- Context assembly subóptimo

### Semana 3: Frontend con assistant-ui
**Objetivos**:
- Interfaz de chat moderna y responsive
- Integración con Convex backend
- Markdown rendering funcionando

**Entregables**:
- Next.js app con assistant-ui
- Chat funcional end-to-end
- Mobile-friendly design

**Riesgos**:
- Problemas de integración Convex + assistant-ui
- Performance issues con markdown largo

### Semana 4: Testing y Refinamiento
**Objetivos**:
- Testing con usuarios reales
- Optimización de respuestas
- Deploy en producción

**Entregables**:
- URL pública funcionando
- Feedback documentado de 10+ testers
- Performance optimizado

**Riesgos**:
- Bugs críticos en producción
- Costos de API más altos de lo esperado

---

## 7. CONSIDERACIONES TÉCNICAS CRÍTICAS

### Procesamiento de PDFs - Mayor Riesgo Técnico
**Challenge**: PDFs políticos tienen formatos inconsistentes, tablas complejas, gráficos

**Mitigation**:
- Usar pymupdf4llm que preserva estructura mejor que PyMuPDF básico
- Validación manual del texto extraído de cada PDF
- Backup plan: OCR con Tesseract para PDFs problemáticos

### Context Assembly - Crítico para Calidad
**Challenge**: Mantener contexto sin sobrepasar límites de tokens

**Strategy**:
- Chunks con overlap de 200 tokens
- Metadata rica para filtrado inteligente
- Reranking de resultados por relevancia

### Prompt Engineering - Key para Precisión
**Strategy**:
```
System: Eres un analista político chileno experto. 
Responde SOLO basándote en el contexto proporcionado.
Si no tienes información específica, di "No tengo información sobre eso en los programas analizados".

Context: [chunks relevantes con metadata]

User: [consulta específica]

Instructions: 
1. Respuesta clara y concisa
2. Cita fuentes específicas
3. Si es comparación, usa estructura organizada
```

---

## 8. MÉTRICAS DE ÉXITO

### Técnicas
- **Response Time**: <3 segundos p95
- **Accuracy**: >85% respuestas útiles (validadas manualmente)
- **Coverage**: >90% consultas tienen respuesta (no "no sé")
- **Uptime**: >99% durante testing

### Negocio/UX
- **User Retention**: >60% hacen más de 1 pregunta
- **Query Success**: >90% obtienen respuesta satisfactoria
- **Feedback Score**: >4/5 estrellas promedio

### Costo
- **Total MVP**: <$200 para desarrollo completo
- **Running Cost**: <$50/mes con 1000 usuarios/mes
- **Cost per Query**: <$0.05 promedio

---

## 9. RIESGOS Y MITIGACIONES

### Alto Riesgo: PDFs Ilegibles
**Probability**: Media | **Impact**: Alto
**Mitigation**: 
- Test de extracción antes de procesar todos
- OCR backup para PDFs problemáticos
- Validación manual chunk por chunk

### Medio Riesgo: Respuestas Imprecisas
**Probability**: Alta | **Impact**: Medio
**Mitigation**:
- Prompt engineering iterativo
- Testing extensivo con consultores políticos
- Confidence scoring en respuestas

### Bajo Riesgo: Costos de API
**Probability**: Baja | **Impact**: Medio
**Mitigation**:
- Cache agresivo de consultas similares
- Rate limiting por usuario
- Monitoring de costos diario

---

## 10. NEXT STEPS INMEDIATOS

### Esta Semana
1. **Setup Convex project** - 2 horas
2. **Download y organizar 7 PDFs** - 3 horas
3. **Script básico de extracción** - 8 horas
4. **Test de 1 PDF completo** - 4 horas

### Criterios de Go/No-Go para continuar
- ✅ Al menos 5/7 PDFs se procesan correctamente
- ✅ Vector search retorna resultados relevantes
- ✅ Convex integration funciona sin issues

**Si alguno falla → STOP y resolver antes de continuar**

---

## 11. CONCLUSIÓN

Este MVP tiene **alta probabilidad de éxito** porque:

1. **Stack probado**: Convex + assistant-ui son production-ready
2. **Scope claro**: Solo consultas y comparaciones, no features extras
3. **Timeline realista**: 4 semanas con buffer para issues
4. **Riesgo manageable**: Mayor riesgo (PDFs) es testeable rápido

**Decisión**: ✅ **PROCEDER CON MVP**

El mayor valor está en resolver bien el procesamiento de PDFs en Semana 1. Si eso funciona, el resto del sistema tiene alta probabilidad de éxito.

**Next Action**: Configurar Convex y empezar con procesamiento de 1 PDF de prueba.

**PDR COMPLETO LISTO.**

**TL;DR del PDR**:

🎯 **MVP Objetivo**: Chatbot que responde preguntas sobre 7+ programas presidenciales chilenos

🏗️ **Stack Final**: 
- Next.js + assistant-ui (frontend)
- Convex (backend all-in-one)
- OpenAI (embeddings + chat)

⚡ **Timeline**: 4 semanas
- Semana 1: Procesar PDFs → embeddings
- Semana 2: API de consultas funcionando  
- Semana 3: Frontend con chat
- Semana 4: Testing + deploy

🔥 **Riesgo #1**: PDFs mal estructurados (mitigación: test rápido primera semana)


**¿Aprobado para proceder? ¿Algún punto del PDR necesita ajuste antes de empezar?**