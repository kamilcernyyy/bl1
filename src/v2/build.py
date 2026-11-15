"""Blatec · směr B (editorial). Builds ./v2/ from the same house data as the main site.

    python3 src/v2/build.py

Data (houses, plans, reviews, travel times, standards, FAQ) is read from src/build.py,
so both design directions always show the same numbers.
Images live in v2/img (warm colour renders from tools/scene.py with LOOK=color).
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
TYPES, HOUSES, GEO, PLANS, REVIEWS, GOOGLE, TRAVEL, STD_CATS, STATUS, FAQ, GALLERY = (D[k] for k in
    ("TYPES", "HOUSES", "GEO", "PLANS", "REVIEWS", "GOOGLE", "TRAVEL", "STD_CATS", "STATUS", "FAQ", "GALLERY"))
cz_typo = D["cz_typo"]
esc = html.escape

TEL, TEL_TXT, MAIL = "+420776294498", "+420 776 294 498", "info@impulsreality.com"
FREE = [h for h in HOUSES if h["status"] == "volny"]
area = lambda v: (f"{v:.1f}".replace(".", ",") if isinstance(v, float) else str(v)) + "&nbsp;m²"
money = lambda p: f"{p:,}".replace(",", "&nbsp;") + "&nbsp;Kč"
price = lambda h: "Prodáno" if h["status"] == "prodany" else (money(h["price"]) if h["price"] else "Na dotaz")
MINP = min(h["price"] for h in HOUSES if h["price"] and h["status"] != "prodany")
MINP_TXT = f"{MINP / 1e6:.2f}".replace(".", ",").rstrip("0").rstrip(",")
cnt = lambda st=None, t=None: len([h for h in HOUSES if (not st or h["status"] == st) and (not t or h["type"] == t)])

# ---- assets
CSS = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
CSS = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
CSS = re.sub(r"\s*\n\s*", "", CSS)
CSS = re.sub(r"\s*([{};,>])\s*", r"\1", CSS).replace(";}", "}")
os.makedirs(os.path.join(OUT, "js"), exist_ok=True)
open(os.path.join(OUT, "js", "app.js"), "w", encoding="utf-8").write(open(os.path.join(HERE, "app.js"), encoding="utf-8").read())
open(os.path.join(OUT, "js", "data.js"), "w", encoding="utf-8").write(
    "window.BLATEC=" + json.dumps(dict(houses=HOUSES, geo=GEO, status=STATUS, travel=TRAVEL), ensure_ascii=False, separators=(",", ":")) + ";")

ICON = {
    "arrow": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 12.5 12.5 3.5M5 3.5h7.5V11" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>',
    "right": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h12M9 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "left": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M14 8H2M7 3 2 8l5 5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "x": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m3 3 10 10M13 3 3 13" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>',
    "plus": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2v12M2 8h12" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>',
    "zoom": '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 6V2h4M14 6V2h-4M2 10v4h4M14 10v4h-4" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>',
}
EMBLEM = ('<svg class="emblem" viewBox="0 0 40 60" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.15" stroke-linejoin="round">'
          '<path d="M20 58V14"/><path d="M20 14c-3.2-3.4-3.2-9 0-12.4 3.2 3.4 3.2 9 0 12.4z"/>'
          + "".join(f'<path d="M20 {y + 8}c-7 0-10.5-4.6-10.5-9.4 7 0 10.5 4.6 10.5 9.4z"/><path d="M20 {y + 8}c7 0 10.5-4.6 10.5-9.4-7 0-10.5 4.6-10.5 9.4z"/>' for y in (16, 27, 38))
          + '<path d="M14 58h12"/></g></svg>')

CAPTION = {"hero": "Patrový dům od ulice", "street": "Nová ulice", "garden": "Terasa a zahrada", "aerial": "Domy z ptačí perspektivy",
           "bungalow": "Přízemní dům", "entry": "Vstup s dřevěným obkladem", "hana": "Blatec a hanácká pole"}


def _src(name):
    """Prefer the warm colour renders in v2/img, fall back to the shared clay renders."""
    local = [s for s in (800, 1200, 1600, 1920) if os.path.exists(os.path.join(OUT, "img", f"{name}-{s}.webp"))]
    if local:
        return "img", local
    return "../img", [s for s in (800, 1200, 1600, 1920) if os.path.exists(os.path.join(ROOT, "img", f"{name}-{s}.webp"))]


def img(name, alt, sizes="100vw", eager=False, cls=""):
    base, have = _src(name)
    srcset = ", ".join(f"{base}/{name}-{s}.webp {s}w" for s in have)
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{base}/{name}-{have[-1]}.webp" srcset="{srcset}" sizes="{sizes}" width="1600" height="900" alt="{esc(alt)}" {load}>'


def zoom(name, group, alt=None, sizes="(min-width:760px) 50vw, 100vw", cls="", eager=False):
    """A figure that opens in the lightbox."""
    base, have = _src(name)
    cap = CAPTION.get(name, "")
    return (f'<figure class="zf {cls}" data-r><button type="button" class="zf__btn" data-zoom="{group}" data-src="{base}/{name}-{have[-1]}.webp" data-cap="{esc(cap)}" aria-label="Zvětšit: {esc(cap or (alt or ""))}">'
            f'{img(name, alt or (cap + " – zástupná vizualizace"), sizes, eager)}<span class="zf__ic">{ICON["zoom"]}</span></button></figure>')


def thumb(name):
    base = "img" if os.path.exists(os.path.join(OUT, "img", f"{name}-thumb.webp")) else "../img"
    return f"{base}/{name}-thumb.webp"


def head(title, desc, preload=None, jsonld=None):
    pre = ""
    if preload:
        base, have = _src(preload)
        pre = (f'<link rel="preload" as="image" href="{base}/{preload}-{have[-1]}.webp" imagesrcset="'
               + ", ".join(f"{base}/{preload}-{s}.webp {s}w" for s in have) + '" imagesizes="100vw" fetchpriority="high">\n')
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


def roll(t):
    return f'<span class="roll"><span>{t}</span><span aria-hidden="true">{t}</span></span>'


LOGO = '<span class="logo__n">Blatec</span><span class="logo__s">HP DOMY Development</span>'


def header():
    return f'''<header class="hdr" id="hdr">
  <a class="logo" href="index.html">{LOGO}</a>
  <div class="hdr__r">
    <a class="hdr__pick" href="nabidka.html">{roll("Vybrat<br>volný dům")}</a>
    <div class="hdr__links">
      <button type="button" data-book>{roll("Prohlídka &amp; hovor")}</button>
      <button type="button" data-menu aria-expanded="false" aria-controls="menu">{roll("Menu")}</button>
    </div>
    <button class="burger" type="button" data-menu aria-expanded="false" aria-controls="menu" aria-label="Otevřít menu"><i></i></button>
  </div>
</header>
'''


NAV = [("index.html", "Úvod"), ("o-projektu.html", "O projektu"), ("lokalita.html", "Lokalita"), ("nabidka.html", "Nabídka domů"),
       ("standardy.html", "Standardy"), ("galerie.html", "Galerie"), ("kontakt.html", "Kontakt")]


def menu():
    links = "".join(f'<a href="{u}"><span class="menu__n">{k + 1:02d}</span>{roll(t)}</a>' for k, (u, t) in enumerate(NAV))
    return f'''<nav class="menu" id="menu" aria-label="Hlavní menu" aria-hidden="true">
  <button class="menu__close" type="button" data-menu-close aria-label="Zavřít menu">{ICON["x"]}</button>
  <div class="menu__claims"><p>Postaveno, aby vydrželo</p><p>Světlo a vlastní zahrada</p><p>Klid na Hané</p></div>
  <div class="menu__nav">{links}</div>
  <div class="menu__foot">
    <div style="display:grid;gap:8px"><span class="label label--reg muted">Prodejce Pavel Čundrla · Impuls Reality</span><a class="h5 serif" href="tel:{TEL}">{TEL_TXT}</a></div>
    <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="tel:{TEL}">Zavolat</a><button class="btn btn--solid" type="button" data-book>Domluvit prohlídku</button></div>
  </div>
</nav>
'''


def form_fields(prefix="", topic=False):
    opts = "".join(f'<option value="{h["id"]}">Dům {h["id"]} · {h["label"].lower()} · {STATUS[h["status"]]}</option>' for h in HOUSES if h["status"] != "prodany")
    top = ('<fieldset class="topics"><legend class="label">S čím vám pomůžeme</legend>'
           + "".join(f'<label><input type="radio" name="topic" value="{v}"{" checked" if k == 0 else ""}><span>{t}</span></label>' for k, (v, t) in enumerate((("prohlidka", "Prohlídka"), ("cena", "Cena a dostupnost"), ("financovani", "Financování"), ("jine", "Jiný dotaz"))))
           + '</fieldset>') if topic else ""
    return f'''{top}
        <div class="grid-2"><label class="field"><span class="label">Jméno</span><input name="name" autocomplete="name" required></label>
        <label class="field"><span class="label">Telefon</span><input name="tel" type="tel" autocomplete="tel" required></label></div>
        <label class="field"><span class="label">E-mail</span><input name="email" type="email" autocomplete="email"></label>
        <label class="field"><span class="label">Dům</span><select name="house"><option value="">Zatím nevím</option>{opts}</select></label>
        <label class="field"><span class="label">Zpráva</span><textarea name="msg" rows="3" placeholder="Kdy se vám hodí prohlídka?"></textarea></label>
        <p class="p p--s muted">Ozve se vám prodejce Pavel Čundrla. Údaje použijeme jen k vyřízení dotazu.</p>'''


THANKS = f'<div class="thanks" hidden><p class="script">Děkujeme</p><p class="p">Prodejce se vám brzy ozve. Spěcháte? Volejte <a class="ulink" href="tel:{TEL}">{TEL_TXT}</a>.</p><p class="label muted">Ukázka: formulář zatím nikam neodesílá</p></div>'


def modal():
    return f'''<div class="modal" id="book" role="dialog" aria-modal="true" aria-labelledby="book-t" aria-hidden="true">
  <div class="modal__bg" data-close></div>
  <div class="modal__box t-cream">
    <button class="modal__x" type="button" data-close aria-label="Zavřít">{ICON["x"]}</button>
    <form class="bookf" novalidate>
      <div class="ttl ttl--s" style="margin-bottom:18px"><p class="script" id="book-t">Domluvte si</p><p class="serif h3">prohlídku</p></div>
      <div style="display:grid;gap:18px">{form_fields()}
        <div><button class="btn btn--solid" type="submit">Odeslat</button></div>
      </div>
    </form>
    {THANKS}
  </div>
</div>
<div class="lbx" id="lbx" role="dialog" aria-modal="true" aria-label="Zvětšená fotografie" aria-hidden="true">
  <button class="lbx__x" type="button" data-lbx-close aria-label="Zavřít">{ICON["x"]}</button>
  <figure class="lbx__fig"><img alt=""><figcaption><span class="label lbx__cap"></span><span class="label label--reg lbx__n"></span></figcaption></figure>
  <button class="lbx__nav lbx__prev" type="button" data-lbx-prev aria-label="Předchozí fotka">{ICON["left"]}</button>
  <button class="lbx__nav lbx__next" type="button" data-lbx-next aria-label="Další fotka">{ICON["right"]}</button>
</div>
'''


def footer():
    links = "".join(f'<a class="p--s" href="{u}">{t}</a>' for u, t in NAV)
    return f'''<footer class="ftr">
      <div><a class="logo" href="index.html">{LOGO}</a><p class="p p--s" style="margin-top:14px">14 rodinných domů v&nbsp;Blatci u&nbsp;Olomouce.</p></div>
      <div><span class="label">Stránky</span>{links}</div>
      <div><span class="label">Prodej</span><span class="p--s">Pavel Čundrla, Impuls Reality</span><a class="p--s ulink" style="justify-self:start" href="tel:{TEL}">{TEL_TXT}</a><a class="p--s ulink" style="justify-self:start" href="mailto:{MAIL}">{MAIL}</a></div>
      <div><span class="label">Developer</span><span class="p--s">HP DOMY s.r.o.</span><span class="p--s">I. P. Pavlova 692/143, Olomouc</span><span class="p--s muted">Vizualizace jsou ilustrační.</span></div>
      <div class="ftr__legal"><span class="label label--reg muted">© 2026 HP DOMY · Blatec (pracovní název)</span><a class="label label--reg ulink" href="../index.html">Zobrazit směr A</a></div>
    </footer>'''


def scripts():
    return '''<script src="js/gsap.min.js" defer></script>
<script src="js/ScrollTrigger.min.js" defer></script>
<script src="js/SplitText.min.js" defer></script>
<script src="js/lenis.min.js" defer></script>
<script src="js/data.js" defer></script>
<script src="js/app.js" defer></script>
</body>
</html>'''


def page(name, title, desc, body, preload=None, jsonld=None):
    cue = '<div class="cue" aria-hidden="true"><span>Scroll</span><i></i></div>\n' if name == "index.html" else ""
    out = (head(title, desc, preload, jsonld) + header() + cue + menu() + f'<main id="main">\n{body}\n</main>\n'
           + modal() + '<div class="hl-float" aria-hidden="true"><img alt=""></div>\n' + scripts())
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(cz_typo(out))


def title(script, words, tag="h2", hid=None, size="h1", rev=False, cls=""):
    """Serif heading with a script accent layered above it (outlined so it stays readable)."""
    s = f'<span class="script js-split" data-split="script">{script}</span>'
    h = f'<span class="serif {size} js-split" data-split="lines">{words}</span>'
    i = f' id="{hid}"' if hid else ""
    return f'<{tag} class="ttl{" ttl--rev" if rev else ""} {cls}"{i}>{h + s if rev else s + h}</{tag}>'


def phead(crumb, script, words, lead=None, extra=""):
    return f'''<section class="t-cream wrap" data-hdr="ink">
  <div class="phead">
    <nav class="crumbs label label--reg" aria-label="Drobečková navigace"><a class="ulink" href="index.html">Blatec</a><span aria-hidden="true">/</span><span>{crumb}</span></nav>
    <h1 class="ttl ttl--rev"><span class="serif mega js-split" data-split="chars">{words}</span><span class="script js-split" data-split="script">{script}</span></h1>
    {f'<p class="p center" style="margin-top:clamp(24px,3vw,44px)" data-r>{lead}</p>' if lead else ""}
    {extra}
  </div>
</section>'''


def final(script="Domluvte si", words="Prohlídku", text=None, cta=None, after=""):
    cta = cta or '<button class="btn btn--solid" type="button" data-book>Napsat prodejci</button>'
    return f'''<section class="sec t-soil wrap" id="prohlidka" data-hdr="light" aria-labelledby="fin-t">
  <div class="final">
    {title(script, words, hid="fin-t")}
    {f'<p class="p center" data-r>{text}</p>' if text else ""}
    <a class="final__tel" href="tel:{TEL}" data-r>{TEL_TXT}</a>
    <div data-r style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center">{cta}</div>
  </div>
  {after}
  {footer()}
</section>'''


def hrow(h, rich=False):
    sold = h["status"] == "prodany"
    th = f'<div class="hl__thumb"><img src="{thumb(h["img"])}" alt="" width="320" height="240" loading="lazy" decoding="async"></div>' if rich else ""
    base, have = _src(h["img"])
    return (f'<a class="hl__row{" is-sold" if sold else ""}" href="dum-{h["id"]}.html" data-id="{h["id"]}" data-img="{base}/{h["img"]}-800.webp" data-type="{h["type"]}" data-status="{h["status"]}">'
            f'{th}<span class="hl__name">Dům {h["id"]:02d}</span><span class="hl__type label label--reg">{h["label"]} · {h["disp"]} · {area(h["area"])}</span>'
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


def sky(script, words, label, img_name="hana", eager=False):
    """Cream page -> drifting clouds -> landscape photo, driven by scroll."""
    base, have = _src(img_name)
    return f'''<section class="sky" data-hdr="light" aria-label="{esc(label)}">
  <div class="sky__stick">
    <div class="sky__photo">{img(img_name, CAPTION.get(img_name, "") + " – zástupná vizualizace", "100vw", eager=eager)}</div>
    <div class="sky__cl sky__cl--b"><div class="sky__drift"><img src="img/cloud-b.webp" alt="" width="2400" height="1100" loading="lazy" decoding="async"><img src="img/cloud-b.webp" alt="" width="2400" height="1100" loading="lazy" decoding="async"></div></div>
    <div class="sky__cl sky__cl--a"><div class="sky__drift"><img src="img/cloud-a.webp" alt="" width="2400" height="1100" loading="lazy" decoding="async"><img src="img/cloud-a.webp" alt="" width="2400" height="1100" loading="lazy" decoding="async"></div></div>
    <div class="sky__fade" aria-hidden="true"></div>
    <div class="sky__txt wrap">
      <p class="label">{label}</p>
      <p class="ttl ttl--rev on-photo"><span class="serif mega">{words}</span><span class="script">{script}</span></p>
    </div>
  </div>
</section>'''


def zoomin(name, quote, label=None):
    """Photo that pulls you in: starts as a framed card, opens to full screen while scrolling."""
    return f'''<section class="zin t-cream" data-hdr="light" aria-label="Citát">
  <div class="zin__stick">
    <div class="zin__media">{img(name, CAPTION.get(name, "") + " – zástupná vizualizace", "100vw")}</div>
    <div class="zin__txt wrap">
      <span class="quote__mark" aria-hidden="true">“</span>
      <p class="serif h4">{quote}</p>
      {f'<p class="label">{label}</p>' if label else ""}
    </div>
  </div>
</section>'''


def hscroll(script, words, items, hid, intro=None, theme="t-cream", hdr="ink"):
    """Pinned horizontal track. items = list of (html) cards."""
    return f'''<section class="hs {theme}" data-hdr="{hdr}" aria-labelledby="{hid}">
  <div class="hs__stick">
    <div class="hs__head wrap">{title(script, words, hid=hid, size="h2")}{f'<p class="p">{intro}</p>' if intro else ""}<p class="label label--reg muted hs__hint">Rolováním se posunete do strany</p></div>
    <div class="hs__track" data-hs>{"".join(items)}</div>
    <div class="hs__bar wrap" aria-hidden="true"><i></i></div>
  </div>
</section>'''


def hcard(name, n, text=None):
    return (f'<article class="hs__card">{zoom(name, "hs", sizes="(min-width:760px) 42vw, 84vw")}'
            f'<div class="hs__cap"><span class="label">{n:02d}</span><span class="serif h5">{CAPTION.get(name, "")}</span>{f"<p class=\"p p--s muted\">{text}</p>" if text else ""}</div></article>')


# ======================================================================= HOME
REASONS = [
    ("01", "Klid obce, město na dosah", "Blatec má kolem 650 obyvatel a&nbsp;vlak do Olomouce staví přímo v&nbsp;obci. Autem jste v&nbsp;centru za 15 minut.", "street"),
    ("02", "Vlastní zahrada", "Pozemky od 529 do 728 m². Zahrada na sever, nebo na jih. Vyberete si podle toho, jak rádi žijete.", "garden"),
    ("03", "Staví HP DOMY", f"Zděná stavba, tepelné čerpadlo a&nbsp;podlahové topení. Developer s&nbsp;hodnocením {str(GOOGLE['rating']).replace('.', ',')} z&nbsp;5 na Googlu.", "entry"),
]
TYPE_TXT = {
    "patrovy": "Dvě podlaží: dole obývací pokoj s&nbsp;kuchyní a&nbsp;pracovna, nahoře ložnice a&nbsp;dva pokoje. Dost místa pro rodinu i&nbsp;hosty.",
    "prizemni": "Všechno na jednom podlaží, bez schodů. Ložnice se šatnou, dva pokoje a&nbsp;obývací pokoj s&nbsp;kuchyní.",
}


def type_slides():
    tabs, slides = "", ""
    for k, (t, T) in enumerate(TYPES.items()):
        hs = [h for h in HOUSES if h["type"] == t]
        free = [h for h in hs if h["status"] == "volny"]
        rooms = len([r for f in PLANS[t] for r in f["rooms"] if r["n"] in ("Ložnice", "Pokoj", "Pracovna")])
        tabs += (f'<button class="ttab" type="button" role="tab" id="tt-{k}" aria-controls="ts-{k}" aria-selected="{str(k == 0).lower()}" data-ttab="{k}">'
                 f'<span class="ttab__img"><img src="{thumb(T["img"])}" alt="" width="320" height="240" loading="lazy" decoding="async"></span>'
                 f'<span class="ttab__t"><span class="serif h5">{T["label"]} dům</span><span class="label label--reg">{T["disp"]} · {area(T["area"])} · {len(free)} volných</span></span>'
                 f'<span class="ttab__dot" aria-hidden="true"></span></button>')
        slides += f'''<div class="tslide{" is-on" if k == 0 else ""}" id="ts-{k}" data-slide="{k}" role="tabpanel" aria-labelledby="tt-{k}">
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
            <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn btn--solid" href="nabidka.html#{"patrove" if t == "patrovy" else "prizemni"}"><span>{T["label"]} domy v&nbsp;nabídce</span>{ICON["arrow"]}</a><a class="btn" href="dum-{free[0]["id"]}.html">Dům {free[0]["id"]}</a></div>
          </div>
        </div>
        <p class="tslide__name serif h2" aria-hidden="true">{T["label"]} dům</p>
      </div>'''
    return f'''<div class="tslider" data-tslider>
    <div class="ttabs" role="tablist" aria-label="Typ domu">{tabs}</div>
    {slides}
    <div class="tpag"><button type="button" data-tprev aria-label="Předchozí typ">{ICON["left"]}</button><span class="label" data-tcur>1</span><span class="tpag__bar"><i></i></span><span class="label">2</span><button type="button" data-tnext aria-label="Další typ">{ICON["right"]}</button></div>
  </div>'''


rv = [r for r in REVIEWS if not r[4] and r[1] == 5 and len(r[3]) > 40]


def reviews():
    items = "".join(f'<figure class="rv__item"{"" if k == 0 else " hidden"} data-rv="{k}" style="margin:0;display:grid;justify-items:center;gap:26px"><blockquote class="serif h4 rv__q" style="margin:0">„{esc(r[3])}“</blockquote><figcaption class="rv__who"><span class="label">{esc(r[0])}</span><span class="label label--reg muted">{r[2]} · Google</span></figcaption></figure>' for k, r in enumerate(rv))
    return f'''<section class="sec t-sky wrap" data-hdr="ink" aria-labelledby="rv-t">
  <div class="rv" data-rv-wrap>
    <h2 class="label" id="rv-t">Hodnocení HP DOMY na Googlu · {str(GOOGLE["rating"]).replace(".", ",")} z&nbsp;5 · {GOOGLE["count"]} recenzí</h2>
    {items}
    <div class="tpag" style="margin-top:0"><button type="button" data-rprev aria-label="Předchozí recenze">{ICON["left"]}</button><span class="label" data-rcur>01 / {len(rv):02d}</span><button type="button" data-rnext aria-label="Další recenze">{ICON["right"]}</button></div>
  </div>
</section>'''


loc_line = " <span aria-hidden=\"true\">·</span> ".join(f'<span><b>{t["place"].replace("Olomouc, hlavní nádraží", "Hlavní nádraží")}</b> {t["auto"]}&nbsp;min</span>' for t in TRAVEL)
std_items = [(n, d) for _, _, _, _, items in STD_CATS for n, d, tag in items if tag == "in"][:6]
GAL = ["hero", "street", "garden", "bungalow", "entry", "aerial", "hana"]

home = f'''
<section class="hero" data-hdr="light" aria-labelledby="hero-t">
  <div class="hero__media">{img("hero", "Zástupná vizualizace patrového domu v Blatci", "100vw", eager=True)}</div>
  <div class="hero__in wrap">
    <h1 class="hero__title ttl ttl--rev on-photo" id="hero-t"><span class="serif mega js-split" data-split="chars">Blatec</span><span class="script js-split" data-split="script">u&nbsp;Olomouce</span></h1>
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

{sky("pod širým nebem", "Na Hané", "Úrodná rovina 8 km jižně od Olomouce")}

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
      {"".join(f'<article class="reason"><div class="reason__img">{zoom(i, "reasons", sizes="(min-width:760px) 45vw, 100vw")}</div><div class="reason__txt"><span class="reason__n" data-r>{n}</span><h3 class="serif h4" data-r>{t}</h3><p class="p" data-r>{p}</p></div></article>' for n, t, p, i in REASONS)}
    </div>
  </div>
</section>

{zoomin("aerial", "Vlastní dům, vlastní zahrada a&nbsp;Olomouc na dosah", "Blatec · 14 domů · Haná")}

<section class="sec t-cream wrap" id="typy" data-hdr="ink" aria-labelledby="typy-t">
  <div class="types__head">{title("Vyberte si", "ze dvou typů domů", hid="typy-t")}<p class="label label--reg muted" style="margin-top:22px" data-r>Přepněte mezi patrovým a&nbsp;přízemním domem</p></div>
  {type_slides()}
</section>

<section class="sec t-sky wrap" id="domy" data-hdr="ink" aria-labelledby="domy-t">
  <div class="types__head">{title("Právě teď", f"{len(FREE)} volných domů", hid="domy-t")}</div>
  <div class="hl" data-hl>{"".join(hrow(h) for h in HOUSES)}</div>
  <div style="display:flex;justify-content:center;margin-top:clamp(40px,5vw,80px)" data-r><a class="btn btn--solid" href="nabidka.html"><span>Situace a&nbsp;celá nabídka</span>{ICON["arrow"]}</a></div>
</section>

<section class="sec t-soil wrap" id="lokalita" data-hdr="light" aria-labelledby="lok-t">
  <div class="loc__head">{title("za patnáct minut", "Olomouc", hid="lok-t", rev=True)}</div>
  <div class="loc__nums">
    <div data-r><span class="serif h2">15</span><span class="label">minut autem do centra</span></div>
    <div data-r><span class="serif h2">20</span><span class="label">minut vlakem z&nbsp;obce</span></div>
    <div data-r><span class="serif h2">8</span><span class="label">kilometrů do Olomouce</span></div>
  </div>
  <p class="loc__line label label--reg" data-r>Autem: {loc_line}</p>
  <div style="display:flex;justify-content:center;margin-top:36px" data-r><a class="btn" href="lokalita.html"><span>Lokalita a&nbsp;vybavenost</span>{ICON["arrow"]}</a></div>
</section>

<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="space-t">
  <div class="space__head">{title("pro život", "Prostor", hid="space-t", rev=True)}</div>
  <div class="space__grid">{"".join(zoom(n, "space") for n in ("garden", "bungalow", "entry", "street"))}</div>
  <div class="space__list">{"".join(f'<div data-r><b>{n}</b><p class="p p--s muted">{d}</p></div>' for n, d in std_items)}</div>
  <div style="display:flex;justify-content:center;margin-top:clamp(40px,5vw,70px)" data-r><a class="btn" href="standardy.html"><span>Všechny standardy</span>{ICON["arrow"]}</a></div>
</section>

{hscroll("Prohlédněte si", "Galerii", [hcard(n, k + 1) for k, n in enumerate(GAL)], "gal-t", theme="t-wheat")}

{reviews()}

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
  <div style="display:flex;justify-content:center;margin-top:clamp(40px,5vw,70px)" data-r><a class="btn" href="o-projektu.html"><span>O projektu</span>{ICON["arrow"]}</a></div>
</section>

{final(text="Prodejce vám ukáže pozemek na místě, projde s&nbsp;vámi půdorysy a&nbsp;poradí s&nbsp;financováním.")}
'''
home_ld = {"@context": "https://schema.org", "@type": "Residence", "name": "Blatec – 14 rodinných domů",
           "address": {"@type": "PostalAddress", "addressLocality": "Blatec", "postalCode": "783 75", "addressCountry": "CZ"},
           "description": "Nová ulice 14 rodinných domů od HP DOMY v Blatci, 8 km od Olomouce."}
page("index.html", "Blatec · 14 rodinných domů u Olomouce | HP DOMY",
     f"Čtrnáct přízemních a patrových domů v Blatci, 8 km od Olomouce. {len(FREE)} volných, od {MINP_TXT} mil. Kč. Developer HP DOMY.",
     home, preload="hero", jsonld=home_ld)

# ======================================================================= OFFER
offer = phead("Nabídka domů", "domů", "Nabídka", extra=f'''
    <p class="label" style="margin-top:clamp(20px,3vw,40px)" data-r>{len(FREE)} volných · {cnt("rezervace")} v&nbsp;rezervaci · {cnt("prodany")} prodané · od {MINP_TXT} mil. Kč</p>
    <div class="chips" role="group" aria-label="Filtr domů" data-r>
      <button type="button" data-f="all" aria-pressed="true">Všechny<sup>{len(HOUSES)}</sup></button>
      <button type="button" data-f="volny" aria-pressed="false">Volné<sup>{len(FREE)}</sup></button>
      <button type="button" data-f="prizemni" aria-pressed="false">Přízemní<sup>{cnt(t="prizemni")}</sup></button>
      <button type="button" data-f="patrovy" aria-pressed="false">Patrové<sup>{cnt(t="patrovy")}</sup></button>
    </div>''').replace('</section>', f'''  <div class="offer">
    <div class="offer__plan" data-r>
      {plan_svg()}
      <div class="offer__legend"><span class="st st--volny">volný</span><span class="st st--rezervace">rezervace</span><span class="st st--prodany">prodaný</span></div>
    </div>
    <div>
      <div class="hl hl--rich" data-hl data-offer>{"".join(hrow(h, rich=True) for h in HOUSES)}</div>
      <p class="label label--reg muted" style="margin-top:22px">Každý dům má 2 stání u&nbsp;domu. Situace je ilustrační.</p>
    </div>
  </div>
</section>''', 1) + final()
page("nabidka.html", "Nabídka domů · Blatec | HP DOMY", f"{len(FREE)} volných rodinných domů v Blatci. Situace, ceny a stavy všech 14 domů.", offer)

# ======================================================================= ABOUT
milestones = [("Příprava projektu", "Projektová dokumentace a povolení", "probíhá"), ("Spuštění prodeje", "Zveřejnění cen a rezervace", "připravujeme"),
              ("Zahájení výstavby", "Základy a inženýrské sítě", "termín upřesníme"), ("Hrubá stavba", "Klientské změny do této fáze", "termín upřesníme"),
              ("Předání domů", "Kolaudace a kupní smlouvy", "termín upřesníme")]
ms_cards = [f'<article class="ms{" is-now" if k == 0 else ""}"><span class="ms__n serif h2">{k + 1:02d}</span><h3 class="serif h4">{n}</h3><p class="p p--s">{d}</p><span class="st {"st--volny" if k == 0 else "st--rezervace"}">{lab}</span></article>' for k, (n, d, lab) in enumerate(milestones)]
spec_rows = [("Pozemek", f'{min(h["plot"] for h in HOUSES)}–{max(h["plot"] for h in HOUSES)} m², zahrada za domem'), ("Parkování", "2 zpevněná stání na pozemku"),
             ("Vytápění", "tepelné čerpadlo, podlahové topení v celém domě"), ("Bez plynu a komína", "dům je čistě elektrický"),
             ("Připraveno", "fotovoltaika, klimatizace, venkovní žaluzie"), ("Konstrukce", "cihelné zdivo Porotherm, železobetonový strop")]


def type_col(t):
    T = TYPES[t]; hs = [h for h in HOUSES if h["type"] == t]; free = [h for h in hs if h["status"] == "volny"]
    return f'''<article class="tcol">
      {zoom(T["img"], "types", sizes="(min-width:860px) 46vw, 100vw")}
      <div class="tcol__b"><h3 class="serif h3" data-r>{T["label"]} dům</h3>
      <dl class="kv" data-r><div><dt class="label label--reg">Dispozice</dt><dd>{T["disp"]}</dd></div><div><dt class="label label--reg">Užitná plocha</dt><dd>{area(T["area"])}</dd></div><div><dt class="label label--reg">Podlaží</dt><dd>{len(PLANS[t])}</dd></div><div><dt class="label label--reg">Volné</dt><dd>{len(free)} z&nbsp;{len(hs)}</dd></div></dl>
      <p class="p" data-r>{TYPE_TXT[t]}</p>
      <div data-r style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn btn--solid" href="nabidka.html#{"patrove" if t == "patrovy" else "prizemni"}"><span>Volné domy</span>{ICON["arrow"]}</a><a class="btn" href="dum-{free[0]["id"]}.html#pudorys">Půdorys</a></div></div>
    </article>'''


about = phead("O projektu", "v Blatci", "14 domů", "Nová ulice s&nbsp;domy ve dvou typech. Ke každému patří vlastní pozemek se zahradou a&nbsp;dvě stání u&nbsp;domu.") + f'''
{zoomin("street", "Čtrnáct domů, jedna klidná ulice a&nbsp;pole na dohled", "Blatec · nová ulice")}
<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="ab-t">
  <div class="types__head">{title("Patrový, nebo", "přízemní", hid="ab-t")}<p class="p center" style="margin-top:22px" data-r>Stejný standard, jiný počet podlaží a&nbsp;pokojů.</p></div>
  <div class="tcols">{type_col("patrovy")}{type_col("prizemni")}</div>
</section>
<section class="sec t-sky wrap" data-hdr="ink" aria-labelledby="ab-k">
  <div class="types__head">{title("Ke každému", "domu", hid="ab-k")}</div>
  <dl class="spec">{"".join(f'<div data-r><dt class="label">{k}</dt><dd class="serif h5">{v}</dd></div>' for k, v in spec_rows)}</dl>
  <div style="display:flex;justify-content:center;margin-top:clamp(40px,5vw,70px)" data-r><a class="btn" href="standardy.html"><span>Všechny standardy</span>{ICON["arrow"]}</a></div>
</section>
{hscroll("Krok za krokem", "Harmonogram", ms_cards, "ab-h", intro="Termíny zveřejníme se spuštěním prodeje.")}
<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="ab-d">
  <div class="stmt"><h2 class="serif h1 js-split" data-split="lines" id="ab-d">HP DOMY</h2><p class="p center" data-r>Developer z&nbsp;Olomouce. Předchozí projekty HP DOMY stojí v&nbsp;Olšanech a&nbsp;ve Slavoníně, můžete se na ně podívat.</p></div>
  <div class="refs">
    <a class="ref" href="https://vilynakline.cz" target="_blank" rel="noopener" data-r><span class="serif h4">Vily na Klíně</span><span class="label label--reg">9 patrových domů 5+kk · Olšany u&nbsp;Prostějova</span><span class="ref__go">{ICON["arrow"]}</span></a>
    <a class="ref" href="https://domynajihu.eu" target="_blank" rel="noopener" data-r><span class="serif h4">Domy na jihu</span><span class="label label--reg">3 patrové domy 5+kk · Olomouc-Slavonín</span><span class="ref__go">{ICON["arrow"]}</span></a>
    <a class="ref" href="https://www.hpdomy.cz" target="_blank" rel="noopener" data-r><span class="serif h4">HP DOMY s.r.o.</span><span class="label label--reg">I. P. Pavlova 692/143, Olomouc · IČ 28603494</span><span class="ref__go">{ICON["arrow"]}</span></a>
  </div>
</section>
{reviews()}
{final()}'''
page("o-projektu.html", "O projektu · Blatec | HP DOMY", "Projekt 14 rodinných domů v Blatci u Olomouce: dva typy domů, co je v ceně, harmonogram a developer HP DOMY.", about, preload=None)

# ======================================================================= LOCATION
amen = [("Vlak do Olomouce", "trať Olomouc – Nezamyslice"), ("Silnice do Olomouce", "a do Prostějova"), ("Obecní dům", "na návsi"),
        ("Kaple sv. Markéty", "dominanta návsi"), ("Sbor dobrovolných hasičů", "spolkový život obce"), ("Olomouc", "školy, nemocnice, obchody")]
pending = [("Mateřská škola", "ověřujeme"), ("Obchod s potravinami", "ověřujeme"), ("Dětské hřiště", "ověřujeme")]
modes = '<div class="modes" role="group" aria-label="Způsob dopravy"><button type="button" data-mode="auto" aria-pressed="true">Autem</button><button type="button" data-mode="vlak" aria-pressed="false">Vlakem</button><button type="button" data-mode="kolo" aria-pressed="false">Na kole</button></div>'
travel_rows = "".join(f'<li data-t="{k}"><span class="serif h4">{t["place"]}</span><span class="label label--reg muted">{t["note"]} · {t["km"]}&nbsp;km</span><span class="tv__min"><b class="serif h3" data-min>{t["auto"]}</b><span class="label">min</span></span></li>' for k, t in enumerate(TRAVEL))
loc = phead("Lokalita", "Haná", "Lokalita", "Blatec leží na Hané 8 km jižně od Olomouce. Cesta do města vede po rovině, takže dojedete i&nbsp;na kole.") + f'''
{sky("na dosah", "Olomouc", "Blatec · okres Olomouc", eager=True)}
<section class="sec t-soil wrap" data-hdr="light" aria-labelledby="lc-t">
  <div class="loc__head">{title("z Blatce", "Dojezdy", hid="lc-t", rev=True)}</div>
  <div class="tv" data-travel>
    {modes}
    <ul class="tv__list">{travel_rows}</ul>
    <p class="label label--reg muted" style="text-align:center;margin-top:24px">Orientační časy ve špičce. Před spuštěním webu je ověříme.</p>
  </div>
</section>
<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="lc-a">
  <div class="types__head">{title("V obci", "a okolí", hid="lc-a")}</div>
  <div class="amen2">{"".join(f'<div data-r><b class="serif h5">{n}</b><span class="label label--reg muted">{s}</span></div>' for n, s in amen)}{"".join(f'<div class="is-pending" data-r><b class="serif h5">{n}</b><span class="label label--reg">{s}</span></div>' for n, s in pending)}</div>
  <div style="display:flex;justify-content:center;margin-top:clamp(40px,5vw,70px)" data-r><a class="btn" href="https://www.blatec.cz/" target="_blank" rel="noopener"><span>Web obce Blatec</span>{ICON["arrow"]}</a></div>
</section>
<section class="sec t-sky wrap" data-hdr="ink" aria-labelledby="lc-h">
  <div class="split2">
    <div style="display:grid;gap:26px;align-content:center">{title("Blatec", "od roku 1131", hid="lc-h", size="h2")}
      <p class="p" data-r>Blatec má kolem 650 obyvatel a&nbsp;první písemná zmínka o&nbsp;obci pochází z&nbsp;roku 1131. Uprostřed návsi stojí kaple sv. Markéty a&nbsp;obecní dům. Obcí prochází železniční trať Olomouc – Nezamyslice a&nbsp;silnice, která ji spojuje s&nbsp;Olomoucí a&nbsp;Prostějovem.</p></div>
    {zoom("hana", "loc", sizes="(min-width:860px) 50vw, 100vw")}
  </div>
</section>
{final()}'''
page("lokalita.html", "Lokalita · Blatec u Olomouce | HP DOMY", "Blatec leží 8 km jižně od Olomouce. Dojezdy autem, vlakem a na kole, vybavenost obce.", loc)

# ======================================================================= STANDARDS
TAGS = {"in": ("V ceně", "st--volny"), "prep": ("Příprava v ceně", "st--rezervace"), "plus": ("Za příplatek", "st--plus")}
cats = ""
for k, (cid, _, name, sub, items) in enumerate(STD_CATS):
    rows = "".join(f'<li data-r><span class="serif h5">{n}</span><span class="p p--s muted">{d}</span><span class="st {TAGS[t][1]}">{TAGS[t][0]}</span></li>' for n, d, t in items)
    cats += f'''<section class="sec {"t-cream" if k % 2 == 0 else "t-sky"} wrap std" id="{cid}" data-hdr="ink" aria-labelledby="sc-{cid}">
  <div class="std__grid">
    <div class="std__head"><span class="label">{k + 1:02d} / {len(STD_CATS):02d}</span><h2 class="serif h2 js-split" data-split="lines" id="sc-{cid}">{name}</h2><p class="p" data-r>{sub}</p></div>
    <ul class="std__list">{rows}</ul>
  </div>
</section>'''
legend = "".join(f'<span class="st {c}">{t}</span>' for t, c in TAGS.values())
steps_ch = [("Konzultace", "S prodejcem projdete, co chcete změnit."), ("Nacenění", "Dostanete rozpočet změn a termín, do kdy je potvrdit."),
            ("Potvrzení", "Změny potvrdíte dodatkem ke smlouvě."), ("Realizace", "Stavba zapracuje změny v příslušné fázi."), ("Kontrola", "Při předání zkontrolujete, že je vše podle dohody.")]
std = phead("Standardy", "domů", "Standardy", "Co dostanete v&nbsp;ceně, co je připravené a&nbsp;co si můžete přiobjednat.", extra=f'<div class="chips" data-r>{legend}</div>') + f'''
{zoomin("entry", "Zděná stavba, tepelné čerpadlo a&nbsp;podlahové topení v&nbsp;celém domě", "Standard HP DOMY")}
{cats}
{hscroll("Klientské", "změny", [f'<article class="ms"><span class="ms__n serif h2">{k + 1:02d}</span><h3 class="serif h4">{n}</h3><p class="p p--s">{d}</p></article>' for k, (n, d) in enumerate(steps_ch)], "sc-z", intro="Změny je potřeba zadat dřív, než stavba dojde do příslušné fáze. Vzorky vám ukáže prodejce.", theme="t-wheat")}
{final()}'''
page("standardy.html", "Standardy domů · Blatec | HP DOMY", "Standardy rodinných domů v Blatci: konstrukce, vytápění, okna, interiér a technologie. Co je v ceně a co za příplatek.", std)

# ======================================================================= GALLERY
gtabs = [("all", "Vše"), ("ext", "Exteriér"), ("patrovy", "Patrový dům"), ("prizemni", "Přízemní dům"), ("okoli", "Okolí")]
GITEMS = GALLERY + [dict(src="hana", title="Blatec a hanácká pole", tags=["okoli"])]
gal = phead("Galerie", "z Blatce", "Galerie", "Zástupné vizualizace. Skutečné vizualizace a fotky ze stavby doplníme.", extra=
            '<div class="chips" role="group" aria-label="Filtr galerie" data-r>' + "".join(f'<button type="button" data-g="{v}" aria-pressed="{str(k == 0).lower()}">{t}</button>' for k, (v, t) in enumerate(gtabs)) + "</div>").replace(
    '</section>', '<div class="gal">' + "".join(f'<div class="gal__i" data-tags="{" ".join(g["tags"])}">{zoom(g["src"], "gal", sizes="(min-width:860px) 33vw, 100vw")}<p class="label label--reg">{g["title"]}</p></div>' for g in GITEMS) + '</div>\n</section>', 1) + final()
page("galerie.html", "Galerie · Blatec | HP DOMY", "Vizualizace rodinných domů v Blatci u Olomouce.", gal)

# ======================================================================= CONTACT
buy = [("Výběr a prohlídka", "Vyberete volný dům a prohlédnete si pozemek."), ("Rezervace", "Rezervační smlouvou si dům podržíte, v nabídce se označí jako rezervovaný."),
       ("Smlouva o smlouvě budoucí", "Stanoví cenu, termíny a platební kalendář."), ("Výstavba a změny", "Během stavby můžete zadat klientské změny."),
       ("Předání", "Po kolaudaci podepíšete kupní smlouvu a převezmete klíče.")]
faq = "".join(f'<div class="acc__i"><button type="button" class="acc__b" aria-expanded="false"><span class="serif h5">{q}</span><span class="acc__ic">{ICON["plus"]}</span></button><div class="acc__p" hidden><p class="p">{a}</p></div></div>' for q, a in FAQ)
contact = f'''<section class="t-cream wrap" data-hdr="ink">
  <div class="phead"><nav class="crumbs label label--reg" aria-label="Drobečková navigace"><a class="ulink" href="index.html">Blatec</a><span aria-hidden="true">/</span><span>Kontakt</span></nav>
    <h1 class="ttl ttl--rev"><span class="serif mega js-split" data-split="chars">Kontakt</span><span class="script js-split" data-split="script">prohlídka</span></h1></div>
  <div class="ct">
    <div class="ct__people">
      <div class="person" data-r><span class="label label--reg">Výhradní prodejce · Impuls Reality</span><span class="serif h3">Pavel Čundrla</span><a class="serif h4" href="tel:{TEL}">{TEL_TXT}</a><a class="ulink p" style="justify-self:start" href="mailto:{MAIL}">{MAIL}</a></div>
      <div class="person" data-r><span class="label label--reg">Developer</span><span class="serif h4">HP DOMY s.r.o.</span><span class="p">I. P. Pavlova 692/143, 783 01 Olomouc</span><a class="ulink p" style="justify-self:start" href="https://mapy.cz/zakladni?q=I.%20P.%20Pavlova%20692%2F143%20Olomouc" target="_blank" rel="noopener">Mapa</a></div>
    </div>
    <div class="ct__form t-sky" data-r>
      <form class="bookf" novalidate><div style="display:grid;gap:18px">{form_fields(topic=True)}<div><button class="btn btn--solid" type="submit">Odeslat dotaz</button></div></div></form>
      {THANKS}
    </div>
  </div>
</section>
{hscroll("Postup", "koupě", [f'<article class="ms"><span class="ms__n serif h2">{k + 1:02d}</span><h3 class="serif h4">{n}</h3><p class="p p--s">{d}</p></article>' for k, (n, d) in enumerate(buy)], "ct-b", intro="Obvyklý postup u novostavby. Podmínky upřesní prodejce.", theme="t-wheat")}
<section class="sec t-cream wrap" data-hdr="ink" aria-labelledby="ct-f">
  <div class="types__head">{title("Časté", "dotazy", hid="ct-f")}</div>
  <div class="acc">{faq}</div>
</section>
{reviews()}
<section class="sec t-soil wrap" data-hdr="light">{footer()}</section>'''
contact = contact.replace('<section class="sec t-soil wrap" data-hdr="light"><footer class="ftr">', '<section class="t-soil wrap" style="padding-bottom:40px" data-hdr="light"><footer class="ftr" style="margin-top:0">')
page("kontakt.html", "Kontakt · Blatec | HP DOMY", "Domluvte si prohlídku rodinného domu v Blatci. Prodejce Pavel Čundrla, Impuls Reality, +420 776 294 498.", contact)

# ======================================================================= HOUSE PAGES
GARDEN_TXT = {"jih": "Zahrada míří na jih. Slunce celý den, ideální pro terasu a&nbsp;záhony.",
              "sever": "Zahrada míří na sever, terasa bude v&nbsp;létě příjemně ve stínu. Ranní a&nbsp;večerní slunce dopadá z&nbsp;boku."}
for h in HOUSES:
    hid, T = h["id"], TYPES[h["type"]]
    sold = h["status"] == "prodany"
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
    gal_names = T["gal"] + ["garden", "hana"]
    gal_names = list(dict.fromkeys(gal_names))
    body = f'''
<section class="dhero" data-hdr="light" aria-labelledby="d-t">
  <div class="hero__media">{img(T["gal"][0], f"Zástupná vizualizace: {T['label'].lower()} dům", "100vw", eager=True)}</div>
  <div class="dhero__in wrap">
    <nav class="crumbs label label--reg" aria-label="Drobečková navigace" style="margin:0"><a class="ulink" href="index.html">Blatec</a><span aria-hidden="true">/</span><a class="ulink" href="nabidka.html">Nabídka</a><span aria-hidden="true">/</span><span>Dům {hid}</span></nav>
    <h1 class="dhero__title ttl ttl--rev on-photo" id="d-t"><span class="serif mega js-split" data-split="chars">Dům {hid}</span><span class="script js-split" data-split="script">{T["label"].lower()}</span></h1>
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
  <div class="stmt">
    <p class="label" data-r>{T["label"]} dům · {T["disp"]}</p>
    <h2 class="serif h4 js-split" data-split="lines" id="d-s">{"Prostorný dům na dvou podlažích s&nbsp;vlastní zahradou" if h["type"] == "patrovy" else "Celý domov na jednom podlaží, bez jediného schodu"}</h2>
    <p class="p center" data-r>{TYPE_TXT[h["type"]]} Pozemek {area(h["plot"])}, dvě stání u&nbsp;domu.</p>
  </div>
</section>

{hscroll("Dům " + str(hid), "v obrazech", [hcard(n, k + 1) for k, n in enumerate(gal_names)], "d-g", theme="t-cream")}

<section class="sec t-sky wrap" id="pudorys" data-hdr="ink" aria-labelledby="d-p">
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
    <div class="dloc__plan" data-r>{plan_svg(hl=hid)}</div>
  </div>
</section>

{final("Domluvte si" if not sold else "Tento dům je", "Prohlídku" if not sold else "Prodaný", cta=cta, after=f"""<nav class="dnav" style="margin-top:var(--sec)" aria-label="Další domy">
    <a href="dum-{prev_id}.html"><span class="label">Předchozí</span><span class="serif h3">Dům {prev_id}</span></a>
    <a href="dum-{next_id}.html"><span class="label">Další</span><span class="serif h3">Dům {next_id}</span></a>
  </nav>""")}
'''
    page(f"dum-{hid}.html", f"Dům {hid} · {T['label']} {T['disp']} · Blatec | HP DOMY",
         f"Dům {hid} v Blatci: {T['label'].lower()} {T['disp']}, {re.sub('&nbsp;', ' ', area(h['area']))} užitné plochy, pozemek {h['plot']} m², {STATUS[h['status']]}.",
         body, preload=T["gal"][0], jsonld=jsonld)

print("v2 built:", sorted(f for f in os.listdir(OUT) if f.endswith(".html")).__len__(), "pages")
