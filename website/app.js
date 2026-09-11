(() => {
  const DOWNLOAD_URL = 'https://github.com/yomismtz/-ngulos-cefalometricos/releases/latest/download/YomCeph_Desktop_Setup.exe';
  const isEnglish = document.documentElement.lang.toLowerCase().startsWith('en');

  const button = document.getElementById('language-toggle');
  if (button) {
    button.textContent = isEnglish ? 'ES' : 'EN';
    button.setAttribute('aria-label', isEnglish ? 'Cambiar a Español' : 'Switch to English');
    button.addEventListener('click', () => {
      const hash = window.location.hash || '';
      window.location.href = (isEnglish ? 'index.html' : 'en.html') + hash;
    });
  }

  // El enlace es estable: cada nueva Release sustituye el destino "latest" sin
  // tener que cambiar manualmente la web.
  const nav = document.querySelector('.main-nav');
  if (nav && !nav.querySelector('[data-yomceph-download]')) {
    const link = document.createElement('a');
    link.href = DOWNLOAD_URL;
    link.textContent = isEnglish ? 'Download' : 'Descargar';
    link.setAttribute('data-yomceph-download', '');
    link.setAttribute('aria-label', isEnglish ? 'Download YomCeph Desktop for Windows' : 'Descargar YomCeph Desktop para Windows');
    nav.appendChild(link);
  }

  const actions = document.querySelector('.hero-actions');
  if (actions && !actions.querySelector('[data-yomceph-download]')) {
    const link = document.createElement('a');
    link.className = 'button primary';
    link.href = DOWNLOAD_URL;
    link.textContent = isEnglish ? '⬇ Free download for Windows' : '⬇ Descarga gratuita para Windows';
    link.setAttribute('data-yomceph-download', '');
    actions.prepend(link);
  }
})();
