import sys
import time
import math
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                             QWidget, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QRectF
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QPainterPath

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

        is_active = False

        while True:
            try:
                if not is_active:
                    self.status_signal.emit("STANDBY")
                    standby_audio = stt.record_audio(duration=3)
                    standby_text = stt.transcribe(standby_audio).lower()
                    
                    if "jarvis" in standby_text:
                        is_active = True
                        self.status_signal.emit("WAKE")
                        self.log_signal.emit("🔔 [WAKE] Hệ thống đã được đánh thức!")
                        tts.speak("Yes, sir? I am listening.")
                    else:
                        time.sleep(0.5)
                        
                else:
                    self.status_signal.emit("LISTENING...")
                    command_audio = stt.record_audio(duration=6)
                    command_text = stt.transcribe(command_audio)
                    
                    if not command_text or len(command_text) < 3:
                        continue
                        
                    self.log_signal.emit(f"🗣️ You: '{command_text}'")
                    
                    if "standby" in command_text.lower() or "stand by" in command_text.lower():
                        is_active = False
                        self.status_signal.emit("STANDBY")
                        tts.speak("Standing by, sir.")
                        continue
                    
                    if "goodbye" in command_text.lower() or "shut down" in command_text.lower():
                        tts.speak("Goodbye sir. Shutting down systems.")
                        time.sleep(1)
                        self.status_signal.emit("SHUTDOWN")
                        break
                        
                    self.status_signal.emit("THINKING...")
                    response = jarvis.ask(command_text)
                    
                    self.log_signal.emit(f"🎵 Jarvis: {response}")
                    self.status_signal.emit("SPEAKING...")
                    tts.speak(response)
                    
            except Exception as e:
                self.log_signal.emit(f"❌ Lỗi: {str(e)}")
                time.sleep(1)

