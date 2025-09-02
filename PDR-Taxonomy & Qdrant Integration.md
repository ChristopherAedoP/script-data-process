

Mejoras **clave para diseñar un buen sistema de consulta con IA**: primero definir el set de **preguntas representativas** de lo que un ciudadano promedio realmente quiere saber de los programas de gobierno.

Voy a proponerte un **stack de 30 preguntas**, agrupadas por grandes áreas de interés ciudadano en Chile (basado en encuestas de opinión, debates nacionales y reclamos frecuentes de la clase media). La idea es que cada pregunta sea **lo bastante clara, pero abierta**, para poder mapear respuestas desde las propuestas de los candidatos y luego aplicar chunking + embeddings.

---

## 📋 Set de 30 preguntas básicas/avanzadas para Chile 2025

### 1. Pensiones y Seguridad Social

1. ¿Qué propone el candidato respecto al sistema de pensiones (AFP / reparto / mixto)?
2. ¿Aumentará la pensión básica universal o algún pilar solidario?
3. ¿Cómo se financiarán los cambios al sistema previsional?

### 2. Salud

4. ¿Qué pasará con las listas de espera en hospitales y clínicas?
5. ¿Cuál es el plan para Fonasa e Isapres, habrá un sistema único o mixto?
6. ¿Se aumentará la inversión en salud pública (consultorios, hospitales, especialistas)?

### 3. Educación

7. ¿Qué propone en educación escolar: calidad, financiamiento y acceso equitativo?
8. ¿Habrá gratuidad total o cambios en educación superior?
9. ¿Cómo se abordará la brecha en educación técnica/profesional?

### 4. Trabajo y Salarios

10. ¿Cuál es la propuesta respecto al salario mínimo?
11. ¿Habrá incentivos o regulaciones para reducir la informalidad laboral?
12. ¿Qué se plantea sobre reducción de jornada laboral (40 → 36 horas, etc.)?

### 5. Economía y Costo de la Vida

13. ¿Qué hará el candidato para enfrentar la inflación y el alto costo de la vida?
14. ¿Habrá políticas para apoyar a la clase media endeudada (créditos, CAE, retail)?
15. ¿Qué se propone respecto al crecimiento económico y atracción de inversiones?

### 6. Seguridad y Crimen Organizado

16. ¿Qué medidas tomará contra el narcotráfico y crimen organizado?
17. ¿Cuál es el plan para Carabineros y la reforma policial?
18. ¿Habrá políticas de seguridad barrial y prevención del delito cotidiano?

### 7. Vivienda y Ciudad

19. ¿Qué se plantea para reducir el déficit habitacional y acceso a vivienda propia?
20. ¿Cómo enfrentará los problemas de arriendos caros y campamentos?
21. ¿Habrá planificación para transporte público, infraestructura urbana y metro?

### 8. Medioambiente y Energía

22. ¿Cuál es la propuesta frente a la crisis hídrica y el acceso al agua?
23. ¿Qué plantea sobre energías renovables, litio e hidrógeno verde?
24. ¿Cómo se abordará la contaminación en ciudades como Santiago, Quintero y Temuco?

### 9. Descentralización y Regiones

25. ¿Qué propone para fortalecer a los gobiernos regionales y municipios?
26. ¿Cómo se impulsará el desarrollo en regiones extremas (Norte/Sur)?
27. ¿Se implementarán beneficios diferenciados para zonas aisladas o rurales?

### 10. Institucionalidad y Política

28. ¿Cuál es la postura sobre una nueva Constitución o reformas al actual texto?
29. ¿Qué plantea sobre probidad, transparencia y financiamiento de la política?
30. ¿Qué hará para reducir la desigualdad social y la percepción de abusos en Chile?

---

## ✅ Observaciones clave

* Son **preguntas transversales**: cualquier ciudadano chileno se las hace, independiente de ideología.
* Cubren **polémicas actuales**: AFP, Isapres, seguridad, costo de la vida, vivienda, crimen organizado.
* Te permiten luego **clasificar y chunkear** programas en dimensiones claras (salud, educación, seguridad, economía, etc.).
* Son **reutilizables**: puedes usarlas tanto para extracción directa de propuestas como para comparar candidatos con una misma pregunta base.

