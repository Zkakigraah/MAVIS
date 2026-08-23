import os
import time
import base64
import psutil
import pyautogui
import comtypes
import screen_brightness_control as sbc
from PIL import ImageGrab
from openai import OpenAI
from memory.qdrant_db import memory_db
import webbrowser
import urllib.parse

# Tắt cảnh báo cú pháp (SyntaxWarning) gây rác màn hình của thư viện WMI
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="wmi")

def search_knowledge(query: str) -> str:
    """Tìm kiếm thông tin cá nhân trong bộ nhớ Vector."""
    print(f"🔎 [RAG] Đang tìm kiếm trong ký ức: '{query}'")
    results = memory_db.search(query, limit=3)
    if not results:
        return "No relevant information found in local memory."
    return "\n".join(results)

def search_internet(query: str) -> str:
    """Tra cứu thông tin cơ bản trên Internet."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            if results:
                return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            return "No results found on the internet."
    except ImportError:
        return "Internet search module not installed. Sir, please run: uv add duckduckgo-search"

def open_application(app_name: str) -> str:
    """Mở ứng dụng bằng cách mô phỏng thao tác gõ phím của con người."""
    print(f"🖥️ [SYSTEM] Đang mở ứng dụng: {app_name}")
    try:
        # Nhấn phím Windows để mở Start Menu
        pyautogui.hotkey('win')
        time.sleep(0.5)
        # Gõ tên ứng dụng
        pyautogui.write(app_name, interval=0.05)
        time.sleep(0.5)
        # Nhấn Enter để mở
        pyautogui.press('enter')
        
        # Trả về câu lệnh thành công để AI tự tin phản hồi
        return f"Action complete: Successfully opened {app_name}."
    except Exception as e:
        return f"Error opening application: {str(e)}"

def open_website(url: str) -> str:
    """Mở một trang web trên trình duyệt mặc định."""
    print(f"🌐 [WEB] Đang mở trang web: {url}")
    try:
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Action complete: Successfully opened {url}"
    except Exception as e:
        return f"Error opening website: {str(e)}"

def play_youtube(query: str) -> str:
    """Tìm kiếm và phát video trên YouTube."""
    print(f"▶️ [YOUTUBE] Đang mở YouTube cho từ khóa: {query}")
    try:
        query_string = urllib.parse.urlencode({"search_query": query})
        url = "https://www.youtube.com/results?" + query_string
        webbrowser.open(url)
        return f"Action complete: Opened YouTube search for '{query}'. Sir, you can now select the video."
    except Exception as e:
        return f"Error playing YouTube: {str(e)}"

def get_system_status() -> str:
    """Lấy thông tin CPU, RAM, Pin và Âm lượng."""
    try:
        # 1. CPU & RAM
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        ram_gb = ram.used / (1024**3)
        ram_total_gb = ram.total / (1024**3)
        
        # 2. Battery
        battery = psutil.sensors_battery()
        bat_percent = battery.percent if battery else 100
        bat_plugged = "charging" if (battery and battery.power_plugged) else "on battery"
        if not battery:
            bat_plugged = "desktop power"
        
        # 3. Volume (Được bọc cẩn thận trong luồng COM)
        vol_str = "unknown"
        try:
            comtypes.CoInitialize()
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            current_vol = round(volume.GetMasterVolumeLevelScalar() * 100)
            vol_str = f"{current_vol}%"
        except Exception as e:
            vol_str = f"error ({str(e)})"
        finally:
            comtypes.CoUninitialize() 
            
        status = (
            f"- CPU usage: {cpu}%\n"
            f"- RAM usage: {ram.percent}% ({ram_gb:.2f}GB of {ram_total_gb:.2f}GB)\n"
            f"- Battery: {bat_percent}% ({bat_plugged})\n"
            f"- Volume: {vol_str}"
        )
        print(f"📊 [STATUS]\n{status}")
        return status
    except Exception as e:
        return f"Failed to get system status: {str(e)}"

def control_system(action: str, volume_level: int = None, brightness_level: int = None) -> str:
    """Điều khiển sâu vào các thông số phần cứng Windows."""
    print(f"⚙️ [CONTROL] Action: {action} | Vol: {volume_level} | Brightness: {brightness_level}")
    try:
        if action == "lock_screen":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Screen locked successfully."
            
        elif action == "play_pause":
            pyautogui.press('playpause')
            return "Media toggled."
            
        elif action == "mute":
            pyautogui.press('volumemute')
            return "System muted."
            
        elif action == "volume_up":
            pyautogui.press('volumeup', presses=5)
            return "Volume increased."
            
        elif action == "volume_down":
            pyautogui.press('volumedown', presses=5)
            return "Volume decreased."
            
        elif action == "set_volume" and volume_level is not None:
            comtypes.CoInitialize()
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                target_vol = max(0, min(100, volume_level)) / 100.0
                volume.SetMasterVolumeLevelScalar(target_vol, None)
                return f"Volume set to {volume_level}%."
            finally:
                comtypes.CoUninitialize()
                
        elif action == "set_brightness" and brightness_level is not None:
            target_brightness = max(0, min(100, brightness_level))
            sbc.set_brightness(target_brightness)
            return f"Brightness set to {target_brightness}%."
            
        elif action == "brightness_up":
            current = sbc.get_brightness()[0]
            sbc.set_brightness(min(100, current + 15))
            return "Brightness increased."
            
        elif action == "brightness_down":
            current = sbc.get_brightness()[0]
            sbc.set_brightness(max(0, current - 15))
            return "Brightness decreased."
            
        return f"Action '{action}' executed successfully."
    except Exception as e:
        return f"Error controlling system: {str(e)}"

def analyze_screen(prompt: str = "What is on the screen?") -> str:
    """
    Chụp màn hình hiện tại và gửi cho mô hình Vision để phân tích.
    """
    print(f"🔎 [VISION] Đang chụp và phân tích màn hình với yêu cầu: '{prompt}'...")
    try:
        workspace_dir = os.path.join(os.path.dirname(__file__), '..', 'workspace', 'outputs')
        os.makedirs(workspace_dir, exist_ok=True)
        img_path = os.path.join(workspace_dir, "vision_temp.jpg")

        img = ImageGrab.grab()
        img.thumbnail((1920, 1080))
        img.save(img_path, format="JPEG", quality=80)

        with open(img_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return "System error: GROQ_API_KEY not found in environment."

        # Đã cập nhật đúng tên model Vision của Groq
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000
        )
        
        result = response.choices[0].message.content
        print(f"✅ [VISION] Hoàn tất phân tích.")
        return f"Screen analysis result from Vision Sub-processor: {result}"

    except Exception as e:
        print(f"❌ [VISION ERROR]: {e}")
        return f"Failed to analyze screen due to an error: {str(e)}"

def read_file(file_path: str) -> str:
    """Đọc nội dung từ một file text hoặc code."""
    print(f"📄 [FILE] Đang đọc file: {file_path}")
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Ghi nội dung vào một file mới."""
    print(f"📝 [FILE] Đang ghi file: {file_path}")
    try:
        # Tự động tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Action complete: Successfully wrote content to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def take_screenshot() -> str:
    """Chụp ảnh màn hình và lưu vào thư mục outputs mà không cần qua mô hình Vision."""
    print("📸 [SYSTEM] Đang chụp ảnh màn hình...")
    try:
        workspace_dir = os.path.join(os.path.dirname(__file__), '..', 'workspace', 'outputs')
        os.makedirs(workspace_dir, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        img_path = os.path.join(workspace_dir, f"screenshot_{timestamp}.png")
        
        img = ImageGrab.grab()
        img.save(img_path, format="PNG")
        
        return f"Action complete: Screenshot saved to {img_path}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"