# Plan de Implementación Ejecutable - Chatbot Político MVP

**Documento**: plan-implementacion-chatbot.md  
**Autor**: Claude Code (Desarrollador Fullstack Senior)  
**Fecha**: 27 de Agosto, 2025  
**Proyecto**: Chatbot Análisis Político - MVP  
**Basado en**: PDR Chatbot Político MVP (pdr-chatbot-politico.md)

---

## Resumen Ejecutivo

### Validación del PDR y Approach Técnico

**Conclusión del Análisis**: El PDR presenta una arquitectura sólida y un timeline realista para un MVP funcional en 4 semanas. Las decisiones técnicas están bien fundamentadas y el scope está claramente delimitado.

**Decisiones Arquitectónicas Validadas**:
- ✅ **Stack Tecnológico**: Next.js + Convex + assistant-ui + OpenAI es óptimo para MVP
- ✅ **Timeline**: 4 semanas es realista con enfoque en riesgo crítico (Semana 1)
- ✅ **Scope**: Consultas + comparaciones es apropiado, evita feature creep
- ✅ **Approach**: Python separado para procesamiento + HTTP hacia Convex es pragmático

**Riesgo Crítico Identificado**: Procesamiento de PDFs (Semana 1) - 70% del éxito del proyecto
**Estrategia de Mitigación**: Validación rápida con 1 PDF antes de procesar los 7

---

## Análisis del PDR

### Key Findings y Decisiones Técnicas Validadas

#### 1. Arquitectura All-in-One con Convex
**Funcionalidad Clave**: Backend unificado que combina DB + Vector Search + API + Real-time
**Justificación Técnica**: 
- Elimina 3-4 integraciones separadas (PostgreSQL + Pinecone + Express + WebSockets)
- Setup en minutos vs días de configuración
- TypeScript end-to-end reduce surface de errores
- Vector index automático elimina configuración manual

#### 2. Assistant-ui para Interface de Chat
**Funcionalidad Clave**: Chat UI production-ready con capacidades avanzadas
**Components Críticos**:
- Markdown rendering automático para respuestas estructuradas
- Streaming nativo para UX fluid
- JSON → React components para tablas comparativas
- Multi-IA support para futuras expansiones

#### 3. Procesamiento Inteligente de Documentos
**Funcionalidad Clave**: Extracción + chunking + embedding + storage
**Components Críticos**:
- Semantic chunking (800-1200 tokens, overlap 200)
- Metadata rica (candidato, sección, keywords, importancia)
- Vector embeddings con OpenAI text-embedding-3-small
- Storage optimizado en Convex con índices automáticos

---

## Arquitectura del Sistema

### Diagrama de Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO FINAL                           │
│                   (Ciudadanos Chilenos)                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND LAYER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Next.js 14    │  │  assistant-ui   │  │   shadcn/ui     │  │
│  │   TypeScript    │  │  Chat Interface │  │   Components    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/WebSocket
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CONVEX BACKEND                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Query API     │  │  Vector Search  │  │   Chat API      │  │
│  │   Functions     │  │   Index         │  │   Functions     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Chunks DB     │  │  Conversations  │  │   Metadata      │  │
│  │   Table         │  │   Table         │  │   Indexes       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP API Calls
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OPENAI SERVICES                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Embeddings    │  │    GPT-4o-mini  │  │   Moderation    │  │
│  │   Service       │  │   Chat Service  │  │   Service       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 PROCESAMIENTO OFFLINE                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Python PDF    │  │   Text Cleaning │  │   Chunking      │  │
│  │   Processor     │  │   & Structure   │  │   & Metadata    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de Datos Principal

```
1. INGESTA (Una vez)
   PDFs → [Python Script] → Text Cleaning → Semantic Chunks → 
   OpenAI Embeddings → Convex Storage

2. CONSULTA (Tiempo Real)
   User Query → [Next.js] → Convex Query Function → Vector Search → 
   Context Assembly → OpenAI Chat → [assistant-ui] → User
```

---

## Estructura Completa del Proyecto

### Organización de Carpetas y Archivos

