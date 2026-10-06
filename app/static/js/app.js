(() => {
  const prompt = document.querySelector('#story_prompt');
  const count = document.querySelector('[data-count]');
  const form = document.querySelector('[data-generation-form]');
  const updateCount = () => { if (prompt && count) count.textContent = `${prompt.value.length} / 800`; };
  if (prompt) { prompt.addEventListener('input', updateCount); updateCount(); }
  document.querySelectorAll('[data-example]').forEach((chip) => chip.addEventListener('click', () => {
    if (!prompt) return;
    prompt.value = chip.dataset.example || '';
    prompt.focus();
    updateCount();
  }));
  if (form) form.addEventListener('submit', () => {
    const button = form.querySelector('button[type="submit"]');
    if (!button) return;
    button.classList.add('is-loading');
    button.disabled = true;
    const label = button.querySelector('span:nth-child(2)');
    if (label) label.textContent = 'Inking your issue…';
  });
})();
