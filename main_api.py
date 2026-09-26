# main_api.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import io, json, time
import numpy as np
import soundfile as sf
import librosa

# ===== ตั้งค่าพื้นฐาน =====
CLASS_NAMES = ["RSV", "ไอกรน", "ปอดบวม", "อื่นๆ"]  # แก้เป็นคลาสจริงได้ — ต้องตรงกับหน้า result.html (4 หลอด)
TARGET_SR = 16000
DURATION_SEC = 3.0

app = FastAPI(title="Cough Code API")

# อนุญาตให้เว็บของคุณเรียก API ข้ามโดเมนได้ (ตอนทดสอบ live server บน 5500/localhost)
# หมายเหตุ: ถ้าเสิร์ฟหน้าเว็บจากโดเมนเดียวกับ API (ผ่าน StaticFiles ด้านล่าง) จะไม่ต้องพึ่ง CORS เลย
# แต่ยังคงไว้เผื่อกรณีทดสอบ frontend แยกเครื่อง/แยกโดเมน
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500", "http://localhost:5500",
        "https://lastcoughcode.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"ok": True}

def preprocess_audio_bytes(raw: bytes) -> np.ndarray:
    """bytes -> mono waveform ที่ TARGET_SR และยาว DURATION_SEC"""
    data, sr = sf.read(io.BytesIO(raw), dtype="float32", always_2d=False)
    if data.ndim == 2:
        data = data.mean(axis=1)
    if sr != TARGET_SR:
        data = librosa.resample(data, orig_sr=sr, target_sr=TARGET_SR)
    need = int(TARGET_SR * DURATION_SEC)
    if len(data) < need:
        data = np.pad(data, (0, need - len(data)))
    else:
        data = data[:need]
    return data

def predict_dummy(_: np.ndarray) -> np.ndarray:
    """เดโม่: สุ่มความน่าจะเป็นแบบ softmax"""
    z = np.random.rand(len(CLASS_NAMES)).astype("float32")
    p = np.exp(z) / np.exp(z).sum()
    return p

@app.post("/predict")
async def predict(file: UploadFile = File(...), symptoms: str | None = Form(None)):
    t0 = time.time()
    raw = await file.read()
    wav = preprocess_audio_bytes(raw)

    # (ยังไม่ใช้โมเดลจริง) — ใช้เดโม่เพื่อทดสอบการเชื่อม
    probs = predict_dummy(wav)

    try:
        sym_list = json.loads(symptoms) if symptoms else []
    except Exception:
        sym_list = []

    conditions = {name: float(p) for name, p in zip(CLASS_NAMES, probs)}
    return JSONResponse({
        "conditions": conditions,
        "version": "v1-demo",
        "latency_ms": int((time.time()-t0)*1000),
        "symptoms_received": sym_list,
    })

# ===== เสิร์ฟหน้าเว็บ (index.html, record.html, ...) จากโฟลเดอร์ public/ =====
# ต้องอยู่หลังการประกาศ route ของ API ทั้งหมด (/ping, /predict) เสมอ
# มิฉะนั้น path เหล่านั้นจะถูก static files ดักจับไปก่อน
app.mount("/", StaticFiles(directory="public", html=True), name="frontend")
