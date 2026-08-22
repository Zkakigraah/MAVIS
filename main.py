from core.stt_engine import STTEngine
from core.tts_engine import TTSEngine
from core.llm_agent import jarvis
import time
import re
import sys
from PyQt6.QtWidgets import QApplication
from ui.hud_overlay import JarvisHUD

def main():
    print("="*50)
    print("🤖 ĐANG KHỞI ĐỘNG GIAO DIỆN J.A.R.V.I.S HUD...")
    print("="*50)
    
    # Khởi tạo Application của PyQt6
    app = QApplication(sys.argv)
    
    # Tạo và hiển thị cửa sổ HUD
    hud = JarvisHUD()
    hud.show()
    
    # Chạy vòng lặp sự kiện của UI (Giữ cho app không bị tắt)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()