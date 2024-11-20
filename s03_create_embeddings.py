import os
from datetime import datetime
import re
from typing import Dict, Any
import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models
from aidevs import answer_question_local, memory, get_embedding
from aidevs_text_extractor import TextFilePlugin

def extract_date_from_filename(filename: str) -> str:
    """Extract date from filename in format YYYY_MM_DD"""
    date_pattern = r'(\d{4}_\d{2}_\d{2})'
    match = re.search(date_pattern, filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%Y_%m_%d').isoformat()
    return None

@memory.cache
def extract_weapon_name(content: str) -> str:
    """Extract weapon name from file content using Gemma"""
    prompt = """Extract the weapon name from the following text. Return only the weapon name, nothing else:

    Text: {content}
    """
    
    response = answer_question_local(
        prompt.format(content=content),
        model='gemma2:27b',
        stream=False
    )
    print(f"Weapon name: {response=}")
    return response.strip()

def process_files(directory: str) -> list[Dict[str, Any]]:
    """Process all text files in directory and return list of documents with embeddings"""
    text_plugin = TextFilePlugin()
    documents = []
    
    for filename in os.listdir(directory):
        if not filename.endswith('.txt'):
            continue
            
        filepath = os.path.join(directory, filename)
        
        # Extract text content
        content = text_plugin.extract(filepath)
        
        # Get embedding (now cached)
        embedding = get_embedding(content)
        
        # Extract metadata (weapon name extraction now cached)
        date = extract_date_from_filename(filename)
        weapon_name = extract_weapon_name(content)
        
        doc = {
            'filename': filename,
            'content': content,
            'embedding': embedding,
            'metadata': {
                'date': date,
                'weapon_name': weapon_name
            }
        }
        
        documents.append(doc)
        
    return documents

def store_in_qdrant(documents: list[Dict[str, Any]]):
    """Store documents in Qdrant cloud database"""
    api_key = os.getenv('QDRANT_API_KEY')
    qdrant_url = os.getenv('QDRANT_URL')
    
    if not api_key:
        raise ValueError("QDRANT_API_KEY environment variable not set")
    if not qdrant_url:
        raise ValueError("QDRANT_URL environment variable not set")
    
    # Initialize Qdrant client
    client = QdrantClient(
        qdrant_url,
        api_key=api_key
    )
    
    # Create collection if it doesn't exist
    collection_name = "factory_documents"
    
    try:
        client.get_collection(collection_name)
    except:
        # Create new collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=len(documents[0]['embedding']),
                distance=models.Distance.COSINE
            )
        )
    
    # Prepare points for upload
    points = []
    for i, doc in enumerate(documents):
        point = models.PointStruct(
            id=i,
            vector=doc['embedding'],
            payload={
                'filename': doc['filename'],
                'content': doc['content'],
                'date': doc['metadata']['date'],
                'weapon_name': doc['metadata']['weapon_name']
            }
        )
        points.append(point)
    
    # Upload points in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch
        )

def main():
    """Main function to process files and store in Qdrant"""
    directory = "data/dane_z_fabryki/do-not-share/"
    
    # Process all files
    print("Processing files and generating embeddings...")
    documents = process_files(directory)
    
    # Store in Qdrant
    print("Storing documents in Qdrant...")
    store_in_qdrant(documents)
    
    print("Done!")

if __name__ == "__main__":
    main() 