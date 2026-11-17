# Pet traffic – perdavimas 2026-11-17

Atnaujinta: 2026-11-17 12:11 Europe/Vilnius

## Galiojanti politika

- Viešas prekės ženklas tik **Pet traffic**.
- ARO Vet, vaistinės skilties, produktų kortelių, affiliate, reklamos ir ARO Vet sekimo Pet traffic projekte nėra ir negali būti grąžinama.
- Viešo turinio, canonical / sitemap / navigacijos, Worker/D1 production, DNS, secrets, prieigos teisių ar billing pakeitimams taikomi atskiri patvirtinimo vartai.
- Nulinis biudžetas; jokio mokamo API ar naujų priklausomybių.
- `automation-history` latest.md/latest.json yra automatiniai snapshot'ai – jų rankiniu būdu nekeisti.

## Patvirtinti šios dienos įrodymai

### Main, PR ir site-check

- Main commit: `a375f02ec0743e894cfd1620d9ee1800f89522ce`.
- Atviri draft PR: #261 (AI JSON schema), #263 (daily-suite D1 routing), #264 (clean canonical), #266 (handover docs), #267 (analytics empty metrics). Naujausi matomi jų PR check run'ai sėkmingi; nė vienas nesujungtas.
- Gyvai patikrinta: homepage, keturi gidai, about, privacy, robots.txt ir sitemap.xml HTTP 200; neegzistuojantis URL HTTP 404. Favicon HTTP 200 matomas Lighthouse tinklo ataskaitoje.
- Owner-only bridge site-check [#44062438870](https://github.com/Pershore/PetTraffic-AI/actions/runs/44062438870) success. `python agent/validate_site.py`, `python -m compileall -q agent`, 31 agent testas ir 149 papildomi Python testai praėjo.
- Tiesioginis Cloudflare Pages deployment ID per turimą integraciją nepasiekiamas. Gyvi URL įrodo dabartinį prieinamumą, bet ne konkretaus deployment ID.

### Daily-suite, Control Center ir D1

- 2026-11-17 06:10 UTC daily-suite `event=schedule` run nerasta. Paskutinis tikras schedule [#43897746978](https://github.com/Pershore/PetTraffic-AI/actions/runs/43897746978) sukurtas 2026-11-16 15:34:13 UTC – 9 val. 24 min. po numatyto cron. Ankstesni schedule vėlavimai patvirtinti, bet konkreti GitHub priežastis neįrodyta.
- Pridėtas vienas tikslus komentaras `/pettraffic-run-daily-suite` (#6944911933). Bridge [#44061637550](https://github.com/Pershore/PetTraffic-AI/actions/runs/44061637550) success, bet dispatch praleistas pagal 20 val. deduplikavimo apsaugą, nes ankstesnis schedule dar buvo lange. Naujų daily-suite workflow_dispatch run nėra; komandos nekartoti, kol nepasibaigė apsaugos langas.
- Site-check catch-up: komentaras `/pettraffic-run-site-check` (#6945023935), bridge [#44062406317](https://github.com/Pershore/PetTraffic-AI/actions/runs/44062406317), site-check [#44062438870](https://github.com/Pershore/PetTraffic-AI/actions/runs/44062438870) – success.
- Event-driven Control Center [#44062455471](https://github.com/Pershore/PetTraffic-AI/actions/runs/44062455471) success; artefaktas #14319280708. Po jo sync [#44062526312](https://github.com/Pershore/PetTraffic-AI/actions/runs/44062526312) success, du D1 write/readback patvirtinti.
- Sync praleido daily-suite source validation ir daily-suite analytics/topic artefaktų parsisiuntimą, nes nėra naujo catch-up daily-suite run. D1 įrašyti Control Center įvykiai; daily-suite analytics/topic įvykių readback dar nepatvirtintas.

### Worker AI ir issue #145

- Gyvas `/health` HTTP 200; D1 ir Control Core schema connected; heartbeat 2026-11-17T10:00:13Z: site HTTP 200, DB ok.
- Paskutinis AI run_date=2026-11-16, started_at 2026-11-16T11:20:24.330Z, completed, ai_calls=5, error_code=null. Control Core `needs_evidence`, 5 spragos; analytics ir technical-seo `needs_evidence`, topics `reviewed`, content-review `invalid_json`. D1 memory present, memory_updated_at=2026-11-16T11:20:31.068Z.
- 2026-11-17 12:11 LT dar nebuvo 13:20 LT tikslinio ciklo, todėl būsena WAITING, ne STALE. Issue #145 paliktas open.

### GA4, Search Console ir URL anomalijos

- Savaitinė ataskaita [#43999680694](https://github.com/Pershore/PetTraffic-AI/actions/runs/43999680694), generated_at 2026-11-17T02:00:01Z. GA4 laikotarpis 2026-11-09–15: 7 aktyvūs, 7 nauji naudotojai, 24 sesijos, 88 peržiūros, 0 patvirtintų organinių sesijų.
- Search Console laikotarpis 2026-11-07–13: 0 parodymų, 0 paspaudimų, sitemap submitted/pending, 5 prioritetiniai URL Google dar nežinomi. Paskutinis GA4/GSC rinkimas 2026-11-16T15:34:41Z; duomenys gali vėluoti.
- RSS radaras apėmė 123 unikalias viešų antraščių nuorodas per 4 iš 7 dienų; tai nėra search volume.
- GA4 path `/articles/kaip-issirinkti-gyvuno-maista` gyvai nukreipia į homepage; `/about` alias rodo about.html; `/gargzdai-augintiniams` gyvai grąžina 404. Šie keliai nėra gyvo puslapio įrodymas.

### SEO canonical ir Lighthouse

- Live `.html` gidų URL peradresuojami 308 į clean URL, bet canonical ir sitemap dar nurodo `.html`. PR #264 yra draft, CI success, produkcijos canonical / sitemap / navigacija nepakeista. Viešam pakeitimui reikalingas atskiras patvirtinimas.
- Lighthouse schedule [#43915631789](https://github.com/Pershore/PetTraffic-AI/actions/runs/43915631789) success, 10 HTML/JSON ataskaitų. Lyginant su [#43855151465](https://github.com/Pershore/PetTraffic-AI/actions/runs/43855151465), dog-diarrhea mobile LCP padidėjo 1.855 → 9.779 s, vet-visit desktop 0.536 → 8.078 s, vet-visit mobile 1.852 → 5.548 s. TTFB atitinkamai 4.35 / 2.56 / 2.14 s; TBT=0, CLS=0, payload 40–44 KiB. Vieno matavimo neužtenka kodo pakeitimui; laukti kito weekly audit.
- Cloudflare tokeno rotacija ir GitHub secret atnaujinimas patvirtinti ankstesniame PROJECT_MEMORY įraše ir CI; šiame vykdyme secrets ar Worker production nekeisti.

## Pirmas neužbaigtas veiksmas

1. Po 13:20 LT patikrinti 2026-11-17 Worker AI ciklą: `run_date`, `started_at` po 13:20, `completed`, 5 AI calls, `error_code=null`, specialistų validūs atsakymai, Control Core sprendimas / evidence gaps ir D1 memory readback. Jei po 13:20 nėra naujo tos dienos run, žymėti STALE; nekartoti run_date. Issue #145 neuždaryti.
2. Po 20 val. daily-suite deduplikavimo lango patikrinti, ar atsirado tikras 2026-11-17 `event=schedule` arba naujas sėkmingas / vykstantis catch-up. Jei ne, naudoti tik esamą owner bridge ir tik vieną kartą; po sėkmingo daily-suite tikrinti visus 3 job, artefaktus ir D1 readback.
3. PR #263 palikti draft iki atskiro leidimo daily-suite snapshot rašymo į production D1 aktyvavimui.
4. PR #264 palikti draft iki atskiro leidimo clean canonical / sitemap / navigation publikavimui.
5. Kito Lighthouse schedule metu patikrinti, ar TTFB/LCP regresija pasikartoja; nekeisti CSS ar vaizdų kodo pagal vieną anomalų run.
6. Search Console sitemap apdorojimą ir 5 prioritetinių URL būsenas tikrinti kitame tikrame rinkime; sitemap pakartotinai neteikti, jei jis jau pateiktas.

## Ribos

- Jokio viešo turinio ar SEO metadata publikavimo be atskiro patvirtinimo.
- Jokio Worker/D1 production deploy, DNS, Cloudflare Access, secrets, paskyrų teisių, billing ar mokamų paslaugų pakeitimo be atskiro leidimo.
- Jokio arbitrary shell, model-generated code execution ar neapribotų task tipų.
- automation-history latest.md/latest.json rankiniu būdu nekeisti.


## 2026-11-17 13:55 LT – tęstinis perdavimas

### PATIKRINTA
- Daily-suite #44077181860: workflow_dispatch, visi analytics / topic-radar / live-check job success; live-check patvirtino core pages, internal links, sitemap, robots, 404 ir 20 senų 301 redirect.
- D1 sync #44077423350: source run valid, analytics/topic artefaktai atsisiųsti, 2 agreguoti įvykiai įrašyti ir perskaityti atgal.
- Read-only D1 diagnostic #43870801165 attempt 2: šiandienos analytics_snapshot ir topic_snapshot jau D1; šiandienos agent_run, specialistų rezultatai ir Control Core dar nėra. Atmintis tebėra 2026-11-16 needs_evidence.
- Worker /health 200; DB ir Control Core schema connected; paskutinis heartbeat 11:45:14Z, site_status 200.
- Worker cron diagnostic #44077019257: Cloudflare schedule config check success, heartbeat observation in progress.

### NEPATVIRTINTA / LAUKIA
- 2026-11-17 tikras daily-suite schedule paleidimas vis dar nerastas. Manual catch-up #44077181860 jo nepakeičia. Paskutinis schedule #43897746978 buvo sukurtas 15:34:13Z 2026-11-16 ir truko 34 s.
- 14:00 LT heartbeat turėtų atlikti Worker catch-up, nes D1 jau yra šios dienos analytics/topic snapshot. Tai prognozė pagal main Worker kodą, ne patvirtintas rezultatas.
- Po 14:00 tikrinti /health ir pakartoti read-only D1 diagnostiką. Reikalauti run_date=2026-11-17, 5 AI kvietimų, specialistų įrodymų, Control Core sprendimo ir memory readback. Jei specialistų evidence gaps išlieka, issue #145 palikti atvirą.
- PR #263 ir #261 draft; #263 pirmas, #261 tik su atskiru leidimu. Manual workflow_dispatch niekada nelaikyti schedule įrodymu.

### Analitika
- GA4 2026-11-10–16: 9 aktyvūs, 26 sesijos, 90 peržiūrų, 0 organinių sesijų.
- GSC 2026-11-08–14: 0 parodymų / paspaudimų, sitemap pending, 5 URL indeksavimas nežinomas.
- Temų radaras: 29 RSS nuorodos / 7 temos, ne paieškų apimtys.

### Saugumo ribos
- Kodo, Worker deploy, DNS, D1 schemos, secrets, billing ar turinio publikavimo pakeitimų nebuvo; tik agreguotų snapshot įrašymas į D1 per esamą OIDC sync ir readback.
- Dashboard viešas read-only; noindex nėra autentifikacija; #248 atviras.
- ARO Vet neliečiamas; pagrindiniuose viešuose puslapiuose ARO Vet elementų nerasta.
- `reports/history/project-state/latest.md` ir `latest.json` generuoja Control Center; rankiniu būdu jų neredaguoti.


## Lighthouse schedule patikra – 2026-11-17 13:56 LT
- PATIKRINTA: Lighthouse run #43915631789 buvo tikras `schedule`, ne `push` ar rankinis paleidimas. Numatyta `27 7 * * 1` (2026-11-16 07:27 UTC), run sukurtas tik 17:10:54Z ir baigtas 17:14:37Z – schedule pristatymas vėlavo apie 9 h 44 min., pats darbas truko 3 min. 43 s.
- Lighthouse artefaktas #14249118806: dog-diarrhea mobile performance 55/100, LCP 9.78 s (TTFB 4.70 s); vet-visit desktop 55/100, LCP 8.08 s (TTFB 5.22 s); vet-visit mobile 60/100, LCP 5.55 s (TTFB 7.71 s). TBT=0 ms, CLS=0 visose šiose ataskaitose; kiti 7 puslapio/įrenginio balai 86–100, accessibility/best-practices/SEO 100.
- Sprendimas: nekeisti kodo pagal vieną svyruojantį matavimą. Pakartoti per kitą suplanuotą auditą (2026-11-23) ir tikrinti TTFB / LCP tendenciją. Daily-suite ir Lighthouse vėlavimai panašūs, o pačių job trukmės trumpos – tai sustiprina schedule event eilės/pristatymo problemos hipotezę, bet neįrodo tikslios GitHub priežasties.
