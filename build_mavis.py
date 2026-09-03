import os
import shutil
import subprocess
from pathlib import Path

def main():
    print("="*60)
    print("🚀 ĐANG KHỞI TẠO QUÁ TRÌNH ĐÓNG GÓI BẢN PHÂN PHỐI (RELEASE)...")
    print("="*60)

    BASE_DIR = Path(__file__).resolve().parent
    DIST_DIR = BASE_DIR / "dist" / "MAVIS"
    INTERNAL_DIR = DIST_DIR / "_internal"

    print("\n📦 Bước 1: Biên dịch mã nguồn (PyInstaller)...")
    icon_filename = "app_icon.ico"
    icon_path = BASE_DIR / icon_filename
    
    if not icon_path.exists():
        print(f"⚠️ CẢNH BÁO: Không tìm thấy file {icon_filename}! Sẽ dùng icon mặc định.")
        icon_path = None

    build_cmd = [
        "uv", "run", "pyinstaller",
        "--noconsole",
        "--name", "MAVIS",
        "--collect-all", "fastembed",
        "--collect-all", "faster_whisper"
    ]
    
    if icon_path:
        # Sử dụng đường dẫn tuyệt đối (Absolute Path) để chắc chắn 100% PyInstaller tìm thấy
        build_cmd.append(f"--icon={str(icon_path)}")
        
    build_cmd.append("main.py")

    try:
        subprocess.run(build_cmd, check=True)
    except subprocess.CalledProcessError:
        print("\n❌ LỖI: Quá trình biên dịch thất bại. Hãy kiểm tra lại code.")
        return

    print("\n📂 Bước 2: Bổ sung dữ liệu ngầm (Từ điển phát âm)...")
    
    # Tìm thư mục espeak-ng-data (Hỗ trợ cả tên gói piper và piper_phonemize)
    espeak_src_1 = BASE_DIR / ".venv" / "Lib" / "site-packages" / "piper" / "espeak-ng-data"
    espeak_src_2 = BASE_DIR / ".venv" / "Lib" / "site-packages" / "piper_phonemize" / "espeak-ng-data"
    
    espeak_src = espeak_src_1 if espeak_src_1.exists() else (espeak_src_2 if espeak_src_2.exists() else None)

    if espeak_src:
        # Dán cạnh file exe (Ưu tiên số 1)
        espeak_dest_root = DIST_DIR / "espeak-ng-data"
        if espeak_dest_root.exists():
            shutil.rmtree(espeak_dest_root)
        shutil.copytree(espeak_src, espeak_dest_root)
        print(" ✅ Đã dán từ điển phát âm vào thư mục gốc.")
        
        # Dán vào _internal/piper (Dự phòng)
        espeak_dest_internal = INTERNAL_DIR / "piper" / "espeak-ng-data"
        os.makedirs(espeak_dest_internal.parent, exist_ok=True)
        if espeak_dest_internal.exists():
            shutil.rmtree(espeak_dest_internal)
        shutil.copytree(espeak_src, espeak_dest_internal)
    else:
        print(" ⚠️ Không tìm thấy thư mục espeak-ng-data. App có thể bị lỗi phát âm.")

    print("\n🔒 Bước 3: Tạo cấu hình bảo mật cho người dùng mới...")
    
    # Tuyệt đối không copy file .env của máy host. Tạo file .env mẫu trắng.
    env_example_path = DIST_DIR / ".env"
    with open(env_example_path, "w", encoding="utf-8") as f:
        f.write("# === CAU HINH J.A.R.V.I.S ===\n")
        f.write("GROQ_API_KEY=your_groq_api_key_here\n")
        f.write("# GEMINI_API_KEY=your_gemini_api_key_here\n")
    print(" ✅ Đã tạo file .env trống (Đảm bảo an toàn API Key của bạn).")

    # Tạo file hướng dẫn sử dụng cho người được share app
    readme_path = DIST_DIR / "HUONG_DAN_CAI_DAT.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write("    HUONG DAN CAI DAT J.A.R.V.I.S (AI ASSISTANT)  \n")
        f.write("==================================================\n\n")
        f.write("Chao mung ban den voi he thong J.A.R.V.I.S!\n\n")
        f.write("De ung dung co the hoat dong va suy nghi, ban can cung cap cho no mot 'Bo nao' (API Key).\n")
        f.write("Hay lam theo 3 buoc cuc ky don gian sau:\n\n")
        f.write("Buoc 1: Truc cap trang web https://console.groq.com/keys va tao mot tai khoan mien phi.\n")
        f.write("Buoc 2: Nhan tao API Key moi (Create API Key) va copy doan ma do.\n")
        f.write("Buoc 3: Mo file '.env' o ngay trong thu muc nay bang Notepad.\n")
        f.write("        Xoa dong chu 'your_groq_api_key_here' va dan API Key cua ban vao do.\n")
        f.write("        Luu file lai (Ctrl + S).\n\n")
        f.write("XONG! Bay gio ban chi can click dup vao file JARVIS.exe de danh thuc tro ly cua rieng ban.\n")
    print(" ✅ Đã tạo file HUONG_DAN_CAI_DAT.txt cho người dùng mới.")

    print("\n🧹 Bước 4: Dọn dẹp không gian làm việc (Xóa rác)...")
    build_temp_dir = BASE_DIR / "build"
    spec_file = BASE_DIR / "JARVIS.spec"
    
    try:
        if build_temp_dir.exists():
            shutil.rmtree(build_temp_dir)
            print(" ✅ Đã xóa thư mục nháp 'build'.")
        if spec_file.exists():
            os.remove(spec_file)
            print(" ✅ Đã xóa file cấu hình 'JARVIS.spec'.")
    except Exception as e:
        print(f" ⚠️ Không thể dọn dẹp hoàn toàn: {e}")

    print("\n" + "="*60)
    print("🎉 ĐÓNG GÓI BẢN RELEASE HOÀN TẤT THÀNH CÔNG!")
    print(f"👉 Thư mục an toàn để nén (.zip) và gửi cho bạn bè:\n   {DIST_DIR}")
    print("="*60)

if __name__ == "__main__":
    main()