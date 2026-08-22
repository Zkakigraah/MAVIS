from memory.qdrant_db import memory_db

print("\n--- KIỂM TRA TRÍ NHỚ J.A.R.V.I.S ---")
query = "favorite food"

print(f"🔎 Đang tìm kiếm từ khóa: '{query}'...")
results = memory_db.search(query, limit=3)

if not results:
    print("\n❌ KẾT QUẢ: DATABASE TRỐNG!")
    print("Nguyên nhân có thể do:")
    print("1. Trình nạp (rag_builder.py) chưa chạy thành công.")
    print("2. File personal_info.txt không nằm đúng thư mục: workspace/personal_docs/")
else:
    print("\n✅ KẾT QUẢ: TÌM THẤY DỮ LIỆU:")
    for idx, res in enumerate(results):
        print(f"[{idx+1}] {res}")