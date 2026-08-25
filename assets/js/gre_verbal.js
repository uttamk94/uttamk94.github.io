/* ===== GRE Verbal Mock Test - Engine ===== */

const BANK_URL = '../data/gre_verbal/questions.json';
const SESSION_KEY = 'gre_verbal_session';
const HISTORY_KEY = 'gre_verbal_history';

/* percent correct -> estimated scaled score (piecewise-linear interpolation) */
const SCORE_SCALE = [
  [100, 170], [90, 163], [80, 157], [70, 151], [60, 146],
  [50, 142], [40, 138], [30, 134], [20, 131], [0, 130]
];

const TYPE_LABELS = {
  tc: 'Text Completion',
  se: 'Sentence Equivalence',
  rc: 'Reading Comprehension'
};

const RING_RADIUS = 62;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

const App = {
  screen: 'start',
  bank: null,
  session: null,   /* active / resumed test */
  results: null,   /* computed after submit */
  timerId: null,
  tickCount: 0,
  reviewRendered: false
};

const $ = (id) => document.getElementById(id);

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function letter(i) {
  return String.fromCharCode(65 + i);
}

function fmtTime(totalSec) {
  const m = Math.floor(Math.max(0, totalSec) / 60);
  const s = Math.max(0, totalSec) % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function pickN(arr, n) {
  return shuffle(arr.slice()).slice(0, Math.min(n, arr.length));
}

function sameSet(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b)) return false;
  const sa = a.slice().sort((x, y) => x - y);
  const sb = b.slice().sort((x, y) => x - y);
  return sa.length === sb.length && sa.every((v, i) => v === sb[i]);
}

function estimateScore(percentCorrect) {
  const p = Math.max(0, Math.min(100, percentCorrect));
  for (let i = 0; i < SCORE_SCALE.length - 1; i++) {
    const [hiP, hiS] = SCORE_SCALE[i];
    const [loP, loS] = SCORE_SCALE[i + 1];
    if (p <= hiP && p >= loP) {
      const t = (p - loP) / (hiP - loP || 1);
      return Math.round(loS + t * (hiS - loS));
    }
  }
  return 130;
}

function showScreen(name) {
  App.screen = name;
  $('startScreen').classList.toggle('hidden', name !== 'start');
  $('testScreen').classList.toggle('hidden', name !== 'test');
  $('resultsScreen').classList.toggle('hidden', name !== 'results');
  window.scrollTo({ top: 0 });
}

/* ===== Bank loading & boot ===== */

