import os
from core.config import BASE_DIR, WORKSPACE_DIR, DOCS_DIR, OUTPUTS_DIR, TEMP_DIR, DB_DIR

def create_directories():
    """Khởi tạo toàn bộ cấu trúc thư mục cần thiết cho dự án."""
    directories = [
        WORKSPACE_DIR,
        DOCS_DIR,
        OUTPUTS_DIR,
        TEMP_DIR,
        DB_DIR,
        BASE_DIR / "core",
        BASE_DIR / "memory"
    ]

    print("🚀 Khởi tạo hệ thống J.A.R.V.I.S...")
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Đã tạo: {directory.relative_to(BASE_DIR)}")
        else:
            print(f"🔹 Đã tồn tại: {directory.relative_to(BASE_DIR)}")
            
    # Tạo file .env mẫu nếu chưa có
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
        print("✅ Đã tạo file .env mẫu. Hãy điền API Key vào đây.")

if __name__ == "__main__":
    create_directories()