---

👉 Te propongo un paso siguiente: tomar este stack y transformarlo en un **árbol de categorías (taxonomy)** para que tu sistema pueda etiquetar automáticamente fragmentos de los programas:  archivo de referencia (`taxonomy.json`) 

---

Perfecto 👌 lo de la **taxonomy** es justamente la clave para que tu sistema no se convierta en un buscador “plano” que solo tira párrafos, sino en algo que **organiza y clasifica** los programas de gobierno de forma consistente.

---

## 🔹 ¿Qué es una *taxonomy* en este contexto?

Es una **estructura jerárquica de categorías y subcategorías** que representa los temas de interés ciudadano.

* **Categoría** = un tema grande (ej: Salud).
* **Subcategorías** = aspectos específicos dentro de ese tema (ej: Isapres, Fonasa, listas de espera).

Esto te sirve para:

1. **Clasificar** fragmentos de texto de los programas (chunks) en una categoría clara.
2. **Comparar candidatos** de manera justa (“qué dice cada uno sobre Isapres”, no en general sobre salud).
3. **Optimizar embeddings** porque en lugar de buscar en todo el documento, puedes buscar primero en la categoría relevante → resultados más precisos, menos ruido.

---

## 🔹 Ejemplo de Taxonomy para programas presidenciales en Chile 2025

### 1. Pensiones y Seguridad Social

* Reforma al sistema de pensiones (AFP / reparto / mixto)
* Pensión básica universal
* Financiamiento del sistema previsional

### 2. Salud

* Reducción de listas de espera
* Reforma a Fonasa
* Futuro de las Isapres
* Inversión en salud pública (consultorios, hospitales)
* Acceso a especialistas y medicamentos

### 3. Educación

* Educación escolar: calidad, financiamiento, equidad
* Educación superior: gratuidad, créditos (CAE)
* Educación técnico-profesional
* Digitalización y tecnología educativa

### 4. Trabajo y Salarios

* Salario mínimo
* Jornada laboral (40 → 36 horas, etc.)
* Informalidad laboral
* Derechos laborales y sindicales

### 5. Economía y Costo de Vida

* Inflación y costo de la vida
* Endeudamiento de la clase media (retail, créditos, CAE)
* Crecimiento económico e inversión
* Política fiscal e impuestos

### 6. Seguridad y Crimen Organizado

* Narcotráfico y crimen organizado
* Reforma a Carabineros / policía
* Seguridad barrial y prevención del delito
* Control de armas y fronteras

### 7. Vivienda y Ciudad

* Déficit habitacional
* Campamentos y viviendas sociales
* Arriendos y mercado inmobiliario
* Transporte público y metro
* Planificación urbana

### 8. Medioambiente y Energía

* Crisis hídrica y acceso al agua
* Energías renovables y transición energética
* Litio e hidrógeno verde
* Contaminación y zonas de sacrificio

### 9. Descentralización y Regiones

* Fortalecimiento de gobiernos regionales
* Desarrollo en regiones extremas (Norte/Sur)
* Zonas aisladas y rurales
* Equidad territorial

### 10. Institucionalidad y Política

* Nueva Constitución / reformas
* Probidad y transparencia
* Financiamiento de la política
* Participación ciudadana
* Reducción de la desigualdad social

---

## 🔹 Cómo usar la taxonomy en tu proyecto

1. **Chunking inteligente**

   * Cortas los programas en fragmentos (ej: 200–400 tokens).
   * A cada chunk le asignas la categoría más probable de la taxonomy.

2. **Embeddings con contexto**

   * En lugar de almacenar solo el texto del chunk → guardas también su categoría.
   * Ejemplo: `{"texto": "...", "categoría": "Salud → Isapres"}`

3. **Consultas ciudadanas**

   * El usuario pregunta: *“¿Qué proponen sobre las Isapres?”*.
   * El sistema primero filtra embeddings en la categoría “Salud → Isapres”.
   * Luego responde con chunks relevantes, comparando candidatos.

