⚛️ M.A.V.I.S
==============

Inspired by J.A.R.V.I.S - "**Just A Rather Very Intelligent System**" - Iron Man

M.A.V.I.S (Multi-purpose Automated Virtual Information System) là một Trợ lý AI cá nhân toàn diện được xây dựng bằng Python, lấy cảm hứng từ vũ trụ Iron Man. Hệ thống hoạt động độc lập trên máy tính Windows, sở hữu giao diện Quả cầu Hologram 3D trong suốt 100%, cùng khả năng Nghe, Nói, Nhìn và can thiệp sâu vào hệ điều hành.

🌟 Tính năng Cốt lõi (Current Version)
--------------------------------------

-   **🎙️ Lắng nghe Tích cực (STT):** Sử dụng `Faster-Whisper` kết hợp Bộ lọc VAD sinh học và danh sách chống "ảo giác". Nhận diện giọng nói con người, bỏ qua hoàn toàn tiếng ồn trắng.

-   **🔊 Giọng nói Quản gia (TTS):** Sử dụng lõi `Piper-TTS` xử lý hoàn toàn Offline trên CPU (giọng British Male). Phát âm thanh trực tiếp (Streaming) với độ trễ siêu thấp.

-   **👁️ Thị giác Máy tính (Vision):** Khả năng tự động chụp ảnh màn hình và phân tích nội dung thông qua Vision AI.

-   **🧠 Trí nhớ Cục bộ (RAG):** Cơ sở dữ liệu Vector siêu tốc `Qdrant` kết hợp `FastEmbed`, cho phép J.A.R.V.I.S ghi nhớ tài liệu cá nhân bảo mật trên ổ cứng.

-   **⚙️ Quyền năng Hệ thống (Tool Calling):**

    -   Tự động mở ứng dụng, tìm kiếm Google, mở video YouTube.

    -   Điều khiển Windows: Khóa màn hình, tăng giảm âm lượng, độ sáng, shutdown máy tính (cẩn trọng khi sử dụng lệnh).

    -   Kiểm tra tình trạng phần cứng (CPU, RAM, Pin).

    -   **Hệ thống Sandbox:** Đọc/Ghi file văn bản một cách an toàn tuyệt đối bên trong thư mục `workspace/outputs/`.

-   **🔮 Giao diện Lõi Hologram 3D:** Giao diện vô hình, giả lập 3D lơ lửng trên màn hình nền. Lõi năng lượng thay đổi màu sắc và tốc độ xoay theo 4 trạng thái: Ngủ (Xanh lam), Lắng nghe (Xanh lá), Suy nghĩ (Cam), Phát âm (Lục lam).

📁 Cấu trúc Dự án
-----------------

```
JARVIS_PROJECT/
├── core/
│   ├── config.py         # Cấu hình đường dẫn và Sandbox bảo mật
│   ├── llm_agent.py      # "Bộ não" trung tâm (Groq API + Tool Calling)
│   ├── stt_engine.py     # "Đôi tai" (Whisper VAD + Chống ảo giác)
│   ├── tts_engine.py     # "Thanh quản" (Piper TTS)
│   └── tools.py          # "Kho vũ khí" (Các kỹ năng điều khiển Windows)
├── memory/
│   ├── qdrant_db.py      # Vector Database lưu trữ ký ức
│   └── rag_builder.py    # Trình nạp văn bản từ TXT vào ký ức
├── ui/
│   ├── console_window.py # Giao diện lưu trữ chat log khi app đang mở
│   └── hud_overlay.py    # Giao diện Hologram 3D PyQt6
├── workspace/            # VÙNG AN TOÀN (Sandbox)
│   ├── personal_docs/    # Bỏ file TXT của bạn vào đây để nạp trí nhớ
│   └── outputs/          # Nơi M.A.V.I.S xuất file code, text, ảnh chụp
├── build_mavis.py        # Trình đóng gói ứng dụng (Release Pipeline)
├── make_icon.py          # Công cụ ép Icon chất lượng cao
├── main.py               # Điểm khởi động hệ thống
└── README.md             # Tài liệu bạn đang đọc

```
