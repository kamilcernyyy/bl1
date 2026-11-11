"""Static site generator for the Blatec (HP DOMY) website.

    python3 src/build.py            -> builds the deployable site into the repo root
    python3 src/build.py artifact   -> builds a self-contained preview into ./_artifact

Everything shared (header, bubble menu, footer, data, CSS, JS) lives here or in src/,
so every page stays consistent. House data is the single source of truth for the
one-pager, the offer page and all 14 house pages.
"""
import json, os, re, shutil, sys, html

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
FLAVOR = sys.argv[1] if len(sys.argv) > 1 else "repo"
OUT = ROOT if FLAVOR == "repo" else os.path.join(ROOT, "_artifact")
os.makedirs(OUT, exist_ok=True)
read = lambda p: open(os.path.join(SRC, p), encoding="utf-8").read()
esc = html.escape

# ------------------------------------------------------------------ data
TYPES = {
    "patrovy": dict(label="Patrový", disp="5+kk", area=142.6, img="entry", gal=["hero", "entry", "garden", "street"]),
    "prizemni": dict(label="Přízemní", disp="4+kk", area=118.4, img="bungalow", gal=["bungalow", "aerial", "street"]),
}
STATUS = {"volny": "volný", "rezervace": "rezervace", "prodany": "prodaný"}
RAW = [
    (1, "patrovy", 612, 9890000, "prodany"), (2, "patrovy", 548, 9490000, "volny"), (3, "prizemni", 701, 8990000, "rezervace"),
    (4, "prizemni", 655, 8790000, "volny"), (5, "patrovy", 532, 9390000, "prodany"), (6, "patrovy", 529, None, "volny"),
    (7, "prizemni", 640, None, "volny"), (8, "patrovy", 590, 9690000, "volny"), (9, "prizemni", 684, 8990000, "volny"),
    (10, "patrovy", 541, 9490000, "rezervace"), (11, "patrovy", 538, 9490000, "volny"), (12, "prizemni", 662, None, "volny"),
    (13, "patrovy", 575, None, "volny"), (14, "prizemni", 728, 9190000, "volny"),
]
GEO = {}
x = 60
for i, w in enumerate([118, 112, 128, 124, 110, 112, 126]):
    GEO[i + 1] = dict(x=x, y=54, w=w, h=196, north=True); x += w + 6
x = 60
for i, w in enumerate([124, 110, 112, 120, 116, 118, 132]):
    GEO[i + 8] = dict(x=x, y=318, w=w, h=196, north=False); x += w + 6
HOUSES = []
for hid, t, plot, price, st in RAW:
    T = TYPES[t]
    HOUSES.append(dict(id=hid, type=t, plot=plot, price=price, status=st, label=T["label"], disp=T["disp"],
                       area=T["area"], img=T["img"], parking="2 stání u domu",
                       garden="sever" if GEO[hid]["north"] else "jih"))
GALLERY = [
    dict(src="hero", title="Patrový dům od ulice", tags=["ext", "patrovy"]),
    dict(src="street", title="Ulice s novými domy", tags=["ext", "okoli"]),
    dict(src="garden", title="Terasa se zastíněním", tags=["ext", "patrovy"]),
    dict(src="aerial", title="Pohled z výšky", tags=["ext", "okoli"]),
    dict(src="bungalow", title="Přízemní dům", tags=["ext", "prizemni"]),
    dict(src="entry", title="Vstup s dřevěným obkladem", tags=["ext", "patrovy"]),
]
TITLES = {g["src"]: g["title"] for g in GALLERY}
PLANS = {
    "prizemni": [dict(name="Přízemí", w=140, h=90, rooms=[
        dict(n="Obývací pokoj s kuchyní", a=44.6, r=[0, 0, 64, 56]), dict(n="Zádveří", a=4.6, r=[0, 56, 24, 34]),
        dict(n="Technická místnost", a=5.2, r=[24, 56, 20, 34]), dict(n="Spíž", a=2.4, r=[44, 56, 20, 16]),
        dict(n="WC", a=1.8, r=[44, 72, 20, 18]), dict(n="Chodba", a=9.8, r=[64, 0, 16, 58]),
        dict(n="Koupelna", a=7.6, r=[64, 58, 16, 32]), dict(n="Ložnice", a=14.6, r=[80, 0, 40, 44]),
        dict(n="Šatna", a=4.4, r=[120, 0, 20, 44]), dict(n="Pokoj", a=11.8, r=[80, 44, 30, 46]),
        dict(n="Pokoj", a=11.6, r=[110, 44, 30, 46])])],
    "patrovy": [
        dict(name="Přízemí", w=115, h=90, rooms=[
            dict(n="Obývací pokoj s kuchyní", a=42.8, r=[0, 0, 70, 52]), dict(n="Pracovna", a=11.4, r=[70, 0, 45, 40]),
            dict(n="Spíž", a=2.6, r=[70, 40, 18, 12]), dict(n="Zádveří", a=5.2, r=[0, 52, 26, 38]),
            dict(n="WC", a=1.8, r=[26, 52, 14, 18]), dict(n="Technická místnost", a=5.6, r=[40, 52, 30, 18]),
            dict(n="Koupelna", a=4.6, r=[26, 70, 44, 20]),
            dict(n="Schodiště a chodba", a=7.4, pts=[[88, 40], [115, 40], [115, 90], [70, 90], [70, 52], [88, 52]], c=[96, 70])]),
        dict(name="Patro", w=90, h=86, rooms=[
            dict(n="Ložnice", a=15.2, r=[0, 0, 42, 40]), dict(n="Šatna", a=4.6, r=[0, 40, 16, 22]),
            dict(n="Koupelna", a=8.0, r=[16, 40, 26, 46]), dict(n="WC", a=2.0, r=[0, 62, 16, 24]),
            dict(n="Chodba", a=6.8, r=[42, 0, 14, 86]), dict(n="Pokoj", a=12.4, r=[56, 0, 34, 43]),
            dict(n="Pokoj", a=12.2, r=[56, 43, 34, 43])]),
    ],
}
STD_SHORT = [
    ["s-brick", "Zděná stavba", "Cihelné zdivo Porotherm a masivní železobetonový strop. Dům, který dobře drží teplo i ticho.", 0],
    ["s-heat", "Tepelné čerpadlo a podlahové topení", "Tepelné čerpadlo vzduch–voda napojené na teplovodní podlahové vytápění v celém domě.", 1],
    ["s-window", "Okna s izolačním trojsklem", "Plastová vícekomorová okna s izolačním trojsklem a kvalitním kováním.", 0],
    ["s-blind", "Příprava pro venkovní žaluzie", "Kastlíky integrované do fasády, žaluzie lze doplnit kdykoli později.", 0],
    ["s-sun", "Příprava pro fotovoltaiku", "Střecha i rozvody jsou připravené na fotovoltaickou elektrárnu.", 2],
    ["s-snow", "Příprava pro klimatizaci", "Rozvody pro klimatizaci v obytných místnostech.", 1],
    ["s-floor", "Podlahy a koupelny", "Prémiové vinylové podlahy, velkoformátové obklady a dlažby v koupelnách.", 1],
    ["s-door", "Bezfalcové dveře 210 cm", "Vnitřní bezfalcové dveře ve výšce 2,1 m, které opticky zvyšují místnosti.", 0],
]
STD_CATS = [
    ("konstrukce", "s-brick", "Konstrukce", "Na čem dům stojí a z čeho je postavený.", [
        ("Cihelné zdivo Porotherm", "Obvodové i vnitřní nosné zdi z keramických bloků. Dobře akumulují teplo a tlumí hluk.", "in"),
        ("Železobetonový strop", "Masivní stropní deska, která nevrže a odděluje patra i zvukově.", "in"),
        ("Plochá střecha", "Jednoduchý tvar bez podkroví, připravený na umístění fotovoltaiky.", "in")]),
    ("energie", "s-heat", "Vytápění a energie", "Jak dům topí a kolik bude stát provoz.", [
        ("Tepelné čerpadlo vzduch–voda", "Hlavní zdroj tepla i teplé vody. Bez plynové přípojky a komína.", "in"),
        ("Podlahové topení v celém domě", "Teplovodní podlahové vytápění ve všech místnostech, bez radiátorů na stěnách.", "in"),
        ("Příprava pro fotovoltaiku", "Rozvody a místo pro střídač. Panely lze doplnit hned, nebo později.", "prep"),
        ("Fotovoltaická elektrárna", "Instalace panelů a střídače na klíč, včetně případné baterie.", "plus")]),
    ("okna", "s-window", "Okna a stínění", "Světlo, výhled a ochrana před horkem.", [
        ("Plastová okna s izolačním trojsklem", "Vícekomorové profily a kvalitní kování, tiché a úsporné.", "in"),
        ("Příprava pro venkovní žaluzie", "Kastlíky schované ve fasádě, žaluzie se do nich dají kdykoli doplnit.", "prep"),
        ("Venkovní žaluzie", "Motorické žaluzie, které v létě udrží dům chladný.", "plus")]),
    ("interier", "s-floor", "Interiér a koupelny", "Co uvidíte a čeho se dotknete každý den.", [
        ("Vinylové podlahy", "Prémiové vinylové podlahy v obytných místnostech, odolné a tiché.", "in"),
        ("Velkoformátové obklady a dlažby", "Moderní velké formáty v koupelnách a na WC, méně spár.", "in"),
        ("Bezfalcové dveře 210 cm", "Vnitřní dveře se skrytými panty, vyšší než běžné. Místnosti působí vzdušněji.", "in")]),
    ("technologie", "s-snow", "Technologie", "Komfort, který lze doplnit.", [
        ("Příprava pro klimatizaci", "Rozvody v obytných místnostech připravené pro vnitřní jednotky.", "prep"),
        ("Klimatizace", "Dodávka a montáž jednotek podle vašeho výběru.", "plus"),
        ("Příprava pro úpravnu vody", "Místo a přípojky v technické místnosti.", "prep"),
        ("Úpravna vody", "Změkčovač nebo filtrace dodaná a zapojená na klíč.", "plus")]),
]
TAGS = {"in": ("tag--in", "V ceně"), "prep": ("tag--prep", "Příprava v ceně"), "plus": ("tag--plus", "Za příplatek")}
FAQ = [
    ["Jak probíhá rezervace domu?", "Vyberete si volný dům a domluvíte se s prodejcem. Po podpisu rezervační smlouvy dům v tabulce označíme jako rezervovaný a připravíme smlouvu o smlouvě budoucí."],
    ["Kdy budou domy dokončené?", "Projekt je před zahájením výstavby. Harmonogram zveřejníme se spuštěním prodeje a budeme ho tu průběžně aktualizovat."],
    ["Mohu si upravit dispozici nebo vybavení?", "Klientské změny řešíme individuálně podle fáze výstavby. Na konkrétní úpravy se zeptejte prodejce."],
    ["Pomůžete mi s financováním?", "Prodejce vám doporučí hypotečního specialistu a pomůže s podklady pro banku."],
    ["Je cena konečná, včetně DPH?", "Uvedené ceny jsou včetně DPH. Příplatky za klientské změny a nadstandardy domluvíte před jejich zadáním do výroby."],
    ["Co když dům ještě nemá cenu?", "U domů s cenou „Na dotaz“ cenu sdělí prodejce. Zveřejníme ji se spuštěním prodeje."],
]

