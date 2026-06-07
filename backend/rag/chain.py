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
4. For hooks, quote the complete opening sentence — never individual words.
5. Views=0 means platform restriction, NOT that the video was removed.
6. Engagement Rate=0.0 means views unavailable. When this happens:
   - State views are unavailable in one sentence
   - Compare using Likes, Comments, Total Interactions, Daily Interaction Rate
   - Then add content-based comparison
   - Never stop after just explaining why metrics are unavailable
7. A newer video with higher Daily Interaction Rate is growing faster than
   an older video with more total likes — always state this explicitly.
8. When engagement metrics are unavailable compare using:
   hook quality, storytelling structure, tone, content value, CTA strength.
9. For factual questions (creator, platform, followers) answer directly
   without adding unsolicited comparisons.
10. Creator names and platform come from stats documents only.
11. Structure: bullet points for comparisons, direct sentences for facts.
12. If both videos are on the same platform say it once then move on.
13. For improvement suggestions, always quote a specific transcript moment
    then explain exactly what to change and why. No generic advice.
    14. Do NOT write citations inside your response text like [Video A, chunk 1].
    Citations are handled separately by the system. Just write clean prose.
    """

def build_prompt(question: str, chunks: list, history: list) -> list:
    context_parts = []
    for c in chunks:
        chunk_type = c.get("chunk_type", "transcript").upper()
        context_parts.append(
            f"[Video {c['video_id']} — {chunk_type}]:\n{c['text']}"
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