```
chatbot-politico/
├── README.md
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├──
├── convex/                     # Backend Convex
│   ├── _generated/
│   ├── schema.ts              # Definición de tablas
│   ├── queries.ts             # Funciones de consulta
│   ├── mutations.ts           # Funciones de escritura
│   └── chat.ts                # Lógica de chat AI
│
├── scripts/                    # Procesamiento offline
│   ├── process_pdfs.py        # Script principal
│   ├── requirements.txt       # Dependencias Python
│   ├── pdfs/                  # Documentos fuente
│   └── processed/             # Datos procesados
│
├── src/
│   ├── app/                   # Next.js App Router
│   │   ├── layout.tsx         # Layout global
│   │   ├── page.tsx           # Página principal
│   │   └── globals.css        # Estilos globales
│   │
│   ├── components/            # Componentes React
│   │   ├── ui/                # shadcn/ui components
│   │   ├── ChatInterface.tsx  # Interface principal
│   │   └── SourceCitation.tsx # Citas de fuentes
│   │
│   ├── lib/                   # Utilidades
│   │   ├── convex.ts          # Cliente Convex
│   │   └── utils.ts           # Funciones helper
│   │
│   └── types/                 # Definiciones TypeScript
│       └── index.ts
│
├── public/                    # Assets estáticos
└── docs/                     # Documentación
    ├── setup-guide.md
    └── api-documentation.md
```

---

## Casos de Uso Detallados

### UC1: Consulta Específica de Candidato

**Descripción**: Usuario consulta propuesta específica de un candidato sobre un tema particular

**Actor Principal**: Ciudadano chileno  
**Precondiciones**: 
- Sistema tiene datos de candidatos procesados
- Vector search está operativo

**Flujo Principal**:
```
1. Usuario ingresa consulta: "¿Qué propone Kast sobre delincuencia?"
2. Sistema identifica entidades: [candidato=Kast, tema=delincuencia]
3. Sistema expande términos relacionados: [delincuencia, criminalidad, seguridad ciudadana]
4. Vector search filtra por candidato="José Antonio Kast"
5. Sistema selecciona top 3 chunks más relevantes
6. OpenAI genera respuesta estructurada con citas
7. assistant-ui renderiza respuesta con fuentes
```

**Componentes Afectados**:
- **Frontend**: ChatInterface.tsx, SourceCitation.tsx
- **Backend**: convex/queries.ts, convex/chat.ts
- **Servicios**: OpenAI Embeddings, GPT-4o-mini
- **Database**: chunks table con filtro por candidato

**Postcondiciones**:
- Usuario recibe respuesta específica del candidato
- Fuentes citadas con página y sección
- Consulta registrada para analytics

**Criterios de Aceptación**:
- Respuesta en < 3 segundos
- Cita fuentes específicas (página, sección)
- Precisión > 85% en respuestas verificables

---

### UC2: Comparación Multi-Candidato

**Descripción**: Usuario solicita comparación entre propuestas de múltiples candidatos sobre un tema

**Actor Principal**: Ciudadano chileno  
**Precondiciones**:
- Datos de múltiples candidatos disponibles
- Sistema puede procesar consultas paralelas

**Flujo Principal**:
```
1. Usuario ingresa: "Compara las políticas de pensiones de Kast y Jara"
2. Sistema identifica: [candidatos=[Kast, Jara], tema=pensiones]
3. Sistema ejecuta vector search paralelo para cada candidato
4. Sistema ensambla contexto comparativo estructurado
5. OpenAI genera comparación con formato organizado
6. assistant-ui renderiza tabla/estructura comparativa
```

**Componentes Afectados**:
- **Frontend**: ChatInterface.tsx (tabla comparativa), SourceCitation.tsx
- **Backend**: convex/queries.ts (parallel queries), convex/chat.ts
- **Servicios**: OpenAI GPT-4o-mini con prompt comparativo
- **Database**: chunks table con múltiples filtros

**Postcondiciones**:
- Usuario ve propuestas de ambos candidatos
- Diferencias clave resaltadas
- Fuentes específicas para cada candidato

**Criterios de Aceptación**:
- Formato de tabla/estructura clara
- Cubre propuestas de todos los candidatos solicitados
- Identifica similitudes y diferencias específicas

---

### UC3: Análisis Transversal por Tema

**Descripción**: Usuario busca información sobre un tema específico across todos los candidatos

**Actor Principal**: Ciudadano chileno, periodista, analista  
**Precondiciones**:
- Datos completos de todos los candidatos
- Sistema puede hacer búsqueda sin filtro de candidato

