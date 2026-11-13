/* Blatec · HP DOMY — shared site script (all pages). Data comes from data.js (window.BLATEC). */
(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const D = window.BLATEC;
const STATUS = D.status;
const H = D.houses;
const byId = id => H.find(h => h.id === +id);
const fmt = n => Math.round(n).toLocaleString('cs-CZ').replace(/[\s\u202f]/g, '\u00a0');
const fmtArea = n => n.toLocaleString('cs-CZ', { minimumFractionDigits: n % 1 ? 1 : 0 }) + '\u00a0m²';
const priceTxt = h => h.price ? fmt(h.price) + '\u00a0Kč' : 'Na dotaz';
const freeCount = H.filter(h => h.status === 'volny').length;
const scrollToEl = el => el && el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });

/* ---------- counters bound to data ---------- */
$$('.cnt-free').forEach(el => el.textContent = '· ' + freeCount);
$$('.cnt-free-n').forEach(el => el.textContent = freeCount);
$$('[data-type-free]').forEach(el => { const n = H.filter(h => h.type === el.dataset.typeFree && h.status === 'volny').length; el.textContent = n + ' volné'; });
const cnt = { all: H.length, volny: freeCount, rezervace: H.filter(h => h.status === 'rezervace').length, prodany: H.filter(h => h.status === 'prodany').length, prizemni: H.filter(h => h.type === 'prizemni').length, patrovy: H.filter(h => h.type === 'patrovy').length };
$$('[data-cnt]').forEach(el => el.textContent = cnt[el.dataset.cnt]);
const minPrice = Math.min(...H.filter(h => h.price && h.status !== 'prodany').map(h => h.price));
$$('[data-min-price]').forEach(el => el.textContent = fmt(minPrice) + ' Kč');

/* ---------- toast ---------- */
const toastEl = $('#toast'); let tt;
const toast = msg => { if (!toastEl) return; toastEl.textContent = msg; toastEl.classList.add('is-on'); clearTimeout(tt); tt = setTimeout(() => toastEl.classList.remove('is-on'), 3200); };

/* ---------- header: floating bubble after first scroll ---------- */
const hdr = $('#hdr');
const onScroll = () => { if (!hdr || hdr.classList.contains('menu-open')) return; hdr.classList.toggle('is-float', scrollY > 24 || document.body.classList.contains('view-ds')); };
addEventListener('scroll', onScroll, { passive: true }); onScroll();
const burger = $('#burger'), menu = $('#menu');
const setMenu = open => {
  if (!burger) return;
  burger.setAttribute('aria-expanded', open); burger.setAttribute('aria-label', open ? 'Zavřít menu' : 'Otevřít menu');
  menu.classList.toggle('is-open', open); menu.setAttribute('aria-hidden', !open);
  hdr.classList.toggle('menu-open', open);
  if (open) hdr.classList.remove('is-float'); else onScroll();
  document.documentElement.style.overflow = open ? 'hidden' : '';
  document.documentElement.classList.toggle('menu-on', open);
};
burger && burger.addEventListener('click', () => { setMenu(burger.getAttribute('aria-expanded') !== 'true'); const f = $('.callfab'); f && f.classList.toggle('is-on', !menu.classList.contains('is-open') && scrollY > 300); });
$$('#menu a').forEach(a => a.addEventListener('click', () => setMenu(false)));


/* ---------- favourites (saved houses, this browser only) ---------- */
const FKEY = 'blatec-oblibene';
let favs = (() => { try { return JSON.parse(localStorage.getItem(FKEY) || '[]').filter(id => byId(id)); } catch { return []; } })();
const saveFavs = () => { try { localStorage.setItem(FKEY, JSON.stringify(favs)); } catch {} };
function paintFavs() {
  $$('[data-fav]').forEach(b => { const on = favs.includes(+b.dataset.fav); b.setAttribute('aria-pressed', on); b.setAttribute('aria-label', `${on ? 'Odebrat' : 'Uložit'} dům ${b.dataset.fav}`); });
  $$('.fav-n').forEach(n => n.textContent = favs.length);
  $$('.hdr__fav, .chip--fav').forEach(x => x.hidden = favs.length === 0);
}
document.addEventListener('click', e => {
  const b = e.target.closest('[data-fav]'); if (!b) return;
  e.preventDefault(); e.stopPropagation();
  const id = +b.dataset.fav, i = favs.indexOf(id);
  if (i > -1) favs.splice(i, 1); else favs.push(id);
  saveFavs(); paintFavs();
  toast(i > -1 ? `Dům ${id} odebrán z uložených` : `Dům ${id} uložen. Najdete ho pod srdíčkem nahoře.`);
  if (state.f === 'fav' && typeof render === 'function') { if (!favs.length) setFilter('all', state.t); else render(); }
});


/* ---------- in-page links: scroll reliably on the first tap ----------
   Smooth anchor scrolling used to be cancelled on phones when images finished loading
   and ScrollTrigger re-measured the page mid-scroll. We drive the scroll ourselves and
   hold any re-measure until it has finished. */
