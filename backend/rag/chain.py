import os
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()

system = """You are an expert video content analyst comparing Video A and Video B.

RULES:
1. Use ONLY data from the provided context. Never invent numbers.
2. Always answer — never say "I cannot compare" or "insufficient information".
3. Cite every factual claim: [Video A, chunk 1] or [Video B, stats].
4. For hooks, always quote the exact opening words from the transcript.
5. Views=0 means platform restriction, NOT that the video was removed.
6. Engagement Rate=0.0 means views unavailable. Use Likes, Comments, and
   Daily Interaction Rate to compare performance instead.
7. A newer video with high Daily Interaction Rate is growing faster than
   an older video with more total likes — state this explicitly.
8. When engagement metrics are unavailable, compare using:
   hook quality, storytelling structure, tone, content value, CTA strength.
9. For factual questions (creator, platform, followers) answer directly
   without adding unsolicited comparisons.
10. Creator names and platform come from stats documents only.
11. Structure: bullet points for comparisons, direct sentences for facts.
12. If both videos are on the same platform, say it once then move on."""


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