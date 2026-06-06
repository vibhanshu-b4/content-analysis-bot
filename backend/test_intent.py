from rag.retriever import detect_intent, retrieve_chunks

questions = [
    "Compare the hooks in the first 5 seconds",
    "What is the engagement rate of each video?",
    "Who is the creator of Video B?",
    "Suggest improvements for Video B",
    "Compare Video A and Video B content quality"
]

for q in questions:
    intent = detect_intent(q)
    chunks = retrieve_chunks(q)
    chunk_ids = [f"Video {c['video_id']} chunk {c['chunk_index']}" for c in chunks]
    print(f"\nQ: {q}")
    print(f"Intent: {intent}")
    print(f"Chunks retrieved: {chunk_ids}")