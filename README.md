# Blatec · web projektu HP DOMY

Návrh jednostránkového prodejního webu pro 14 rodinných domů v Blatci u Olomouce
(pracovní název projektu). Statický web bez buildu: `index.html` + složka `img/`.

## Spuštění

Stačí otevřít `index.html`, nebo spustit libovolný statický server:

```bash
npx serve .
```

## Struktura stránky

1. Úvod – vizualizace přes celou šířku, logo, claim, podpis HP DOMY DEVELOPMENT
2. O projektu – text, pruh klíčových čísel, dva typy domů
3. Lokalita – text, schematická mapa, vzdálenosti, ověřené služby, odkaz na web obce
4. Nabídka domů – situace 14 domů propojená s tabulkou (desktop) a kartami (mobil), filtry, karta domu
5. Standardy – akordeon s ikonami, tlačítko na PDF
6. Galerie – mřížka + lightbox (klávesnice, swipe)
7. Kontakt – formulář s výběrem domu, validací, stavem odesílání a potvrzením
8. Patička – firemní údaje HP DOMY, další projekty, ochrana údajů

Na adrese `#komponenty` je design systém: logo v pozitivu a negativu, favicon,
náhled pro sdílení, barvy, typografie, stavy tlačítek, polí, řádků tabulky, menu a ikony.

## Data domů

Zástupné údaje jsou v poli `H` v `index.html` (sekce `data (zástupné údaje)`):
`[číslo, typ, pozemek m², cena Kč nebo null = „Na dotaz“, stav]`.
Stav: `volny`, `rezervace`, `prodany`.

## Co je zástupné

- Vizualizace v `img/` jsou studijní model (renderováno z `tools/scene.py`, Blender).
  Po dodání vizualizací od HP DOMY stačí přepsat soubory se stejnými názvy.
- Situace je ilustrační SVG generované ze skriptu, nahradí ji podklad od HP DOMY.
- Mapa je schematická. Na produkci vložit Mapy.cz nebo Google Maps.
- Formulář zatím neodesílá – napojit na backend (PHP mailer / Formspree / vlastní endpoint).

## Technologie

HTML, CSS, vanilla JS, GSAP 3.12.5 + ScrollTrigger (lokálně v `js/`). Písma Michroma,
Inter a Encode Sans Expanded hostovaná lokálně v `fonts/` (woff2, latin + latin-ext),
bez požadavků na Google Fonts. Obrázky WebP v několika šířkách přes `srcset`.
Respektuje `prefers-reduced-motion`.