async function loadBank() {
  try {
    const res = await fetch(BANK_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    App.bank = await res.json();
    renderStart();
  } catch (e) {
    $('startScreen').innerHTML =
      '<div class="card"><h3>Failed to load question bank</h3><p>' +
      escapeHtml(e.message) + '</p></div>';
    console.error('Bank load error:', e);
  }
}

/* ===== Test assembly ===== */

function combinations(arr, k) {
  const out = [];
  const rec = (start, cur) => {
    if (cur.length === k) { out.push(cur.slice()); return; }
    for (let i = start; i < arr.length; i++) {
      cur.push(arr[i]);
      rec(i + 1, cur);
      cur.pop();
    }
  };
  rec(0, []);
  return out;
}

function pickRcPassages(passages, targetQs) {
  /* prefer an exact-sum subset of passages */
  for (let k = Math.min(3, passages.length); k >= 1; k--) {
    for (const combo of combinations(passages, k)) {
      if (combo.reduce((n, p) => n + p.questions.length, 0) === targetQs) {
        return shuffle(combo);
      }
    }
  }
  /* fallback: greedy fill from largest, then trim the overflow questions */
  const sorted = passages.slice().sort((a, b) => b.questions.length - a.questions.length);
  const chosen = [];
  let total = 0;
  for (const p of sorted) {
    if (total >= targetQs) break;
    chosen.push(p);
    total += p.questions.length;
  }
  let excess = total - targetQs;
  while (excess > 0 && chosen.length) {
    const last = chosen[chosen.length - 1];
    if (last.questions.length > excess) {
      last.questions = last.questions.slice(0, last.questions.length - excess);
      excess = 0;
    } else {
      excess -= last.questions.length;
      chosen.pop();
    }
  }
  return chosen;
}

function assembleTest() {
  const cfg = App.bank.test_config.composition;
  const tcByBlanks = { 1: [], 2: [], 3: [] };
  App.bank.text_completion.forEach(q => { if (tcByBlanks[q.blanks]) tcByBlanks[q.blanks].push(q); });

  const tc = [
    ...pickN(tcByBlanks[1], cfg.text_completion_single),
    ...pickN(tcByBlanks[2], cfg.text_completion_double),
    ...pickN(tcByBlanks[3], cfg.text_completion_triple)
  ];
  const se = pickN(App.bank.sentence_equivalence, cfg.sentence_equivalence);
  const rcPassages = pickRcPassages(App.bank.reading_comprehension, cfg.reading_comprehension_questions);

  const descriptors = [];
  shuffle(tc).forEach(q => descriptors.push({ kind: 'tc', srcId: q.id }));
  shuffle(se).forEach(q => descriptors.push({ kind: 'se', srcId: q.id }));
  rcPassages.forEach(p => p.questions.forEach(q =>
    descriptors.push({ kind: 'rc', passageId: p.id, qId: q.id })
  ));

  return descriptors;
}

/* Resolve descriptors against the bank into runtime question objects. */
function materializeQuestions(descriptors) {
  return descriptors.map(d => {
    if (d.kind === 'tc') {
      const q = App.bank.text_completion.find(x => x.id === d.srcId);
      return { ...q, kind: 'tc' };
    }
    if (d.kind === 'se') {
      const q = App.bank.sentence_equivalence.find(x => x.id === d.srcId);
      return { ...q, kind: 'se' };
    }
    const passage = App.bank.reading_comprehension.find(p => p.id === d.passageId);
    const q = passage.questions.find(x => x.id === d.qId);
    return { ...q, kind: 'rc', passageRef: passage };
  });
}

/* ===== Session persistence (crash / refresh safety) ===== */

function saveSession() {
  if (!App.session || App.session.submitted) return;
  try {
    localStorage.setItem(SESSION_KEY, JSON.stringify({
      startedAt: App.session.startedAt,
      remainingSec: App.session.remainingSec,
      currentIndex: App.session.currentIndex,
      descriptors: App.session.descriptors,
      answers: App.session.answers,
      marked: App.session.marked
    }));
  } catch (e) { /* storage unavailable - continue in memory */ }
}

function loadSavedSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) { return null; }
}

function clearSavedSession() {
  try { localStorage.removeItem(SESSION_KEY); } catch (e) {}
}

/* ===== Timer ===== */

function startTimer() {
  stopTimer();
  App.timerId = setInterval(() => {
    App.session.remainingSec--;
    App.tickCount++;
    updateTimerDisplay();
    if (App.tickCount % 10 === 0) saveSession();
    if (App.session.remainingSec <= 0) submitTest(true);
  }, 1000);
}

function stopTimer() {
  if (App.timerId) clearInterval(App.timerId);
  App.timerId = null;
}

function updateTimerDisplay() {
  const el = $('timerDisplay');
  el.textContent = fmtTime(App.session.remainingSec);
  el.classList.toggle('warning', App.session.remainingSec < 300);
}

/* ===== Start screen ===== */

function renderStart() {
  const saved = loadSavedSession();
  if (saved && saved.descriptors && !saved.submitted) {
    $('resumeBanner').classList.remove('hidden');
    $('resumeInfo').textContent =
      `An unfinished test was found — ${saved.remainingSec} sec remaining.`;
  } else {
    $('resumeBanner').classList.add('hidden');
  }
  renderHistory();
}

function startNewTest() {
  clearSavedSession();
  App.results = null;
  App.reviewRendered = false;
  const descriptors = assembleTest();
  App.session = {
    startedAt: new Date().toISOString(),
    durationSec: (App.bank.test_config.duration_minutes || 30) * 60,
    remainingSec: (App.bank.test_config.duration_minutes || 30) * 60,
    currentIndex: 0,
    descriptors,
    answers: descriptors.map(() => null),
    marked: descriptors.map(() => false),
    submitted: false
  };
  beginTestUi();
}

