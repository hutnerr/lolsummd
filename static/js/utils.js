// ── Escape HTML ──────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Toast helpers ─────────────────────────────────────────────────────────────
function showError(el, msg) {
  el.textContent = msg;
  el.classList.add('active');
}

function clearError(el) {
  el.textContent = '';
  el.classList.remove('active');
}

// ── Fetch wrapper ─────────────────────────────────────────────────────────────
async function postForm(url, formData) {
  const res  = await fetch(url, { method: 'POST', body: formData });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Something went wrong.');
  return data;
}