from langchain_huggingface import HuggingFaceEmbeddings
from vectorstore.chroma_store import get_collection

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    return _embedder

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
    question_lower = question.lower()

    stats = get_video_stats(["A", "B"])

    needs_hook = any(word in question_lower for word in [
        "hook", "first", "opening", "seconds", "start", "begin", "intro"
    ])

    needs_stats_only = any(word in question_lower for word in [
        "engagement rate", "views", "likes", "comments", "follower", "who is", "creator"
    ])

    needs_content_context = any(word in question_lower for word in [
        "compare", "why", "quality", "content", "hook", "story", "tone"
    ])

    if needs_stats_only:
        if not needs_content_context:
            return stats
        query_embedding = embedder.embed_query(question)
        collection = get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=4,
            include=["documents", "metadatas", "distances"]
        )
        extra = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            if meta.get("type") in ("stats", "hook"):
                continue
            extra.append({
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
        return stats + extra[:2]

    if needs_hook:
        collection = get_collection()
        hook_chunks = []
        for vid_id in ["A", "B"]:
            try:
                result = collection.get(
                    ids=[f"{vid_id}_hook"],
                    include=["documents", "metadatas"]
                )
                if result["documents"]:
                    meta = result["metadatas"][0]
                    hook_chunks.append({
                        "text": result["documents"][0],
                        "video_id": vid_id,
                        "chunk_index": 0,
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
        return hook_chunks

    # default semantic search
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
        if meta.get("type") in ("stats", "hook"):
            continue
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

    video_a = [c for c in all_chunks if c["video_id"] == "A"][:2]
    video_b = [c for c in all_chunks if c["video_id"] == "B"][:2]

    return stats + video_a + video_b