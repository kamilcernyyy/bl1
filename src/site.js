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
const fmt = n => Math.round(n).toLocaleString('cs-CZ').replace(/ /g, ' ');
const fmtArea = n => n.toLocaleString('cs-CZ', { minimumFractionDigits: n % 1 ? 1 : 0 }) + ' m²';
const priceTxt = h => h.price ? fmt(h.price) + ' Kč' : 'Na dotaz';
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
};
burger && burger.addEventListener('click', () => setMenu(burger.getAttribute('aria-expanded') !== 'true'));
$$('#menu a').forEach(a => a.addEventListener('click', () => setMenu(false)));

/* ---------- copy + placeholders ---------- */
$$('[data-copy]').forEach(b => b.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(b.dataset.copy); toast('Zkopírováno: ' + b.dataset.copy); }
  catch { const r = document.createRange(); r.selectNodeContents(b.previousElementSibling); const s = getSelection(); s.removeAllRanges(); s.addRange(r); toast('Označeno, zkopírujte Ctrl+C'); }
}));
$$('[data-gdpr]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); toast('Zásady ochrany osobních údajů doplní HP DOMY'); }));
$$('[data-pdf]').forEach(b => b.addEventListener('click', () => toast(b.dataset.pdf === 'standardy' ? 'PDF se standardy doplníme po dodání podkladů' : `PDF karta domu ${b.dataset.pdf} bude dostupná po dodání podkladů`)));

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

/* ---------- site plan (situace) ---------- */
const svg = $('#plan'), NS = 'http://www.w3.org/2000/svg';
const el = (t, a = {}, p) => { const n = document.createElementNS(NS, t); for (const k in a) n.setAttribute(k, a[k]); if (p) p.appendChild(n); return n; };
const COL = { volny: ['#e5f1e9', '#2f7a4c'], rezervace: ['#f8eedb', '#a86a12'], prodany: ['#efedea', '#a7a299'] };
const geo = D.geo;
const plots = {};
const state = { f: 'all', t: null, sort: 'id', dir: 1, active: null, cmp: [] };
let vertical = null;
function buildPlan() {
  if (!svg) return;
  const v = matchMedia('(max-width: 700px)').matches;
  if (v === vertical) return; vertical = v;
  svg.innerHTML = '';
  svg.setAttribute('viewBox', v ? '0 0 560 1000' : '0 0 1000 560');
  const root = v ? el('g', { transform: 'translate(560 0) rotate(90)' }, svg) : svg;
  const up = (cx, cy) => v ? ` rotate(-90 ${cx} ${cy})` : '';
  el('rect', { x: 0, y: 0, width: 1000, height: 560, fill: '#f6f5f2' }, root);
  el('rect', { x: 30, y: 258, width: 940, height: 52, rx: 6, fill: '#dedbd4' }, root);
  el('line', { x1: 50, y1: 284, x2: 950, y2: 284, stroke: '#fff', 'stroke-width': 2, 'stroke-dasharray': '14 12' }, root);
  el('text', { x: 500, y: 289, 'text-anchor': 'middle', 'font-family': 'Inter,system-ui', 'font-size': 12, fill: '#6c675f', 'letter-spacing': '2' }, root).textContent = 'NOVÁ PŘÍJEZDOVÁ ULICE';
  const cg = el('g', { transform: 'translate(952 30)' }, root); el('circle', { r: 16, fill: '#fff', stroke: '#dedbd4' }, cg); el('path', { d: 'M0 -10 L5 5 L0 2 L-5 5Z', fill: '#161616' }, cg);
  el('text', { x: 0, y: 30, 'text-anchor': 'middle', 'font-size': 10, 'font-family': 'Inter,system-ui', fill: '#6c675f', transform: up(0, 27) }, cg).textContent = 'S';
  const sg = el('g', { transform: 'translate(60 540)', 'font-family': 'Inter,system-ui', 'font-size': 10, fill: '#6c675f' }, root);
  el('rect', { x: 0, y: -6, width: 60, height: 5, fill: '#161616' }, sg); el('rect', { x: 60, y: -6, width: 60, height: 5, fill: '#fff', stroke: '#161616', 'stroke-width': 1 }, sg);
  el('text', { x: 0, y: 10 }, sg).textContent = '0'; el('text', { x: 54, y: 10 }, sg).textContent = '10'; el('text', { x: 114, y: 10 }, sg).textContent = '20 m';
  H.forEach(h => {
    const g = geo[h.id], [fill, stroke] = COL[h.status];
    const grp = el('g', { class: 'plot', tabindex: 0, role: 'button', 'data-id': h.id, 'aria-label': `Dům ${h.id}, ${h.label.toLowerCase()}, ${STATUS[h.status]}, ${priceTxt(h)}` }, root);
    el('rect', { class: 'plot__ring', x: g.x - 5, y: g.y - 5, width: g.w + 10, height: g.h + 10, rx: 10, fill: 'none', stroke: '#161616', 'stroke-width': 1, 'stroke-dasharray': '4 4' }, grp);
    el('rect', { class: 'plot__bg', x: g.x, y: g.y, width: g.w, height: g.h, rx: 6, fill, stroke, 'stroke-width': 1.5 }, grp);
    const hx = g.x + 14, hw = g.w - 28, hy = g.north ? g.y + g.h - 112 : g.y + 50;
    const houseFill = h.status === 'prodany' ? '#c9c5bd' : '#161616';
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
    const nb = el('g', { transform: `translate(${g.x + 18} ${g.north ? g.y + g.h - 30 : g.y + 22})${v ? ' rotate(-90)' : ''}` }, grp);
    el('circle', { r: v ? 16 : 13, fill: '#fff', stroke: '#161616', 'stroke-width': 1 }, nb);
    el('text', { class: 'plot__num', 'text-anchor': 'middle', y: 5, style: v ? 'font-size:18px' : '' }, nb).textContent = h.id;
    plots[h.id] = grp;
    grp.addEventListener('mouseenter', () => hover(h.id, true));
    grp.addEventListener('mouseleave', () => hover(h.id, false));
    grp.addEventListener('focus', () => hover(h.id, true));
    grp.addEventListener('blur', () => hover(h.id, false));
    grp.addEventListener('click', () => openHouse(h.id, grp));
    grp.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openHouse(h.id, grp); } });
    if (state.active === h.id) grp.classList.add('is-active');
  });
  applyDim();
}
const visible = h => (state.f === 'all' || h.status === state.f) && (!state.t || h.type === state.t);
const applyDim = () => Object.entries(plots).forEach(([id, g]) => g.classList.toggle('is-dim', !visible(byId(id))));

