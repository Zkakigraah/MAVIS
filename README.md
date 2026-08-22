jarvis_project/
├── .venv/                     # Môi trường ảo tạo bởi uv
├── uv.lock                    # Quản lý dependency
├── pyproject.toml
├── core/
│   ├── wake_word.py
│   ├── stt_engine.py
│   ├── llm_agent.py           # Gọi Google API (Phase 1) hoặc Llama.cpp (Phase 2)
│   ├── tts_engine.py
│   └── tools.py               # Chứa các hàm os.startfile, web_search
├── memory/
│   ├── qdrant_local/          # Chứa data của Qdrant
│   └── rag_builder.py
├── ui/
│   └── hud_overlay.py         # PyQt6 UI
├── workspace/                 # ⚠️ VÙNG LÀM VIỆC CỐ ĐỊNH (Workable Folder)
│   ├── temp_audio/            # Chứa file ghi âm tạm thời
│   ├── personal_docs/         # Chỉ đọc (PDF, txt để RAG scan)
│   └── outputs/               # Chỉ ghi (File AI tạo ra)
└── main.py