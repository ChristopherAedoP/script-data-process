#!/usr/bin/env python3
"""
Script para subir datos a Qdrant Cloud
Requiere: API key y cluster URL de Qdrant Cloud
"""
import json
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models

def upload_to_qdrant_cloud(
    api_key: str, 
    url: str, 
    collection_name: str = "political_documents",
    data_file: str = "political_documents.json"
):
    """Upload data to Qdrant Cloud"""
    
    # Initialize client with API key
    client = QdrantClient(url=url, api_key=api_key)
    
    print(f"Connecting to Qdrant Cloud: {url}")
    
    # Create collection if it doesn't exist
    try:
        client.get_collection(collection_name)
        print(f"Collection {collection_name} already exists")
    except:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384,  # all-MiniLM-L6-v2 dimension
                distance=models.Distance.COSINE
            )
        )
        print(f"Created collection {collection_name}")
    
    # Load points from JSON file
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    points = data["points"]
    total_points = len(points)
    
    print(f"Uploading {total_points} points...")
    
    # Upload points in batches
    batch_size = 64  # Smaller batches for cloud
    
    for i in range(0, total_points, batch_size):
        batch = points[i:i + batch_size]
        
        qdrant_points = [
            models.PointStruct(
                id=point["id"],
                vector=point["vector"],
                payload=point["payload"]
            )
            for point in batch
        ]
        
        try:
            client.upsert(
                collection_name=collection_name,
                points=qdrant_points
            )
            
            batch_num = i//batch_size + 1
            total_batches = (total_points + batch_size - 1)//batch_size
            print(f"✅ Uploaded batch {batch_num}/{total_batches} ({len(batch)} points)")
            
        except Exception as e:
            print(f"❌ Error uploading batch {batch_num}: {e}")
            return False
    
    print(f"🎉 Successfully uploaded {total_points} points to Qdrant Cloud!")
    
    # Print collection stats
    try:
        collection_info = client.get_collection(collection_name)
        print(f"📊 Collection info: {collection_info}")
    except Exception as e:
        print(f"⚠️ Could not fetch collection info: {e}")
    
    return True

def main():
    # Configuration - Replace with your Qdrant Cloud credentials
    API_KEY = os.getenv("QDRANT_API_KEY")
    CLUSTER_URL = os.getenv("QDRANT_URL")
    
    if not API_KEY:
        print("❌ Error: QDRANT_API_KEY environment variable not set")
        print("Set it with: export QDRANT_API_KEY=your_api_key_here")
        return
    
    if not CLUSTER_URL:
        print("❌ Error: QDRANT_URL environment variable not set")  
        print("Set it with: export QDRANT_URL=https://your-cluster-url.qdrant.tech")
        return
    
    print("🚀 Starting upload to Qdrant Cloud...")
    print(f"Cluster: {CLUSTER_URL}")
    print(f"API Key: {API_KEY[:8]}...")
    
    success = upload_to_qdrant_cloud(
        api_key=API_KEY,
        url=CLUSTER_URL,
        collection_name="political_documents",
        data_file="political_documents.json"
    )
    
    if success:
        print("\n✅ Upload completed successfully!")
        print("Next steps:")
        print("1. Test queries using Qdrant Cloud dashboard")
        print("2. Check the filters guide: political_documents_filters_guide.md")
        print("3. Integrate with your web chatbot")
    else:
        print("\n❌ Upload failed. Check your credentials and network connection.")

if __name__ == "__main__":
    main()