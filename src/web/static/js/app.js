const state = {
  config: null,
  exercise: null,
  exerciseSignature: null,
  feedback: null,
  awaitingAnswer: false,
  loading: false,
  selection: [],
  timerFrame: null,
  timerDeadline: null,
};

const selectors = {
  form: document.getElementById('settings-form'),
  minRange: document.getElementById('min-difficulty'),
  maxRange: document.getElementById('max-difficulty'),
  minValue: document.querySelector('[data-min-difficulty]'),
  maxValue: document.querySelector('[data-max-difficulty]'),
  tenseSelect: document.getElementById('tense'),
  modeSelect: document.getElementById('game-mode'),
  modelSelect: document.getElementById('model'),
  providerContainer: document.querySelector('[data-provider-options]'),
  modeBadge: document.querySelector('[data-mode-badge]'),
  statusText: document.querySelector('[data-status-text]'),
  gameContent: document.querySelector('[data-game-content]'),
  feedback: document.querySelector('[data-feedback]'),
  systemMessage: document.querySelector('[data-system-message]'),
  loading: document.querySelector('[data-loading]'),
  nextBtn: document.querySelector('[data-action="next"]'),
  hintBtn: document.querySelector('[data-action="hint"]'),
  resetBtn: document.querySelector('[data-action="reset"]'),
};

document.addEventListener('DOMContentLoaded', () => {
  bindFormEvents();
  bootstrap();
});

function setExercise(exercise) {
  const signature = buildExerciseSignature(exercise);
  const changed = signature !== state.exerciseSignature;
  state.exercise = exercise;
  state.exerciseSignature = signature;

  if (!exercise) {
    state.selection = [];
    return;
  }

  if (changed) {
    state.selection = [];
  }
}

function buildExerciseSignature(exercise) {
  if (!exercise) return null;
  switch (exercise.type) {
    case 'word-selection':
      return `${exercise.type}:${exercise.englishSentence}`;
    case 'translation':
      return `${exercise.type}:${exercise.direction}:${exercise.sentence}`;
    case 'article-selection':
      return `${exercise.type}:${exercise.noun}:${exercise.case}`;
    case 'fill-blank':
    case 'error-detection':
      return `${exercise.type}:${exercise.sentence}`;
    case 'verb-conjugation':
      return `${exercise.type}:${exercise.infinitive}:${exercise.pronoun}:${exercise.tense}`;
    case 'speed-translation':
      return `${exercise.type}:${exercise.sentence}:${exercise.timeLimit}`;
    case 'conversation':
      return `${exercise.type}:${exercise.scenario}:${exercise.progress?.current}`;
    default:
      return `${exercise.type}`;
  }
}

async function bootstrap() {
  try {
    await loadConfig();
    await hydrateStatus();
  } catch (error) {
    setSystemMessage(error.message || 'Unable to load configuration', 'error');
  }
}

function bindFormEvents() {
  selectors.form?.addEventListener('submit', handleStart);
  selectors.resetBtn?.addEventListener('click', handleReset);
  selectors.nextBtn?.addEventListener('click', handleNext);
  selectors.hintBtn?.addEventListener('click', handleHint);

  selectors.minRange?.addEventListener('input', () => {
    selectors.minValue.textContent = selectors.minRange.value;
  });
  selectors.maxRange?.addEventListener('input', () => {
    selectors.maxValue.textContent = selectors.maxRange.value;
  });
}

async function loadConfig() {
  const response = await apiGet('/api/config');
  if (!response.success) throw new Error('Could not load configuration');

  state.config = response.config;
  populateGameOptions(response.config.games);
  populateTenses(response.config.tenses);
  populateProviders(response.config.providers);
  updateModelOptions();
}

function populateGameOptions(options = []) {
  if (!selectors.modeSelect) return;
  selectors.modeSelect.innerHTML = '';

  const grouped = options.reduce((acc, item) => {
    acc[item.category] = acc[item.category] || [];
    acc[item.category].push(item);
    return acc;
  }, {});

  Object.keys(grouped).forEach((category) => {
    const group = document.createElement('optgroup');
    group.label = category;
    grouped[category].forEach((item) => {
      const option = document.createElement('option');
      option.value = item.value;
      option.textContent = item.label;
      group.appendChild(option);
    });
    selectors.modeSelect.appendChild(group);
  });
}

function populateTenses(tenses = []) {
  if (!selectors.tenseSelect) return;
  selectors.tenseSelect.innerHTML = '';
  tenses.forEach((tense) => {
    const option = document.createElement('option');
    option.value = tense;
    option.textContent = tense;
    selectors.tenseSelect.appendChild(option);
  });
}