function resumeTest() {
  const saved = loadSavedSession();
  if (!saved) return;
  App.results = null;
  App.reviewRendered = false;
  App.session = {
    startedAt: saved.startedAt,
    durationSec: (App.bank.test_config.duration_minutes || 30) * 60,
    remainingSec: saved.remainingSec,
    currentIndex: saved.currentIndex || 0,
    descriptors: saved.descriptors,
    answers: saved.answers,
    marked: saved.marked,
    submitted: false
  };
  beginTestUi();
}

function discardSavedSession() {
  clearSavedSession();
  $('resumeBanner').classList.add('hidden');
}

function beginTestUi() {
  showScreen('test');
  buildPalette();
  updateTimerDisplay();
  startTimer();
  renderQuestion();
  saveSession();
}

/* ===== Answer state helpers ===== */

function currentQuestion() {
  return materializeQuestions([App.session.descriptors[App.session.currentIndex]])[0];
}

function isQuestionAnswered(q, ans) {
  if (!Array.isArray(ans) || ans.length === 0) return false;
  if (q.kind === 'tc') return ans.every(v => v !== null && v !== undefined);
  if (q.kind === 'se') return ans.length === 2;
  return true; /* rc single/multiple/sip all need >=1 selection */
}

function setAnswer(arr) {
  App.session.answers[App.session.currentIndex] = arr;
  saveSession();
  updatePalette();
}

/* ===== Palette ===== */

function buildPalette() {
  const wrap = $('paletteGrid');
  wrap.innerHTML = '';
  App.session.descriptors.forEach((d, i) => {
    const btn = document.createElement('button');
    btn.className = 'pal-q';
    btn.id = `palq-${i}`;
    btn.textContent = i + 1;
    btn.title = TYPE_LABELS[d.kind];
    btn.addEventListener('click', () => goToQuestion(i));
    wrap.appendChild(btn);
  });
  updatePalette();
}

function updatePalette() {
  const qs = materializeQuestions(App.session.descriptors);
  App.session.descriptors.forEach((_, i) => {
    const el = $(`palq-${i}`);
    if (!el) return;
    el.classList.toggle('answered', isQuestionAnswered(qs[i], App.session.answers[i]));
    el.classList.toggle('marked', !!App.session.marked[i]);
    el.classList.toggle('current', i === App.session.currentIndex);
  });
}

/* ===== Question rendering ===== */

function renderQuestion() {
  const idx = App.session.currentIndex;
  const q = currentQuestion();
  const card = $('questionCard');
  const badgeClass = q.kind === 'tc' ? '' : (q.kind === 'se' ? ' se' : ' rc');

  const head = `
    <div class="qcard-head">
      <span class="qtype-badge${badgeClass}">${TYPE_LABELS[q.kind]}</span>
      <span class="qnum">Question ${idx + 1} of ${App.session.descriptors.length}</span>
    </div>`;

  if (q.kind === 'tc') card.innerHTML = head + renderTC(q);
  else if (q.kind === 'se') card.innerHTML = head + renderSE(q);
  else card.innerHTML = head + renderRC(q);

  let answeredCount = 0;
  for (let i = 0; i < App.session.descriptors.length; i++) {
    if (isQuestionAnswered(qsAt(i), App.session.answers[i])) answeredCount++;
  }
  $('progressText').textContent = `${answeredCount} of ${App.session.descriptors.length} answered`;
  $('markBtn').classList.toggle('marked', !!App.session.marked[idx]);
  $('markBtn').innerHTML = App.session.marked[idx] ? '⚑ Marked' : '⚐ Mark for Review';
  $('prevBtn').disabled = idx === 0;
  $('nextBtn').textContent = idx === App.session.descriptors.length - 1 ? 'Finish Test' : 'Next →';
  updatePalette();
}

function qsAt(i) {
  return materializeQuestions([App.session.descriptors[i]])[0];
}

function optionButtonsHTML(options, selectedIdxs, shape) {
  const square = shape === 'square' ? ' square' : '';
  return options.map((opt, oi) => {
    const sel = selectedIdxs && selectedIdxs.includes(oi) ? ' selected' : '';
    return `
      <button class="opt-btn${square}${sel}" data-idx="${oi}">
        <span class="opt-marker">${letter(oi)}</span>
        <span>${escapeHtml(opt)}</span>
      </button>`;
  }).join('');
}

