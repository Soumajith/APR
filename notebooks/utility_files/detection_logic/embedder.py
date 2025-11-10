from ultralytics import YOLO
import cv2
import os
import numpy as np
import json
from keras_facenet import FaceNet

detector = YOLO("yolov11n-face.pt")
embedder = FaceNet()
base_dir = os.path.dirname(os.path.abspath(__file__))
photo_dir = os.path.join(base_dir, 'photos')
face_data = []
error_files = []

print(os.listdir(photo_dir))

for photo in os.listdir(photo_dir):
    photo_path = os.path.join(photo_dir, photo)
    img = cv2.imread(photo_path)
    if img is None:
        error_files.append(photo)
        continue
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    bounding_box = detector(img)  # top-left x, top-left y, width, height
    for index, face in enumerate(bounding_box[0].boxes.xyxy):
        x1, y1, x2, y2 = map(int, face)
        face_region = img[y1:y2, x1:x2]
        face_rgb = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
        face_resized = cv2.resize(face_rgb, (160, 160))
        face_input = np.expand_dims(face_resized, axis=0)

        embedding = embedder.embeddings(face_input)[0]
        face_data.append({
            "file_name": photo,
            "face_index": index,
            "embedding": embedding.tolist()
        })

print(error_files)

with open("embeddings.json", "w") as f:
    json.dump(face_data, f)