**Flujo Principal**:
```
1. Usuario pregunta: "¿Qué candidatos proponen bajar impuestos?"
2. Sistema hace vector search amplio (sin filtro de candidato)
3. Sistema filtra por contenido relacionado con impuestos
4. Sistema agrupa resultados por candidato
5. OpenAI genera resumen estructurado por candidato
6. assistant-ui presenta lista organizada con propuestas
```

**Componentes Afectados**:
- **Frontend**: ChatInterface.tsx (lista estructurada)
- **Backend**: convex/queries.ts (broad search), convex/chat.ts
- **Servicios**: OpenAI GPT-4o-mini con prompt de análisis
- **Database**: chunks table búsqueda completa + agrupación

**Postcondiciones**:
- Usuario ve todos los candidatos relevantes al tema
- Propuestas específicas de cada candidato
- Resumen ejecutivo del tema

**Criterios de Aceptación**:
- Incluye todos los candidatos con propuestas relevantes
- Propuestas específicas, no generalizaciones
- Organización clara por candidato

---

## Flujos de Proceso Críticos

### Flujo 1: Procesamiento de PDFs (Offline - Una vez)

```
INICIO → Descarga PDFs → Validación Formato → Extracción Texto
   ↓
Limpieza y Estructuración → Semantic Chunking → Generación Metadata
   ↓
OpenAI Embeddings → Almacenamiento Convex → Creación Índices → FIN

Puntos Críticos de Validación:
• Post-Extracción: Validar estructura y contenido legible
• Post-Chunking: Verificar contexto preservado
• Post-Embeddings: Test de similarity search
• Post-Storage: Confirmar índices funcionando
```

### Flujo 2: Query Processing (Tiempo Real)

```
User Input → Entity Extraction → Query Expansion → Vector Search
     ↓
Context Assembly → Prompt Engineering → OpenAI API → Response Processing
     ↓
Source Attribution → UI Rendering → User Display → Analytics Log

Puntos Críticos de Performance:
• Vector Search: < 500ms
• OpenAI API: < 2s
• UI Rendering: < 200ms
• Total: < 3s p95
```

### Flujo 3: Error Handling & Recovery

```
Error Detection → Error Classification → Recovery Strategy → User Notification
     ↓
┌─ API Error → Retry Logic → Fallback Response
├─ Search Error → Simplified Query → Partial Results  
├─ Timeout → Cache Lookup → Graceful Degradation
└─ Parse Error → User Clarification → Query Refinement
```

---

## Plan Semanal Funcional

### SEMANA 1: Fundación del Sistema (Procesamiento de Datos)
**Objetivo**: Establecer la base de datos de conocimiento con documentos procesados
**Riesgo Crítico**: Esta semana determina el 70% del éxito del proyecto

#### Día 1 (Lunes): Setup del Ecosistema

**Funcionalidad a Implementar**: Infraestructura base del proyecto
**Componentes Afectados**:
- Convex Backend (configuración inicial)
- Next.js Frontend (estructura base)
- Python Processing Environment

**Tareas Funcionales**:
- Crear proyecto Next.js con TypeScript + Tailwind
- Configurar Convex con schema inicial
- Setup Python environment para procesamiento
- Establecer conexiones y autenticación

**Criterios de Validación Funcional**:
- ✅ Convex dashboard activo y conectado
- ✅ Next.js dev server funcionando
- ✅ Python puede conectar a Convex HTTP API
- ✅ Schema básico deployado sin errores

---

#### Día 2 (Martes): Procesamiento de Documentos - Fase 1

**Funcionalidad a Implementar**: Capacidad de extraer y limpiar texto de PDFs
**Componentes Afectados**:
- Python PDF Processor
- Text Cleaning Pipeline
- Validation Systems

**Tareas Funcionales**:
- Implementar extracción de texto con pymupdf4llm
- Crear pipeline de limpieza y estructuración
- Desarrollar sistema de validación de calidad
- Probar con 1 PDF completo

**Criterios de Validación Funcional**:
- ✅ Extracción preserva estructura (títulos, párrafos)
- ✅ Texto limpio sin caracteres especiales problemáticos
- ✅ Metadata extraída correctamente (página, sección)
- ✅ Validación manual confirma calidad del texto

**Punto Crítico**: Si la extracción falla → STOP y resolver antes de continuar

---

#### Día 3 (Miércoles): Semantic Chunking y Metadata

