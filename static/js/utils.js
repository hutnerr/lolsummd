// ── Escape HTML ──────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Notification bar helpers ──────────────────────────────────────────────────
const errorBar    = document.getElementById('errorBar');
const errorBarMsg = document.getElementById('errorBarMessage');

function showMessage(msg) {
  errorBarMsg.textContent = msg;
  errorBar.classList.remove('error');
  errorBar.classList.add('success', 'active');
}

function showError(msg) {
  errorBarMsg.textContent = msg;
  errorBar.classList.remove('success');
  errorBar.classList.add('error', 'active');
}

function clearNotif() {
  errorBarMsg.textContent = '';
  errorBar.classList.remove('active', 'error', 'success');
}

// ── Fetch wrapper ─────────────────────────────────────────────────────────────
async function postForm(url, formData) {
  const res  = await fetch(url, { method: 'POST', body: formData });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Something went wrong.');
  return data;
}