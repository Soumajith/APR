// js/api.js
export async function postForm(url, formData, extraHeaders = {}) {
  console.log(`📡 POST -> ${url}`);
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: extraHeaders, // may include Authorization
      body: formData,
    });

    // if server returned non-2xx, try to produce helpful error message
    if (!res.ok) {
      // Try to parse json error, otherwise return status text
      let text;
      try {
        text = await res.text();
      } catch (e) {
        text = res.statusText || `HTTP ${res.status}`;
      }
      return { success: false, error: text || `${res.status} ${res.statusText}`, status: res.status };
    }

    const data = await res.json();
    console.log("✅ Response:", data);
    return data;
  } catch (err) {
    console.error("❌ Network/Error:", err);
    return { success: false, error: err.message || String(err) };
  }
}