# Google reviews of HP DOMY, copied verbatim from the Google profile (state 11. 11. 2026).
# Texts cut off on Google ("… Více") stay cut off here, never completed.
GOOGLE = dict(rating=4.6, count=31, dist={5: 24, 4: 4, 3: 2, 2: 0, 1: 1},
              url="https://www.google.com/search?q=HP+DOMY+Olomouc+recenze")
REVIEWS = [
    ("Hana H.", 5, "před 6 lety", "S firmou HP Domy mám dobrou zkušenost, konkrétně Olomoucká pobočka. Chválím především profesionální přístup, rychlost papírování, vše vysvětlí, poradí, případné", True),
    ("Veronika J. R.", 5, "před 6 lety", "Chtěli bychom z celého <3 poděkovat týmu HP domy, konkrétně tedy pobočce Olomouc, za perfektní jednání od začátku až po předání, veškerá komunikace byla", True),
    ("Romana M.", 5, "před 3 lety", "S firmou HP DOMY máme pozitivní zkušenost při stavbě našeho domu.Měli jsme i svůj stavební dozor, který nenašel žádné závažné vady či pochybení. Materiál je", True),
    ("Lada L.", 5, "před rokem", "HP-Domy (Bradlecká pobočka) nám stavěly zděný dům (HP-137 + klientské úpravy) na klíč v okolí Mladé Boleslavi. Z naší strany velká spokojenost, jak s kvalitou a", True),
    ("Radovan S.", 5, "před 6 lety", "V domě HP90 se dobře bydlí, po ročním bydlení není nutné nic reklamovat, což je myslím dobrá známka. S firmou velmi dobrá zkušenost, doporučuji.", False),
    ("Petr J.", 5, "před 6 lety", "Stavěl jsem s nimi v roce 2015. Mohu vřele doporučit. Stavba probíhala dle harmonogramu. Vybral jsem si je po delším porovnávání jednotlivých dodavatelů, kde", True),
    ("Pavel R.", 5, "před 6 lety", "Dům byl postaven v roce 2012. S odstupem času mohu jen konstatovat, že vybrat firmu HP domy bylo velmi dobré rozhodnutí. Oceňuji osobní přístup majitele firmy a", True),
    ("Vera D.", 5, "před rokem", "Skvělá zkušenost s HP Domy!", True),
    ("Jitka H.", 5, "před 6 lety", "Za nás maximální spokojenost - rychlost, pečlivost, výborná komunikace. Můžeme jen doporučit, děkujeme HP domy za krásný domeček.", False),
    ("Vlastimil S.", 5, "před 6 lety", "Neskutečně profesionální přístup, poctivě a kvalitně odvedený kus práce. Za nás maximální spokojenost a mohu všem doporučit všemi deseti :-)", False),
    ("Ctibor T.", 4, "před 6 lety", "Máme pozitivní zkušenost s výstavbou od HP domy. Komunikace byla dobrá, pomohli s úpravou projektu na atypickou dřevostavbu. Realizace vcelku bez problémů až na", True),
    ("František N.", 4, "před 6 lety", "korektní jednání a poctivá stavařina...", False),
    ("Lenka K.", 3, "před 2 lety", "S firmou HP domy máme dobrou zkušenost ohledně výstavby domu HP 90 která", True),
    ("Roman S.", 5, "před 5 lety", "Lepší firma na stavbu domu (dřevostavba) asi neexistuje. Obešeli jsme několik firem než jsme zvolili firmu HPdomy. A jednání této firmy bylo nad očekávání.", True),
    ("Petr Š.", 5, "před 2 lety", "Mohu jen doporučit!", False),
]

TRAVEL = [
    dict(place="Centrum Olomouce", note="práce, úřady, kultura", km=8, auto=15, vlak=20, kolo=30),
    dict(place="Fakultní nemocnice Olomouc", note="nejbližší velká nemocnice", km=9, auto=15, vlak=30, kolo=35),
    dict(place="Olomouc, hlavní nádraží", note="rychlíky do Prahy a Brna", km=9, auto=15, vlak=12, kolo=35),
    dict(place="Prostějov", note="druhé nejbližší město", km=14, auto=20, vlak=15, kolo=50),
    dict(place="Dálnice D46", note="směr Prostějov a Brno", km=6, auto=10, vlak=None, kolo=None),
]
ICONS = [["a-rail", "Vlak"], ["a-road", "Silnice"], ["a-hall", "Obecní dům"], ["a-chapel", "Kaple"], ["a-fire", "Hasiči"], ["a-city", "Město"], ["a-tree", "Příroda"],
         ["s-brick", "Zdivo"], ["s-heat", "Tepelné čerpadlo"], ["s-window", "Okna"], ["s-blind", "Žaluzie"], ["s-sun", "Fotovoltaika"], ["s-snow", "Klimatizace"],
         ["s-floor", "Podlahy"], ["s-door", "Dveře"], ["s-water", "Úpravna vody"], ["s-car", "Parkování"], ["s-plan", "Dispozice"], ["s-area", "Plocha"]]
DATA = dict(status=STATUS, houses=HOUSES, geo=GEO, gallery=GALLERY, plans=PLANS, stdShort=STD_SHORT, faq=FAQ, travel=TRAVEL, icons=ICONS)


# ------------------------------------------------------------------ Google reviews component
G_MARK = ('<img src="img/google-g.svg" width="18" height="18" alt="">' if os.path.exists(os.path.join(ROOT, "img", "google-g.svg"))
          else '<svg aria-hidden="true"><use href="#i-star"/></svg>')
def stars(n, cls="stars"):
    return f'<span class="{cls}" role="img" aria-label="{n} z 5 hvězdiček">' + "".join(f'<svg class="{"on" if i < round(n) else ""}" aria-hidden="true"><use href="#i-star"/></svg>' for i in range(5)) + "</span>"
rating_txt = f'{GOOGLE["rating"]:.1f}'.replace(".", ",")

def rating_button(cls="btn btn--ghost on-dark", href="#recenze"):
    return f'<a class="{cls} rating-btn" href="{href}"><span class="g-mark">{G_MARK}</span><b class="tnum">{rating_txt}</b>{stars(GOOGLE["rating"])}<span class="rating-btn__n">{GOOGLE["count"]} recenzí na Google</span></a>'

def review_card(r):
    name, n, when, text, cut = r
    initials = "".join(w[0] for w in name.replace(".", "").split()[:2]).upper()
    body = esc(text) + ("…" if cut else "")
    return (f'<article class="rvc"><div class="rvc__top">{stars(n)}<span class="rvc__src">Google</span></div>'
            f'<blockquote class="rvc__txt"><p>{body}</p></blockquote>'
            f'<footer class="rvc__who"><span class="rvc__av" aria-hidden="true">{initials}</span><span><b>{esc(name)}</b><small>{when}</small></span>'
            + (f'<a class="rvc__more" href="{GOOGLE["url"]}" target="_blank" rel="noopener">Celá recenze</a>' if cut else "")
            + '</footer></article>')

def reviews(variant="full", title="Co o HP DOMY říkají majitelé domů", count=None, sid=None):
    items = REVIEWS if count is None else REVIEWS[:count]
    total = GOOGLE["count"]
    bars = "".join(f'<li><span>{k}</span><svg aria-hidden="true"><use href="#i-star"/></svg><i><b style="width:{GOOGLE["dist"][k] / total * 100:.1f}%"></b></i><span class="tnum">{GOOGLE["dist"][k]}</span></li>' for k in (5, 4, 3, 2, 1))
    summary = f'''<div class="rv__sum">
      <div class="rv__score"><b class="tnum">{rating_txt}</b><div>{stars(GOOGLE["rating"])}<span>{total} recenzí na Google</span></div></div>
      {"<ul class='rv__dist' aria-label='Rozložení hodnocení'>" + bars + "</ul>" if variant == "full" else ""}
      <a class="btn btn--ghost btn--sm" href="{GOOGLE["url"]}" target="_blank" rel="noopener"><span class="g-mark g-mark--sm">{G_MARK}</span>Všechny recenze</a>
    </div>'''
    nav = '<div class="rv__nav"><button class="rv__btn" data-rv="prev" aria-label="Předchozí recenze"><svg><use href="#i-left"/></svg></button><span class="rv__prog" aria-hidden="true"><i></i></span><button class="rv__btn" data-rv="next" aria-label="Další recenze"><svg><use href="#i-right"/></svg></button></div>'
    head = (f'<div class="sub-head"><h2 class="h2">{title}</h2>'
            '<p class="lead">Hodnocení firmy HP DOMY na Google od lidí, kterým už postavila dům.</p></div>') if variant != "inline" else ""
    return f'''<div class="rv rv--{variant}"{f' id="{sid}"' if sid else ""}>
  {head}
  <div class="rv__grid">
    {summary}
    <div class="rv__slider" data-slider>
      <div class="rv__track" tabindex="0" role="region" aria-label="Recenze, posouvejte do stran">{"".join(review_card(r) for r in items)}</div>
      {nav}
    </div>
  </div>
  <p class="rv__note">Recenze převzaté z Google beze změn, u zkrácených pokračuje text na Google. Jména zkrácena na iniciálu příjmení.</p>
</div>'''

