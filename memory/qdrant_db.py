import uuid
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from core.config import DB_DIR

class LocalMemoryDB:
    # Đổi tên collection để ép hệ thống tạo file cơ sở dữ liệu hoàn toàn mới, bỏ qua file rác cũ
    def __init__(self, collection_name="jarvis_core_memory"):
        self.collection_name = collection_name
        
        self.client = QdrantClient(path=str(DB_DIR))
        
        print("🧠 Đang tải AI Model nhúng (FastEmbed)...")
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Tạo collection với cấu hình vector 384 chiều của mô hình BAAI."""
        if not self.client.collection_exists(collection_name=self.collection_name):
            print(f"🛠️ Đang tạo bộ nhớ mới: {self.collection_name}...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print("✅ Đã khởi tạo bộ nhớ thành công!")

    def reset_collection(self):
        """Xóa sạch bộ nhớ cũ để nạp lại từ đầu."""
        if self.client.collection_exists(collection_name=self.collection_name):
            print(f"🗑️ Đang xóa vùng nhớ cũ: {self.collection_name}...")
            self.client.delete_collection(collection_name=self.collection_name)
        self._ensure_collection_exists()

    def add_texts(self, texts: list[str], metadata: list[dict] = None):
        """Thêm văn bản vào bộ nhớ (Sử dụng Deterministic ID để chống trùng lặp)."""
        if not texts:
            return
            
        print(f"🧠 Đang nạp {len(texts)} khối kiến thức vào bộ nhớ...")
        embeddings = list(self.embedding_model.embed(texts))
        
        points = []
        for i, (text, emb) in enumerate(zip(texts, embeddings)):
            meta = metadata[i] if metadata else {}
            meta["document"] = text
            
            # KỸ THUẬT RAG PRO: Tạo ID dựa trên chính nội dung Text.
            # Nếu chạy RAG nhiều lần, ID này không đổi -> Tự động Ghi Đè (Overwrite) thay vì đẻ thêm bản sao!
            deterministic_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, text))
            
            points.append(
                PointStruct(
                    id=deterministic_id,
                    vector=emb.tolist(),
                    payload=meta
                )
            )
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print("✅ Hoàn tất ghi nhớ.")

    def search(self, query: str, limit: int = 3):
        """Tìm kiếm thông tin trong bộ nhớ (Sử dụng API query_points mới nhất)."""
        if not self.client.collection_exists(self.collection_name):
            return []
            
        query_vector = list(self.embedding_model.query_embed([query]))[0]
        
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            limit=limit
        )
        
        return [res.payload.get("document", "") for res in response.points]

# Khởi tạo instance mặc định để các module khác import
memory_db = LocalMemoryDB()