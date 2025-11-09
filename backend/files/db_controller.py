# files/db_controller.py
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from files.logger import logger
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME_STUDENT = os.getenv("COLLECTION_NAME_STUDENT")
COLLECTION_NAME_ATTENDANCE = os.getenv("COLLECTION_NAME_ATTENDANCE")


class DBController:
    def __init__(self):
        self.version = "0.0.3"
        self.module_name = "DBController"
        self.client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        self.db = None
        self.students = None
        self.attendance = None

        logger.info(f"{self.module_name} initialized (v{self.version})")
        self.connect()

    def info(self) -> Dict[str, Any]:
        return {"module_name": self.module_name, "version": self.version}

    def connect(self):
        try:
            if not MONGO_URI:
                raise ValueError("MONGO_URI not found in env")

            if not DB_NAME or not COLLECTION_NAME_STUDENT or not COLLECTION_NAME_ATTENDANCE:
                raise ValueError("DB_NAME or collection env vars missing")

            self.client = AsyncIOMotorClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.students = self.db[COLLECTION_NAME_STUDENT]
            self.attendance = self.db[COLLECTION_NAME_ATTENDANCE]

            logger.info(f"{self.module_name} connected to collections: {COLLECTION_NAME_STUDENT}, {COLLECTION_NAME_ATTENDANCE}")

        except Exception as e:
            logger.error(f"{self.module_name} connection failed: {e}")
            raise e

    # ---------------- Student functions ---------------- #
    async def register_student(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            roll_raw = data.get("roll")
            if not roll_raw:
                raise ValueError("Missing 'roll' in data")
            roll = roll_raw.strip().lower()
            data["roll"] = roll  # ensure stored roll is normalized

            result = await self.students.update_one(
                {"roll": roll},
                {"$set": data},
                upsert=True
            )

            if result.upserted_id:
                logger.info(f"{self.module_name}: inserted new roll={roll}")
                return {"inserted_id": str(result.upserted_id)}
            else:
                logger.info(f"{self.module_name}: updated existing roll={roll}")
                return {"updated_roll": roll}

        except Exception as e:
            logger.error(f"{self.module_name} create_entry error: {e}")
            raise e

    async def check_login(self, roll: str | None = None, name: str | None = None) -> dict | None:
        if not roll and not name:
            raise ValueError("Provide at least one of: roll or name")

        query: Dict[str, Any] = {}
        if roll:
            query["roll"] = roll.strip().lower()
        if name:
            query["name"] = name.strip()

        doc = await self.students.find_one(query)
        if doc:
            doc.pop("_id", None)  # remove MongoDB ObjectId for clean output
            return doc
        return None

    async def read_entry(self, query: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # normalize roll query if present
            if "roll" in query and isinstance(query["roll"], str):
                query["roll"] = query["roll"].strip().lower()

            doc = await self.students.find_one(query)
            if doc:
                # Remove MongoDB _id to avoid serialization issues
                doc.pop("_id", None)
            return doc
        except Exception as e:
            logger.error(f"{self.module_name} read_entry error: {e}")
            raise e

    async def fetch_all_entries(self) -> List[Dict[str, Any]]:
        try:
            cursor = self.students.find({})
            docs = []
            async for doc in cursor:
                doc.pop("_id", None)
                docs.append(doc)
            logger.info(f"{self.module_name}: fetched {len(docs)} students")
            return docs
        except Exception as e:
            logger.error(f"{self.module_name} fetch_all_entries error: {e}")
            raise e

    async def delete_student(self, roll: str) -> str:
        try:
            if not roll:
                return "not_found"
            roll_n = roll.strip().lower()
            res = await self.students.delete_one({"roll": roll_n})
            if res.deleted_count == 0:
                logger.info(f"{self.module_name}: delete_student not found: {roll_n}")
                return "not_found"
            logger.info(f"{self.module_name}: deleted student {roll_n}")
            return "deleted"
        except Exception as e:
            logger.error(f"{self.module_name} delete_student error: {e}")
            raise e

    # ---------------- Attendance functions ---------------- #
    async def insert_attendance(self, data: Dict[str, Any]) -> str:
        try:
            roll = data.get("roll")
            course = data.get("course")
            date_str = data.get("date")
            if not (roll and course and date_str):
                raise ValueError("Missing roll/course/date in attendance data")

            # nested path
            path = f"courses.{course}.students.{roll}"
            student_attendance = {
                "name": data.get("name"),
                "roll": roll,
                "timestamp": data.get("timestamp"),
                "status": data.get("status", "marked"),
                "similarity": data.get("similarity", None)
            }

            # check if already exists
            existing = await self.attendance.find_one({"date": date_str, path: {"$exists": True}})
            if existing:
                logger.info(f"{self.module_name}: duplicate attendance for roll={roll}, course={course}, date={date_str}")
                return "duplicate"

            update_doc = {"$set": {path: student_attendance}}
            result = await self.attendance.update_one({"date": date_str}, update_doc, upsert=True)

            logger.info(f"{self.module_name}: attendance inserted for roll={roll} date={date_str} course={course}")
            return "inserted"
        except Exception as e:
            logger.error(f"{self.module_name} insert_attendance error: {e}")
            return "error"

    async def get_attendance_by_date(self, date: str) -> Dict[str, Any]:
        try:
            doc = await self.attendance.find_one({"date": date})
            if not doc:
                return {}
            doc.pop("_id", None)
            return doc
        except Exception as e:
            logger.error(f"{self.module_name} get_attendance_by_date error: {e}")
            raise e

    async def get_attendance_by_course(self, date: str, course: str) -> Dict[str, Any]:
        try:
            doc = await self.attendance.find_one({"date": date})
            if not doc:
                return {}
            courses = doc.get("courses", {})
            return courses.get(course, {}).get("students", {})
        except Exception as e:
            logger.error(f"{self.module_name} get_attendance_by_course error: {e}")
            raise e

    async def get_attendance_by_roll(self, date: str, roll: str) -> Dict[str, Any]:
        try:
            doc = await self.attendance.find_one({"date": date})
            if not doc:
                return {}
            courses = doc.get("courses", {})
            # find roll under any course
            for course_id, cdata in (courses.items() if isinstance(courses, dict) else []):
                students = cdata.get("students", {})
                if roll in students:
                    return students[roll]
            return {}
        except Exception as e:
            logger.error(f"{self.module_name} get_attendance_by_roll error: {e}")
            raise e