**Funcionalidad a Implementar**: División inteligente del contenido en chunks semánticamente coherentes
**Componentes Afectados**:
- Chunking Algorithm
- Metadata Generation
- Quality Assessment

**Tareas Funcionales**:
- Implementar chunking con overlapping (800-1200 tokens, 200 overlap)
- Generar metadata rica (candidato, sección, keywords)
- Calcular importance scores para cada chunk
- Validar coherencia semántica

**Criterios de Validación Funcional**:
- ✅ Chunks mantienen contexto semántico completo
- ✅ Overlapping previene pérdida de información
- ✅ Metadata precisa y consistente
- ✅ No chunks truncados o mal formados

---

#### Día 4 (Jueves): Embeddings y Vector Storage

**Funcionalidad a Implementar**: Transformación de texto a vectores y almacenamiento optimizado
**Componentes Afectados**:
- OpenAI Embeddings Service
- Convex Vector Storage
- Vector Index System

**Tareas Funcionales**:
- Integrar OpenAI text-embedding-3-small
- Batch processing para eficiencia de costos
- Almacenar embeddings en Convex con metadata
- Crear vector index para similarity search

**Criterios de Validación Funcional**:
- ✅ Embeddings se generan correctamente
- ✅ Vector index responde a queries básicas
- ✅ Similarity search retorna resultados relevantes
- ✅ Costo de embeddings dentro del presupuesto ($20 max)

---

#### Día 5 (Viernes): Testing y Validación del Pipeline

**Funcionalidad a Implementar**: Validación completa del sistema de procesamiento
**Componentes Afectados**:
- Entire Processing Pipeline
- Quality Assurance Systems
- Performance Monitoring

**Tareas Funcionales**:
- Procesar los 7 PDFs completos
- Ejecutar tests de calidad end-to-end
- Validar vector search con queries reales
- Documentar issues y resolverlos

**Criterios de Validación Funcional**:
- ✅ 5/7 PDFs procesados exitosamente (mínimo)
- ✅ Vector search encuentra contenido relevante
- ✅ Performance de queries < 500ms
- ✅ No errores críticos en el pipeline

**Go/No-Go Decision**: Si <5 PDFs funcionan → evaluar continuar o replantear

---

### SEMANA 2: Motor de Consultas (Backend Intelligence)
**Objetivo**: Desarrollar la inteligencia de consultas y respuestas del sistema

#### Día 8 (Lunes): Convex Query Functions

**Funcionalidad a Implementar**: Sistema de búsqueda vectorial optimizado
**Componentes Afectados**:
- Convex Query Functions
- Vector Search Logic
- Context Assembly System

**Tareas Funcionales**:
- Desarrollar functions para vector similarity search
- Implementar filtros por candidato, sección, tema
- Crear sistema de ranking y reranking
- Optimizar performance de queries

#### Día 9 (Martes): Entity Recognition y Query Processing

**Funcionalidad a Implementar**: Comprensión inteligente de consultas de usuario
**Componentes Afectados**:
- Query Processing Pipeline
- Entity Extraction
- Term Expansion System

**Tareas Funcionales**:
- Implementar extracción de entidades (candidatos, temas)
- Crear sistema de expansión de términos
- Desarrollar lógica de contextualización
- Testing con variaciones de queries

#### Día 10 (Miércoles): Context Assembly y Prompt Engineering

**Funcionalidad a Implementar**: Ensamblaje inteligente de contexto para IA
**Componentes Afectados**:
- Context Assembly Engine
- Prompt Engineering System
- Token Management

**Tareas Funcionales**:
- Desarrollar algoritmo de selección de chunks
- Crear templates de prompts optimizados
- Implementar manejo de límites de tokens
- Testing de calidad de respuestas

#### Día 11 (Jueves): OpenAI Integration y Response Generation

**Funcionalidad a Implementar**: Generación de respuestas inteligentes con citas
**Componentes Afectados**:
- OpenAI Chat Integration
- Response Processing
- Source Attribution

**Tareas Funcionales**:
- Integrar GPT-4o-mini con prompts optimizados
- Implementar sistema de citación de fuentes
- Crear lógica de fallback para errores
- Optimizar costos de API

#### Día 12 (Viernes): Testing End-to-End del Backend

**Funcionalidad a Implementar**: Validación completa del motor de consultas
**Componentes Afectados**:
- Complete Backend System
- Quality Assurance
- Performance Monitoring

