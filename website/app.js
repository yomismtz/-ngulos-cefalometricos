(() => {
  const button = document.getElementById('language-toggle');
  if (!button) return;
  const isEnglish = document.documentElement.lang.toLowerCase().startsWith('en');
  button.textContent = isEnglish ? 'ES' : 'EN';
  button.setAttribute('aria-label', isEnglish ? 'Cambiar a Español' : 'Switch to English');
  button.addEventListener('click', () => {
    const hash = window.location.hash || '';
    window.location.href = (isEnglish ? 'index.html' : 'en.html') + hash;
  });
})();
