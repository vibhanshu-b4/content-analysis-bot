from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ingestion.youtube import get_youtube_data
from ingestion.instagram import get_instagram_data
from ingestion.metrics import build_video_summary
from vectorstore.chroma_store import clear_collection
from vectorstore.embedder import ingest_video


class IngestRequest(BaseModel):
    youtube_url: str
    instagram_url: str


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(request: IngestRequest):
    try:
        yt_data = get_youtube_data(request.youtube_url)
        ig_data = get_instagram_data(request.instagram_url)
        summary_a = build_video_summary(yt_data, "A")
        summary_b = build_video_summary(ig_data, "B")
        clear_collection()
        chunks_a = ingest_video(summary_a, "A")
        chunks_b = ingest_video(summary_b, "B")
        return {
            "video_a": summary_a,
            "video_b": summary_b,
            "chunks_a": chunks_a,
            "chunks_b": chunks_b,
            "status": "ok",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
