# Blatec · web projektu HP DOMY

Prodejní web pro 14 rodinných domů v Blatci u Olomouce (pracovní název projektu).
Statický web bez frameworku, připravený k nasazení na libovolný hosting.

## Stránky

| Soubor | Obsah |
| --- | --- |
| `index.html` | One-pager se všemi sekcemi (úvod, o projektu, lokalita, nabídka, standardy, galerie, kontakt) |
| `o-projektu.html` | Typy domů vedle sebe, co je v ceně, harmonogram, developer a jeho projekty |
| `lokalita.html` | Dojezdové časy (auto / vlak / kolo), mapa, ověřená vybavenost obce |
| `nabidka.html` | Situace propojená s tabulkou, filtry, porovnání až 3 domů, rychlý náhled |
| `dum-1.html` … `dum-14.html` | Detail domu: fotky, parametry, půdorys s místnostmi, orientace zahrady, kalkulačka splátky, podobné domy |
| `standardy.html` | Standardy po oblastech s označením V ceně / Příprava / Za příplatek, klientské změny |
| `galerie.html` | Galerie s filtry a lightboxem, průběh výstavby |
| `kontakt.html` | Formulář s typem dotazu a předvyplněním domu (`kontakt.html#dum-4`), postup koupě, FAQ |

Design systém návrhu je na `index.html#komponenty`.

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
