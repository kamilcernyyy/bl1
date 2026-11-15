"""Blatec · směr B (editorial). Builds ./v2/ from the same house data as the main site.

    python3 src/v2/build.py

Data (houses, plans, reviews, travel times, standards) is read from src/build.py,
so both design directions always show the same numbers.
"""
import json, os, re, html, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
OUT = os.path.join(ROOT, "v2")

# ---- shared data: execute only the data block of the main generator
_main = open(os.path.join(SRC, "build.py"), encoding="utf-8").read()
_argv = sys.argv; sys.argv = [_argv[0], "repo"]
D = {"__file__": os.path.join(SRC, "build.py")}
exec(_main[:_main.index("G_MARK =")], D)
exec(_main[_main.index("_ONE = re.compile"):_main.index("NAV = [")], D)
sys.argv = _argv
TYPES, HOUSES, GEO, PLANS, REVIEWS, GOOGLE, TRAVEL, STD_CATS, STATUS = (D[k] for k in
    ("TYPES", "HOUSES", "GEO", "PLANS", "REVIEWS", "GOOGLE", "TRAVEL", "STD_CATS", "STATUS"))
cz_typo = D["cz_typo"]
esc = html.escape

TEL, TEL_TXT, MAIL = "+420776294498", "+420 776 294 498", "info@impulsreality.com"
FREE = [h for h in HOUSES if h["status"] == "volny"]
area = lambda v: (f"{v:.1f}".replace(".", ",") if isinstance(v, float) else str(v)) + "&nbsp;m²"
money = lambda p: f"{p:,}".replace(",", "&nbsp;") + "&nbsp;Kč"
price = lambda h: "Prodáno" if h["status"] == "prodany" else (money(h["price"]) if h["price"] else "Na dotaz")
MINP = min(h["price"] for h in HOUSES if h["price"] and h["status"] != "prodany")
MINP_TXT = f"{MINP / 1e6:.2f}".replace(".", ",").rstrip("0").rstrip(",")

# ---- assets
CSS = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
CSS = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
CSS = re.sub(r"\s*\n\s*", "", CSS)
CSS = re.sub(r"\s*([{};,>])\s*", r"\1", CSS).replace(";}", "}")
os.makedirs(os.path.join(OUT, "js"), exist_ok=True)
open(os.path.join(OUT, "js", "app.js"), "w", encoding="utf-8").write(open(os.path.join(HERE, "app.js"), encoding="utf-8").read())
open(os.path.join(OUT, "js", "data.js"), "w", encoding="utf-8").write(
    "window.BLATEC=" + json.dumps(dict(houses=HOUSES, geo=GEO, status=STATUS), ensure_ascii=False, separators=(",", ":")) + ";")

ICON = {
    "arrow": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 12.5 12.5 3.5M5 3.5h7.5V11" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>',
    "right": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h12M9 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "left": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M14 8H2M7 3 2 8l5 5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "x": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m3 3 10 10M13 3 3 13" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>',
}
EMBLEM = ('<svg class="emblem" viewBox="0 0 40 60" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.15" stroke-linejoin="round">'
          '<path d="M20 58V14"/><path d="M20 14c-3.2-3.4-3.2-9 0-12.4 3.2 3.4 3.2 9 0 12.4z"/>'
          + "".join(f'<path d="M20 {y + 8}c-7 0-10.5-4.6-10.5-9.4 7 0 10.5 4.6 10.5 9.4z"/><path d="M20 {y + 8}c7 0 10.5-4.6 10.5-9.4-7 0-10.5 4.6-10.5 9.4z"/>' for y in (16, 27, 38))
          + '<path d="M14 58h12"/></g></svg>')


def img(name, alt, sizes="100vw", eager=False, cls="", w=None):
    have = [s for s in (800, 1200, 1600, 1920) if os.path.exists(os.path.join(ROOT, "img", f"{name}-{s}.webp"))]
    srcset = ", ".join(f"../img/{name}-{s}.webp {s}w" for s in have)
    big = have[-1] if not w else w
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="../img/{name}-{big}.webp" srcset="{srcset}" sizes="{sizes}" width="1600" height="900" alt="{esc(alt)}" {load}>'


