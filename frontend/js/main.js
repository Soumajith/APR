// js/main.js
import { postForm } from "./api.js"; // if other code uses it; optional

// Grab navbar controls (IDs must match your HTML)
const navRegister = document.getElementById("nav-register");
const navAttendance = document.getElementById("nav-attendance");
const themeToggle = document.getElementById("theme-toggle");

// Simple auth utilities
export function isLoggedIn() {
  const token = localStorage.getItem("authToken");
  return !!token;
}

export function logout() {
  localStorage.removeItem("authToken");
  localStorage.removeItem("userName");
  // optionally remove userRoll, courseId etc.
  window.location.href = "/login.html";
}

// When user clicks Mark Attendance
navAttendance.onclick = () => {
  if (isLoggedIn()) {
    // Open the standalone page (same tab)
    window.location.href = "/markattendance.html";
  } else {
    alert("Please login to mark attendance.");
    window.location.href = "/login.html";
  }
};

// Optional: show user name on navbar
function refreshNavUser() {
  const name = localStorage.getItem("userName");
  if (name) {
    // create a small element to show name if not present
    if (!document.getElementById("nav-user")) {
      const span = document.createElement("span");
      span.id = "nav-user";
      span.style.marginLeft = "12px";
      span.style.color = "white";
      span.style.fontWeight = 600;
      navAttendance.parentElement.insertBefore(span, navAttendance.nextSibling);
    }
    document.getElementById("nav-user").textContent = name;
  }
}
refreshNavUser();

// theme toggle handler (if not present already)
if (themeToggle) {
  const html = document.documentElement;
  themeToggle.addEventListener("click", () => {
    html.classList.toggle("dark");
    localStorage.setItem("theme", html.classList.contains("dark") ? "dark" : "light");
  });
  if (localStorage.getItem("theme") === "dark") html.classList.add("dark");
}
