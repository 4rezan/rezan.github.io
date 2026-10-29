(() => {
  const button = document.querySelector('.theme-toggle');
  const icon = document.querySelector('.theme-icon');
  const menuButton = document.querySelector('.header-toggle');
  const nav = document.querySelector('.nav');
  menuButton.addEventListener('click', () => {
    const expanded = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(expanded));
    menuButton.setAttribute('aria-label', expanded ? 'Close navigation menu' : 'Open navigation menu');
    menuButton.textContent = expanded ? '×' : '☰';
    nav.classList.toggle('open', expanded);
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    nav.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'Open navigation menu');
    menuButton.textContent = '☰';
  }));
  const saved = localStorage.getItem('rezan-site-theme');
  if (saved === 'dark') document.body.classList.add('dark');
  const sync = () => { icon.src = document.body.classList.contains('dark') ? 'icons/moon.svg' : 'icons/sun.svg'; };
  sync();
  button.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    localStorage.setItem('rezan-site-theme', document.body.classList.contains('dark') ? 'dark' : 'light');
    sync();
  });
})();
