# 🎭 Face Swap Studio

A real-time face swap web application built with **InsightFace**, **inswapper_128**, and **Streamlit**.  
Upload a single face photo + a video → get a fully swapped video with original audio preserved.

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Downloading Models](#downloading-models)
- [Running the App](#running-the-app)
- [How to Use](#how-to-use)
- [Settings Guide](#settings-guide)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Deploying to GitHub](#deploying-to-github)
- [Ethical Use](#ethical-use)

---

## ✨ Features

- 🔄 **One-image face swap** — swap any face into a video using just one photo
- 🔊 **Audio preserved** — original audio is muxed back with frame-perfect lip sync
- 🚫 **Smart no-face detection** — cut-away scenes and non-face frames are left untouched
- ⚡ **CPU optimised** — re-detect faces every N frames for major speed boost
- 🎚️ **Confidence filtering** — adjustable threshold prevents false swaps
- 🌐 **Simple web UI** — runs in your browser via Streamlit

---

## 📁 Project Structure

```
faceswap_project/
│
├── app.py                  ← Main Streamlit application (single file)
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
├── .gitignore              ← Excludes models and temp files from git
│
└── models/
    ├── inswapper_128.onnx  ← Face swap model (~530 MB) — download separately
    └── README.txt          ← Instructions for downloading models
```

---

## 🖥️ Requirements

| Requirement | Version |
|---|---|
| Python | **3.10 only** (3.11/3.12 have insightface build issues) |
| OS | Windows 10/11, Ubuntu 20.04+, macOS 12+ |
| RAM | 8 GB minimum, 16 GB recommended |
| GPU | Optional — CPU works, GPU is 5–10× faster |

---

## ⚙️ Installation

### Step 1 — Clone or download the project

```bash
git clone https://github.com/YOUR_USERNAME/faceswap-studio.git
cd faceswap-studio
```

### Step 2 — Create a Python 3.10 environment

```bash
# Using conda (recommended)
conda create -n faceswap python=3.10 -y
conda activate faceswap

# OR using venv
python3.10 -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / Mac
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## 📥 Downloading Models

The model files are too large for GitHub. Download them manually:

### inswapper_128.onnx (Required — ~530 MB)

**Windows PowerShell:**
```powershell
New-Item -ItemType Directory -Force -Path models
Invoke-WebRequest -Uri "https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx" -OutFile "models\inswapper_128.onnx"
```

**Linux / Mac:**
```bash
mkdir -p models
wget -O models/inswapper_128.onnx \
  https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx
```

> The **buffalo_l** detection model (~300 MB) downloads **automatically** the first time you run the app.

---

## ▶️ Running the App

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🕹️ How to Use

1. **Upload source face** — a clear, front-facing, well-lit photo (JPG/PNG/WEBP)
2. **Upload target video** — the video where faces will be replaced (MP4/MOV/AVI)
3. **Adjust settings** in the sidebar if needed (defaults work well)
4. Click **🚀 Swap Faces**
5. Preview the result in the browser
6. Click **⬇️ Download video** to save the output with audio

### Tips for best results

- Source photo: front-facing, no glasses, good lighting, single face
- Video: 480p–720p works fastest; avoid very dark footage
- Set **Max frames** to `60` for a quick 2-second test before processing the full video
- If cut-away shots look weird, increase the **confidence** slider

---

## 🎛️ Settings Guide

| Setting | Default | Description |
|---|---|---|
| Re-detect every N frames | 5 | How often to run face detection. Higher = faster but less precise for moving faces |
| Face detection confidence | 0.5 | Minimum score to count as a real face. Raise to avoid false swaps |
| Swap ALL faces | Off | Swap every face in the video, not just the largest one |
| Max frames | 0 | Limit how many frames to process. 0 = full video |

---

## 🔬 How It Works

```
Source photo
     │
     ▼
Face Detection (InsightFace buffalo_l)
     │  extracts 512-d ArcFace identity embedding
     ▼
For each video frame:
  ├─ Re-detect target faces every N frames (cached in between)
  ├─ Confidence filter — skip frame if no confident face found
  ├─ Neural swap (inswapper_128.onnx) — transfers identity onto target face
  └─ Write swapped frame to temp video
     │
     ▼
Audio mux (imageio_ffmpeg bundled binary)
  ├─ Stream-copy video + original audio → perfect lip sync
  └─ Output: H.264 + AAC MP4
```

**Key design decisions:**
- **Cache reset after 10 face-absent frames** — prevents wrongly swapping cut-away shots, title cards, or audience shots
- **Stream-copy mux** (no video re-encode) — preserves exact frame timestamps, eliminating audio/lip sync drift
- **Confidence filtering** — low-score detections (partial faces, motion blur) are ignored

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'insightface'` | Run `pip install -r requirements.txt` |
| `Model not found: models/inswapper_128.onnx` | Download the model (see above) |
| `No face detected in source image` | Use a clearer, brighter, front-facing photo |
| Output video has no audio | Run `pip install imageio imageio-ffmpeg` |
| Build error installing insightface | Make sure Python is **3.10**, not 3.11/3.12 |
| App is slow | Lower video resolution, or increase "Re-detect every N frames" to 10–15 |
| Cut-away scenes look weird | Increase confidence slider to 0.7 |
| Lip sync is off | Already fixed — uses stream-copy mux for frame-perfect sync |

---

## 🚀 Deploying to GitHub

See the full step-by-step guide below ↓

---

## ⚠️ Ethical Use

This tool is intended for:
- Creative projects, film production, education, and entertainment
- Situations where **all people involved have given consent**

**Do not use this tool to:**
- Create non-consensual deepfakes of real people
- Produce misleading or harmful content
- Violate any applicable laws

The developers are not responsible for misuse of this software.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI |
| `insightface` | Face detection + ArcFace embedding |
| `onnxruntime` | ONNX model inference (CPU) |
| `opencv-python-headless` | Video reading and writing |
| `numpy` | Array operations |
| `imageio-ffmpeg` | Bundled ffmpeg for audio muxing |
| `Pillow` | Image decoding |

---

## 📄 License

This project uses InsightFace models which are available for **non-commercial research use only**.  
See [InsightFace license](https://github.com/deepinsight/insightface/blob/master/LICENSE) for details.