/* --- Text Completion --- */

function renderTC(q) {
  const ans = App.session.answers[App.session.currentIndex] || new Array(q.blanks).fill(null);
  let passage = escapeHtml(q.passage);
  for (let b = 0; b < q.blanks; b++) {
    const chosen = ans[b] !== null && ans[b] !== undefined
      ? escapeHtml(q.option_sets[b][ans[b]]) : `Blank ${b + 1}`;
    passage = passage.replace(`{${b + 1}}`, `<span class="blank-chip" id="chip-${b}">${chosen}</span>`);
  }
  const groups = q.option_sets.map((opts, b) => {
    const sel = ans[b] !== null && ans[b] !== undefined ? [ans[b]] : [];
    return `
      <div class="opt-group">
        <div class="opt-group-title">Blank ${b + 1}</div>
        ${optionButtonsHTML(opts, sel, 'round')}
      </div>`;
  }).join('');
  return `
    <div class="q-instruction">Select one entry from each list to fill the numbered blank${q.blanks > 1 ? 's' : ''} in the passage.</div>
    <p style="font-size:1rem;line-height:1.8;color:var(--text-color);margin-bottom:0.5rem;">${passage}</p>
    ${groups}`;
}

function selectTCChoice(blankIdx, optIdx) {
  const q = currentQuestion();
  const prev = App.session.answers[App.session.currentIndex];
  const ans = (prev || new Array(q.blanks).fill(null)).slice();
  ans[blankIdx] = optIdx;
  setAnswer(ans);
  renderQuestion();
}

/* --- Sentence Equivalence --- */

function renderSE(q) {
  const ans = App.session.answers[App.session.currentIndex] || [];
  const sentence = escapeHtml(q.sentence)
    .replace('|BLANK|', '<strong style="color:var(--primary-dark);">________</strong>');
  const complete = ans.length === 2;
  return `
    <div class="q-instruction">Select the <strong>two</strong> answer choices that, when used to complete the sentence, fit the meaning of the sentence as a whole <em>and</em> produce completed sentences that are alike in meaning.</div>
    <p style="font-size:1.05rem;line-height:1.8;color:var(--text-color);margin-bottom:1rem;">${sentence}</p>
    <div style="display:flex;justify-content:flex-end;margin-bottom:0.6rem;">
      <span class="se-counter${complete ? ' complete' : ''}">${ans.length} of 2 selected</span>
    </div>
    ${optionButtonsHTML(q.options, ans, 'square')}`;
}

function selectSEChoice(optIdx) {
  let ans = (App.session.answers[App.session.currentIndex] || []).slice();
  if (ans.includes(optIdx)) {
    ans = ans.filter(i => i !== optIdx);
  } else if (ans.length < 2) {
    ans.push(optIdx);
  } else {
    ans.shift(); /* replace oldest selection with newest */
    ans.push(optIdx);
  }
  setAnswer(ans);
  renderQuestion();
}

/* --- Reading Comprehension --- */

function renderRC(q) {
  const ans = App.session.answers[App.session.currentIndex] || null;
  const p = q.passageRef;

  let passageHtml;
  if (q.type === 'select_in_passage') {
    passageHtml = p.sentences.map((s, si) => {
      const sel = ans && ans.includes(si) ? ' selected' : '';
      return `<span class="sent${sel}" data-sent="${si}">${escapeHtml(s)}</span>`;
    }).join(' ');
  } else {
    passageHtml = escapeHtml(p.passage);
  }

  let instruction;
  if (q.type === 'single') instruction = 'Select one answer choice.';
  else if (q.type === 'multiple') instruction = 'Select <strong>all</strong> answer choices that apply.';
  else instruction = 'Click on the sentence in the passage that answers the question.';

  let body;
  if (q.type === 'select_in_passage') {
    body = `<p style="font-size:1rem;color:var(--text-color);">${escapeHtml(q.prompt)}</p>`;
  } else {
    body = `
      <p style="font-size:1rem;color:var(--text-color);margin-bottom:0.9rem;">${escapeHtml(q.prompt)}</p>
      ${optionButtonsHTML(q.options, ans || [], q.type === 'multiple' ? 'square' : 'round')}`;
  }

  return `
    <div class="q-instruction">${instruction}</div>
    <div class="passage-box">${passageHtml}</div>
    ${body}`;
}

