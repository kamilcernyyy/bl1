# Blatec · web projektu HP DOMY

Prodejní web pro 14 rodinných domů v Blatci u Olomouce (pracovní název projektu).
Statický web bez frameworku, připravený k nasazení na libovolný hosting.

## Stránky

| Soubor | Obsah |
| --- | --- |
| `index.html` | One-pager se všemi sekcemi (úvod, o projektu, lokalita, nabídka, standardy, galerie, kontakt) |
| `o-projektu.html` | Typy domů vedle sebe, co je v ceně, harmonogram, developer a jeho projekty |
| `lokalita.html` | Dojezdové časy (auto / vlak / kolo), mapa, ověřená vybavenost obce |
| `nabidka.html` | Úvodní fotka s počty, situace vedle seznamu domů (fotka, parametry, cena, stav), filtry stavu a typu, řazení, porovnání až 3 domů, rychlý náhled |
| `dum-1.html` … `dum-14.html` | Detail domu: fotky, parametry, půdorys s místnostmi, orientace zahrady, kalkulačka splátky, podobné domy |
| `standardy.html` | Standardy po oblastech s označením V ceně / Příprava / Za příplatek, klientské změny |
| `galerie.html` | Galerie s filtry a lightboxem, průběh výstavby |
| `kontakt.html` | Formulář s typem dotazu a předvyplněním domu (`kontakt.html#dum-4`), postup koupě, FAQ |

Design systém návrhu je na `index.html#komponenty`.

## Směr B (`v2/`)

Druhý designový směr inspirovaný Era Residence: velká didotová písma verzálkami, kurzívní akcenty, teplá paleta (krémová, pudrová, šampaňská zlatá a bordó), jemné zrno papíru, otáčivá pečeť projektu, plynulé rolování a přechody mezi stránkami. Data domů bere ze stejného `src/build.py`, takže čísla jsou v obou směrech vždy stejná.

- Celý web: `v2/index.html`, `o-projektu`, `lokalita`, `nabidka`, `standardy`, `galerie`, `kontakt` a `dum-1` … `dum-14`
- Efekty: mraky při rolování (krémová → mraky → krajina), vtažení do fotky, vodorovně rolované galerie a kroky, zvětšení každé fotky (lightbox)
- Barevné vizualizace v `v2/img/` (render `LOOK=color python3 tools/scene.py <záběr> …`, záběr `hana` = krajina s poli), mraky jsou procedurální
- Sestavení: `python3 src/v2/build.py` (zdroje v `src/v2/`: `build.py`, `style.css`, `app.js`)
- Písma: jen dvě rodiny – Instrument Serif (verzálky na nadpisy, kurzíva jako akcent) a Archivo Expanded (text a štítky), lokálně v `v2/fonts/`, s češtinou. Nadpisy v 6 velikostech: mega, h1–h5.
- Pohyb: GSAP 3.13 + ScrollTrigger + SplitText, Lenis (jen kolečko myši, dotyk zůstává nativní)
- Funkčně stejný jako směr A: uložené domy (srdíčko, filtr `#oblibene`), porovnání až 3 domů, řazení, hlídací pes, kalkulačka splátky, podobné volné domy, orientace zahrady, schematická mapa, recenze, tlačítko Zavolat na mobilu a spodní lišta s cenou na detailu domu
- Na mobilu je hlavička po odrolování plná lišta (krémová nad světlými sekcemi, bordó nad tmavými)
- Logo je otáčivá pečeť (točí se podle rolování), text se při rolování nikdy neskrývá ani neposouvá – animují se jen fotky (ořez při příchodu, paralaxa, mraky)
- Mraky jsou opakující se dlaždice (`v2/img/cloud-a/b.webp`, 1100 × 504 px), JS dopočítá šířku dlaždice, takže smyčka nemá šev
- Menu: vycentrovaný seznam, dole telefon a prohlídka; vejde se bez rolování od 375 × 560 px
- Psací akcenty nad nadpisy nikdy nezakrývají háčky, čárky a kroužky (akcent leží za verzálkami), řádkování velkých nadpisů má místo na Ů, Č, Ř
- Nadpisy stránek naskakují čistě přes CSS, takže se vykreslí hned (LCP kolem 1 s i na pomalém 4G)
- SEO a AEO připravené: titulky a popisy všech stránek, Open Graph obrázek `v2/img/og-1200x630.jpg`, strukturovaná data (Residence, Organization s hodnocením, WebSite, BreadcrumbList, ItemList domů, SingleFamilyResidence s cenou, FAQPage, Place, ImageGallery), `v2/sitemap.xml`
- Audit 15. 11. 2026: všech 21 stránek bez chyb v konzoli, bez rozbitých odkazů a kotev, jeden H1 na stránku, všechny obrázky s alt; Lighthouse mobil výkon 91–96, přístupnost a doporučené postupy 100, SEO 100 (bez `noindex`); počítač 99–100
- **Při spuštění:** odstranit `noindex`, v `src/v2/build.py` přepsat `BASE` (a adresu og:image) na finální doménu, napojit formuláře (prohlídka, hlídací pes) na e-mail nebo CRM, přidat sitemap do robots.txt
- Stránky mají `noindex`, aby se v Googlu nepletly se směrem A. Po výběru směru `noindex` odstranit.

