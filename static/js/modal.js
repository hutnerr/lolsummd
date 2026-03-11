// ── Help Modal ────────────────────────────────────────────────────────────────
function openHelp() {
  document.getElementById('helpModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeHelp() {
  document.getElementById('helpModal').classList.remove('active');
  document.body.style.overflow = '';
}

function closeOnBackdrop(e) {
  if (e.target === document.getElementById('helpModal')) closeHelp();
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeHelp();
});