**Tareas Funcionales**:
- Testing con 50+ consultas diversas
- Validar precisión de respuestas
- Medir performance end-to-end
- Documentar casos edge

---

### SEMANA 3: Interfaz de Usuario (Frontend Experience)
**Objetivo**: Crear la experiencia de usuario moderna y accesible

#### Día 15 (Lunes): Setup Frontend con assistant-ui

**Funcionalidad a Implementar**: Interface base de chat moderna
**Componentes Afectados**:
- Next.js App Structure
- assistant-ui Integration
- Base UI Components

#### Día 16 (Martes): Chat Interface y UX Flow

**Funcionalidad a Implementar**: Flujo conversacional intuitivo
**Componentes Afectados**:
- ChatInterface Component
- Message Handling
- User Input Processing

#### Día 17 (Miércoles): Rendering y Visualización

**Funcionalidad a Implementar**: Presentación rica de respuestas (markdown, tablas)
**Componentes Afectados**:
- Response Rendering Engine
- Markdown Parser
- Table/List Components

#### Día 18 (Jueves): Responsive Design y Accessibility

**Funcionalidad a Implementar**: Experiencia optimizada para todos los dispositivos
**Componentes Afectados**:
- Responsive Layout
- Mobile Optimization
- Accessibility Features

#### Día 19 (Viernes): Integration Testing Frontend-Backend

**Funcionalidad a Implementar**: Sistema completo funcionando end-to-end
**Componentes Afectados**:
- Complete System
- Integration Points
- User Experience Flow

---

### SEMANA 4: Validación y Despliegue (Production Readiness)
**Objetivo**: Preparar y lanzar el MVP con validación de usuarios reales

#### Día 22 (Lunes): User Testing y Feedback

**Funcionalidad a Implementar**: Validación con usuarios reales
**Componentes Afectados**:
- Complete User Experience
- Feedback Collection
- Issue Identification

#### Día 23 (Martes): Performance Optimization

**Funcionalidad a Implementar**: Optimización basada en metrics reales
**Componentes Afectados**:
- Performance Bottlenecks
- Caching Strategy
- API Optimization

#### Día 24 (Miércoles): Production Deployment

**Funcionalidad a Implementar**: Sistema live en producción
**Componentes Afectados**:
- Vercel Deployment
- Convex Production Environment
- Domain Configuration

#### Día 25 (Jueves): Monitoring y Analytics

**Funcionalidad a Implementar**: Observabilidad del sistema en producción
**Componentes Afectados**:
- Error Monitoring
- Performance Tracking
- Usage Analytics

#### Día 26 (Viernes): Documentation y Handoff

**Funcionalidad a Implementar**: Documentación completa para mantenimiento
**Componentes Afectados**:
- Technical Documentation
- User Guides
- Maintenance Procedures

---

## Componentes y Responsabilidades del Sistema

### Componente 1: Python PDF Processor
**Responsabilidad Principal**: Transformar documentos PDFs en datos estructurados
**Funciones Específicas**:
- Extracción de texto preservando estructura semántica
- Limpieza y normalización de contenido
- Generación de metadata contextual
- Validación de calidad de datos extraídos

**Dependencias**:
- pymupdf4llm (extracción)
- OpenAI API (embeddings)
- Convex HTTP API (storage)

**Inputs**: 7 PDFs de programas presidenciales
**Outputs**: Chunks estructurados con embeddings en Convex DB

---

### Componente 2: Convex Backend Engine
**Responsabilidad Principal**: Core del sistema - storage, search y API
**Funciones Específicas**:
- Vector similarity search con filtros contextuales
- Context assembly para consultas complejas
- Real-time data management
- API functions para frontend

**Dependencias**:
- Convex platform (managed service)
- OpenAI Chat API (response generation)

**Inputs**: User queries, vector search requests
**Outputs**: Contextual responses con source attribution

---

### Componente 3: Next.js Frontend Application
**Responsabilidad Principal**: User interface y experience management
**Funciones Específicas**:
- Chat interface moderna con assistant-ui
- Real-time communication con Convex
- Responsive design para todos los devices
- Accessibility compliance

**Dependencias**:
- assistant-ui (chat components)
- Convex client (real-time data)
- shadcn/ui (UI components)

**Inputs**: User interactions, Convex responses
**Outputs**: Rich formatted responses, user interface

---

## Scripts de Validación y Testing

