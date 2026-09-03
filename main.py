import sys
import threading
import os
import time
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QObject
from ui.hud_overlay import HUDOverlay
from ui.console_window import ConsoleWindow
from core.stt_engine import STTEngine
from core.tts_engine import TTSEngine
from core.llm_agent import LLMAgent

class LogEmitter(QObject):
    log_signal = pyqtSignal(str, str)

def run_ai_loop(hud, log_emitter):
    try:
        hud.set_state("THINKING")
        log_emitter.log_signal.emit("SYSTEM", "Initializing cognitive subsystems...")
        stt = STTEngine()
        tts = TTSEngine()
        llm = LLMAgent()
        
        is_awake = False
        hud.set_state("STANDBY")
        log_emitter.log_signal.emit("SYSTEM", "M.A.V.I.S. operational. Standby mode active.")
        
        while True:
            if not is_awake:
                hud.set_state("STANDBY")
                temp_audio = stt.record_audio(duration=3.0)
                text = stt.transcribe(temp_audio)
                
                if text:
                    text_lower = text.lower().replace(".", "").replace(",", "").replace("!", "").strip()
                    if "wake up" in text_lower:
                        is_awake = True
                        log_emitter.log_signal.emit("USER", "Wake up")
                        hud.set_state("SPEAKING")
                        tts.speak("System initialized and ready.")
                        log_emitter.log_signal.emit("MAVIS", "System initialized and ready.")
                        continue
            else:
                hud.set_state("LISTENING")
                temp_audio = stt.record_audio(duration=6.0)
                user_text = stt.transcribe(temp_audio)
                
                if not user_text:
                    continue
                    
                log_emitter.log_signal.emit("USER", user_text)
                user_text_lower = user_text.lower().replace(".", "").replace(",", "").replace("!", "").strip()
                
                # Deterministic app termination intercept (Does NOT shut down the PC)
                if user_text_lower in [
                    "shut down system",
                    "shut down the system",
                    "exit mavis",
                    "close mavis",
                    "terminate system",
                    "goodbye"
                ]:
                    hud.set_state("SPEAKING")
                    farewell = "Shutting down M.A.V.I.S. Goodbye, sir."
                    log_emitter.log_signal.emit("MAVIS", farewell)
                    tts.speak(farewell)
                    time.sleep(1.0)
                    os._exit(0)

                # Deterministic standby intercept
                if "go to sleep" in user_text_lower or user_text_lower in ["standby", "enter standby"]:
                    is_awake = False
                    hud.set_state("SPEAKING")
                    tts.speak("Entering standby mode.")
                    log_emitter.log_signal.emit("MAVIS", "Entering standby mode.")
                    continue
                    
                hud.set_state("THINKING")
                response_text = llm.chat(user_text)
                
                log_emitter.log_signal.emit("MAVIS", response_text)
                hud.set_state("SPEAKING")
                tts.speak(response_text)

                # If a tool call requested an application exit, terminate cleanly after speech finishes
                if getattr(llm, "should_exit", False):
                    time.sleep(1.0)
                    os._exit(0)
            
    except Exception as e:
        error_msg = f"Fatal AI Loop Error: {e}"
        print(error_msg)
        log_emitter.log_signal.emit("ERROR", error_msg)
        hud.set_state("STANDBY")

if __name__ == '__main__':
    class DummyOutput:
        def write(self, x): pass
        def flush(self): pass
    if sys.stdout is None: sys.stdout = DummyOutput()
    if sys.stderr is None: sys.stderr = DummyOutput()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    hud = HUDOverlay()
    hud.show()
    
    console = ConsoleWindow()
    
    tray_icon = QSystemTrayIcon(app)
    
    icon_path = "app_icon.ico"
    if os.path.exists(icon_path):
        tray_icon.setIcon(QIcon(icon_path))
    else:
        tray_icon.setIcon(app.style().standardIcon(app.style().StandardPixmap.SP_ComputerIcon))
        
    tray_menu = QMenu()
    
    toggle_console_action = QAction("Toggle Console Log", app)
    toggle_console_action.triggered.connect(console.toggle_visibility)
    tray_menu.addAction(toggle_console_action)
    
    quit_action = QAction("Exit M.A.V.I.S", app)
    quit_action.triggered.connect(app.quit)
    tray_menu.addAction(quit_action)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    log_emitter = LogEmitter()
    log_emitter.log_signal.connect(console.append_log)

    ai_thread = threading.Thread(target=run_ai_loop, args=(hud, log_emitter), daemon=True)
    ai_thread.start()

    sys.exit(app.exec())