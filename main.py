import sys
# --- BẢO VỆ CHỐNG CRASH KHI TẢI MODEL TRÊN MÁY MỚI ---
# Tạo một "lỗ đen" hứng toàn bộ thanh tiến trình tải Model để app không bị văng
class DummyWriter:
    def write(self, text): pass
    def flush(self): pass

if sys.stdout is None:
    sys.stdout = DummyWriter()
if sys.stderr is None:
    sys.stderr = DummyWriter()

from core.stt_engine import STTEngine
from core.tts_engine import TTSEngine
from core.llm_agent import jarvis
import time
import re
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from ui.hud_overlay import JarvisHUD

def create_tray_icon(app, hud):
    """Tạo biểu tượng J.A.R.V.I.S dưới khay hệ thống (Góc phải màn hình)"""
    # Tự động vẽ một biểu tượng Lõi năng lượng nhỏ
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor("transparent"))
    painter = QPainter(pixmap)
    painter.setBrush(QColor(0, 229, 255))
    painter.setPen(QColor(0, 150, 255))
    painter.drawEllipse(4, 4, 24, 24)
    painter.end()
    
    tray_icon = QSystemTrayIcon(QIcon(pixmap), app)
    tray_icon.setToolTip("J.A.R.V.I.S. System Core")
    
    # Tạo Menu chuột phải
    menu = QMenu()
    toggle_action = menu.addAction("Show / Hide HUD")
    toggle_action.triggered.connect(lambda: hud.hide() if hud.isVisible() else hud.show())
    
    menu.addSeparator()
    
    quit_action = menu.addAction("Shut Down System")
    quit_action.triggered.connect(app.quit)
    
    tray_icon.setContextMenu(menu)
    tray_icon.show()
    
    return tray_icon

def main():
    print("="*50)
    print("🤖 ĐANG KHỞI ĐỘNG GIAO DIỆN J.A.R.V.I.S HUD...")
    print("="*50)
    
    # Khởi tạo Application của PyQt6
    app = QApplication(sys.argv)
    
    # Đảm bảo app không bị tắt khi bạn chủ động ẩn cửa sổ HUD
    app.setQuitOnLastWindowClosed(False)
    
    # Tạo và hiển thị cửa sổ HUD
    hud = JarvisHUD()
    hud.show()
    
    # Tạo biểu tượng System Tray
    tray_icon = create_tray_icon(app, hud)
    
    # Chạy vòng lặp sự kiện của UI (Giữ cho app không bị tắt)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()