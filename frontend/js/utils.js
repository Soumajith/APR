// js/utils.js
export function showResponse(element, message, isSuccess = true) {
  element.textContent = message;
  element.className = `response ${isSuccess ? "success" : "error"}`;
}

export function showLoader(element, show = true) {
  if (show) {
    element.innerHTML = `<div class="loader"></div>`;
    element.classList.add("loading");
  } else {
    element.classList.remove("loading");
  }
}
