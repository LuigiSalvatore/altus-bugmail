// ─── Commit Prompt View ───────────────────────────────────────
// Full commit-prompt system: form, prompt generation, branch/repo management.
// This is a self-contained feature module.

import state from '../state/store.js';
import { toast } from '../ui/notifications.js';
import { esc } from '../utils/dom.js';
import { LS_CS, LS_RE, LS_FH, DEF_BRANCH, DEF_REPO } from '../utils/constants.js';

// ─── Commit state ─────────────────────────────────────────────

let cs = {
  bugName: '', bugLink: '', bugDesc: '',
  files: [{ file: '', desc: '' }],
  repo: DEF_REPO, branch: DEF_BRANCH, hash: '', notes: ''
};

function loadCS() {
  try {
    const s = localStorage.getItem(LS_CS);
    if (s) cs = { ...cs, ...JSON.parse(s) };
  } catch (e) { /* ignore */ }
  if (!cs.files?.length) cs.files = [{ file: '', desc: '' }];
}

function saveCS() {
  localStorage.setItem(LS_CS, JSON.stringify(cs));
}

// ─── Branch/Repo persistence ──────────────────────────────────

function getBranchesKey(repo) {
  return `bz_branches_${(repo || 'default').replace(/[^a-zA-Z0-9_]/g, '_')}`;
}
function getBranches(repo) {
  const k = getBranchesKey(repo || cs.repo);
  try { return JSON.parse(localStorage.getItem(k)) || [DEF_BRANCH]; }
  catch (e) { return [DEF_BRANCH]; }
}
function saveBranches(a, repo) {
  localStorage.setItem(getBranchesKey(repo || cs.repo), JSON.stringify(a));
}
function getRepos() {
  try { return JSON.parse(localStorage.getItem(LS_RE)) || [DEF_REPO]; }
  catch (e) { return [DEF_REPO]; }
}
function saveRepos(a) {
  localStorage.setItem(LS_RE, JSON.stringify(a));
}
function getDefBranch(repo) {
  return localStorage.getItem(`bz_def_branch_${(repo || cs.repo).replace(/[^a-zA-Z0-9_]/g, '_')}`) || DEF_BRANCH;
}
function setDefBranch(v, repo) {
  localStorage.setItem(`bz_def_branch_${(repo || cs.repo).replace(/[^a-zA-Z0-9_]/g, '_')}`, v);
}
function getDefRepo() {
  return localStorage.getItem('bz_def_repo') || DEF_REPO;
}
function setDefRepo(v) {
  localStorage.setItem('bz_def_repo', v);
}
function getFileHist() {
  try { return JSON.parse(localStorage.getItem(LS_FH)) || []; }
  catch (e) { return []; }
}
function addToFileHist(f) {
  if (!f.trim()) return;
  let h = getFileHist().filter(x => x !== f);
  h.unshift(f);
  if (h.length > 80) h = h.slice(0, 80);
  localStorage.setItem(LS_FH, JSON.stringify(h));
}

// ─── Form HTML builder ────────────────────────────────────────

