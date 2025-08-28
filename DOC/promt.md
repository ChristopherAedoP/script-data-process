# Prompt para Claude Code - Análisis PDR Chatbot Político

## 1. Contexto de la tarea

Eres un asistente de codificacion y debes tomar el **ROL DE DESARROLLADOR FULLSTACK SENIOR** especializado en Next.js, Python, Convex y sistemas de AI. Tu tarea es analizar un documento PDR (Preliminary Design Review) y generar un plan de implementación ejecutable completo para un chatbot de análisis político.

**OUTPUT REQUERIDO**: Debes crear un archivo markdown completo llamado `plan-implementacion-chatbot.md` que sirva como documento de respaldo y registro oficial del plan de desarrollo que propones.

## 2. Contexto del tono

Adopta un enfoque técnico y pragmático, enfocándote en la implementación práctica. Sé directo y específico en tus recomendaciones. Prioriza soluciones que minimicen riesgos y maximicen la probabilidad de éxito del MVP en el timeline establecido.

## 3. Datos de contexto, documentos e imágenes

**DOCUMENTO PRINCIPAL**: `pdr-chatbot-politico.md`

**CONTEXTO TÉCNICO**:
- Stack: Next.js 14 + Convex + assistant-ui + OpenAI
- Timeline: 4 semanas para MVP
- Scope: Procesamiento de 7 PDFs → embeddings → chat interface
- Usuario objetivo: Público general (incluyendo personas mayores)

**MCP**: usa los MCP (Model Context Protocol) instalados como referencias para obtener informacion y ayuda para la resolucion de problemas, consultar ultimas versiones de librerias y ejemplos de uso, buenas practicas.

**ARQUITECTURA DECIDIDA**:
- Frontend: Next.js + assistant-ui
- Backend: Convex (all-in-one)
- AI: OpenAI embeddings + GPT-4o-mini
- Processing: Python script separado

## 4. Descripción detallada de la tarea y reglas

**TAREA PRINCIPAL**: 
Analiza el PDR completo y genera un plan de implementación ejecutable que incluya:

**REGLAS OBLIGATORIAS**:
1. Respeta el stack tecnológico ya definido (no sugieras alternativas)
2. Mantén el timeline ordenado
3. Prioriza el mayor riesgo técnico: procesamiento de PDFs
4. Genera tareas específicas y ejecutables, no conceptos generales
5. Incluye comandos exactos, nombres de archivos, y estructura de carpetas
6. Considera que el desarrollador es competente pero no experto en estas tecnologías específicas

**ENFOQUE**:
- Semana 1 es crítica (procesamiento PDFs)
- Validación en cada paso antes de continuar
- Approach iterativo: probar con 1 PDF antes que con 7

## 5. Ejemplos

**EJEMPLO DE OUTPUT ESPERADO**:
```
## Semana 1, Día 1: Setup Convex
### Tareas específicas:
1. `npx create-next-app@latest chatbot-politico --typescript --tailwind --app`
2. `cd chatbot-politico && npx convex init`
3. Crear archivo `convex/schema.ts` con definición exacta de tabla chunks
4. Test de deployment: `npx convex deploy`

### Criterios de validación:
- Convex dashboard muestra proyecto activo
- Schema deployed sin errores
- Vector index creado automáticamente
```

## 6. Historial de la conversación

**CONTEXTO PREVIO**:
- Se analizaron múltiples opciones de stack tecnológico
- Se decidió por Convex por simplicidad y speed-to-market
- Se identificó procesamiento de PDFs como mayor riesgo técnico
- Se estableció approach de Python separado para processing
- Se validó que assistant-ui es la mejor opción para chat UI

**DECISIONES YA TOMADAS**:
- NO cambiar stack tecnológico
- NO agregar login/auth en MVP
- NO usar PostgreSQL o Pinecone
- SÍ usar approach HTTP entre Python y Convex

## 7. Descripción inmediata de la tarea o solicitud

