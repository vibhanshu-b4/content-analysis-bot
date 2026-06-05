import asyncio
from rag.chain import get_llm, build_prompt
from rag.retriever import retrieve_chunks

questions = [
    "Compare Video A and Video B. Which has better content quality and why? Use transcript evidence.",
    "What is the engagement rate of each video? If unavailable explain why and compare based on content instead.",
    "Compare the hooks in the first 5 seconds of each video. Quote the actual opening words.",
    "Who is the creator of Video A and Video B? What platform are they on and what is their follower count?",
    "Suggest 3 specific improvements for Video B based on what worked in Video A. Reference specific transcript moments."
]

async def test():
    llm = get_llm()
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"Q{i}: {question}")
        print(f"{'='*60}")
        chunks = retrieve_chunks(question)
        messages = build_prompt(question, chunks, [])
        async for token in llm.astream(messages):
            print(token.content, end="", flush=True)
        print()

asyncio.run(test())