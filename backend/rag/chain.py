import os
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()

def build_prompt(question: str, chunks: list, history: list) -> list:
    system = """You are a video content analyst comparing two videos.

You will be given statistics and transcript chunks for Video A and Video B.
These videos may be from any platform (YouTube, Instagram, TikTok, etc).

Rules:
- Never assume which platform is better or worse
- Base engagement analysis strictly on the provided engagement_rate values
- If engagement_rate is 0.0, state that metrics were unavailable for that platform
- Use transcript content to compare hooks, tone, style, and storytelling
- After every factual claim cite the source like [Video A, chunk 2]
- Be specific — reference actual words from the transcripts when comparing

Do not make assumptions beyond what the context provides."""

    # group metadata by video_id
    video_stats = {}
    for c in chunks:
        vid = c["video_id"]
        if vid not in video_stats:
            video_stats[vid] = {
                "views": c.get("views", 0),
                "likes": c.get("likes", 0),
                "comments": c.get("comments", 0),
                "engagement_rate": c.get("engagement_rate", 0.0),
                "creator": c.get("creator", "Unknown"),
                "platform": c.get("platform", "Unknown")
            }

    # build stats block
    stats_block = "=== VIDEO STATISTICS ===\n"
    for vid_id, stats in video_stats.items():
        engagement_note = (
        f"{stats['engagement_rate']}%"
        if stats['engagement_rate'] > 0
        else "Unavailable (platform does not expose public metrics)"
    )
    stats_block += f"""
    Video {vid_id}:
    - Platform: {stats['platform'].upper()}
    - Creator: {stats['creator']}
    - Views: {stats['views']:,} {'(unavailable)' if stats['views'] == 0 else ''}
    - Likes: {stats['likes']:,} {'(unavailable)' if stats['likes'] == 0 else ''}
    - Comments: {stats['comments']:,} {'(unavailable)' if stats['comments'] == 0 else ''}
    - Engagement Rate: {engagement_note}
    """

    # build transcript chunks block
    context_parts = []
    for c in chunks:
        context_parts.append(
            f"[Video {c['video_id']}, chunk {c['chunk_index']}]: {c['text']}"
        )
    transcript_block = "\n\n".join(context_parts)

    messages = [SystemMessage(content=system)]
    for turn in history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))

    user_message = f"{stats_block}\n\n=== TRANSCRIPT CHUNKS ===\n{transcript_block}\n\nQuestion: {question}"
    messages.append(HumanMessage(content=user_message))
    return messages

def get_llm():
    return ChatOllama(
        model="llama3.2",
        temperature=0.3,
    )