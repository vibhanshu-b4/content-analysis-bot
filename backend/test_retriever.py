from rag.retriever import retrieve_chunks

chunks = retrieve_chunks('What is the engagement rate of Video A?')
for c in chunks:
    print(f"Video {c['video_id']} chunk {c['chunk_index']}: {c['text'][:80]}")