function buildFormHTML(formId) {
  const bOpts = getBranches(cs.repo).map(b =>
    `<option value="${esc(b)}"${b === cs.branch ? ' selected' : ''}>${esc(b)}</option>`
  ).join('');
  const rOpts = getRepos().map(r =>
    `<option value="${esc(r)}"${r === cs.repo ? ' selected' : ''}>${esc(r)}</option>`
  ).join('');
  const rowsHTML = cs.files.map((f, i) => `
    <div class="file-row">
      <input type="text" class="form-input" list="file-history-datalist" value="${esc(f.file)}"
        placeholder="path/to/file.c" data-file-idx="${i}" data-file-prop="file">
      <input type="text" class="form-input" value="${esc(f.desc)}"
        placeholder="What changed in this file" data-file-idx="${i}" data-file-prop="desc">
      <button class="btn btn-ghost btn-icon btn-sm file-rm" data-remove-row="${i}"
        title="Remove" ${cs.files.length === 1 ? 'disabled' : ''}>✕</button>
    </div>`).join('');

  return `
    <div class="cg2">
      <div class="form-group">
        <label class="form-label">Bug Name <span class="auto-badge">auto</span></label>
        <input type="text" class="form-input" value="${esc(cs.bugName)}"
          placeholder="Bug XXXXX - Summary" data-cs-field="bugName">
      </div>
      <div class="form-group">
        <label class="form-label">Bug Link</label>
        <input type="text" class="form-input" value="${esc(cs.bugLink)}"
          placeholder="https://…" data-cs-field="bugLink">
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Bug Description / Comments <span class="auto-badge">auto</span></label>
      <textarea class="form-input commit-ta" rows="5"
        placeholder="Comments from the bug…"
        data-cs-field="bugDesc">${esc(cs.bugDesc)}</textarea>
    </div>
    <div class="form-group">
      <div class="fgh"><label class="form-label" style="margin:0">Files Changed</label>
        <button class="btn btn-outline btn-sm" data-action="add-file-row">+ Add Row</button></div>
      <div class="file-rows-head"><span>File path</span><span>Description of change</span><span></span></div>
      <div id="file-rows-${formId}">${rowsHTML}</div>
    </div>
    <div class="cg2">
      <div class="form-group">
        <div class="fgh"><label class="form-label" style="margin:0">Repository</label>
          <button class="btn btn-ghost btn-sm" data-manage-type="repo">✎ Manage</button></div>
        <select class="form-input" data-cs-select="repo">${rOpts}</select>
      </div>
      <div class="form-group">
        <div class="fgh"><label class="form-label" style="margin:0">Branch</label>
          <button class="btn btn-ghost btn-sm" data-manage-type="branch">✎ Manage</button></div>
        <select class="form-input" data-cs-select="branch">${bOpts}</select>
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Commit Hash(es) <span style="color:var(--text-muted);font-weight:400">(fill after committing)</span></label>
      <input type="text" class="form-input" value="${esc(cs.hash || '')}"
        placeholder="e.g. a1b2c3d  or  a1b2c3d e4f5a6b" data-cs-field="hash">
    </div>
    <div class="form-group">
      <label class="form-label">Notes <span style="color:var(--text-muted);font-weight:400">(optional)</span></label>
      <textarea class="form-input commit-ta" rows="2"
        placeholder="Additional notes…"
        data-cs-field="notes">${esc(cs.notes)}</textarea>
    </div>
    <div class="form-group">
      <div class="fgh" style="flex-wrap:wrap;gap:8px;">
        <label class="form-label" style="margin:0">Generated Prompt</label>
        <div style="display:flex;gap:6px;">
          <button class="btn btn-outline btn-sm" data-action="copy-prompt">📋 Copy Prompt</button>
          <button class="btn btn-primary btn-sm" data-action="copy-and-gpt">🤖 Copy &amp; Go to GPT</button>
        </div>
      </div>
      <pre class="commit-out" id="prompt-out-${formId}"></pre>
    </div>`;
}

// ─── Render + wire both form instances ────────────────────────

function renderCommitForms() {
  const i = document.getElementById('commit-form-inline');
  const t = document.getElementById('commit-form-tab');
  if (i) i.innerHTML = buildFormHTML('inline');
  if (t) t.innerHTML = buildFormHTML('tab');

  // Update file-history datalist
  const dl = document.getElementById('file-history-datalist');
  if (dl) dl.innerHTML = getFileHist().map(f => `<option value="${esc(f)}">`).join('');

  updatePromptOutputs();
  _wireFormEvents();
}

function _wireFormEvents() {
  // CS field inputs
  document.querySelectorAll('[data-cs-field]').forEach(el => {
    el.addEventListener('input', () => {
      cs[el.dataset.csField] = el.value;
      saveCS();
      updatePromptOutputs();
    });
  });

  // File row inputs
  document.querySelectorAll('[data-file-idx]').forEach(el => {
    el.addEventListener('input', () => {
      const idx = parseInt(el.dataset.fileIdx);
      const prop = el.dataset.fileProp;
      if (!cs.files[idx]) return;
      cs.files[idx][prop] = el.value;
      if (prop === 'file' && el.value.trim()) addToFileHist(el.value.trim());
      saveCS();
      updatePromptOutputs();
    });
  });

  // Remove file row
  document.querySelectorAll('[data-remove-row]').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.dataset.removeRow);
      if (cs.files.length <= 1) return;
      cs.files.splice(idx, 1);
      saveCS();
      renderCommitForms();
    });
  });

  // Add file row
  document.querySelectorAll('[data-action="add-file-row"]').forEach(btn => {
    btn.addEventListener('click', () => {
      cs.files.push({ file: '', desc: '' });
      saveCS();
      renderCommitForms();
    });
  });

  // Select dropdowns (repo / branch)
  document.querySelectorAll('[data-cs-select="repo"]').forEach(sel => {
    sel.addEventListener('change', () => {
      cs.repo = sel.value;
      cs.branch = getDefBranch(sel.value);
      saveCS();
      renderCommitForms();
    });
  });
  document.querySelectorAll('[data-cs-select="branch"]').forEach(sel => {
    sel.addEventListener('change', () => {
      cs.branch = sel.value;
      saveCS();
      updatePromptOutputs();
    });
  });

  // Manage buttons
  document.querySelectorAll('[data-manage-type]').forEach(btn => {
    btn.addEventListener('click', () => openManageDrop(btn.dataset.manageType));
  });

  // Copy / GPT buttons
  document.querySelectorAll('[data-action="copy-prompt"]').forEach(btn => {
    btn.addEventListener('click', copyPrompt);
  });
  document.querySelectorAll('[data-action="copy-and-gpt"]').forEach(btn => {
    btn.addEventListener('click', copyAndGPT);
  });
}

