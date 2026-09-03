import os
import sys
import subprocess
import webbrowser
import urllib.parse
import psutil
import pyautogui
from PIL import ImageGrab
from core.config import is_safe_path, WORKSPACE_DIR, TEMP_DIR

OUTPUTS_DIR = os.path.join(WORKSPACE_DIR, "outputs")
PERSONAL_DOCS_DIR = os.path.join(WORKSPACE_DIR, "personal_docs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(PERSONAL_DOCS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except ImportError:
    SBC_AVAILABLE = False


def _get_volume_control():
    if not PYCAW_AVAILABLE:
        return None
    try:
        devices = AudioUtilities.GetSpeakers()
        if hasattr(devices, 'Activate'):
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        else:
            interface = devices.EndpointVolume
        return interface.QueryInterface(IAudioEndpointVolume) if hasattr(interface, 'QueryInterface') else interface
    except Exception:
        return None


def search_knowledge(query: str) -> str:
    from memory.qdrant_db import QdrantDB
    try:
        db = QdrantDB()
        results = db.search(query, limit=3)
        if not results:
            return "No matching records found in long-term memory."
        return "\n".join([f"- {r.payload.get('text', '')}" for r in results])
    except Exception as e:
        return f"Memory query failure: {e}"


def open_application(app_name: str) -> str:
    try:
        app_name_clean = app_name.strip()
        pyautogui.press('win')
        pyautogui.write(app_name_clean, interval=0.03)
        pyautogui.press('enter')
        return f"Executed launch sequence for application: {app_name_clean}"
    except Exception as e:
        return f"Failed to open application: {e}"


def open_website(url: str) -> str:
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Navigated to website: {url}"
    except Exception as e:
        return f"Navigation failed: {e}"


def play_youtube(search_query: str) -> str:
    try:
        encoded_query = urllib.parse.quote_plus(search_query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(url)
        return f"Query dispatched to YouTube: {search_query}"
    except Exception as e:
        return f"YouTube query failed: {e}"


def search_internet(query: str) -> str:
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "No search results returned from search engine."
            formatted = []
            for r in results:
                formatted.append(f"Title: {r.get('title', '')}\nSnippet: {r.get('body', '')}\nLink: {r.get('href', '')}")
            return "\n\n".join(formatted)
    except Exception as e:
        return f"Web search failed: {e}"


def get_system_status() -> str:
    try:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        
        status = [
            f"CPU Usage: {cpu}%",
            f"RAM Usage: {ram.percent}% ({ram.used / (1024**3):.2f}GB / {ram.total / (1024**3):.2f}GB)"
        ]
        
        if battery:
            status.append(f"Battery: {battery.percent}% ({'Plugged In' if battery.power_plugged else 'On Battery'})")
        else:
            status.append("Battery: AC Connected (No Battery Detected)")
            
        vol_ctrl = _get_volume_control()
        if vol_ctrl:
            try:
                current_vol = int(round(vol_ctrl.GetMasterVolumeLevelScalar() * 100))
                is_muted = bool(vol_ctrl.GetMute())
                status.append(f"Master Volume: {current_vol}%{' (Muted)' if is_muted else ''}")
            except Exception:
                status.append("Master Volume: Unavailable")
        
        if SBC_AVAILABLE:
            try:
                brightness = sbc.get_brightness()
                status.append(f"Display Brightness: {brightness[0]}%")
            except Exception:
                status.append("Display Brightness: Unavailable")

        return "\n".join(status)
    except Exception as e:
        return f"System telemetry retrieval failed: {e}"


def control_system(action: str, value: int = None) -> str:
    action_lower = action.lower().strip()
    
    if action_lower in ["shutdown_pc", "power_off_pc"]:
        subprocess.run(["shutdown", "/s", "/t", "5"], shell=True)
        return "Operating system power-down initiated (5-second grace period)."
        
    elif action_lower in ["restart_pc"]:
        subprocess.run(["shutdown", "/r", "/t", "5"], shell=True)
        return "Operating system restart initiated."
        
    elif action_lower in ["lock_workstation", "lock_screen"]:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked successfully."
        
    elif action_lower in ["exit_mavis", "close_mavis", "terminate_app"]:
        # Do not terminate immediately here; return confirmation so the LLM and TTS can speak first
        return "MAVIS application termination sequence confirmed. Bid the user farewell."

    elif "volume" in action_lower or action_lower in ["mute", "unmute"]:
        vol_ctrl = _get_volume_control()
        if not vol_ctrl:
            return "Audio endpoint interface unavailable."
        try:
            if action_lower == "volume_up":
                curr = vol_ctrl.GetMasterVolumeLevelScalar()
                vol_ctrl.SetMasterVolumeLevelScalar(min(1.0, curr + 0.1), None)
                return f"Volume set to {int(min(1.0, curr + 0.1) * 100)}%."
            elif action_lower == "volume_down":
                curr = vol_ctrl.GetMasterVolumeLevelScalar()
                vol_ctrl.SetMasterVolumeLevelScalar(max(0.0, curr - 0.1), None)
                return f"Volume set to {int(max(0.0, curr - 0.1) * 100)}%."
            elif action_lower == "set_volume" and value is not None:
                scalar = max(0.0, min(100.0, float(value))) / 100.0
                vol_ctrl.SetMasterVolumeLevelScalar(scalar, None)
                return f"Volume calibrated to {int(value)}%."
            elif action_lower == "mute":
                vol_ctrl.SetMute(1, None)
                return "Audio output muted."
            elif action_lower == "unmute":
                vol_ctrl.SetMute(0, None)
                return "Audio output unmuted."
        except Exception as e:
            return f"Audio manipulation error: {e}"

    elif "brightness" in action_lower:
        if not SBC_AVAILABLE:
            return "Display brightness control library unavailable."
        try:
            if action_lower == "brightness_up":
                curr = sbc.get_brightness()[0]
                new_val = min(100, curr + 10)
                sbc.set_brightness(new_val)
                return f"Brightness adjusted to {new_val}%."
            elif action_lower == "brightness_down":
                curr = sbc.get_brightness()[0]
                new_val = max(0, curr - 10)
                sbc.set_brightness(new_val)
                return f"Brightness adjusted to {new_val}%."
            elif action_lower == "set_brightness" and value is not None:
                target = max(0, min(100, int(value)))
                sbc.set_brightness(target)
                return f"Brightness calibrated to {target}%."
        except Exception as e:
            return f"Brightness manipulation error: {e}"

    return f"Unrecognized system action parameter: '{action}'."


def analyze_screen(prompt: str) -> str:
    try:
        temp_img_path = os.path.join(TEMP_DIR, "vision_temp.jpg")
        screenshot = ImageGrab.grab()
        screenshot.save(temp_img_path, format="JPEG", quality=85)
        
        import base64
        with open(temp_img_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
        from groq import Groq
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            model="llama-3.2-11b-vision-preview",
            max_tokens=512
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Vision processing failed: {e}"


def write_file(filename: str = None, file_path: str = None, content: str = "") -> str:
    target_name = filename or file_path
    if not target_name:
        return "Write failed: Target filename not provided."
    safe_target = os.path.basename(target_name)
    destination = os.path.join(OUTPUTS_DIR, safe_target)
    if not is_safe_path(destination):
        return "Write failed: Destination path outside configured sandbox boundary."
    try:
        with open(destination, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File successfully written to: {destination}"
    except Exception as e:
        return f"File write error: {e}"


def read_file(filename: str = None, file_path: str = None) -> str:
    target_name = filename or file_path
    if not target_name:
        return "Read failed: Source filename not provided."
    safe_target = os.path.basename(target_name)
    destination = os.path.join(OUTPUTS_DIR, safe_target)
    if not is_safe_path(destination):
        return "Read failed: Source path outside configured sandbox boundary."
    try:
        if not os.path.exists(destination):
            return f"Read failed: File '{safe_target}' does not exist."
        with open(destination, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"File read error: {e}"


def take_screenshot(filename: str = None, file_path: str = None) -> str:
    target_name = filename or file_path or "screenshot.png"
    safe_target = os.path.basename(target_name)
    if not safe_target.endswith(".png") and not safe_target.endswith(".jpg"):
        safe_target += ".png"
    destination = os.path.join(OUTPUTS_DIR, safe_target)
    if not is_safe_path(destination):
        return "Screenshot failed: Destination path outside configured sandbox boundary."
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(destination)
        return f"Display captured and saved to: {destination}"
    except Exception as e:
        return f"Screen capture error: {e}"


def remember_information(fact: str) -> str:
    try:
        from memory.qdrant_db import QdrantDB
        db = QdrantDB()
        db.add_texts([fact])
        
        persist_file = os.path.join(PERSONAL_DOCS_DIR, "auto_learned_facts.txt")
        with open(persist_file, "a", encoding="utf-8") as f:
            f.write(fact.strip() + "\n")
            
        return f"Stored into long-term vector memory: '{fact}'"
    except Exception as e:
        return f"Memory persistence failure: {e}"