let progScroll = false, progT = 0;
function goTo(id, push) {
  const t = document.getElementById(id); if (!t) return false;
  const off = id === 'top' ? 0 : (hdr ? 84 : 0);
  const top = Math.max(0, t.getBoundingClientRect().top + scrollY - off);
  progScroll = true; clearTimeout(progT);
  const done = () => { progScroll = false; removeEventListener('scrollend', done); };
  addEventListener('scrollend', done, { once: true }); progT = setTimeout(done, 1600);
  window.scrollTo({ top, behavior: reduce ? 'auto' : 'smooth' });
  if (push) { try { history.pushState(null, '', '#' + id); } catch {} }
  return true;
}
document.addEventListener('click', e => {
  if (e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  const a = e.target.closest('a[href]'); if (!a || a.target === '_blank') return;
  const url = new URL(a.getAttribute('href'), location.href);
  if (url.origin !== location.origin || url.pathname.replace(/index\.html$/, '') !== location.pathname.replace(/index\.html$/, '') || url.hash.length < 2) return;
  const id = decodeURIComponent(url.hash.slice(1));
  if (id === 'komponenty' || !document.getElementById(id)) return; // hash-driven views and filters keep their default
  e.preventDefault();
  if (menu && menu.classList.contains('is-open')) setMenu(false);
  goTo(id, true);
});

/* ---------- copy + placeholders ---------- */
$$('[data-copy]').forEach(b => b.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(b.dataset.copy); toast('Zkopírováno: ' + b.dataset.copy); }
  catch { const r = document.createRange(); r.selectNodeContents(b.previousElementSibling); const s = getSelection(); s.removeAllRanges(); s.addRange(r); toast('Označeno, zkopírujte Ctrl+C'); }
}));
$$('[data-gdpr]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); toast('Zásady ochrany osobních údajů doplní HP DOMY'); }));
$$('[data-pdf]').forEach(b => b.addEventListener('click', e => { e.preventDefault(); toast(b.dataset.pdf === 'standardy' ? 'PDF se standardy doplníme po dodání podkladů' : `PDF karta domu ${b.dataset.pdf} bude dostupná po dodání podkladů`); }));

/* ---------- accordion ---------- */
function acc(root, items, renderHead, onOpen) {
  if (!root) return;
  root.innerHTML = items.map((it, i) => `<div class="acc__item ${i === 0 ? 'is-open' : ''}"><button class="acc__btn" aria-expanded="${i === 0}" aria-controls="${root.id}-p${i}" id="${root.id}-b${i}">${renderHead(it)}<span class="pm" aria-hidden="true"></span></button><div class="acc__panel" id="${root.id}-p${i}" role="region" aria-labelledby="${root.id}-b${i}"><div><p>${it.text}</p></div></div></div>`).join('');
  $$('.acc__btn', root).forEach((b, i) => b.addEventListener('click', () => {
    const item = b.parentElement, open = !item.classList.contains('is-open');
    $$('.acc__item', root).forEach(x => { x.classList.remove('is-open'); x.querySelector('.acc__btn').setAttribute('aria-expanded', false); });
    if (open) { item.classList.add('is-open'); b.setAttribute('aria-expanded', true); onOpen && onOpen(i); }
  }));
}
const faqHead = it => `<span class="h3" style="font-family:var(--f-text);font-weight:500;font-size:clamp(17px,1.5vw,20px);letter-spacing:-.015em">${it.q}</span>`;
acc($('#faq-acc'), D.faq.map(f => ({ q: f[0], text: f[1] })), faqHead);
const STD_ACC = D.stdShort;
acc($('#std-acc'), STD_ACC.map(s => ({ ico: s[0], t: s[1], text: s[2], k: s[3] })), it => `<svg class="ico" aria-hidden="true"><use href="#${it.ico}"/></svg><span class="h3">${it.t}</span>`, i => { $$('#std-media img').forEach(im => im.classList.toggle('is-on', +im.dataset.k === STD_ACC[i][3])); });

/* ---------- lightbox (shared) ---------- */
const lb = $('#lb');
const LB = { list: [], i: 0, from: null };
function lbShow(i) {
  const L = LB.list; if (!L.length) return; LB.i = (i + L.length) % L.length; const g = L[LB.i];
  $('#lb-img').src = `img/${g.src}-1600.webp`; $('#lb-img').alt = g.title + ' – zástupná vizualizace';
  $('#lb-cap').textContent = g.title; $('#lb-count').textContent = `${LB.i + 1} / ${L.length}`;
  const th = $('#lb-thumbs'); if (th) $$('button', th).forEach((b, k) => b.setAttribute('aria-current', k === LB.i));
}
function lbOpen(list, i, from) {
  if (!lb) return; LB.list = list; LB.from = from;
  const th = $('#lb-thumbs');
  if (th) th.innerHTML = list.map((g, k) => `<button aria-label="${g.title}" data-k="${k}"><img src="img/${g.src}-800.webp" alt="" loading="lazy"></button>`).join('');
  lbShow(i); lb.classList.add('is-open'); document.documentElement.style.overflow = 'hidden'; $('#lb-close').focus();
}
const lbClose = () => { lb.classList.remove('is-open'); document.documentElement.style.overflow = ''; LB.from && LB.from.focus({ preventScroll: true }); };
if (lb) {
  $('#lb-close').addEventListener('click', lbClose);
  $('#lb-prev').addEventListener('click', () => lbShow(LB.i - 1)); $('#lb-next').addEventListener('click', () => lbShow(LB.i + 1));
  $('#lb-stage').addEventListener('click', e => { if (e.target === e.currentTarget) lbClose(); });
  let sx = null; $('#lb-stage').addEventListener('pointerdown', e => sx = e.clientX);
  $('#lb-stage').addEventListener('pointerup', e => { if (sx === null) return; const dx = e.clientX - sx; if (Math.abs(dx) > 50) lbShow(LB.i + (dx < 0 ? 1 : -1)); sx = null; });
  const th = $('#lb-thumbs'); th && th.addEventListener('click', e => { const b = e.target.closest('button'); if (b) lbShow(+b.dataset.k); });
}

/* ---------- gallery grid ---------- */
const gal = $('#gal');
if (gal) {
  const all = D.gallery; let f = 'all';
  const filtered = () => all.filter(g => f === 'all' || g.tags.includes(f));
  const render = () => {
    const items = filtered(), big = gal.dataset.big !== 'off';
    gal.innerHTML = items.map((g, i) => `<button class="gal__item" data-i="${i}" aria-label="Zvětšit: ${g.title}"><img src="img/${g.src}-800.webp" srcset="img/${g.src}-800.webp 800w, img/${g.src}-1600.webp 1600w" sizes="(min-width:860px) ${i === 0 && big ? '50vw' : '25vw'}, 50vw" alt="${g.title} – zástupná vizualizace" loading="lazy" decoding="async" width="800" height="450"><span>${g.title}</span></button>`).join('')
      + (f === 'all' || f === 'int' ? `<div class="gal__ph"><div><svg><use href="#i-image"/></svg>Vizualizace interiéru doplníme, jakmile je HP DOMY uvolní.</div></div>` : '');
  };
  render();
  $$('[data-g]').forEach(b => b.addEventListener('click', () => { f = b.dataset.g; $$('[data-g]').forEach(x => x.setAttribute('aria-pressed', x === b)); render(); }));
  gal.addEventListener('click', e => { const b = e.target.closest('.gal__item'); if (b) lbOpen(filtered(), +b.dataset.i, b); });
}
$$('[data-lb]').forEach(b => b.addEventListener('click', () => { const list = JSON.parse(b.closest('[data-lb-list]').dataset.lbList); lbOpen(list, +b.dataset.lb, b); }));

/* ---------- site plan (situace): always a vertical strip, the whole street fits one screen ---------- */
const svg = $('#plan'), NS = 'http://www.w3.org/2000/svg';
const el = (t, a = {}, p) => { const n = document.createElementNS(NS, t); for (const k in a) n.setAttribute(k, a[k]); if (p) p.appendChild(n); return n; };
const COL = { volny: ['#eceefc', '#2c3fd6'], rezervace: ['#f8eedb', '#c9a36a'], prodany: ['#efedea', '#c9c5bd'] };
const HOUSE = { volny: '#2c3fd6', rezervace: '#8f8a82', prodany: '#c9c5bd' };
const geo = D.geo;
const plots = {};
const state = { f: 'all', t: null, sort: 'id', dir: 1, active: null, cmp: [], all: false };
const stacked = matchMedia('(max-width: 899px)'), canHover = matchMedia('(hover: hover)');
function buildPlan() {
  if (!svg) return;
  svg.innerHTML = '';
  const root = el('g', { transform: 'translate(560 0) rotate(90)' }, svg);
  const up = (cx, cy) => ` rotate(-90 ${cx} ${cy})`;
  el('rect', { x: 0, y: 0, width: 1000, height: 560, fill: '#f6f5f2' }, root);
  el('rect', { x: 30, y: 258, width: 940, height: 52, rx: 6, fill: '#dedbd4' }, root);
  el('line', { x1: 50, y1: 284, x2: 950, y2: 284, stroke: '#fff', 'stroke-width': 2, 'stroke-dasharray': '14 12' }, root);
  el('text', { x: 500, y: 289, 'text-anchor': 'middle', 'font-family': 'Inter,system-ui', 'font-size': 12, fill: '#6c675f', 'letter-spacing': '2' }, root).textContent = 'NOVÁ PŘÍJEZDOVÁ ULICE';
  const cg = el('g', { transform: 'translate(952 30)' }, root); el('circle', { r: 16, fill: '#fff', stroke: '#dedbd4' }, cg); el('path', { d: 'M0 -10 L5 5 L0 2 L-5 5Z', fill: '#161616' }, cg);
  el('text', { x: 0, y: 30, 'text-anchor': 'middle', 'font-size': 10, 'font-family': 'Inter,system-ui', fill: '#6c675f', transform: up(0, 27) }, cg).textContent = 'S';
  H.forEach(h => {
    const g = geo[h.id], [fill, stroke] = COL[h.status];
    const grp = el('g', { class: 'plot', tabindex: 0, role: 'button', 'data-id': h.id, 'aria-label': `Dům ${h.id}, ${h.label.toLowerCase()}, ${STATUS[h.status]}, ${priceTxt(h)}` }, root);
    el('rect', { class: 'plot__ring', x: g.x - 5, y: g.y - 5, width: g.w + 10, height: g.h + 10, rx: 10, fill: 'none', stroke: '#161616', 'stroke-width': 1, 'stroke-dasharray': '4 4' }, grp);
    el('rect', { class: 'plot__bg', x: g.x, y: g.y, width: g.w, height: g.h, rx: 6, fill, stroke, 'stroke-width': 1.5 }, grp);
    const hx = g.x + 14, hw = g.w - 28, hy = g.north ? g.y + g.h - 112 : g.y + 50;
    const houseFill = HOUSE[h.status];
    if (h.type === 'patrovy') {
      el('rect', { class: 'plot__house', x: hx + 8, y: hy, width: hw - 16, height: 66, rx: 2, fill: houseFill }, grp);
      el('rect', { x: hx + 18, y: hy + 10, width: hw - 36, height: 46, rx: 1, fill: 'none', stroke: '#fff', 'stroke-width': 1.2, opacity: .55 }, grp);
    } else {
      el('path', { class: 'plot__house', d: `M${hx} ${hy} h${hw} v44 h-${hw * .45} v28 h-${hw * .55} z`, fill: houseFill, transform: g.north ? '' : 'translate(0 -6)' }, grp);
    }
    const py = g.north ? g.y + g.h - 38 : g.y + 8, px = g.x + g.w - 29;
    el('rect', { x: g.x + g.w - 46, y: py, width: 34, height: 30, rx: 3, fill: '#fff', stroke, 'stroke-width': 1 }, grp);
    el('text', { x: px, y: py + 20, 'text-anchor': 'middle', 'font-family': 'Inter,system-ui', 'font-size': 13, 'font-weight': 600, fill: stroke, transform: up(px, py + 15) }, grp).textContent = 'P';
    const gy = g.north ? g.y + 18 : g.y + g.h - 26;
    [0, 1, 2].forEach(k => el('circle', { cx: g.x + 22 + k * 22, cy: gy, r: 6, fill: stroke, opacity: .18 }, grp));
    const nb = el('g', { transform: `translate(${g.x + 18} ${g.north ? g.y + g.h - 30 : g.y + 22}) rotate(-90)` }, grp);
    el('circle', { r: 17, fill: '#fff', stroke: '#161616', 'stroke-width': 1 }, nb);
    el('text', { class: 'plot__num', 'text-anchor': 'middle', y: 6, style: 'font-size:18px' }, nb).textContent = h.id;
    plots[h.id] = grp;
    grp.addEventListener('mouseenter', () => hover(h.id, true));
    grp.addEventListener('mouseleave', () => hover(h.id, false));
    grp.addEventListener('focus', () => hover(h.id, true));
    grp.addEventListener('blur', () => hover(h.id, false));
    grp.addEventListener('click', () => pick(h.id, grp));
    grp.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(h.id, grp); } });
    if (state.active === h.id) grp.classList.add('is-active');
  });
  applyDim();
}
const visible = h => (state.f === 'all' || (state.f === 'fav' ? favs.includes(h.id) : h.status === state.f)) && (!state.t || h.type === state.t);
const applyDim = () => Object.entries(plots).forEach(([id, g]) => g.classList.toggle('is-dim', !visible(byId(id))));
/* plot click: quick view beside the list on desktop, jump to the house row on phones */
function pick(id, from) {
  if (!stacked.matches || !hlist) { openHouse(id, from); return; }
  let r = $(`.hrow[data-id="${id}"]`);
  if (!r || r.hidden) { if (!visible(byId(id))) setFilter('all', null); state.all = true; render(); r = $(`.hrow[data-id="${id}"]`); }
  if (!r) return;
  scrollToEl(r);
  r.classList.remove('is-flash'); void r.offsetWidth; r.classList.add('is-flash');
}

