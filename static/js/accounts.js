// ── State ─────────────────────────────────────────────────────────────────────
let currentAccounts = [];

// ── Local storage ─────────────────────────────────────────────────────────────
const ACCOUNTS_STORAGE_KEY = 'lolsummd_accounts';

function saveAccountsToStorage(accounts) {
  if (accounts.length === 0) {
    localStorage.removeItem(ACCOUNTS_STORAGE_KEY);
  } else {
    localStorage.setItem(ACCOUNTS_STORAGE_KEY, JSON.stringify(accounts));
  }
}

function loadAccountsFromStorage() {
  try {
    const raw = localStorage.getItem(ACCOUNTS_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed) && parsed.length > 0) return parsed;
  } catch {}
  return null;
}

// ── URL param encoding ────────────────────────────────────────────────────────
function parseUrlAccounts() {
  const params = new URLSearchParams(window.location.search);
  const raw = params.get('a');
  if (!raw) return null;
  try {
    const accounts = raw.split(',')
      .map(s => s.split('~').map(decodeURIComponent))
      .filter(parts => parts.length === 3 && parts.every(p => p.trim()));
    return accounts.length > 0 ? accounts : null;
  } catch {
    return null;
  }
}

function buildShareUrl(accounts) {
  const encoded = accounts
    .map(([u, t, r]) => [u, t, r].map(encodeURIComponent).join('~'))
    .join(',');
  const url = new URL(window.location.href);
  url.search = '?a=' + encoded;
  return url.toString();
}

// ── Restore accounts via server (no Riot API validation) ──────────────────────
async function restoreAccounts(accounts) {
  const fd = new FormData();
  fd.set('action', 'restore');
  fd.set('accounts', JSON.stringify(accounts));
  try {
    const data = await postForm('/accounts', fd);
    renderAccounts(data.accounts);
    return data.accounts;
  } catch {
    return [];
  }
}

// ── Render account list ───────────────────────────────────────────────────────
function renderAccounts(accounts) {
  currentAccounts = accounts;
  saveAccountsToStorage(accounts);

  const list    = document.getElementById('accountList');
  const divider = document.getElementById('accountDivider');
  const actions = document.getElementById('actionButtons');

  list.innerHTML = '';

  if (accounts.length === 0) {
    divider.style.display = 'none';
    actions.style.display = 'none';
    return;
  }

  divider.style.display = '';
  actions.style.display = '';

  accounts.forEach(([username, tag, region], index) => {
    const li = document.createElement('li');
    li.innerHTML = `
      <span class="account-name">
        ${escHtml(username)}<span class="hash">#</span><span class="tag">${escHtml(tag)}</span><span class="region"> (${escHtml(region)})</span>
      </span>
      <button class="btn btn-danger remove-btn" data-index="${index}">Remove</button>
    `;
    list.appendChild(li);
  });
}

// ── Tag placeholder + auto-fill ───────────────────────────────────────────────
const tagInput     = document.getElementById('tag');
const regionSelect = document.getElementById('region');

function updateTagPlaceholder() {
  const selected = regionSelect.options[regionSelect.selectedIndex];
  tagInput.placeholder = selected?.dataset.defaultTag || '';
}

// ── Paste handler: split "Summoner#TAG" automatically ────────────────────────
document.getElementById('username').addEventListener('paste', function (e) {
  const pasted = (e.clipboardData || window.clipboardData).getData('text');
  const hash   = pasted.indexOf('#');
  if (hash === -1) return;

  e.preventDefault();
  const name = pasted.slice(0, hash).trim();
  const tag  = pasted.slice(hash + 1).trim().slice(0, 5);

  this.value     = name;
  tagInput.value = tag;
});

const REGION_KEY = 'lolsummd_last_region';

const savedRegion = localStorage.getItem(REGION_KEY);
if (savedRegion) {
  const match = [...regionSelect.options].find(o => o.value === savedRegion);
  if (match) regionSelect.value = savedRegion;
}

regionSelect.addEventListener('change', () => {
  localStorage.setItem(REGION_KEY, regionSelect.value);
  updateTagPlaceholder();
});
updateTagPlaceholder();

// ── Add Account ───────────────────────────────────────────────────────────────
const addForm = document.getElementById('addAccountForm');

addForm.addEventListener('submit', async function (e) {
  e.preventDefault();
  clearNotif();

  if (!tagInput.value.trim()) {
    const selected = regionSelect.options[regionSelect.selectedIndex];
    tagInput.value = selected?.dataset.defaultTag || '';
  }

  const fd = new FormData(this);
  fd.set('action', 'add');

  const masteryBtn = document.getElementById('getMasteryBtn');
  if (masteryBtn) masteryBtn.disabled = true;

  try {
    const data = await postForm('/accounts', fd);
    renderAccounts(data.accounts);
    if (data.message) showMessage(data.message);
    addForm.reset();
    updateTagPlaceholder();
  } catch (err) {
    showError(err.message);
  } finally {
    if (masteryBtn) masteryBtn.disabled = false;
  }
});

// ── Clear Form ────────────────────────────────────────────────────────────────
document.getElementById('clearFormBtn').addEventListener('click', function () {
  document.getElementById('username').value = '';
  tagInput.value = '';
  document.getElementById('username').focus();
});

// ── Remove Account (delegated) ────────────────────────────────────────────────
document.getElementById('accountList').addEventListener('click', async function (e) {
  const btn = e.target.closest('.remove-btn');
  if (!btn) return;

  const fd = new FormData();
  fd.set('action', 'remove');
  fd.set('remove_index', btn.dataset.index);

  try {
    const data = await postForm('/accounts', fd);
    renderAccounts(data.accounts);
    if (data.message) showMessage(data.message);
  } catch (err) {
    showError(err.message);
  }
});

// ── Clear All ─────────────────────────────────────────────────────────────────
document.getElementById('clearAllBtn').addEventListener('click', async function () {
  const fd = new FormData();
  fd.set('action', 'clear');

  try {
    const data = await postForm('/accounts', fd);
    renderAccounts(data.accounts);
    document.getElementById('output').innerHTML = '';
    if (data.message) showMessage(data.message);
  } catch (err) {
    showError(err.message);
  }
});

// ── Share Link ────────────────────────────────────────────────────────────────
document.getElementById('shareBtn').addEventListener('click', async function () {
  if (currentAccounts.length === 0) return;

  const url = buildShareUrl(currentAccounts);
  try {
    await navigator.clipboard.writeText(url);
    showMessage('Link copied to clipboard!');
  } catch {
    // Fallback: select text from a temporary input
    const input = document.createElement('input');
    input.value = url;
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    document.body.removeChild(input);
    showMessage('Link copied to clipboard!');
  }
});

// ── Page load: restore from URL params or local storage ──────────────────────
(async function init() {
  const urlAccounts = parseUrlAccounts();
  if (urlAccounts) {
    history.replaceState(null, '', window.location.pathname);
    await restoreAccounts(urlAccounts);
    showMessage(`Loaded ${urlAccounts.length} account${urlAccounts.length !== 1 ? 's' : ''} from shared link.`);
    return;
  }

  // Seed currentAccounts from server-rendered session
  currentAccounts = window.__INITIAL_ACCOUNTS__ || [];

  if (currentAccounts.length > 0) {
    // Session is active — keep local storage in sync
    saveAccountsToStorage(currentAccounts);
  } else {
    // Session is empty — try to restore from local storage
    const stored = loadAccountsFromStorage();
    if (stored) {
      await restoreAccounts(stored);
    }
  }
})();