function populateProviders(providers = []) {
  if (!selectors.providerContainer) return;
  selectors.providerContainer.innerHTML = '';

  providers.forEach((provider, index) => {
    const id = `provider-${provider.value}`;
    const label = document.createElement('label');
    label.className = 'provider-chip';
    label.htmlFor = id;
    label.innerHTML = `
      <input type="radio" name="provider" id="${id}" value="${provider.value}" ${index === 0 ? 'checked' : ''}/>
      <span>${provider.label}</span>
    `;
    selectors.providerContainer.appendChild(label);
  });

  selectors.providerContainer.addEventListener('change', (event) => {
    if (event.target.name === 'provider') {
      updateProviderStyles(event.target.value);
      updateModelOptions(event.target.value);
    }
  });

  updateProviderStyles(document.querySelector('input[name="provider"]:checked')?.value);
}

function updateProviderStyles(activeValue) {
  document.querySelectorAll('.provider-chip').forEach((chip) => {
    chip.classList.toggle('active', chip.querySelector('input')?.value === activeValue);
  });
}

function updateModelOptions(providerValue) {
  if (!state.config || !selectors.modelSelect) return;
  const selectedProvider = providerValue || document.querySelector('input[name="provider"]:checked')?.value;
  const providerConfig = state.config.providers.find((p) => p.value === selectedProvider) || state.config.providers[0];

  selectors.modelSelect.innerHTML = '';
  providerConfig.models.forEach((model) => {
    const option = document.createElement('option');
    option.value = model;
    option.textContent = model;
    selectors.modelSelect.appendChild(option);
  });
}

async function hydrateStatus() {
  const response = await apiGet('/api/status');
  if (!response.success) return;
  if (response.exercise) {
    setExercise(response.exercise);
    state.awaitingAnswer = true;
  }
  render();
}

async function handleStart(event) {
  event.preventDefault();
  if (state.loading) return;

  const payload = collectFormPayload();
  if (!payload.gameMode) {
    setSystemMessage('Please choose a game mode before starting.', 'error');
    return;
  }

  state.selection = [];
  await withLoading(async () => {
    const data = await apiPost('/api/start', payload);
    if (!data.success) throw new Error(data.error || 'Unable to start game.');
    setExercise(data.exercise || null);
    state.feedback = null;
    state.awaitingAnswer = !!data.exercise;
    setSystemMessage('');
    render();
  });
}

function collectFormPayload() {
  const formData = new FormData(selectors.form);
  return {
    gameMode: formData.get('gameMode'),
    minDifficulty: Number(formData.get('minDifficulty')) || 1,
    maxDifficulty: Number(formData.get('maxDifficulty')) || 3,
    tense: formData.get('tense'),
    provider: formData.get('provider'),
    model: formData.get('model'),
  };
}

async function handleNext() {
  if (state.loading) return;
  await withLoading(async () => {
    const data = await apiPost('/api/next');
    if (!data.success) throw new Error(data.error || 'Unable to fetch next exercise.');
    setExercise(data.exercise || null);
    state.feedback = null;
    state.awaitingAnswer = !!data.exercise;
    setSystemMessage('');
    render();
  });
}

async function handleHint() {
  if (state.loading) return;
  await withLoading(async () => {
    const data = await apiPost('/api/hint');
    if (!data.success) throw new Error(data.error || 'Hints are unavailable right now.');
    setSystemMessage(data.hint || 'Hint requested.', 'hint');
  });
}

async function handleReset() {
  if (state.loading) return;
  await withLoading(async () => {
    await apiPost('/api/reset');
    setExercise(null);
    state.feedback = null;
    state.awaitingAnswer = false;
    stopTimer();
    setSystemMessage('Session reset. Configure a new game to continue.', 'hint');
    render();
  });
}

async function submitAnswer(payload) {
  if (state.loading) return;
  await withLoading(async () => {
    const data = await apiPost('/api/answer', payload);
    if (!data.success) throw new Error(data.error || 'Could not validate answer.');
    state.feedback = data.feedback || null;
    state.awaitingAnswer = false;

    if (data.conversation) {
      setExercise(data.conversation);
      state.awaitingAnswer = data.conversation.awaitingUser;
    }

    setSystemMessage('');
    render();
  });
}