function selectRCSingle(idx) {
  setAnswer([idx]);
  renderQuestion();
}

function selectRCMultiple(idx) {
  let ans = (App.session.answers[App.session.currentIndex] || []).slice();
  ans = ans.includes(idx) ? ans.filter(i => i !== idx) : [...ans, idx].sort((a, b) => a - b);
  setAnswer(ans);
  renderQuestion();
}

function selectSentence(sentIdx) {
  setAnswer([sentIdx]);
  renderQuestion();
}

/* Delegated clicks for option buttons & sentences inside the question card */
$('questionCard').addEventListener('click', (e) => {
  const optBtn = e.target.closest('.opt-btn');
  if (optBtn) {
    const idx = parseInt(optBtn.dataset.idx, 10);
    const q = currentQuestion();
    if (q.kind === 'tc') {
      /* find which blank's group this button belongs to */
      const groups = Array.from($('questionCard').querySelectorAll('.opt-group'));
      const groupEl = optBtn.closest('.opt-group');
      selectTCChoice(groups.indexOf(groupEl), idx);
    } else if (q.kind === 'se') {
      selectSEChoice(idx);
    } else if (q.type === 'multiple') {
      selectRCMultiple(idx);
    } else {
      selectRCSingle(idx);
    }
    return;
  }
  const sent = e.target.closest('.sent');
  if (sent) selectSentence(parseInt(sent.dataset.sent, 10));
});

/* ===== Navigation ===== */

function goToQuestion(i) {
  App.session.currentIndex = i;
  saveSession();
  renderQuestion();
  window.scrollTo({ top: 0 });
}

function nextQuestion() {
  if (App.session.currentIndex >= App.session.descriptors.length - 1) {
    openSubmitModal();
    return;
  }
  goToQuestion(App.session.currentIndex + 1);
}

function prevQuestion() {
  if (App.session.currentIndex > 0) goToQuestion(App.session.currentIndex - 1);
}

function toggleMark() {
  const i = App.session.currentIndex;
  App.session.marked[i] = !App.session.marked[i];
  saveSession();
  renderQuestion();
}

/* ===== Submit & scoring ===== */

function openSubmitModal() {
  const qs = materializeQuestions(App.session.descriptors);
  const unanswered = qs.filter((q, i) => !isQuestionAnswered(q, App.session.answers[i])).length;
  $('modalUnanswered').textContent = unanswered > 0
    ? `You have ${unanswered} unanswered question${unanswered > 1 ? 's' : ''}. Unanswered questions are scored as incorrect.`
    : 'All questions have been answered. Ready to submit.';
  $('submitModal').classList.add('open');
}

function closeSubmitModal() {
  $('submitModal').classList.remove('open');
}

function computeResults() {
  const qs = materializeQuestions(App.session.descriptors);
  let correct = 0;
  const byType = { tc: [0, 0], se: [0, 0], rc: [0, 0] };
  const perQuestion = qs.map((q, i) => {
    const user = App.session.answers[i];
    const answered = isQuestionAnswered(q, user);
    const isCorrect = answered && sameSet(user, q.answers);
    if (isCorrect) correct++;
    byType[q.kind][1]++;
    if (isCorrect) byType[q.kind][0]++;
    return { q, user, answered, isCorrect };
  });
  const total = qs.length;
  return { perQuestion, correct, total, byType, percent: Math.round((correct / total) * 100) };
}

function submitTest(auto = false) {
  if (!App.session || App.session.submitted) return;
  stopTimer();
  closeSubmitModal();
  App.session.submitted = true;
  App.session.usedSec = App.session.durationSec - Math.max(0, App.session.remainingSec);
  clearSavedSession();

  App.results = computeResults();
  addHistoryEntry({
    date: new Date().toISOString(),
    raw: App.results.correct,
    total: App.results.total,
    est: estimateScore(App.results.percent),
    byType: App.results.byType,
    autoSubmitted: auto
  });
  renderResults(auto);
}

/* ===== Results screen ===== */