4. **Comparación automática entre candidatos**

   * Puedes generar vistas:

     * “Candidato A vs B en Pensiones”
     * “Qué dicen todos sobre Educación Técnico-profesional”

---

👉 Con esta taxonomy ya puedes diseñar el **pipeline RAG** para tu app.
 **esquema del flujo**: Programas → Chunking → Taxonomy → Embeddings,  para que tengas la arquitectura clara.


---

Perfecto, revisé tu script (`document_processor.py`) y está bien armado para un **MVP de RAG**, pero si lo quieres alinear con lo que hablamos de **taxonomy**, aquí van recomendaciones y mejoras (sin modificar código, solo sugerencias de diseño y uso):

---

## 🔹 Observaciones de tu script actual

1. **Clasificación temática**

   * Ya tienes una función `classify_topic_from_headers` que usa *keywords* en headers → pero está limitado a un set corto (pensiones, salud, educación, economía, seguridad, vivienda, transporte, medio ambiente).
   * Problema: muchos programas usan títulos distintos, o incluyen temas mezclados (ej: “Protección social” puede hablar de pensiones y salud al mismo tiempo).

2. **Tipo de propuesta**

   * La función `detect_proposal_type` diferencia entre *propuesta específica, meta cuantitativa, diagnóstico, descripción general*.
   * Esto es muy útil, pero se queda en un nivel **superficial** y no conecta con la taxonomy que definimos (ej: "Isapres" o "CAEs" no se detectan directamente).

3. **Metadatos políticos**

   * Tus chunks ya guardan: candidato, partido, página, sección, tipo de propuesta, topic\_category.
   * Falta: **subcategoría** (nivel 2 de la taxonomy) y quizá un campo `taxonomy_path` que guarde jerárquicamente (ej: `"Salud > Isapres"`).

---

### 1. Expande el **diccionario de clasificación temática**

* Ahora tienes solo 8 categorías → debes alinearlas con las **10 macroáreas de la taxonomy** que definimos (Pensiones, Salud, Educación, Trabajo, Economía, Seguridad, Vivienda, Medioambiente, Regiones, Institucionalidad).
* Ejemplo de keywords extra:

  * **Pensiones**: AFP, retiro, cotización, jubilación.
  * **Seguridad**: narcotráfico, crimen organizado, carabineros.
  * **Medioambiente**: agua, sequía, litio, hidrógeno verde.

### 2. Agregar **subcategorías automáticas** (nivel 2 taxonomy)

* Puedes crear un segundo diccionario de *keywords → subcategoría*.
* Ejemplo en Salud:

  * “isapre”, “seguro privado” → `sub_category = "Isapres"`
  * “lista de espera”, “operación”, “atención” → `sub_category = "Listas de espera"`
* Esto lo puedes asignar como un nuevo campo: `taxonomy_path = "Salud > Isapres"`.

### 3. Normalizar con un **árbol de taxonomy**

* Define un JSON estático con la taxonomy completa (categorías y subcategorías).
* Así garantizas que todos los programas se clasifiquen en el mismo marco.
* Ejemplo de estructura:

  ```json
  {
    "Salud": {
      "Isapres": ["isapre", "seguro privado"],
      "Fonasa": ["fonasa", "seguro público"],
      "Listas de espera": ["lista de espera", "cirugía", "operación"]
    },
    "Pensiones": {
      "AFP": ["afp", "administradora de fondos"],
      "Pensión básica universal": ["pensión básica", "universal"]
    }
  }
  ```

### 4. Guardar `taxonomy_path` en metadatos

* Ejemplo de chunk enriquecido:

  ```json
  {
    "candidate": "X",
    "party": "Y",
    "topic_category": "Salud",
    "sub_category": "Isapres",
    "taxonomy_path": "Salud > Isapres",
    "proposal_type": "propuesta_especifica",
    "section_hierarchy": ["Capítulo 2", "Salud y Bienestar"]
  }
  ```

### 5. Uso en la fase de consulta

* Cuando un usuario pregunte: *“Qué propone cada candidato sobre Isapres”* →

  * Tu pipeline filtra embeddings por `taxonomy_path = "Salud > Isapres"`.
  * Esto evita confusiones con otros temas de salud (ej: listas de espera).