def head(title, desc, preload=None, jsonld=None):
    pre = ""
    if preload:
        pre = (f'<link rel="preload" as="image" href="../img/{preload}-1600.webp" imagesrcset="../img/{preload}-800.webp 800w, ../img/{preload}-1600.webp 1600w'
               + (f', ../img/{preload}-1920.webp 1920w' if os.path.exists(os.path.join(ROOT, "img", f"{preload}-1920.webp")) else "")
               + '" imagesizes="100vw" fetchpriority="high">\n')
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n' if jsonld else ""
    return f'''<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, follow">
<meta name="theme-color" content="#2b221a">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="website"><meta property="og:locale" content="cs_CZ"><meta property="og:image" content="../img/og-1200x630.jpg">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%232b221a'/%3E%3Cpath d='M32 54V20M32 20c-4-4-4-11 0-15 4 4 4 11 0 15zM32 30c-8 0-12-5-12-11 8 0 12 5 12 11zM32 30c8 0 12-5 12-11-8 0-12 5-12 11zM32 42c-8 0-12-5-12-11 8 0 12 5 12 11zM32 42c8 0 12-5 12-11-8 0-12 5-12 11z' fill='none' stroke='%23f3f0e6' stroke-width='2.4'/%3E%3C/svg%3E">
<link rel="preload" as="font" type="font/woff2" href="fonts/instrument-serif-latin-400-normal.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="fonts/archivo-x-latin-400.woff2" crossorigin>
{pre}<script>(function(d){{var r=d.documentElement;r.classList.add(matchMedia('(prefers-reduced-motion: reduce)').matches?'rm':'motion');try{{if(sessionStorage.getItem('pt')){{r.classList.add('pt-in');sessionStorage.removeItem('pt')}}}}catch(e){{}}}})(document)</script>
<style>{CSS}</style>
{ld}</head>
<body>
<a class="skip" href="#main">Přeskočit na obsah</a>
<div class="pt" aria-hidden="true">{EMBLEM}</div>
'''


def header():
    return f'''<header class="hdr" id="hdr">
  <a class="logo" href="index.html"><span class="logo__n">Blatec</span><span class="logo__s">HP DOMY DEVELOPMENT</span></a>
  <div class="hdr__r">
    <a class="hdr__pick" href="nabidka.html"><span class="roll"><span>Vybrat<br>volný dům</span><span aria-hidden="true">Vybrat<br>volný dům</span></span></a>
    <div class="hdr__links">
      <button type="button" data-book><span class="roll"><span>Prohlídka &amp; hovor</span><span aria-hidden="true">Prohlídka &amp; hovor</span></span></button>
      <button type="button" data-menu aria-expanded="false" aria-controls="menu"><span class="roll"><span>Menu</span><span aria-hidden="true">Menu</span></span></button>
    </div>
    <button class="burger" type="button" data-menu aria-expanded="false" aria-controls="menu" aria-label="Otevřít menu"><i></i></button>
  </div>
</header>
'''


def menu():
    return f'''<nav class="menu" id="menu" aria-label="Hlavní menu" aria-hidden="true">
  <button class="menu__close" type="button" data-menu-close aria-label="Zavřít menu">{ICON["x"]}</button>
  <div class="menu__claims"><p>Postaveno, aby vydrželo</p><p>Světlo a vlastní zahrada</p><p>Klid na Hané</p></div>
  <div class="menu__nav">
    <a href="index.html"><span class="roll"><span>Úvod</span><span aria-hidden="true">Úvod</span></span></a>
    <a href="nabidka.html"><span class="roll"><span>Nabídka domů</span><span aria-hidden="true">Nabídka domů</span></span></a>
    <a href="index.html#typy"><span class="roll"><span>Typy domů</span><span aria-hidden="true">Typy domů</span></span></a>
    <a href="index.html#lokalita"><span class="roll"><span>Lokalita</span><span aria-hidden="true">Lokalita</span></span></a>
    <a href="index.html#prohlidka"><span class="roll"><span>Prohlídka</span><span aria-hidden="true">Prohlídka</span></span></a>
  </div>
  <div class="menu__foot">
    <div style="display:grid;gap:8px"><span class="label label--reg muted">Prodejce Pavel Čundrla · Impuls Reality</span><a class="h5 serif" href="tel:{TEL}">{TEL_TXT}</a></div>
    <button class="btn btn--solid" type="button" data-book>Domluvit prohlídku</button>
  </div>
</nav>
'''


def modal():
    opts = "".join(f'<option value="{h["id"]}">Dům {h["id"]} · {h["label"].lower()} · {STATUS[h["status"]]}</option>' for h in HOUSES if h["status"] != "prodany")
    return f'''<div class="modal" id="book" role="dialog" aria-modal="true" aria-labelledby="book-t" aria-hidden="true">
  <div class="modal__bg" data-close></div>
  <div class="modal__box">
    <button class="modal__x" type="button" data-close aria-label="Zavřít">{ICON["x"]}</button>
    <form class="bookf" novalidate>
      <div style="display:grid;gap:6px;margin-bottom:18px"><p class="script" id="book-t">Domluvte si</p><p class="serif h4">prohlídku</p></div>
      <div style="display:grid;gap:18px">
        <div class="grid-2"><label class="field"><span class="label">Jméno</span><input name="name" autocomplete="name" required></label>
        <label class="field"><span class="label">Telefon</span><input name="tel" type="tel" autocomplete="tel" required></label></div>
        <label class="field"><span class="label">E-mail</span><input name="email" type="email" autocomplete="email"></label>
        <label class="field"><span class="label">Dům</span><select name="house"><option value="">Zatím nevím</option>{opts}</select></label>
        <label class="field"><span class="label">Zpráva</span><textarea name="msg" rows="3" placeholder="Kdy se vám hodí prohlídka?"></textarea></label>
        <p class="p p--s muted">Ozve se vám prodejce Pavel Čundrla. Údaje použijeme jen k vyřízení dotazu.</p>
        <div><button class="btn btn--solid" type="submit">Odeslat</button></div>
      </div>
    </form>
    <div class="thanks" hidden><p class="script">Děkujeme</p><p class="p">Prodejce se vám brzy ozve. Spěcháte? Volejte <a class="ulink" href="tel:{TEL}">{TEL_TXT}</a>.</p><p class="label muted">Ukázka: formulář zatím nikam neodesílá</p></div>
  </div>
</div>
'''


