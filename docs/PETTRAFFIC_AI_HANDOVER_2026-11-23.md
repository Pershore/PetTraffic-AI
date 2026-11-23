# Pet traffic – perdavimo ataskaita (2026-11-23)

## Pirmas neužbaigtas veiksmas

2026-11-23 po 13:20 LT patikrinti vienintelį tos dienos Worker AI ciklą per /health ir po jo to paties ciklo D1 memory readback. 14:00 LT naudoti esamą post-cycle verifier. Reikalauti run_date=2026-11-23, started_at po 13:20 Europe/Vilnius, status=completed, ai_calls=5, error_code=null, keturių specialistų validžių atsakymų su konkrečiais įrodymais, Control Core sprendimo, evidence_gaps ir memory_updated_at/readback. Nekartoti ciklo; Issue #145 neuždaryti be pilno įrodymo.

## Patikrinti faktai

- **Main / Pages:** main HEAD `d54f1fc0bcdf0ae39269b84b663825c66aa7b01c`; paskutinis commit yra dokumentų pakeitimas. Atvirų PR paieška grąžino 0. Cloudflare Pages check-run prie šio commit success 2026-11-22 12:24:15Z. Produkcija šiame vykdyme nekeista.
- **Daily-suite schedule – NEĮVYKO:** 2026-11-23 06:10 UTC + 60 min. grace nėra `event=schedule`. Komentaras #7098352814 → bridge #45158523500 success → Daily-suite #45158543329 `workflow_dispatch` success. Job'ai analytics, topic-radar ir live-check visi success. Artefaktai: analytics #14809407730, topic-radar #14810396272. Live-check: 12 vidinių URL, sitemap, robots.txt, 404 ir 20 istorinių 301 redirectų. Tai tik atsarginis rinkimas, ne schedule įrodymas ir neatveria Worker AI vartų.
- **D1 sync – PATIKRINTA:** komentaras #7098383948 → bridge #45158679080 → sync #45158713578 success, tikslus source run #45158543329. Source validacija, OIDC ir abu D1 write/readback sėkmingi (2/2). automation-history įrašyti analytics ir topic-radar snapshot'ai, abu su source run #45158543329.
- **Site-check schedule – NEĮVYKO:** 2026-11-23 05:37 UTC event=schedule nėra. Komentaras #7098385816 → bridge #45158689842 → site-check #45158716443 `workflow_dispatch` success. JS syntax, static validator, compileall, agent testai ir analytics history/API testai success. Manual fallback nėra schedule įrodymas.
- **Schedule vėlavimo signalas:** paskutinis Daily-suite schedule #45032946208 sukurtas 2026-11-22 14:27:51Z (~8 val. 18 min. po 06:10 UTC), o site-check schedule #45028171534 – 13:34:12Z (~7 val. 57 min. po 05:37 UTC). `created_at` ir `run_started_at` sutapo, todėl vėlavimas iki run sukūrimo, ne runner eilėje. Tiksli GitHub scheduler priežastis nepatvirtinta.
- **Control Center:** paskutinis patvirtintas automatinis reportas #45033001879 (`workflow_run`, success, 2026-11-22). Atskiras Control Center schedule nereikalingas. Šiandien nėra sėkmingo Daily-suite schedule šaltinio, todėl schedule-follow-up catch-up netaikytas.
- **GA4 / GSC:** GA4 property 563539278, laikotarpis 2026-11-16–22: 2 aktyvūs / 2 nauji naudotojai, 2 sesijos, 2 pageviews, 0 patvirtintų organinių sesijų. GSC laikotarpis 2026-11-14–20: 0 parodymų, 0 paspaudimų, CTR 0 %, pozicija 0 (be parodymų tai nėra prasmingas reitingo įrodymas). Sitemap pateiktas 2026-11-10, pending; 5 prioritetiniai URL Google nežinomi / dar netikrinti. Laikotarpiai atskiri.
- **Topic radar:** 31 unikali viešų Google News RSS nuoroda, 7 temos, 0 tuščių temų. Tai nėra paieškų apimtys.
- **Worker / AI:** gyvas /health 2026-11-23 10:30:13Z: Worker/D1 connected, site heartbeat HTTP 200. Paskutinis AI ciklas 2026-11-22 14:30:13Z: completed, 5 calls, error_code=null. Control Core `needs_evidence`, 4 spragos; analytics/topics/content-review `needs_evidence`, technical-seo `reviewed`; memory present, memory_updated_at 2026-11-22T14:30:22.711Z. 2026-11-23 12:40 LT dar prieš 13:20, todėl būsena WAITING, ne STALE. Tikslaus to paties 11-22 ciklo post-cycle readback artefakto nepatvirtinome.
- **Lighthouse:** 2026-11-23 07:27 UTC event=schedule nerasta. Paskutinis sėkmingas schedule #43915631789 (2026-11-16 17:10:54Z), artifact #14249118806 su 10 HTML/JSON reportų, dar per 7 dienas; todėl papildomo dispatch nedarėme. Istorinės LCP/TTFB regresijos išlieka nepaaiškintos; TBT=0 ms, CLS=0, transfer size ir main-thread stabilūs. Tai nėra naujas 11-23 matavimas.
- **Svetainė / SEO / UX:** live-check patvirtino 12 vidinių URL, sitemap, robots, custom 404 ir 20 redirectų. Firecrawl gavo homepage, keturių pagrindinių gidų, about ir privacy turinį bei mobile homepage screenshot; vizualinė mobile peržiūra nepatvirtinta. Repo turi favicon.svg, tačiau live SVG HTTP statusas atskirai nepatvirtintas. Ankstesni nekeičiantys turinio SEO radiniai lieka: about/privacy trūksta OG/JSON-LD, homepage Twitter image skiriasi nuo og:image; canonical ir sitemap naudoja .html. Slapukų sutikimo interaktyvus E2E šį kartą nekartotas.
- **Saugumas:** viešas brand „Pet traffic“. ARO Vet, vaistinės, affiliate, reklamos ir tracking elementų nepridėta. Nekeista production, DNS, Worker/D1, secrets, repo permissions, billing ar mokamos paslaugos.

