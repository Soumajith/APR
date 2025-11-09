# files/AImodels.py
import os
from typing import List, Dict, Any, Optional

import numpy as np
import cv2
from numpy.linalg import norm

from files.db_controller import DBController
from files.logger import logger
from dotenv import load_dotenv

# Load .env for local dev; on Render, real env vars override
load_dotenv()


class AIModules:
    def __init__(self):
        self.module_name = "AIModules"
        self.version = "0.2.0"

        # ---- Lazy-import classes / models ----
        self._yolo_face_cls = None      # type: ignore
        self._facenet_cls = None        # type: ignore
        self.detector = None            # YOLO face detector instance
        self.embedder = None            # FaceNet instance

        self._yolo_spoof_cls = None     # type: ignore
        self._spoof_model = None        # YOLO spoof model instance

        # ---- Model paths (env or defaults) ----
        # Face detector (Ultralytics YOLO) — default to your repo model
        self.face_model_path = self._resolve_path(
            os.environ.get("FACE_MODEL_PATH"),
            default_rel="models/yolov11n-face.pt"
        )
        # Spoof detector (Ultralytics YOLO) — mirror attendance_server default
        self.spoof_model_path = self._resolve_path(
            os.environ.get("SPOOF_MODEL_PATH"),
            default_rel="models/best.pt"  # if your file is elsewhere, set SPOOF_MODEL_PATH in .env
        )

        # ---- Spoof options from env (attendance_server parity) ----
        # Order must match your training!
        self.class_names: List[str] = os.environ.get("CLASS_NAMES", "spoof,real").split(",")
        try:
            self.conf_thresh: float = float(os.environ.get("CONF_THRESH", 0.35))
        except ValueError:
            self.conf_thresh = 0.35
        try:
            self.img_size: int = int(os.environ.get("IMG_SIZE", 640))
        except ValueError:
            self.img_size = 640

        logger.info(
            f"{self.module_name} init (v{self.version}) | "
            f"FACE_MODEL_PATH={self.face_model_path} | SPOOF_MODEL_PATH={self.spoof_model_path}"
        )

    # ---------------- Path helper ----------------
    def _resolve_path(self, path_env_value: Optional[str], default_rel: str) -> str:
        """
        If env provides absolute -> use it.
        If env provides relative -> resolve against project root (parent of files/).
        Else use default relative under project root.
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if path_env_value:
            return path_env_value if os.path.isabs(path_env_value) else os.path.join(project_root, path_env_value)
        return os.path.join(project_root, default_rel)

    # ---------------- Face model lazy loaders ----------------
    def _ensure_face_classes(self):
        if self._yolo_face_cls is None:
            try:
                from ultralytics import YOLO as _YOLO_FACE
                self._yolo_face_cls = _YOLO_FACE
            except Exception as e:
                logger.error(f"{self.module_name}: import ultralytics (face) failed: {e}")
                self._yolo_face_cls = None

        if self._facenet_cls is None:
            try:
                from keras_facenet import FaceNet as _FACENET
                self._facenet_cls = _FACENET
            except Exception as e:
                logger.error(f"{self.module_name}: import keras_facenet failed: {e}")
                self._facenet_cls = None

    def _ensure_face_models(self):
        self._ensure_face_classes()

        if self.detector is None:
            try:
                if self._yolo_face_cls is None:
                    raise RuntimeError("Ultralytics YOLO (face) not available")
                if not os.path.exists(self.face_model_path):
                    raise FileNotFoundError(f"Face model not found at {self.face_model_path}")
                self.detector = self._yolo_face_cls(self.face_model_path)
                logger.info(f"{self.module_name}: YOLO face detector loaded.")
            except Exception as e:
                logger.error(f"{self.module_name}: YOLO face load failed: {e}")
                self.detector = None

        if self.embedder is None:
            try:
                if self._facenet_cls is None:
                    raise RuntimeError("FaceNet not available")
                self.embedder = self._facenet_cls()
                logger.info(f"{self.module_name}: FaceNet embedder loaded.")
            except Exception as e:
                logger.error(f"{self.module_name}: FaceNet load failed: {e}")
                self.embedder = None

    # ---------------- Spoof model lazy loaders ----------------
    def _ensure_spoof_class(self):
        if self._yolo_spoof_cls is None:
            try:
                from ultralytics import YOLO as _YOLO_SPOOF
                self._yolo_spoof_cls = _YOLO_SPOOF
            except Exception as e:
                logger.error(f"{self.module_name}: import ultralytics (spoof) failed: {e}")
                self._yolo_spoof_cls = None

    def _ensure_spoof_model(self):
        self._ensure_spoof_class()
        if self._spoof_model is None:
            if self._yolo_spoof_cls is None:
                raise RuntimeError("Ultralytics YOLO (spoof) not available")
            if not os.path.exists(self.spoof_model_path):
                raise FileNotFoundError(f"Spoof model not found at {self.spoof_model_path}")
            try:
                self._spoof_model = self._yolo_spoof_cls(self.spoof_model_path)
                logger.info(f"{self.module_name}: Spoof YOLO model loaded from {self.spoof_model_path}")
            except Exception as e:
                logger.error(f"{self.module_name}: Spoof YOLO load failed: {e}")
                self._spoof_model = None

    # ---------------- Face API ----------------
    async def create_embeddings(self, roll: str, image_bytes: bytes) -> List[float]:
        """Create FaceNet embedding from the first detected face."""
        self._ensure_face_models()
        if self.embedder is None or self.detector is None:
            raise RuntimeError("Face models not initialized")

        np_img = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image bytes")

        # Run YOLO face on BGR image
        results = self.detector(img)
        if not results or len(results[0].boxes) == 0:
            raise ValueError("No face detected")

        # First detection only
        x1, y1, x2, y2 = map(int, results[0].boxes.xyxy[0])
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

    async def match_face(self, roll: str, image_bytes: bytes) -> Dict[str, Any]:
        """Return best matching roll (cosine similarity) from stored embeddings."""
        self._ensure_face_models()
        if self.embedder is None or self.detector is None:
            raise RuntimeError("Face models not initialized")

        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return {"matched_roll": None, "similarity": 0.0}

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

        # Compare with DB
        db = DBController()
        students = await db.fetch_all_entries()
        if not students:
            return {"matched_roll": None, "similarity": 0.0}

        best_score = -1.0
        best_roll: Optional[str] = None

        for s in students:
            emb = s.get("embedding")
            if not emb:
                continue
            emb_arr = np.asarray(emb, dtype=np.float32)
            denom = float(norm(input_embedding) * norm(emb_arr))
            if denom == 0.0:
                continue
            score = float(np.dot(input_embedding, emb_arr) / denom)
            if score > best_score:
                best_score = score
                best_roll = s.get("roll")

        if best_roll is not None and best_score > 0.6:
            logger.info(f"{self.module_name}: matched roll={best_roll} score={best_score:.3f}")
            return {"matched_roll": best_roll, "similarity": float(best_score)}

        logger.info(f"{self.module_name}: no good match (best={best_score:.3f})")
        return {"matched_roll": None, "similarity": float(best_score if best_score >= 0 else 0.0)}

    # ---------------- Spoof API (parity with attendance_server.py) ----------------
    @staticmethod
    def _read_imagefile(file_bytes: bytes):
        try:
            arr = np.frombuffer(file_bytes, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # BGR
            return img
        except Exception:
            return None

    def _run_yolo_spoof(self, bgr_img) -> List[Dict[str, Any]]:
        """
        Equivalent to attendance_server.run_yolo_on_image().
        Returns list of detections with: x1,y1,x2,y2,conf,cls,label,probs
        """
        self._ensure_spoof_model()
        if self._spoof_model is None:
            raise RuntimeError("Spoof model not initialized")

        if bgr_img is None:
            return []

        try:
            res = self._spoof_model(
                bgr_img,
                conf=self.conf_thresh,
                imgsz=self.img_size,
                verbose=False
            )[0]
        except Exception as e:
            raise RuntimeError(f"Inference error: {e}")

        detections: List[Dict[str, Any]] = []
        boxes = getattr(res, "boxes", None)
        if not boxes:
            return detections

        for box in boxes:
            # xyxy
            try:
                xy = box.xyxy[0].tolist()
            except Exception:
                try:
                    xy = [float(x) for x in box.xyxy]
                except Exception:
                    xy = [0.0, 0.0, 0.0, 0.0]

            # cls & conf
            try:
                cls_id = int(box.cls)
            except Exception:
                cls_id = int(getattr(box, "cls", -1) or -1)

            try:
                conf = float(box.conf)
            except Exception:
                conf = 0.0

            x1, y1, x2, y2 = [float(v) for v in xy]

            # 2-class heuristic probs like your server
            probs: Optional[List[float]] = None
            if len(self.class_names) == 2 and 0 <= cls_id < 2:
                probs = [0.0, 0.0]
                probs[cls_id] = conf
                probs[1 - cls_id] = max(0.0, 1.0 - conf)

            detections.append({
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "conf": conf,
                "cls": cls_id,
                "label": self.class_names[cls_id] if 0 <= cls_id < len(self.class_names) else str(cls_id),
                "probs": probs
            })

        return detections

    def spoof_detect(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Mirror attendance_server /api/attendance decision:
        - decode
        - run YOLO
        - tally 'real' vs 'spoof'
        - choose overall: 'real' | 'spoof' | 'no_face' | best-by-conf (on tie/unknown)
        - return boolean is_spoof along with details
        """
        bgr = self._read_imagefile(image_bytes)
        if bgr is None:
            raise ValueError("Invalid image file")

        detections = self._run_yolo_spoof(bgr)

        counts = {"real": 0, "spoof": 0, "no_face": 0, "unknown": 0}
        for d in detections:
            lbl = str(d.get("label", "")).lower()
            if lbl == "real":
                counts["real"] += 1
            elif lbl == "spoof":
                counts["spoof"] += 1
            else:
                counts["unknown"] += 1

        if not detections:
            overall = "no_face"
        else:
            if counts["real"] > counts["spoof"]:
                overall = "real"
            elif counts["spoof"] > counts["real"]:
                overall = "spoof"
            else:
                # tie / unknown -> pick highest conf label
                best = max(detections, key=lambda x: x.get("conf", 0.0))
                overall = str(best.get("label", "unknown")).lower()

        is_spoof = (overall == "spoof")

        return {
            "is_spoof": bool(is_spoof),
            "overall": overall,
            "counts": counts,
            "detections": detections,
            "count": len(detections),
        }