fmt = lambda n: f"{n:,.0f}".replace(",", "\u00a0")
area = lambda a: (f"{a:.1f}".replace(".", ",") if a % 1 else f"{a:.0f}") + "\u00a0m²"
price_txt = lambda h: fmt(h["price"]) + "\u00a0Kč" if h["price"] else "Na dotaz"
free = [h for h in HOUSES if h["status"] == "volny"]


# ------------------------------------------------------------------ Czech typography
_ONE = re.compile(r'(?<![0-9A-Za-zÀ-ž])([vVkKsSzZoOuUaAiI])[ \t\n]+(?=\S)')
_UNIT = re.compile(r'(\d)[ \t]+(km|m²|m|Kč|min|%|let|lety|obyvatel|ks|fotky|fotek|domů|domy|dům|m²)(?=[^0-9A-Za-zÀ-ž]|$)')
_THOUS = re.compile(r'(\d)[ ](\d{3})(?!\d)')
def cz_typo(html_text):
    """Non-breaking spaces after one-letter words and between numbers and units (text nodes only)."""
    parts = re.split(r'(<[^>]+>)', html_text)
    skip = False
    for i, p in enumerate(parts):
        if p.startswith('<'):
            t = p[1:].split()[0].lower() if len(p) > 2 else ''
            if t in ('script', 'style'): skip = True
            elif t in ('/script', '/style'): skip = False
            continue
        if skip or not p.strip():
            continue
        p = _ONE.sub(lambda m: m.group(1) + '\u00a0', p)
        for _ in range(3): p = _THOUS.sub('\\1\u00a0\\2', p)
        p = _UNIT.sub('\\1\u00a0\\2', p)
        parts[i] = p
    return ''.join(parts)

# ------------------------------------------------------------------ partials
NAV = [("o-projektu", "O projektu"), ("lokalita", "Lokalita"), ("nabidka", "Nabídka domů"),
       ("standardy", "Standardy"), ("galerie", "Galerie"), ("kontakt", "Kontakt")]
SPRITE = read("sprite.svg")
CSS = read("base.css") + "\n" + read("pages.css")
CSS_MIN = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
CSS_MIN = re.sub(r"\s*\n\s*", "", CSS_MIN)
CSS_MIN = re.sub(r"\s*([{};,])\s*", r"\1", CSS_MIN).replace(";}", "}")
JS = read("site.js")
GSAP_V = "3.12.5"

FONT_FACES = ""
if FLAVOR == "repo":
    LATIN = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
    LATEXT = "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF"
    for fam, slug, w in [("Michroma", "michroma", 400), ("Inter", "inter", 400), ("Inter", "inter", 500), ("Inter", "inter", 600), ("Encode Sans Expanded", "encode-sans-expanded", 300)]:
        for sub, rng in (("latin", LATIN), ("latin-ext", LATEXT)):
            FONT_FACES += f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url(fonts/{slug}-{sub}-{w}-normal.woff2) format('woff2');unicode-range:{rng}}}\n"

FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23161616'/%3E%3Cpath d='M14 46V30h20v16zM26 30V18h24v28H34' fill='none' stroke='%23fff' stroke-width='3.2'/%3E%3C/svg%3E"


