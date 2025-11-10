import base64
import sys
import os
import traceback
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from fastapi import FastAPI, UploadFile, Form, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from dotenv import load_dotenv

from collections import deque
from fastapi.responses import PlainTextResponse, FileResponse
from contextlib import asynccontextmanager

# Make "files" importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from files.db_controller import DBController
from files.logger import logger
from files.processing import DataProcessor

if TYPE_CHECKING:
    from files.AImodels import AIModules  # type hints only

# Env
load_dotenv()
# ---------- Lazy loader for AI ----------
_AI: Optional["AIModules"] = None
def get_ai() -> "AIModules":
    global _AI
    if _AI is None:
        from files.AImodels import AIModules  # heavy import lazily
        logger.info("Loading AIModules (Face/Embed + Spoof)...")
        _AI = AIModules()
        logger.info("AIModules loaded.")
    return _AI

# ---------- Lifespan (startup/shutdown) ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Lifespan: warming up models...")
        get_ai()
        logger.info("Lifespan: models ready.")
    except Exception as e:
        logger.error(f"Lifespan warm-up failed: {e}\n{traceback.format_exc()}")
    # Hand control to the app
    yield
    # Shutdown
    # ---------- Shutdown ----------
    try:
        # Detect reason for shutdown (Render or FastAPI process exit)
        import signal
        reason = "Normal shutdown or deployment restart"
        # Render often sends SIGTERM on redeploy
        if hasattr(signal, "SIGTERM"):
            reason = "Received SIGTERM (Render deployment or service restart)"

        logger.info(f"Lifespan: shutting down FastAPI app. Reason: {reason}")

        # Optional cleanup: free up models
        global _AI
        if _AI is not None:
            _AI = None
            logger.info("Lifespan: released AI models from memory.")

    except Exception as e:
        logger.error(f"Lifespan shutdown error: {e}\n{traceback.format_exc()}")

# ---------- App ----------
app = FastAPI(title="APR Project", version="0.0.5", lifespan=lifespan)

# CORS (lock this down in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("FastAPI app initialized (lazy model loading enabled).")

# ---------- Models ----------
class StudentData(BaseModel):
    name: str
    roll: str
    course_id: str
    image_data: bytes
    model_config = ConfigDict(extra='allow')

# ---------- Routes ----------
@app.get("/wakeup")
def wakeup_call():
    get_ai()
    return {"success": "true"}

@app.post("/register")
async def receive_data(name: str = Form(...), roll: str = Form(...), image: UploadFile = File(...)):
    try:
        logger.info(f"API /register called by roll={roll}")
        processor = DataProcessor(ai_modules=get_ai())
        processed_data = await processor.process_input(name, roll, image)

        db = DBController()
        result = await db.register_student(processed_data)

        logger.info(f"Data successfully stored for roll={roll}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error in /register for roll={roll}: {e}\n{traceback.format_exc()}")
        return {"success": False, "error": str(e)}

@app.post("/login")
async def login(name: str = Form(...), roll: str = Form(...)):
    try:
        db = DBController()
        student = await db.check_login(roll=roll, name=name)
        if not student or (name and student.get("name") != name):
            return {"success": False, "message": "Invalid credentials or student not found"}

        image_bytes = student.get("image_data")
        if image_bytes:
            student["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")

        student.pop("embedding", None)
        student.pop("image_data", None)

        return {"success": True, "message": "Login successful", "student": student}
    except Exception as e:
        logger.error(f"Error in /login: {e}\n{traceback.format_exc()}")
        return {"success": False, "message": "Internal server error", "error": str(e)}

# ---------- Spoof Detection API ----------
@app.post("/spoof")
async def spoof(
    image: UploadFile = File(...),
    authorization: Optional[str] = Header(None)  # optional, keep if you need it later
):
    try:
        content = await image.read()
        if not content:
            return {"success": False, "reason": "Empty file"}

        if len(content) > int(os.environ.get("MAX_IMAGE_BYTES", 5 * 1024 * 1024)):
            return {"success": False, "reason": "Image too large"}

        ai = get_ai()
        result = ai.spoof_detect(content)  # returns full payload dict

        return {"success": True, **result}

    except HTTPException as e:
        return {"success": False, "reason": str(e.detail)}
    except Exception as e:
        logger.error(f"/spoof error: {e}\n{traceback.format_exc()}")
        return {"success": False, "reason": "Internal server error"}