/* ---------- table + cards ---------- */
const tbody = $('#tbl tbody'), cards = $('#cards');
const withCmp = !!$('[data-compare]');
const statusRank = { volny: 0, rezervace: 1, prodany: 2 };
function render() {
  if (!tbody) return;
  const list = H.filter(visible).sort((a, b) => {
    const k = state.sort; let va = a[k], vb = b[k];
    if (k === 'status') { va = statusRank[va]; vb = statusRank[vb]; }
    if (k === 'price') { va = va ?? Infinity; vb = vb ?? Infinity; }
    if (k === 'type') { va = a.label; vb = b.label; }
    return (va > vb ? 1 : va < vb ? -1 : a.id - b.id) * state.dir;
  });
  const cmpBtn = h => `<button class="cmp" type="button" data-cmp="${h.id}" aria-pressed="${state.cmp.includes(h.id)}" aria-label="Porovnat dům ${h.id}"></button>`;
  tbody.innerHTML = list.map(h => `
    <tr data-id="${h.id}" class="${h.status === 'prodany' ? 'is-sold' : ''} ${state.active === h.id ? 'is-active' : ''}" tabindex="0">
      ${withCmp ? `<td class="cmp-cell">${cmpBtn(h)}</td>` : ''}
      <td class="house-no">${h.id}</td><td>${h.label}</td><td>${h.disp}</td>
      <td class="num">${fmtArea(h.area)}</td><td class="num">${fmtArea(h.plot)}</td><td>${h.parking}</td>
      <td class="num price ${h.price ? '' : 'ask'}">${priceTxt(h)}</td>
      <td class="st"><span class="badge badge--${h.status}">${STATUS[h.status]}</span></td>
      <td class="card-col"><a class="pdf-btn" href="dum-${h.id}.html" data-nodrawer>Detail domu</a></td>
    </tr>`).join('');
  cards.innerHTML = list.map(h => `
    <article class="hcard ${h.status === 'prodany' ? 'is-sold' : ''} ${state.active === h.id ? 'is-active' : ''}" data-id="${h.id}">
      <div class="hcard__top"><div class="hcard__title"><b>Dům ${h.id}</b><span>${h.label} · ${h.parking}</span></div><span class="badge badge--${h.status}">${STATUS[h.status]}</span></div>
      <dl><div><dt>Dispozice</dt><dd>${h.disp}</dd></div><div><dt>Užitná plocha</dt><dd>${fmtArea(h.area)}</dd></div><div><dt>Pozemek</dt><dd>${fmtArea(h.plot)}</dd></div></dl>
      <div class="hcard__bottom"><span class="hcard__price ${h.price ? '' : 'ask'}">${priceTxt(h)}</span>
      <div class="hcard__actions" style="display:flex;gap:8px;align-items:center">${withCmp ? `<label class="cmp-lbl">${cmpBtn(h)}Porovnat</label>` : ''}<a class="btn btn--ghost btn--sm" href="dum-${h.id}.html">Detail domu</a></div></div>
    </article>`).join('');
  $('#empty').hidden = list.length > 0;
  applyDim();
  $$('#tbl th[data-sort]').forEach(th => { if (th.dataset.sort === state.sort) th.setAttribute('aria-sort', state.dir > 0 ? 'ascending' : 'descending'); else th.removeAttribute('aria-sort'); });
}
function setFilter(f, t) {
  state.f = f; state.t = t;
  $$('[data-f]').forEach(x => x.setAttribute('aria-pressed', x.dataset.f === state.f));
  $$('[data-t]').forEach(x => x.setAttribute('aria-pressed', x.dataset.t === state.t));
  render(); applyDim();
}
if (svg || tbody) {
  buildPlan(); render();
  matchMedia('(max-width: 700px)').addEventListener('change', () => { buildPlan(); render(); });
  $$('.filters .chip').forEach(c => c.addEventListener('click', () => {
    if (c.dataset.f) setFilter(c.dataset.f, state.t);
    if (c.dataset.t) setFilter(state.f, state.t === c.dataset.t ? null : c.dataset.t);
  }));
  const rs = $('[data-reset]'); rs && rs.addEventListener('click', () => setFilter('all', null));
  $$('#tbl th[data-sort] button').forEach(b => b.addEventListener('click', () => { const k = b.parentElement.dataset.sort; state.dir = state.sort === k ? -state.dir : 1; state.sort = k; render(); }));
  // filters from the URL hash (#volne, #patrove, #prizemni)
  const hashFilter = () => { const m = { volne: ['volny', null], patrove: ['all', 'patrovy'], prizemni: ['all', 'prizemni'] }[location.hash.slice(1)]; if (m) setFilter(m[0], m[1]); };
  hashFilter(); addEventListener('hashchange', hashFilter);
}
const tip = $('#tip'), box = $('#plan-box');
function hover(id, on) {
  plots[id]?.classList.toggle('is-hover', on);
  $$(`#tbl tr[data-id="${id}"]`).forEach(r => r.classList.toggle('is-hover', on));
  if (!tip) return;
  if (on) {
    if (vertical || !plots[id]) return;
    const h = byId(id), b = box.getBoundingClientRect(), r = plots[id].querySelector('.plot__bg').getBoundingClientRect();
    tip.innerHTML = `<b>Dům ${h.id}</b> · ${h.label} ${h.disp}<br>${fmtArea(h.plot)} pozemek · ${priceTxt(h)} · ${STATUS[h.status]}`;
    tip.style.left = (r.left - b.left + r.width / 2) + 'px'; tip.style.top = (r.top - b.top + 8) + 'px';
    tip.classList.add('is-on');
  } else tip.classList.remove('is-on');
}
if (tbody) {
  tbody.addEventListener('mouseover', e => { const r = e.target.closest('tr'); if (r) plots[+r.dataset.id]?.classList.add('is-hover'); });
  tbody.addEventListener('mouseout', e => { const r = e.target.closest('tr'); if (r) plots[+r.dataset.id]?.classList.remove('is-hover'); });
  tbody.addEventListener('click', e => { if (e.target.closest('[data-nodrawer],[data-cmp]')) return; const r = e.target.closest('tr'); if (r) openHouse(+r.dataset.id, r); });
  tbody.addEventListener('keydown', e => { const r = e.target.closest('tr'); if (r && e.key === 'Enter' && e.target === r) openHouse(+r.dataset.id, r); });
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
  return s + `<circle cx="${g.x + g.w / 2}" cy="${g.y + g.h / 2}" r="34" fill="none" stroke="#7a5a3a" stroke-width="5"/></svg>`;
}
function openHouse(id, from) {
  if (!drawer) { location.href = `dum-${id}.html`; return; }
  const h = byId(id); state.active = id; lastFocus = from || document.activeElement;
  Object.entries(plots).forEach(([k, g]) => g.classList.toggle('is-active', +k === id));
  $$('#tbl tr, .hcard').forEach(r => r.classList.toggle('is-active', +r.dataset.id === id));
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
const subnav = $('.subnav');
if (subnav) {
  const links = $$('a', subnav);
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) links.forEach(a => { const on = a.getAttribute('href') === '#' + e.target.id; a.classList.toggle('is-active', on); if (on) a.scrollIntoView({ block: 'nearest', inline: 'nearest' }); }); }), { rootMargin: '-40% 0px -55% 0px' });
  links.forEach(a => { const t = $(a.getAttribute('href')); t && io.observe(t); });
}
const mbar = $('.mbar');
if (mbar) { const top = $('.hd-price'); const io = new IntersectionObserver(([e]) => mbar.classList.toggle('is-on', !e.isIntersecting && e.boundingClientRect.top < 0)); io.observe(top); }

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
  const ease = 'power3.out';
  if ($('.hero')) {
    gsap.fromTo('[data-hero-media] img', { scale: 1.12 }, { scale: 1, duration: 2.2, ease: 'power2.out' });
    gsap.from('[data-hero-in]', { y: 28, duration: 1.1, ease, stagger: .09, delay: .1 });
    gsap.from('.hero__sig, .hero__ctas, .hero__bottom', { opacity: 0, duration: .9, ease, stagger: .1, delay: .25 });
  }
  if ($('[data-page-in]')) gsap.from('[data-page-in]', { y: 22, duration: .9, ease, stagger: .07, delay: .05 });
  gsap.from('.hdr__in', { y: -16, opacity: 0, duration: .9, ease, delay: .1 });
  const rest = () => {
    if ($('.hero')) gsap.to('[data-hero-media] img', { yPercent: 12, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
    const h = $('[data-words]');
    if (h) {
      const nodes = [...h.childNodes]; h.innerHTML = '';
      nodes.forEach(n => { if (n.nodeType === 3) n.textContent.split(/(\s+)/).forEach(w => { if (!w.trim()) h.append(w); else { const s = document.createElement('span'); s.className = 'word'; s.textContent = w; h.append(s); } }); else h.append(n); });
      gsap.fromTo(h.querySelectorAll('.word'), { opacity: .2 }, { opacity: 1, stagger: .1, ease: 'none', scrollTrigger: { trigger: h, start: 'top 82%', end: 'bottom 45%', scrub: true } });
      gsap.from(h.querySelector('.pill-img'), { width: 0, marginLeft: 0, marginRight: 0, duration: 1.1, ease, scrollTrigger: { trigger: h, start: 'top 75%' } });
    }
    $$('[data-reveal]').forEach(elm => gsap.from(elm, { y: 36, opacity: 0, duration: 1, ease, scrollTrigger: { trigger: elm, start: 'top 88%', once: true } }));
    $$('.sec__head, .sub-head').forEach(elm => gsap.from(elm.children, { y: 26, opacity: 0, duration: .9, ease, stagger: .08, scrollTrigger: { trigger: elm, start: 'top 86%', once: true } }));
    $$('[data-stagger]').forEach(g => gsap.from(g.children, { y: 26, opacity: 0, duration: .8, ease, stagger: .06, scrollTrigger: { trigger: g, start: 'top 88%', once: true } }));
    $$('[data-count]').forEach(n => { const end = +n.dataset.count, o = { v: 0 }; gsap.to(o, { v: end, duration: 1.4, ease: 'power2.out', scrollTrigger: { trigger: n, start: 'top 90%', once: true }, onUpdate: () => n.textContent = Math.round(o.v) }); });
    $$('[data-reveal-img]').forEach(f => { gsap.fromTo(f, { clipPath: 'inset(10% 6% 0% 6% round 22px)' }, { clipPath: 'inset(0% 0% 0% 0% round 22px)', ease: 'none', scrollTrigger: { trigger: f, start: 'top 95%', end: 'top 35%', scrub: true } }); gsap.fromTo(f.querySelector('img'), { scale: 1.14 }, { scale: 1, ease: 'none', scrollTrigger: { trigger: f, start: 'top bottom', end: 'bottom top', scrub: true } }); });
    const band = $('[data-band]');
    if (band) {
      gsap.fromTo(band, { clipPath: 'inset(0% 8% 0% 8% round 22px)' }, { clipPath: 'inset(0% 0% 0% 0% round 22px)', ease: 'none', scrollTrigger: { trigger: band, start: 'top 90%', end: 'center 55%', scrub: true } });
      gsap.fromTo(band.querySelector('img'), { yPercent: -8 }, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: band, start: 'top bottom', end: 'bottom top', scrub: true } });
      gsap.from(band.querySelector('.band__txt'), { y: 40, opacity: 0, duration: 1, ease, scrollTrigger: { trigger: band, start: 'top 60%', once: true } });
    }
    if (svg) gsap.from('#plan .plot', { opacity: 0, y: 10, duration: .6, ease, stagger: .04, scrollTrigger: { trigger: '#plan', start: 'top 80%', once: true }, clearProps: 'opacity,transform' });
    if (gal) gsap.from('.gal__item, .gal__ph', { y: 30, opacity: 0, duration: .9, ease, stagger: .07, scrollTrigger: { trigger: '#gal', start: 'top 82%', once: true } });
    if ($('.amen__grid')) gsap.from('.amen__item', { y: 24, opacity: 0, duration: .8, ease, stagger: .06, scrollTrigger: { trigger: '.amen__grid', start: 'top 88%', once: true } });
    if ($('.ct')) gsap.from('.ct .form, .ct .person', { y: 30, opacity: 0, duration: 1, ease, stagger: .1, scrollTrigger: { trigger: '.ct', start: 'top 78%', once: true } });
    if ($('.tl')) gsap.from('.tl li', { y: 20, opacity: 0, duration: .7, ease, stagger: .08, scrollTrigger: { trigger: '.tl', start: 'top 85%', once: true } });
  };
  ('requestIdleCallback' in window) ? requestIdleCallback(rest, { timeout: 900 }) : setTimeout(rest, 300);
};
if (document.readyState === 'complete' || window.gsap) startMotion(); else addEventListener('load', startMotion, { once: true });
})();
