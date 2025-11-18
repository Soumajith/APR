// js/main.js
import { postForm } from "./api.js"; 

const navRegister = document.getElementById("nav-register");
const navAttendance = document.getElementById("nav-attendance");
const themeToggle = document.getElementById("theme-toggle");

export function isLoggedIn() {
  const token = localStorage.getItem("authToken");
  return !!token;
}

export function logout() {
  localStorage.removeItem("authToken");
  localStorage.removeItem("userName");
  window.location.href = "/login.html";
}

navAttendance.onclick = () => {
  if (isLoggedIn()) {
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

if (themeToggle) {
  const html = document.documentElement;
  themeToggle.addEventListener("click", () => {
    html.classList.toggle("dark");
    localStorage.setItem("theme", html.classList.contains("dark") ? "dark" : "light");
  });
  if (localStorage.getItem("theme") === "dark") html.classList.add("dark");
}
