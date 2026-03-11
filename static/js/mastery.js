// ── Render mastery table ──────────────────────────────────────────────────────
function renderMastery(result) {
  const output = document.getElementById('output');

  if (!result || result.length === 0) {
    output.innerHTML = '';
    return;
  }

  const rows = result.map((champ, i) => {
    const levelClass = champ.level >= 7 ? 'mastery-level-7'
                     : champ.level >= 5 ? 'mastery-level-5'
                     : 'mastery-level-lo';
    const icon = champ.icon
      ? `<img src="${escHtml(champ.icon)}" alt="${escHtml(champ.name)}">`
      : '';
    return `
      <tr>
        <td>${i + 1}</td>
        <td class="champion-cell">${icon}${escHtml(champ.name)}</td>
        <td><span class="mastery-badge ${levelClass}">${champ.level}</span></td>
        <td>${champ.points.toLocaleString()}</td>
      </tr>`;
  }).join('');

  output.innerHTML = `
    <div class="divider"><span>✦</span></div>
    <h3>Combined Mastery</h3>
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Champion</th>
          <th style="text-align:center">Level</th>
          <th style="text-align:right">Points</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}

// ── Get Combined Mastery ──────────────────────────────────────────────────────
const getMasteryBtn = document.getElementById('getMasteryBtn');

getMasteryBtn.addEventListener('click', async function () {
  clearNotif();

  getMasteryBtn.disabled = true;
  getMasteryBtn.classList.add('btn-loading');
  getMasteryBtn.innerHTML = '<span class="spinner"></span>Loading…';

  try {
    const res  = await fetch('/mastery', { method: 'POST' });
    const data = await res.json();
    
    if (!res.ok) throw new Error(data.error || 'Something went wrong.');

    const output = document.getElementById('output');
    output.classList.add('fading');
    await new Promise(r => setTimeout(r, 200));
    renderMastery(data.result);
    output.classList.remove('fading');
    if (data.message) showMessage(data.message);
  } catch (err) {
    showError(err.message);
  } finally {
    getMasteryBtn.disabled = false;
    getMasteryBtn.classList.remove('btn-loading');
    getMasteryBtn.textContent = 'Get Combined Mastery';
  }
});