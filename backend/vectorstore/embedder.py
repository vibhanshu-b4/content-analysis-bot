from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vectorstore.chroma_store import get_collection

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    return _embedder


def ingest_video(video_data: dict, label: str) -> int:
    embedder = get_embedder()
    collection = get_collection()

    base_meta = {
        "video_id": label,
        "creator": str(video_data.get("creator") or "Unknown"),
        "views": int(video_data.get("views") or 0),
        "likes": int(video_data.get("likes") or 0),
        "comments": int(video_data.get("comments") or 0),
        "engagement_rate": float(video_data.get("engagement_rate") or 0),
        "platform": str(video_data.get("platform") or "Unknown"),
        "title": str(video_data.get("title") or "Unknown")
    }

    # 1. store stats document
    engagement_rate = base_meta["engagement_rate"]
    views = base_meta["views"]
    likes = base_meta["likes"]
    comments = base_meta["comments"]

    stats_text = f"""=== OFFICIAL STATS FOR VIDEO {label} ===
Title: {base_meta['title']}
Creator: {base_meta['creator']}
Platform: {base_meta['platform'].upper()}
Views: {views:,}
Likes: {likes:,}
Comments: {comments:,}
Engagement Rate: {engagement_rate}%
Duration: {video_data.get('duration', 'Unknown')} seconds
Followers: {video_data.get('followers') or 'Unavailable'}

NOTE: If views=0 or engagement_rate=0.0 this means the platform
does not expose these metrics publicly. They are unavailable due
to platform restrictions, not because engagement did not happen."""

    stats_embedding = embedder.embed_documents([stats_text])[0]
    collection.add(
        ids=[f"{label}_stats"],
        embeddings=[stats_embedding],
        documents=[stats_text],
        metadatas=[{**base_meta, "chunk_index": -1, "type": "stats"}]
    )
    print(f"  Stored {label}_stats")

    # 2. store hook document
    transcript = str(video_data.get("transcript") or "")
    hook_text = f"[HOOK - opening of Video {label}]: {transcript[:300]}"
    hook_embedding = embedder.embed_documents([hook_text])[0]
    collection.add(
        ids=[f"{label}_hook"],
        embeddings=[hook_embedding],
        documents=[hook_text],
        metadatas=[{**base_meta, "chunk_index": 0, "type": "hook"}]
    )
    print(f"  Stored {label}_hook")

    # 3. store transcript chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=50
    )
    chunks = splitter.split_text(transcript)
    if chunks:
        chunk_embeddings = embedder.embed_documents(chunks)
        for i, chunk in enumerate(chunks):
            collection.add(
                ids=[f"{label}_chunk_{i}"],
                embeddings=[chunk_embeddings[i]],
                documents=[chunk],
                metadatas=[{**base_meta, "chunk_index": i + 1, "type": "transcript"}]
            )
        print(f"  Stored {len(chunks)} transcript chunks for {label}")

    return len(chunks) + 2  # chunks + stats + hook