// ─── Prompt output ────────────────────────────────────────────

function updatePromptOutputs() {
  const p = buildPrompt();
  document.querySelectorAll('.commit-out').forEach(el => el.textContent = p);
}

function buildPrompt() {
  const files = cs.files.filter(f => f.file || f.desc);
  const filesStr = files.length ? files.map(f => `- ${f.file}`).join('\n') : '{PLACEHOLDER}';
  const changesStr = files.length ? files.map(f => `- [${f.file}] ${f.desc}`).join('\n') : '{PLACEHOLDER}';
  const sep = '-----------------------------------------------------------------------';
  return `TASK:
Generate commit messages FIRST.
Generate Bugzilla message ONLY after hashes are provided.

Language: English only
Be precise and deterministic.

--------------------------------
PHASE 1 — COMMIT MESSAGES

Generate one or more commit messages.

FORMAT (STRICT):

<type>: <description>

<body>

Files:
- <file1>
- <file2>

Refs: <name>

RULES:
- type: choose ONE (feat | fix | refactor | build | style | chore | docs | test | ci | sync | merge | revert)
- description: lowercase, imperative, no final period
- body: explain WHAT, WHY, HOW (paragraphs with blank lines)
- files: concise list
- always include Refs

Split commits if multiple logical changes exist.

OUTPUT:

[Commit Message 1]
<text>

[Commit Message 2] (if needed)
<text>

DO NOT generate Bugzilla message in this phase.

--------------------------------
PHASE 2 — BUGZILLA MESSAGE (ONLY AFTER HASHES PROVIDED)

When hashes are given, generate Bugzilla message.

STRUCTURE:

1. Issue summary
2. Root cause
3. Implemented solution

Then append ONE block per commit:

${sep}
\t\t\t\t\t\t\tGit Tracking
${sep}
Repository:\t${cs.repo || '{PLACEHOLDER}'}
Branch:\t\t${cs.branch || '{PLACEHOLDER}'}
Hash:\t\t${cs.hash || '{provided later}'}
${sep}
<ordinal> change

Repeat for each commit (1st change, 2nd change, ...)

Finish with:
Changed to RESOLVED IMPLEMENTED.

OUTPUT:

[Bugzilla Message]
<text>

--------------------------------
INPUT DATA

Bug name: ${cs.bugName || '{PLACEHOLDER}'}
Bug link: ${cs.bugLink || '{PLACEHOLDER}'}
Bug description: ${cs.bugDesc || '{PLACEHOLDER}'}
Changes made:
${changesStr}
Files changed:
${filesStr}
Repository: ${cs.repo || '{PLACEHOLDER}'}
Branch: ${cs.branch || '{PLACEHOLDER}'}
Hashes: ${cs.hash || '{provided later}'}
Notes: ${cs.notes || '(none)'}`;
}

// ─── Auto-fill from current bug ───────────────────────────────

export function autoFillBug() {
  const bug = state.data?.current_bug;
  if (!bug) { toast('No current bug loaded', 'error'); return; }
  cs.bugName = `Bug ${bug.id} - ${bug.summary || ''}`;
  const comments = bug.comments || [];
  cs.bugDesc = comments.length
    ? comments.map(c => `--- ${c.author || '?'} (${(c.creation_time || '').slice(0, 10)}) ---\n${(c.text || '').trim()}`).join('\n\n')
    : (bug.description || '');
  const base = (state.config?.bugzilla_url || '').replace(/\/+$/, '');
  cs.bugLink = `${base}/show_bug.cgi?id=${bug.id}`;
  saveCS();
  renderCommitForms();
  toast(`Filled from Bug #${bug.id}`, 'success');
}

// ─── Clipboard actions ────────────────────────────────────────