### Script 1: Validación de Procesamiento de PDFs
```bash
# Propósito: Verificar que el procesamiento de PDFs está funcionando correctamente
# Uso: Ejecutar después de procesar cada PDF
# Criterios de Éxito: Extracción limpia, chunks coherentes, metadata completa

Pasos de Validación:
1. Verificar estructura de texto extraído
2. Validar coherencia semántica de chunks  
3. Confirmar metadata precisos (candidato, sección, página)
4. Test de similarity search con queries conocidas
5. Verificar embeddings generados correctamente
```

### Script 2: Testing de Query Performance
```bash
# Propósito: Validar performance y precisión del sistema de consultas
# Uso: Testing continuo durante desarrollo y post-deployment
# Criterios de Éxito: <3s response time, >85% accuracy, fuentes citadas

Test Cases:
1. Consultas específicas por candidato (20 queries)
2. Comparaciones multi-candidato (15 queries) 
3. Análisis transversales por tema (10 queries)
4. Edge cases y queries ambiguas (10 queries)
5. Performance bajo carga (stress testing)
```

### Script 3: End-to-End System Validation
```bash
# Propósito: Validar funcionamiento completo del sistema
# Uso: Pre-deployment y post-deployment
# Criterios de Éxito: Flujo completo funcionando sin errores

Validation Flow:
1. User input → Query processing ✅
2. Vector search → Context retrieval ✅  
3. AI response → Source attribution ✅
4. UI rendering → User display ✅
5. Analytics logging → Data collection ✅
```

---

## Contingency Plans y Risk Mitigation

### Contingency 1: PDFs Ilegibles o Mal Estructurados
**Probabilidad**: Media (40%) | **Impacto**: Alto

**Scenario**: Algunos PDFs tienen formato complejo o están mal digitalizados
**Detection**: Texto extraído con caracteres raros, chunks sin sentido, estructura perdida

**Mitigation Strategy**:
- **Plan A**: OCR con Tesseract para PDFs problemáticos
- **Plan B**: Procesamiento manual + transcripción de secciones críticas  
- **Plan C**: Reducir scope a PDFs de mejor calidad (mínimo 5/7)
- **Rollback**: Volver a métodos de extracción más simples

**Implementation Time**: 2-3 días adicionales
**Success Criteria**: Al menos 5/7 PDFs procesados con calidad acceptable

---

### Contingency 2: Respuestas de IA Imprecisas o Alucinadas
**Probabilidad**: Alta (70%) | **Impacto**: Medio

**Scenario**: OpenAI genera respuestas que no están basadas en los documentos
**Detection**: Respuestas sin fuentes, información contradictoria, hechos no verificables

**Mitigation Strategy**:
- **Plan A**: Prompt engineering más restrictivo + validation layers
- **Plan B**: Post-processing para verificar citas y fuentes
- **Plan C**: Confidence scoring + "No tengo información" responses
- **Rollback**: Templates de respuestas más estructurados y conservadores  

**Implementation Time**: 1-2 días de refinamiento
**Success Criteria**: >85% respuestas tienen fuentes verificables

---

### Contingency 3: Performance Issues (Slow Response Times)
**Probabilidad**: Media (50%) | **Impacto**: Medio

**Scenario**: Sistema responde >5 segundos, poor user experience
**Detection**: Performance monitoring, user complaints, timeout errors

**Mitigation Strategy**:
- **Plan A**: Optimización de vector search + caching strategies
- **Plan B**: Query pre-processing para reducir complexity
- **Plan C**: Batch processing + async responses con loading states
- **Rollback**: Simplificar queries y reducir context size

**Implementation Time**: 2-3 días de optimización
**Success Criteria**: <3s p95 response time

---

### Contingency 4: Costos de API Excesivos
**Probabilidad**: Baja (25%) | **Impacto**: Medio

**Scenario**: Costos de OpenAI exceden budget de $200 para desarrollo
**Detection**: Daily cost monitoring, API usage alerts

**Mitigation Strategy**:
- **Plan A**: Query caching para reducir API calls repetidas
- **Plan B**: Rate limiting por usuario + query throttling
- **Plan C**: Batch processing para embeddings, query optimization
- **Rollback**: Usar modelos más baratos (GPT-3.5-turbo) temporalmente

**Implementation Time**: 1 día de optimización
**Success Criteria**: <$200 total development cost, <$50/month running