FOOT_LINKS = [("index.html", "Úvod"), ("nabidka.html", "Nabídka domů"), ("index.html#typy", "Typy domů"), ("index.html#lokalita", "Lokalita")]


def footer():
    links = "".join(f'<a class="p--s" href="{u}">{t}</a>' for u, t in FOOT_LINKS)
    return f'''<footer class="ftr">
      <div><span class="logo"><span class="logo__n">Blatec</span><span class="logo__s">HP DOMY DEVELOPMENT</span></span><p class="p p--s" style="margin-top:14px">14 rodinných domů v&nbsp;Blatci u&nbsp;Olomouce.</p></div>
      <div><span class="label">Stránky</span>{links}</div>
      <div><span class="label">Prodej</span><span class="p--s">Pavel Čundrla, Impuls Reality</span><a class="p--s ulink" style="justify-self:start" href="tel:{TEL}">{TEL_TXT}</a><a class="p--s ulink" style="justify-self:start" href="mailto:{MAIL}">{MAIL}</a></div>
      <div><span class="label">Developer</span><span class="p--s">HP DOMY</span><span class="p--s">Vizualizace jsou ilustrační.</span></div>
      <div class="ftr__legal"><span class="label label--reg muted">© 2026 HP DOMY · Blatec (pracovní název)</span><a class="label label--reg ulink" href="../index.html">Zobrazit směr A</a></div>
    </footer>'''


def scripts(extra=""):
    return f'''<script src="js/gsap.min.js" defer></script>
<script src="js/ScrollTrigger.min.js" defer></script>
<script src="js/SplitText.min.js" defer></script>
<script src="js/lenis.min.js" defer></script>
<script src="js/data.js" defer></script>
<script src="js/app.js" defer></script>
{extra}</body>
</html>'''


def page(name, title, desc, body, preload=None, jsonld=None):
    out = head(title, desc, preload, jsonld) + header() + ('<div class="cue" aria-hidden="true"><span>Scroll</span><i></i></div>\n' if name == 'index.html' else '') + menu() + f'<main id="main">\n{body}\n</main>\n' + modal() + '<div class="hl-float" aria-hidden="true"><img alt=""></div>\n' + scripts()
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(cz_typo(out))


def hrow(h, rich=False):
    sold = h["status"] == "prodany"
    thumb = f'<div class="hl__thumb"><img src="../img/{h["img"]}-thumb.webp" alt="" width="320" height="240" loading="lazy" decoding="async"></div>' if rich else ""
    return (f'<a class="hl__row{" is-sold" if sold else ""}" href="dum-{h["id"]}.html" data-id="{h["id"]}" data-img="../img/{h["img"]}-800.webp" data-type="{h["type"]}" data-status="{h["status"]}">'
            f'{thumb}<span class="hl__name">Dům {h["id"]:02d}</span><span class="hl__type label label--reg">{h["label"]} · {h["disp"]} · {area(h["area"])}</span>'
            f'<span class="hl__plot label label--reg">Pozemek {area(h["plot"])}</span>'
            + (f'<span class="hl__plot label label--reg">Zahrada na {h["garden"]}</span>' if rich else "")
            + f'<span class="hl__price">{price(h)}</span><span class="hl__st"><span class="st st--{h["status"]}">{STATUS[h["status"]]}</span></span>'
            f'<span class="hl__go">{ICON["arrow"]}</span></a>')


def plan_svg(hl=None):
    """Situation drawn as a vertical strip (fits one screen), Hanák palette."""
    fills = {"volny": ("#f3f0e6", "#1c2230"), "rezervace": ("#e5ddc9", "#8d8576"), "prodany": ("#dcd6c8", "#b3ab9b")}
    s = '<svg viewBox="0 0 560 1000" role="group" aria-label="Situace domů"><g transform="translate(560 0) rotate(90)">'
    s += '<rect width="1000" height="560" fill="#ebe6d8"/><rect x="30" y="258" width="940" height="52" fill="#d9d2c1"/><line x1="50" y1="284" x2="950" y2="284" stroke="#f3f0e6" stroke-width="2" stroke-dasharray="14 12"/>'
    s += '<text x="500" y="289" text-anchor="middle" font-family="Archivo X,Arial" font-size="12" font-weight="600" letter-spacing="3" fill="#6f6758">NOVÁ ULICE</text>'
    for h in HOUSES:
        g = GEO[h["id"]]; f, st = fills[h["status"]]
        on = hl == h["id"]
        cx, cy = g["x"] + g["w"] / 2, g["y"] + (52 if g["north"] else g["h"] - 52)
        s += (f'<g class="plot" data-id="{h["id"]}" tabindex="0" role="button" aria-label="Dům {h["id"]}, {STATUS[h["status"]]}, {re.sub("&nbsp;", " ", price(h))}">'
              f'<rect class="pbg" x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" fill="{"#d8be86" if on else f}" stroke="{st}" stroke-width="{2.5 if on else 1}"/>'
              f'<rect x="{g["x"] + 18}" y="{g["y"] + (g["h"] - 120 if g["north"] else 40)}" width="{g["w"] - 36}" height="{64 if h["type"] == "patrovy" else 52}" fill="{st}" opacity="{.88 if h["status"] == "volny" else .45}"/>'
              f'<text x="{cx}" y="{cy}" transform="rotate(-90 {cx} {cy})" text-anchor="middle" dominant-baseline="central" font-family="Instrument Serif,serif" font-size="40" fill="{"#1c2230" if h["status"] != "prodany" else "#9a9282"}">{h["id"]}</text></g>')
    return s + "</g></svg>"