function typeBar(label, ct) {
  const [c, t] = ct;
  const pct = t ? Math.round((c / t) * 100) : 0;
  return `
    <div class="bar-row">
      <span>${label}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
      <span class="bar-count">${c}/${t}</span>
    </div>`;
}

function renderResults(auto = false) {
  showScreen('results');
  const r = App.results;
  const est = estimateScore(r.percent);

  $('ringFill').style.strokeDasharray = RING_CIRCUMFERENCE;
  $('ringFill').style.strokeDashoffset = RING_CIRCUMFERENCE * (1 - r.percent / 100);
  $('ringScore').textContent = r.percent + '%';
  $('estScore').textContent = est;
  $('rawLine').textContent = `${r.correct} of ${r.total} correct`;
  $('timeLine').textContent =
    `Time used: ${fmtTime(App.session.usedSec)} of ${fmtTime(App.session.durationSec)}${auto ? ' (auto-submitted)' : ''}`;

  $('typeBars').innerHTML =
    typeBar('Text Completion', r.byType.tc) +
    typeBar('Sentence Equivalence', r.byType.se) +
    typeBar('Reading Comprehension', r.byType.rc);

  App.reviewRendered = false;
  $('reviewArea').innerHTML = '';
  $('reviewArea').classList.add('hidden');
  $('reviewToggleBtn').textContent = 'Review Answers';
}

function toggleReview() {
  const area = $('reviewArea');
  if (area.classList.contains('hidden') && !App.reviewRendered) {
    area.innerHTML = buildReviewHtml();
    App.reviewRendered = true;
  }
  area.classList.toggle('hidden');
  $('reviewToggleBtn').textContent = area.classList.contains('hidden')
    ? 'Review Answers' : 'Hide Review';
}

function answerText(q, idxs) {
  if (!idxs || !idxs.length) return '<em>Not answered</em>';
  if (q.kind === 'tc') {
    return idxs.map((oi, bi) =>
      oi === null || oi === undefined ? '<em>—</em>' : escapeHtml(q.option_sets[bi][oi])
    ).join(' / ');
  }
  return idxs.map(oi => escapeHtml(q.options[oi])).join('; ');
}

function buildReviewHtml() {
  return App.results.perQuestion.map((pq, i) => {
    const { q, user, answered, isCorrect } = pq;
    const verdictCls = !answered ? 'skipped' : (isCorrect ? 'ok' : 'no');
    const verdictTxt = !answered ? 'SKIPPED' : (isCorrect ? 'CORRECT' : 'INCORRECT');
    const itemCls = !answered ? '' : (isCorrect ? 'correct-q' : 'wrong-q');

    let stem;
    if (q.kind === 'tc') {
      stem = `<div class="review-passage">${escapeHtml(q.passage)}</div>`;
    } else if (q.kind === 'se') {
      stem = `<div class="review-passage">${escapeHtml(q.sentence.replace('|BLANK|', '________'))}</div>`;
    } else if (q.type === 'select_in_passage') {
      const sipReveal = q.passageRef.sentences.map((s, si) => {
        const u = Array.isArray(user) && user.includes(si);
        const c = q.answer.includes(si);
        let cls = '';
        if (c) cls += ' reveal-correct';
        else if (u) cls += ' reveal-wrong';
        return `<span class="sent${cls}">${escapeHtml(s)}</span>`;
      }).join(' ');
      stem = `<div class="review-passage">${sipReveal}</div>
        <p style="font-size:0.95rem;color:var(--text-color);margin-bottom:0.5rem;">${escapeHtml(q.prompt)}</p>`;
    } else {
      stem = `<div class="review-passage">${escapeHtml(q.passageRef.passage)}</div>
        <p style="font-size:0.95rem;color:var(--text-color);margin-bottom:0.5rem;">${escapeHtml(q.prompt)}</p>`;
    }

    let lines;
    if (q.kind === 'tc') {
      lines = `
        <div class="answer-line"><span class="lbl ${!answered ? 'yours-bad' : (isCorrect ? 'yours-ok' : 'yours-bad')}">Your answer:</span> ${answerText(q, user || [])}</div>
        <div class="answer-line"><span class="lbl correct-lbl">Correct answer:</span> ${answerText(q, q.answers)}</div>`;
    } else if (q.type === 'select_in_passage') {
      lines = `
        <div class="answer-line"><span class="lbl ${!answered ? 'yours-bad' : (isCorrect ? 'yours-ok' : 'yours-bad')}">Your selection:</span> ${answered ? 'shown in the passage above' : '<em>none</em>'}</div>
        <div class="answer-line"><span class="lbl correct-lbl">Correct sentence:</span> highlighted in green</div>`;
    } else {
      lines = `
        <div class="answer-line"><span class="lbl ${!answered ? 'yours-bad' : (isCorrect ? 'yours-ok' : 'yours-bad')}">Your answer:</span> ${answerText(q, user || [])}</div>
        <div class="answer-line"><span class="lbl correct-lbl">Correct answer${q.kind === 'se' ? 's (both required)' : ''}:</span> ${answerText(q, q.answers)}</div>`;
    }

    return `
      <div class="review-item ${itemCls}">
        <div class="review-head">
          <span class="verdict-badge ${verdictCls}">${verdictTxt}</span>
          <strong>#${i + 1}</strong>
          <span class="qtype-badge${q.kind === 'tc' ? '' : (q.kind === 'se' ? ' se' : ' rc')}">${TYPE_LABELS[q.kind]}</span>
        </div>
        ${stem}
        <div class="review-answer-lines">${lines}</div>
        <div class="review-explanation"><strong>Explanation:</strong> ${escapeHtml(q.explanation)}</div>
      </div>`;
  }).join('');
}

