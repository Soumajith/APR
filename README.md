# Smart Attendance System

## Overview

Smart Attendance is a face-recognition-based attendance system consisting of:

* **Frontend (HTML + JavaScript + TailwindCSS)** for user interaction, student login/registration, and camera-based attendance marking.
* **Backend (FastAPI + Python)** for face detection, spoof detection, and attendance logging.

---

## Project Structure

```
APR/
├── backend/
│   ├── entrypoint/
│   ├── files/
│   ├── logs/
│   ├── models/
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

---

## Backend Setup (FastAPI)

### 1. Create and activate a virtual environment

```bash
cd APR/backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If `fastapi` or `uvicorn` are not listed, install them manually:

```bash
pip install fastapi uvicorn python-multipart
```

### 3. Run the backend server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

After running, the backend will be available at:

```
http://127.0.0.1:8000
```

**Example API Endpoints**

* `POST /mark_attendance` — mark attendance for a student
* `POST /register` — register a new student
* `POST /detect` — spoof detection
* `GET /api/v1/...` — fetch other API resources (if configured)

Logs and runtime information are saved under `backend/logs/`.

---

## Frontend Setup (Static HTML + JS)

### Option 1: Using VS Code Live Server (recommended)

1. Open the folder `APR/frontend` in Visual Studio Code.
2. Right-click on `index.html` and select **“Open with Live Server”**.
3. The application will be served at:

   ```
   http://127.0.0.1:5500/
   ```
4. Visit pages:

   * `index.html` — home page
   * `login.html` — login form
   * `register.html` — registration form
   * `markattendance.html` — camera-based attendance marking



## Example Run Sequence

1. Start backend:

   ```bash
   cd APR/backend
   uvicorn main:app --reload --port 8000
   ```

2. Start frontend:


  open `index.html` using Live Server.

3. Open:

   ```
   http://127.0.0.1:5500/
   ```

4. Log in → Mark attendance -> Marked/Not Marked

---

## License

This project is for educational and research purposes. Redistribution and commercial use require permission.

