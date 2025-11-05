# files/AImodels.py
import os
import numpy as np
import cv2
from numpy.linalg import norm
from keras_facenet import FaceNet
from ultralytics import YOLO

from files.db_controller import DBController
from files.logger import logger

class AIModules:
    def __init__(self):
        self.module_name = "AIModules"
        self.version = "0.0.1"

        # compute model path relative to project
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "models", "yolov11n-face.pt")

        # load models (may be heavy; do it once)
        try:
            self.detector = YOLO(model_path)
        except Exception as e:
            # if YOLO load fails, keep attribute None but log
            logger.error(f"{self.module_name}: YOLO load failed: {e}")
            self.detector = None

        try:
            self.embedder = FaceNet()
        except Exception as e:
            logger.error(f"{self.module_name}: FaceNet load failed: {e}")
            self.embedder = None

        logger.info(f"{self.module_name} initialized (v{self.version})")

    async def create_embeddings(self, roll: str, image_bytes: bytes):
        try:
            if self.embedder is None or self.detector is None:
                raise RuntimeError("Model(s) not initialized")

            # bytes -> numpy buffer -> cv2 image
            np_img = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Invalid image bytes")

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # detect faces
            results = self.detector(img_rgb)
            if not results or len(results[0].boxes) == 0:
                raise ValueError("No face detected")

            # use first box
            x1, y1, x2, y2 = map(int, results[0].boxes.xyxy[0])
            # clamp coords
            h, w = img.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            face = img[y1:y2, x1:x2]
            if face.size == 0:
                raise ValueError("Empty face crop")

            face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face_resized = cv2.resize(face_rgb, (160, 160))
            face_input = np.expand_dims(face_resized, axis=0)

            embedding = self.embedder.embeddings(face_input)[0]
            logger.info(f"{self.module_name}: embeddings created for roll={roll}")
            return embedding.tolist()

        except Exception as e:
            logger.error(f"{self.module_name}: create_embeddings failed for roll={roll}: {e}")
            raise e

    async def match_face(self, roll: str, image_bytes: bytes):
        try:
            if self.embedder is None or self.detector is None:
                raise RuntimeError("Model(s) not initialized")

            # decode and detect
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("Invalid image bytes")

            results = self.detector(frame)
            if not results or len(results[0].boxes) == 0:
                return {"matched_roll": None, "similarity": 0.0}

            x1, y1, x2, y2 = map(int, results[0].boxes.xyxy[0])
            h, w = frame.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                return {"matched_roll": None, "similarity": 0.0}

            face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face_resized = cv2.resize(face_rgb, (160, 160))
            face_input = np.expand_dims(face_resized, axis=0)

            input_embedding = self.embedder.embeddings(face_input)[0]

            # fetch students and compare
            db = DBController()
            students = await db.fetch_all_entries()

            if not students:
                return {"matched_roll": None, "similarity": 0.0}

            best_score = -1.0
            best_student = None
            for s in students:
                emb = s.get("embedding")
                if not emb:
                    continue
                emb_arr = np.array(emb, dtype=np.float32)
                # cosine
                denom = (norm(input_embedding) * norm(emb_arr))
                if denom == 0:
                    continue
                score = float(np.dot(input_embedding, emb_arr) / denom)
                if score > best_score:
                    best_score = score
                    best_student = s

            if best_student is not None and best_score > 0.6:
                matched_roll = best_student.get("roll")
                logger.info(f"{self.module_name}: matched roll={matched_roll} score={best_score:.3f}")
                return {"matched_roll": matched_roll, "similarity": float(best_score)}
            else:
                logger.info(f"{self.module_name}: no good match (best={best_score:.3f})")
                return {"matched_roll": None, "similarity": float(best_score if best_score >= 0 else 0.0)}

        except Exception as e:
            logger.error(f"{self.module_name}: match_face failed for roll={roll}: {e}")
            # return no match with reason logged
            return {"matched_roll": None, "similarity": 0.0}
