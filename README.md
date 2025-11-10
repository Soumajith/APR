#🧠 Smart Attendance System with Face Anti-Spoofing (YOLO11m Transfer Learning)

A real-time Smart Attendance System powered by Face Recognition and Face Anti-Spoofing to ensure secure, live attendance marking.
This project integrates a YOLO11m-based anti-spoofing model into a FastAPI + TailwindCSS web application to detect whether a face is real (live) or spoofed (e.g., from a phone screen) — preventing attendance fraud.

🚀 Overview

This system enables:

✅ Real-time face recognition using webcam
✅ Anti-spoofing detection via YOLO11m fine-tuned model
✅ Automatic attendance marking through FastAPI backend
✅ User-friendly frontend built with HTML, JavaScript, and TailwindCSS

🧩 Project Architecture
APR/
├── backend/
│   ├── entrypoint/
│   ├── files/
│   ├── logs/
│   ├── models/                # Trained YOLO11m anti-spoof model
│   ├── main.py                # FastAPI entry point
│   ├── API_docs.txt
│   ├── render.yaml
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── assets/
│   │   └── logo.png
│   ├── js/
│   │   ├── api.js
│   │   ├── camera.js
│   │   ├── config.js
│   │   └── main.js
│   ├── index.html
│   ├── login.html
│   ├── markattendance.html
│   └── register.html
│
└── notebooks/
    └── sample_dataset/

🧠 Face Anti-Spoofing using YOLO11m
🎯 Objective

Detect whether the detected face in the webcam feed is:

🟢 Real / Live

🔴 Spoof / Fake (e.g., printed photo or phone screen)

⚙️ Model Details
Feature	Description
Base Model	yolo11m.pt
Task	Binary classification – Real vs Spoof
Approach	Transfer Learning (fine-tuning last YOLO layers)
Framework	PyTorch + Ultralytics YOLOv11
Input Source	Live webcam frames
📊 Dataset
Split	Persons	Description
Train (70%)	2	Real faces + Spoof (phone screen)
Validation (20%)	1	Unseen identity for generalization
Test (10%)	1	Unseen identity for evaluation

This split ensures the model generalizes across different people and doesn’t simply memorize faces.

📈 Training Performance

✅ Smooth convergence with decreasing loss

✅ High precision and recall on validation

✅ Strong generalization to unseen test identities

(Include your plots here — e.g., training curves, mAP graphs, etc.)

💡 Why YOLO11m?

YOLO’s convolutional features capture:

👤 Skin texture & reflectivity

📱 Screen glare & sharp edges (spoof cues)

🔍 Fine-grained pixel artifacts

These make it an excellent backbone for anti-spoofing.

🧩 Smart Attendance System

A complete web-based attendance solution integrating the YOLO11m anti-spoof module.

🖥️ Components

Frontend: HTML, TailwindCSS, JavaScript (Live Camera)

Backend: FastAPI (Python)

Model: YOLO11m Transfer-Learned Anti-Spoofing

Database: JSON / CSV (configurable for production DB)

⚙️ Backend Setup (FastAPI)
1️⃣ Create and Activate Virtual Environment
cd APR/backend
python -m venv venv
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate

2️⃣ Install Dependencies
pip install -r requirements.txt
# If needed
pip install fastapi uvicorn python-multipart

3️⃣ Run Backend Server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload


Backend will be available at:
👉 http://127.0.0.1:8000

Example API Endpoints
Method	Endpoint	Description
POST	/register	Register a new student
POST	/mark_attendance	Mark attendance
POST	/detect	Perform anti-spoof detection
GET	/api/v1/...	Fetch API resources

Logs are stored in backend/logs/.

🎨 Frontend Setup (HTML + JS + TailwindCSS)
Option 1 — Using VS Code Live Server (Recommended)

Open folder:

cd APR/frontend


Right-click index.html → Open with Live Server

Visit: http://127.0.0.1:5500/

Pages
Page	Description
index.html	Home page
login.html	Student login
register.html	Student registration
markattendance.html	Camera-based attendance
▶️ Example Run Sequence

Start Backend

cd APR/backend
uvicorn main:app --reload --port 8000


Launch Frontend

Open index.html in browser via Live Server.

Workflow

Login → Open Camera → Face Detection & Anti-Spoof → Attendance Marked ✅

📜 License

This project is for educational and research purposes only.
Commercial use or redistribution requires explicit permission from the author.

❤️ Acknowledgements

Ultralytics YOLOv11

FastAPI

TailwindCSS

OpenCV

🌟 Future Improvements

🔁 Database integration (PostgreSQL / Firebase)

🔊 Voice feedback after attendance marking

📱 Mobile-friendly UI

📈 Model pruning for faster inference on low-power devices