---

## Criterios de Éxito por Fase

### Fase 1: Procesamiento de Datos (Semana 1)
**Criterios Técnicos**:
- ✅ 5/7 PDFs procesados exitosamente (mínimo critical)
- ✅ 500-1000 chunks generados con metadata rica
- ✅ Vector similarity search functional
- ✅ <500ms query response time

**Criterios de Negocio**:
- ✅ Texto extraído mantiene coherencia semántica
- ✅ Metadata permite filtros precisos (candidato, tema)
- ✅ Sample queries retornan resultados relevantes
- ✅ Costo de embeddings <$20 total

**Go/No-Go Criteria**: Si <5 PDFs procesados → evaluar continuar vs rediseñar approach

---

### Fase 2: Backend Intelligence (Semana 2) 
**Criterios Técnicos**:
- ✅ Query API responde en <2s p95
- ✅ Context assembly mantiene relevancia >90%
- ✅ OpenAI integration estable sin timeouts
- ✅ Source attribution preciso en todas las respuestas

**Criterios de Negocio**:
- ✅ Respuestas específicas a consultas por candidato
- ✅ Comparaciones multi-candidato estructuradas
- ✅ Análisis transversales por tema funcionales  
- ✅ >85% precision en 50 test queries

**Success Metrics**:
- Response accuracy (manual validation): >85%
- Query coverage (non-"no sé" responses): >90%
- Source citation rate: 100%
- API cost per query: <$0.05

---

### Fase 3: Frontend Experience (Semana 3)
**Criterios Técnicos**:
- ✅ assistant-ui integration fluida sin bugs
- ✅ Real-time communication con Convex stable
- ✅ Responsive design funcional en mobile/desktop
- ✅ Accessibility compliance (WCAG basic)

**Criterios de Negocio**:
- ✅ Chat interface intuitiva para usuarios no-técnicos
- ✅ Markdown rendering limpio para respuestas complejas
- ✅ Loading states claros durante processing
- ✅ Error messages user-friendly

**Success Metrics**:
- Page load time: <2s
- Time to first response: <3s
- Mobile usability score: >90
- Accessibility score: >85

---

### Fase 4: Production Readiness (Semana 4)
**Criterios Técnicos**:
- ✅ Deployment en Vercel/Convex sin downtime
- ✅ Monitoring y error tracking operational
- ✅ Performance benchmarks meet SLA
- ✅ Security basics implemented

**Criterios de Negocio**:
- ✅ 10+ real users tested successfully
- ✅ Feedback score >4/5 promedio
- ✅ Common user journeys work end-to-end
- ✅ Documentation completa para maintenance

**Success Metrics**:
- User retention (>1 query): >60%
- Average satisfaction score: >4.0/5.0
- Critical bug count: 0
- Documentation completeness: 100%

---

## Registro de Decisiones Técnicas

### Decisión 1: Convex vs PostgreSQL + Pinecone
**Fecha**: Análisis PDR  
**Contexto**: Backend architecture para MVP de 4 semanas
**Opciones Evaluadas**: Convex all-in-one vs stack tradicional separado

**Decisión Final**: Convex all-in-one
**Justificación**:
- **Time-to-Market**: Setup en minutos vs días de configuración
- **Complexity Reduction**: 1 servicio vs 3+ integraciones separadas
- **TypeScript Native**: End-to-end type safety sin configuración
- **Vector Search Incluido**: No necesita Pinecone separado
- **MVP Appropriate**: Plan gratuito cubre necesidades del MVP

**Trade-offs Aceptados**:
- Vendor lock-in con Convex (vs open-source alternatives)
- Menos control granular sobre performance tuning
- Learning curve para nuevo framework

**Validation**: PDR confirma que beneficios superan risks para MVP

---

### Decisión 2: assistant-ui vs Custom Chat Implementation
**Fecha**: Análisis PDR  
**Contexto**: Frontend chat interface para usuarios no-técnicos
**Opciones Evaluadas**: assistant-ui vs desarrollo custom

**Decisión Final**: assistant-ui
**Justificación**:
- **Production Ready**: Maneja edge cases que custom implementation tomaría semanas
- **Rich Formatting**: Markdown + tables automáticos para respuestas complejas
- **Streaming Support**: UX fluida para respuestas largas
- **Multi-AI Ready**: Future-proof para expansiones
- **Accessibility**: Built-in accessibility features

