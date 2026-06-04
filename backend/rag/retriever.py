from langchain_community.embeddings import HuggingFaceEmbeddings
from vectorstore.chroma_store import get_collection


def retrieve_chunks(question: str, k: int = 5) -> list:
    embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    query_embedding = embedder.embed_query(question)
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "text": doc,
            "video_id": results["metadatas"][0][i]["video_id"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": results["distances"][0][i]
        })
    return chunks
