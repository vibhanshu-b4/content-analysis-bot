from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from .chroma_store import get_collection


def ingest_video(video_data: dict, label: str) -> int:
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    chunks = splitter.split_text(video_data["transcript"])
    embedder = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    embeddings = embedder.embed_documents(chunks)
    collection = get_collection()

    for i, chunk in enumerate(chunks):
        collection.add(
            ids=[f"{label}_chunk_{i}"],
            embeddings=[embeddings[i]],
            documents=[chunk],
            metadatas=[{
                "video_id": label,
                "chunk_index": i,
                "creator": str(video_data.get("creator", "")),
                "views": int(video_data.get("views") or 0),
                "likes": int(video_data.get("likes") or 0),
                "comments": int(video_data.get("comments") or 0),
                "engagement_rate": float(video_data.get("engagement_rate") or 0),
                "platform": str(video_data.get("platform", "")),
            }],
        )

    return len(chunks)
