// theme.js
(function () {
  const KEY = 'theme'; // 'light' | 'dark'
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

  function apply(theme){
    document.documentElement.setAttribute('data-theme', theme);
    const cb = document.getElementById('themeToggle');
    if (cb) cb.checked = (theme === 'dark'); // เปิด=มืด
  }

  function init(){
    const saved = localStorage.getItem(KEY);
    const theme = saved || (prefersDark.matches ? 'dark' : 'light');
    apply(theme);

    const cb = document.getElementById('themeToggle');
    if (cb){
      cb.addEventListener('change', ()=>{
        const next = cb.checked ? 'dark' : 'light';
        localStorage.setItem(KEY, next);
        apply(next);
      });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
