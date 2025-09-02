# Changelog

## [2025-09-02] - Corrección Preservación de Chunks Pequeños

### 🐛 Fixed

**Problema Crítico: Pérdida de información en chunks pequeños**
- **DirectProcessor**: Eliminaba chunks importantes como títulos de sección ("SALUD", "EDUCACIÓN", "SEGURIDAD") 
- **DocumentProcessor**: Función `merge_small_chunks()` descartaba chunks <50 caracteres que no podían fusionarse
- **Impacto**: Pérdida de títulos de sección fundamentales para navegación y clasificación temática

### 🔧 Changes

**src/document_processor.py**
- `merge_small_chunks()`: Cambiado comportamiento de eliminación a preservación
  - **ANTES**: `print("Warning: Skipping very small chunk...") + continue` (elimina chunk)
  - **DESPUÉS**: `merged_chunks.append(current_chunk)` (preserva chunk)
  - **Justificación**: Títulos de sección son información crítica, no ruido

**src/direct_processor.py**  
- `_validate_chunk()`: Relajada validación de longitud mínima
  - **ANTES**: `len(text.strip()) < 10` rechazaba chunks <10 caracteres
  - **DESPUÉS**: `len(text.strip()) < 1` solo rechaza chunks completamente vacíos
  - **Justificación**: Chunks de 1-9 caracteres pueden contener información válida

### ✅ Testing

**Casos verificados**:
- ✅ Chunk "SALUD SALUD PRESIDENTE 2026" (27 chars) - PRESERVADO
- ✅ Chunk "EDUCACIÓN PARA CHILE" (20 chars) - PRESERVADO  
- ✅ Títulos de sección en páginas independientes - PRESERVADOS
- ✅ Franco Parisi: 784 chunks procesados, 0 errores de validación

### 📊 Results  

**Antes (Problemático)**:
```
Warning: Skipping very small chunk: 'CORAZÓN CORAZÓN PRES...'
Warning: Skipping very small chunk: 'SALUD SALUD PRESIDEN...'
Warning: Skipping very small chunk: 'EDUCACIÓN PARA CHILE...'
# Información crítica eliminada
```

**Después (Corregido)**:
```
Chunk 1 (27 chars): 'SALUD SALUD PRESIDENTE 2026' - PRESERVADO
Chunk 3 (20 chars): 'EDUCACIÓN PARA CHILE' - PRESERVADO
# Toda la información se mantiene
```

### 💡 Philosophy

**Principio aplicado**: KISS (Keep It Simple, Stupid)
- **No casos borde**: No necesidad de detectar qué es título vs contenido
- **Zero data loss**: Preservar toda la información por defecto
- **Menos código**: Eliminación de lógica compleja de filtrado
- **Compatibilidad**: Restaura comportamiento funcional anterior

### 🔄 Compatibility

- **Backward compatible**: No afecta estructura de datos existente
- **Performance**: Neutral (mismo procesamiento, menos eliminaciones)
- **API**: Sin cambios en interfaces públicas
- **Data**: Mejora calidad de datos (más información preservada)