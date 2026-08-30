/* ===== Algorithms Landing Page App ===== */

const State = {
  topics: [],
  filtered: [],
  typeFilter: 'all',
  sortBy: 'priority',
  searchTerm: ''
};

const $ = (id) => document.getElementById(id);
const elements = {};
let manifest = null;

function cacheElements() {
  Object.assign(elements, {
    search: $('algoSearch'),
    clearSearch: $('clearSearch'),
    typeFilter: $('algoType'),
    sortBy: $('algoSort'),
    contentArea: $('contentArea'),
    resultsInfo: $('resultsInfo'),
    resultCount: $('resultCount'),
    heroStats: $('heroStats'),
    backToTop: $('backToTop')
  });
}

function escapeHtml(s) {
  if (!s) return '';
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function updateStats() {
  const total = State.topics.length;
  const types = new Set(State.topics.map(t => t.type)).size;
  const must = State.topics.filter(t => t.priority >= 5).length;
  if (!elements.heroStats) return;
  elements.heroStats.innerHTML = '';
  [['Topics', total], ['Types', types], ['Must-Know', must]].forEach(([label, value]) => {
    const s = document.createElement('span');
    s.className = 'stat-badge';
    s.textContent = label + ': ' + value;
    elements.heroStats.appendChild(s);
  });
}

function renderTypeOptions() {
  const sel = elements.typeFilter;
  sel.innerHTML = '<option value="all">All Types</option>';
  const keys = [];
  State.topics.forEach(t => { if (keys.indexOf(t.type) === -1) keys.push(t.type); });
  keys.forEach(key => {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = (State.topics.find(t => t.type === key) || {}).type_label || key;
    sel.appendChild(opt);
  });
}

async function loadData() {
  elements.contentArea.innerHTML = '<div class="loading-message">Loading algorithms...</div>';
  try {
    const res = await fetch('../data/algorithms/algos.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    manifest = await res.json();
    State.topics = manifest.topics || [];
    renderTypeOptions();
    updateStats();
    applyFilters();
  } catch (e) {
    elements.contentArea.innerHTML =
      '<div class="algo-empty"><h3>Failed to load algorithm data</h3><p>' +
      escapeHtml(e.message) + '</p></div>';
  }
}

function matches(topic, term) {
  if (!term) return true;
  const hay = (topic.name + ' ' + topic.type_label + ' ' + topic.type_icon + ' ' +
    (topic.outline || []).join(' ')).toLowerCase();
  return hay.indexOf(term.toLowerCase()) !== -1;
}

function priorityColor(p) {
  if (p === 5) return '#dc2626';
  if (p === 4) return '#ea580c';
  if (p === 3) return '#2563eb';
  if (p === 2) return '#64748b';
  return '#94a3b8';
}

function topicCard(t) {
  const outline = (t.outline || []).map(o => '<li>' + escapeHtml(o) + '</li>').join('');
  const color = priorityColor(t.priority);
  return '<article class="algo-card">' +
    '<div class="algo-card-head"><span style="font-size:1.5rem;">' + escapeHtml(t.icon) + '</span>' +
    '<h3 class="algo-card-name">' + escapeHtml(t.name) + '</h3>' +
    '<span class="algo-pri" style="background:' + color + ';">' + escapeHtml(t.priority_label) + '</span></div>' +
    '<div class="algo-chips">' +
    '<span class="algo-chip">' + escapeHtml(t.type_icon) + ' ' + escapeHtml(t.type_label) + '</span>' +
    '<span class="algo-chip">' + escapeHtml(t.difficulty) + '</span>' +
    '<span class="algo-chip">' + escapeHtml(t.worst_complexity) + '</span>' +
    '</div>' +
    '<ul class="algo-outline">' + outline + '</ul>' +
    '<a class="btn algo-open" href="' + escapeHtml(t.link) + '" style="padding:.45rem 1rem; font-size:.85rem;">Open Tutorial →</a>' +
    '</article>';
}

function applyFilters() {
  const term = State.searchTerm;
  let list = State.topics.filter(t =>
    (State.typeFilter === 'all' || t.type === State.typeFilter) && matches(t, term));

  if (State.sortBy === 'priority') {
    list = list.slice().sort((a, b) => (b.priority - a.priority) || a.name.localeCompare(b.name));
  } else if (State.sortBy === 'type') {
    list = list.slice().sort((a, b) => a.type_label.localeCompare(b.type_label) || a.name.localeCompare(b.name));
  } else {
    list = list.slice().sort((a, b) => a.name.localeCompare(b.name));
  }

  State.filtered = list;
  if (elements.resultsInfo) elements.resultsInfo.style.display = 'block';
  if (elements.resultCount) elements.resultCount.textContent = list.length;
  render();
}

function render() {
  if (!State.filtered.length) {
    elements.contentArea.innerHTML =
      '<div class="algo-empty"><h3>No algorithms found</h3><p>Try adjusting your search or filters.</p></div>';
    return;
  }
  if (State.sortBy === 'name') {
    elements.contentArea.innerHTML = State.filtered.map(topicCard).join('');
    return;
  }
  const groups = [];
  const seen = {};
  State.filtered.forEach(t => {
    if (!seen[t.type]) {
      seen[t.type] = true;
      groups.push({ key: t.type, label: t.type_label, icon: t.type_icon, items: [] });
    }
    groups.find(g => g.key === t.type).items.push(t);
  });
  elements.contentArea.innerHTML = groups.map(g =>
    '<section class="algo-type-group">' +
    '<header class="algo-type-header"><span class="algo-type-icon">' + escapeHtml(g.icon) + '</span>' +
    '<h3 class="algo-type-title">' + escapeHtml(g.label) + '</h3>' +
    '<span class="algo-type-count">' + g.items.length + '</span></header>' +
    g.items.map(topicCard).join('') +
    '</section>'
  ).join('');
}

function bindEvents() {
  let timer;
  elements.search.addEventListener('input', (e) => {
    clearTimeout(timer);
    timer = setTimeout(() => { State.searchTerm = e.target.value.trim(); applyFilters(); }, 200);
  });
  elements.clearSearch.addEventListener('click', () => {
    elements.search.value = '';
    State.searchTerm = '';
    applyFilters();
    elements.search.focus();
  });
  elements.typeFilter.addEventListener('change', (e) => { State.typeFilter = e.target.value; applyFilters(); });
  elements.sortBy.addEventListener('change', (e) => { State.sortBy = e.target.value; applyFilters(); });

  window.addEventListener('scroll', () => {
    if (elements.backToTop) elements.backToTop.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });
  if (elements.backToTop) {
    elements.backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }
}

document.addEventListener('DOMContentLoaded', () => {
  cacheElements();
  bindEvents();
  loadData();
});

