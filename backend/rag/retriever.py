from langchain_huggingface import HuggingFaceEmbeddings
from vectorstore.chroma_store import get_collection

# load once at module level, not inside the function
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    return _embedder

def retrieve_chunks(question: str, k: int = 6) -> list:
    embedder = get_embedder()
    query_embedding = embedder.embed_query(question)
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        include=["documents", "metadatas", "distances"]
    )
    all_chunks = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        all_chunks.append({
            "text": doc,
            "video_id": meta.get("video_id", "?"),
            "chunk_index": meta.get("chunk_index", i),
            "views": meta.get("views", 0),
            "likes": meta.get("likes", 0),
            "comments": meta.get("comments", 0),
            "engagement_rate": meta.get("engagement_rate", 0.0),
            "creator": meta.get("creator", "Unknown"),
            "platform": meta.get("platform", "Unknown"),
            "title": meta.get("title", ""),
            "distance": results["distances"][0][i]
        })
    video_a = [c for c in all_chunks if c["video_id"] == "A"][:3]
    video_b = [c for c in all_chunks if c["video_id"] == "B"][:3]
    return video_a + video_b