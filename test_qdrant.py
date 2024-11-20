import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np

def main():
    # Get API key from environment variable
    api_key = os.getenv("QDRANT_API_KEY")
    if not api_key:
        raise ValueError("Please set QDRANT_API_KEY environment variable")

    # Initialize Qdrant client
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=api_key
    )

    collection_name = "test_collection"
    vector_size = 384  # Common embedding size, adjust if needed

    # Check if collection exists
    collections = client.get_collections()
    collection_names = [collection.name for collection in collections.collections]

    if collection_name not in collection_names:
        print(f"Creating new collection: {collection_name}")
        # Create new collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size, 
                distance=Distance.COSINE
            )
        )
        
        # Insert some test vectors
        test_vectors = np.random.rand(3, vector_size)  # 3 random test vectors
        points = [
            PointStruct(
                id=idx,
                vector=vector.tolist(),
                payload={"description": f"Test vector {idx}"}
            )
            for idx, vector in enumerate(test_vectors)
        ]
        
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        print("Added test vectors to collection")
    else:
        print(f"Collection {collection_name} already exists")

    # Get collection info
    collection_info = client.get_collection(collection_name)
    print("\nCollection info:")
    print(f"Points count: {collection_info.points_count}")
    print(f"Vectors size: {collection_info.config.params.vectors.size}")
    print(f"Distance: {collection_info.config.params.vectors.distance}")

if __name__ == "__main__":
    main() 