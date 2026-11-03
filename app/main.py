import csv
import io
import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from app.schemas import InterviewSetup, AnswerRequest, ReportRequest
from app import gemini_service
from app import tts_service

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Start loading the voice model while the user sets up the interview.
    warmup = asyncio.create_task(asyncio.to_thread(tts_service.preload_pipeline))
    try:
        yield
    finally:
        await warmup


app = FastAPI(title="Company-Specific AI Interviewer", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "groq_key_configured": bool(os.getenv("GROQ_API_KEY", "").strip()),
        "voice_model": tts_service.get_pipeline_state(),
    }

@app.post("/api/speak")
def speak(request: dict):
    try:
        text = request.get("text", "").strip()

        if not text:
            raise HTTPException(
                status_code=400, 
                detail="Speech text is required.")

        audio_data = tts_service.generate_speech(text)

        return Response(
            content=audio_data,
            media_type="audio/wav"
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502, 
            detail=str(exc))

@app.post("/api/dataset-preview")
async def dataset_preview(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a CSV file.")
    raw = await file.read()
    if len(raw) > 2_000_000:
        raise HTTPException(413, "CSV must be smaller than 2 MB.")
    try:
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        if not rows:
            raise ValueError("CSV has no data rows.")
        context = "\n".join(str(row) for row in rows[:40])
        return {"filename": file.filename, "rows_read": len(rows), "context": context[:12000]}
    except Exception as exc:
        raise HTTPException(400, f"Could not read CSV: {exc}")

@app.post("/api/start")
def start_interview(setup: InterviewSetup):
    try:
        return {"questions": gemini_service.create_questions(setup.model_dump())}
    except Exception as exc:
        raise HTTPException(502, str(exc))

@app.post("/api/evaluate")
def evaluate(request: AnswerRequest):
    try:
        return gemini_service.evaluate_answer(request.model_dump())
    except Exception as exc:
        raise HTTPException(502, str(exc))

@app.post("/api/report")
def report(request: ReportRequest):
    try:
        return gemini_service.create_report(request.model_dump())
    except Exception as exc:
        raise HTTPException(502, str(exc))
