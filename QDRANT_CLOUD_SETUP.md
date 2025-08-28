# Guía Setup Qdrant Cloud para Chatbot Político

## Paso 1: Crear Cuenta en Qdrant Cloud

1. Ve a https://cloud.qdrant.io/
2. Crear cuenta con email o GitHub
3. Verificar email si es necesario

## Paso 2: Crear Cluster

1. En el dashboard, clic "Create Cluster"
2. Configuración recomendada:
   - **Cluster name**: `political-chatbot`
   - **Region**: Selecciona el más cercano (US East, EU West, etc.)
   - **Plan**: Free tier (1GB RAM, suficiente para 3274 documents)
3. Clic "Create cluster"
4. Esperar 2-3 minutos hasta que esté "Running"

## Paso 3: Obtener Credenciales

1. En tu cluster, ve a "API Keys" tab
2. Clic "Generate API Key"
3. Copia el **API Key** (solo se muestra una vez)
4. Copia la **Cluster URL** (formato: `https://xxx-xxx-xxx.qdrant.tech`)

## Paso 4: Configurar Variables de Entorno

```bash
# Windows Command Prompt
set QDRANT_API_KEY=qdt_your_api_key_here
set QDRANT_URL=https://your-cluster-url.qdrant.tech

# Windows PowerShell
$env:QDRANT_API_KEY="qdt_your_api_key_here"
$env:QDRANT_URL="https://your-cluster-url.qdrant.tech"

# Linux/Mac
export QDRANT_API_KEY=qdt_your_api_key_here
export QDRANT_URL=https://your-cluster-url.qdrant.tech
```

## Paso 5: Instalar Dependencias

```bash
pip install qdrant-client
```

## Paso 6: Subir Datos

```bash
cd data/qdrant_export
python upload_to_qdrant_cloud.py
```

## Paso 7: Verificar Upload

1. Ve al dashboard de Qdrant Cloud
2. Selecciona tu cluster
3. Ve a "Collections" tab
4. Deberías ver `political_documents` con 3274 points

## Paso 8: Test API Connection

```python
from qdrant_client import QdrantClient
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Test connection
collection_info = client.get_collection("political_documents")
print(f"Collection has {collection_info.points_count} points")
```

## Configuración para Web Chatbot

Una vez que tengas los datos en Qdrant Cloud, puedes conectar tu chatbot web:

```python
import openai  # o tu LLM preferido
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class PoliticalChatbot:
    def __init__(self, qdrant_url, qdrant_api_key):
        self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def search_documents(self, query, candidate=None, topic=None, limit=5):
        # Generar embedding de la query
        query_vector = self.encoder.encode(query).tolist()
        
        # Construir filtros
        filters = []
        if candidate:
            filters.append({"key": "candidate", "match": {"value": candidate}})
        if topic:
            filters.append({"key": "topic_category", "match": {"value": topic}})
        
        # Buscar en Qdrant
        results = self.qdrant_client.search(
            collection_name="political_documents",
            query_vector=query_vector,
            query_filter={"must": filters} if filters else None,
            limit=limit
        )
        
        return results
    
    def answer_question(self, question, candidate=None, topic=None):
        # Buscar documentos relevantes
        documents = self.search_documents(question, candidate, topic)
        
        # Construir contexto para LLM
        context = "\n\n".join([
            f"Candidato: {doc.payload['candidate']}\n"
            f"Página: {doc.payload.get('page_number', 'N/A')}\n"
            f"Contenido: {doc.payload['content']}"
            for doc in documents
        ])
        
        # Generar respuesta con LLM
        prompt = f"""
        Basándote en los siguientes documentos de programas políticos, responde la pregunta:
        
        Pregunta: {question}
        
        Documentos:
        {context}
        
        Respuesta (incluye citas con candidato y página):
        """
        
        # Aquí usarías tu LLM preferido (OpenAI, Anthropic, etc.)
        # response = openai.ChatCompletion.create(...)
        
        return prompt  # Por ahora retorna el prompt
```

## Costos y Límites

- **Free Tier**: 1GB RAM, suficiente para ~10K-50K documents
- **Paid Plans**: Desde $25/mes para más capacidad
- **Bandwidth**: Sin límite en free tier para consultas normales

## Troubleshooting

### Error de Conexión
- Verificar API key y URL
- Confirmar que el cluster está "Running"
- Revisar firewall/proxy si aplica

### Batch Upload Failures
- Reducir `batch_size` a 32 o menos
- Revisar formato de los vectores (384 dimensiones)
- Verificar que no hay caracteres especiales problemáticos

### Performance Lenta
- Considerar usar índice HNSW para datasets grandes
- Optimizar los filtros en las queries
- Usar cache local para queries frecuentes