/* ===== History ===== */

function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; }
  catch (e) { return []; }
}

function saveHistory(h) {
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify(h)); } catch (e) {}
}

function addHistoryEntry(entry) {
  const h = loadHistory();
  h.unshift(entry);
  saveHistory(h.slice(0, 20));
}

function renderHistory() {
  const h = loadHistory();
  const body = $('historyBody');
  if (!h.length) {
    body.innerHTML = '<p class="vt-empty-note">No attempts yet — take your first full-length mock!</p>';
    return;
  }
  body.innerHTML = `
    <table>
      <thead><tr><th>Date</th><th>Est. Score</th><th>Raw</th><th>TC</th><th>SE</th><th>RC</th></tr></thead>
      <tbody>
        ${h.slice(0, 10).map(e => {
          const d = new Date(e.date);
          return `<tr>
            <td>${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
            <td><strong>${e.est}</strong></td>
            <td>${e.raw}/${e.total}</td>
            <td>${e.byType.tc[0]}/${e.byType.tc[1]}</td>
            <td>${e.byType.se[0]}/${e.byType.se[1]}</td>
            <td>${e.byType.rc[0]}/${e.byType.rc[1]}</td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>`;
}

function clearHistory() {
  saveHistory([]);
  renderHistory();
}

/* ===== Results actions & boot ===== */

function backToStartFromResults() {
  renderStart();
  showScreen('start');
}

document.addEventListener('DOMContentLoaded', () => {
  $('startBtn').addEventListener('click', startNewTest);
  $('resumeBtn').addEventListener('click', resumeTest);
  $('discardResumeBtn').addEventListener('click', discardSavedSession);
  $('submitBtn').addEventListener('click', openSubmitModal);
  $('confirmSubmitBtn').addEventListener('click', () => submitTest(false));
  $('cancelSubmitBtn').addEventListener('click', closeSubmitModal);
  $('prevBtn').addEventListener('click', prevQuestion);
  $('nextBtn').addEventListener('click', nextQuestion);
  $('markBtn').addEventListener('click', toggleMark);
  $('reviewToggleBtn').addEventListener('click', toggleReview);
  $('retakeBtn').addEventListener('click', startNewTest);
  $('backHomeBtn').addEventListener('click', backToStartFromResults);
  $('clearHistoryBtn').addEventListener('click', clearHistory);

  document.addEventListener('keydown', (e) => {
    if (App.screen !== 'test' || !$('testScreen') || $('testScreen').classList.contains('hidden')) return;
    if ($('submitModal').classList.contains('open')) return;
    if (e.key === 'ArrowRight') nextQuestion();
    if (e.key === 'ArrowLeft') prevQuestion();
  });

  window.addEventListener('beforeunload', () => saveSession());
  loadBank();
});