def floor_svg(fl, k):
    W, H = fl["w"], fl["h"]
    s = f'<svg viewBox="-6 -6 {W + 12} {H + 12}" data-floor-svg="{k}"{"" if k == 0 else " hidden"} aria-label="Půdorys: {fl["name"]}" role="img">'
    for i, r in enumerate(fl["rooms"], 1):
        if "r" in r:
            x, y, w, h = r["r"]; cx, cy = x + w / 2, y + h / 2
            s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#f3f0e6" stroke="#1c2230" stroke-width=".9"/>'
        else:
            pts = " ".join(f"{a},{b}" for a, b in r["pts"]); cx, cy = r["c"]
            s += f'<polygon points="{pts}" fill="#f3f0e6" stroke="#1c2230" stroke-width=".9"/>'
        s += f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" font-family="Instrument Serif,serif" font-size="6.4" fill="#1c2230">{i}</text>'
    return s + f'<rect x="0" y="0" width="{W}" height="{H}" fill="none" stroke="#1c2230" stroke-width="2.6"/></svg>'


# ======================================================================= HOME
REASONS = [
    ("01", "Klid obce, město na dosah", "Blatec má kolem 650 obyvatel a&nbsp;vlak do Olomouce staví přímo v&nbsp;obci. Autem jste v&nbsp;centru za 15 minut.", "street", "Zástupná vizualizace ulice s novými domy"),
    ("02", "Vlastní zahrada", "Pozemky od 529 do 728 m². Zahrada na sever, nebo na jih. Vyberete si podle toho, jak rádi žijete.", "garden", "Zástupná vizualizace terasy se zahradou"),
    ("03", "Staví HP DOMY", f"Zděná stavba, tepelné čerpadlo a&nbsp;podlahové topení. Developer s&nbsp;hodnocením {str(GOOGLE['rating']).replace('.', ',')} z&nbsp;5 na Googlu.", "entry", "Zástupná vizualizace vstupu do domu"),
]
TYPE_TXT = {
    "patrovy": "Dvě podlaží: dole obývací pokoj s&nbsp;kuchyní a&nbsp;pracovna, nahoře ložnice a&nbsp;dva pokoje. Dost místa pro rodinu i&nbsp;hosty.",
    "prizemni": "Všechno na jednom podlaží, bez schodů. Ložnice se šatnou, dva pokoje a&nbsp;obývací pokoj s&nbsp;kuchyní.",
}
types_html = ""
for k, (t, T) in enumerate(TYPES.items()):
    hs = [h for h in HOUSES if h["type"] == t]
    free = [h for h in hs if h["status"] == "volny"]
    rooms = len([r for f in PLANS[t] for r in f["rooms"] if r["n"] in ("Ložnice", "Pokoj", "Pracovna")])
    types_html += f'''<div class="tslide{" is-on" if k == 0 else ""}" data-slide="{k}" role="group" aria-roledescription="snímek" aria-label="{T["label"]} dům">
        <div class="tslide__grid">
          <div class="tslide__facts">
            <dl><dt class="label label--reg">Dispozice</dt><dd class="num">{T["disp"]}</dd></dl>
            <dl><dt class="label label--reg">Užitná plocha</dt><dd class="num">{area(T["area"])}</dd></dl>
            <dl><dt class="label label--reg">Volných domů z&nbsp;{len(hs)}</dt><dd class="num">{len(free)}</dd></dl>
          </div>
          <a class="tslide__img" href="dum-{free[0]["id"]}.html" aria-label="Detail domu {free[0]["id"]}">{img(T["img"], f"Zástupná vizualizace: {T['label'].lower()} dům", "(min-width:860px) 34vw, 100vw")}</a>
          <div class="tslide__txt">
            <p class="p">{TYPE_TXT[t]}</p>
            <p class="label label--reg muted">{rooms} pokoje a&nbsp;obývací pokoj · {len(PLANS[t])} podlaží</p>
            <a class="btn" href="nabidka.html#{"patrove" if t == "patrovy" else "prizemni"}"><span>{T["label"]} domy</span>{ICON["arrow"]}</a>
          </div>
        </div>
        <p class="tslide__name serif h2" aria-hidden="true">{T["label"]} dům</p>
      </div>'''

