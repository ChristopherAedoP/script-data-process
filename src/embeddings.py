"""
Embeddings module for RAG MVP
Handles text embedding generation using OpenAI API
"""
import os
import time
from typing import List, Optional
import numpy as np
from openai import OpenAI # Importar el cliente de OpenAI
import logging

from .config import config

# Configurar logger
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings using OpenAI API"""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Inicializa el generador de embeddings.
        
        Args:
            model_name (str, optional): Nombre del modelo de OpenAI. 
                                      Por defecto es 'text-embedding-3-small' (1536 dims).
        """
        # Usar text-embedding-3-small por defecto, que genera 1536 dims
        self.model_name = model_name or "text-embedding-3-small" 
        # Obtener la clave API del entorno
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required.")
        self.client = OpenAI(api_key=api_key) # Inicializar cliente
        self.embedding_dim = 1536 # Dimensión fija para text-embedding-3-small
        
    def encode_texts(self, texts: List[str], batch_size: Optional[int] = None, show_progress: bool = True) -> np.ndarray:
        """
        Codifica una lista de textos en embeddings usando la API de OpenAI.
        
        Args:
            texts (List[str]): Lista de textos a codificar.
            batch_size (int, optional): Tamaño del lote para las llamadas a la API. 
                                      Por defecto, usa el valor de config.BATCH_SIZE.
            show_progress (bool): Si se muestra el progreso del procesamiento.
        
        Returns:
            np.ndarray: Array de NumPy con los embeddings generados (shape: len(texts) x 1536).
        
        Raises:
            Exception: Si ocurre un error durante la generación de embeddings.
        """
        if not texts:
            return np.array([])
            
        batch_size = batch_size or config.BATCH_SIZE
        all_embeddings = []
        
        logger.info(f"Generating {self.model_name} embeddings (1536 dims) for {len(texts)} texts...")
        print(f"Generating {self.model_name} embeddings (1536 dims) for {len(texts)} texts...")
        start_time = time.time()
        
        # Procesar en lotes
        total_batches = (len(texts) + batch_size - 1) // batch_size
        for i in range(0, len(texts), batch_size):
            batch_num = i // batch_size + 1
            batch = texts[i:i + batch_size]
            try:
                # Llamar a la API de OpenAI
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model_name
                    # Nota: text-embedding-3-small por defecto genera 1536 dims
                    # Si quisieramos cambiar la dimensión, añadiríamos:
                    # dimensions=1024 # (solo para text-embedding-3-large)
                )
                # Extraer los embeddings de la respuesta
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                if show_progress:
                    print(f"  Processed batch {batch_num}/{total_batches}")
                    logger.info(f"  Processed batch {batch_num}/{total_batches}")
                    
            except Exception as e:
                error_msg = f"Error generating embeddings for batch {batch_num}: {e}"
                print(error_msg)
                logger.error(error_msg)
                raise # Re-lanzar el error para detener el proceso
        
        generation_time = time.time() - start_time
        success_msg = f"Generated {len(all_embeddings)} embeddings in {generation_time:.2f}s"
        print(success_msg)
        logger.info(success_msg)
        
        # Convertir a numpy array
        return np.array(all_embeddings)
        
    def encode_query(self, query: str) -> np.ndarray:
        """
        Codifica una sola consulta de texto.
        
        Args:
            query (str): El texto de la consulta.
        
        Returns:
            np.ndarray: El vector de embedding de la consulta (1536,).
        """
        # Reutilizar la lógica de encode_texts para una sola consulta
        embeddings = self.encode_texts([query], show_progress=False)
        return embeddings[0] # Return single embedding
        
    def get_model_info(self) -> dict:
        """
        Obtiene información sobre el modelo de embeddings.
        
        Returns:
            dict: Diccionario con información del modelo.
        """
        from datetime import date
        # text-embedding-3-small siempre genera 1536 dimensiones
        return {
            "model_name": self.model_name,
            "dimensions": self.embedding_dim, 
            "device": "cloud (OpenAI API)",
            "language": "es",
            "generated_date": date.today().strftime("%Y-%m-%d")
        }
    
