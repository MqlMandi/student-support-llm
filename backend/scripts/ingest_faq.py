import os
import uuid
import argparse
from backend.utils.document_parser import parse_file
from backend.utils.chunker import chunk_text
from backend.utils.embedder import generate_embedding
from backend.database import get_chroma_client

def main(directory_path: str):
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        return

    client = get_chroma_client()
    # Create or get collection
    collection = client.get_or_create_collection(name="university_faq")

    print(f"Scanning directory: {directory_path}")
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if not os.path.isfile(filepath):
            continue
            
        try:
            print(f"Processing {filename}...")
            text = parse_file(filepath)
            chunks = chunk_text(text)
            
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                # Only embed non-empty chunks
                if not chunk.strip():
                    continue
                emb = generate_embedding(chunk)
                
                ids.append(str(uuid.uuid4()))
                embeddings.append(emb)
                documents.append(chunk)
                metadatas.append({"source": filename, "chunk_index": i})
            
            if ids:
                collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
            print(f"Successfully ingested {len(ids)} chunks from {filename}")
            
        except Exception as e:
            print(f"Skipping {filename}: {str(e)}")

    print(f"Ingestion complete. Total items in collection: {collection.count()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest FAQ documents into ChromaDB")
    parser.add_argument("directory", help="Path to the directory containing FAQ documents")
    args = parser.parse_args()
    main(args.directory)
