from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ingestion.youtube import get_youtube_data
from ingestion.instagram import get_instagram_data
from ingestion.metrics import build_video_summary
from vectorstore.chroma_store import clear_collection
from vectorstore.embedder import ingest_video
from fastapi.responses import StreamingResponse
from rag.retriever import retrieve_chunks
from rag.chain import build_prompt, get_llm
from rag.memory import get_history, save_turn
import json


class IngestRequest(BaseModel):
    video_url_a: str
    video_url_b: str

class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"


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
        from ingestion.detector import get_video_data

        print(f"Fetching Video A: {request.video_url_a}")
        data_a = get_video_data(request.video_url_a)
        
        print(f"Fetching Video B: {request.video_url_b}")
        data_b = get_video_data(request.video_url_b)

        summary_a = build_video_summary(data_a, "A")
        summary_b = build_video_summary(data_b, "B")

        clear_collection()

        chunks_a = ingest_video(summary_a, "A")
        chunks_b = ingest_video(summary_b, "B")

        return {
    "video_a": {
        "title": summary_a.get("title"),
        "creator": summary_a.get("creator"),
        "platform": summary_a.get("platform"),
        "likes": summary_a.get("likes"),
        "comments": summary_a.get("comments"),
        "views": summary_a.get("views"),
        "engagement_rate": summary_a.get("engagement_rate"),
        "daily_interactions": summary_a.get("daily_interactions"),
        "upload_date_formatted": summary_a.get("upload_date_formatted"),
        "days_since_upload": summary_a.get("days_since_upload"),
        "duration": summary_a.get("duration"),
        "followers": summary_a.get("followers"),
        "source_url": summary_a.get("source_url"),
        "transcript": summary_a.get("transcript"),
        "chunks": chunks_a
    },
    "video_b": {
        "title": summary_b.get("title"),
        "creator": summary_b.get("creator"),
        "platform": summary_b.get("platform"),
        "likes": summary_b.get("likes"),
        "comments": summary_b.get("comments"),
        "views": summary_b.get("views"),
        "engagement_rate": summary_b.get("engagement_rate"),
        "daily_interactions": summary_b.get("daily_interactions"),
        "upload_date_formatted": summary_b.get("upload_date_formatted"),
        "days_since_upload": summary_b.get("days_since_upload"),
        "duration": summary_b.get("duration"),
        "followers": summary_b.get("followers"),
        "source_url": summary_b.get("source_url"),
        "transcript": summary_b.get("transcript"),
        "chunks": chunks_b
    },
    "status": "ok"
}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest):

    async def stream_response():
        full_answer = ""
        chunks = retrieve_chunks(request.question)
        history = get_history(request.session_id)
        messages = build_prompt(request.question, chunks, history)
        llm = get_llm()

        async for token in llm.astream(messages):
            text = token.content
            if text:
                full_answer += text
                payload = json.dumps({"token": text})
                yield f"data: {payload}\n\n"

        citations = [
            {"video_id": c["video_id"], "chunk_index": c["chunk_index"]}
            for c in chunks
        ]
        final = json.dumps({"token": "", "citations": citations, "done": True})
        yield f"data: {final}\n\n"

        save_turn(request.session_id, request.question, full_answer)

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
