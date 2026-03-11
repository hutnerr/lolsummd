// ── Sort state ────────────────────────────────────────────────────────────────
let masteryData  = [];           // full result array from the last fetch
let sortKey      = 'points';     // 'points' | 'level' | 'name'
let sortDir      = 'desc';       // 'asc' | 'desc'

function sortedData() {
  return [...masteryData].sort((a, b) => {
    let av, bv;
    if (sortKey === 'name') {
      av = a.name.toLowerCase();
      bv = b.name.toLowerCase();
    } else {
      av = a[sortKey];
      bv = b[sortKey];
    }
    if (av < bv) return sortDir === 'asc' ? -1 : 1;
    if (av > bv) return sortDir === 'asc' ?  1 : -1;
    return 0;
  });
}

// ── Build table rows ──────────────────────────────────────────────────────────
function buildRows(data) {
  return data.map((champ, i) => {
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
}

// ── Update sort indicators on headers ────────────────────────────────────────
function updateHeaders() {
  const headers = {
    name:   document.getElementById('thName'),
    level:  document.getElementById('thLevel'),
    points: document.getElementById('thPoints'),
  };
  const arrow = sortDir === 'asc' ? '↑' : '↓';
  const labels = { name: 'Champion', level: 'Level', points: 'Points' };

  for (const [key, el] of Object.entries(headers)) {
    if (!el) continue;
    el.classList.toggle('th-active', key === sortKey);
    el.innerHTML = key === sortKey
      ? `${labels[key]} <span class="sort-arrow">${arrow}</span>`
      : labels[key];
  }
}

// ── Re-render tbody only (keeps table structure intact) ───────────────────────
function refreshTable() {
  const tbody = document.getElementById('masteryTbody');
  if (!tbody) return;
  tbody.innerHTML = buildRows(sortedData());
  updateHeaders();
}

// ── Build podium (top 3 by points) ───────────────────────────────────────────
function buildPodium(result) {
  const top3 = [...result]
    .sort((a, b) => b.points - a.points)
    .slice(0, 3);

  if (top3.length < 1) return '';

  function podiumSlot(champ, place) {
    if (!champ) return `<div class="podium-slot podium-${place} podium-empty"></div>`;
    const icon = champ.icon
      ? `<img src="${escHtml(champ.icon)}" alt="${escHtml(champ.name)}" class="podium-icon">`
      : `<div class="podium-icon podium-icon-fallback">${escHtml(champ.name[0])}</div>`;
    return `
      <div class="podium-slot podium-${place}">
        <div class="podium-rank">${place}</div>
        ${icon}
        <div class="podium-name">${escHtml(champ.name)}</div>
        <div class="podium-pts">${champ.points.toLocaleString()}</div>
      </div>`;
  }

  return `
    <div class="podium">
      ${podiumSlot(top3[1] || null, 2)}
      ${podiumSlot(top3[0],         1)}
      ${podiumSlot(top3[2] || null, 3)}
    </div>`;
}

// ── Full render (first load or new fetch) ─────────────────────────────────────
function renderMastery(result) {
  const output = document.getElementById('output');

  if (!result || result.length === 0) {
    output.innerHTML = '';
    return;
  }

  masteryData = result;
  sortKey     = 'points';
  sortDir     = 'desc';

  output.innerHTML = `
    <div class="divider"><span>✦</span></div>
    <h3>Combined Mastery</h3>
    ${buildPodium(result)}
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th id="thName"   class="th-sortable">Champion</th>
          <th id="thLevel"  class="th-sortable th-center">Level</th>
          <th id="thPoints" class="th-sortable th-right th-active">
            Points <span class="sort-arrow">↓</span>
          </th>
        </tr>
      </thead>
      <tbody id="masteryTbody">${buildRows(sortedData())}</tbody>
    </table>`;

  // Attach click handlers to sortable headers
  document.getElementById('thName').addEventListener('click',   () => onSort('name'));
  document.getElementById('thLevel').addEventListener('click',  () => onSort('level'));
  document.getElementById('thPoints').addEventListener('click', () => onSort('points'));
}

// ── Sort click handler ────────────────────────────────────────────────────────
function onSort(key) {
  if (sortKey === key) {
    sortDir = sortDir === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey = key;
    sortDir = key === 'name' ? 'asc' : 'desc';  // default: name A→Z, others high→low
  }
  refreshTable();
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