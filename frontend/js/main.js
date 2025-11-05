import { setupCamera, stopCamera, captureImage } from "./camera.js";
import { postForm } from "./api.js";
import { showResponse, showLoader } from "./utils.js";
import { REGISTER_API, ATTENDANCE_API } from "./config.js";

// ===== Navbar Switching =====
const navRegister = document.getElementById("nav-register");
const navAttendance = document.getElementById("nav-attendance");
const registerSection = document.getElementById("register-section");
const attendanceSection = document.getElementById("attendance-section");

navRegister.onclick = () => switchSection("register");
navAttendance.onclick = () => switchSection("attendance");

function switchSection(section) {
  const isRegister = section === "register";

  // Update navbar button styles
  if (isRegister) {
    navRegister.classList.add("active");
    navAttendance.classList.remove("active");
  } else {
    navRegister.classList.remove("active");
    navAttendance.classList.add("active");
  }

  // Show/hide sections
  if (isRegister) {
    registerSection.classList.remove("hidden");
    registerSection.classList.add("active-section");
    attendanceSection.classList.add("hidden");
    attendanceSection.classList.remove("active-section");
  } else {
    registerSection.classList.add("hidden");
    registerSection.classList.remove("active-section");
    attendanceSection.classList.remove("hidden");
    attendanceSection.classList.add("active-section");
  }
}

// ===== Registration =====
let regStream, regImageBlob;
const regVideo = document.getElementById("reg-video");
const regCanvas = document.getElementById("reg-canvas");
const regCapture = document.getElementById("reg-capture");
const regRetry = document.getElementById("reg-retry");

setupCamera(regVideo).then((s) => (regStream = s));

regCapture.onclick = async () => {
  regImageBlob = await captureImage(regVideo, regCanvas);
  if (!regImageBlob) return alert("Failed to capture image!");

  // Show canvas, hide video
  regCanvas.classList.remove("hidden");
  regVideo.classList.add("hidden");

  // Toggle buttons
  regCapture.classList.add("hidden");
  regRetry.classList.remove("hidden");

  stopCamera(regStream);
};

regRetry.onclick = async () => {
  // Hide canvas, show video
  regCanvas.classList.add("hidden");
  regVideo.classList.remove("hidden");

  // Toggle buttons
  regCapture.classList.remove("hidden");
  regRetry.classList.add("hidden");

  regImageBlob = null;
  setupCamera(regVideo).then((s) => (regStream = s));
};

document.getElementById("register-form").onsubmit = async (e) => {
  e.preventDefault();
  const name = document.getElementById("reg-name").value.trim();
  const roll = document.getElementById("reg-roll").value.trim();
  const responseDiv = document.getElementById("register-response");

  if (!regImageBlob) return alert("Capture an image first!");

  const formData = new FormData();
  formData.append("name", name);
  formData.append("roll", roll);
  formData.append("image", regImageBlob, "photo.jpg");

  showLoader(responseDiv);
  const data = await postForm(REGISTER_API, formData);
  showLoader(responseDiv, false);
  showResponse(
    responseDiv,
    data.success ? "✅ Registered successfully!" : `❌ ${data.error}`,
    data.success
  );
};

// ===== Attendance =====
let attStream, attImageBlob;
const attVideo = document.getElementById("att-video");
const attCanvas = document.getElementById("att-canvas");
const attCapture = document.getElementById("att-capture");
const attRetry = document.getElementById("att-retry");

setupCamera(attVideo).then((s) => (attStream = s));

attCapture.onclick = async () => {
  attImageBlob = await captureImage(attVideo, attCanvas);
  if (!attImageBlob) return alert("Failed to capture image!");

  // Show canvas, hide video
  attCanvas.classList.remove("hidden");
  attVideo.classList.add("hidden");

  // Toggle buttons
  attCapture.classList.add("hidden");
  attRetry.classList.remove("hidden");

  stopCamera(attStream);
};

attRetry.onclick = async () => {
  // Hide canvas, show video
  attCanvas.classList.add("hidden");
  attVideo.classList.remove("hidden");

  // Toggle buttons
  attCapture.classList.remove("hidden");
  attRetry.classList.add("hidden");

  attImageBlob = null;
  setupCamera(attVideo).then((s) => (attStream = s));
};

document.getElementById("attendance-form").onsubmit = async (e) => {
  e.preventDefault();
  const roll = document.getElementById("att-roll").value.trim();
  const course_id = document.getElementById("att-course").value.trim();
  const responseDiv = document.getElementById("attendance-response");

  if (!attImageBlob) return alert("Capture an image first!");

  const formData = new FormData();
  formData.append("roll", roll);
  formData.append("course_id", course_id);
  formData.append("image", attImageBlob, "photo.jpg");

  showLoader(responseDiv);
  const data = await postForm(ATTENDANCE_API, formData);
  showLoader(responseDiv, false);

  if (data.success) {
    showResponse(
      responseDiv,
      `✅ Attendance ${data.status} | Similarity: ${data.similarity}`,
      true
    );
  } else {
    showResponse(
      responseDiv,
      `❌ ${data.reason || "Failed to mark attendance"}`,
      false
    );
  }
};