**Trade-offs Aceptados**:
- Dependencia de librería third-party
- Menor customización visual vs implementación custom
- Bundle size adicional

**Validation**: Análisis costo-beneficio favorece speed-to-market

---

### Decisión 3: Python Separado vs JavaScript/TypeScript para PDF Processing
**Fecha**: Análisis PDR  
**Contexto**: Procesamiento de PDFs complejos con estructura variable
**Opciones Evaluadas**: Python ecosystem vs mantener todo en TypeScript

**Decisión Final**: Python separado con HTTP API hacia Convex
**Justificación**:
- **PDF Libraries**: pymupdf4llm y ecosystem Python más maduro
- **Data Processing**: Pandas y NumPy para manipulation de datos
- **Flexibility**: Easier para agregar OCR, ML processing futures  
- **Separation of Concerns**: Processing offline vs real-time queries

**Trade-offs Aceptados**:
- 2 lenguajes en el stack vs 1 lenguaje unified
- HTTP communication overhead (mínimo para batch processing)
- Deployment complexity adicional

**Validation**: Riesgo técnico del PDF processing justifica usar best tools

---

### Decisión 4: GPT-4o-mini vs GPT-4 vs Modelos Open Source
**Fecha**: Análisis PDR  
**Contexto**: Balance costo-calidad para respuestas de consultas políticas
**Opciones Evaluadas**: OpenAI GPT-4o-mini vs GPT-4 vs Llama/Claude alternatives

**Decisión Final**: OpenAI GPT-4o-mini
**Justificación**:
- **Cost Efficiency**: $0.15/1K tokens vs $30/1K tokens de GPT-4
- **Quality Sufficient**: Para MVP, calidad suficiente con prompting adecuado
- **Reliability**: API madura y estable vs open-source deployment complexity
- **Speed**: Faster response times vs GPT-4 full

**Trade-offs Aceptados**:
- Menor reasoning capability vs GPT-4 (mitigable con mejor prompting)
- Vendor lock-in con OpenAI
- Potential bias in political analysis (mitigable con source-based responses)

**Validation**: Cost analysis y timeline constraints favorecen esta opción

---

## Métricas de Éxito Finales

### Métricas Técnicas del Sistema
- **Response Time**: <3 segundos p95 para end-to-end queries
- **Accuracy Rate**: >85% respuestas útiles (validación manual)
- **Coverage Rate**: >90% queries tienen respuesta (no "no sé")
- **Availability**: >99% uptime durante período de testing
- **Error Rate**: <1% queries fallan por errores técnicos

### Métricas de Negocio/UX
- **User Retention**: >60% usuarios hacen más de 1 pregunta
- **Query Success**: >90% usuarios obtienen respuesta satisfactoria
- **Satisfaction Score**: >4/5 estrellas promedio en feedback
- **Usability**: Usuarios no-técnicos completan tareas sin ayuda
- **Accessibility**: Interface usable por personas mayores

### Métricas de Costo y Efficiency  
- **Development Cost**: <$200 total para MVP completo
- **Running Cost**: <$50/mes con 1000 usuarios/mes proyectados
- **Cost per Query**: <$0.05 promedio (embeddings + chat)
- **Development Time**: MVP funcional en 4 semanas calendario

### Métricas de Calidad de Datos
- **PDF Processing Success**: 5/7 PDFs mínimo procesados correctamente
- **Chunk Quality**: >90% chunks mantienen coherencia semántica  
- **Source Attribution**: 100% respuestas incluyen citas específicas
- **Metadata Accuracy**: >95% metadata (candidato, sección) correctos

---

**DOCUMENTO PLAN DE IMPLEMENTACIÓN COMPLETADO**

**Resumen del Documento**:
✅ Análisis completo del PDR con validación de decisiones técnicas  
✅ Arquitectura del sistema con diagramas ASCII y flujos de datos  
✅ Casos de uso detallados con componentes afectados específicos  
✅ Plan semanal funcional con 26 días de tareas estructuradas  
✅ Scripts de validación y criterios de éxito measurables  
✅ Contingency plans para todos los riesgos identificados  
✅ Registro de decisiones técnicas con justificaciones  
✅ Métricas de éxito por fase y finales del MVP

Este documento sirve como guía completa de implementación, respaldo oficial del plan de desarrollo, y herramienta de tracking de progreso para el equipo.
