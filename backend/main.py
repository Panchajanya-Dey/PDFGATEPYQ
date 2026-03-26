from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import subprocess
import json

app = FastAPI()

# ===== Enable CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Paths =====

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/uploads",
    StaticFiles(directory=os.path.join(BASE_DIR, "uploads")),
    name="uploads"
)

# backend folder
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Backend Dir {BACKEND_DIR}")

# project folder (one level above backend)
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
print(f"Project Dir {PROJECT_DIR}")

# uploads folder is in project root
UPLOAD_DIR = os.path.join(PROJECT_DIR, "backend", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===== Upload Endpoint =====
@app.post("/upload")
async def upload_files(
    question_pdf: UploadFile = File(...),
    answer_pdf: UploadFile = File(...)
):
    try:
        # Save PDFs inside project/uploads
        q_path = os.path.join(UPLOAD_DIR, "questions.pdf")
        a_path = os.path.join(UPLOAD_DIR, "answers.pdf")

        with open(q_path, "wb") as f:
            shutil.copyfileobj(question_pdf.file, f)

        with open(a_path, "wb") as f:
            shutil.copyfileobj(answer_pdf.file, f)

        print("PDFs saved successfully")

        # Run scripts inside backend folder
        subprocess.run(
            ["python", "pdfToImg.py", q_path],
            cwd=BACKEND_DIR,
            check=True
        )
        subprocess.run(
            ["python", "pdfToAns.py", a_path],
            cwd=BACKEND_DIR,
            check=True
        )
        subprocess.run(["python", "generateQuizJson.py"], cwd=BACKEND_DIR, check=True)

        print("Scripts executed successfully")

        # Load generated JSON
        json_path = os.path.join(UPLOAD_DIR, "quiz.json")

        if not os.path.exists(json_path):
            return {"error": "quiz.json not found"}

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    except subprocess.CalledProcessError as e:
        print("Script failed:", e)
        return {"error": "Script execution failed"}

    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}