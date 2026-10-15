/**
 * Small replacements for the parts of Elementor's frontend JS the design relies on.
 * Everything else lives next to its section (inline scripts copied from the HTML widgets).
 */

// 1. Entrance animations (Elementor "Motion Effects > Entrance Animation").
//    Elements start with .elementor-invisible; when they enter the viewport they get
//    `animated <name>` after their delay, exactly like Elementor's waypoint handler.
function initAnimations() {
  const els = document.querySelectorAll<HTMLElement>('[data-anim]');
  if (!els.length) return;
  const show = (el: HTMLElement) => {
    const delay = Number(el.dataset.animDelay || 0);
    window.setTimeout(() => {
      el.classList.remove('elementor-invisible');
      el.classList.add('animated', el.dataset.anim!);
    }, delay);
  };
  if (!('IntersectionObserver' in window)) return els.forEach(show);
  const io = new IntersectionObserver(
    (entries) =>
      entries.forEach((e) => {
        if (e.isIntersecting) {
          io.unobserve(e.target);
          show(e.target as HTMLElement);
        }
      }),
    { rootMargin: '0px 0px -15% 0px' },
  );
  els.forEach((el) => io.observe(el));
}

// 2. Sticky header effects (Elementor Pro sticky: effects offset 388px desktop, 8px mobile).
function initStickyHeader() {
  const bar = document.querySelector<HTMLElement>('.sx-header > .e-con');
  if (!bar) return;
  bar.classList.add('elementor-sticky', 'elementor-sticky--active');
  const mq = window.matchMedia('(max-width: 767px)');
  let ticking = false;
  const update = () => {
    ticking = false;
    const offset = mq.matches ? 8 : 388;
    bar.classList.toggle('elementor-sticky--effects', window.scrollY > offset);
  };
  window.addEventListener('scroll', () => {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }, { passive: true });
  update();
}

// 3. Language switcher: the <select> jumps to the same page in the chosen language.
function initLangSwitch() {
  document.querySelectorAll<HTMLSelectElement>('[data-lang-switch]').forEach((s) =>
    s.addEventListener('change', () => {
      if (s.value) window.location.href = s.value;
    }),
  );
}

// 4. Contact form: posts to /api/contact and shows Elementor-style messages.
function initContactForm() {
  document.querySelectorAll<HTMLFormElement>('form[data-contact]').forEach((form) => {
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      form.querySelectorAll('.elementor-message').forEach((m) => m.remove());
      form.classList.add('elementor-form-waiting');
      const btn = form.querySelector<HTMLButtonElement>('button[type=submit]');
      if (btn) btn.disabled = true;
      let ok = false;
      let msg = '';
      try {
        const res = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: { Accept: 'application/json' },
        });
        const data = await res.json().catch(() => ({}));
        ok = res.ok && data.ok;
        msg = data.message || '';
      } catch {
        ok = false;
      }
      form.classList.remove('elementor-form-waiting');
      if (btn) btn.disabled = false;
      const box = document.createElement('div');
      box.className = `elementor-message ${ok ? 'elementor-message-success' : 'elementor-message-danger'}`;
      box.setAttribute('role', ok ? 'status' : 'alert');
      box.textContent = msg || (ok ? form.dataset.ok || '' : form.dataset.error || '');
      form.appendChild(box);
      if (ok) form.reset();
    });
  });
}

initAnimations();
initStickyHeader();
initLangSwitch();
initContactForm();
