import streamlit as st
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import tempfile, os, time, shutil, subprocess

st.set_page_config(page_title="Face Swap Studio", page_icon="🎭", layout="centered")
st.title("🎭 Face Swap Studio")
st.caption("Face swap with audio • CPU optimised • lip-sync accurate")

# ── Auto-download model from Google Drive ────────────────────────────────────
# REPLACE the FILE_ID below with your own Google Drive file ID
GDRIVE_FILE_ID = "1QN8nJsaVl_7OKW36b7KfBjZuYXUYs44B"
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "models", "inswapper_128.onnx")

def download_model():
    if os.path.exists(MODEL_PATH):
        return True
    os.makedirs("models", exist_ok=True)
    try:
        import gdown
        url = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"
        with st.spinner("⬇️ Downloading model (530 MB, one-time only)…"):
            gdown.download(url, MODEL_PATH, quiet=False)
        if os.path.exists(MODEL_PATH):
            st.success("✅ Model downloaded successfully")
            return True
        else:
            st.error("❌ Download failed — file not found after download")
            return False
    except Exception as e:
        st.error(f"❌ Model download failed: {e}\n\nMake sure your Google Drive link is public.")
        return False

if not download_model():
    st.stop()

st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    detect_every = st.slider(
        "Re-detect face every N frames", 1, 30, 5,
        help="5 = ~5x faster. Use 1 if the face moves a lot."
    )
    confidence = st.slider(
        "Face detection confidence", 0.3, 0.9, 0.5, 0.05,
        help="Higher = only swap when very sure a face is present."
    )
    swap_all = st.toggle("Swap ALL faces in video", value=False)
    limit    = st.number_input("Max frames (0 = full video)", 0, 99999, 0, 30,
                                help="Set 60 for a quick test first")
    st.divider()
    st.caption("💡 Tips:")
    st.caption("• detect every 5 = ~4x faster")
    st.caption("• 480p video = fastest")
    st.caption("• confidence 0.5 = good balance")

# ── Load models ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading models…")
def load_models():
    fa = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    fa.prepare(ctx_id=-1, det_size=(640, 640))
    sw = insightface.model_zoo.get_model(MODEL_PATH, download=False, download_zip=False)
    return fa, sw

try:
    face_app, swapper = load_models()
    st.success("✅ Models loaded — ready")
except Exception as e:
    st.error(f"❌ {e}")
    st.stop()

# ── Uploads ───────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    st.subheader("📸 Source face")
    src_file = st.file_uploader("Photo with face to copy",
                                type=["jpg","jpeg","png","webp"])
    if src_file:
        st.image(src_file, width=280)
with c2:
    st.subheader("🎬 Target video")
    vid_file = st.file_uploader("Video to swap faces into",
                                type=["mp4","mov","avi"])
    if vid_file:
        st.video(vid_file)

st.divider()

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_source_face(img_bytes: bytes):
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    faces = face_app.get(img)
    if not faces:
        return None
    return max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))


def faces_above_confidence(faces, thresh):
    return [f for f in faces if f.det_score >= thresh]


def swap_frame(frame, src_face, target_faces, all_faces):
    if not target_faces:
        return frame
    out = frame.copy()
    targets = (target_faces if all_faces else
               [max(target_faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))])
    for t in targets:
        try:
            out = swapper.get(out, t, src_face, paste_back=True)
        except Exception:
            pass
    return out


def mux_audio(original, noaudio, output):
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        r = subprocess.run([
            ffmpeg, "-y",
            "-i", noaudio, "-i", original,
            "-map", "0:v:0", "-map", "1:a:0?",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "-shortest", output,
        ], capture_output=True, timeout=600)
        if r.returncode == 0 and os.path.exists(output) and os.path.getsize(output) > 1000:
            return True
        # fallback: re-encode
        r2 = subprocess.run([
            ffmpeg, "-y",
            "-i", noaudio, "-i", original,
            "-map", "0:v:0", "-map", "1:a:0?",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "-shortest", output,
        ], capture_output=True, timeout=600)
        return r2.returncode == 0 and os.path.exists(output) and os.path.getsize(output) > 1000
    except Exception as ex:
        st.warning(f"⚠️ Audio mux error: {ex}")
        return False


def process_video(src_bytes, vid_bytes, all_faces, det_every, conf_thresh, max_frames):
    src_face = get_source_face(src_bytes)
    if src_face is None:
        raise ValueError("No face detected in source image.\n"
                         "Use a clear, front-facing, well-lit photo.")

    tmp     = tempfile.mkdtemp()
    v_in    = os.path.join(tmp, "input.mp4")
    v_raw   = os.path.join(tmp, "raw.mp4")
    v_final = os.path.join(tmp, "final.mp4")

    with open(v_in, "wb") as f:
        f.write(vid_bytes)

    cap   = cv2.VideoCapture(v_in)
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if max_frames > 0:
        total = min(total, max_frames)

    writer = cv2.VideoWriter(v_raw, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))

    bar    = st.progress(0, text="Processing frames…")
    status = st.empty()
    t0     = time.time()
    cached = []
    frames_since_face = 0
    NO_FACE_RESET_AFTER = 10

    for i in range(total):
        ret, frame = cap.read()
        if not ret:
            break
        if i % det_every == 0:
            found = faces_above_confidence(face_app.get(frame), conf_thresh)
            if found:
                cached = found
                frames_since_face = 0
            else:
                frames_since_face += det_every
                if frames_since_face >= NO_FACE_RESET_AFTER:
                    cached = []
        writer.write(swap_frame(frame, src_face, cached, all_faces))
        if i % 5 == 0 or i == total - 1:
            pct  = (i + 1) / total
            rate = (i + 1) / max(time.time() - t0, 0.001)
            eta  = int((total - i - 1) / max(rate, 0.001))
            bar.progress(pct, text=f"Frame {i+1} / {total}  ({pct*100:.0f}%)")
            status.caption(f"⚡ {rate:.1f} fps  •  ETA {eta}s")

    cap.release()
    writer.release()
    bar.progress(1.0, text="✅ Frames done — adding audio…")
    status.empty()

    with st.spinner("Adding audio…"):
        ok = mux_audio(v_in, v_raw, v_final)

    if not ok:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([ffmpeg, "-y", "-i", v_raw,
                        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                        "-movflags", "+faststart", v_final],
                       capture_output=True, timeout=300)
        if not os.path.exists(v_final):
            shutil.copy(v_raw, v_final)

    elapsed = time.time() - t0
    st.info(f"⏱ Done in **{elapsed:.0f}s**  •  **{total/elapsed:.1f} fps**  •  **{total}** frames")
    return v_final


# ── Run button ────────────────────────────────────────────────────────────────
if src_file and vid_file:
    if st.button("🚀 Swap Faces", type="primary", use_container_width=True):
        try:
            result = process_video(
                src_bytes   = src_file.getvalue(),
                vid_bytes   = vid_file.getvalue(),
                all_faces   = swap_all,
                det_every   = detect_every,
                conf_thresh = confidence,
                max_frames  = int(limit),
            )
            st.success("✅ Face swap complete!")
            st.video(result)
            with open(result, "rb") as f:
                st.download_button(
                    "⬇️ Download video (with audio)",
                    data=f.read(), file_name="faceswap_output.mp4",
                    mime="video/mp4", use_container_width=True,
                )
        except Exception as e:
            st.error(f"❌ {e}")
            import traceback
            with st.expander("Full traceback"):
                st.code(traceback.format_exc())
else:
    st.info("👆 Upload a face photo and a target video above, then hit Swap Faces.")
