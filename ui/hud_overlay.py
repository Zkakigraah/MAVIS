import math
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen

class HologramSphereWidget(QWidget):
    """Khung vẽ giả lập 3D (Pseudo-3D) Quả cầu Hologram lơ lửng"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(250, 250)
        self.phase = 0.0
        
        # Biến trạng thái mượt mà
        self.current_radius = 50.0
        self.target_radius = 50.0
        self.rotation_speed = 1.0
        self.pulse_amplitude = 2.0
        
        self.status = "BOOTING"
        self.color = QColor(0, 229, 255, 200) # Lục lam
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30) # ~33fps
        
    def update_state(self, status):
        self.status = status
        if status == "STANDBY":
            self.color = QColor(0, 150, 255, 150) # Xanh lam nhạt, ngủ yên
            self.target_radius = 45.0
            self.rotation_speed = 0.8
            self.pulse_amplitude = 1.0
        elif status == "LISTENING":
            self.color = QColor(0, 255, 128, 220) # Xanh lá đón lệnh
            self.target_radius = 70.0
            self.rotation_speed = 2.5
            self.pulse_amplitude = 4.0
        elif status == "THINKING":
            self.color = QColor(255, 170, 0, 255) # Cam/Vàng rực rỡ (Lõi Reactor)
            self.target_radius = 60.0
            self.rotation_speed = 8.0 # Xoay cực mạnh khi não bộ đang vắt kiệt
            self.pulse_amplitude = 2.0
        elif status == "SPEAKING":
            self.color = QColor(0, 229, 255, 255) # Lục lam
            self.target_radius = 80.0
            self.rotation_speed = 4.0
            self.pulse_amplitude = 12.0 # Đập nhịp điệu lớn
        else:
            self.color = QColor(255, 0, 85, 255) # Đỏ (Booting/Error)
            self.target_radius = 40.0
            self.rotation_speed = 1.0
            self.pulse_amplitude = 0.0
            
    def animate(self):
        # Lerp radius (Chuyển đổi kích thước mượt mà)
        self.current_radius += (self.target_radius - self.current_radius) * 0.1
        self.phase += self.rotation_speed
        if self.phase > 360000:
            self.phase = 0
        self.update() # Vẽ lại frame mới
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx = self.width() / 2
        cy = self.height() / 2
        
        # Nhịp đập (Pulse)
        pulse = math.sin(self.phase * 0.1) * self.pulse_amplitude
        base_r = self.current_radius + pulse
        
        painter.translate(cx, cy)
        
        # 1. Vẽ Lõi trung tâm phát sáng
        painter.setBrush(QColor(self.color.red(), self.color.green(), self.color.blue(), 40))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(-base_r*0.2, -base_r*0.2, base_r*0.4, base_r*0.4))
        
        # 2. Vẽ các vòng quỹ đạo (Pseudo 3D Rings)
        num_rings = 7
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        for i in range(num_rings):
            painter.save()
            
            # Tính toán bán kính và độ mờ của từng vòng
            ring_r = base_r * (0.4 + i * 0.18)
            alpha = max(20, min(255, int(255 - (i * 25))))
            ring_color = QColor(self.color.red(), self.color.green(), self.color.blue(), alpha)
            
            pen = QPen(ring_color, 1.5 + (i * 0.3))
            
            # Tạo hiệu ứng vạch đứt gãy phong cách Cyber/Hologram
            if i % 3 == 0:
                pen.setStyle(Qt.PenStyle.DashLine)
            elif i % 2 == 0:
                pen.setStyle(Qt.PenStyle.DotLine)
            else:
                pen.setStyle(Qt.PenStyle.DashDotLine)
                
            painter.setPen(pen)
            
            # Xoay 2D (Quay quanh trục Z)
            direction = 1 if i % 2 == 0 else -1
            painter.rotate(self.phase * direction * (0.3 + i * 0.15))
            
            # Giả lập 3D (Bóp méo trục Y bằng hàm Sine để tạo cảm giác bị nghiêng)
            tilt = math.sin((self.phase * 0.015) + i) * 0.7 + 0.3
            tilt = max(0.05, min(1.0, math.fabs(tilt))) 
            
            painter.scale(1.0, tilt)
            
            painter.drawEllipse(QRectF(-ring_r, -ring_r, ring_r * 2, ring_r * 2))
            painter.restore()

class HUDOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Hình vuông hoàn hảo cho Quả cầu 3D
        self.setFixedSize(250, 250) 
        
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background: transparent;")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.hologram = HologramSphereWidget()
        main_layout.addWidget(self.hologram)

        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def set_state(self, status):
        """Hàm được gọi từ main.py để thay đổi trạng thái của Hologram"""
        self.hologram.update_state(status)

    # Các hàm hỗ trợ kéo thả quả cầu trên màn hình bằng chuột
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