// theme.js
(function () {
  const KEY = 'theme'; // 'light' | 'dark'
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

  function apply(theme){
    document.documentElement.setAttribute('data-theme', theme);
    const cb = document.getElementById('themeToggle');
    if (cb) cb.checked = (theme === 'dark'); // เปิด=มืด
  }

  function initNavToggle(){
    const toggle = document.getElementById('navToggle');
    const panel = document.querySelector('.header-actions.site-nav');
    if (!toggle || !panel) return;
    toggle.addEventListener('click', () => {
      const open = panel.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    // ปิดเมนูอัตโนมัติเมื่อกดลิงก์ หรือขยายจอใหญ่ขึ้นจนเมนูกลับมาเป็นแถวปกติ
    panel.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => { panel.classList.remove('open'); toggle.setAttribute('aria-expanded','false'); });
    });
    window.matchMedia('(min-width: 761px)').addEventListener('change', (e) => {
      if (e.matches){ panel.classList.remove('open'); toggle.setAttribute('aria-expanded','false'); }
    });
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

    initNavToggle();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