/* ---------- house list ---------- */
const hlist = $('#hlist');
const withCmp = !!$('[data-compare]');
const statusRank = { volny: 0, rezervace: 1, prodany: 2 };
const plural = n => n === 1 ? 'dům' : n > 1 && n < 5 ? 'domy' : 'domů';
function render() {
  if (!hlist) return;
  const list = H.filter(visible).sort((a, b) => {
    const k = state.sort; let va = a[k], vb = b[k];
    if (k === 'status') { va = statusRank[va]; vb = statusRank[vb]; }
    if (k === 'price') { va = a.status === 'prodany' ? 2e12 : va ?? 1e12; vb = b.status === 'prodany' ? 2e12 : vb ?? 1e12; }
    return (va > vb ? 1 : va < vb ? -1 : a.id - b.id) * state.dir;
  });
  const favBtn = h => `<button class="fav" type="button" data-fav="${h.id}" aria-pressed="${favs.includes(h.id)}" aria-label="${favs.includes(h.id) ? 'Odebrat' : 'Uložit'} dům ${h.id}"><svg aria-hidden="true"><use href="#i-heart"/></svg></button>`;
  const cmpBtn = h => `<label class="cmp-lbl"><button class="cmp" type="button" data-cmp="${h.id}" aria-pressed="${state.cmp.includes(h.id)}" aria-label="Porovnat dům ${h.id}"></button><span>Porovnat</span></label>`;
  hlist.innerHTML = list.map(h => `
    <article class="hrow hrow--${h.status}${state.active === h.id ? ' is-active' : ''}" data-id="${h.id}" tabindex="0">
      <a class="hrow__img" href="dum-${h.id}.html" data-nodrawer tabindex="-1" aria-hidden="true"><img src="img/${h.img}-thumb.webp" alt="" width="320" height="240" loading="lazy" decoding="async"><span class="hrow__no">${h.id}</span></a>
      <div class="hrow__main">
        <div class="hrow__t"><b class="hrow__name">Dům ${h.id}</b><span class="badge badge--${h.status}">${STATUS[h.status]}</span></div>
        <p class="hrow__type">${h.label} · ${h.disp} · ${fmtArea(h.area)}</p>
        <dl class="hrow__kv"><div><dt>Pozemek</dt><dd>${fmtArea(h.plot)}</dd></div><div><dt>Zahrada</dt><dd>na ${h.garden}</dd></div></dl>
      </div>
      <div class="hrow__side">
        <b class="hrow__price${h.price ? '' : ' ask'}">${priceTxt(h)}</b>
        <div class="hrow__act">${withCmp ? cmpBtn(h) : ''}${favBtn(h)}<a class="hrow__go" href="dum-${h.id}.html" data-nodrawer>Detail<span class="sr"> domu ${h.id}</span><svg aria-hidden="true"><use href="#i-arrow"/></svg></a></div>
      </div>
    </article>`).join('');
  // home on phones: the first houses, the rest on request
  const lim = +(hlist.dataset.limit || 0);
  if (lim && stacked.matches && !state.all && list.length > lim) {
    $$('.hrow', hlist).slice(lim).forEach(c => c.hidden = true);
    hlist.insertAdjacentHTML('beforeend', `<div class="cards-more"><button class="btn btn--ghost" type="button" data-allcards>Zobrazit všech ${list.length} domů</button></div>`);
  }
  const n = $('#hl-n'); if (n) n.parentElement.innerHTML = `<span id="hl-n">${list.length}</span> ${plural(list.length)}<small> · každý se 2 stáními u domu</small>`;
  $('#empty').hidden = list.length > 0;
  applyDim(); paintFavs();
}
function setFilter(f, t) {
  state.f = f; state.t = t;
  $$('[data-f]').forEach(x => x.setAttribute('aria-pressed', x.dataset.f === state.f));
  $$('[data-t]').forEach(x => x.setAttribute('aria-pressed', x.dataset.t === (state.t || '')));
  render(); applyDim();
}
if (svg || hlist) {
  buildPlan(); render();
  stacked.addEventListener('change', render);
  $$('.filters .chip').forEach(c => c.addEventListener('click', () => {
    if (c.dataset.f) setFilter(c.dataset.f, state.t);
    if (c.dataset.t !== undefined) setFilter(state.f, c.dataset.t || null);
  }));
  const rs = $('[data-reset]'); rs && rs.addEventListener('click', () => setFilter('all', null));
  const so = $('#hl-sort'); so && so.addEventListener('change', () => { state.sort = so.value; state.dir = 1; render(); });
  // filters from the URL hash (#volne, #patrove, #prizemni)
  const hashFilter = () => { const m = { volne: ['volny', null], patrove: ['all', 'patrovy'], prizemni: ['all', 'prizemni'], oblibene: ['fav', null] }[location.hash.slice(1)]; if (m) setFilter(m[0], m[1]); };
  hashFilter(); addEventListener('hashchange', hashFilter);
}
const tip = $('#tip'), box = $('#plan-box');
function hover(id, on) {
  plots[id]?.classList.toggle('is-hover', on);
  $$(`.hrow[data-id="${id}"]`).forEach(r => r.classList.toggle('is-hover', on));
  if (!tip) return;
  if (on && canHover.matches && plots[id]) {
    const h = byId(id), b = box.getBoundingClientRect(), r = plots[id].querySelector('.plot__bg').getBoundingClientRect();
    tip.innerHTML = `<b>Dům ${h.id}</b> · ${h.label} ${h.disp}<br>${fmtArea(h.plot)} pozemek · ${priceTxt(h)}`;
    tip.style.left = (r.left - b.left + r.width / 2) + 'px'; tip.style.top = (r.top - b.top + 6) + 'px';
    tip.classList.add('is-on');
  } else tip.classList.remove('is-on');
}
if (hlist) {
  let cur = null;
  const set = id => { if (id === cur) return; if (cur) plots[cur]?.classList.remove('is-hover'); cur = id; if (id) plots[id]?.classList.add('is-hover'); };
  hlist.addEventListener('mouseover', e => { const r = e.target.closest('.hrow'); set(r ? +r.dataset.id : null); });
  hlist.addEventListener('mouseleave', () => set(null));
  hlist.addEventListener('click', e => {
    if (e.target.closest('[data-allcards]')) { state.all = true; render(); return; }
    if (e.target.closest('a,button,label')) return;
    const r = e.target.closest('.hrow'); if (r) openHouse(+r.dataset.id, r);
  });
  hlist.addEventListener('keydown', e => { const r = e.target.closest('.hrow'); if (r && e.target === r && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openHouse(+r.dataset.id, r); } });
}