rv = [r for r in REVIEWS if not r[4] and r[1] == 5 and len(r[2]) > 0 and len(r[3]) > 40]
rv_html = "".join(f'<figure class="rv__item"{"" if k == 0 else " hidden"} data-rv="{k}" style="margin:0;display:grid;justify-items:center;gap:26px"><blockquote class="serif h4 rv__q" style="margin:0">„{esc(r[3])}“</blockquote><figcaption class="rv__who"><span class="label">{esc(r[0])}</span><span class="label label--reg muted">{r[2]} · Google</span></figcaption></figure>' for k, r in enumerate(rv))

std_items = [(n, d) for _, _, _, _, items in STD_CATS for n, d, tag in items if tag == "in"][:6]
travel_html = "".join(f'<li><span class="h5 serif">{t["place"]}</span><span class="label label--reg muted">{t["note"]}</span><span class="label">{t["auto"]} min autem</span></li>' for t in TRAVEL)

home = f'''
<section class="hero" data-hdr="light" aria-labelledby="hero-t">
  <div class="hero__media">{img("hero", "Zástupná vizualizace patrového domu v Blatci", "100vw", eager=True)}</div>
  <div class="hero__in wrap">
    <h1 class="hero__title" id="hero-t"><span class="serif mega js-split" data-split="chars">Blatec</span><span class="script js-split" data-split="script">u&nbsp;Olomouce</span></h1>
    <div class="hero__row">
      <p class="serif h5" data-r="fade">Nový domov</p>
      <div class="hero__mid on-dark">
        <p class="label" data-r="fade">14 rodinných domů · {len(FREE)} volných · od {MINP_TXT} mil. Kč</p>
        <div class="hero__cta" data-r="fade"><a class="btn btn--solid" href="nabidka.html"><span>Vybrat volný dům</span>{ICON["arrow"]}</a><button class="btn" type="button" data-book><span>Domluvit prohlídku</span></button></div>
      </div>
      <p class="serif h5" data-r="fade">na Hané</p>
    </div>
  </div>
</section>

<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="stmt-t">
  <div class="stmt">
    <p class="label" data-r>Projekt</p>
    <h2 class="serif h4 js-split" data-split="lines" id="stmt-t">Nová ulice čtrnácti rodinných domů v&nbsp;klidné části Blatce, osm kilometrů od Olomouce</h2>
    <div class="stmt__foot">
      <p class="p p--s center" data-r>Přízemní i&nbsp;patrové domy od HP DOMY. Každý s&nbsp;vlastní zahradou a&nbsp;dvěma stáními u&nbsp;domu. Zděné, s&nbsp;tepelným čerpadlem a&nbsp;podlahovým topením.</p>
      <span data-r>{EMBLEM}</span>
    </div>
  </div>
</section>

<section class="t-cream arch-wrap" data-hdr="ink" aria-labelledby="arch-t">
  <div class="arch">
    <div class="arch__bg" aria-hidden="true"></div>
    <svg class="arch__text" viewBox="0 0 1200 420" aria-hidden="true"><path id="arc" d="M60 400 A540 380 0 0 1 1140 400" fill="none"/><text><textPath href="#arc" startOffset="50%" text-anchor="middle">Tři důvody pro Blatec</textPath></text></svg>
    <div class="arch__mid">
      <h2 class="sr" id="arch-t">Tři důvody pro Blatec</h2>
      <div class="row"><span class="label">Haná</span>{EMBLEM}<span class="label">Olomouc</span></div>
      <p class="label label--reg">Domov na roky dopředu</p>
    </div>
    <div class="reasons">
      {"".join(f'<article class="reason"><div class="reason__img" data-r>{img(i, a, "(min-width:760px) 45vw, 100vw")}</div><div class="reason__txt"><span class="reason__n" data-r>{n}</span><h3 class="serif h4" data-r>{t}</h3><p class="p" data-r>{p}</p></div></article>' for n, t, p, i, a in REASONS)}
    </div>
  </div>
</section>

<section class="quote" data-hdr="light" aria-label="Citát">
  <div class="quote__media" data-par>{img("aerial", "Zástupná vizualizace nových domů z ptačí perspektivy", "100vw")}</div>
  <div class="quote__in wrap">
    <span class="quote__mark" aria-hidden="true">“</span>
    <p class="serif h4 js-split" data-split="lines">Vlastní dům, vlastní zahrada a&nbsp;Olomouc na dosah</p>
  </div>
</section>

<section class="sec t-cream wrap" id="typy" data-hdr="ink" aria-labelledby="typy-t">
  <div class="types__head">
    <p class="script js-split" data-split="script">Vyberte si</p>
    <h2 class="serif h1 js-split" data-split="lines" id="typy-t">Dva typy domů</h2>
  </div>
  <div class="tslider" data-tslider>
    {types_html}
    <div class="tpag"><button type="button" data-tprev aria-label="Předchozí typ">{ICON["left"]}</button><span class="label" data-tcur>1</span><span class="tpag__bar"><i></i></span><span class="label">2</span><button type="button" data-tnext aria-label="Další typ">{ICON["right"]}</button></div>
  </div>
</section>

<section class="sec t-sky wrap" id="domy" data-hdr="ink" aria-labelledby="domy-t">
  <div class="types__head">
    <p class="script js-split" data-split="script">Právě teď</p>
    <h2 class="serif h1 js-split" data-split="lines" id="domy-t">{len(FREE)} volných domů</h2>
  </div>
  <div class="hl" data-hl>{"".join(hrow(h) for h in HOUSES)}</div>
  <div style="display:flex;justify-content:center;margin-top:clamp(40px,5vw,80px)" data-r><a class="btn" href="nabidka.html"><span>Situace a&nbsp;celá nabídka</span>{ICON["arrow"]}</a></div>
</section>

<section class="sec t-soil wrap" id="lokalita" data-hdr="light" aria-labelledby="lok-t">
  <div class="loc__head">
    <h2 class="serif h1 js-split" data-split="lines" id="lok-t">Olomouc</h2>
    <p class="script js-split" data-split="script">za patnáct minut</p>
  </div>
  <div class="loc__nums">
    <div data-r><span class="serif h2">15</span><span class="label">minut autem do centra</span></div>
    <div data-r><span class="serif h2">20</span><span class="label">minut vlakem z&nbsp;obce</span></div>
    <div data-r><span class="serif h2">8</span><span class="label">kilometrů do Olomouce</span></div>
  </div>
  <div class="loc__list" data-r><ul>{travel_html}</ul></div>
  <p class="label label--reg muted center" style="margin-top:28px;text-align:center">Orientační časy, před spuštěním webu je ověříme.</p>
</section>

<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="space-t">
  <div class="space__head">
    <h2 class="serif h1 js-split" data-split="lines" id="space-t">Prostor</h2>
    <p class="script js-split" data-split="script">pro život</p>
  </div>
  <div class="space__grid">
    {"".join(f'<figure data-r>{img(n, a, "(min-width:760px) 50vw, 100vw")}</figure>' for n, a in (("garden", "Terasa se zastíněním"), ("bungalow", "Přízemní dům"), ("entry", "Vstup s dřevěným obkladem"), ("street", "Ulice s novými domy")))}
  </div>
  <div class="space__list">{"".join(f'<div data-r><b>{n}</b><p class="p p--s muted">{d}</p></div>' for n, d in std_items)}</div>
</section>

<section class="sec t-sky wrap" data-hdr="ink" aria-labelledby="rv-t">
  <div class="rv" data-rv-wrap>
    <h2 class="label" id="rv-t">Hodnocení HP DOMY na Googlu · {str(GOOGLE["rating"]).replace(".", ",")} z&nbsp;5 · {GOOGLE["count"]} recenzí</h2>
    {rv_html}
    <div class="tpag" style="margin-top:0"><button type="button" data-rprev aria-label="Předchozí recenze">{ICON["left"]}</button><span class="label" data-rcur>01 / {len(rv):02d}</span><button type="button" data-rnext aria-label="Další recenze">{ICON["right"]}</button></div>
  </div>
</section>

<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="dev-t">
  <div class="stmt">
    <h2 class="serif h1 js-split" data-split="lines" id="dev-t">HP DOMY</h2>
    <p class="p center" data-r>Stavitel rodinných domů s&nbsp;dlouholetou praxí. Blatec je jeho nový projekt u&nbsp;Olomouce.</p>
  </div>
  <dl class="facts">
    <div data-r><dt class="label label--reg">Developer</dt><dd class="serif h5">HP DOMY</dd></div>
    <div data-r><dt class="label label--reg">Prodej</dt><dd class="serif h5">Impuls Reality</dd></div>
    <div data-r><dt class="label label--reg">Domů v&nbsp;projektu</dt><dd class="serif h5">14</dd></div>
    <div data-r><dt class="label label--reg">Lokalita</dt><dd class="serif h5">Blatec, okres Olomouc</dd></div>
  </dl>
</section>

<section class="sec t-soil wrap" id="prohlidka" data-hdr="light" aria-labelledby="fin-t">
  <div class="final">
    <p class="script js-split" data-split="script">Domluvte si</p>
    <h2 class="serif h1 js-split" data-split="lines" id="fin-t">Prohlídku</h2>
    <p class="p center" data-r>Prodejce vám ukáže pozemek na místě, projde s&nbsp;vámi půdorysy a&nbsp;poradí s&nbsp;financováním.</p>
    <a class="final__tel" href="tel:{TEL}" data-r>{TEL_TXT}</a>
    <div data-r><button class="btn btn--solid" type="button" data-book>Napsat prodejci</button></div>
  </div>
  {footer()}
</section>
'''
home_ld = {"@context": "https://schema.org", "@type": "Residence", "name": "Blatec – 14 rodinných domů",
           "address": {"@type": "PostalAddress", "addressLocality": "Blatec", "postalCode": "783 75", "addressCountry": "CZ"},
           "description": "Nová ulice 14 rodinných domů od HP DOMY v Blatci, 8 km od Olomouce."}
