import os
import uuid
import argparse
import hashlib
from backend.utils.document_parser import parse_file
from backend.utils.chunker import chunk_text
from backend.utils.embedder import generate_embedding
from backend.database import get_chroma_client

def process_single_file(filepath: str, collection):
    filename = os.path.basename(filepath)
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
            
            chunk_id = hashlib.sha256(f"{filename}_{i}".encode('utf-8')).hexdigest()
            ids.append(chunk_id)
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

def main(dir_path: str = None, file_path: str = None):
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="university_faq")

    if file_path:
        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return
        process_single_file(file_path, collection)
    
    elif dir_path:
        if not os.path.exists(dir_path):
            print(f"Error: Directory '{dir_path}' does not exist.")
            return
        print(f"Scanning directory: {dir_path}")
        for filename in os.listdir(dir_path):
            full_path = os.path.join(dir_path, filename)
            if os.path.isfile(full_path):
                process_single_file(full_path, collection)

    print(f"Ingestion complete. Total items in collection: {collection.count()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest FAQ documents into ChromaDB")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", help="Path to the directory containing FAQ documents")
    group.add_argument("--file", help="Path to a single FAQ document")
    args = parser.parse_args()
    
    main(dir_path=args.dir, file_path=args.file)