/* ---------- compare (nabídka) ---------- */
const tray = $('#tray'), cmpModal = $('#cmp-modal');
function updateTray() {
  if (!tray) return;
  tray.classList.toggle('is-on', state.cmp.length > 0);
  $('#tray-chips').innerHTML = state.cmp.map(id => `<span>Dům ${id}</span>`).join('');
  $('#tray-go').toggleAttribute('disabled', state.cmp.length < 2);
  $('#tray-go').setAttribute('aria-disabled', state.cmp.length < 2);
}
document.addEventListener('click', e => {
  const b = e.target.closest('[data-cmp]'); if (!b) return;
  e.preventDefault(); e.stopPropagation();
  const id = +b.dataset.cmp, i = state.cmp.indexOf(id);
  if (i > -1) state.cmp.splice(i, 1);
  else if (state.cmp.length >= 3) { toast('Porovnat můžete nejvýš 3 domy'); return; }
  else state.cmp.push(id);
  $$(`[data-cmp="${id}"]`).forEach(x => x.setAttribute('aria-pressed', state.cmp.includes(id)));
  updateTray();
});
function openCompare() {
  const L = state.cmp.map(byId);
  const rows = [
    ['Typ', h => h.label], ['Dispozice', h => h.disp], ['Užitná plocha', h => fmtArea(h.area), h => h.area, 'max'],
    ['Pozemek', h => fmtArea(h.plot), h => h.plot, 'max'], ['Parkování', h => h.parking],
    ['Zahrada', h => 'na ' + h.garden], ['Cena', h => priceTxt(h), h => h.price || Infinity, 'min'], ['Stav', h => `<span class="badge badge--${h.status}">${STATUS[h.status]}</span>`]
  ];
  $('#cmp-body').innerHTML = `<div style="overflow-x:auto"><table class="ctable"><thead><tr><th></th>${L.map(h => `<th scope="col">Dům ${h.id}</th>`).join('')}</tr></thead><tbody>${rows.map(([n, f, val, best]) => {
    let bi = -1; if (val) { const vs = L.map(val); const t = best === 'max' ? Math.max(...vs) : Math.min(...vs); if (vs.filter(v => v === t).length === 1 && isFinite(t)) bi = vs.indexOf(t); }
    return `<tr><th scope="row">${n}</th>${L.map((h, k) => `<td class="${k === bi ? 'best' : ''}">${f(h)}</td>`).join('')}</tr>`;
  }).join('')}<tr><th></th>${L.map(h => `<td><a class="btn btn--sm" href="dum-${h.id}.html">Detail <span class="ic" style="width:28px;height:28px"><svg><use href="#i-arrow"/></svg></span></a></td>`).join('')}</tr></tbody></table></div>
  <p class="calc__note" style="padding:14px 24px 20px">Tečka označuje nejlepší hodnotu v řádku. Zástupné údaje.</p>`;
  cmpModal.classList.add('is-open'); document.documentElement.style.overflow = 'hidden'; $('#cmp-close').focus();
}
const closeCompare = () => { cmpModal.classList.remove('is-open'); document.documentElement.style.overflow = ''; $('#tray-go').focus(); };
if (tray) {
  $('#tray-go').addEventListener('click', openCompare);
  $('#tray-clear').addEventListener('click', () => { state.cmp = []; $$('[data-cmp]').forEach(x => x.setAttribute('aria-pressed', false)); updateTray(); });
  $('#cmp-close').addEventListener('click', closeCompare);
  cmpModal.addEventListener('click', e => { if (e.target === cmpModal) closeCompare(); });
}

