# Real-Time Face Anti-Spoofing and Smart Attendance System

This project implements a **Real-Time Face Anti-Spoofing (FAS)** mechanism using a fine-tuned **YOLO11m** model, integrated into a comprehensive **Smart Attendance System**. The system is designed to utilize computer vision for student attendance marking while rigorously preventing fraudulent attempts using images, videos, or displays (spoofing).

The architecture consists of a robust **FastAPI** backend handling the computer vision tasks and a static **HTML/JavaScript/TailwindCSS** frontend for user interaction and webcam feed management.

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

## Project Structure

APR/ ├── backend/ # FastAPI Application and Models │ ├── entrypoint/ │ ├── files/ │ ├── logs/ # Runtime logs and attendance records │ ├── models/ # Anti-spoofing model files (YOLO11m) │ ├── main.py # FastAPI entry point │ └── requirements.txt # Backend dependencies │ ├── frontend/ # Static Web Application │ ├── js/ # Core JavaScript logic (API, Camera, Main) │ ├── index.html # Home page │ ├── login.html │ ├── markattendance.html # Attendance marking page with camera │ └── register.html │ └── notebooks/ # Training and Exploration Scripts


---

## Setup and Execution Guide

### 1. Backend Setup (FastAPI)

The backend must be running to handle all attendance and anti-spoofing requests.

**A. Virtual Environment Setup**

```bash
cd APR/backend
python -m venv venv
# Activate the environment
source venv/bin/activate       # macOS/Linux
# OR
venv\Scripts\activate          # Windows
B. Dependency Installation

Install all required Python packages:

Bash

pip install -r requirements.txt
# Ensure core dependencies are present
pip install fastapi uvicorn python-multipart
C. Running the Server

Start the FastAPI server using Uvicorn:

Bash

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
The backend API will be accessible at http://127.0.0.1:8000.

Key API Endpoints:

POST /register: Register a new student.

POST /mark_attendance: Mark attendance after successful spoof detection.

POST /detect: Spoof detection service.

2. Frontend Setup (HTML + JS)
The frontend is a static web application that requires a local server for secure access to the webcam.

Recommended Method (VS Code Live Server):

Open the APR/frontend directory in Visual Studio Code.

Right-click on index.html and select “Open with Live Server”.

The application will be served, typically at: http://127.0.0.1:5500/

Key Frontend Pages:

index.html: Project Home.

markattendance.html: Camera interface for attendance marking.

3. Execution Sequence
Start Backend (See Step 1.C).

Start Frontend (See Step 2).

Access the application URL (e.g., http://127.0.0.1:5500/), proceed to log in, and mark attendance using the camera. The system will automatically perform the Anti-Spoofing check before logging the attendance.
