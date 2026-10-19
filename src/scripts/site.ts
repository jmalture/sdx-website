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
  window.addEventListener(
    'scroll',
    () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    },
    { passive: true },
  );
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

/**
 * FAQ sections: the decorative folders are placed with % of the section height, so opening an
 * answer or "show more" made them travel down. Pin each folder at the pixel position it has in
 * the collapsed state; re-measure on width changes while nothing is expanded. Also keeps them still when a category
 * chip shortens the list.
 */
function initFaqFolds() {
  document.querySelectorAll<HTMLElement>('.sdxq').forEach((sec) => {
    const folds = [...sec.querySelectorAll<HTMLElement>('.sdxt-fold, .sxf-fold')];
    if (!folds.length) return;
    const expanded = () => !!sec.querySelector('.sdxq-item.is-open, .sdxq-more.is-less');
    const orig = folds.map((f) => [f.style.top, f.style.bottom]);
    const pin = () => {
      folds.forEach((f, i) => {
        f.style.top = orig[i][0];
        f.style.bottom = orig[i][1];
      });
      const tops = folds.map((f) => f.offsetTop); // offsetTop ignores the bob/rotate transforms
      folds.forEach((f, i) => {
        f.style.setProperty('top', `${tops[i]}px`, 'important');
        f.style.setProperty('bottom', 'auto', 'important');
      });
    };
    pin();
    let w = window.innerWidth;
    window.addEventListener('resize', () => {
      if (window.innerWidth === w || expanded()) return;
      w = window.innerWidth;
      pin();
    });
  });
}

/**
 * Phones: card rows made swipeable in site.css get dots below them showing the current card.
 * Tapping a dot scrolls to that card.
 */
function initSwipe() {
  const rows = document.querySelectorAll<HTMLElement>(
    'main .sdxs-tiles, main #sdx-why-stack, main .sxf-bento, main .sxf-vgrid, main .sxf-ntf .pts, main .sxa-log .cards, main .sfx-grid',
  );
  rows.forEach((row) => {
    const cards = [...row.children] as HTMLElement[];
    if (cards.length < 2) return;
    const dots = document.createElement('div');
    dots.className = 'sx-dots';
    dots.setAttribute('aria-hidden', 'true');
    cards.forEach((card) => {
      const d = document.createElement('i');
      d.addEventListener('click', () => row.scrollTo({ left: card.offsetLeft - 18, behavior: 'smooth' }));
      dots.appendChild(d);
    });
    row.insertAdjacentElement('afterend', dots);
    const update = () => {
      const x = row.scrollLeft + 18;
      let cur = 0;
      cards.forEach((c, i) => {
        if (c.offsetLeft - 1 <= x) cur = i;
      });
      if (row.scrollLeft + row.clientWidth >= row.scrollWidth - 2) cur = cards.length - 1;
      [...dots.children].forEach((d, i) => d.classList.toggle('on', i === cur));
    };
    row.addEventListener('scroll', update, { passive: true });
    update();
  });
}

/**
 * Phones: burger button opens the side menu (slides in from the right over a dimmed page).
 * Closes on the X, the dimmed area, a link tap, Escape, or when the screen gets wider.
 */
function initMobileMenu() {
  const btn = document.querySelector<HTMLButtonElement>('.sx-burger');
  const side = document.getElementById('sx-mnav');
  if (!btn || !side) return;
  const set = (open: boolean) => {
    side.classList.toggle('is-open', open);
    side.toggleAttribute('inert', !open);
    document.documentElement.classList.toggle('sx-side-lock', open);
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', (open ? btn.dataset.labelClose : btn.dataset.labelOpen) || '');
    if (open) side.querySelector<HTMLElement>('.sx-side-x')?.focus({ preventScroll: true });
    else if (side.contains(document.activeElement)) btn.focus({ preventScroll: true });
  };
  // allow the slide/fade transitions only once the page (incl. late styles) is painted closed
  const ready = () => requestAnimationFrame(() => requestAnimationFrame(() => side.classList.add('is-ready')));
  if (document.readyState === 'complete') ready();
  else window.addEventListener('load', ready, { once: true });
  // page restored from the back/forward cache: show it closed, without animating
  window.addEventListener('pageshow', (e) => {
    if (!e.persisted) return;
    side.classList.remove('is-ready');
    set(false);
    ready();
  });
  btn.addEventListener('click', () => set(!side.classList.contains('is-open')));
  side.addEventListener('click', (e) => {
    const el = e.target as HTMLElement;
    const a = el.closest('a');
    if (a && !e.metaKey && !e.ctrlKey && !e.shiftKey && a.origin === location.origin) {
      const sameDoc = a.pathname === location.pathname;
      set(false);
      if (!sameDoc) {
        // let the panel slide out before the next page starts loading
        e.preventDefault();
        setTimeout(() => (location.href = a.href), 260);
      }
      return;
    }
    if (el.closest('[data-close]')) set(false);
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && side.classList.contains('is-open')) set(false);
  });
  window.matchMedia('(min-width: 768px)').addEventListener('change', (m) => m.matches && set(false));
}

initAnimations();
initStickyHeader();
initMobileMenu();
initFaqFolds();
initSwipe();
initLangSwitch();
initContactForm();
