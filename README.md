# 🎭 Face Swap Studio
Elegant. Amazing. Aura-forming.

Face Swap Studio is a sleek, real-time face-swapping web app powered by InsightFace, inswapper_128, and Streamlit. Drop in a single portrait and a target video — and watch a flawless face swap unfold with the original audio preserved. Crafted for creators who want cinematic results with minimal fuss.

---

## ✨ Why this feels magical
- One clear photo + a video → a believable, smooth swap that keeps the original voice and timing.
- Thoughtful defaults and confidence filtering keep results natural and reduce artifacts.
- Quick experiments or full-length swaps: tune the speed vs. quality tradeoff and get predictable results.

---

## 📋 Quick links
- [Features](#features)  
- [Project Structure](#project-structure)  
- [Requirements](#requirements)  
- [Installation](#installation)  
- [Downloading Models](#downloading-models)  
- [Run the App](#run-the-app)  
- [How to Use](#how-to-use)  
- [Settings Guide](#settings-guide)  
- [How It Works](#how-it-works)  
- [Troubleshooting](#troubleshooting)  
- [Ethical Use](#ethical-use)

---

## ✨ Features
- 🔄 One-image face swap — transform faces using just one source photo.  
- 🔊 Audio preserved — the app muxes original audio back into the final result for perfect lip sync.  
- 🚫 Smart no-face handling — cutaways, title cards, and non-face frames stay untouched.  
- ⚡ CPU-optimised mode — re-detect faces every N frames for big speed gains.  
- 🎚️ Confidence filtering — avoid false-positive swaps with an adjustable threshold.  
- 🌐 Friendly web UI — built with Streamlit for a simple, responsive interface.

---

## 📁 Project structure
```
faceswap_project/
│
├── app.py                  ← Main Streamlit application (single file)
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
├── .gitignore              ← Excludes large models and temp files
│
└── models/
    ├── inswapper_128.onnx  ← Face swap model (~530 MB) — download separately
    └── README.txt          ← Instructions for downloading models
```

---

## 🖥️ Requirements
| Requirement | Version / notes |
|---|---|
| Python | 3.10 only (3.11/3.12 can cause insightface build issues) |
| OS | Windows 10/11, Ubuntu 20.04+, macOS 12+ |
| RAM | 8 GB minimum, 16 GB recommended |
| GPU | Optional — CPU works, GPU is ~5–10× faster |

---

## ⚙️ Installation

### 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/faceswap-studio.git
cd faceswap-studio
```

### 2 — Create Python 3.10 environment
```bash
# Using conda (recommended)
conda create -n faceswap python=3.10 -y
conda activate faceswap

# OR using venv
python3.10 -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS
```

### 3 — Install dependencies
```bash
pip install -r requirements.txt
```

---

## 📥 Downloading models
Models are large and excluded from Git. Download manually.

### inswapper_128.onnx (required — ~530 MB)

**Windows PowerShell:**
```powershell
New-Item -ItemType Directory -Force -Path models
Invoke-WebRequest -Uri "https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx" -OutFile "models\inswapper_128.onnx"
```

**Linux / macOS:**
```bash
mkdir -p models
wget -O models/inswapper_128.onnx \
  https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx
```

> Note: The InsightFace "buffalo_l" detection model (~300 MB) is downloaded automatically the first time you run the app.

---

## ▶️ Run the app
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

---

## 🕹️ How to use
1. Upload a source face — a clear, front-facing, well-lit portrait (JPG/PNG/WEBP).  
2. Upload a target video — MP4/MOV/AVI.  
3. Tweak settings in the sidebar if desired (defaults are a good starting point).  
4. Click 🚀 “Swap Faces.”  
5. Preview the result and click ⬇️ “Download video” to save the MP4 with original audio.

### Pro tips for stunning swaps
- Pick a front-facing, evenly lit source photo without glasses or heavy occlusion.  
- Use 480p–720p target videos for faster processing with good quality.  
- For a quick test, set Max frames to 60 (about 2 seconds).  
- If cutaways are causing glitches, raise the confidence slider.

---

## 🎛️ Settings guide
| Setting | Default | What it does |
|---|---:|---|
| Re-detect every N frames | 5 | How often target faces are re-detected. Higher = faster, but less precise for moving faces |
| Face detection confidence | 0.5 | Minimum confidence to consider a detection valid — increase to avoid false swaps |
| Swap ALL faces | Off | Toggle to swap every detected face instead of only the largest one |
| Max frames | 0 | Limit how many frames are processed. 0 = entire video |

---

## 🔬 How it works (conceptual)
```
Source photo
     │
     ▼
Face detection (InsightFace buffalo_l)
     │  → extracts a 512-d ArcFace identity embedding
     ▼
For each video frame:
  ├─ Re-detect faces every N frames (cached between checks)
  ├─ Confidence filter — skip frames with no confident face
  ├─ Neural swap (inswapper_128.onnx) — transfer identity to target face
  └─ Write swapped frame to temp video
     │
     ▼
Audio mux (imageio-ffmpeg)
  ├─ Stream-copy video + original audio → perfect lip sync
  └─ Output: H.264 + AAC MP4
```

Key design decisions:
- Cache resets after several face-absent frames to avoid swapping title cards or non-face shots.  
- Stream-copy muxing preserves exact frame timing so audio never drifts.  
- Confidence filtering reduces false positives from partial faces or motion blur.

---

## 🐛 Troubleshooting
| Problem | Fix |
|---|---|
| No module named 'insightface' | pip install -r requirements.txt |
| Model not found: models/inswapper_128.onnx | Download the model (see above) |
| No face detected in source image | Use a clear, front-facing, well-lit photo |
| Output video has no audio | pip install imageio imageio-ffmpeg |
| Build error installing insightface | Use Python 3.10 (not 3.11/3.12) |
| App is slow | Lower video resolution or increase "Re-detect every N frames" |
| Cut-away scenes look weird | Increase confidence slider (try 0.7) |

---

## ⚠️ Ethical use
This tool is for creative, educational, and consenting use only. Respect people’s privacy and rights.

Do not use Face Swap Studio to:
- Create non-consensual deepfakes of real people  
- Produce misleading or harmful content  
- Break the law

The developers are not responsible for misuse. Use with care and respect.

---

## 📦 Dependencies
| Package | Purpose |
|---|---|
| streamlit | Web UI |
| insightface | Face detection + ArcFace embeddings |
| onnxruntime | ONNX model inference (CPU) |
| opencv-python-headless | Video I/O |
| numpy | Array operations |
| imageio-ffmpeg | Bundled ffmpeg for audio muxing |
| Pillow | Image decoding |

---

Authors  
Hassnain Soomro  
Shoaib Ahmed Bullo

---

## 📄 License
InsightFace models are provided for non-commercial research use only. See [InsightFace license](https://github.com/deepinsight/insightface/blob/master/LICENSE) for details.
