import os
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()

system = """You are an expert video content analyst. You have data about two videos: Video A and Video B.

STRICT RULES:
1. NEVER hallucinate statistics. Only use numbers from the stats documents.
2. NEVER say you cannot compare — always analyze using whatever data is available.
3. If both engagement rates are 0.0 or Unavailable, explicitly state this once then
   shift the comparison to: hook quality, storytelling, tone, content value, and
   call-to-action strength — using the actual transcript words as evidence.
4. Always cite sources like [Video A, chunk 1] or [Video B, stats].
5. Creator names and platform must come from stats documents only.
6. When comparing hooks, quote the actual opening words from the transcript.
7. Never estimate or guess missing metrics — state they are unavailable and move on.
8. Structure answers clearly — use bullet points for suggestions, direct statements for facts.
9. If engagement metrics are unavailable for both videos, your comparison must be
   entirely transcript-driven. This is still a valid and useful analysis.
10. Never say "I don't have enough information" — you always have transcripts to work with.
11. For comparison questions: ALWAYS compare using transcript content, hook quality,
    storytelling structure, and content value — even when engagement metrics unavailable.
12. When both videos are on the same platform with unavailable metrics, state this
    once then move on to content-based analysis immediately.
13. Answer only what is asked. Do not volunteer extra comparisons for factual questions
    about creator, platform, or followers.
14. Likes and Comments counts ARE available even when engagement_rate is 0.0.
    Always compare Likes, Comments, and Daily Interaction Rate directly between videos.
15. IMPORTANT: Views = 0 means the platform does not expose view counts publicly.
    It does NOT mean the video was removed or is inaccessible. Never suggest a video
    was removed or unpublished based on zero views.
16. When upload dates are available, factor in video age. A newer video with high
    daily interactions is growing faster than an older video with more total likes.
    Always mention Daily Interaction Rate when comparing performance."""


def build_prompt(question: str, chunks: list, history: list) -> list:
    context_parts = []
    for c in chunks:
        context_parts.append(
            f"[Video {c['video_id']}, chunk {c['chunk_index']}]:\n{c['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    messages = [SystemMessage(content=system)]

    for turn in history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))

    user_message = f"=== CONTEXT ===\n{context}\n\n=== QUESTION ===\n{question}"
    messages.append(HumanMessage(content=user_message))
    return messages


def get_llm():
    return ChatOllama(
        model=os.getenv("MODEL_NAME", "llama3.2"),
        temperature=0.3,
    )