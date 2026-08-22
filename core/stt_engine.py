import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
from core.config import TEMP_DIR

class STTEngine:
    def __init__(self, model_size="base"):
        # Bạn có thể đổi sang "tiny" (nhẹ hơn) hoặc "small" (nặng hơn, chuẩn hơn)
        # Tải mô hình vào RAM thường (CPU) và dùng lượng tử hóa int8 để tiết kiệm tài nguyên
        print("🎙️ Đang tải mô hình Lắng nghe (Faster-Whisper CPU)...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("✅ Mô-đun STT đã sẵn sàng!")

    def record_audio(self, duration=5, sample_rate=16000) -> str:
        """
        Ghi âm từ Microphone trong một khoảng thời gian cố định.
        
        Args:
            duration: Thời gian ghi âm (giây)
            sample_rate: Tần số lấy mẫu (16000Hz là tối ưu cho Whisper)
        """
        print(f"\n🔴 J.A.R.V.I.S is listening ({duration}s)...")
        
        # Bắt đầu ghi âm (mono channel)
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()  # Block tiến trình chờ đến khi ghi âm xong
        
        print("⏹️ Đang xử lý âm thanh...")
        
        # Đảm bảo thư mục temp tồn tại và lưu file ghi âm
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        file_path = TEMP_DIR / "temp_mic.wav"
        sf.write(str(file_path), audio_data, sample_rate)
        
        return str(file_path)

    def transcribe(self, audio_path: str) -> str:
        """
        Chuyển đổi file âm thanh thành văn bản.
        """
        # Beam_size=5 giúp tăng độ chính xác khi dịch
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        
        # Gom các đoạn text lại với nhau
        text = " ".join([segment.text for segment in segments])
        return text.strip()

# Khởi tạo instance mặc định
# stt = STTEngine()