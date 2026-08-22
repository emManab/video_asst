---
title: AI Video Assistant
emoji: 🎥
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
---

<div align="center">

# 🎬 AI Video Assistant

**Transcribe · Summarise · Chat with your meetings**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Mistral AI](https://img.shields.io/badge/LLM-Mistral_AI-orange)](https://mistral.ai/)
[![Whisper](https://img.shields.io/badge/STT-OpenAI_Whisper-412991?logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![LangChain](https://img.shields.io/badge/RAG-LangChain-1C3C3C?logo=langchain)](https://www.langchain.com/)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔊 **Multi-source Input** | YouTube URLs or local video/audio files |
| 📝 **Accurate Transcription** | OpenAI Whisper (English) or Sarvam AI (Hinglish → English) |
| 📋 **AI Summarisation** | Map-reduce summarisation via Mistral AI |
| ✅ **Action Item Extraction** | Automatically identifies tasks, owners, and deadlines |
| 🔑 **Key Decision Extraction** | Pulls out all decisions made during the meeting |
| ❓ **Open Question Detection** | Flags unresolved topics needing follow-up |
| 💬 **RAG Chat** | Ask anything about your meeting using ChromaDB + Mistral AI |
| 🎨 **Beautiful Dark UI** | Glassmorphism-style Streamlit dashboard with live pipeline status |

---

## 🏗️ Architecture

```
videoasst/
├── app.py                   # Streamlit UI (main entry point)
├── main.py                  # CLI entry point
├── test.py                  # Quick smoke-test
├── Requirements.txt         # Python dependencies
├── .env                     # Your API keys (git-ignored)
├── .env.example             # Safe-to-commit placeholder
│
├── core/
│   ├── transcriber.py       # Whisper + Sarvam AI STT routing
│   ├── summarizer.py        # Map-reduce summarisation (Mistral AI)
│   ├── extractor.py         # Action items / decisions / questions
│   ├── rag_engine.py        # LangChain LCEL RAG pipeline
│   └── vector_store.py      # ChromaDB vector store (HuggingFace embeddings)
│
└── utils/
    └── audio_processor.py   # yt-dlp download + pydub chunking
```

### Pipeline Flow

```
Input (URL / File)
       │
       ▼
 Audio Processing (yt-dlp / pydub)
       │  chunks audio into 10-min WAV segments
       ▼
  Transcription (Whisper or Sarvam AI)
       │  joins all chunk transcripts
       ▼
  ┌────┴────────────────────────┐
  │                             │
  ▼                             ▼
LLM Analysis (Mistral AI)    RAG Build (ChromaDB)
  • Title generation            • Chunk + embed transcript
  • Summarisation               • Store in local vector DB
  • Action items
  • Key decisions
  • Open questions
       │                             │
       └────────────┬────────────────┘
                    ▼
             Streamlit Dashboard
             • Full results display
             • Interactive Q&A chat
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.10+**
- **FFmpeg** must be installed and available on `PATH`

**Install FFmpeg on Windows:**
```powershell
winget install ffmpeg
# or via Chocolatey:
choco install ffmpeg
```

**Install FFmpeg on macOS:**
```bash
brew install ffmpeg
```

**Install FFmpeg on Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

---

### 2. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/your-username/AI-Video-Assistant.git
cd AI-Video-Assistant

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activate (macOS / Linux)
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r Requirements.txt
```

> ⚠️ **Note:** `torch` can be large (~2 GB). On CPU-only machines this is fine; for GPU acceleration install the CUDA variant from [pytorch.org](https://pytorch.org/).

---

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env   # macOS/Linux
copy .env.example .env  # Windows
```

Then edit `.env` and fill in your API keys:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here   # Only needed for Hinglish mode
WHISPER_MODEL=tiny
SARVAM_STT_MODEL=saaras:v2.5
```

#### Where to get the API keys

| Key | Where to get it |
|---|---|
| `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai/api-keys) |
| `SARVAM_API_KEY` | [dashboard.sarvam.ai](https://dashboard.sarvam.ai) — only needed for Hinglish |

---

### 5. Run the Streamlit App

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**.

---

### 6. (Optional) CLI Mode

```bash
python main.py
```

Follow the prompts to enter a YouTube URL or local file path and choose the language.

---

## 📦 Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `MISTRAL_API_KEY` | ✅ Yes | — | Mistral AI API key for LLM tasks |
| `SARVAM_API_KEY` | ⚠️ Hinglish only | — | Sarvam AI key for Hindi/Hinglish STT |
| `WHISPER_MODEL` | ❌ Optional | `tiny` | Whisper model size: `tiny` / `base` / `small` / `medium` / `large` |
| `SARVAM_STT_MODEL` | ❌ Optional | `saaras:v2.5` | Sarvam model version |

---

## 🌐 Language Support

| Language | Engine | Notes |
|---|---|---|
| **English** | OpenAI Whisper (local) | Runs fully offline after model download |
| **Hinglish** (Hindi+English) | Sarvam AI (cloud API) | Translates to English while transcribing. Requires `SARVAM_API_KEY`. Audio is split into ≤25s pieces per API limit. |

---

## 🛠️ Troubleshooting

### `FileNotFoundError: ffmpeg` or `ffprobe not found`
FFmpeg is not on your PATH. Follow the install steps in the Prerequisites section.

### `RuntimeError: SARVAM_API_KEY is not set`
Add your Sarvam key to `.env` or switch to English mode (uses local Whisper instead).

### Whisper model download is slow
The first run downloads the model (~250 MB for `small`). Subsequent runs use the cached version at `~/.cache/whisper/`.

### `ChromaDB` import errors
Run:
```bash
pip install langchain-chroma chromadb
```

### Out of memory with large videos
Try switching to `WHISPER_MODEL=tiny` in your `.env`, or split the video before processing.

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss major changes.

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