page("index.html", "Blatec · 14 rodinných domů u Olomouce | HP DOMY",
     f"Čtrnáct přízemních a patrových domů v Blatci, 8 km od Olomouce. {len(FREE)} volných, od {MINP_TXT} mil. Kč. Developer HP DOMY.",
     home, preload="hero", jsonld=home_ld)

# ======================================================================= OFFER
cnt = lambda st=None, t=None: len([h for h in HOUSES if (not st or h["status"] == st) and (not t or h["type"] == t)])
offer = f'''
<section class="t-cream wrap" data-hdr="ink" aria-labelledby="nab-t">
  <div class="phead">
    <nav class="crumbs label label--reg" aria-label="Drobečková navigace"><a class="ulink" href="index.html">Blatec</a><span aria-hidden="true">/</span><span>Nabídka domů</span></nav>
    <h1 class="serif mega js-split" data-split="chars" id="nab-t">Nabídka</h1>
    <p class="script js-split" data-split="script">domů</p>
    <p class="label" style="margin-top:clamp(20px,3vw,40px)" data-r>{len(FREE)} volných · {cnt("rezervace")} v&nbsp;rezervaci · {cnt("prodany")} prodané · od {MINP_TXT} mil. Kč</p>
    <div class="chips" role="group" aria-label="Filtr domů" data-r>
      <button type="button" data-f="all" aria-pressed="true">Všechny<sup>{len(HOUSES)}</sup></button>
      <button type="button" data-f="volny" aria-pressed="false">Volné<sup>{len(FREE)}</sup></button>
      <button type="button" data-f="prizemni" aria-pressed="false">Přízemní<sup>{cnt(t="prizemni")}</sup></button>
      <button type="button" data-f="patrovy" aria-pressed="false">Patrové<sup>{cnt(t="patrovy")}</sup></button>
    </div>
  </div>
  <div class="offer">
    <div class="offer__plan" data-r>
      {plan_svg()}
      <div class="offer__legend"><span class="st st--volny">volný</span><span class="st st--rezervace">rezervace</span><span class="st st--prodany">prodaný</span></div>
    </div>
    <div>
      <div class="hl hl--rich" data-hl data-offer>{"".join(hrow(h, rich=True) for h in HOUSES)}</div>
      <p class="label label--reg muted" style="margin-top:22px">Každý dům má 2 stání u&nbsp;domu. Situace je ilustrační.</p>
    </div>
  </div>
</section>
<section class="sec t-soil wrap" data-hdr="light" aria-labelledby="fin-t">
  <div class="final">
    <p class="script js-split" data-split="script">Domluvte si</p>
    <h2 class="serif h1 js-split" data-split="lines" id="fin-t">Prohlídku</h2>
    <a class="final__tel" href="tel:{TEL}" data-r>{TEL_TXT}</a>
    <div data-r><button class="btn btn--solid" type="button" data-book>Napsat prodejci</button></div>
  </div>
  {footer()}
</section>
'''
page("nabidka.html", "Nabídka domů · Blatec | HP DOMY", f"{len(FREE)} volných rodinných domů v Blatci. Situace, ceny a stavy všech 14 domů.", offer)

