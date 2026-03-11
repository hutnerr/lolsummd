// ── Render account list ───────────────────────────────────────────────────────
function renderAccounts(accounts) {
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

regionSelect.addEventListener('change', updateTagPlaceholder);
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