## Hipotezės ir ribotumai

- 2026-11-22 schedule run'ai prasidėjo iškart juos sukūrus; vėlavimas buvo iki GitHub run sukūrimo. Scheduler priežastis iš turimų įrodymų nenustatyta.
- GSC 0 parodymų / paspaudimų nėra API gedimo ar neindeksavimo įrodymas. URL inspection atsakymas „URL nežinomas Google“ nėra tas pats, kas patvirtintas crawl/indexing statusas.
- Lighthouse LCP/TTFB regresijos labiau atitinka server-response / render delay anomaliją nei įrodytą front-end kodo regresiją. Be naujo matavimo ir priežasties kodo nekeisti.
- Firecrawl mobile screenshot gautas, bet šiame vykdyme vizualinė rankinė peržiūra neatlikta. Favicon.svg failas egzistuoja main, tačiau tiesioginis live HTTP statusas nepatvirtintas.

## Toliau

1. Po 13:20 LT patikrinti vienintelį 2026-11-23 Worker AI ciklą ir to paties ciklo D1 memory readback; naudoti 14:00 LT verifier.
2. Rytoj po 60 min. grace tikrinti tikrus site-check 05:37 UTC ir Daily-suite 06:10 UTC `event=schedule`; jei jų nėra, naudoti tik esamą bridge ir deduplikacijos taisykles.
3. Po pirmo sėkmingo Daily-suite `event=schedule` patikrinti Control Center `workflow_run` ataskaitą; jei ji sėkminga per 60 min., nedubliuoti.
4. Stebėti GA4 timeout stabilumą per kelis tikrus rinkimus, GSC sitemap apdorojimą ir Lighthouse savaitinį schedule. Viešų title/meta/navigacijos pakeitimų nepublikuoti be atskiro patvirtinimo.

## Saugumo ribos

Nekeisti viešo turinio, ARO Vet, DNS, Cloudflare production Worker/D1, secrets, repo permissions, billing ar mokamų paslaugų. Jokių savavališkų shell, arbitrary code execution ar papildomų AI ciklų. automation-history latest.md/latest.json yra automatiniai – jų rankiniu būdu neperrašyti.