async function copyPrompt() {
  try { await navigator.clipboard.writeText(buildPrompt()); toast('Copied!', 'success'); }
  catch (e) { toast('Copy failed', 'error'); }
}

async function copyAndGPT() {
  try { await navigator.clipboard.writeText(buildPrompt()); } catch (e) { /* ignore */ }
  window.open('https://chatgpt.com', '_blank');
  toast('Copied — opening ChatGPT', 'success');
}

// ─── Manage Dropdown Modal ────────────────────────────────────

let _mType = 'branch';

function openManageDrop(type) {
  _mType = type;
  document.getElementById('manage-dropdown-title').textContent =
    type === 'branch' ? 'Manage Branches' : 'Manage Repositories';
  document.getElementById('manage-dropdown-input').value = '';
  document.getElementById('manage-dropdown-input').placeholder =
    type === 'branch' ? 'e.g. v1.15.x.x/develop' : 'e.g. linux-arm';
  renderManageList();
  document.getElementById('manage-dropdown-overlay').classList.add('open');
  setTimeout(() => document.getElementById('manage-dropdown-input').focus(), 60);
}

function closeManageDropdown() {
  document.getElementById('manage-dropdown-overlay').classList.remove('open');
  renderCommitForms();
}

function renderManageList() {
  const items = _mType === 'branch' ? getBranches(cs.repo) : getRepos();
  const def = _mType === 'branch' ? getDefBranch(cs.repo) : getDefRepo();
  document.getElementById('manage-dropdown-list').innerHTML = items.length
    ? items.map((v, i) => `
      <div class="manage-item">
        <span class="manage-item-label">${esc(v)}</span>
        <div class="manage-item-actions">
          ${v === def
            ? '<span class="default-badge">default</span>'
            : `<button class="btn btn-ghost btn-sm" data-set-def="${esc(v)}">Set default</button>`}
          <button class="btn btn-ghost btn-sm btn-icon" data-remove-manage="${i}" title="Remove">✕</button>
        </div>
      </div>`).join('')
    : '<div class="hold-empty">No items</div>';

  // Wire events
  document.querySelectorAll('[data-set-def]').forEach(btn => {
    btn.addEventListener('click', () => _setManageDef(btn.dataset.setDef));
  });
  document.querySelectorAll('[data-remove-manage]').forEach(btn => {
    btn.addEventListener('click', () => _removeManageItem(parseInt(btn.dataset.removeManage)));
  });
}

function _addManageDropdownItem() {
  const v = document.getElementById('manage-dropdown-input').value.trim();
  if (!v) return;
  const items = _mType === 'branch' ? getBranches(cs.repo) : getRepos();
  if (items.includes(v)) { toast('Already exists', 'error'); return; }
  items.push(v);
  _mType === 'branch' ? saveBranches(items, cs.repo) : saveRepos(items);
  document.getElementById('manage-dropdown-input').value = '';
  renderManageList();
}

function _removeManageItem(idx) {
  const items = _mType === 'branch' ? getBranches(cs.repo) : getRepos();
  const removed = items.splice(idx, 1)[0];
  _mType === 'branch' ? saveBranches(items, cs.repo) : saveRepos(items);
  const def = _mType === 'branch' ? getDefBranch(cs.repo) : getDefRepo();
  if (def === removed) {
    _mType === 'branch' ? setDefBranch(items[0] || '', cs.repo) : setDefRepo(items[0] || '');
  }
  renderManageList();
}

function _setManageDef(v) {
  _mType === 'branch' ? setDefBranch(v, cs.repo) : setDefRepo(v);
  if (_mType === 'branch') cs.branch = v; else cs.repo = v;
  saveCS();
  renderManageList();
}

// ─── Init ─────────────────────────────────────────────────────

/**
 * Initialise the commit prompt system.
 * Call once after DOM is ready.
 */
export function initCommitSystem() {
  loadCS();
  if (!cs.repo)   cs.repo   = getDefRepo();
  if (!cs.branch) cs.branch = getDefBranch(cs.repo);
  renderCommitForms();

  // Manage dropdown modal events
  document.getElementById('manage-dropdown-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') _addManageDropdownItem();
  });
  document.getElementById('manage-dropdown-overlay').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeManageDropdown();
  });
  // "Done" button
  document.getElementById('btn-manage-done').addEventListener('click', closeManageDropdown);
  // "Add" button
  document.getElementById('btn-manage-add').addEventListener('click', _addManageDropdownItem);

  // "Fill from current bug" button on the commit tab panel
  document.getElementById('btn-fill-from-bug').addEventListener('click', autoFillBug);
}
