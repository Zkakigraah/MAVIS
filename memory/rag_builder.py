import os
import sys
from pathlib import Path

# Thêm thư mục gốc vào biến môi trường để Python nhận diện module core
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.config import DOCS_DIR
from memory.qdrant_db import memory_db

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Cắt một đoạn văn bản dài thành các khối nhỏ (chunks)."""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
        
    return chunks

def ingest_documents():
    """Đọc file .txt trong personal_docs và nạp vào DB."""
    print(f"🔍 Đang quét thư mục tài liệu cá nhân: {DOCS_DIR}...")
    
    if not DOCS_DIR.exists():
        print("❌ Thư mục không tồn tại!")
        return

    files = list(DOCS_DIR.glob("*.txt"))
    if not files:
        print("⚠️ Không tìm thấy file .txt nào để nạp.")
        return

    print("🧠 Đang định dạng lại vùng trí nhớ...")
    memory_db.reset_collection()

    total_chunks = 0
    for file_path in files:
        print(f"📄 Đang xử lý file: {file_path.name}...")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            chunks = chunk_text(content)
            metadata = [{"source": file_path.name}] * len(chunks)
            
            memory_db.add_texts(texts=chunks, metadata=metadata)
            total_chunks += len(chunks)
            
        except Exception as e:
            print(f"❌ Lỗi khi đọc file {file_path.name}: {str(e)}")
            
    print(f"✅ Hoàn tất! Đã nạp thành công {total_chunks} khối tri thức vào trí nhớ J.A.R.V.I.S.")

if __name__ == "__main__":
    ingest_documents()