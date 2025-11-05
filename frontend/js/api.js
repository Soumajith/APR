// js/api.js
export async function postForm(url, formData) {
  console.log(`📡 POST -> ${url}`);
  try {
    const res = await fetch(url, { method: "POST", body: formData });
    const data = await res.json();
    console.log("✅ Response:", data);
    return data;
  } catch (err) {
    console.error("❌ Error:", err);
    return { success: false, error: err.message };
  }
}
