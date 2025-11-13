# Real-Time Face Anti-Spoofing and Smart Attendance System

This project implements a Real-Time Face Anti-Spoofing (FAS) mechanism using a fine-tuned YOLO11m model, integrated into a comprehensive Smart Attendance System. The system is designed to utilize computer vision for student attendance marking while rigorously preventing fraudulent attempts using images, videos, or displays (spoofing).

For identity verification, the system uses a separate pipeline to generate Face Embeddings using the FaceNet model, which are then compared to registered student embeddings.

The architecture consists of a robust FastAPI backend handling the computer vision tasks and a static HTML/JavaScript/TailwindCSS frontend for user interaction and webcam feed management.

---

## Project Components and Features

### 1. Face Anti-Spoofing (FAS) Module

The core of the security mechanism is the FAS module, which validates the authenticity of the presented face.

* **Model:** YOLO11m (Transfer Learning approach).
* **Task:** Binary Classification (Real vs. Spoof).
* **Methodology:** The pre-trained `yolo11m.pt` model was fine-tuned on a custom webcam-collected dataset.
* **Dataset Integrity:** Data was split strictly by **unseen identities** (70% Train, 20% Validation, 10% Test) to ensure the model's ability to generalize robustly across new users.
* **YOLO Rationale:** YOLO feature maps are leveraged to capture essential anti-spoofing cues, including subtle differences in **skin texture**, **reflective patterns** on screens, and **sharp edges/pixel noise** inherent to digital displays.

### 2. Smart Attendance System

This is the application layer for student management.

* **Functionality:** Includes user registration, login, and camera-based attendance marking.
* **Backend (FastAPI):** Handles face detection, the real-time spoof detection logic, and persistence of attendance records.
* **Frontend (HTML/JS):** Manages the user interface, camera stream acquisition, and asynchronous communication with the backend APIs.

---

## Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | Python, **FastAPI**, Uvicorn | API orchestration, Spoof Detection logic, Attendance Logging. |
| **Model** | **YOLO11m**, PyTorch/Ultralytics | Real-time face anti-spoofing prediction. |
| **Frontend** | HTML5, JavaScript, **TailwindCSS** | User Interface, Webcam stream handling, API communication. |

---

##  Project Architecture

```
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
```
##  Face Anti-Spoofing using YOLO11m

###  Objective

Detect whether the detected face in the webcam feed is:

* 🟢 **Real / Live**
* 🔴 **Spoof / Fake (e.g., printed photo or phone screen)**

###  Model Details

| Feature          | Description                                      |
| ---------------- | ------------------------------------------------ |
| **Base Model**   | `yolo11m.pt`                                     |
| **Task**         | Binary classification – Real vs Spoof            |
| **Approach**     | Transfer Learning (fine-tuning last YOLO layers) |
| **Framework**    | PyTorch + Ultralytics YOLOv11                    |
| **Input Source** | Live webcam frames                               |

###  Dataset

| Split                | Persons | Description                        |
| -------------------- | ------- | ---------------------------------- |
| **Train (70%)**      | 2       | Real faces + Spoof (phone screen)  |
| **Validation (20%)** | 1       | Unseen identity for generalization |
| **Test (10%)**       | 1       | Unseen identity for evaluation     |

This split ensures the model generalizes across different people and doesn’t simply memorize faces.

###  Components

* **Frontend:** HTML, TailwindCSS, JavaScript (Live Camera)
* **Backend:** FastAPI (Python)
* **Model:** YOLO11m Transfer-Learned Anti-Spoofing
* **Database:** JSON / CSV (configurable for production DB)

---

## Backend Setup (FastAPI)

### Create and Activate Virtual Environment

```bash
cd APR/backend
python -m venv venv
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
# If needed
pip install fastapi uvicorn python-multipart
```

###  Run Backend Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### Example API Endpoints

| Method | Endpoint           | Description                  |
| ------ | ------------------ | ---------------------------- |
| `POST` | `/register`        | Register a new student       |
| `POST` | `/mark_attendance` | Mark attendance              |
| `POST` | `/detect`          | Perform anti-spoof detection |
| `GET`  | `/api/v1/...`      | Fetch API resources          |

Logs are stored in `backend/logs/`.

---

##  Frontend Setup (HTML + JS + TailwindCSS)

### Option 1 — Using VS Code Live Server (Recommended)

1. Open folder:

   ```bash
   cd APR/frontend
   ```
2. Right-click `index.html` → **Open with Live Server**
3. Visit: **[http://127.0.0.1:5500/](http://127.0.0.1:5500/)**

### Pages

| Page                  | Description             |
| --------------------- | ----------------------- |
| `index.html`          | Home page               |
| `login.html`          | Student login           |
| `register.html`       | Student registration    |
| `markattendance.html` | Camera-based attendance |

---

## Example Run Sequence

1. **Start Backend**

   ```bash
   cd APR/backend
   uvicorn main:app --reload --port 8000
   ```

2. **Launch Frontend**

   * Open `index.html` in browser via Live Server.

3. **Workflow**

   * Login → Open Camera → Face Detection & Anti-Spoof → Attendance Marked ✅

---
This project is for **educational and research purposes only**.
Commercial use or redistribution requires explicit permission from the author.
---
