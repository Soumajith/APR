export const API_BASE_URL = "http://127.0.0.1:8000";

export const LOGIN_API = `${API_BASE_URL}/login`;
export const REGISTER_API = `${API_BASE_URL}/register`;
export const ATTENDANCE_API = `${API_BASE_URL}/mark_attendance`;
export const DETECT_API = `${API_BASE_URL}/spoof`;

export const SPOOF_THRESHOLD = 0.5;
export const BLUR_THRESHOLD = 2;
