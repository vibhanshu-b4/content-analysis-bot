from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import label
from vectorstore.chroma_store import get_collection

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    return _embedder


def split_into_semantic_chunks(transcript: str, label: str) -> list:
    sentences = transcript.replace(".\n", ". ").split(". ")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    chunks = []
    
    # chunk 0 — always the hook (first 2 sentences)
    hook = ". ".join(sentences[:2])
    chunks.append({
        "text": f"[HOOK]: {hook}",
        "type": "hook",
        "index": 0
    })
    
    # chunk 1 — problem/context (sentences 3-6)
    if len(sentences) > 2:
        context = ". ".join(sentences[2:6])
        chunks.append({
            "text": f"[CONTEXT]: {context}",
            "type": "context",
            "index": 1
        })
    
    # chunk 2 — main content (sentences 7-14)
    if len(sentences) > 6:
        main = ". ".join(sentences[6:14])
        chunks.append({
            "text": f"[MAIN CONTENT]: {main}",
            "type": "main",
            "index": 2
        })
    
    # chunk 3 — CTA/conclusion (last 3 sentences)
    if len(sentences) > 10:
        cta = ". ".join(sentences[-3:])
        chunks.append({
            "text": f"[CONCLUSION/CTA]: {cta}",
            "type": "cta",
            "index": 3
        })
    
    return chunks



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
Upload Date: {video_data.get('upload_date_formatted', 'Unknown')}
Days Since Upload: {video_data.get('days_since_upload', 0)} days
Views: {views:,} (unavailable - platform restriction)
Likes: {likes:,}
Comments: {comments:,}
Total Interactions (Likes + Comments): {likes + comments:,}
Daily Interaction Rate: {video_data.get('daily_interactions', 0)} interactions/day
Engagement Rate: {engagement_rate}% (0.0 because views unavailable)
Duration: {video_data.get('duration', 'Unknown')} seconds
Followers: {video_data.get('followers') or 'Unavailable'}

NOTE: Views unavailable due to platform restrictions.
Use Total Interactions and Daily Interaction Rate to compare engagement.
Daily Interaction Rate accounts for video age — newer videos with high
daily rates are growing faster than older videos with more total likes."""

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
    # 3. store transcript chunks (semantic chunking)
    semantic_chunks = split_into_semantic_chunks(transcript, label)

    if semantic_chunks:
        chunk_texts = [c["text"] for c in semantic_chunks]
        chunk_embeddings = embedder.embed_documents(chunk_texts)

        for i, chunk in enumerate(semantic_chunks):
            collection.add(
                ids=[f"{label}_chunk_{i}"],
                embeddings=[chunk_embeddings[i]],
                documents=[chunk["text"]],
                metadatas=[{
                **base_meta,
                "chunk_index": i,
                "chunk_type": chunk["type"],
                "type": "transcript"
            }]
        )
        print(f"  Stored {len(semantic_chunks)} semantic chunks for {label}")

    return len(semantic_chunks) + 2