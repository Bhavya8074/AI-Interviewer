# Company-Specific AI Interviewer (MVP)

A local mock-interview app using Groq, FastAPI, HTML/CSS/JavaScript, optional CSV context, browser speech recognition, Kokoro text-to-speech, and a local webcam preview.

## Scope and privacy
This is a working MVP, not a production hiring system. Groq receives text answers and optional CSV reference data. The webcam is preview-only: video is not recorded or uploaded. AI feedback is approximate coaching, not a hiring decision.

## Requirements
- Python 3.10–3.12 (Kokoro currently requires Python below 3.13)
- Groq API key
- Chrome or Edge recommended for speech recognition

## Windows PowerShell setup
```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
If activation is blocked, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv312\Scripts\Activate.ps1
```

Open `.env` and add your NEW key:
```env
GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
GROQ_MODEL=openai/gpt-oss-20b
```
Never share the key or commit `.env`. Keep `.env.example` free of real credentials.

## Dataset
You can upload a UTF-8 CSV in the app. Suggested columns: `role`, `topic`, `question`, `difficulty`, `company`. The first 40 rows are passed as reference context to Groq. This MVP does not train an ML model.

## Run
```powershell
.\.venv312\Scripts\python.exe -m uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

The local Kokoro voice model begins loading in the background when the server starts, while you set up the interview. The first question is spoken once the model is ready. Initial model loading can take a little time; later questions reuse the loaded model.

## First test
1. Company: Example Technologies; Role: Python Developer.
2. Choose Technical and 3 questions.
3. Add company rules or leave blank.
4. Generate questions, answer each, and submit.
5. Finish to view the coaching report.

## Structure
```text
company_ai_interviewer/
├── app/ (__init__.py, main.py, gemini_service.py, schemas.py)
├── data/ (.gitkeep; place your CSV here if preferred)
├── static/ (index.html, styles.css, app.js)
├── .env.example
├── .gitignore
└── requirements.txt
```

## Troubleshooting
- Missing key: check `.env` and `GROQ_API_KEY`.
- 401/403: create a fresh key and verify Groq API access.
- 429: wait and retry if rate-limited.
- Speech unavailable: use Chrome/Edge, allow microphone access, or type.
- Camera unavailable: use localhost, allow camera access, and close other apps using it.
- CSV error: save as UTF-8 `.csv` with a header row.

Before deployment, add authentication, rate limits, privacy/consent flows, secure logging, and tests. Do not use real candidate personal data in this MVP.