---

## 🔹 Beneficios de integrar taxonomy en tu pipeline

✅ Mejor precisión al responder preguntas ciudadanas.
✅ Comparación directa entre candidatos en subtemas concretos.
✅ Menos “ruido” en embeddings porque los chunks ya vienen clasificados.
✅ Estandarización: todos los programas se analizan bajo el mismo esquema.

---

vi tu payload (`payload.json`) y efectivamente es el objeto que terminas subiendo a **Qdrant**. Está bien estructurado, pero pensando en lo que hablamos de **taxonomy + consultas más precisas**, sí se puede mejorar bastante.

---

## 🔹 Cómo está tu payload hoy

Ejemplo actual:

```json
{
   "source_file": "...Programa_Johannes_Kaiser.md",
   "chunk_id": "Programa_Johannes_Kaiser_1995_6af12ef5",
   "chunk_index": 1995,
   "headers": {
      "Header 2": "PILAR 1: DESARROLLO DE LA AUTONOMÍA EN LA PERSONA"
   },
   "char_count": 508,
   "candidate": "Johannes Kaiser",
   "page_number": 95,
   "topic_category": "general",
   "proposal_type": "descripcion_general",
   "section_hierarchy": [
      "PILAR 1: DESARROLLO DE LA AUTONOMÍA EN LA PERSONA"
   ],
   "content": "Las personas en Chile prefieren obedecer...",
   "content_preview": "Las personas en Chile prefieren obedecer...",
   "has_page_number": true,
   "section_depth": 1
}
```

Problema principal:

* `topic_category` es muy general.
* Falta **taxonomy\_path**, subcategoría y etiquetas normalizadas para consultas más finas.

---

## 🔹 Cómo quedaría con mejoras de taxonomy

Ejemplo enriquecido:

```json
{
   "source_file": "...Programa_Johannes_Kaiser.md",
   "chunk_id": "Programa_Johannes_Kaiser_1995_6af12ef5",
   "chunk_index": 1995,
   "headers": {
      "Header 2": "PILAR 1: DESARROLLO DE LA AUTONOMÍA EN LA PERSONA"
   },
   "char_count": 508,
   "candidate": "Johannes Kaiser",
   "party": null,
   "page_number": 95,
   "topic_category": "Educación",
   "sub_category": "Formación ciudadana",
   "taxonomy_path": "Educación > Formación ciudadana",
   "proposal_type": "descripcion_general",
   "section_hierarchy": [
      "PILAR 1: DESARROLLO DE LA AUTONOMÍA EN LA PERSONA"
   ],
   "content": "Las personas en Chile prefieren obedecer...",
   "content_preview": "Las personas en Chile prefieren obedecer...",
   "has_page_number": true,
   "section_depth": 1,
   "embedding_metadata": {
      "language": "es",
      "tokens": 120,
      "version": "v1"
   }
}
```

---

## 🔹 Cambios clave que recomiendo

1. **Agregar `sub_category` y `taxonomy_path`**

   * Así puedes filtrar directo en queries: `taxonomy_path = "Salud > Isapres"`.

2. **Normalizar partidos** (cuando los tengas).

   * Hoy está en `None`. Mejor tener un valor uniforme (ej: `"Partido Republicano"`, `"Independiente"`).

3. **Enriquecer `embedding_metadata`**

   * Guardar idioma, cantidad de tokens, versión de procesamiento → útil para depuración y mejoras futuras.

4. **Content Preview optimizado**

   * Hoy repite el inicio del texto. Mejor un *summary corto automático* (ej: primeras 20 palabras limpias).

5. **Etiquetas adicionales (tags)**

   * Por ejemplo: `["salud", "isapres", "privado", "reforma"]`.
   * Estas se pueden usar en Qdrant para búsquedas híbridas (texto + tags).

---

## 🔹 Beneficio de estos cambios

* Cuando un usuario pregunte *“qué proponen los candidatos sobre Isapres”*, no dependes solo del embedding.
* Puedes **filtrar en Qdrant primero** por `taxonomy_path: "Salud > Isapres"` y luego hacer similarity search.
* Resultado: **más precisión, menos ruido**.

