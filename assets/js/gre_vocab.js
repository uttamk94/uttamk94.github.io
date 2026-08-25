/* ===== GRE Vocabulary Builder - Frontend App ===== */

const TIER_MAP = {
  'essential': 'Essential', 'high': 'High Priority',
  'medium': 'Medium Priority', 'review': 'Review'
};

const State = {
  words: [],
  filtered: [],
  mode: 'browse',
  learned: new Set(),
  searchTerm: '',
  tierFilter: 'all',
  posFilter: 'all',
  quiz: {
    question: null,
    options: [],
    correctAnswer: '',
    score: 0,
    total: 0,
    answered: false,
    currentWord: null,
  }
};

const $ = (id) => document.getElementById(id);

function cacheElements() {
  Object.assign(elements, {
    wordSearch: $('wordSearch'),
    clearSearch: $('clearSearch'),
    tierFilter: $('tierFilter'),
    posFilter: $('posFilter'),
    browseMode: $('browseMode'),
    quizMode: $('quizMode'),
    contentArea: $('contentArea'),
    resultsInfo: $('resultsInfo'),
    resultCount: $('resultCount'),
    heroStats: $('heroStats'),
    progressContainer: $('progressContainer'),
    progressFill: $('progressFill'),
    progressCount: $('progressCount'),
  });
}
const elements = {};

function getTierKey(tierName) {
  if (tierName === 'Essential') return 'essential';
  if (tierName === 'High Priority') return 'high';
  if (tierName === 'Medium Priority') return 'medium';
  return 'review';
}

function loadLearnedWords() {
  try {
    const saved = localStorage.getItem('gre_vocabulary_learned');
    if (saved) {
      State.learned = new Set(JSON.parse(saved));
      updateProgress();
    }
  } catch (e) {
    State.learned = new Set();
  }
}

function saveLearnedWords() {
  localStorage.setItem('gre_vocabulary_learned', JSON.stringify([...State.learned]));
}

function toggleLearned(word) {
  if (State.learned.has(word)) {
    State.learned.delete(word);
  } else {
    State.learned.add(word);
  }
  saveLearnedWords();
  updateProgress();
  render();
}

function updateProgress() {
  const total = State.words.length;
  const learned = State.learned.size;
  elements.progressContainer.style.display = total > 0 ? 'block' : 'none';
  if (total > 0) {
    const percent = Math.round((learned / total) * 100);
    elements.progressFill.style.width = percent + '%';
    elements.progressCount.textContent = `${learned}/${total} learned`;
  }
}

function updateStats() {
  elements.heroStats.innerHTML = '';
  const stats = [
    { label: 'Words Total', value: State.words.length },
    { label: 'Learned', value: State.learned.size },
    { label: 'Remaining', value: State.words.length - State.learned.size },
  ];
  stats.forEach(s => {
    const span = document.createElement('span');
    span.className = 'stat-badge';
    span.textContent = `${s.label}: ${s.value}`;
    elements.heroStats.appendChild(span);
  });
  updateProgress();
}

