import asyncio
from rag.chain import get_llm, build_prompt
from rag.retriever import retrieve_chunks

question = "What is the engagement rate of each video?"
chunks = retrieve_chunks(question)
messages = build_prompt(question, chunks, [])
llm = get_llm()

async def test():
    print("Answer:\n")
    async for token in llm.astream(messages):
        print(token.content, end="", flush=True)
    print("\n\nDone.")

asyncio.run(test())