/* ---------- drawer: quick view ---------- */
const drawer = $('#drawer'), scrim = $('#scrim'); let lastFocus = null;
function miniPlan(id) {
  const g = geo[id];
  let s = `<svg viewBox="40 40 920 490" aria-hidden="true"><rect x="30" y="258" width="940" height="52" fill="#dedbd4"/>`;
  H.forEach(h => { const q = geo[h.id]; s += `<rect x="${q.x}" y="${q.y}" width="${q.w}" height="${q.h}" rx="6" fill="${h.id === id ? '#161616' : '#fff'}" stroke="#cfcac1"/>`; });
  return s + `<circle cx="${g.x + g.w / 2}" cy="${g.y + g.h / 2}" r="34" fill="none" stroke="#2c3fd6" stroke-width="5"/></svg>`;
}
function openHouse(id, from) {
  if (!drawer) { location.href = `dum-${id}.html`; return; }
  const h = byId(id); state.active = id; lastFocus = from || document.activeElement;
  Object.entries(plots).forEach(([k, g]) => g.classList.toggle('is-active', +k === id));
  $$('.hrow').forEach(r => r.classList.toggle('is-active', +r.dataset.id === id));
  $('#dr-body').innerHTML = `
    <div class="drawer__img"><img src="img/${h.img}-800.webp" alt="Zástupná vizualizace – ${h.label.toLowerCase()} dům" width="800" height="450"></div>
    <div class="drawer__title"><h2 class="h2" id="dr-title">Dům ${h.id}</h2><span class="badge badge--${h.status}">${STATUS[h.status]}</span></div>
    <dl class="spec">
      <div><dt>Typ</dt><dd>${h.label}</dd></div><div><dt>Dispozice</dt><dd>${h.disp}</dd></div>
      <div><dt>Užitná plocha</dt><dd>${fmtArea(h.area)}</dd></div><div><dt>Pozemek</dt><dd>${fmtArea(h.plot)}</dd></div>
      <div><dt>Parkování</dt><dd>${h.parking}</dd></div><div><dt>Zahrada</dt><dd>na ${h.garden}</dd></div>
    </dl>
    <div class="drawer__price"><span style="color:var(--muted);font-size:14px">Cena vč. DPH</span><b>${priceTxt(h)}</b></div>
    <div class="drawer__plans"><div class="mini">${miniPlan(id)}</div><a class="mini" href="dum-${h.id}.html#pudorys" style="text-decoration:none"><span><svg style="width:26px;height:26px;margin:0 auto 8px;display:block;color:var(--ink)"><use href="#s-plan"/></svg>Půdorys a místnosti v detailu domu</span></a></div>
    <span class="placeholder-note"><svg><use href="#i-info"/></svg>Zástupné údaje pro návrh webu</span>`;
  $('#dr-detail').href = `dum-${h.id}.html`;
  $('#dr-interest').hidden = h.status === 'prodany';
  drawer.classList.add('is-open'); scrim.classList.add('is-open');
  document.documentElement.style.overflow = 'hidden';
  setTimeout(() => $('#dr-close').focus(), 50);
}
function closeHouse() {
  drawer.classList.remove('is-open'); scrim.classList.remove('is-open');
  document.documentElement.style.overflow = '';
  if (lastFocus && document.contains(lastFocus)) lastFocus.focus({ preventScroll: true });
}
if (drawer) {
  $('#dr-close').addEventListener('click', closeHouse); scrim.addEventListener('click', closeHouse);
  $('#dr-interest').addEventListener('click', () => { const id = state.active; closeHouse(); want(id); });
  drawer.addEventListener('keydown', e => {
    if (e.key !== 'Tab') return;
    const f = $$('button:not([hidden]), a[href], [tabindex="0"]', drawer).filter(x => x.offsetParent !== null);
    if (!f.length) return; const first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });
}
function want(id) {
  const sel = $('#f-house');
  if (!sel) { location.href = `kontakt.html#dum-${id}`; return; }
  sel.value = String(id); scrollToEl($('#kontakt') || $('#form'));
  setTimeout(() => $('#f-name').focus({ preventScroll: true }), reduce ? 0 : 700); toast(`Dům ${id} je předvyplněný ve formuláři`);
}
$$('[data-want]').forEach(b => { if (!b.closest('#cards')) b.addEventListener('click', () => want(+b.dataset.want)); });

