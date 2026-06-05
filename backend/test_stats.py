from vectorstore.chroma_store import get_collection

collection = get_collection()

print("=== Video A stats ===")
try:
    result = collection.get(
        ids=["A_stats"],
        include=["documents", "metadatas"]
    )
    print("Document:", result["documents"])
    print("Metadata:", result["metadatas"])
except Exception as e:
    print("ERROR:", e)

print("\n=== Video B stats ===")
try:
    result = collection.get(
        ids=["B_stats"],
        include=["documents", "metadatas"]
    )
    print("Document:", result["documents"])
    print("Metadata:", result["metadatas"])
except Exception as e:
    print("ERROR:", e)

print("\n=== All IDs in collection ===")
all_data = collection.get()
print("IDs:", all_data["ids"])