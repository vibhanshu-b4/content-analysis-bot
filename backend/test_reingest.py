from ingestion.detector import get_video_data
from ingestion.metrics import build_video_summary
from vectorstore.chroma_store import clear_collection
from vectorstore.embedder import ingest_video

URL_A = 'https://www.instagram.com/reel/DZGIPMWzgS2/?igsh=Yzc0a3d2dWMxYWV4'
URL_B = 'https://www.instagram.com/reel/DShsISsEtAq/?igsh=MWIxbWVmcnVveGRvNw=='

print(f"Fetching Video A from: {URL_A}")
data_a = get_video_data(URL_A)
summary_a = build_video_summary(data_a, 'A')
print(f"Platform: {summary_a['platform']} | Creator: {summary_a['creator']}")

print(f"Fetching Video B from: {URL_B}")
data_b = get_video_data(URL_B)
summary_b = build_video_summary(data_b, 'B')
print(f"Platform: {summary_b['platform']} | Creator: {summary_b['creator']}")

print("Clearing collection...")
clear_collection()

print("Ingesting A...")
chunks_a = ingest_video(summary_a, 'A')
print(f"Chunks A: {chunks_a}")

print("Ingesting B...")
chunks_b = ingest_video(summary_b, 'B')
print(f"Chunks B: {chunks_b}")

print("All done.")