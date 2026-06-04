import chromadb, os
from dotenv import load_dotenv


load_dotenv()


def get_collection():
    path = os.getenv("CHROMA_PATH", "./chroma_db")
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(
        name="video_chunks",
        metadata={"hnsw:space": "cosine"}
    )


def clear_collection():
    path = os.getenv("CHROMA_PATH", "./chroma_db")
    client = chromadb.PersistentClient(path=path)
    try:
        client.delete_collection("video_chunks")
    except Exception:
        pass
    return client.create_collection(
        name="video_chunks",
        metadata={"hnsw:space": "cosine"}
    )
