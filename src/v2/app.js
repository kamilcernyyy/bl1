/* Blatec · směr B — motion & interactions (GSAP 3.13 + ScrollTrigger + SplitText, Lenis) */
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const root = document.documentElement;
  const motion = root.classList.contains('motion') && window.gsap;
  const D = window.BLATEC || { houses: [] };
  const IO = 'power4.inOut', OUT = 'expo.out';
  if (window.gsap) gsap.registerPlugin(ScrollTrigger, SplitText);

  /* ---------- smooth scroll (wheel only; touch stays native) ---------- */
  let lenis = null;
  if (motion && window.Lenis) {
    lenis = new Lenis({ lerp: 0.1, wheelMultiplier: 1, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(t => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }
  const scrollToEl = (el, off = 0) => { if (!el) return; lenis ? lenis.scrollTo(el, { offset: off, duration: 1.4 }) : el.scrollIntoView({ behavior: motion ? 'smooth' : 'auto' }); };
  const lock = on => { lenis && (on ? lenis.stop() : lenis.start()); root.style.overflow = on ? 'hidden' : ''; };

  /* ---------- page transitions ---------- */
  const pt = $('.pt');
  const internal = a => a && a.href && a.origin === location.origin && !a.target && !a.hasAttribute('download') && !/^(tel|mailto):/.test(a.getAttribute('href')) && !(a.pathname === location.pathname && a.hash);
  if (motion && pt) {
    if (root.classList.contains('pt-in')) {
      gsap.set(pt, { yPercent: 0 });
      root.classList.remove('pt-in');
      gsap.to(pt, { yPercent: -100, duration: 1, ease: IO, delay: .05 });
    } else gsap.set(pt, { yPercent: 100 });
    document.addEventListener('click', e => {
      const a = e.target.closest('a');
      if (!internal(a) || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
      e.preventDefault();
      try { sessionStorage.setItem('pt', '1'); } catch (_) {}
      gsap.fromTo(pt, { yPercent: 100 }, { yPercent: 0, duration: .8, ease: IO, onComplete: () => { location.href = a.href; } });
    });
    addEventListener('pageshow', e => { if (e.persisted) gsap.set(pt, { yPercent: 100 }); });
  }

  /* ---------- in-page anchors (first tap works, Lenis aware) ---------- */
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href*="#"]');
    if (!a || a.origin !== location.origin || a.pathname !== location.pathname) return;
    const t = a.hash && document.getElementById(a.hash.slice(1));
    if (!t) return;
    e.preventDefault(); closeMenu(); scrollToEl(t);
    history.replaceState(null, '', a.hash);
  });

  /* ---------- header: colour by section underneath, hide on scroll down ---------- */
  const hdr = $('#hdr');
  let lastY = scrollY, ticking = false;
  const cue = $('.cue');
  const paintHdr = () => {
    ticking = false;
    const y = scrollY;
    cue && cue.classList.toggle('is-off', y > innerHeight * .4);
    const under = document.elementsFromPoint(innerWidth / 2, 34).map(el => el.closest('[data-hdr]')).find(Boolean);
    hdr.classList.toggle('is-ink', !!under && under.dataset.hdr === 'ink');
    hdr.classList.toggle('is-hidden', y > 260 && y > lastY + 2 && !root.classList.contains('menu-on'));
    if (y < lastY - 2 || y < 260) hdr.classList.remove('is-hidden');
    lastY = y;
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(paintHdr); } }, { passive: true });
  paintHdr();

  /* ---------- menu ---------- */
  const menu = $('#menu');
  function openMenu() { menu.classList.add('is-open'); menu.setAttribute('aria-hidden', 'false'); root.classList.add('menu-on'); $$('[data-menu]').forEach(b => b.setAttribute('aria-expanded', 'true')); lock(true);
    if (motion) gsap.fromTo($$('.menu__nav a, .menu__claims p, .menu__foot', menu), { yPercent: 60, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 1, ease: OUT, stagger: .05, delay: .35 });
    setTimeout(() => $('.menu__close', menu).focus(), 50); }
  function closeMenu() { if (!menu.classList.contains('is-open')) return; menu.classList.remove('is-open'); menu.setAttribute('aria-hidden', 'true'); root.classList.remove('menu-on'); $$('[data-menu]').forEach(b => b.setAttribute('aria-expanded', 'false')); lock(false); }
  $$('[data-menu]').forEach(b => b.addEventListener('click', openMenu));
  $('[data-menu-close]').addEventListener('click', closeMenu);

  /* ---------- booking modal ---------- */
  const modal = $('#book'), form = $('.bookf', modal), thanks = $('.thanks', modal);
  let lastFocus = null;
  const openBook = house => { closeMenu(); lastFocus = document.activeElement; modal.classList.add('is-open'); modal.setAttribute('aria-hidden', 'false'); lock(true);
    form.hidden = false; thanks.hidden = true; if (house) form.house.value = house; setTimeout(() => form.name.focus(), 60); };
  const closeBook = () => { if (!modal.classList.contains('is-open')) return; modal.classList.remove('is-open'); modal.setAttribute('aria-hidden', 'true'); lock(false); lastFocus && lastFocus.focus(); };
  document.addEventListener('click', e => { const b = e.target.closest('[data-book]'); if (b) { e.preventDefault(); openBook(b.dataset.house); } });
  $$('[data-close]', modal).forEach(b => b.addEventListener('click', closeBook));
  $$('.bookf').forEach(f0 => f0.addEventListener('submit', e => {
    e.preventDefault();
    const fm = e.currentTarget; let ok = true;
    [['name', v => v.trim().length > 1, 'Vyplňte jméno'], ['tel', v => v.replace(/\D/g, '').length >= 9, 'Zadejte telefon']].forEach(([n, test, msg]) => {
      const f = fm[n].closest('.field'); const good = test(fm[n].value);
      f.classList.toggle('is-err', !good); let sm = $('small', f);
      if (!good) { if (!sm) { sm = document.createElement('small'); f.appendChild(sm); } sm.textContent = msg; ok = false; } else sm && sm.remove();
    });
    if (!ok) { $('.is-err input', fm).focus(); return; }
    fm.hidden = true; fm.parentElement.querySelector('.thanks').hidden = false;
  }));
  // contact page: #dum-4 preselects the house
  const cf = $('.ct .bookf'); const hm = location.hash.match(/^#dum-(\d+)$/); if (cf && hm) cf.house.value = hm[1];

  /* ---------- lightbox: every zoomable photo ---------- */
  const lbx = $('#lbx'), lImg = $('img', lbx); let lGroup = [], lIdx = 0, lFrom = null;
  const lShow = i => { lIdx = (i + lGroup.length) % lGroup.length; const b = lGroup[lIdx];
    lImg.src = b.dataset.src; lImg.alt = b.dataset.cap || ''; $('.lbx__cap', lbx).textContent = b.dataset.cap || '';
    $('.lbx__n', lbx).textContent = String(lIdx + 1).padStart(2, '0') + ' / ' + String(lGroup.length).padStart(2, '0');
    $$('.lbx__nav', lbx).forEach(n => n.hidden = lGroup.length < 2);
    if (motion) gsap.fromTo(lImg, { opacity: 0, scale: .96 }, { opacity: 1, scale: 1, duration: .7, ease: OUT }); };
  const lOpen = b => { lFrom = b; lGroup = $$(`[data-zoom="${b.dataset.zoom}"]`).filter(x => x.offsetParent !== null || x.closest('.hs')); lShow(lGroup.indexOf(b)); lbx.classList.add('is-open'); lbx.setAttribute('aria-hidden', 'false'); lock(true); setTimeout(() => $('.lbx__x', lbx).focus(), 50); };
  const lClose = () => { if (!lbx.classList.contains('is-open')) return; lbx.classList.remove('is-open'); lbx.setAttribute('aria-hidden', 'true'); lock(false); lFrom && lFrom.focus(); };
  document.addEventListener('click', e => { const b = e.target.closest('[data-zoom]'); if (b) { e.preventDefault(); lOpen(b); } });
  $('[data-lbx-close]', lbx).addEventListener('click', lClose);
  $('[data-lbx-prev]', lbx).addEventListener('click', () => lShow(lIdx - 1));
  $('[data-lbx-next]', lbx).addEventListener('click', () => lShow(lIdx + 1));
  lbx.addEventListener('click', e => { if (e.target === lbx) lClose(); });
  addEventListener('keydown', e => { if (!lbx.classList.contains('is-open')) return; if (e.key === 'Escape') lClose(); if (e.key === 'ArrowRight') lShow(lIdx + 1); if (e.key === 'ArrowLeft') lShow(lIdx - 1); });
  let tx = null; lbx.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive: true });
  lbx.addEventListener('touchend', e => { if (tx === null) return; const d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 50) lShow(lIdx + (d < 0 ? 1 : -1)); tx = null; });

  /* ---------- FAQ ---------- */
  $$('.acc__b').forEach(b => b.addEventListener('click', () => { const open = b.getAttribute('aria-expanded') === 'true'; b.setAttribute('aria-expanded', !open); b.nextElementSibling.hidden = open; if (motion && !open) gsap.from(b.nextElementSibling, { opacity: 0, y: -10, duration: .5, ease: OUT }); ScrollTrigger && ScrollTrigger.refresh(); }));

  /* ---------- gallery filter ---------- */
  $$('[data-g]').forEach(b => b.addEventListener('click', () => { const g = b.dataset.g;
    $$('[data-g]').forEach(x => x.setAttribute('aria-pressed', x === b));
    $$('.gal__i').forEach(i => { const v = g === 'all' || i.dataset.tags.split(' ').includes(g); i.hidden = !v; });
    if (motion) { gsap.fromTo($$('.gal__i:not([hidden]) .zf'), { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .8, ease: OUT, stagger: .05 }); ScrollTrigger.refresh(); } }));

  /* ---------- travel modes ---------- */
  const tv = $('[data-travel]');
  if (tv) $$('[data-mode]', tv).forEach(b => b.addEventListener('click', () => { const m = b.dataset.mode;
    $$('[data-mode]', tv).forEach(x => x.setAttribute('aria-pressed', x === b));
    $$('[data-t]', tv).forEach(li => { const v = D.travel[li.dataset.t][m]; const el = $('[data-min]', li); li.classList.toggle('is-na', v == null);
      if (motion && v != null) gsap.fromTo(el, { innerText: +el.textContent || 0 }, { innerText: v, duration: .8, ease: 'power2.out', snap: { innerText: 1 } }); else el.textContent = v == null ? '–' : v; }); }));

  addEventListener('keydown', e => { if (e.key === 'Escape') { closeBook(); closeMenu(); } });

  /* ---------- house type slider ---------- */
  const ts = $('[data-tslider]');
  if (ts) {
    const slides = $$('.tslide', ts); let cur = 0;
    const show = n => {
      const next = (n + slides.length) % slides.length; if (next === cur) return;
      const a = slides[cur], b = slides[next];
      if (motion) {
        gsap.to(a, { opacity: 0, duration: .45, ease: 'power2.in', onComplete: () => { a.classList.remove('is-on'); b.classList.add('is-on');
          gsap.fromTo(b, { opacity: 0 }, { opacity: 1, duration: .6 });
          gsap.fromTo($('.tslide__name', b), { yPercent: 40, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 1.1, ease: OUT });
          gsap.fromTo($('.tslide__img img', b), { scale: 1.15 }, { scale: 1, duration: 1.4, ease: OUT });
          ScrollTrigger.refresh(); } });
      } else { a.classList.remove('is-on'); b.classList.add('is-on'); }
      cur = next; $('[data-tcur]', ts).textContent = cur + 1;
      $$('[data-ttab]', ts).forEach(t => t.setAttribute('aria-selected', +t.dataset.ttab === cur));
      $('.tpag__bar i', ts).style.inset = cur ? '0 0 0 50%' : '0 50% 0 0';
    };
    $('[data-tprev]', ts).addEventListener('click', () => show(cur - 1));
    $('[data-tnext]', ts).addEventListener('click', () => show(cur + 1));
    $$('[data-ttab]', ts).forEach(t => t.addEventListener('click', () => show(+t.dataset.ttab)));
    $('.ttabs', ts).addEventListener('keydown', e => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { show(cur + (e.key === 'ArrowRight' ? 1 : -1)); $$('[data-ttab]', ts)[cur].focus(); } });
  }

  /* ---------- reviews slider ---------- */
  const rw = $('[data-rv-wrap]');
  if (rw) {
    const items = $$('[data-rv]', rw); let cur = 0;
    const show = n => { const nx = (n + items.length) % items.length;
      items[cur].hidden = true; items[nx].hidden = false; cur = nx;
      $('[data-rcur]', rw).textContent = String(cur + 1).padStart(2, '0') + ' / ' + String(items.length).padStart(2, '0');
      if (motion) gsap.fromTo(items[cur].children, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 1, ease: OUT, stagger: .08 }); };
    $('[data-rprev]', rw).addEventListener('click', () => show(cur - 1));
    $('[data-rnext]', rw).addEventListener('click', () => show(cur + 1));
  }

  /* ---------- floor plan tabs ---------- */
  $$('[data-ftab]').forEach(b => b.addEventListener('click', () => {
    const k = b.dataset.ftab;
    $$('[data-ftab]').forEach(x => x.setAttribute('aria-pressed', x === b));
    $$('[data-floor-svg]').forEach(x => x.hidden = x.dataset.floorSvg !== k);
    $$('[data-floor-list]').forEach(x => x.hidden = x.dataset.floorList !== k);
  }));

  /* ---------- house list: floating photo on hover ---------- */
  const fl = $('.hl-float'), flImg = fl && $('img', fl);
  if (fl && matchMedia('(hover: hover)').matches && !$('[data-offer]')) {
    const qx = motion ? gsap.quickTo(fl, 'x', { duration: .6, ease: 'power3' }) : v => fl.style.left = v + 'px';
    const qy = motion ? gsap.quickTo(fl, 'y', { duration: .6, ease: 'power3' }) : v => fl.style.top = v + 'px';
    $$('[data-hl]').forEach(list => {
      list.addEventListener('mousemove', e => { qx(e.clientX); qy(e.clientY); });
      list.addEventListener('mouseover', e => { const r = e.target.closest('.hl__row'); if (!r) return; if (flImg.getAttribute('src') !== r.dataset.img) flImg.src = r.dataset.img; fl.classList.add('is-on'); if (motion) gsap.to(fl, { scale: 1, duration: .5, ease: OUT }); });
      list.addEventListener('mouseleave', () => { fl.classList.remove('is-on'); if (motion) gsap.to(fl, { scale: .8, duration: .4 }); });
    });
    if (motion) gsap.set(fl, { xPercent: -50, yPercent: -50, x: innerWidth / 2, y: innerHeight / 2, scale: .8, left: 0, top: 0 });
  }

  /* ---------- offer page: filters + plan <-> list ---------- */
  const offer = $('[data-offer]');
  if (offer) {
    const rows = $$('.hl__row', offer), plots = $$('.plot');
    const vis = (r, f) => f === 'all' || r.dataset.status === f || r.dataset.type === f;
    const setF = f => {
      $$('[data-f]').forEach(b => b.setAttribute('aria-pressed', b.dataset.f === f));
      rows.forEach(r => { const v = vis(r, f); if (r.hidden !== !v) { r.hidden = !v; } });
      plots.forEach(p => { const r = rows.find(x => x.dataset.id === p.dataset.id); p.classList.toggle('is-dim', r.hidden); });
      if (motion) { gsap.fromTo(rows.filter(r => !r.hidden), { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .7, ease: OUT, stagger: .03 }); ScrollTrigger.refresh(); }
    };
    $$('[data-f]').forEach(b => b.addEventListener('click', () => setF(b.dataset.f)));
    const m = { volne: 'volny', patrove: 'patrovy', prizemni: 'prizemni' }[location.hash.slice(1)]; if (m) setF(m);
    const hl = (id, on) => { plots.forEach(p => p.classList.toggle('is-hl', on && p.dataset.id === id)); rows.forEach(r => r.classList.toggle('is-hl', on && r.dataset.id === id)); };
    rows.forEach(r => { r.addEventListener('mouseenter', () => hl(r.dataset.id, true)); r.addEventListener('mouseleave', () => hl(r.dataset.id, false)); });
    const pick = id => { const r = rows.find(x => x.dataset.id === id); if (r.hidden) setF('all'); scrollToEl(r, -140); r.classList.remove('is-flash'); void r.offsetWidth; r.classList.add('is-flash'); setTimeout(() => r.classList.remove('is-flash'), 1600); };
    plots.forEach(p => {
      p.addEventListener('mouseenter', () => hl(p.dataset.id, true)); p.addEventListener('mouseleave', () => hl(p.dataset.id, false));
      p.addEventListener('click', () => pick(p.dataset.id));
      p.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); location.href = 'dum-' + p.dataset.id + '.html'; } });
    });
  }

  /* ---------- motion ---------- */
  if (!motion) return;
  const ENTER = 'top 90%';
  const go = () => {
    // hero title: letters rise out of a mask
    $$('.js-split').forEach(el => {
      const kind = el.dataset.split;
      const inView = el.getBoundingClientRect().top < innerHeight * .95;
      if (kind === 'chars') {
        const s = SplitText.create(el, { type: 'chars', mask: 'chars', charsClass: 'char', aria: 'none' });
        el.style.visibility = 'visible';
        gsap.from(s.chars, { yPercent: 115, duration: 1.4, ease: OUT, stagger: .05, delay: inView ? .15 : 0, scrollTrigger: inView ? null : { trigger: el, start: ENTER, once: true }, onComplete: () => s.revert() });
      } else if (kind === 'script') {
        el.style.visibility = 'visible';
        gsap.from(el, { clipPath: 'inset(0 100% 0 0)', duration: 1.6, ease: 'power3.inOut', delay: inView ? .6 : 0, scrollTrigger: inView ? null : { trigger: el, start: ENTER, once: true }, clearProps: 'clipPath' });
      } else {
        const s = SplitText.create(el, { type: 'lines', mask: 'lines', linesClass: 'line', aria: 'none' });
        el.style.visibility = 'visible';
        gsap.from(s.lines, { yPercent: 115, duration: 1.2, ease: OUT, stagger: .08, scrollTrigger: { trigger: el, start: ENTER, once: true }, onComplete: () => s.revert() });
      }
    });
    // simple reveals
    ScrollTrigger.batch('[data-r]', { start: 'top 94%', once: true,
      onEnter: b => gsap.to(b, { opacity: 1, y: 0, duration: 1.1, ease: OUT, stagger: .08, overwrite: true }) });
    // hero photo settles
    $$('.hero__media img').forEach(i => gsap.to(i, { scale: 1, duration: 2.2, ease: 'power3.out' }));
    $$('.hero, .dhero').forEach(h => gsap.to($('.hero__media', h), { yPercent: 18, ease: 'none', scrollTrigger: { trigger: h, start: 'top top', end: 'bottom top', scrub: true } }));
    // parallax bands
    $$('[data-par]').forEach(p => gsap.fromTo(p, { yPercent: -8 }, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: p.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } }));
    $$('.reason__img img, .space__grid img').forEach(i => gsap.fromTo(i, { yPercent: -6 }, { yPercent: 4, ease: 'none', scrollTrigger: { trigger: i.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } }));
    // arch opens up as it rises
    const arch = $('.arch__bg');
    if (arch) gsap.fromTo(arch, { scaleX: .72 }, { scaleX: 1, ease: 'none', scrollTrigger: { trigger: arch, start: 'top 95%', end: 'top 25%', scrub: true } });
    // clouds: cream -> drifting clouds -> landscape
    $$('.sky').forEach(sec => {
      const st = { trigger: sec, start: 'top top', end: 'bottom bottom', scrub: true };
      const tl = gsap.timeline({ scrollTrigger: st });
      tl.fromTo($('.sky__fade', sec), { opacity: 1 }, { opacity: 0, duration: .25, ease: 'none' }, 0)
        .fromTo($('.sky__cl--b', sec), { opacity: 1, scale: 1, yPercent: 0 }, { opacity: 0, scale: 1.7, yPercent: -10, duration: .6, ease: 'power1.in' }, .05)
        .fromTo($('.sky__cl--a', sec), { opacity: .95, yPercent: 0 }, { opacity: .55, yPercent: -40, duration: .9, ease: 'none' }, 0)
        .fromTo($('.sky__photo img', sec), { scale: 1.25 }, { scale: 1, duration: 1, ease: 'none' }, 0)
        .fromTo($('.sky__txt', sec), { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: .3, ease: 'power2.out' }, .5);
      $$('.sky__drift', sec).forEach((d, k) => gsap.to(d, { xPercent: -50, duration: k ? 90 : 140, ease: 'none', repeat: -1 }));
    });
    // pull-in photo: framed card opens to full screen
    $$('.zin').forEach(sec => {
      const tl = gsap.timeline({ scrollTrigger: { trigger: sec, start: 'top top', end: 'bottom bottom', scrub: true } });
      tl.fromTo($('.zin__media', sec), { clipPath: 'inset(16% 28% 16% 28%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: .7, ease: 'none' }, 0)
        .fromTo($('.zin__media img', sec), { scale: 1.35 }, { scale: 1, duration: 1, ease: 'none' }, 0)
        .fromTo($('.zin__txt', sec), { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: .3, ease: 'power2.out' }, .6);
    });
    // horizontal tracks (desktop): vertical scroll drives the track sideways
    const mm = gsap.matchMedia();
    mm.add('(min-width: 761px)', () => {
      $$('.hs').forEach(sec => {
        const track = $('[data-hs]', sec), bar = $('.hs__bar i', sec);
        const dist = () => Math.max(0, track.scrollWidth - innerWidth + parseFloat(getComputedStyle(track).paddingLeft));
        const tl = gsap.timeline({ scrollTrigger: { trigger: sec, start: 'top top', end: () => '+=' + dist(), pin: $('.hs__stick', sec), scrub: .6, invalidateOnRefresh: true, anticipatePin: 1 } });
        tl.to(track, { x: () => -dist(), ease: 'none' }, 0).fromTo(bar, { scaleX: 0 }, { scaleX: 1, ease: 'none' }, 0);
      });
    });
    ScrollTrigger.refresh();
  };
  // fonts first so split lines are measured right; never wait longer than 1.2 s
  Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 1200))]).then(go);
  // safety: never leave text hidden
  setTimeout(() => $$('.js-split').forEach(el => el.style.visibility = 'visible'), 2500);
})();
