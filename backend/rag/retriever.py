from langchain_huggingface import HuggingFaceEmbeddings
from vectorstore.chroma_store import get_collection
import hashlib

_query_cache = {}

def embed_with_cache(embedder, question: str) -> list:
    key = hashlib.md5(question.encode()).hexdigest()
    if key not in _query_cache:
        _query_cache[key] = embedder.embed_query(question)
    return _query_cache[key]
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    return _embedder

def detect_intent(question: str) -> str:
    q = question.lower()
    
    if any(w in q for w in ["hook", "first", "opening", "seconds", "start", "intro", "begin"]):
        return "hook"
    
    if any(w in q for w in ["engagement", "likes", "views", "comments", "rate", "perform", "metric"]):
        return "stats"
    
    if any(w in q for w in ["creator", "who", "follower", "platform", "channel"]):
        return "stats"
    
    if any(w in q for w in ["improve", "suggest", "better", "fix", "recommendation", "tip"]):
        return "improvement"
    
    if any(w in q for w in ["cta", "call to action", "conclusion", "end", "subscribe", "follow"]):
        return "cta"
    
    if any(w in q for w in ["compare", "difference", "versus", "vs", "which", "why"]):
        return "compare"
    
    return "general"


def get_video_stats(video_ids: list = ["A", "B"]) -> list:
    collection = get_collection()
    stats = []
    for vid_id in video_ids:
        try:
            result = collection.get(
                ids=[f"{vid_id}_stats"],
                include=["documents", "metadatas"]
            )
            if result["documents"]:
                meta = result["metadatas"][0]
                stats.append({
                    "text": result["documents"][0],
                    "video_id": vid_id,
                    "chunk_index": -1,
                    "views": meta.get("views", 0),
                    "likes": meta.get("likes", 0),
                    "comments": meta.get("comments", 0),
                    "engagement_rate": meta.get("engagement_rate", 0.0),
                    "creator": meta.get("creator", "Unknown"),
                    "platform": meta.get("platform", "Unknown"),
                    "title": meta.get("title", ""),
                    "distance": 0.0
                })
        except Exception:
            pass
    return stats


def retrieve_chunks(question: str, k: int = 6) -> list:
    embedder = get_embedder()
    collection = get_collection()
    stats = get_video_stats(["A", "B"])
    intent = detect_intent(question)

    if intent == "stats":
        return stats

    if intent == "hook":
        hook_chunks = []
        for vid_id in ["A", "B"]:
            try:
                result = collection.get(
                    ids=[f"{vid_id}_chunk_0"],
                    include=["documents", "metadatas"]
                )
                if result["documents"]:
                    meta = result["metadatas"][0]
                    hook_chunks.append(build_chunk_dict(
                        result["documents"][0], meta, vid_id, 0
                    ))
            except Exception:
                pass
        return stats + hook_chunks

    if intent == "cta":
        cta_chunks = []
        for vid_id in ["A", "B"]:
            try:
                result = collection.get(
                    ids=[f"{vid_id}_chunk_3"],
                    include=["documents", "metadatas"]
                )
                if result["documents"]:
                    meta = result["metadatas"][0]
                    cta_chunks.append(build_chunk_dict(
                        result["documents"][0], meta, vid_id, 3
                    ))
            except Exception:
                pass
        return stats + cta_chunks

    # for compare, improvement, general — semantic search
    query_embedding = embedder.embed_query(question)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        include=["documents", "metadatas", "distances"]
    )

    all_chunks = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        if meta.get("type") == "stats":
            continue
        all_chunks.append(build_chunk_dict(
            doc, meta,
            meta.get("video_id", "?"),
            meta.get("chunk_index", i),
            results["distances"][0][i]
        ))

    video_a = [c for c in all_chunks if c["video_id"] == "A"][:2]
    video_b = [c for c in all_chunks if c["video_id"] == "B"][:2]
    return stats + video_a + video_b


def build_chunk_dict(doc, meta, video_id, chunk_index, distance=0.0):
    return {
        "text": doc,
        "video_id": video_id,
        "chunk_index": chunk_index,
        "chunk_type": meta.get("chunk_type", "transcript"),
        "views": meta.get("views", 0),
        "likes": meta.get("likes", 0),
        "comments": meta.get("comments", 0),
        "engagement_rate": meta.get("engagement_rate", 0.0),
        "creator": meta.get("creator", "Unknown"),
        "platform": meta.get("platform", "Unknown"),
        "title": meta.get("title", ""),
        "distance": distance
    }