function bindExerciseHandlers(exercise) {
  const container = selectors.gameContent;
  if (!container) return;

  if (['translation', 'fill-blank', 'error-detection', 'verb-conjugation', 'speed-translation'].includes(exercise.type)) {
    const form = container.querySelector('form[data-action="submit-answer"]');
    form?.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(event.target);
      const answer = (formData.get('answer') || '').toString().trim();
      if (!answer) {
        setSystemMessage('Type your answer before submitting.', 'error');
        return;
      }
      submitAnswer({ answer });
      event.target.reset();
    });
  }

  if (exercise.type === 'word-selection') {
    container.querySelector('[data-word-bank]')?.addEventListener('click', (event) => {
      const btn = event.target.closest('button[data-word]');
      if (!btn || btn.disabled) return;
      const word = btn.dataset.word;
      if (!word) return;
      if (!state.selection.includes(word)) {
        state.selection.push(word);
        render();
      }
    });

    container.querySelector('[data-action="undo"]')?.addEventListener('click', () => {
      state.selection.pop();
      render();
    });

    container.querySelector('[data-action="clear"]')?.addEventListener('click', () => {
      state.selection = [];
      render();
    });

    container.querySelector('form[data-action="submit-selection"]')?.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!state.selection.length) {
        setSystemMessage('Select at least one word before checking.', 'error');
        return;
      }
      submitAnswer({ selectedWords: state.selection });
    });
  }

  if (exercise.type === 'article-selection') {
    container.querySelector('[data-article-grid]')?.addEventListener('click', (event) => {
      const btn = event.target.closest('button[data-article]');
      if (!btn) return;
      submitAnswer({ selectedArticle: btn.dataset.article });
    });
  }

  if (exercise.type === 'conversation') {
    container.querySelector('[data-option-grid]')?.addEventListener('click', (event) => {
      const card = event.target.closest('[data-option-index]');
      if (!card || card.dataset.disabled === 'true') return;
      submitAnswer({ optionIndex: Number(card.dataset.optionIndex) });
    });
  }
}

function render() {
  renderExercise();
  renderFeedback();
  updateControls();
}

function renderExercise() {
  const container = selectors.gameContent;
  if (!container) return;

  const exercise = state.exercise;
  if (!exercise) {
    container.innerHTML = `
      <div class="placeholder">
        <h3>No active game</h3>
        <p>Start a new session from the left panel to receive exercises.</p>
      </div>
    `;
    stopTimer();
    return;
  }

  let html = '';
  switch (exercise.type) {
    case 'translation':
      html = renderTranslation(exercise);
      break;
    case 'word-selection':
      if (!state.selection.length) state.selection = [];
      html = renderWordSelection(exercise);
      break;
    case 'article-selection':
      html = renderArticleSelection(exercise);
      break;
    case 'fill-blank':
      html = renderFillBlank(exercise);
      break;
    case 'error-detection':
      html = renderErrorDetection(exercise);
      break;
    case 'verb-conjugation':
      html = renderVerbConjugation(exercise);
      break;
    case 'speed-translation':
      html = renderSpeedTranslation(exercise);
      break;
    case 'conversation':
      html = renderConversation(exercise);
      break;
    default:
      html = `<p>Unsupported exercise type: ${exercise.type}</p>`;
  }

  container.innerHTML = html;
  bindExerciseHandlers(exercise);

  if (exercise.type === 'speed-translation') {
    startTimer(exercise.timeLimit);
  } else {
    stopTimer();
  }
}

function renderTranslation(exercise) {
  const directionLabel = exercise.direction === 'de-en' ? 'German → English' : 'English → German';
  const placeholder = exercise.direction === 'de-en' ? 'Type the English translation...' : 'Schreibe die deutsche Übersetzung...';
  return `
    <div class="exercise-header">
      <p class="eyebrow">${directionLabel}</p>
      <h3>${escapeHtml(exercise.sentence || '')}</h3>
    </div>
    <div class="exercise-meta">
      ${exercise.tense ? `<span>Tense: ${escapeHtml(exercise.tense)}</span>` : ''}
      ${exercise.verb ? `<span>Verb: ${escapeHtml(exercise.verb)}</span>` : ''}
    </div>
    <form class="response-form" data-action="submit-answer">
      <label>Your answer</label>
      <textarea name="answer" placeholder="${placeholder}"></textarea>
      <button class="btn primary" type="submit">Check answer</button>
    </form>
  `;
}

