import base64
import sys
import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, Form, File
from pydantic import BaseModel, ConfigDict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from files.db_controller import DBController
from files.logger import logger
from files.processing import DataProcessor
from files.AImodels import AIModules
from dotenv import load_dotenv

load_dotenv()

class StudentData(BaseModel):
    name: str
    roll: str #branch in roll should be in LOWER CASE -- check from frontend
    course_id: str
    image_data: bytes
    model_config = ConfigDict(extra='allow')

app = FastAPI(title="APR Project", version="0.0.2")
logger.info("FastAPI app started.")

@app.post("/register")
async def receive_data(
    name: str = Form(...),
    roll: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        logger.info(f"API /submit called by roll={roll}")

        processor = DataProcessor()
        processed_data = await processor.process_input(name, roll, image)

        db = DBController()
        result = await db.register_student(processed_data)

        logger.info(f"Data successfully stored for roll={roll}")
        return {"success": True, "result": result}

    except Exception as e:
        logger.error(f"Error in /submit for roll={roll}: {e}")
        return {"success": False, "error": str(e)}



@app.post("/login")
async def login(name: str = Form(...), roll: str = Form(...)):
    try:
        db = DBController()
        student = await db.check_login(roll=roll, name=name)

        if not student:
            return {
                "success": False,
                "message": "Invalid credentials or student not found"
            }

        # Convert image to base64 for frontend dashboard display
        image_bytes = student.get("image_data")
        if image_bytes:
            student["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")

        # Remove heavy fields before sending
        student.pop("embedding", None)
        student.pop("image_data", None)

        return {
            "success": True,
            "message": "Login successful",
            "student": student
        }

    except Exception as e:
        logger.error(f"Error in /login: {e}")
        return {
            "success": False,
            "message": "Internal server error",
            "error": str(e)
        }



@app.post("/mark_attendance")
async def mark_attendance(
    roll: str = Form(...),
    course_id: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        logger.info(f"/mark_attendance called for roll={roll}")

        if image.content_type not in ("image/jpeg", "image/png"):
            return {
                "success": False,
                "status": "unmarked",
                "similarity": "",
                "reason": "Only JPG/PNG allowed"
            }

        image_bytes = await image.read()
        models = AIModules()
        match = await models.match_face("unknown", image_bytes)

        matched_roll = match.get("matched_roll")
        similarity = match.get("similarity", "")

        if not matched_roll:
            return {
                "success": False,
                "status": "unmarked",
                "similarity": similarity,
                "reason": "No face match found"
            }

        if matched_roll != roll:
            return {
                "success": False,
                "status": "unmarked",
                "similarity": similarity,
                "reason": f"Face matched with another student ({matched_roll})"
            }

        db = DBController()
        student = await db.read_entry({"roll": matched_roll})

        if not student:
            return {
                "success": False,
                "status": "unmarked",
                "similarity": similarity,
                "reason": "Student not found in DB"
            }

        now = datetime.now()
        attendance_data = {
            "roll": roll,
            "name": student.get("name"),
            "course": course_id,
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "similarity": similarity,
            "status": "marked"
        }

        await db.insert_attendance(attendance_data)
        logger.info(f"Attendance marked for roll={roll}")

        return {
            "success": True,
            "status": "marked",
            "similarity": similarity,
            "reason": ""
        }

    except Exception as e:
        logger.error(f"Error in mark_attendance: {e}")
        return {
            "success": False,
            "status": "unmarked",
            "similarity": "",
            "reason": "Internal server error"
        }

@app.get("/get_student/{roll}")
async def retrieve_student(roll: str):
    try:
        db = DBController()
        student = await db.read_entry({"roll": roll})

        if not student:
            return {
                "success": False,
                "status": "not_found",
                "message": f"No record found for roll {roll}"
            }

        image_bytes = student.get("image_data")
        if image_bytes:
            student["image_base64"] = base64.b64encode(image_bytes).decode("utf-8")

        student.pop("image_data", None)
        student.pop("embedding", None)
        student.pop("_id", None)

        return {
            "success": True,
            "status": "found",
            "student_details": student
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": "Internal server error",
            "error": str(e)
        }

@app.delete("/delete_student/{roll}")
async def delete_student_api(roll: str):
    try:
        db = DBController()
        result = await db.delete_student(roll)

        if result == "deleted":
            return {"success": True, "message": f"Student with roll {roll} deleted"}

        return {"success": False, "message": f"No student found with roll {roll}"}

    except Exception as e:
        return {"success": False, "message": "Internal server error", "error": str(e)}

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