# ======================================================================= HOUSE PAGES
GARDEN_TXT = {"jih": "Zahrada míří na jih. Slunce celý den, ideální pro terasu a&nbsp;záhony.",
              "sever": "Zahrada míří na sever, terasa bude v&nbsp;létě příjemně ve stínu. Ranní a&nbsp;večerní slunce dopadá z&nbsp;boku."}
for h in HOUSES:
    hid, T = h["id"], TYPES[h["type"]]
    sold = h["status"] == "prodany"
    gal = T["gal"][:3]
    floors = PLANS[h["type"]]
    tabs = ("<div class=\"fplan__tabs\" role=\"group\" aria-label=\"Podlaží\">" + "".join(f'<button type="button" data-ftab="{k}" aria-pressed="{str(k == 0).lower()}">{f["name"]}</button>' for k, f in enumerate(floors)) + "</div>") if len(floors) > 1 else ""
    rooms = "".join(f'<ul class="fplan__rooms" data-floor-list="{k}"{"" if k == 0 else " hidden"}>' + "".join(f'<li><span class="label">{i:02d}</span><b>{r["n"]}</b><span class="label label--reg">{area(r["a"])}</span></li>' for i, r in enumerate(f["rooms"], 1)) + "</ul>" for k, f in enumerate(floors))
    prev_id, next_id = (hid - 2) % 14 + 1, hid % 14 + 1
    cta = (f'<button class="btn btn--solid" type="button" data-book data-house="{hid}">Domluvit prohlídku domu {hid}</button>' if not sold
           else f'<a class="btn btn--solid" href="nabidka.html#volne"><span>Zobrazit volné domy</span>{ICON["arrow"]}</a>')
    jsonld = {"@context": "https://schema.org", "@type": "SingleFamilyResidence", "name": f"Dům {hid} – Blatec",
              "numberOfRooms": int(h["disp"][0]), "floorSize": {"@type": "QuantitativeValue", "value": h["area"], "unitCode": "MTK"},
              "address": {"@type": "PostalAddress", "addressLocality": "Blatec", "postalCode": "783 75", "addressCountry": "CZ"}}
    if h["price"] and not sold:
        jsonld["offers"] = {"@type": "Offer", "price": h["price"], "priceCurrency": "CZK", "availability": "https://schema.org/InStock"}
    body = f'''
<section class="dhero" data-hdr="light" aria-labelledby="d-t">
  <div class="hero__media">{img(T["gal"][0], f"Zástupná vizualizace: {T['label'].lower()} dům", "100vw", eager=True)}</div>
  <div class="dhero__in wrap">
    <nav class="crumbs label label--reg" aria-label="Drobečková navigace" style="margin:0"><a class="ulink" href="index.html">Blatec</a><span aria-hidden="true">/</span><a class="ulink" href="nabidka.html">Nabídka</a><span aria-hidden="true">/</span><span>Dům {hid}</span></nav>
    <h1 class="dhero__title" id="d-t"><span class="serif mega js-split" data-split="chars">Dům {hid}</span><span class="script js-split" data-split="script">{T["label"].lower()}</span></h1>
    <dl class="dfacts" data-r>
      <div><dt class="label label--reg">Stav</dt><dd>{STATUS[h["status"]]}</dd></div>
      <div><dt class="label label--reg">Cena</dt><dd>{price(h)}</dd></div>
      <div><dt class="label label--reg">Dispozice</dt><dd>{h["disp"]}</dd></div>
      <div><dt class="label label--reg">Užitná plocha</dt><dd>{area(h["area"])}</dd></div>
      <div><dt class="label label--reg">Pozemek</dt><dd>{area(h["plot"])}</dd></div>
      <div><dt class="label label--reg">Zahrada</dt><dd>na {h["garden"]}</dd></div>
    </dl>
  </div>
</section>

<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="d-s">
  <div class="stmt" style="margin-bottom:var(--sec)">
    <p class="label" data-r>{T["label"]} dům · {T["disp"]}</p>
    <h2 class="serif h4 js-split" data-split="lines" id="d-s">{"Prostorný dům na dvou podlažích s&nbsp;vlastní zahradou" if h["type"] == "patrovy" else "Celý domov na jednom podlaží, bez jediného schodu"}</h2>
    <p class="p center" data-r>{TYPE_TXT[h["type"]]} Pozemek {area(h["plot"])}, dvě stání u&nbsp;domu.</p>
  </div>
  <div class="dgal">{"".join(f'<figure data-r>{img(g, "Zástupná vizualizace", "(min-width:760px) 55vw, 100vw")}</figure>' for g in gal)}</div>
</section>

<section class="sec t-sky wrap" data-hdr="ink" aria-labelledby="d-p">
  <div class="types__head"><h2 class="serif h1 js-split" data-split="lines" id="d-p">Půdorys</h2></div>
  <div class="fplan">
    <div class="fplan__svg" data-r>{"".join(floor_svg(f, k) for k, f in enumerate(floors))}</div>
    <div data-r>{tabs}{rooms}<p class="label label--reg muted" style="margin-top:18px">Ilustrační půdorys. Skutečný doplní HP DOMY.</p></div>
  </div>
</section>

<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="d-l">
  <div class="dloc">
    <div style="display:grid;gap:24px">
      <h2 class="serif h2 js-split" data-split="lines" id="d-l">Místo v&nbsp;ulici</h2>
      <p class="p" data-r>{GARDEN_TXT[h["garden"]]}</p>
      <p class="label label--reg muted" data-r>Dům {hid} je zvýrazněný v&nbsp;situaci. Ilustrační podklad.</p>
      <div data-r><a class="btn" href="nabidka.html"><span>Celá situace</span>{ICON["arrow"]}</a></div>
    </div>
    <div style="max-width:420px;justify-self:center;width:100%" data-r>{plan_svg(hl=hid)}</div>
  </div>
</section>

<section class="sec t-soil wrap" data-hdr="light" aria-labelledby="fin-t">
  <div class="final">
    <p class="script js-split" data-split="script">{"Domluvte si" if not sold else "Tento dům je"}</p>
    <h2 class="serif h1 js-split" data-split="lines" id="fin-t">{"Prohlídku" if not sold else "Prodaný"}</h2>
    <a class="final__tel" href="tel:{TEL}" data-r>{TEL_TXT}</a>
    <div data-r>{cta}</div>
  </div>
  <nav class="dnav" style="margin-top:var(--sec)" aria-label="Další domy">
    <a href="dum-{prev_id}.html"><span class="label">Předchozí</span><span class="serif h3">Dům {prev_id}</span></a>
    <a href="dum-{next_id}.html"><span class="label">Další</span><span class="serif h3">Dům {next_id}</span></a>
  </nav>
  {footer()}
</section>
'''
    page(f"dum-{hid}.html", f"Dům {hid} · {T['label']} {T['disp']} · Blatec | HP DOMY",
         f"Dům {hid} v Blatci: {T['label'].lower()} {T['disp']}, {re.sub('&nbsp;', ' ', area(h['area']))} užitné plochy, pozemek {h['plot']} m², {STATUS[h['status']]}.",
         body, preload=T["gal"][0], jsonld=jsonld)

print("v2 built:", len(os.listdir(OUT)), "entries")