## Funkce pro kupce

- **Uložené domy** – srdíčko u domu (tabulka, karty, detail), počet v plovoucí hlavičce, filtr `nabidka.html#oblibene`. Ukládá se jen v prohlížeči kupce.
- **Porovnání** až 3 domů v nabídce.
- **Hlídací pes** – formulář na upozornění (spuštění prodeje, uvolnění domu, novinky ze stavby). Je v nabídce, v galerii a u rezervovaných a prodaných domů. **Zatím neodesílá** – napojit na e-mailingový nástroj (Ecomail, Mailchimp, SmartEmailing) nebo vlastní backend.
- **Zavolat** – plovoucí tlačítko na mobilu a tabletu, na detailu domu je telefon ve spodní liště.
- **Kalkulačka splátky** na detailu domu.
- **Google recenze** HP DOMY (`REVIEWS` v `src/build.py`).

Filtry nabídky jdou otevřít odkazem: `nabidka.html#volne`, `#patrove`, `#prizemni`.

## Úpravy

Stránky se generují z `src/` – needitujte HTML v kořeni ručně.

```bash
python3 src/build.py            # vygeneruje web do kořene repozitáře
python3 src/build.py artifact   # samostatný náhled do _artifact/
```

- **Data domů** (stav, cena, pozemek): pole `RAW` v `src/build.py`.
  Formát `(číslo, typ, pozemek m², cena Kč nebo None = „Na dotaz“, stav)`, stav `volny` / `rezervace` / `prodany`.
- **Půdorysy**: `PLANS` v `src/build.py` (ilustrační, nahradit podklady HP DOMY).
- **Standardy, FAQ, dojezdové časy**: `STD_CATS`, `FAQ`, `TRAVEL` v `src/build.py`.
- **Styly**: `src/base.css` + `src/pages.css` → `assets/site.css`.
- **Skripty**: `src/site.js` → `assets/site.js`, data → `assets/data.js`.

## Co je zástupné

- Vizualizace v `img/` jsou studijní model (render z `tools/scene.py`, Blender). Po dodání vizualizací stačí přepsat soubory se stejnými názvy.
- Situace a půdorysy jsou ilustrační. Orientace zahrad vychází z ilustrační situace.
- Ceny, plochy, pozemky a stavy domů jsou zástupné.
- Dojezdové časy a vzdálenosti (kromě 8 km do Olomouce) jsou orientační.
- Mapa je schematická – na produkci vložit Mapy.cz.
- Kontaktní formulář a Hlídací pes neodesílají – napojit na backend (PHP mailer / Formspree / e-mailingový nástroj).
- Harmonogram nemá termíny – doplní HP DOMY.

## Technologie

HTML, CSS, vanilla JS, GSAP 3.12.5 + ScrollTrigger (lokálně v `js/`).
Písma Michroma, Inter a Encode Sans Expanded hostovaná lokálně v `fonts/` (woff2, latin + latin-ext), bez Google Fonts.
Obrázky WebP v několika šířkách přes `srcset`. Respektuje `prefers-reduced-motion`.
Detail domu má strukturovaná data schema.org (`SingleFamilyResidence`).