function renderWordSelection(exercise) {
  const selected = state.selection;
  return `
    <div class="word-selection">
      <div class="exercise-header">
        <p class="eyebrow">Build the German sentence</p>
        <h3>${escapeHtml(exercise.englishSentence || '')}</h3>
      </div>
      <div>
        <p class="label">Your translation</p>
        <div class="selected-words">
          ${selected.length ? selected.map((word) => `<span class="word-chip">${escapeHtml(word)}</span>`).join('') : '<span class="label">Tap words below to build your answer.</span>'}
        </div>
        <div class="game-actions" style="margin-top:0.75rem;">
          <button type="button" class="btn subtle" data-action="undo" ${selected.length ? '' : 'disabled'}>Undo</button>
          <button type="button" class="btn ghost" data-action="clear" ${selected.length ? '' : 'disabled'}>Clear</button>
        </div>
      </div>
      <div>
        <p class="label">Available words</p>
        <div class="article-grid" data-word-bank>
          ${exercise.words
            .map((word) => {
              const disabled = selected.includes(word) ? 'disabled' : '';
              return `<button type="button" class="word-chip ${disabled ? 'disabled' : ''}" data-word="${escapeHtml(word)}" ${disabled}>${escapeHtml(word)}</button>`;
            })
            .join('')}
        </div>
      </div>
      <form data-action="submit-selection">
        <button class="btn primary" type="submit" ${selected.length ? '' : 'disabled'}>Check answer</button>
      </form>
    </div>
  `;
}

function renderArticleSelection(exercise) {
  return `
    <div class="exercise-header">
      <p class="eyebrow">Article selection</p>
      <h3>${escapeHtml(exercise.noun || '')}</h3>
    </div>
    <div class="exercise-meta">
      ${exercise.case ? `<span>Case: ${escapeHtml(exercise.case)}</span>` : ''}
      ${exercise.meaning ? `<span>Meaning: ${escapeHtml(exercise.meaning)}</span>` : ''}
    </div>
    <div class="article-grid" data-article-grid>
      ${exercise.articles
        .map((article) => `<button type="button" data-article="${escapeHtml(article)}">${escapeHtml(article)}</button>`)
        .join('')}
    </div>
    <div class="label" style="margin-top:1rem;">
      ${exercise.exampleSentence ? `Example: ${escapeHtml(exercise.exampleSentence)}` : ''}
    </div>
  `;
}

function renderFillBlank(exercise) {
  return `
    <div class="exercise-header">
      <p class="eyebrow">Fill in the blank</p>
      <h3>${escapeHtml(exercise.sentence || '')}</h3>
    </div>
    <form class="response-form" data-action="submit-answer">
      <label>Missing word</label>
      <input type="text" name="answer" placeholder="Type the missing word..." />
      ${exercise.hint ? `<p class="label">Hint: ${escapeHtml(exercise.hint)}</p>` : ''}
      <button class="btn primary" type="submit">Check answer</button>
    </form>
  `;
}

function renderErrorDetection(exercise) {
  return `
    <div class="exercise-header">
      <p class="eyebrow">Find the error</p>
      <h3>${escapeHtml(exercise.sentence || '')}</h3>
    </div>
    <form class="response-form" data-action="submit-answer">
      <label>Corrected sentence</label>
      <textarea name="answer" placeholder="Rewrite the sentence without the error."></textarea>
      <button class="btn primary" type="submit">Check answer</button>
    </form>
  `;
}

function renderVerbConjugation(exercise) {
  return `
    <div class="exercise-header">
      <p class="eyebrow">Verb conjugation</p>
      <div class="exercise-meta">
        <span>Infinitive: <strong>${escapeHtml(exercise.infinitive || '')}</strong></span>
        <span>Pronoun: <strong>${escapeHtml(exercise.pronoun || '')}</strong></span>
        <span>Tense: <strong>${escapeHtml(exercise.tense || '')}</strong></span>
      </div>
    </div>
    <form class="response-form" data-action="submit-answer">
      <label>Conjugated form</label>
      <input type="text" name="answer" placeholder="Type the correct conjugation..." />
      <button class="btn primary" type="submit">Check answer</button>
    </form>
  `;
}

function renderSpeedTranslation(exercise) {
  return `
    <div class="exercise-header">
      <p class="eyebrow">Speed translation</p>
      <h3>${escapeHtml(exercise.sentence || '')}</h3>
    </div>
    <div class="exercise-meta">
      ${exercise.category ? `<span>Category: ${escapeHtml(exercise.category)}</span>` : ''}
      <span class="timer-chip">⏱ <span data-timer>${exercise.timeLimit ?? 0}s</span></span>
    </div>
    <form class="response-form" data-action="submit-answer">
      <label>English translation</label>
      <input type="text" name="answer" placeholder="Type as fast as you can..." />
      <button class="btn primary" type="submit">Submit</button>
    </form>
  `;
}

