/* Blatec · směr B — motion & interactions (GSAP 3.13 + ScrollTrigger, Lenis) */
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const root = document.documentElement;
  const motion = root.classList.contains('motion') && window.gsap;
  const D = window.BLATEC || { houses: [] };
  const IO = 'power4.inOut', OUT = 'expo.out';
  let favs = (() => { try { return JSON.parse(localStorage.getItem('blatec-favs') || '[]').filter(id => D.houses.some(h => h.id === id)); } catch (_) { return []; } })();
  let offerF = null;
  if (window.gsap) { gsap.registerPlugin(ScrollTrigger); ScrollTrigger.config({ ignoreMobileResize: true }); }

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
  const ring = $('.seal--logo .seal__ring');
  const cue = $('.cue'), fab = $('.callfab'), dock = $('.dock');
  const paintHdr = () => {
    ticking = false;
    const y = scrollY;
    cue && cue.classList.toggle('is-off', y > innerHeight * .4);
    if (ring && !root.classList.contains('rm')) ring.style.transform = `rotate(${(y * .12) % 360}deg)`;
    const under = document.elementsFromPoint(innerWidth / 2, 34).map(el => el.closest('[data-hdr]')).find(Boolean);
    hdr.classList.toggle('is-ink', !!under && under.dataset.hdr === 'ink');
    hdr.classList.toggle('is-bar', y > 24 && innerWidth <= 760);
    fab && fab.classList.toggle('is-off', y < innerHeight * .6);
    dock && dock.classList.toggle('is-off', y < innerHeight * .5);
    hdr.classList.toggle('is-hidden', y > 260 && y > lastY + 2 && !root.classList.contains('menu-on'));
    if (y < lastY - 2 || y < 260) hdr.classList.remove('is-hidden');
    lastY = y;
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(paintHdr); } }, { passive: true });
  paintHdr();

  /* ---------- menu ---------- */
  const menu = $('#menu');
  function openMenu() { menu.classList.add('is-open'); menu.setAttribute('aria-hidden', 'false'); root.classList.add('menu-on'); $$('[data-menu]').forEach(b => b.setAttribute('aria-expanded', 'true')); lock(true);
    if (motion) { gsap.fromTo($$('.menu__nav a', menu), { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: .9, ease: OUT, stagger: .045, delay: .35, clearProps: 'transform,opacity' });
      gsap.fromTo($$('.menu__lab, .menu__bar', menu), { opacity: 0 }, { opacity: 1, duration: .9, ease: OUT, delay: .45, clearProps: 'opacity' }); }
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
  $$('.acc__b').forEach(b => b.addEventListener('click', () => { const open = b.getAttribute('aria-expanded') === 'true'; b.setAttribute('aria-expanded', !open); b.nextElementSibling.hidden = open; if (motion && !open) gsap.from(b.nextElementSibling, { opacity: 0, y: -10, duration: .5, ease: OUT }); window.ScrollTrigger && ScrollTrigger.refresh(); }));

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
    const vis = (r, f) => f === 'all' || (f === 'fav' ? favs.includes(+r.dataset.id) : r.dataset.status === f || r.dataset.type === f);
    offerF = f => setF(f);
    const setF = f => {
      $$('[data-f]').forEach(b => b.setAttribute('aria-pressed', b.dataset.f === f));
      rows.forEach(r => { const v = vis(r, f); if (r.hidden !== !v) { r.hidden = !v; } });
      plots.forEach(p => { const r = rows.find(x => x.dataset.id === p.dataset.id); p.classList.toggle('is-dim', r.hidden); });
      const n = rows.filter(r => !r.hidden).length; $('[data-count]').textContent = n + (n === 1 ? ' dům' : n < 5 ? ' domy' : ' domů');
      if (motion) { gsap.fromTo(rows.filter(r => !r.hidden), { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .7, ease: OUT, stagger: .03 }); ScrollTrigger.refresh(); }
    };
    $$('[data-f]').forEach(b => b.addEventListener('click', () => setF(b.dataset.f)));
    const m = { volne: 'volny', patrove: 'patrovy', prizemni: 'prizemni', oblibene: 'fav' }[location.hash.slice(1)]; if (m && (m !== 'fav' || favs.length)) setF(m);
    const sortSel = $('[data-sort]');
    sortSel && sortSel.addEventListener('change', () => { const k = sortSel.value;
      const val = r => { const p = +r.dataset.price; return k === 'plot' ? -r.dataset.plot : k === 'id' ? +r.dataset.id : k === 'price' ? (p || 9e9) : (p ? -p : 9e9); };
      rows.slice().sort((a, b) => val(a) - val(b)).forEach(r => offer.appendChild(r));
      if (motion) gsap.fromTo(rows.filter(r => !r.hidden), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: .6, ease: OUT, stagger: .025 }); });
    const hl = (id, on) => { plots.forEach(p => p.classList.toggle('is-hl', on && p.dataset.id === id)); rows.forEach(r => r.classList.toggle('is-hl', on && r.dataset.id === id)); };
    rows.forEach(r => { r.addEventListener('mouseenter', () => hl(r.dataset.id, true)); r.addEventListener('mouseleave', () => hl(r.dataset.id, false)); });
    const pick = id => { const r = rows.find(x => x.dataset.id === id); if (r.hidden) setF('all'); scrollToEl(r, -140); r.classList.remove('is-flash'); void r.offsetWidth; r.classList.add('is-flash'); setTimeout(() => r.classList.remove('is-flash'), 1600); };
    plots.forEach(p => {
      p.addEventListener('mouseenter', () => hl(p.dataset.id, true)); p.addEventListener('mouseleave', () => hl(p.dataset.id, false));
      p.addEventListener('click', () => pick(p.dataset.id));
      p.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); location.href = 'dum-' + p.dataset.id + '.html'; } });
    });
  }

  /* ---------- clouds: exact tile width so the drift loops without a seam ---------- */
  const tiles = () => $$('.sky__drift').forEach(d => { const tw = Math.round(d.offsetHeight * 1100 / 504); d.style.setProperty('--tw', tw + 'px'); d.style.backgroundSize = tw + 'px 100%'; });
  tiles(); addEventListener('resize', tiles);

  /* ---------- free houses: swipeable cards ---------- */
  $$('[data-hc]').forEach(hc => {
    const tr = $('[data-hc-track]', hc), bar = $('.hc__bar i', hc);
    const step = () => { const c = tr.firstElementChild; return c ? c.getBoundingClientRect().width + parseFloat(getComputedStyle(tr).columnGap || 16) : 300; };
    const paint = () => { const w = tr.clientWidth / tr.scrollWidth; bar.style.width = (w * 100) + '%'; bar.style.left = (tr.scrollLeft / tr.scrollWidth * 100) + '%';
      $('[data-hc-prev]', hc).disabled = tr.scrollLeft < 4; $('[data-hc-next]', hc).disabled = tr.scrollLeft + tr.clientWidth > tr.scrollWidth - 4; };
    $('[data-hc-prev]', hc).addEventListener('click', () => tr.scrollBy({ left: -step(), behavior: 'smooth' }));
    $('[data-hc-next]', hc).addEventListener('click', () => tr.scrollBy({ left: step(), behavior: 'smooth' }));
    tr.addEventListener('scroll', paint, { passive: true }); addEventListener('resize', paint); paint();
  });

  /* ---------- toast ---------- */
  const toastEl = $('#toast'); let tt;
  function toast(msg) { if (!toastEl) return; toastEl.textContent = msg; toastEl.classList.add('is-on'); clearTimeout(tt); tt = setTimeout(() => toastEl.classList.remove('is-on'), 3200); }
  $$('[data-pdf]').forEach(b => b.addEventListener('click', () => toast(b.dataset.pdf === 'standardy' ? 'PDF se standardy doplníme po dodání podkladů' : `PDF karta domu ${b.dataset.pdf} bude k dispozici po dodání podkladů`)));

  /* ---------- favourites (this browser only) ---------- */
  const paintFavs = () => {
    $$('[data-fav]').forEach(b => { const on = favs.includes(+b.dataset.fav); b.setAttribute('aria-pressed', on); b.setAttribute('aria-label', `${on ? 'Odebrat' : 'Uložit'} dům ${b.dataset.fav}`); const t = $('span', b); if (t) t.textContent = on ? 'Uloženo' : 'Uložit dům'; });
    $$('.fav-n').forEach(n => n.textContent = favs.length);
    $$('.chip--fav').forEach(c => c.hidden = !favs.length);
  };
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-fav]'); if (!b) return;
    e.preventDefault(); e.stopPropagation();
    const id = +b.dataset.fav, i = favs.indexOf(id);
    if (i > -1) favs.splice(i, 1); else favs.push(id);
    try { localStorage.setItem('blatec-favs', JSON.stringify(favs)); } catch (_) {}
    paintFavs();
    if (motion && i < 0) gsap.fromTo($('svg', b), { scale: .6 }, { scale: 1, duration: .7, ease: 'elastic.out(1, .4)' });
    toast(i > -1 ? `Dům ${id} odebrán z uložených` : `Dům ${id} uložen. Najdete ho v nabídce pod „Uložené“.`);
    if (offerF && $('[data-f="fav"][aria-pressed="true"]')) offerF(favs.length ? 'fav' : 'all');
  });
  paintFavs();

  /* ---------- compare up to 3 houses (offer page) ---------- */
  const tray = $('#tray'), cmpM = $('#cmp'); let cmp = [];
  if (tray && cmpM) {
    const H = id => D.houses.find(h => h.id === id);
    const fmt = n => Math.round(n).toLocaleString('cs-CZ');
    const upd = () => { tray.classList.toggle('is-on', cmp.length > 0); $('#tray-chips').innerHTML = cmp.map(id => `<span>Dům ${id}</span>`).join('');
      $('#tray-go').disabled = cmp.length < 2; $$('[data-cmp]').forEach(x => x.setAttribute('aria-pressed', cmp.includes(+x.dataset.cmp))); };
    document.addEventListener('click', e => { const b = e.target.closest('[data-cmp]'); if (!b) return; e.preventDefault(); e.stopPropagation();
      const id = +b.dataset.cmp, i = cmp.indexOf(id);
      if (i > -1) cmp.splice(i, 1); else if (cmp.length >= 3) { toast('Porovnat můžete nejvýš 3 domy'); return; } else cmp.push(id);
      upd(); });
    const ST = { volny: 'Volný', rezervace: 'Rezervace', prodany: 'Prodaný' };
    const openCmp = () => { const L = cmp.map(H);
      const rows = [['Typ', h => h.label], ['Dispozice', h => h.disp], ['Užitná plocha', h => String(h.area).replace('.', ',') + ' m²', h => h.area, 'max'],
        ['Pozemek', h => h.plot + ' m²', h => h.plot, 'max'], ['Zahrada', h => 'na ' + h.garden], ['Parkování', h => h.parking],
        ['Cena', h => h.price && h.status !== 'prodany' ? fmt(h.price) + ' Kč' : h.status === 'prodany' ? 'Prodáno' : 'Na dotaz', h => h.status === 'prodany' ? Infinity : (h.price || Infinity), 'min'],
        ['Stav', h => `<span class="st st--${h.status}">${ST[h.status]}</span>`]];
      $('#cmp-body').innerHTML = `<div style="overflow-x:auto"><table class="ctable"><thead><tr><th></th>${L.map(h => `<th scope="col">Dům ${h.id}</th>`).join('')}</tr></thead><tbody>${rows.map(([n, f, val, best]) => {
        let bi = -1; if (val) { const vs = L.map(val); const t = best === 'max' ? Math.max(...vs) : Math.min(...vs); if (isFinite(t) && vs.filter(v => v === t).length === 1) bi = vs.indexOf(t); }
        return `<tr><th scope="row">${n}</th>${L.map((h, k) => `<td class="${k === bi ? 'best' : ''}">${f(h)}</td>`).join('')}</tr>`; }).join('')}
        <tr><th></th>${L.map(h => `<td><a class="ulink label" href="dum-${h.id}.html">Detail domu ${h.id}</a></td>`).join('')}</tr></tbody></table></div><p class="label label--reg muted" style="margin-top:16px">Zlatá tečka označuje nejlepší hodnotu v řádku. Zástupné údaje.</p>`;
      cmpM.classList.add('is-open'); cmpM.setAttribute('aria-hidden', 'false'); lock(true); setTimeout(() => $('.modal__x', cmpM).focus(), 60); };
    const closeCmp = () => { if (!cmpM.classList.contains('is-open')) return; cmpM.classList.remove('is-open'); cmpM.setAttribute('aria-hidden', 'true'); lock(false); $('#tray-go').focus(); };
    $('#tray-go').addEventListener('click', openCmp);
    $('#tray-clear').addEventListener('click', () => { cmp = []; upd(); });
    $$('[data-cmp-close]', cmpM).forEach(b => b.addEventListener('click', closeCmp));
    addEventListener('keydown', e => { if (e.key === 'Escape') closeCmp(); });
  }

  /* ---------- watchdog ---------- */
  $$('[data-wd]').forEach(wd => {
    $$('[data-wd-topic]', wd).forEach(b => b.addEventListener('click', () => b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') !== 'true')));
    wd.addEventListener('submit', e => { e.preventDefault();
      const em = wd.email, ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em.value.trim()), topics = $$('[data-wd-topic][aria-pressed="true"]', wd);
      const f = em.closest('.field'); f.classList.toggle('is-err', !ok); let sm = $('small', f);
      if (!ok) { if (!sm) { sm = document.createElement('small'); f.appendChild(sm); } sm.textContent = 'Zadejte e-mail ve tvaru jmeno@domena.cz'; } else sm && sm.remove();
      wd.ok.closest('.consent').classList.toggle('is-err', !wd.ok.checked);
      if (!topics.length) { toast('Vyberte, co máme hlídat'); return; }
      if (!ok) { em.focus(); return; }
      if (!wd.ok.checked) { toast('Potvrďte prosím souhlas se zasíláním'); wd.ok.focus(); return; }
      $('[data-wd-msg]', wd).textContent = `Na ${em.value.trim()} vám napíšeme: ${topics.map(t => t.textContent.toLowerCase()).join(', ')}.`;
      $('.wd__body', wd).hidden = true; $('.wd__done', wd).hidden = false;
      if (motion) gsap.from($('.wd__done', wd).children, { y: 24, opacity: 0, duration: .9, ease: OUT, stagger: .08 }); });
  });

  /* ---------- mortgage calculator ---------- */
  const calc = $('[data-calc]');
  if (calc) {
    const price = +calc.dataset.price, ins = { own: $('#c-own'), rate: $('#c-rate'), years: $('#c-years') };
    const fmt = n => Math.round(n).toLocaleString('cs-CZ') + ' Kč';
    const upd = () => { const own = +ins.own.value, rate = +ins.rate.value, years = +ins.years.value;
      Object.values(ins).forEach(i => i.style.setProperty('--p', ((i.value - i.min) / (i.max - i.min) * 100) + '%'));
      const loan = price * (1 - own / 100), r = rate / 100 / 12, n = years * 12, pay = r ? loan * r / (1 - Math.pow(1 + r, -n)) : loan / n;
      $('#o-own').textContent = own + ' % · ' + fmt(price * own / 100); $('#o-rate').textContent = rate.toLocaleString('cs-CZ', { minimumFractionDigits: 1 }) + ' %';
      $('#o-years').textContent = years + ' let'; $('#o-pay').textContent = fmt(pay); $('#o-loan').textContent = fmt(loan); $('#o-total').textContent = fmt(pay * n); };
    Object.values(ins).forEach(i => i.addEventListener('input', upd)); upd();
  }

  /* ---------- motion ---------- */
  if (!motion) return;
  // photos open up as they arrive; text is never hidden or moved by scrolling
  const zfs = $$('.zf').filter(f => f.getBoundingClientRect().top > innerHeight);
  zfs.forEach(f => f.classList.add('is-pre'));
  const zio = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting || e.boundingClientRect.top < 0) { e.target.classList.remove('is-pre'); zio.unobserve(e.target); } }), { rootMargin: '0px 0px 8% 0px' });
  zfs.forEach(f => zio.observe(f));
  const go = () => {
    // hero photo settles
    $$('.hero__media img').forEach(i => gsap.to(i, { scale: 1, duration: 2.2, ease: 'power3.out' }));
    $$('.hero, .dhero').forEach(h => gsap.to($('.hero__media', h), { yPercent: 18, ease: 'none', scrollTrigger: { trigger: h, start: 'top top', end: 'bottom top', scrub: true } }));
    // parallax bands
    $$('[data-par]').forEach(p => gsap.fromTo(p, { yPercent: -8 }, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: p.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } }));
    $$('.reason__img img, .space__grid img').forEach(i => gsap.fromTo(i, { yPercent: -5, scale: 1.12 }, { yPercent: 5, scale: 1.12, ease: 'none', scrollTrigger: { trigger: i.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } }));
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
    });
    // pull-in photo: framed card opens to full screen
    $$('.zin').forEach(sec => {
      const tl = gsap.timeline({ scrollTrigger: { trigger: sec, start: 'top top', end: 'bottom bottom', scrub: true } });
      // starts as an upside-down arch (flat top, round bottom) and opens to full screen
      const sx = innerWidth < 761 ? 9 : 27, sy = innerWidth < 761 ? 17 : 13;
      const r = 50 - sx;  // bottom radius = half the card width, so the bottom is a true semicircle
      tl.fromTo($('.zin__media', sec), { clipPath: `inset(${sy}% ${sx}% ${sy}% ${sx}% round 0vw 0vw ${r}vw ${r}vw)` }, { clipPath: 'inset(0% 0% 0% 0% round 0vw 0vw 0vw 0vw)', duration: .7, ease: 'none' }, 0)
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
    // keep scroll-linked scenes measured right when images, fonts or the iOS toolbar change the layout
    let rt; const refresh = () => { clearTimeout(rt); rt = setTimeout(() => ScrollTrigger.isScrolling() ? refresh() : ScrollTrigger.refresh(), 250); };
    addEventListener('load', refresh); addEventListener('orientationchange', refresh);
    if ('ResizeObserver' in window) { let last = document.body.scrollHeight; new ResizeObserver(() => { const hg = document.body.scrollHeight; if (Math.abs(hg - last) > 60) { last = hg; refresh(); } }).observe(document.body); }
  };
  // fonts first so split lines are measured right; never wait longer than 1.2 s
  Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 1200))]).then(go);
  // if GSAP failed to load, never leave content hidden
  setTimeout(() => { if (!window.ScrollTrigger) root.classList.remove('motion'); }, 3000);
})();
