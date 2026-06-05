import asyncio
from rag.chain import get_llm, build_prompt
from rag.retriever import retrieve_chunks

questions = [
    "Why did Video A get more engagement than Video B?",
    "What is the engagement rate of each video?",
    "Compare the hooks in the first 5 seconds of each video.",
    "Who is the creator of Video B and what is their follower count?",
    "Suggest improvements for Video B based on what worked in Video A."
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