function renderConversation(exercise) {
  const history = (exercise.history || [])
    .map((entry) => {
      const role = entry.speaker === 'ai' ? 'ai' : 'user';
      const title = role === 'ai' ? 'AI' : 'You';
      return `
        <div class="conversation-bubble ${role}">
          <strong>${title}</strong>
          <p>${escapeHtml(entry.text)}</p>
          ${entry.translation ? `<p class="label">${escapeHtml(entry.translation)}</p>` : ''}
        </div>
      `;
    })
    .join('');

  const options = exercise.prompt?.options || [];

  return `
    <div class="exercise-header">
      <p class="eyebrow">${escapeHtml(exercise.scenario || 'Conversation')}</p>
      <h3>${escapeHtml(exercise.scenarioDescription || '')}</h3>
    </div>
    <div class="conversation-history">
      ${history || '<p class="label">Conversation will appear here.</p>'}
    </div>
    ${
      exercise.awaitingUser
        ? `
      <div>
        <p class="label">Choose your response:</p>
        <div class="options-grid" data-option-grid>
          ${options
            .map(
              (option, index) => `
            <div class="option-card" data-option-index="${index}">
              <strong>${String.fromCharCode(65 + index)}.</strong> ${escapeHtml(option)}
            </div>`
            )
            .join('')}
        </div>
      </div>
    `
        : `<p class="label">AI is responding... keep an eye on the history.</p>`
    }
  `;
}

function renderFeedback() {
  const card = selectors.feedback;
  if (!card) return;

  if (!state.feedback) {
    card.hidden = true;
    card.classList.remove('success', 'error');
    card.innerHTML = '';
    return;
  }

  const isCorrect = !!state.feedback.is_correct;
  card.hidden = false;
  card.classList.toggle('success', isCorrect);
  card.classList.toggle('error', !isCorrect);
  card.innerHTML = formatMultiline(state.feedback.message || state.feedback.feedback || '');
}

function updateControls() {
  const mode = selectors.modeSelect?.value;
  if (selectors.modeBadge) {
    selectors.modeBadge.textContent = mode || 'Choose a game';
  }

  if (selectors.statusText) {
    if (!state.exercise) {
      selectors.statusText.textContent = 'Idle – configure a session to begin.';
    } else if (state.awaitingAnswer) {
      selectors.statusText.textContent = 'Waiting for your answer.';
    } else {
      selectors.statusText.textContent = 'Review feedback or move to the next exercise.';
    }
  }

  const disabled = !state.exercise;
  if (selectors.nextBtn) selectors.nextBtn.disabled = disabled;
  if (selectors.hintBtn) selectors.hintBtn.disabled = disabled;
}

function startTimer(timeLimit) {
  if (!timeLimit) return;
  stopTimer();
  state.timerDeadline = Date.now() + timeLimit * 1000;

  const tick = () => {
    const timerEl = document.querySelector('[data-timer]');
    if (!timerEl) {
      stopTimer();
      return;
    }
    const remaining = Math.max(0, state.timerDeadline - Date.now());
    timerEl.textContent = `${(remaining / 1000).toFixed(1)}s`;
    if (remaining <= 0) {
      stopTimer();
    } else {
      state.timerFrame = requestAnimationFrame(tick);
    }
  };

  state.timerFrame = requestAnimationFrame(tick);
}

function stopTimer() {
  if (state.timerFrame) {
    cancelAnimationFrame(state.timerFrame);
    state.timerFrame = null;
  }
}

function setSystemMessage(message, variant = 'info') {
  const el = selectors.systemMessage;
  if (!el) return;

  if (!message) {
    el.hidden = true;
    el.textContent = '';
    return;
  }

  el.hidden = false;
  el.textContent = message;
  el.classList.toggle('hint', variant === 'hint');
}

function formatMultiline(text) {
  if (!text) return '';
  return text
    .split('\n')
    .filter(Boolean)
    .map((line) => `<p>${escapeHtml(line)}</p>`)
    .join('');
}

async function withLoading(fn) {
  try {
    setLoading(true);
    await fn();
  } catch (error) {
    setSystemMessage(error.message || 'Something went wrong.', 'error');
  } finally {
    setLoading(false);
  }
}

function setLoading(flag) {
  state.loading = flag;
  if (selectors.loading) {
    selectors.loading.hidden = !flag;
  }
}

async function apiGet(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.json();
}

async function apiPost(url, data) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: data ? JSON.stringify(data) : null,
  });
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.json();
}

function escapeHtml(value) {
  if (value === undefined || value === null) return '';
  return value
    .toString()
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
