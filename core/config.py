import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# --- CẤU HÌNH ĐƯỜNG DẪN (SANDBOX) TƯƠNG THÍCH EXE ---
if getattr(sys, 'frozen', False):
    # Nếu đang chạy file JARVIS.exe, lấy thư mục chứa file .exe làm gốc
    BASE_DIR = Path(sys.executable).parent
else:
    # Nếu đang chạy code Python bình thường, lấy thư mục gốc của dự án
    BASE_DIR = Path(__file__).resolve().parent.parent

# VÙNG LÀM VIỆC CỐ ĐỊNH (Workspace Sandbox)
# AI CHỈ ĐƯỢC PHÉP đọc/ghi file trong thư mục này.
WORKSPACE_DIR = BASE_DIR / "workspace"
DOCS_DIR = WORKSPACE_DIR / "personal_docs"   # Nơi bạn bỏ file text, pdf vào
OUTPUTS_DIR = WORKSPACE_DIR / "outputs"      # Nơi AI lưu file kết quả
TEMP_DIR = WORKSPACE_DIR / "temp"            # Chứa file ghi âm, cache tạm

# Cơ sở dữ liệu
DB_DIR = BASE_DIR / "memory" / "qdrant_local"

# --- API KEYS ---
# Lấy từ file .env, nếu không có sẽ trả về chuỗi rỗng
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- HÀM BẢO MẬT (PATH VALIDATION) ---
def is_safe_path(target_path: Path) -> bool:
    """
    Kiểm tra xem một đường dẫn có nằm gọn bên trong WORKSPACE_DIR hay không.
    Ngăn chặn lỗi Path Traversal (ví dụ: AI sinh lệnh đọc file ../../../Windows/System32/...)
    """
    try:
        # Resolve để lấy đường dẫn tuyệt đối thực sự, loại bỏ các ký tự như '..'
        resolved_target = target_path.resolve()
        resolved_workspace = WORKSPACE_DIR.resolve()
        
        # Kiểm tra xem target có bắt đầu bằng workspace hay không
        return resolved_workspace in resolved_target.parents or resolved_target == resolved_workspace
    except Exception:
        return False