---

Te armo un **PDR (Product Design Requirement)** dividido en dos partes:

1. **Requerimientos de mejoras para el script de procesamiento**
2. **Definición del payload estándar para Qdrant**

---

# 📑 PDR – Taxonomy & Qdrant Integration

## 1. Requerimientos para el script de procesamiento

### 1.1. Clasificación temática (Taxonomy)

* El sistema debe soportar una **taxonomy jerárquica** de al menos 2 niveles:

  * Nivel 1: Categoría (ej: Salud, Educación, Pensiones).
  * Nivel 2: Subcategoría (ej: Salud > Isapres, Educación > Técnico-profesional).
* Se debe mantener un archivo de referencia (`taxonomy.json`) con la estructura y keywords por subcategoría.
* El script debe detectar **topic\_category** y **sub\_category** en base a headers y contenido.

### 1.2. Metadata enriquecida

* Cada chunk debe generar metadatos con los siguientes campos mínimos:

  * `candidate` (string, requerido)
  * `party` (string, requerido, valor `"Independiente"` si no se detecta)
  * `page_number` (int, opcional)
  * `proposal_type` (enum: `propuesta_especifica`, `meta_cuantitativa`, `diagnostico`, `descripcion_general`)
  * `topic_category` (string, requerido)
  * `sub_category` (string, opcional)
  * `taxonomy_path` (string concatenado, ej: `"Salud > Isapres"`)
  * `section_hierarchy` (lista de strings con títulos detectados)

### 1.3. Manejo de embeddings

* Cada chunk debe incluir un campo de metadatos `embedding_metadata`:

  * `language`: `"es"`
  * `tokens`: int (estimación del tamaño del chunk)
  * `version`: string (versión del pipeline, ej: `"v1.0-taxonomy"`)

### 1.4. Normalización de contenido

* `content_preview` debe generarse con las primeras 20 palabras del chunk, **sin cortar a la mitad de una palabra**.
* Se deben eliminar caracteres no deseados (ej: saltos de línea duplicados).

### 1.5. Trazabilidad

* El `chunk_id` debe incluir:

  * Nombre del archivo base
  * Índice
  * Hash de contenido (8 dígitos)

---

## 2. Payload estándar para Qdrant

Cada **vector** insertado en Qdrant debe contener:

```json
{
  "id": "Programa_Johannes_Kaiser_1995_6af12ef5",
  "vector": [/* embedding array */],
  "payload": {
    "source_file": "Programa_Johannes_Kaiser.md",
    "chunk_index": 1995,
    "candidate": "Johannes Kaiser",
    "party": "Independiente",
    "page_number": 95,
    "topic_category": "Educación",
    "sub_category": "Formación ciudadana",
    "taxonomy_path": "Educación > Formación ciudadana",
    "proposal_type": "descripcion_general",
    "section_hierarchy": [
      "PILAR 1: DESARROLLO DE LA AUTONOMÍA EN LA PERSONA"
    ],
    "content": "Las personas en Chile prefieren obedecer que decidir por sí mismos...",
    "content_preview": "Las personas en Chile prefieren obedecer que decidir por sí mismos...",
    "char_count": 508,
    "section_depth": 1,
    "embedding_metadata": {
      "language": "es",
      "tokens": 120,
      "version": "v1.0-taxonomy"
    },
    "tags": ["educación", "autonomía", "ciudadanía"]
  }
}
```

---

## 3. Beneficios del nuevo diseño

✅ **Consultas más precisas**: se puede filtrar por `taxonomy_path` antes de similarity search.
✅ **Estandarización**: todos los programas se indexan bajo la misma estructura.
✅ **Comparación automática**: permite preguntar *“qué proponen todos los candidatos sobre Isapres”* y obtener chunks exactos.
✅ **Trazabilidad total**: cada chunk se puede rastrear a su archivo, página y sección.
✅ **Escalabilidad**: la taxonomy puede crecer sin romper el pipeline.

---

👉 Con esto tendrías la **especificación oficial** para implementar mejoras al script y al payload en Qdrant.

