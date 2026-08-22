import sys
import re
import time
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTextEdit, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QRectF
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPen, QBrush

# Import AI Core
from core.stt_engine import STTEngine
from core.tts_engine import TTSEngine
from core.llm_agent import jarvis

class JarvisWorker(QThread):
    """Luồng xử lý ngầm (Background Thread) cho J.A.R.V.I.S"""
    status_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def run(self):
        self.status_signal.emit("BOOTING")
        self.log_signal.emit("🤖 Khởi động các hệ thống quang học...")
        
        stt = STTEngine(model_size="base")
        tts = TTSEngine()
        
        self.log_signal.emit("✅ Hệ thống đã sẵn sàng.")
        tts.speak("System is online. Awaiting your command, sir.")

        # Biến trạng thái: Đang trong cuộc trò chuyện liên tục hay không?
        is_active = False

        while True:
            try:
                if not is_active:
                    # Giai đoạn 1: STANDBY (Ngủ đông chờ gọi tên)
                    self.status_signal.emit("STANDBY")
                    standby_audio = stt.record_audio(duration=3)
                    standby_text = stt.transcribe(standby_audio).lower()
                    clean_text = re.sub(r'[^\w\s]', '', standby_text)

                    if "wake up" in clean_text:
                        is_active = True # Chuyển sang chế độ đàm thoại liên tục
                        self.status_signal.emit("WAKE")
                        self.log_signal.emit("\n🔔 [WAKE] Hệ thống đã được đánh thức!")
                        tts.speak("Yes, sir? I am listening.")
                    else:
                        time.sleep(0.5)
                        
                else:
                    # Giai đoạn 2: ACTIVE (Đàm thoại liên tục)
                    self.status_signal.emit("LISTENING...")
                    command_audio = stt.record_audio(duration=6)
                    command_text = stt.transcribe(command_audio)
                    
                    if not command_text or len(command_text) < 3:
                        # Thay vì báo không nghe rõ, hệ thống cứ lặng lẽ tiếp tục nghe
                        continue
                        
                    self.log_signal.emit(f"🗣️ You: '{command_text}'")
                    
                    # Lệnh trở về trạng thái chờ
                    if "standby" in command_text.lower() or "stand by" in command_text.lower():
                        is_active = False
                        self.status_signal.emit("STANDBY")
                        self.log_signal.emit("🔄 Đưa hệ thống vào chế độ chờ...")
                        tts.speak("Standing by, sir.")
                        continue
                    
                    # Lệnh tắt hẳn hệ thống
                    if "goodbye" in command_text.lower() or "shut down" in command_text.lower():
                        self.log_signal.emit("Tắt hệ thống...")
                        tts.speak("Goodbye sir. Shutting down systems.")
                        time.sleep(1) # Chờ cho ngài quản gia nói xong hẳn
                        self.status_signal.emit("SHUTDOWN") # Mới phát lệnh đóng cửa sổ
                        break
                        
                    # Lệnh bình thường
                    self.status_signal.emit("THINKING...")
                    response = jarvis.ask(command_text)
                    
                    self.log_signal.emit(f"🎵 Jarvis: {response}")
                    self.status_signal.emit("SPEAKING...")
                    tts.speak(response)
                    
            except Exception as e:
                self.log_signal.emit(f"❌ Lỗi: {str(e)}")
                time.sleep(1)

class AICoreWidget(QWidget):
    """Widget tùy chỉnh vẽ lõi năng lượng có Hoạt ảnh Sóng âm"""
    def __init__(self):
        super().__init__()
        self.setFixedSize(120, 120)
        self.angle_outer = 0
        self.angle_inner = 0
        self.pulse_phase = 0.0 # Biến pha cho sóng âm dao động
        self.status = "BOOTING"
        self.status_color = QColor(0, 229, 255) # Mặc định màu Lục Lam (Cyan)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)
        
    def update_state(self, status):
        self.status = status
        # Đổi màu lõi dựa trên trạng thái
        if status == "STANDBY":
            self.status_color = QColor(0, 150, 255, 120) # Xanh dương mờ
        elif status == "LISTENING...":
            self.status_color = QColor(0, 255, 128, 255) # Xanh lá
        elif status == "THINKING...":
            self.status_color = QColor(255, 170, 0, 255) # Vàng cam
        elif status == "SPEAKING...":
            self.status_color = QColor(0, 229, 255, 255) # Lục lam
        else:
            self.status_color = QColor(255, 0, 85, 255)  # Đỏ (Lỗi hoặc Boot)
            
    def animate(self):
        # Tạo hiệu ứng xoay ngược chiều
        self.angle_outer = (self.angle_outer - 3) % 360
        self.angle_inner = (self.angle_inner + 5) % 360
        
        # Nhịp đập sóng âm (chạy liên tục)
        self.pulse_phase += 0.2
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Tính toán cường độ đập của sóng âm (Amplitude)
        pulse_amplitude = 5
        if self.status == "SPEAKING...":
            pulse_amplitude = 15 # Đập mạnh khi nói
        elif self.status == "LISTENING...":
            pulse_amplitude = 8  # Đập vừa khi nghe
        elif self.status == "STANDBY":
            pulse_amplitude = 2  # Thở nhẹ khi ngủ
            
        # Ánh sáng tỏa ra ở giữa co giãn theo hình sin (Soundwave pulse)
        pulse_radius = 60 + math.sin(self.pulse_phase) * pulse_amplitude
        
        glow_color = QColor(self.status_color.red(), self.status_color.green(), self.status_color.blue(), 40)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        center_offset = (120 - pulse_radius) / 2
        painter.drawEllipse(QRectF(center_offset, center_offset, pulse_radius, pulse_radius))
        
        # Vòng ngoài (Đứt quãng)
        pen_outer = QPen(self.status_color, 3)
        pen_outer.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_outer)
        painter.drawArc(10, 10, 100, 100, self.angle_outer * 16, 280 * 16)
        
        # Vòng trong (Đứt nét dạng chấm)
        pen_inner = QPen(self.status_color, 4)
        pen_inner.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen_inner)
        painter.drawArc(22, 22, 76, 76, self.angle_inner * 16, 360 * 16)
        
        # Lõi cứng bên trong cùng cố định
        pen_solid = QPen(self.status_color, 1)
        painter.setPen(pen_solid)
        painter.drawEllipse(35, 35, 50, 50)

