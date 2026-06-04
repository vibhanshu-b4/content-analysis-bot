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
    youtube_url: str
    instagram_url: str


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
