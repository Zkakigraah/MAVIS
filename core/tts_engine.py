import os
import io
import wave
import requests
import numpy as np
import sounddevice as sd
from pathlib import Path
from piper.voice import PiperVoice
from core.config import BASE_DIR, TEMP_DIR

MODEL_DIR = BASE_DIR / "models" / "tts"
# Đường dẫn tải Model Tiếng Anh (Giọng Nam Anh - British Male, phong cách quản gia AI)
MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alan/medium/en_GB-alan-medium.onnx"
CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"

class TTSEngine:
    def __init__(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        self.model_path = MODEL_DIR / "en_GB-alan-medium.onnx"
        self.config_path = MODEL_DIR / "en_GB-alan-medium.onnx.json"
        
        # Tải mô hình nếu chưa có (Chỉ cần tải 1 lần duy nhất)
        self._ensure_model_exists()
        
        print("🔊 Đang khởi động Thanh quản (Piper TTS CPU)...")
        # Khởi tạo instance PiperVoice
        self.voice = PiperVoice.load(model_path=str(self.model_path), config_path=str(self.config_path))
        print("✅ Mô-đun TTS đã sẵn sàng!")

    def _ensure_model_exists(self):
        """Kiểm tra và tự động tải mô hình TTS từ HuggingFace nếu chưa tồn tại trên máy."""
        if not self.model_path.exists():
            print(f"⬇️ Đang tải trọng số Giọng nói (.onnx)...")
            self._download_file(MODEL_URL, self.model_path)
            
        if not self.config_path.exists():
            print(f"⬇️ Đang tải file cấu hình (.json)...")
            self._download_file(CONFIG_URL, self.config_path)

    def _download_file(self, url: str, dest_path: Path):
        """Hàm tải file qua HTTP request có thanh tiến trình cơ bản."""
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def speak(self, text: str):
        """
        Dịch văn bản thành giọng nói và phát trực tiếp từ RAM ra loa dạng Stream (Độ trễ siêu thấp).
        """
        if not text.strip():
            return

        # Dọn dẹp các ký tự đặc biệt AI sinh ra (như markdown) để tránh làm TTS đọc vấp
        text = text.replace("*", "").replace("#", "")
        
        try:
            sample_rate = self.voice.config.sample_rate
            
            # Khởi tạo Stream để phát âm thanh trực tiếp (Streaming)
            stream = sd.OutputStream(samplerate=sample_rate, channels=1, dtype='int16')
            stream.start()
            
            has_audio = False
            
            for chunk in self.voice.synthesize(text):
                has_audio = True
                
                # Trích xuất bytes từ đối tượng chunk (tương thích đa phiên bản)
                if isinstance(chunk, bytes):
                    chunk_bytes = chunk
                elif hasattr(chunk, "audio_int16_bytes"):
                    chunk_bytes = chunk.audio_int16_bytes
                else:
                    chunk_bytes = bytes(chunk)
                    
                # Chuyển thành numpy array và bơm thẳng ra loa (Phát thời gian thực)
                audio_data = np.frombuffer(chunk_bytes, dtype=np.int16)
                stream.write(audio_data)
                
            # Allow the audio driver hardware buffer to drain completely before stopping
            import time
            time.sleep(0.4)

            stream.stop()
            stream.close()
            
            if not has_audio:
                print("❌ Lỗi: Piper-TTS không tạo ra được âm thanh nào (Generator rỗng)!")
                
        except Exception as e:
            print(f"❌ Lỗi khi phát âm: {str(e)}")