class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        self.worker = JarvisWorker()
        self.worker.status_signal.connect(self.update_status)
        self.worker.log_signal.connect(self.update_log)
        self.worker.start()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, 550)
        
        self.central_widget = QFrame()
        self.central_widget.setObjectName("MainFrame")
        # Nền trong suốt 45% để không cản trở nội dung màn hình
        self.central_widget.setStyleSheet("""
            #MainFrame {
                background-color: rgba(8, 12, 18, 0.45);
                border: 1px solid rgba(0, 229, 255, 0.2);
                border-radius: 12px;
            }
        """)
        
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 229, 255, 60))
        glow.setOffset(0, 0)
        self.central_widget.setGraphicsEffect(glow)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)

        # -- KHU VỰC HEADER --
        header_layout = QHBoxLayout()
        self.ai_core = AICoreWidget()
        header_layout.addWidget(self.ai_core)
        
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.title_label = QLabel("J.A.R.V.I.S.")
        self.title_label.setStyleSheet("color: #00E5FF; font-family: 'Courier New'; font-size: 26px; font-weight: bold; letter-spacing: 4px;")
        
        self.subtitle_label = QLabel("MK. I TACTICAL INTERFACE")
        self.subtitle_label.setStyleSheet("color: #778899; font-family: 'Consolas'; font-size: 10px; letter-spacing: 1px;")
        
        self.status_label = QLabel("SYSTEM: BOOTING")
        self.status_label.setStyleSheet("color: #FF0055; font-family: 'Consolas'; font-size: 14px; font-weight: bold; margin-top: 10px;")
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)
        title_layout.addWidget(self.status_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("border-top: 1px solid rgba(0, 229, 255, 0.4); margin-top: 10px; margin-bottom: 10px;")
        main_layout.addWidget(separator)

        # -- KHU VỰC LOG --
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: rgba(0, 255, 204, 0.9);
                font-family: 'Consolas', 'Courier New';
                font-size: 13px;
                border: none;
                line-height: 1.5;
            }
        """)
        main_layout.addWidget(self.console_output)

        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def update_status(self, status):
        """Cập nhật Status Text, Màu Core và Xử lý Lệnh Đóng"""
        # Bắt sự kiện hệ thống báo Shut down để tắt UI
        if status == "SHUTDOWN":
            QApplication.quit()
            return
            
        self.status_label.setText(f"SYSTEM: {status}")
        self.ai_core.update_state(status)
        
        if status == "STANDBY":
            self.status_label.setStyleSheet("color: #4A90E2; font-family: 'Consolas'; font-size: 14px; font-weight: bold; margin-top: 10px;")
        elif status == "LISTENING...":
            self.status_label.setStyleSheet("color: #00FF80; font-family: 'Consolas'; font-size: 14px; font-weight: bold; margin-top: 10px;")
        elif status == "THINKING...":
            self.status_label.setStyleSheet("color: #FFAA00; font-family: 'Consolas'; font-size: 14px; font-weight: bold; margin-top: 10px;")
        else:
            self.status_label.setStyleSheet("color: #00E5FF; font-family: 'Consolas'; font-size: 14px; font-weight: bold; margin-top: 10px;")

    def update_log(self, message):
        self.console_output.append(message)
        scrollbar = self.console_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'old_pos'):
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        if hasattr(self, 'old_pos'):
            del self.old_pos