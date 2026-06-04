import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv


load_dotenv()


def build_prompt(question: str, chunks: list, history: list) -> list:
    system = """You are a video content analyst.
Answer questions about two videos using only the provided context.
Label the videos as Video A and Video B.
After every factual claim, add a citation like [Video A, chunk 3].
Be specific and analytical."""

    context_parts = []
    for c in chunks:
        context_parts.append(
            f"[Video {c['video_id']}, chunk {c['chunk_index']}]: {c['text']}"
        )
    context = "\n\n".join(context_parts)

    messages = [SystemMessage(content=system)]
    for turn in history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=turn["content"]))

    user_message = f"Context:\n{context}\n\nQuestion: {question}"
    messages.append(HumanMessage(content=user_message))
    return messages


def get_llm():
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        temperature=0.3,
        streaming=True
    )
