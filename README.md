# 📘 Real-Time Face Anti-Spoofing and Smart Attendance System

This project implements a **Real-Time Face Anti-Spoofing (FAS)** mechanism using a fine-tuned **YOLO11m** model, integrated into a comprehensive **Smart Attendance System**. The system is designed to utilize computer vision for student attendance marking while rigorously preventing fraudulent attempts using images, videos, or displays (spoofing).

The architecture consists of a robust **FastAPI** backend handling the computer vision tasks and a static **HTML/JavaScript/TailwindCSS** frontend for user interaction and webcam feed management.

---

## 🚀 Project Components and Features

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

## 🛠️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | Python, **FastAPI**, Uvicorn | API orchestration, Spoof Detection logic, Attendance Logging. |
| **Model** | **YOLO11m**, PyTorch/Ultralytics | Real-time face anti-spoofing prediction. |
| **Frontend** | HTML5, JavaScript, **TailwindCSS** | User Interface, Webcam stream handling, API communication. |

---

## 📂 Project Structure