@app.post("/mark_attendance")
async def mark_attendance(course_id: str = Form(...), image: UploadFile = File(...)):
    try:
        logger.info("/mark_attendance called (no roll from client)")
        if image.content_type not in ("image/jpeg", "image/png"):
            return {"success": False, "status": "unmarked", "reason": "Only JPG/PNG allowed"}

        image_bytes = await image.read()
        logger.info(f"Received image of size {len(image_bytes)} bytes")

        match = await get_ai().match_face("unknown", image_bytes)
        matched_roll = match.get("matched_roll")
        similarity = match.get("similarity", "")

        if not matched_roll:
            return {"success": False, "status": "unmarked", "similarity": similarity, "reason": "No face match found"}

        db = DBController()
        student = await db.read_entry({"roll": matched_roll})
        if not student:
            return {"success": False, "status": "unmarked", "similarity": similarity, "reason": "Student not found in DB"}

        now = datetime.now()
        attendance_data = {
            "roll": matched_roll,
            "name": student.get("name"),
            "course": course_id,
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "similarity": similarity,
            "status": "marked"
        }

        await db.insert_attendance(attendance_data)
        logger.info(f"Attendance marked for roll={matched_roll}")
        payload = {
            "success": True,
            "status": "marked",
            "similarity": similarity,
            "reason": "",
            "details":{
                "name":student.get("name"),
                "roll":matched_roll,
                "timestamp":now.isoformat()
            }
        }

        return payload
    except Exception as e:
        logger.error(f"Error in mark_attendance: {e}\n{traceback.format_exc()}")
        return {"success": False, "status": "unmarked", "reason": "Internal server error"}

#--------------- view logs ----------
def _tail_filter_log(
    path: str,
    max_lines: int,
    level: Optional[str],
    grep: Optional[str],
):
    """
    Read log file line-by-line, keep only the last `max_lines` lines after optional filters.
    Uses deque to avoid loading whole file into memory.
    """
    max_lines = max(1, min(max_lines, 5000))  # cap to avoid abuse
    level = (level or "").strip().upper() or None
    grep_low = (grep or "").lower() or None

    q = deque(maxlen=max_lines)
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                keep = True
                if level:
                    # assumes format: "YYYY-mm-dd HH:MM:SS | LEVEL | message"
                    keep = f"| {level} |" in line
                if keep and grep_low:
                    keep = grep_low in line.lower()
                if keep:
                    q.append(line.rstrip("\n"))
    except FileNotFoundError:
        return [], {"exists": False, "size": 0, "mtime": None}

    try:
        stat = os.stat(path)
        meta = {
            "exists": True,
            "size": stat.st_size,
            "mtime": int(stat.st_mtime),
        }
    except Exception:
        meta = {"exists": True, "size": None, "mtime": None}

    return list(q), meta

@app.get("/logs", response_class=PlainTextResponse)
def get_logs(
    lines: int = 200,
    level: Optional[str] = None,   # e.g., INFO, WARNING, ERROR
    grep: Optional[str] = None,    # substring match, case-insensitive
    raw: bool = True               # return plain text when True; JSON when False
):
    log_path = getattr(logger, "log_path", None)
    if not log_path:
        return PlainTextResponse("Logger has no log_path configured.", status_code=500)

    lines_out, meta = _tail_filter_log(log_path, lines, level, grep)

    if raw:
        # Return as text/plain
        return "\n".join(lines_out)

    # Or as JSON payload (set raw=false)
    return {
        "success": True,
        "path": log_path,
        "meta": meta,
        "count": len(lines_out),
        "lines": lines_out,
        "level": level,
        "grep": grep,
    }

@app.get("/logs/download")
def download_logs():
    log_path = getattr(logger, "log_path", None)
    if not log_path or not os.path.exists(log_path):
        return {"success": False, "error": "Log file not found."}
    return FileResponse(
        log_path,
        media_type="text/plain",
        filename="app.log"
    )

@app.get("/get_student/{roll}")
async def retrieve_student(roll: str):
    try:
        db = DBController()
        student = await db.read_entry({"roll": roll})
        if not student:
            return {"success": False, "status": "not_found", "message": f"No record found for roll {roll}"}

        image_bytes = student.get("image_data")
        if image_bytes:
            student["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")

        student.pop("image_data", None)
        student.pop("embedding", None)
        student.pop("_id", None)

        return {"success": True, "status": "found", "student_details": student}
    except Exception as e:
        return {"success": False, "status": "error", "message": str(e)}

@app.delete("/delete_student/{roll}")
async def delete_student_api(roll: str):
    try:
        db = DBController()
        result = await db.delete_student(roll)
        if result == "deleted":
            return {"success": True, "message": f"Student with roll {roll} deleted"}
        return {"success": False, "message": f"No student found with roll {roll}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/attendance/by_date/{date}")
async def get_attendance_by_date(date: str):
    try:
        db = DBController()
        records = await db.get_attendance_by_date(date)
        if not records:
            return {"success": False, "message": "No attendance found for this date"}
        return {"success": True, "date": date, "attendance": records}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/attendance/by_course")
async def get_attendance_by_course(date: str, course: str):
    try:
        db = DBController()
        result = await db.get_attendance_by_course(date, course)
        if not result:
            return {"success": False, "message": "No records for given date & course"}
        return {"success": True, "date": date, "course": course, "students": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/attendance/by_roll")
async def get_attendance_by_roll(date: str, roll: str):
    try:
        db = DBController()
        result = await db.get_attendance_by_roll(date, roll)
        if not result:
            return {"success": False, "message": "Not marked for this date"}
        return {"success": True, "date": date, "roll": roll, "details": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