def head(title, desc, preload_img=None, jsonld=None, main=False):
    if FLAVOR == "repo":
        assets = ('<link rel="preload" as="font" type="font/woff2" href="fonts/michroma-latin-400-normal.woff2" crossorigin>\n'
                  '<link rel="preload" as="font" type="font/woff2" href="fonts/inter-latin-400-normal.woff2" crossorigin>\n'
                  '<link rel="icon" type="image/svg+xml" href="favicon.svg">\n'
                  '<link rel="stylesheet" href="assets/site.css">\n'
                  f'<style>{FONT_FACES}</style>\n')
    else:
        assets = (f'<link rel="icon" type="image/svg+xml" href="{FAVICON}">\n'
                  '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                  '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Encode+Sans+Expanded:wght@300;400&family=Inter:wght@400;500;600&family=Michroma&display=swap">\n'
                  f'<style>\n{CSS}\n</style>\n')
    if preload_img == "hero":
        pre = '<link rel="preload" as="image" href="img/hero-1200.webp" imagesrcset="img/hero-800.webp 800w, img/hero-1200.webp 1200w, img/hero-1920.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
    elif preload_img:
        pre = f'<link rel="preload" as="image" href="img/{preload_img}-800.webp" imagesrcset="img/{preload_img}-800.webp 800w, img/{preload_img}-1600.webp 1600w" imagesizes="(min-width:860px) 66vw, 100vw" fetchpriority="high">\n'
    else:
        pre = ""
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n' if jsonld else ""
    meta = (f"<title>{esc(title)}</title>\n"
            + ('<meta name="claude:viewport-fit-sides" content="cover">\n' if FLAVOR != "repo" else "")
            + f'<meta name="description" content="{esc(desc)}">\n<meta name="theme-color" content="#ffffff">\n'
            f'<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">'
            '<meta property="og:image" content="img/og-1200x630.jpg"><meta name="twitter:card" content="summary_large_image">\n')
    if FLAVOR != "repo" and main:
        return meta + pre + assets + ld
    return ('<!doctype html>\n<html lang="cs">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + meta + pre + assets + ld + "</head>\n<body>\n")


def scripts(main=False):
    if FLAVOR == "repo":
        s = ('<script src="js/gsap.min.js" defer></script>\n<script src="js/ScrollTrigger.min.js" defer></script>\n'
             '<script src="assets/data.js" defer></script>\n<script src="assets/site.js" defer></script>\n')
    else:
        s = (f'<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/{GSAP_V}/gsap.min.js" defer></script>\n'
             f'<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/{GSAP_V}/ScrollTrigger.min.js" defer></script>\n'
             f'<script>window.BLATEC={json.dumps(DATA, ensure_ascii=False)};</script>\n'
             f'<script>document.addEventListener("DOMContentLoaded",function(){{\n{JS}\n}});</script>\n')
    return s + ("" if (FLAVOR != "repo" and main) else "</body>\n</html>\n")


def header(active, hero=False):
    links = "\n".join(f'      <a href="{p}.html"{" aria-current=\"page\"" if p == active else ""}>{n}</a>' for p, n in NAV)
    mlinks = "\n".join(f'    <li><a href="{p}.html"{" aria-current=\"page\"" if p == active else ""}><small>{i + 1:02d}</small>{n}</a></li>' for i, (p, n) in enumerate(NAV))
    return f'''<header class="hdr {"hdr--hero" if hero else "hdr--light"}" id="hdr">
  <div class="wrap hdr__in">
    <a class="logo" href="index.html" aria-label="Blatec HP DOMY DEVELOPMENT, úvodní stránka">
      <span class="logo__name">Blatec</span>
      <span class="logo__sig">HP DOMY DEVELOPMENT</span>
    </a>
    <nav class="nav" aria-label="Hlavní menu">
{links}
    </nav>
    <div class="hdr__right">
      <a class="hdr__fav" href="nabidka.html#oblibene" aria-label="Uložené domy" hidden><svg aria-hidden="true"><use href="#i-heart"/></svg><span class="fav-n tnum">0</span></a>
      <a class="btn {"btn--light" if hero else ""} btn--sm hdr__cta" href="nabidka.html#volne">Volné domy <span class="cnt-free tnum"></span></a>
      <a class="btn btn--sm hdr__mcta" href="nabidka.html#volne">Volné <span class="cnt-free tnum"></span></a>
      <button class="burger" id="burger" aria-expanded="false" aria-controls="menu" aria-label="Otevřít menu"><span></span></button>
    </div>
  </div>
</header>
<div class="menu" id="menu" aria-hidden="true">
  <ol>
{mlinks}
  </ol>
  <div class="menu__foot">
    <span>Prodejce: <b>+420 776 294 498</b></span>
    <a class="btn btn--light btn--sm" href="nabidka.html#volne">Volné domy <span class="cnt-free tnum"></span></a>
  </div>
</div>
'''


FOOTER = f'''<footer class="ftr">
  <div class="wrap">
    <div class="ftr__grid">
      <div class="ftr__brand">
        <a class="logo" href="index.html"><span class="logo__name">Blatec</span><span class="logo__sig">HP DOMY DEVELOPMENT</span></a>
        <p style="max-width:34ch">14 rodinných domů v Blatci u Olomouce.</p>
        <div class="social"><a href="#" aria-label="Instagram HP DOMY"><svg><use href="#i-ig"/></svg></a><a href="#" aria-label="Facebook HP DOMY"><svg><use href="#i-fb"/></svg></a></div>
      </div>
      <div><h2 class="ftr-h">Projekt</h2><ul>{"".join(f'<li><a href="{p}.html">{n}</a></li>' for p, n in NAV)}</ul></div>
      <div><h2 class="ftr-h">Další projekty HP DOMY</h2><ul><li><a href="https://vilynakline.cz" target="_blank" rel="noopener">Vily na Klíně</a></li><li><a href="https://domynajihu.eu" target="_blank" rel="noopener">Domy na jihu</a></li><li><a href="https://www.hpdomy.cz" target="_blank" rel="noopener">Všechny projekty na hpdomy.cz</a></li></ul></div>
      <div><h2 class="ftr-h">Developer</h2><p><span class="hpd">HP DOMY</span><br>HP DOMY s.r.o.<br>I. P. Pavlova 692/143<br>783 01 Olomouc<br>IČ: 28603494</p></div>
    </div>
    <div class="ftr__legal">
      <span>Spisová značka C 44281 vedená u Krajského soudu v Ostravě</span>
      <span style="display:flex;gap:18px;flex-wrap:wrap"><a href="#" data-gdpr>Ochrana osobních údajů</a><a href="index.html#komponenty">Design systém návrhu</a><span>© 2026 HP DOMY s.r.o.</span></span>
    </div>
  </div>
</footer>
'''

DRAWER = '''<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-labelledby="dr-title" tabindex="-1">
  <div class="drawer__head"><span class="drawer__label">Rychlý náhled</span><button class="drawer__close" id="dr-close" aria-label="Zavřít náhled domu"><svg><use href="#i-close"/></svg></button></div>
  <div class="drawer__body" id="dr-body"></div>
  <div class="drawer__actions">
    <a class="btn btn--ghost" id="dr-detail" href="#">Celý detail domu</a>
    <button class="btn" id="dr-interest" type="button">Mám zájem <span class="ic"><svg><use href="#i-arrow"/></svg></span></button>
  </div>
</aside>
'''
LIGHTBOX = '''<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Galerie">
  <div class="lb__bar"><span class="lb__cap" id="lb-cap"></span><button class="lb__btn" id="lb-close" aria-label="Zavřít galerii"><svg><use href="#i-close"/></svg></button></div>
  <div class="lb__stage" id="lb-stage"><img id="lb-img" alt=""></div>
  <div class="lb__nav"><button class="lb__btn" id="lb-prev" aria-label="Předchozí"><svg><use href="#i-left"/></svg></button><span class="tnum" id="lb-count" style="align-self:center;min-width:56px;text-align:center"></span><button class="lb__btn" id="lb-next" aria-label="Další"><svg><use href="#i-right"/></svg></button></div>
  <div class="lb__thumbs" id="lb-thumbs"></div>
</div>
'''
TOAST = '<div class="toast" id="toast" role="status" aria-live="polite"></div>\n'

PERSON = '''<div class="person">
  <div class="person__av" aria-hidden="true">PČ</div>
  <div>
    <small>Výhradní prodejce · Impuls Reality</small>
    <b>Pavel Čundrla</b>
    <div class="person__lines">
      <span><a href="tel:+420776294498" class="tnum">+420 776 294 498</a><button class="copy" data-copy="+420 776 294 498">Kopírovat</button></span>
      <span><a href="mailto:info@impulsreality.com">info@impulsreality.com</a><button class="copy" data-copy="info@impulsreality.com">Kopírovat</button></span>
    </div>
  </div>
</div>'''


def crumbs(*items):
    parts = ['<a href="index.html">Blatec</a>']
    for href, name in items:
        parts.append('<span aria-hidden="true">/</span>')
        parts.append(f'<a href="{href}">{name}</a>' if href else f'<span aria-current="page">{name}</span>')
    return f'<nav class="crumbs" aria-label="Drobečková navigace" data-page-in>{"".join(parts)}</nav>'


def cta_band(title="Chcete se podívat na pozemek?", text="Prodejce vám ukáže situaci na místě, projde s vámi půdorysy a odpoví na otázky k financování."):
    return f'''<section class="sub-sec" style="padding-top:0"><div class="wrap">
  <div class="ctaband" data-reveal>
    <div><h2 class="h2">{title}</h2><p>{text}</p>
      <div class="ctaband__seller"><span class="person__av" aria-hidden="true">PČ</span><span>Pavel Čundrla · <span class="tnum">+420 776 294 498</span></span></div></div>
    <div class="ctaband__act"><a class="btn btn--light" href="kontakt.html">Domluvit prohlídku <span class="ic"><svg><use href="#i-arrow"/></svg></span></a><a class="btn btn--ghost on-dark" href="nabidka.html#volne">Volné domy</a></div>
  </div></div></section>'''


def next_page(slug, label):
    return f'''<section class="sub-sec" style="padding-top:0"><div class="wrap"><a class="nextp" href="{slug}.html" data-reveal><div><small>Pokračovat</small><span class="h2">{label}</span></div><span class="ic"><svg><use href="#i-arrow"/></svg></span></a></div></section>'''


def img(src, alt, sizes="100vw", eager=False, w=1600):
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    srcset = "img/hero-800.webp 800w, img/hero-1200.webp 1200w, img/hero-1920.webp 1920w" if src == "hero" else f"img/{src}-800.webp 800w, img/{src}-1600.webp 1600w"
    return (f'<img src="img/{src}-{"1200" if src == "hero" else "800"}.webp" srcset="{srcset}" '
            f'sizes="{sizes}" width="1600" height="900" alt="{esc(alt)}" {load}>')


def page(slug, title, desc, body, active=None, preload=None, jsonld=None, extra="", main=False, hero=False):
    fab = '' if slug.startswith("dum-") else CALL_FAB
    out = head(title, desc, preload, jsonld, main) + SPRITE + header(active or slug, hero) + body + FOOTER + extra + fab + TOAST + scripts(main)
    out = cz_typo(out)
    fn = "index.html" if slug == "index" else f"{slug}.html"
    open(os.path.join(OUT, fn), "w", encoding="utf-8").write(out)
    return fn



# ------------------------------------------------------------------ call FAB + watchdog
CALL_FAB = ('<a class="callfab" href="tel:+420776294498" aria-label="Zavolat prodejci, +420 776 294 498">'
            '<svg aria-hidden="true"><use href="#i-phone"/></svg><span>Zavolat</span></a>\n')
WD_TOPICS = [("prodej", "Spuštění prodeje a ceny"), ("dum", "Uvolnění rezervovaného domu"), ("stavba", "Novinky ze stavby")]

def watchdog(preset, title, text, house=None, compact=False):
    chips = "".join(f'<button type="button" class="chip" data-wd-topic="{k}" aria-pressed="{str(k in preset).lower()}">{n if not (house and k == "dum") else f"Uvolnění domu {house}"}</button>' for k, n in WD_TOPICS)
    return f'''<form class="wd{" wd--compact" if compact else ""}" id="hlidaci-pes" novalidate data-wd{f' data-house="{house}"' if house else ""}>
  <div class="wd__head"><span class="wd__ico" aria-hidden="true"><svg><use href="#i-bell"/></svg></span><div><h2 class="h3">{title}</h2><p>{text}</p></div></div>
  <div class="wd__body">
    <div class="wd__chips" role="group" aria-label="Co chcete hlídat">{chips}</div>
    <div class="wd__row">
      <div class="field"><label class="sr" for="wd-email">E-mail</label><input class="input" id="wd-email" type="email" autocomplete="email" placeholder="váš@email.cz" required><span class="err"><svg><use href="#i-alert"/></svg>Zadejte e-mail ve tvaru jmeno@domena.cz.</span></div>
      <button class="btn" type="submit">Hlídat <span class="ic"><svg><use href="#i-arrow"/></svg></span></button>
    </div>
    <label class="consent wd__consent"><input type="checkbox" id="wd-consent" required><span>Souhlasím se zasíláním upozornění k projektu Blatec. Odhlásit se můžete jedním klikem v každém e-mailu.</span></label>
  </div>
  <div class="wd__done" role="status" aria-live="polite"><span class="ok"><svg><use href="#i-check"/></svg></span><div><b>Hlídáme za vás</b><p id="wd-done-msg"></p></div></div>
</form>'''

# ------------------------------------------------------------------ index (one-pager)
idx_main = read("pages/index.main.html")
more = lambda href, label: f'      <div class="sec-more"><a class="btn btn--ghost" href="{href}">{label} <svg style="width:14px;height:14px"><use href="#i-arrow"/></svg></a></div>\n'
for marker, href, label in [("  <!-- 3 · LOKALITA -->", "o-projektu.html", "Více o projektu"),
                            ("  <!-- přechodový moment -->", "lokalita.html", "Více o lokalitě"),
                            ("  <!-- 5 · STANDARDY -->", "nabidka.html", "Celá nabídka a porovnání domů"),
                            ("  <!-- 6 · GALERIE -->", "standardy.html", "Všechny standardy"),
                            ("  <!-- FAQ (navíc oproti zadání) -->", "galerie.html", "Celá galerie")]:
    i = idx_main.index(marker)
    j = idx_main.rindex("    </div>\n  </section>", 0, i)
    idx_main = idx_main[:j] + more(href, label) + idx_main[j:]
idx_main = idx_main.replace('<th scope="col">Karta domu</th>', '<th scope="col">Detail</th>')
idx_main = idx_main.replace('<a class="scroll-cue" href="#projekt"><i></i>Posunout dolů</a>', rating_button())
idx_main = idx_main.replace("  <!-- FAQ (navíc oproti zadání) -->",
    f'  <!-- RECENZE -->\n  <section class="sec" id="recenze" style="padding-top:0"><div class="wrap">{reviews("full")}</div></section>\n\n  <!-- FAQ (navíc oproti zadání) -->')
idx_after = read("pages/index.after.html")
idx_after = re.sub(r'<!-- KARTA DOMU \(drawer\) -->.*?</aside>\n', DRAWER, idx_after, flags=re.S)
idx_after = re.sub(r'<!-- LIGHTBOX -->.*?</div>\n</div>\n', LIGHTBOX, idx_after, flags=re.S)
idx_after = idx_after.replace('<div class="toast" id="toast" role="status" aria-live="polite"></div>\n', "")
page("index", "Blatec · 14 rodinných domů u Olomouce | HP DOMY",
     "14 rodinných domů v Blatci, 8 km od Olomouce. Přízemní i patrové domy s parkováním u domu. Projekt HP DOMY DEVELOPMENT.",
     idx_main, active="", preload="hero", hero=True, extra=idx_after, main=True)

# ------------------------------------------------------------------ O projektu
def type_card(t):
    T = TYPES[t]; hs = [h for h in HOUSES if h["type"] == t]
    prices = [h["price"] for h in hs if h["price"] and h["status"] != "prodany"]
    plots = [h["plot"] for h in hs]
    nfree = len([h for h in hs if h["status"] == "volny"])
    ideal = {"patrovy": "Pro rodiny, které chtějí oddělit ložnice od denního provozu. Pět pokojů a pracovna v přízemí.",
             "prizemni": "Pro bydlení bez schodů, ať už s malými dětmi, nebo na celý život. Všechno na jednom podlaží."}[t]
    anchor = "patrove" if t == "patrovy" else "prizemni"
    return f'''<article class="tcard" data-reveal>
  <div class="tcard__img">{img(T["img"], "Zástupná vizualizace – " + T["label"].lower() + " dům", "(min-width:860px) 50vw, 100vw")}</div>
  <div class="tcard__body">
    <div class="tcard__row"><h3 class="h3" style="font-size:clamp(20px,2vw,26px)">{T["label"]} dům</h3><span class="badge badge--volny">{nfree} volné z {len(hs)}</span></div>
    <p class="tcard__ideal">{ideal}</p>
    <dl class="kv">
      <div><dt>Dispozice</dt><dd>{T["disp"]}</dd></div><div><dt>Užitná plocha</dt><dd>{area(T["area"])}</dd></div>
      <div><dt>Pozemky</dt><dd>{min(plots)}–{max(plots)} m²</dd></div><div><dt>Cena od</dt><dd>{fmt(min(prices)) + " Kč" if prices else "Na dotaz"}</dd></div>
      <div><dt>Podlaží</dt><dd>{"2" if t == "patrovy" else "1"}</dd></div><div><dt>Parkování</dt><dd>2 stání u domu</dd></div>
    </dl>
    <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="nabidka.html#{anchor}">{T["label"]} domy v nabídce <span class="ic"><svg><use href="#i-arrow"/></svg></span></a><a class="btn btn--ghost" href="dum-{next(h["id"] for h in hs if h["status"] == "volny")}.html#pudorys">Půdorys</a></div>
  </div>
</article>'''

milestones = [("Příprava projektu", "Projektová dokumentace a povolení", "now", "probíhá"),
              ("Spuštění prodeje", "Zveřejnění cen a rezervace", "", "připravujeme"),
              ("Zahájení výstavby", "Základy a inženýrské sítě", "", "termín upřesníme"),
              ("Hrubá stavba", "Klientské změny do této fáze", "", "termín upřesníme"),
              ("Předání domů", "Kolaudace a kupní smlouvy", "", "termín upřesníme")]
tl = "".join(f'<li class="{"is-now" if s == "now" else ""}"><b>{n}</b><span>{d}</span><em>{lab}</em></li>' for n, d, s, lab in milestones)
body = f'''<main class="page">
  <div class="wrap">
    {crumbs((None, "O projektu"))}
    <div class="phero phero--split">
      <div style="display:grid;gap:20px"><h1 class="h1" data-page-in>Čtrnáct domů pro klidné bydlení u Olomouce</h1><p class="lead" data-page-in>Nová ulice v Blatci s rodinnými domy ve dvou typech. Každý dům má vlastní pozemek se zahradou a dvě parkovací stání přímo u domu.</p></div>
      <div class="phero__aside" data-page-in><div class="facts"><span class="fact"><b>14</b> domů</span><span class="fact"><b class="cnt-free-n">–</b> volných</span><span class="fact">od <b data-min-price>–</b></span><span class="fact"><svg><use href="#i-pin"/></svg>8 km od Olomouce</span></div></div>
    </div>
    <figure class="pfig" data-reveal-img>{img("street", "Zástupná vizualizace ulice s novými domy v Blatci", eager=True)}</figure>
  </div>
  <section class="sub-sec"><div class="wrap">
    <div class="sub-head"><h2 class="h2">Vyberte si, jak chcete bydlet</h2><p class="lead">Oba typy mají stejný standard, liší se počtem podlaží a pokojů.</p></div>
    <div class="tcomp">{type_card("patrovy")}{type_card("prizemni")}</div>
  </div></section>
  <section class="sub-sec sub-sec--tint"><div class="wrap">
    <div class="sub-head"><h2 class="h2">Co dostanete v ceně</h2></div>
    <div class="grid-4" data-stagger>
      <div class="tile"><svg class="ti"><use href="#s-area"/></svg><h3>Vlastní pozemek</h3><p>Pozemky od {min(h["plot"] for h in HOUSES)} do {max(h["plot"] for h in HOUSES)} m² se zahradou za domem.</p></div>
      <div class="tile"><svg class="ti"><use href="#s-car"/></svg><h3>Parkování u domu</h3><p>Dvě zpevněná stání na vlastním pozemku, bez garáže.</p></div>
      <div class="tile"><svg class="ti"><use href="#s-heat"/></svg><h3>Tepelné čerpadlo</h3><p>Podlahové topení v celém domě, bez plynu a komína.</p></div>
      <div class="tile"><svg class="ti"><use href="#s-sun"/></svg><h3>Připraveno na FVE</h3><p>Rozvody pro fotovoltaiku, klimatizaci a venkovní žaluzie.</p></div>
    </div>
    <div class="more-link"><a class="link" href="standardy.html">Všechny standardy <svg><use href="#i-arrow"/></svg></a></div>
  </div></section>
  <section class="sub-sec"><div class="wrap">
    <div class="sub-head"><h2 class="h2">Kde je projekt teď</h2><p class="lead">Termíny doplníme se spuštěním prodeje a budeme je tu průběžně aktualizovat.</p></div>
    <ol class="tl">{tl}</ol>
  </div></section>
  <section class="sub-sec sub-sec--tint"><div class="wrap">
    <div class="sub-head"><h2 class="h2">HP DOMY, developer z Olomouce</h2><p class="lead">Rodinné domy staví na Olomoucku. Blatec navazuje na jejich předchozí projekty, které můžete navštívit.</p></div>
    <div class="grid-3" data-stagger>
      <a class="ref" href="https://vilynakline.cz" target="_blank" rel="noopener"><b>Vily na Klíně</b><span>9 patrových domů 5+kk, Olšany u Prostějova</span><small>vilynakline.cz <svg><use href="#i-arrow"/></svg></small></a>
      <a class="ref" href="https://domynajihu.eu" target="_blank" rel="noopener"><b>Domy na jihu</b><span>3 patrové domy 5+kk, Olomouc-Slavonín</span><small>domynajihu.eu <svg><use href="#i-arrow"/></svg></small></a>
      <a class="ref" href="https://www.hpdomy.cz" target="_blank" rel="noopener"><b>HP DOMY s.r.o.</b><span>I. P. Pavlova 692/143, Olomouc · IČ 28603494</span><small>hpdomy.cz <svg><use href="#i-arrow"/></svg></small></a>
    </div>
    <div style="margin-top:clamp(36px,5vw,56px)">{reviews("inline", count=10)}</div>
  </div></section>
  {cta_band()}
  {next_page("lokalita", "Lokalita")}
</main>
'''
page("o-projektu", "O projektu · Blatec | HP DOMY", "Projekt 14 rodinných domů v Blatci u Olomouce: dva typy domů, co je v ceně, harmonogram a developer HP DOMY.", body, preload="street")

# ------------------------------------------------------------------ Lokalita
amen = [("a-rail", "Vlak do Olomouce", "trať Olomouc – Nezamyslice"), ("a-road", "Silnice do Olomouce", "a do Prostějova"),
        ("a-hall", "Obecní dům", "na návsi"), ("a-chapel", "Kaple sv. Markéty", "dominanta návsi"),
        ("a-fire", "Sbor dobrovolných hasičů", "spolkový život obce"), ("a-city", "Olomouc", "školy, nemocnice, obchody")]
pending = [("Mateřská škola", "ověřujeme"), ("Obchod s potravinami", "ověřujeme"), ("Dětské hřiště", "ověřujeme")]
amen_html = "".join(f'<div class="amen__item"><svg><use href="#{i}"/></svg><b>{n}<small>{s}</small></b></div>' for i, n, s in amen)
amen_html += "".join(f'<div class="amen__item is-pending"><svg><use href="#i-info"/></svg><b>{n}<small>{s}</small></b></div>' for n, s in pending)
map_svg = read("pages/index.main.html")
map_svg = map_svg[map_svg.index('<div class="map"'):map_svg.index('<div class="amen">')]
map_svg = map_svg[:map_svg.rindex("</div>")]  # strip the closing of .loc
body = f'''<main class="page">
  <div class="wrap">
    {crumbs((None, "Lokalita"))}
    <div class="phero phero--split">
      <div style="display:grid;gap:20px"><h1 class="h1" data-page-in>Venkovský klid, Olomouc za 15 minut</h1><p class="lead" data-page-in>Blatec leží na Hané asi 8 km jižně od Olomouce. Do města dojedete autem, vlakem i na kole po rovině.</p></div>
      <div class="phero__aside" data-page-in><div class="facts"><span class="fact"><svg><use href="#a-city"/></svg><b>8 km</b> do centra</span><span class="fact"><svg><use href="#a-rail"/></svg>vlak v obci</span><span class="fact">cca <b>650</b> obyvatel</span></div></div>
    </div>
  </div>
  <section class="sub-sec" style="padding-top:0"><div class="wrap">
    <div class="loc">
      <div class="loc__text">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap"><h2 class="h3" style="font-size:clamp(20px,2vw,26px)">Jak daleko to mám</h2>
          <div class="seg" role="group" aria-label="Způsob dopravy"><button data-mode="auto" aria-pressed="true"><svg><use href="#s-car"/></svg>Auto</button><button data-mode="vlak" aria-pressed="false"><svg><use href="#a-rail"/></svg>Vlak</button><button data-mode="kolo" aria-pressed="false"><svg><use href="#a-road"/></svg>Kolo</button></div></div>
        <ul class="travel" id="travel" aria-live="polite"></ul>
        <span class="placeholder-note"><svg><use href="#i-info"/></svg>Orientační časy ve špičce. Před spuštěním webu je ověříme.</span>
      </div>
      {map_svg}
    </div>
  </div></section>
  <section class="sub-sec sub-sec--tint"><div class="wrap">
    <div class="sub-head"><h2 class="h2">Co najdete v Blatci</h2><p class="lead">Ukazujeme jen služby, které jsme ověřili. Další doplníme po potvrzení s obcí.</p></div>
    <div class="amen__grid" style="grid-template-columns:repeat(auto-fill,minmax(170px,1fr))">{amen_html}</div>
    <div class="more-link"><a class="link" href="https://www.blatec.cz/" target="_blank" rel="noopener">Web obce Blatec <svg><use href="#i-arrow"/></svg></a></div>
  </div></section>
  <section class="sub-sec"><div class="wrap">
    <div class="grid-2" style="align-items:center">
      <div class="sub-head" style="margin:0"><h2 class="h2">Malá obec s dlouhou historií</h2>
        <p style="color:var(--stone-600)">Blatec žije kolem 650 obyvatel a první písemná zmínka o obci pochází z roku 1131. Uprostřed návsi stojí kaple sv. Markéty a obecní dům. Obcí prochází železniční trať Olomouc – Nezamyslice a silnice, která ji spojuje s Olomoucí a Prostějovem.</p>
        <p style="color:var(--stone-600)">Nové domy vzniknou v klidné části obce s vlastní příjezdovou ulicí, takže kolem nebude projíždět tranzitní doprava.</p></div>
      <figure class="pfig" style="aspect-ratio:4/3" data-reveal-img>{img("aerial", "Zástupná vizualizace nových domů z ptačí perspektivy", "(min-width:860px) 50vw, 100vw")}</figure>
    </div>
  </div></section>
  {cta_band("Přijeďte se podívat na místo", "Prodejce vám ukáže pozemky přímo v Blatci a projde s vámi, kde přesně bude stát váš dům.")}
  {next_page("nabidka", "Nabídka domů")}
</main>
'''
page("lokalita", "Lokalita · Blatec u Olomouce | HP DOMY", "Blatec leží 8 km jižně od Olomouce. Dojezdové časy autem, vlakem a na kole, vybavenost obce a mapa.", body)

# ------------------------------------------------------------------ Nabídka
offer_src = read("pages/index.main.html")
offer = offer_src[offer_src.index('<div class="offer-top">'):offer_src.index('<!-- 5 · STANDARDY -->')]
offer = offer[:offer.rindex("    </div>\n  </section>")]
offer = offer.replace('<th scope="col">Karta domu</th>', '<th scope="col">Detail</th>')
offer = offer.replace(' data-limit="5"', '')
offer = offer.replace('<thead><tr>\n', '<thead><tr>\n                <th scope="col" class="cmp-cell"><span class="sr">Porovnat</span></th>\n')
offer = offer.replace('<button class="chip" data-f="volny" aria-pressed="false">Volné <span class="cnt" data-cnt="volny"></span></button>',
                      '<button class="chip" data-f="volny" aria-pressed="false">Volné <span class="cnt" data-cnt="volny"></span></button>\n          <button class="chip" data-f="rezervace" aria-pressed="false">Rezervace <span class="cnt" data-cnt="rezervace"></span></button>')
body = f'''<main class="page" data-compare>
  <div class="wrap">
    {crumbs((None, "Nabídka domů"))}
    <div class="phero phero--split" style="padding-bottom:28px">
      <div style="display:grid;gap:20px"><h1 class="h1" data-page-in>Najděte svůj dům v Blatci</h1><p class="lead" data-page-in>Vyberte pozemek v situaci, nebo si domy seřaďte v tabulce. Až tři domy můžete porovnat vedle sebe.</p></div>
      <div class="ostats" data-page-in>
        <div class="ostat ostat--free"><b data-cnt="volny">–</b><span>volných domů</span></div>
        <div class="ostat"><b data-cnt="rezervace">–</b><span>v rezervaci</span></div>
        <div class="ostat"><b data-cnt="prodany">–</b><span>prodaných</span></div>
        <div class="ostat"><b style="font-size:20px" data-min-price>–</b><span>nejnižší cena</span></div>
      </div>
    </div>
    {offer}
  </div>
  <section class="sub-sec" style="padding-bottom:0"><div class="wrap">{watchdog(["prodej", "dum"], "Hlídací pes", "Nechte nám e-mail a dáme vám vědět, až zveřejníme ceny, nebo když se uvolní rezervovaný dům.")}</div></section>
  <section class="sub-sec" style="padding-bottom:0"><div class="wrap">
    <div class="sub-head"><h2 class="h2">Na co se při výběru dívat</h2></div>
    <div class="grid-3" data-stagger>
      <div class="tile"><svg class="ti"><use href="#s-area"/></svg><h3>Velikost pozemku</h3><p>Pozemky se liší až o {max(h["plot"] for h in HOUSES) - min(h["plot"] for h in HOUSES)} m². Větší zahrada znamená víc místa, ale i víc údržby.</p></div>
      <div class="tile"><svg class="ti"><use href="#s-sun"/></svg><h3>Orientace zahrady</h3><p>Domy 8–14 mají zahradu na jih, domy 1–7 na sever. Detail domu ukazuje orientaci přesně.</p></div>
      <div class="tile"><svg class="ti"><use href="#s-plan"/></svg><h3>Typ domu</h3><p>Patrový 5+kk pro větší rodiny, přízemní 4+kk pro bydlení bez schodů.</p></div>
    </div>
  </div></section>
  <section class="sub-sec"><div class="wrap">{reviews("compact", title="Proč stavět s HP DOMY", count=8)}</div></section>
  {cta_band("Nevíte, který dům vybrat?", "Prodejce s vámi projde rozdíly mezi domy a doporučí ty, které odpovídají vašim představám.")}
  {next_page("standardy", "Standardy")}
</main>
<div class="tray" id="tray" role="region" aria-label="Porovnání domů"><span class="tray__txt">Porovnat</span><div class="tray__chips" id="tray-chips"></div><button class="tray__clear" id="tray-clear" type="button">Zrušit</button><button class="btn btn--light btn--sm" id="tray-go" type="button" disabled>Porovnat <span class="ic" style="width:28px;height:28px"><svg><use href="#i-arrow"/></svg></span></button></div>
<div class="modal" id="cmp-modal" role="dialog" aria-modal="true" aria-labelledby="cmp-h"><div class="modal__box"><div class="modal__head"><h2 class="h3" id="cmp-h">Porovnání domů</h2><button class="drawer__close" id="cmp-close" aria-label="Zavřít porovnání"><svg><use href="#i-close"/></svg></button></div><div id="cmp-body"></div></div></div>
'''
page("nabidka", "Nabídka domů · Blatec | HP DOMY", f"{len(free)} volných rodinných domů v Blatci. Situace, ceny, stavy a porovnání domů.", body, extra=DRAWER)

# ------------------------------------------------------------------ Standardy
cats_nav = "".join(f'<a href="#{c[0]}">{c[2]}</a>' for c in STD_CATS)
cats_html = ""
for slug, ico, name, sub, items in STD_CATS:
    lis = "".join(f'<li><b>{n}</b><span class="tag {TAGS[k][0]}">{TAGS[k][1]}</span><p>{d}</p></li>' for n, d, k in items)
    cats_html += f'<section class="std-cat" id="{slug}"><div class="std-cat__head"><svg><use href="#{ico}"/></svg><h2 class="h2">{name}</h2><p style="color:var(--stone-600)">{sub}</p></div><ul class="std-list" data-stagger>{lis}</ul></section>'
legend = "".join(f'<span class="tag {c}">{t}</span>' for c, t in TAGS.values())
body = f'''<main class="page">
  <div class="wrap">
    {crumbs((None, "Standardy"))}
    <div class="phero phero--split">
      <div style="display:grid;gap:20px"><h1 class="h1" data-page-in>Co dostanete v ceně domu</h1><p class="lead" data-page-in>Přehled podle oblastí. U každé položky vidíte, jestli je v ceně, připravená pro pozdější doplnění, nebo za příplatek.</p></div>
      <div class="phero__aside" data-page-in><div class="legend-tags">{legend}</div><div style="display:flex;gap:10px;flex-wrap:wrap"><button class="btn" data-pdf="standardy">Standardy v PDF <span class="ic"><svg><use href="#i-down"/></svg></span></button></div></div>
    </div>
    <nav class="subnav" aria-label="Oblasti standardů" style="top:calc(84px + env(safe-area-inset-top,0px));margin:0 0 8px">{cats_nav}<a href="#zmeny">Klientské změny</a></nav>
    {cats_html}
  </div>
  <section class="sub-sec sub-sec--tint" id="zmeny" style="scroll-margin-top:150px"><div class="wrap">
    <div class="sub-head"><h2 class="h2">Dům si můžete přizpůsobit</h2><p class="lead">Změny je potřeba zadat včas, dokud stavba nedošla do příslušné fáze. Obvyklý postup:</p></div>
    <ol class="steps" data-stagger>
      <li><b>Konzultace</b><p>S prodejcem projdete, co chcete změnit.</p></li>
      <li><b>Nacenění</b><p>Dostanete rozpočet změn a termín, do kdy je potvrdit.</p></li>
      <li><b>Potvrzení</b><p>Změny potvrdíte dodatkem ke smlouvě.</p></li>
      <li><b>Realizace</b><p>Stavba zapracuje změny v příslušné fázi.</p></li>
      <li><b>Kontrola</b><p>Při předání zkontrolujete, že je vše podle dohody.</p></li>
    </ol>
    <p class="calc__note" style="margin-top:18px">Postup a termíny upřesní HP DOMY. Standardy vycházejí z předchozích projektů HP DOMY.</p>
  </div></section>
  <section class="sub-sec"><div class="wrap">
    <div class="sub-head"><h2 class="h2">Na co se kupující ptají</h2></div>
    <div class="acc" id="faq-acc"></div>
  </div></section>
  {cta_band("Chcete vidět materiály naživo?", "Prodejce vám ukáže vzorky podlah, obkladů a oken a vysvětlí, co lze změnit.")}
  {next_page("galerie", "Galerie")}
</main>
'''
page("standardy", "Standardy · Blatec | HP DOMY", "Standardy rodinných domů v Blatci: konstrukce, tepelné čerpadlo, okna, interiér a technologie. Co je v ceně a co za příplatek.", body)

# ------------------------------------------------------------------ Galerie
body = f'''<main class="page gallery-page">
  <div class="wrap">
    {crumbs((None, "Galerie"))}
    <div class="phero phero--split" style="padding-bottom:32px">
      <div style="display:grid;gap:20px"><h1 class="h1" data-page-in>Jak budou domy vypadat</h1><p class="lead" data-page-in>Zástupné vizualizace obou typů domů. Finální vizualizace exteriéru i interiéru doplníme, jakmile je HP DOMY uvolní.</p></div>
      <div class="gal-tabs phero__aside" role="group" aria-label="Filtr galerie" data-page-in style="display:flex;flex-wrap:wrap;gap:8px">
        <button class="chip" aria-pressed="true" data-g="all">Vše</button><button class="chip" aria-pressed="false" data-g="patrovy">Patrový dům</button>
        <button class="chip" aria-pressed="false" data-g="prizemni">Přízemní dům</button><button class="chip" aria-pressed="false" data-g="okoli">Ulice a okolí</button>
        <button class="chip" aria-pressed="false" data-g="int">Interiér</button>
      </div>
    </div>
    <div class="gal" id="gal"></div>
  </div>
  <section class="sub-sec"><div class="wrap">
    <div class="sub-head"><h2 class="h2">Fotky ze stavby</h2><p class="lead">Po zahájení výstavby sem budeme přidávat fotky z jednotlivých fází, abyste viděli, jak váš dům roste.</p></div>
    <ol class="tl">{tl}</ol>
  </div></section>
  <section class="sub-sec" style="padding-top:0"><div class="wrap">{watchdog(["stavba"], "Chcete vidět, jak stavba roste?", "Pošleme vám e-mail, když přidáme fotky z nové fáze výstavby.")}</div></section>
  {cta_band()}
  {next_page("kontakt", "Kontakt")}
</main>
'''
page("galerie", "Galerie · Blatec | HP DOMY", "Vizualizace rodinných domů v Blatci: patrový a přízemní dům, ulice a okolí.", body, extra=LIGHTBOX)

# ------------------------------------------------------------------ Kontakt
form_src = read("pages/index.main.html")
form_html = form_src[form_src.index('<form class="form"'):form_src.index("</form>") + len("</form>")]
topics = [("prohlidka", "Prohlídka", "Kdy se vám hodí prohlídka pozemku?"), ("dum", "Dotaz na dům", "Na co se chcete zeptat?"),
          ("financovani", "Financování", "Jakou částku plánujete financovat hypotékou?"), ("jine", "Jiné", "Napište nám, s čím můžeme pomoci.")]
seg = '<div class="field"><span style="font-size:13.5px;font-weight:500">Co potřebujete</span><div class="seg seg--wrap" role="group" aria-label="Typ dotazu">' + "".join(
    f'<button type="button" data-topic="{k}" data-ph="{ph}" aria-pressed="{str(i == 0).lower()}">{n}</button>' for i, (k, n, ph) in enumerate(topics)) + "</div></div>"
form_html = form_html.replace('<div class="form__row form__row--2">', seg + '\n          <div class="form__row form__row--2">', 1)
form_html = form_html.replace('aria-labelledby="ct-h"', 'aria-labelledby="kt-h"')
body = f'''<main class="page">
  <div class="wrap">
    {crumbs((None, "Kontakt"))}
  </div>
  <section class="contact contact--page sec" id="kontakt" aria-labelledby="kt-h" style="margin-inline:max(10px,env(safe-area-inset-left,0px));padding-block:clamp(40px,6vw,88px)">
    <div class="contact__bg" aria-hidden="true"><img src="img/garden-800.webp" alt="" loading="lazy" decoding="async"></div>
    <div class="wrap"><div class="ct">
      <div>
        <h1 class="h2" id="kt-h" style="margin-top:18px" data-page-in>Domluvte si prohlídku pozemku</h1>
        <p class="lead" style="margin-top:18px" data-page-in>Napište nám, nebo rovnou zavolejte. Prodejce se vám ozve do dvou pracovních dnů.</p>
        <div class="ct-direct">
          <a href="tel:+420776294498"><svg><use href="#i-phone"/></svg><span><small>Zavolat</small><span class="tnum">+420 776 294 498</span></span></a>
          <a href="mailto:info@impulsreality.com"><svg><use href="#i-mail"/></svg><span><small>Napsat e-mail</small>info@impulsreality.com</span></a>
        </div>
        <div class="ct__people">{PERSON}
          <div class="person"><div class="person__av" aria-hidden="true" style="font-size:10px">HP</div><div><small>Developer</small><b>HP DOMY s.r.o.</b><div class="person__lines"><span>I. P. Pavlova 692/143, 783 01 Olomouc</span><a href="https://mapy.cz/zakladni?q=I.%20P.%20Pavlova%20692%2F143%20Olomouc" target="_blank" rel="noopener">Mapa</a></div></div></div>
        </div>
      </div>
      {form_html}
    </div></div>
  </section>
  <section class="sub-sec"><div class="wrap">
    <div class="sub-head"><h2 class="h2">Jak probíhá koupě domu</h2><p class="lead">Obvyklý postup u novostavby. Konkrétní podmínky upřesní prodejce.</p></div>
    <ol class="steps" data-stagger>
      <li><b>Výběr a prohlídka</b><p>Vyberete volný dům a prohlédnete si pozemek.</p></li>
      <li><b>Rezervace</b><p>Rezervační smlouvou si dům podržíte, v tabulce se označí jako rezervovaný.</p></li>
      <li><b>Smlouva o smlouvě budoucí</b><p>Stanoví cenu, termíny a platební kalendář.</p></li>
      <li><b>Výstavba a změny</b><p>Během stavby můžete zadat klientské změny.</p></li>
      <li><b>Předání</b><p>Po kolaudaci podepíšete kupní smlouvu a převezmete klíče.</p></li>
    </ol>
  </div></section>
  <section class="sub-sec" style="padding-top:0"><div class="wrap">{reviews("compact", title="Zkušenosti majitelů domů od HP DOMY", count=8)}</div></section>
  <section class="sub-sec sub-sec--tint"><div class="wrap">
    <div class="faq"><div style="display:grid;gap:18px;align-content:start"><h2 class="h2">Než nám napíšete</h2></div><div class="acc" id="faq-acc"></div></div>
  </div></section>
</main>
'''
page("kontakt", "Kontakt · Blatec | HP DOMY", "Domluvte si prohlídku rodinného domu v Blatci. Prodejce Pavel Čundrla, Impuls Reality, +420 776 294 498.", body)

# ------------------------------------------------------------------ house detail ×14
def garden_dial(dirn):
    ang = 0 if dirn == "sever" else 180
    return f'''<svg class="orient__dial" viewBox="-60 -60 120 120" aria-hidden="true"><circle r="56" fill="#fff" stroke="#dedbd4"/><circle r="40" fill="none" stroke="#edebe6"/>
<text y="-44" text-anchor="middle" font-size="11" font-family="Inter,system-ui" fill="#161616" font-weight="600">S</text><text y="52" text-anchor="middle" font-size="11" font-family="Inter,system-ui" fill="#6c675f">J</text>
<text x="48" y="4" text-anchor="middle" font-size="11" font-family="Inter,system-ui" fill="#6c675f">V</text><text x="-48" y="4" text-anchor="middle" font-size="11" font-family="Inter,system-ui" fill="#6c675f">Z</text>
<g transform="rotate({ang})"><path d="M-14 -34 A36 36 0 0 1 14 -34 L6 -6 L-6 -6Z" fill="#2c3fd6" opacity=".85"/></g><rect x="-11" y="-11" width="22" height="22" rx="3" fill="#161616"/></svg>'''

def mini_plan(hid):
    g = GEO[hid]
    s = '<svg viewBox="40 40 920 490" aria-hidden="true" style="width:100%;height:auto;display:block"><rect x="30" y="258" width="940" height="52" rx="6" fill="#dedbd4"/>'
    for h in HOUSES:
        q = GEO[h["id"]]; on = h["id"] == hid
        s += f'<rect x="{q["x"]}" y="{q["y"]}" width="{q["w"]}" height="{q["h"]}" rx="6" fill="{"#161616" if on else "#fff"}" stroke="#cfcac1"/>'
        s += f'<text x="{q["x"] + q["w"] / 2}" y="{q["y"] + q["h"] / 2 + 8}" text-anchor="middle" font-family="Inter,system-ui" font-size="26" font-weight="500" fill="{"#fff" if on else "#a39e94"}">{h["id"]}</text>'
    return s + f'<circle cx="{g["x"] + g["w"] / 2}" cy="{g["y"] + g["h"] / 2}" r="58" fill="none" stroke="#2c3fd6" stroke-width="6"/></svg>'

for h in HOUSES:
    hid, T = h["id"], TYPES[h["type"]]
    sold = h["status"] == "prodany"
    gal = [dict(src=s, title=TITLES[s]) for s in T["gal"]]
    gal_attr = esc(json.dumps(gal, ensure_ascii=False))
    gal_html = "".join(f'<button data-lb="{k}"{"" if k == 0 else f' aria-label="Zvětšit: {g["title"]}"'}>{img(g["src"], g["title"] + " – zástupná vizualizace", "(min-width:860px) 66vw, 100vw" if k == 0 else "33vw", eager=(k == 0))}' + (f'<span class="count"><svg><use href="#i-image"/></svg>Zvětšit · {len(gal)} {"fotky" if len(gal) < 5 else "fotek"}</span>' if k == 0 else "") + "</button>" for k, g in enumerate(gal[:3]))
    calc_price = h["price"] or (9490000 if h["type"] == "patrovy" else 8990000)
    similar = sorted([x for x in HOUSES if x["id"] != hid and x["status"] == "volny"], key=lambda x: (x["type"] != h["type"], abs(x["plot"] - h["plot"])))[:3]
    sim_html = "".join(f'''<a class="scard" href="dum-{s["id"]}.html"><div class="scard__img"><img src="img/{s["img"]}-800.webp" alt="" loading="lazy" decoding="async" width="800" height="450"></div><div class="scard__body"><div class="scard__row"><b>Dům {s["id"]}</b><span class="badge badge--{s["status"]}">{STATUS[s["status"]]}</span></div><span class="scard__meta">{s["label"]} {s["disp"]} · pozemek {area(s["plot"])} · zahrada na {s["garden"]}</span><span class="scard__price">{price_txt(s)}</span></div></a>''' for s in similar)
    floors_btn = "".join(f'<button data-floor="{k}" aria-pressed="{str(k == 0).lower()}">{f["name"]}</button>' for k, f in enumerate(PLANS[h["type"]]))
    prev_id, next_id = (hid - 2) % 14 + 1, hid % 14 + 1
    actions = ('<a class="btn" href="kontakt.html#dum-%d">Domluvit prohlídku <span class="ic"><svg><use href="#i-arrow"/></svg></span></a>' % hid) if not sold else '<a class="btn" href="nabidka.html#volne">Volné domy <span class="ic"><svg><use href="#i-arrow"/></svg></span></a>'
    garden_note = ("Zahrada je orientovaná na jih. Nejvíc slunce celý den, ideální pro terasu a záhony." if h["garden"] == "jih"
                   else "Zahrada je orientovaná na sever, terasa bude v létě příjemně ve stínu. Ranní a večerní slunce dopadá z boku.")
    jsonld = {"@context": "https://schema.org", "@type": "SingleFamilyResidence", "name": f"Dům {hid} – Blatec",
              "numberOfRooms": int(h["disp"][0]), "floorSize": {"@type": "QuantitativeValue", "value": h["area"], "unitCode": "MTK"},
              "address": {"@type": "PostalAddress", "addressLocality": "Blatec", "postalCode": "783 75", "addressCountry": "CZ"}}
    if h["price"] and not sold:
        jsonld["offers"] = {"@type": "Offer", "price": h["price"], "priceCurrency": "CZK", "availability": "https://schema.org/InStock"}
    body = f'''<main class="page">
  <div class="wrap">
    {crumbs(("nabidka.html", "Nabídka domů"), (None, f"Dům {hid}"))}
    {'<div class="sold-banner" data-page-in><svg><use href="#i-info"/></svg><span>Tento dům je prodaný. Podívejte se na podobné volné domy níže.</span></div>' if sold else ''}
    <div class="hd-top">
      <div><div class="hd-title" data-page-in><h1 class="h1">Dům {hid}</h1><span class="badge badge--{h["status"]}">{STATUS[h["status"]]}</span></div>
        <p class="hd-sub" data-page-in>{T["label"]} dům {h["disp"]} · {area(h["area"])} užitné plochy · pozemek {area(h["plot"])}</p></div>
      <div class="hd-price" data-page-in><small>Cena vč. DPH</small><b>{price_txt(h)}</b><div class="row">{actions}<button class="fav fav--lg" type="button" data-fav="{hid}" aria-pressed="false" aria-label="Uložit dům {hid}"><svg aria-hidden="true"><use href="#i-heart"/></svg></button><button class="btn btn--ghost" data-pdf="{hid}"><svg style="width:16px;height:16px"><use href="#i-pdf"/></svg>&nbsp;Karta PDF</button></div></div>
    </div>
    <div class="hd-gal" data-lb-list="{gal_attr}" data-page-in>{gal_html}</div>
    <nav class="subnav subnav--house" aria-label="Části stránky"><a href="#parametry">Parametry</a><a href="#pudorys">Půdorys</a><a href="#poloha">Poloha</a><a href="#vybaveni">V ceně</a><a href="#financovani">Financování</a><a href="#podobne">Podobné domy</a><a href="#recenze">Recenze</a></nav>
    <div class="hd-layout">
      <div class="hd-main">
        {watchdog(["dum"], f"Dům {hid} je {'rezervovaný' if h['status'] == 'rezervace' else 'prodaný'}", "Rezervace někdy padnou. Dáme vám vědět e-mailem, kdyby se dům uvolnil, nebo když se objeví podobný.", house=hid, compact=True) if h["status"] != "volny" else ""}
        <section class="hd-sec" id="parametry"><header><h2 class="h2">Parametry</h2></header>
          <div class="params" data-stagger>
            <div class="param"><svg><use href="#s-plan"/></svg><div><small>Dispozice</small><b>{h["disp"]}</b></div></div>
            <div class="param"><svg><use href="#s-area"/></svg><div><small>Užitná plocha</small><b>{area(h["area"])}</b></div></div>
            <div class="param"><svg><use href="#a-tree"/></svg><div><small>Pozemek</small><b>{area(h["plot"])}</b></div></div>
            <div class="param"><svg><use href="#s-car"/></svg><div><small>Parkování</small><b>2 stání u domu</b></div></div>
            <div class="param"><svg><use href="#s-sun"/></svg><div><small>Zahrada</small><b>na {h["garden"]}</b></div></div>
            <div class="param"><svg><use href="#s-heat"/></svg><div><small>Vytápění</small><b>Tepelné čerpadlo</b></div></div>
          </div>
        </section>
        <section class="hd-sec" id="pudorys"><header><h2 class="h2">Půdorys</h2>{'<div class="seg" role="group" aria-label="Podlaží">' + floors_btn + '</div>' if len(PLANS[h["type"]]) > 1 else ''}</header>
          <div class="fp" id="fp" data-house="{hid}">
            <div class="fp__canvas"><svg id="fp-svg" role="img" aria-label="Ilustrační půdorys domu {hid}"></svg></div>
            <div><ul class="rooms" id="fp-rooms"></ul><p class="calc__note" style="margin-top:12px">Ilustrační půdorys. Skutečné půdorysy doplní HP DOMY.</p></div>
          </div>
        </section>
        <section class="hd-sec" id="poloha"><header><h2 class="h2">Poloha v ulici</h2><a class="link" href="nabidka.html">Celá situace <svg><use href="#i-arrow"/></svg></a></header>
          <div class="loc-row"><div class="fp__canvas">{mini_plan(hid)}</div><div class="orient">{garden_dial(h["garden"])}<p><b style="color:var(--ink)">Zahrada na {h["garden"]}</b><br>{garden_note}</p></div></div>
        </section>
        <section class="hd-sec" id="vybaveni"><header><h2 class="h2">Co je v ceně</h2><a class="link" href="standardy.html">Všechny standardy <svg><use href="#i-arrow"/></svg></a></header>
          <div class="grid-2" style="gap:10px" data-stagger>
            {"".join(f'<div class="tile" style="grid-template-columns:auto 1fr;align-items:center;padding:16px 18px"><svg class="ti"><use href="#{s[0]}"/></svg><div><h3>{s[1]}</h3></div></div>' for s in STD_SHORT[:6])}
          </div>
        </section>
        <section class="hd-sec" id="financovani"><header><h2 class="h2">Kolik bude splátka</h2></header>
          <div class="calc" id="calc" data-price="{calc_price}">
            <div class="calc__in">
              <div class="range"><div class="range__top"><label for="c-own">Vlastní zdroje</label><output id="o-own"></output></div><input type="range" id="c-own" min="10" max="60" step="5" value="20"></div>
              <div class="range"><div class="range__top"><label for="c-rate">Úroková sazba</label><output id="o-rate"></output></div><input type="range" id="c-rate" min="2" max="8" step="0.1" value="4.9"></div>
              <div class="range"><div class="range__top"><label for="c-years">Doba splácení</label><output id="o-years"></output></div><input type="range" id="c-years" min="10" max="30" step="1" value="30"></div>
              <p class="calc__note">Orientační výpočet {"z ceny domu" if h["price"] else "z obvyklé ceny tohoto typu domu"} ({fmt(calc_price)} Kč). Nejde o nabídku úvěru.</p>
            </div>
            <div class="calc__out" aria-live="polite"><small>Měsíční splátka</small><b id="o-pay">–</b>
              <dl><div><dt>Výše úvěru</dt><dd id="o-loan">–</dd></div><div><dt>Celkem zaplatíte</dt><dd id="o-total">–</dd></div></dl>
              <a class="btn btn--light btn--sm" href="kontakt.html#dum-{hid}" style="justify-self:start">Pomoc s financováním</a></div>
          </div>
        </section>
        <section class="hd-sec" id="podobne"><header><h2 class="h2">Podobné volné domy</h2><a class="link" href="nabidka.html#volne">Všechny volné <svg><use href="#i-arrow"/></svg></a></header>
          <div class="similar">{sim_html}</div>
        </section>
        <section class="hd-sec" id="recenze"><header><h2 class="h2">Kdo dům postaví</h2></header>
          <p style="color:var(--stone-600);max-width:60ch">Stavět bude HP DOMY, olomoucký developer s hodnocením {rating_txt} z 5 na Google. Takhle o firmě píšou lidé, kterým už postavila dům.</p>
          {reviews("inline", count=8)}
        </section>
      </div>
      <aside class="hd-side">
        <div class="sidecard"><div class="hd-title" style="justify-content:space-between"><b style="font:400 20px var(--f-display)">Dům {hid}</b><span class="badge badge--{h["status"]}">{STATUS[h["status"]]}</span></div>
          <dl class="kv"><div><dt>Cena</dt><dd>{price_txt(h)}</dd></div><div><dt>Pozemek</dt><dd>{area(h["plot"])}</dd></div></dl>
          {actions.replace('class="btn"', 'class="btn" style="justify-content:space-between"')}
          {PERSON}
        </div>
      </aside>
    </div>
    <nav class="house-nav" aria-label="Další domy"><a href="dum-{prev_id}.html"><svg><use href="#i-left"/></svg>Dům {prev_id}</a><a href="dum-{next_id}.html">Dům {next_id}<svg><use href="#i-right"/></svg></a></nav>
  </div>
  <div style="height:clamp(56px,8vw,112px)"></div>
  {cta_band(f"Zaujal vás dům {hid}?" if not sold else "Hledáte podobný dům?", "Prodejce vám ukáže pozemek a projde s vámi půdorys i financování.")}
</main>
<nav class="dock" aria-label="Dům {hid}">
  <div class="dock__top"><div class="dock__info"><small>Dům {hid} · {STATUS[h["status"]]}</small><b>{price_txt(h)}</b></div>
    <div class="dock__act"><a class="dock__call" href="tel:+420776294498" aria-label="Zavolat prodejci"><svg aria-hidden="true"><use href="#i-phone"/></svg></a>{('<a class="btn btn--sm dock__cta" href="kontakt.html#dum-%d">Mám zájem</a>' % hid) if not sold else '<a class="btn btn--sm dock__cta" href="nabidka.html#volne">Volné domy</a>'}</div></div>
  <div class="dock__tabs">
    <a href="#parametry"><svg aria-hidden="true"><use href="#s-area"/></svg><span>Parametry</span></a>
    <a href="#pudorys"><svg aria-hidden="true"><use href="#s-plan"/></svg><span>Půdorys</span></a>
    <a href="#poloha"><svg aria-hidden="true"><use href="#i-pin"/></svg><span>Poloha</span></a>
    <a href="#financovani"><svg aria-hidden="true"><use href="#i-calc"/></svg><span>Splátka</span></a>
    <a href="#podobne"><svg aria-hidden="true"><use href="#i-home"/></svg><span>Podobné</span></a>
  </div>
</nav>
'''
    page(f"dum-{hid}", f"Dům {hid} · {T['label']} {h['disp']} · Blatec | HP DOMY",
         f"Dům {hid} v Blatci: {T['label'].lower()} {h['disp']}, {area(h['area'])}, pozemek {area(h['plot'])}, zahrada na {h['garden']}. Cena: {price_txt(h)}. Stav: {STATUS[h['status']]}.",
         body, active="nabidka", preload=T["gal"][0], jsonld=jsonld, extra=LIGHTBOX)


# ------------------------------------------------------------------ assets
if FLAVOR == "repo":
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    open(os.path.join(OUT, "assets/site.css"), "w", encoding="utf-8").write(CSS_MIN)
    open(os.path.join(OUT, "assets/site.js"), "w", encoding="utf-8").write(JS)
    open(os.path.join(OUT, "assets/data.js"), "w", encoding="utf-8").write("window.BLATEC=" + json.dumps(DATA, ensure_ascii=False) + ";\n")
else:
    os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
    for f in os.listdir(os.path.join(ROOT, "img")):
        shutil.copy(os.path.join(ROOT, "img", f), os.path.join(OUT, "img", f))
print("built", FLAVOR, sorted(os.listdir(OUT))[:6], "…")
