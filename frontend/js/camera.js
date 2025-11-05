// js/camera.js
export async function setupCamera(videoElement) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoElement.srcObject = stream;
    return stream;
  } catch (err) {
    alert("Unable to access camera: " + err.message);
  }
}

export function stopCamera(stream) {
  if (stream) stream.getTracks().forEach((t) => t.stop());
}

export function captureImage(video, canvas) {
  const ctx = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);
  return new Promise((res) => canvas.toBlob(res, "image/jpeg"));
}