class SoundWaveWidget(QWidget):
    """Khung vẽ đồ họa Sóng Âm (Waveform & EQ Bars) mô phỏng ảnh yêu cầu"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(350, 80)
        self.phase = 0.0
        
        # Các thông số vật lý của sóng âm (Sẽ nội suy mượt mà)
        self.current_amplitude = 5.0
        self.target_amplitude = 5.0
        self.current_speed = 0.1
        self.target_speed = 0.1
        
        self.status = "BOOTING"
        self.status_color = QColor(0, 229, 255) # Lục lam mặc định
        
        # Sinh ra độ lệch ngẫu nhiên cho các cột EQ để nhìn tự nhiên hơn
        self.eq_offsets = [random.uniform(0, math.pi * 2) for _ in range(60)]
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30) # ~33fps
        
    def update_state(self, status):
        self.status = status
        # Cấu hình biên độ (độ cao sóng) và tốc độ cho từng trạng thái
        if status == "STANDBY":
            self.status_color = QColor(0, 150, 255, 180) 
            self.target_amplitude = 5.0  # Sóng gợn nhẹ
            self.target_speed = 0.05     # Trôi rất chậm
        elif status == "LISTENING...":
            self.status_color = QColor(0, 255, 128, 255) 
            self.target_amplitude = 15.0 # Mở rộng để hứng âm thanh
            self.target_speed = 0.2
        elif status == "THINKING...":
            self.status_color = QColor(255, 170, 0, 255) 
            self.target_amplitude = 8.0  # Sóng đều đặn, tập trung
            self.target_speed = 0.3      # Suy nghĩ nhanh
        elif status == "SPEAKING...":
            self.status_color = QColor(0, 229, 255, 255) 
            self.target_amplitude = 35.0 # Đập cực mạnh, nhấp nhô lớn
            self.target_speed = 0.4
        else:
            self.status_color = QColor(255, 0, 85, 255)
            self.target_amplitude = 5.0
            self.target_speed = 0.1
            
    def animate(self):
        # Nội suy (Lerp) để sóng âm chuyển trạng thái mượt mà không bị giật cục
        self.current_amplitude += (self.target_amplitude - self.current_amplitude) * 0.1
        self.current_speed += (self.target_speed - self.current_speed) * 0.1
        
        self.phase += self.current_speed
        self.update() # Yêu cầu vẽ lại màn hình
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        mid_y = height / 2
        
        # 1. Vẽ các đường cong mềm mại (Sine waves) trôi dạt phía sau
        path1 = QPainterPath()
        path2 = QPainterPath()
        path1.moveTo(0, mid_y)
        path2.moveTo(0, mid_y)
        
        for x in range(0, width, 5):
            # Tính toán hình sin phức hợp tạo sự tự nhiên
            y_offset1 = math.sin((x * 0.02) + self.phase) * self.current_amplitude * 0.8
            y_offset2 = math.cos((x * 0.015) - self.phase * 1.2) * self.current_amplitude * 0.6
            
            path1.lineTo(x, mid_y + y_offset1)
            path2.lineTo(x, mid_y + y_offset2)
            
        pen_curve1 = QPen(QColor(self.status_color.red(), self.status_color.green(), self.status_color.blue(), 100), 1.5)
        pen_curve2 = QPen(QColor(self.status_color.red(), self.status_color.green(), self.status_color.blue(), 60), 2.5)
        
        painter.setPen(pen_curve2)
        painter.drawPath(path2)
        painter.setPen(pen_curve1)
        painter.drawPath(path1)
        
        # 2. Vẽ các cột EQ Bar thẳng đứng giống bức ảnh yêu cầu
        num_bars = 60
        bar_width = width / num_bars
        pen_bar = QPen(self.status_color, 2)
        pen_bar.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bar)
        
        for i in range(num_bars):
            x = i * bar_width + (bar_width / 2)
            
            # Chiều cao của từng cột phụ thuộc vào vị trí X, phase hiện tại và độ lệch ngẫu nhiên tĩnh
            # Trong lúc nói (SPEAKING), thêm một chút nhiễu (noise) ngẫu nhiên để giống phổ âm thanh thật
            noise = random.uniform(0.5, 1.5) if self.status == "SPEAKING..." else 1.0
            
            bar_h = math.fabs(math.sin((i * 0.1) + self.phase + self.eq_offsets[i])) * self.current_amplitude * noise
            
            # Vẽ nét đứt từ tâm ra 2 phía trên dưới
            painter.drawLine(int(x), int(mid_y - bar_h), int(x), int(mid_y + bar_h))


class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        self.worker = JarvisWorker()
        self.worker.status_signal.connect(self.update_status)
        
        # Vẫn bắt tín hiệu log nhưng chỉ in ra Terminal (Console), không hiện lên màn hình UI nữa
        self.worker.log_signal.connect(lambda msg: print(msg)) 
        
        self.worker.start()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Chuyển form thành hình chữ nhật ngang nhỏ gọn
        self.setFixedSize(450, 160) 
        
        self.central_widget = QFrame()
        self.central_widget.setObjectName("MainFrame")
        self.central_widget.setStyleSheet("""
            #MainFrame {
                background-color: rgba(10, 15, 25, 0.6);
                border: 1px solid rgba(0, 229, 255, 0.3);
                border-radius: 15px;
            }
        """)
        
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 229, 255, 50))
        glow.setOffset(0, 0)
        self.central_widget.setGraphicsEffect(glow)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)

        # -- KHU VỰC TEXT HEADER --
        header_layout = QHBoxLayout()
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        self.title_label = QLabel("J.A.R.V.I.S.")
        self.title_label.setStyleSheet("color: #00E5FF; font-family: 'Courier New'; font-size: 20px; font-weight: bold; letter-spacing: 5px;")
        
        self.status_label = QLabel("SYSTEM: BOOTING")
        self.status_label.setStyleSheet("color: #FF0055; font-family: 'Consolas'; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.status_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # -- KHU VỰC SÓNG ÂM (Trọng tâm) --
        # Đã loại bỏ khung Chat Log
        self.sound_wave = SoundWaveWidget()
        main_layout.addWidget(self.sound_wave)

        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def update_status(self, status):
        if status == "SHUTDOWN":
            QApplication.quit()
            return
            
        self.status_label.setText(f"STATUS: {status}")
        self.sound_wave.update_state(status)
        
        if status == "STANDBY":
            self.status_label.setStyleSheet("color: #4A90E2; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")
        elif status == "LISTENING...":
            self.status_label.setStyleSheet("color: #00FF80; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")
        elif status == "THINKING...":
            self.status_label.setStyleSheet("color: #FFAA00; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #00E5FF; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")

    # Cho phép kéo thả ứng dụng trên màn hình
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