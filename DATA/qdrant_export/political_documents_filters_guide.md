# Qdrant Search Filters Guide for Political Documents

## Collection Stats
- Total documents: 3274
- Vector dimension: 384
- Candidates: 1
- Parties: 1  
- Topics: 9
- Proposal types: 4

## Available Filter Fields

### Political Filters
- **candidate**: Jeannette Jara
- **party**: Partido Socialista
- **topic_category**: salud, economía, seguridad, general, pensiones, vivienda, medio_ambiente, transporte, educación
- **proposal_type**: propuesta_especifica, descripcion_general, diagnostico, meta_cuantitativa

### Document Structure
- **page_number**: Integer (page number in original document)
- **section_depth**: Integer (0-4, depth of section hierarchy)
- **source_file**: String (original filename)

## Example Qdrant Queries

### 1. Find candidate's pension proposals
```python
results = client.search(
    collection_name="political_documents",
    query_vector=query_embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="candidate", match=models.MatchValue(value="Jeannette Jara")),
            models.FieldCondition(key="topic_category", match=models.MatchValue(value="pensiones"))
        ]
    ),
    limit=5
)
```

### 2. Compare candidates on health policy
```python
results = client.search(
    collection_name="political_documents", 
    query_vector=query_embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="topic_category", match=models.MatchValue(value="salud")),
            models.FieldCondition(key="proposal_type", match=models.MatchValue(value="propuesta_especifica"))
        ]
    ),
    limit=10
)
```

### 3. Find specific page references
```python
results = client.search(
    collection_name="political_documents",
    query_vector=query_embedding, 
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="candidate", match=models.MatchValue(value="Jeannette Jara")),
            models.FieldCondition(key="page_number", range=models.Range(gte=10, lte=20))
        ]
    ),
    limit=5
)
```

### 4. Search by document section depth
```python
# Find main section headers (depth 1-2)
results = client.search(
    collection_name="political_documents",
    query_vector=query_embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="section_depth", range=models.Range(gte=1, lte=2))
        ]
    )
)
```

## Political Analysis Patterns

### Candidate Comparison
1. Search same topic across candidates
2. Filter by proposal_type for comparable content
3. Use page_number for precise citations

### Policy Deep-dive  
1. Filter by topic_category + specific candidate
2. Use section_hierarchy for structured navigation
3. Filter by proposal_type for different content types

### Citation Generation
Use payload fields: candidate, page_number, section_hierarchy for precise citations:
"Según Jeannette Jara (Página 45, Políticas Sociales > Sistema Previsional)"
