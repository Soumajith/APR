import cv2
import numpy as np
import json
import os
from keras_facenet import FaceNet
from numpy.linalg import norm
from ultralytics import YOLO


yolo_model = YOLO("yolov11n-face.pt")

embedder = FaceNet()

with open("embeddings.json", "r") as f:
    face_data = json.load(f)

known_embeddings = []
known_names = []

for face in face_data:
    known_embeddings.append(np.array(face["embedding"]))
    name = os.path.splitext(face["file_name"])[0]    # we will use roll number in case of database
    known_names.append(name)

known_embeddings = np.array(known_embeddings)

def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = yolo_model(frame)

    for box in results[0].boxes.xyxy:  # xyxy format: x1, y1, x2, y2
        x1, y1, x2, y2 = map(int, box)
        
        face_region = frame[y1:y2, x1:x2]
        if face_region.size == 0:  
            continue

        face_rgb = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
        face_resized = cv2.resize(face_rgb, (160, 160))
        face_input = np.expand_dims(face_resized, axis=0)

        embedding = embedder.embeddings(face_input)[0]

        similarities = [cosine_similarity(embedding, known_emb) for known_emb in known_embeddings]
        best_match_idx = np.argmax(similarities)
        best_score = similarities[best_match_idx]

        if best_score > 0.6:
            name = known_names[best_match_idx]
        else:
            name = "Unknown"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{name} ({best_score:.2f})", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("YOLO Face Identification", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