async function loadData() {
  elements.contentArea.innerHTML = '<div class="loading-message">Loading vocabulary words...</div>';
  try {
    const response = await fetch('../data/gre_words/all_words.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    State.words = await response.json();
    updateStats();
    applyFilters();
  } catch (error) {
    elements.contentArea.innerHTML =
      '<div class="gre-empty"><h3>Failed to load vocabulary data</h3><p>' +
      error.message + '</p></div>';
    console.error('Load error:', error);
  }
}

function render() {
  if (State.mode === 'browse') {
    renderWordList();
  } else {
    renderQuiz();
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderWordList() {
  if (State.filtered.length === 0) {
    elements.contentArea.innerHTML =
      '<div class="gre-empty"><h3>No words found</h3><p>Try adjusting your search or filters.</p></div>';
    return;
  }
  const html = State.filtered.map(w => renderWordCard(w)).join('');
  elements.contentArea.innerHTML = html;
}

function renderWordCard(w) {
  const tierKey = getTierKey(w.tier);
  const isLearned = State.learned.has(w.word);
  const synonyms = w.synonyms ? w.synonyms.split(';').map(s => s.trim()).filter(Boolean) : [];
  const antonyms = w.antonyms ? w.antonyms.split(';').map(a => a.trim()).filter(Boolean) : [];
  const examples = [w.example_1, w.example_2, w.example_3].filter(Boolean);

  return `
<div class="gre-word-card ${isLearned ? 'learned' : ''}">
  <button class="gre-learned-btn ${isLearned ? 'learned' : ''}"
    onclick="toggleLearned('${escapeHtml(w.word)}')"
    title="${isLearned ? 'Mark as unlearned' : 'Mark as learned'}">
    ${isLearned ? '✓' : '○'}
  </button>
  <div class="gre-word-header">
    <h2 class="gre-word-title">${escapeHtml(w.word)}</h2>
    <span class="gre-word-pos">${escapeHtml(w.pos)}</span>
    <span class="gre-tier-badge tier-${tierKey}">${escapeHtml(w.tier)}</span>
    <span class="gre-word-rank">#${w.rank}</span>
  </div>
  <p class="gre-word-definition">${escapeHtml(w.definition)}</p>
  ${synonyms.length > 0 ? `
  <div class="gre-synonyms">
    <strong>Synonyms:</strong>
    <div class="gre-synonym-list">
      ${synonyms.map(s => `<span class="gre-synonym-chip">${escapeHtml(s)}</span>`).join('')}
    </div>
  </div>` : ''}
  ${antonyms.length > 0 ? `
  <div class="gre-antonyms">
    <strong>Antonyms:</strong>
    <div class="gre-antonym-list">
      ${antonyms.map(a => `<span class="gre-antonym-chip">${escapeHtml(a)}</span>`).join('')}
    </div>
  </div>` : ''}
  <div class="gre-usage">
    <div class="gre-usage-where">${escapeHtml(w.usage_where || '')}</div>
    <div class="gre-usage-where-not">${escapeHtml(w.usage_where_not || '')}</div>
  </div>
  ${examples.length > 0 ? `
  <div class="gre-examples">
    ${examples.map(e => `<div class="gre-example">${escapeHtml(e)}</div>`).join('')}
  </div>` : ''}
</div>`;
}

function applyFilters() {
  let words = State.words;
  const term = State.searchTerm.toLowerCase();
  if (term) {
    words = words.filter(w =>
      w.word.toLowerCase().includes(term) ||
      w.definition.toLowerCase().includes(term)
    );
  }
  if (State.tierFilter !== 'all') {
    words = words.filter(w => getTierKey(w.tier) === State.tierFilter);
  }
  if (State.posFilter !== 'all') {
    words = words.filter(w => w.pos === State.posFilter);
  }
  State.filtered = words;
  elements.resultsInfo.style.display = words.length > 0 ? 'block' : 'none';
  elements.resultCount.textContent = words.length;
  render();
}

/* ===== Quiz Mode ===== */

function startQuiz() {
  const pool = State.filtered.length > 0 ? State.filtered : State.words;
  if (pool.length < 4) {
    alert('Not enough words to start a quiz. Add more words first.');
    return;
  }
  State.quiz.score = 0;
  State.quiz.total = 0;
  State.quiz.answered = false;
  State.quiz.currentWord = null;
  nextQuizQuestion(pool);
}

function nextQuizQuestion(pool) {
  const word = pool[Math.floor(Math.random() * pool.length)];
  const correctDef = word.definition;

  // Pick 3 random wrong-answer words from the pool
  const wrong = [];
  const wrongPool = pool.filter(w => w.word !== word.word);
  for (let i = 0; i < 3 && wrongPool.length > 0; i++) {
    const idx = Math.floor(Math.random() * wrongPool.length);
    const choice = wrongPool.splice(idx, 1)[0];
    wrong.push(choice);
  }

  // Shuffle: put correct answer at a random position
  const options = [{ word, definition: correctDef, isCorrect: true }];
  wrong.forEach(w => options.push({ word: w, definition: w.definition, isCorrect: false }));
  // Shuffle
  for (let i = options.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [options[i], options[j]] = [options[j], options[i]];
  }

  State.quiz.question = word;
  State.quiz.options = options;
  State.quiz.answered = false;
  State.quiz.currentWord = word;
  renderQuiz();
}

function checkQuizAnswer(element) {
  if (State.quiz.answered) return;
  State.quiz.answered = true;

  const allOptions = element.closest('.gre-quiz-options').querySelectorAll('.gre-quiz-option');
  allOptions.forEach(el => {
    el.classList.add('disabled');
    el.style.pointerEvents = 'none';
  });

  const isCorrect = element.dataset.correct === 'true';
  if (isCorrect) {
    element.classList.add('correct');
    State.quiz.score++;
    showQuizFeedback(true);
  } else {
    element.classList.add('incorrect');
    // Highlight the correct option
    allOptions.forEach(el => {
      if (el.dataset.correct === 'true') {
        el.classList.add('correct');
      }
    });
    showQuizFeedback(false);
  }
  State.quiz.total++;

  // Update nav buttons
  updateQuizNav();
}

function showQuizFeedback(isCorrect) {
  const feedback = document.getElementById('quizFeedback');
  if (!feedback) return;
  if (isCorrect) {
    feedback.innerHTML = `<span style="color: #10b981; font-weight: 600;">Correct! ✓</span>`;
  } else {
    const w = State.quiz.currentWord;
    feedback.innerHTML = `<strong style="color: #ef4444;">Incorrect.</strong> The word "${w.word}" means: ${w.definition}`;
  }
}

function updateQuizNav() {
  const skipBtn = document.getElementById('quizSkip');
  const nextBtn = document.getElementById('quizNext');
  if (skipBtn) skipBtn.style.display = 'none';
  if (nextBtn) nextBtn.style.display = 'inline-block';
}

function nextQuiz() {
  const pool = State.filtered.length > 0 ? State.filtered : State.words;
  nextQuizQuestion(pool);
}

function renderQuiz() {
  const q = State.quiz.question;
  if (!q) return;

  const scoreDisplay = Math.round((State.quiz.score / Math.max(1, State.quiz.total)) * 100) || 0;

  let html = `
<div class="gre-quiz-container">
  <div class="gre-quiz-card">
    <div class="gre-quiz-header">
      <span class="gre-quiz-progress">Score: ${State.quiz.score}/${State.quiz.total} | ${scoreDisplay}%</span>
      <span class="gre-quiz-progress">Difficulty: ${q.tier || ''}</span>
    </div>

    <div class="gre-quiz-question">${escapeHtml(q.word)}</div>

    <p style="text-align: center; color: var(--text-light); margin-bottom: 1.5rem;">
      Choose the correct definition:
    </p>

    <div class="gre-quiz-options" id="quizOptions">
      ${State.quiz.options.map(opt => `
        <div class="gre-quiz-option"
             data-correct="${opt.isCorrect}"
             onclick="checkQuizAnswer(this)">
          ${escapeHtml(opt.definition)}
        </div>
      `).join('')}
    </div>

    <div id="quizFeedback" style="min-height: 2.5rem; margin: 1rem 0;"></div>

    <div class="gre-quiz-nav">
      <button class="btn btn-secondary" id="quizSkip" onclick="nextQuiz()" style="padding: 0.5rem 1.5rem;">
        Skip
      </button>
      <button class="btn btn-primary" id="quizNext" onclick="nextQuiz()" style="padding: 0.5rem 1.5rem; display: none;">
        Next Question
      </button>
    </div>
  </div>
</div>`;

  elements.contentArea.innerHTML = html;
}

/* ===== Mode Switching ===== */

function setMode(mode) {
  State.mode = mode;
  elements.browseMode.classList.toggle('mode-active', mode === 'browse');
  elements.quizMode.classList.toggle('mode-active', mode === 'quiz');

  if (mode === 'quiz') {
    elements.resultsInfo.style.display = 'none';
    startQuiz();
  } else {
    applyFilters(); // re-renders the word list
  }
}

/* ===== Event Bindings & Init ===== */

function bindEvents() {
  let debounceTimer;
  elements.wordSearch.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      State.searchTerm = e.target.value.trim();
      if (State.mode === 'browse') applyFilters();
    }, 200);
  });

  elements.clearSearch.addEventListener('click', () => {
    elements.wordSearch.value = '';
    State.searchTerm = '';
    if (State.mode === 'browse') applyFilters();
    elements.wordSearch.focus();
  });

  elements.tierFilter.addEventListener('change', (e) => {
    State.tierFilter = e.target.value;
    if (State.mode === 'browse') applyFilters();
  });

  elements.posFilter.addEventListener('change', (e) => {
    State.posFilter = e.target.value;
    if (State.mode === 'browse') applyFilters();
  });

  elements.browseMode.addEventListener('click', () => setMode('browse'));
  elements.quizMode.addEventListener('click', () => setMode('quiz'));
}

document.addEventListener('DOMContentLoaded', () => {
  cacheElements();
  loadLearnedWords();
  bindEvents();
  loadData();
});