/* ---------- contact form ---------- */
const form = $('#form');
if (form) {
  const sel = $('#f-house');
  sel.innerHTML = `<option value="">Ještě nemám vybráno</option>` + H.map(h => `<option value="${h.id}" ${h.status === 'prodany' ? 'disabled' : ''}>Dům ${h.id} · ${h.label.toLowerCase()} ${h.disp} · ${STATUS[h.status]}</option>`).join('');
  const m = location.hash.match(/^#dum-(\d+)$/); if (m && byId(m[1]) && byId(m[1]).status !== 'prodany') sel.value = m[1];
  if (form.dataset.house) sel.value = form.dataset.house;
  $$('[data-topic]').forEach(b => b.addEventListener('click', () => { $$('[data-topic]').forEach(x => x.setAttribute('aria-pressed', x === b)); const msg = $('#f-msg'); if (msg) msg.placeholder = b.dataset.ph; }));
  const rules = {
    'f-name': v => v.trim().split(/\s+/).length >= 2,
    'f-phone': v => /^(\+?420)?\s?[1-9]\d{2}\s?\d{3}\s?\d{3}$/.test(v.replace(/[\s-]/g, ' ').trim()) || /^\+?\d{9,13}$/.test(v.replace(/[\s-]/g, '')),
    'f-email': v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim())
  };
  const check = id => { const i = document.getElementById(id), ok = rules[id](i.value); i.closest('.field').classList.toggle('has-error', !ok); i.setAttribute('aria-invalid', !ok); return ok; };
  Object.keys(rules).forEach(id => { const i = document.getElementById(id); i.addEventListener('blur', () => { if (i.value) check(id); }); i.addEventListener('input', () => { if (i.closest('.field').classList.contains('has-error')) check(id); }); });
  $('#f-consent').addEventListener('change', e => $('#consent').classList.toggle('has-error', !e.target.checked));
  form.addEventListener('submit', e => {
    e.preventDefault();
    const okFields = Object.keys(rules).map(check).every(Boolean);
    const consent = $('#f-consent').checked; $('#consent').classList.toggle('has-error', !consent);
    const ok = okFields && consent;
    $('#form-alert').classList.toggle('is-on', !ok);
    $('#form-alert span').textContent = !okFields ? 'Zkontrolujte prosím označená pole.' : 'Pro odeslání potvrďte souhlas se zpracováním údajů.';
    if (!ok) { (form.querySelector('.has-error .input') || $('#f-consent')).focus(); return; }
    const btn = $('#f-submit'); btn.classList.add('is-loading'); btn.disabled = true;
    btn.firstChild.textContent = 'Odesíláme '; btn.querySelector('use').setAttribute('href', '#i-loader');
    setTimeout(() => {
      btn.classList.remove('is-loading'); btn.disabled = false; btn.firstChild.textContent = 'Odeslat poptávku '; btn.querySelector('use').setAttribute('href', '#i-arrow');
      const house = sel.value ? `o dům ${sel.value}` : '';
      $('#done-msg').textContent = `Prodejce se vám ozve ${house ? 'ohledně zájmu ' + house + ' ' : ''}do dvou pracovních dnů na ${$('#f-email').value.trim()}.`;
      form.classList.add('is-done');
    }, 1300);
  });
  $('#f-again').addEventListener('click', () => { form.reset(); form.classList.remove('is-done'); $('#form-alert').classList.remove('is-on'); $('#f-name').focus(); });
}

/* ---------- travel times (lokalita) ---------- */
const travel = $('#travel');
if (travel) {
  const T = D.travel; let mode = 'auto';
  const draw = () => {
    const max = Math.max(...T.map(t => t[mode] || 0));
    travel.innerHTML = T.map(t => `<li><b>${t.place}</b><small>${t.note}</small><span class="t">${t[mode] ? t[mode] + ' min' : '–'}<i>${t.km ? 'cca ' + t.km + ' km' : ''}</i></span><span class="bar"><span style="transform:scaleX(${t[mode] ? (t[mode] / max).toFixed(3) : 0})"></span></span></li>`).join('');
  };
  draw();
  $$('[data-mode]').forEach(b => b.addEventListener('click', () => { mode = b.dataset.mode; $$('[data-mode]').forEach(x => x.setAttribute('aria-pressed', x === b)); draw(); }));
}

/* ---------- house detail: floor plan, calculator, sub-nav, mobile bar ---------- */
const fp = $('#fp');
if (fp) {
  const h = byId(fp.dataset.house), floors = D.plans[h.type];
  const draw = fi => {
    const f = floors[fi];
    $('#fp-svg').setAttribute('viewBox', `-4 -4 ${f.w + 8} ${f.h + 8}`);
    $('#fp-svg').innerHTML = f.rooms.map((r, k) => {
      const shape = r.pts ? `<polygon points="${r.pts.map(p => p.join(',')).join(' ')}"/>` : `<rect x="${r.r[0]}" y="${r.r[1]}" width="${r.r[2]}" height="${r.r[3]}"/>`;
      const [cx, cy] = r.c || [r.r[0] + r.r[2] / 2, r.r[1] + r.r[3] / 2];
      return `<g class="room" tabindex="0" data-k="${k}" aria-label="${k + 1}. ${r.n}, ${fmtArea(r.a)}">${shape}<circle cx="${cx}" cy="${cy}" r="4.6"/><text x="${cx}" y="${cy + 1.75}" text-anchor="middle">${k + 1}</text></g>`;
    }).join('') + `<rect x="0" y="0" width="${f.w}" height="${f.h}" fill="none" stroke="#161616" stroke-width="2.4"/>`;
    const tot = f.rooms.reduce((s, r) => s + r.a, 0);
    $('#fp-rooms').innerHTML = f.rooms.map((r, k) => `<li data-k="${k}"><span><i>${k + 1}</i>${r.n}</span><span>${fmtArea(r.a)}</span></li>`).join('') + `<li class="total"><span><i style="border:0"></i>${floors.length > 1 ? f.name + ' celkem' : 'Celkem'}</span><span>${fmtArea(Math.round(tot * 10) / 10)}</span></li>`;
    const on = (k, v) => { $$(`#fp [data-k="${k}"]`).forEach(x => x.classList.toggle('is-on', v)); };
    $$('#fp [data-k]').forEach(x => { x.addEventListener('mouseenter', () => on(x.dataset.k, true)); x.addEventListener('mouseleave', () => on(x.dataset.k, false)); x.addEventListener('focus', () => on(x.dataset.k, true)); x.addEventListener('blur', () => on(x.dataset.k, false)); });
  };
  draw(0);
  $$('[data-floor]').forEach(b => b.addEventListener('click', () => { $$('[data-floor]').forEach(x => x.setAttribute('aria-pressed', x === b)); draw(+b.dataset.floor); }));
}
const calc = $('#calc');
if (calc) {
  const price = +calc.dataset.price;
  const ins = { own: $('#c-own'), rate: $('#c-rate'), years: $('#c-years') };
  const upd = () => {
    const own = +ins.own.value, rate = +ins.rate.value, years = +ins.years.value;
    Object.values(ins).forEach(i => i.style.setProperty('--p', ((i.value - i.min) / (i.max - i.min) * 100) + '%'));
    const loan = price * (1 - own / 100), r = rate / 100 / 12, n = years * 12;
    const pay = r ? loan * r / (1 - Math.pow(1 + r, -n)) : loan / n;
    $('#o-own').textContent = own + ' % · ' + fmt(price * own / 100) + ' Kč';
    $('#o-rate').textContent = rate.toLocaleString('cs-CZ', { minimumFractionDigits: 1 }) + ' %';
    $('#o-years').textContent = years + ' let';
    $('#o-pay').textContent = fmt(pay) + ' Kč';
    $('#o-loan').textContent = fmt(loan) + ' Kč';
    $('#o-total').textContent = fmt(pay * n) + ' Kč';
  };
  Object.values(ins).forEach(i => i.addEventListener('input', upd)); upd();
}
const subnav = $('.subnav, .dock__tabs');
if (subnav) {
  const links = $$('.subnav a, .dock__tabs a');
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) links.forEach(a => { const on = a.getAttribute('href') === '#' + e.target.id; a.classList.toggle('is-active', on); if (on) { const p = a.parentElement; if (p.offsetParent && p.scrollWidth > p.clientWidth) p.scrollTo({ left: a.offsetLeft - (p.clientWidth - a.clientWidth) / 2, behavior: reduce ? 'auto' : 'smooth' }); } }); }), { rootMargin: '-40% 0px -55% 0px' });
  links.forEach(a => { const t = $(a.getAttribute('href')); t && io.observe(t); });
}
const mbar = $('.dock');
if (mbar) { const top = $('.hd-price'); const io = new IntersectionObserver(([e]) => mbar.classList.toggle('is-on', !e.isIntersecting && e.boundingClientRect.top < 0)); io.observe(top); }