**TAREA PRINCIPAL**: Analiza el archivo `pdr-chatbot-politico.md` línea por línea y **GENERA UN ARCHIVO MARKDOWN COMPLETO** llamado `plan-implementacion-chatbot.md` que transforme el PDR conceptual en un plan de implementación ejecutable.

**ARCHIVO DE OUTPUT REQUERIDO**: `plan-implementacion-chatbot.md`

**PROPÓSITO DEL ARCHIVO**:
- Documento oficial de planificación del proyecto
- Respaldo técnico de todas las decisiones de implementación  
- Registro detallado que el equipo pueda seguir paso a paso
- Referencia para tracking de progreso y validaciones

**ENTREGABLES REQUERIDOS EN EL ARCHIVO**:

1. **Plan semanal detallado** con tareas diarias específicas
2. **Comandos exactos** para cada setup
3. **Estructura de archivos** completa del proyecto
4. **Checkpoints de validación** con criterios claros de éxito/falla
5. **Scripts de testing** para validar cada fase
6. **Contingency plans** para los riesgos identificados
7. **Registro de decisiones técnicas** y justificaciones

## 8. Pensar paso a paso / respira hondo

Antes de responder:
1. Lee completamente el PDR
2. Identifica las dependencias entre tareas
3. Prioriza según riesgo técnico
4. Valida que cada tarea sea ejecutable sin ambigüedad
5. Asegúrate que el timeline sea realista
6. Considera puntos de falla y rollback plans

## 9. Formato de salida

**ARCHIVO MARKDOWN REQUERIDO**: `plan-implementacion-chatbot.md`

**ESTRUCTURA EXACTA DEL ARCHIVO**:
```markdown
# Plan de Implementación Ejecutable - Chatbot Político MVP
**Documento**: plan-implementacion-chatbot.md  
**Autor**: Claude Code (Desarrollador Fullstack Senior)  
**Fecha**: [Fecha actual]  
**Proyecto**: Chatbot Análisis Político - MVP  

## Resumen Ejecutivo
[Validación del PDR y approach técnico]

## Análisis del PDR
[Key findings y decisiones técnicas validadas]

## Estructura Completa del Proyecto  
[Carpetas, archivos, y organización exacta]

## Semana 1: [Titulo y objetivos]
### Día 1: [Fecha] - [Tareas específicas con comandos]
### Día 2: [Fecha] - [Tareas específicas con comandos]  
### Día 3: [Fecha] - [Tareas específicas con comandos]
...

## Semana 2: [Titulo y objetivos]
### Día 8: [Fecha] - [Tareas específicas con comandos]
...

## Scripts de Validación y Testing
[Tests específicos copy-paste ready]

## Contingency Plans y Risk Mitigation
[Qué hacer si falla cada riesgo mayor]

## Comandos de Setup Completos  
[Todos los comandos organizados por categoría]

## Registro de Decisiones Técnicas
[Justificación de cada decisión importante]

## Criterios de Éxito por Fase
[Métricas claras para validar progreso]
```

## 10. Respuesta pre-rellenada (si existe)

No existe respuesta previa. Genera el plan completo desde cero basándote únicamente en el análisis del PDR proporcionado.

---

**INSTRUCCIÓN FINAL**: 

Asume el **ROL DE DESARROLLADOR FULLSTACK SENIOR** y analiza completamente el archivo `pdr-chatbot-politico.md`. Luego **GENERA EL ARCHIVO COMPLETO** `plan-implementacion-chatbot.md` siguiendo exactamente la estructura y reglas definidas arriba.

**IMPORTANTE**: El archivo debe ser un documento técnico profesional que sirva como:
- Guía de implementación paso a paso
- Respaldo oficial del plan de desarrollo  
- Registro de decisiones técnicas
- Herramienta de tracking de progreso

**El archivo debe estar listo para ser guardado como `plan-implementacion-chatbot.md` y usado inmediatamente por el equipo de desarrollo.**