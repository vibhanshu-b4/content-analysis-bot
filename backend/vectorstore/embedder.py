from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from vectorstore.chroma_store import get_collection


_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    return _embedder


def ingest_video(video_data: dict, label: str) -> int:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from vectorstore.chroma_store import get_collection

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=50
    )
    transcript = video_data.get("transcript", "")
    chunks = splitter.split_text(transcript)

    # add a special "hook" chunk — first 300 chars of transcript
    hook_text = transcript[:300]
    all_chunks = [f"[HOOK - first 5 seconds]: {hook_text}"] + chunks

    embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    embeddings = embedder.embed_documents(all_chunks)

    collection = get_collection()

    base_meta = {
        "video_id": label,
        "creator": str(video_data.get("creator", "")),
        "views": int(video_data.get("views") or 0),
        "likes": int(video_data.get("likes") or 0),
        "comments": int(video_data.get("comments") or 0),
        "engagement_rate": float(video_data.get("engagement_rate") or 0),
        "platform": str(video_data.get("platform", "")),
        "title": str(video_data.get("title", ""))
    }

    for i, chunk in enumerate(all_chunks):
        meta = {**base_meta, "chunk_index": i}
        collection.add(
            ids=[f"{label}_chunk_{i}"],
            embeddings=[embeddings[i]],
            documents=[chunk],
            metadatas=[meta]
        )

    return len(all_chunks)