/* ---------- review slider (scroll-snap + buttons + mouse drag) ---------- */
$$('[data-slider]').forEach(sl => {
  const tr = $('.rv__track', sl), prev = $('[data-rv="prev"]', sl), next = $('[data-rv="next"]', sl), bar = $('.rv__prog i', sl);
  const step = () => { const c = tr.firstElementChild; return c ? c.getBoundingClientRect().width + 14 : 300; };
  const upd = () => {
    const max = tr.scrollWidth - tr.clientWidth;
    prev.disabled = tr.scrollLeft < 4; next.disabled = tr.scrollLeft > max - 4;
    const vis = tr.clientWidth / tr.scrollWidth;
    bar.style.width = (vis * 100) + '%';
    bar.style.transform = `translateX(${max > 0 ? (tr.scrollLeft / max) * ((1 - vis) / vis) * 100 : 0}%)`;
  };
  prev.addEventListener('click', () => tr.scrollBy({ left: -step(), behavior: reduce ? 'auto' : 'smooth' }));
  next.addEventListener('click', () => tr.scrollBy({ left: step(), behavior: reduce ? 'auto' : 'smooth' }));
  tr.addEventListener('scroll', upd, { passive: true }); addEventListener('resize', upd); upd();
  tr.addEventListener('keydown', e => { if (e.key === 'ArrowRight') { e.preventDefault(); next.click(); } if (e.key === 'ArrowLeft') { e.preventDefault(); prev.click(); } });
  let down = null, moved = false;
  tr.addEventListener('pointerdown', e => { if (e.pointerType !== 'mouse') return; down = { x: e.clientX, s: tr.scrollLeft }; moved = false; });
  addEventListener('pointermove', e => { if (!down) return; const dx = e.clientX - down.x; if (Math.abs(dx) > 4) { moved = true; tr.classList.add('is-drag'); tr.scrollLeft = down.s - dx; } });
  addEventListener('pointerup', () => { if (!down) return; down = null; tr.classList.remove('is-drag'); });
  tr.addEventListener('click', e => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
});



/* ---------- floating call button: appears with the bubble ---------- */
const fab = $('.callfab');
if (fab) { const f = () => fab.classList.toggle('is-on', scrollY > 300 && !(menu && menu.classList.contains('is-open'))); addEventListener('scroll', f, { passive: true }); f(); }

/* ---------- watchdog (hlídací pes) ---------- */
const wd = $('[data-wd]');
if (wd) {
  $$('[data-wd-topic]', wd).forEach(b => b.addEventListener('click', () => b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') !== 'true')));
  const em = $('#wd-email'), cons = $('#wd-consent');
  const ok = () => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em.value.trim());
  em.addEventListener('input', () => { if (em.closest('.field').classList.contains('has-error')) em.closest('.field').classList.toggle('has-error', !ok()); });
  cons.addEventListener('change', () => cons.closest('.consent').classList.toggle('has-error', !cons.checked));
  wd.addEventListener('submit', e => {
    e.preventDefault();
    const topics = $$('[data-wd-topic][aria-pressed="true"]', wd);
    em.closest('.field').classList.toggle('has-error', !ok()); em.setAttribute('aria-invalid', !ok());
    cons.closest('.consent').classList.toggle('has-error', !cons.checked);
    if (!topics.length) { toast('Vyberte, co máme hlídat'); return; }
    if (!ok()) { em.focus(); return; }
    if (!cons.checked) { cons.focus(); return; }
    const btn = $('button[type="submit"]', wd); btn.classList.add('is-loading'); btn.disabled = true; btn.querySelector('use').setAttribute('href', '#i-loader');
    setTimeout(() => {
      $('#wd-done-msg').textContent = `Na ${em.value.trim()} vám napíšeme: ${topics.map(t => t.textContent.toLowerCase()).join(', ')}.`;
      wd.classList.add('is-done');
    }, 1000);
  });
}

paintFavs();

/* ---------- wall section (standardy) ---------- */
const ws = $('.ws');
if (ws) {
  const on = (l, v) => $$(`.ws [data-l="${l}"]`).forEach(x => x.classList.toggle('is-on', v));
  $$('.ws [data-l]').forEach(x => { ['mouseenter', 'focus'].forEach(ev => x.addEventListener(ev, () => on(x.dataset.l, true))); ['mouseleave', 'blur'].forEach(ev => x.addEventListener(ev, () => on(x.dataset.l, false))); });
}

/* ---------- keyboard ---------- */
addEventListener('keydown', e => {
  if (lb && lb.classList.contains('is-open')) { if (e.key === 'Escape') lbClose(); if (e.key === 'ArrowRight') lbShow(LB.i + 1); if (e.key === 'ArrowLeft') lbShow(LB.i - 1); return; }
  if (e.key !== 'Escape') return;
  if (cmpModal && cmpModal.classList.contains('is-open')) return closeCompare();
  if (drawer && drawer.classList.contains('is-open')) closeHouse();
  if (menu && menu.classList.contains('is-open')) setMenu(false);
});

/* ---------- design system view (#komponenty, index only) ---------- */
const dsIcons = $('#ds-icons');
if (dsIcons) {
  dsIcons.innerHTML = D.icons.map(([i, n]) => `<div><svg><use href="#${i}"/></svg>${n}</div>`).join('');
  const route = () => {
    const ds = location.hash === '#komponenty';
    document.body.classList.toggle('view-ds', ds);
    hdr.classList.toggle('hdr--hero', !ds);
    if (ds) scrollTo(0, 0);
    onScroll(); if (window.ScrollTrigger) ScrollTrigger.refresh();
  };
  addEventListener('hashchange', route); route();
}

/* ---------- motion (GSAP + ScrollTrigger) ---------- */
const startMotion = () => {
  if (reduce || !window.gsap) return;
  gsap.registerPlugin(ScrollTrigger);
  // no automatic re-measure on load/resize: those run through our guarded refresh(), never mid-scroll
  ScrollTrigger.config({ ignoreMobileResize: true, autoRefreshEvents: 'visibilitychange,DOMContentLoaded' });
  const ease = 'power3.out';
  if ($('.hero')) {
    gsap.fromTo('[data-hero-media] img', { scale: 1.12 }, { scale: 1, duration: 2.2, ease: 'power2.out' });
    gsap.from('[data-hero-in]', { y: 28, duration: 1.1, ease, stagger: .09, delay: .1 });
    gsap.from('.hero__ctas, .hero__bottom', { opacity: 0, duration: .9, ease, stagger: .1, delay: .25 });
  }
  if ($('[data-page-in]')) gsap.from('[data-page-in]', { y: 22, duration: .9, ease, stagger: .07, delay: .05 });
  gsap.from('.hdr__in', { y: -16, opacity: 0, duration: .9, ease, delay: .1 });
  const rest = () => {
    // Reveals fire the moment an element's top edge enters the viewport (not halfway in).
    // Only elements still below the fold get hidden first, so nothing above it can stay invisible.
    const ENTER = 'top 98%';
    const REVEAL = '[data-reveal], .sec__head > *, .sub-head > *, [data-stagger] > *, .amen__item, .gal__item, .gal__ph, .ct .form, .ct .person, .rv__track > *, .tl li, .band__txt, .wd, .std-cat, .tcard, .nextp, .ctaband';
    const below = [...new Set($$(REVEAL))].filter(e => e.offsetParent && e.getBoundingClientRect().top > innerHeight * .98);
    gsap.set(below, { opacity: 0, y: 18 });
    ScrollTrigger.batch(below, { start: ENTER, once: true, interval: .05, batchMax: 6,
      onEnter: batch => gsap.to(batch, { opacity: 1, y: 0, duration: .55, ease, stagger: .045, overwrite: true, clearProps: 'transform' }) });
    if ($('.hero')) gsap.to('[data-hero-media] img', { yPercent: 12, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: .2 } });
    const h = $('[data-words]');
    if (h) {
      const nodes = [...h.childNodes]; h.innerHTML = '';
      nodes.forEach(n => { if (n.nodeType === 3) n.textContent.split(/(\s+)/).forEach(w => { if (!w.trim()) h.append(w); else { const s = document.createElement('span'); s.className = 'word'; s.textContent = w; h.append(s); } }); else h.append(n); });
      if (h.getBoundingClientRect().top > innerHeight * .98) gsap.fromTo(h.querySelectorAll('.word'), { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .6, stagger: .05, ease, scrollTrigger: { trigger: h, start: ENTER, once: true }, clearProps: 'transform' });
      gsap.from(h.querySelector('.pill-img'), { width: 0, marginLeft: 0, marginRight: 0, duration: .8, ease, scrollTrigger: { trigger: h, start: ENTER, once: true } });
    }
    $$('[data-count]').forEach(n => { const end = +n.dataset.count, o = { v: 0 }; gsap.to(o, { v: end, duration: 1, ease: 'power2.out', scrollTrigger: { trigger: n, start: ENTER, once: true }, onUpdate: () => n.textContent = Math.round(o.v) }); });
    $$('[data-reveal-img]').forEach(f => { gsap.fromTo(f, { clipPath: 'inset(8% 5% 0% 5% round 8px)' }, { clipPath: 'inset(0% 0% 0% 0% round 8px)', ease: 'none', scrollTrigger: { trigger: f, start: 'top bottom', end: 'top 55%', scrub: .2 } }); gsap.fromTo(f.querySelector('img'), { scale: 1.1 }, { scale: 1, ease: 'none', scrollTrigger: { trigger: f, start: 'top bottom', end: 'bottom top', scrub: .2 } }); });
    const band = $('[data-band]');
    if (band) {
      gsap.fromTo(band, { clipPath: 'inset(0% 6% 0% 6% round 8px)' }, { clipPath: 'inset(0% 0% 0% 0% round 8px)', ease: 'none', scrollTrigger: { trigger: band, start: 'top bottom', end: 'top 40%', scrub: .2 } });
      gsap.fromTo(band.querySelector('img'), { yPercent: -8 }, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: band, start: 'top bottom', end: 'bottom top', scrub: .2 } });
    }
    if (svg && $('#plan').getBoundingClientRect().top > innerHeight * .98) gsap.from('#plan .plot', { opacity: 0, y: 8, duration: .45, ease, stagger: .025, scrollTrigger: { trigger: '#plan', start: ENTER, once: true }, clearProps: 'opacity,transform' });
    // keep trigger positions right when fonts, images or expanding content change the layout
    let rt; const refresh = () => { clearTimeout(rt); rt = setTimeout(() => { if (progScroll || ScrollTrigger.isScrolling()) return refresh(); ScrollTrigger.refresh(); }, 200); };
    document.fonts && document.fonts.ready.then(refresh);
    addEventListener('load', refresh); addEventListener('resize', refresh);
    if ('ResizeObserver' in window) { let last = document.body.scrollHeight; new ResizeObserver(() => { const hgt = document.body.scrollHeight; if (Math.abs(hgt - last) > 40) { last = hgt; refresh(); } }).observe(document.body); }
  };
  ('requestIdleCallback' in window) ? requestIdleCallback(rest, { timeout: 400 }) : setTimeout(rest, 200);
};
if (document.readyState === 'complete' || window.gsap) startMotion(); else addEventListener('load', startMotion, { once: true });
})();
