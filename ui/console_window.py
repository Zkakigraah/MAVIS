from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt

class ConsoleWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Cập nhật chuẩn hằng số (Enum) của PyQt6
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 15, 30, 200);
                color: #00FFFF;
                font-family: Consolas, monospace;
                font-size: 14px;
                border: 1px solid rgba(0, 255, 255, 50);
                border-radius: 8px;
                padding: 10px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 255, 255, 100);
                border-radius: 4px;
            }
        """)
        
        layout.addWidget(self.text_area)
        
    def append_log(self, role, text):
        if role == "USER":
            formatted_text = f"<span style='color: #00FF00;'>[YOU]:</span> {text}"
        elif role == "MAVIS":
            formatted_text = f"<span style='color: #00FFFF;'>[M.A.V.I.S]:</span> {text}"
        else:
            formatted_text = f"<span style='color: #AAAAAA;'>[{role}]:</span> {text}"
            
        self.text_area.append(formatted_text)
        
        # Đảm bảo cuộn xuống cuối cùng
        scrollbar = self.text_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def mousePressEvent(self, event):
        # Cập nhật chuẩn MouseButton của PyQt6
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # Cập nhật chuẩn MouseButton của PyQt6
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()