# Pet traffic – handover 2026-11-27

## Pirmas neužbaigtas veiksmas

1. **Daily-suite retry patikra:** iki 2026-11-27T10:13Z nėra šios dienos `event=schedule`. Owner bridge jau atliko atsarginį rinkimą: komentaras #7215536153 → bridge #45979663985 success → Daily-suite #45979691648 `workflow_dispatch` success, 3/3 job success. Fallback nėra schedule įrodymas ir neatveria Worker AI vartų. Jis prasidėjo 10:09:23Z, prieš 10:10 UTC retry; šio retry 60 min. grace baigiasi 11:10Z, o 11:10 UTC slotas dar laukia. Jei vėluojantis tikras schedule atsiras, patikrinti jo 3 job'us ir po jo Control Center `workflow_run` bei D1 sync; antro fallback nedaryti.
2. **Worker AI ciklas:** 2026-11-27 10:13Z dar iki 13:20 LT, todėl dienos ciklas WAITING. Po 13:20 tikrinti naujausią `/health`: tos pačios dienos run_date, started_at po 13:20, status=completed, ai_calls=5, error_code=null, specialistų įrodymai, Control Core sprendimas/evidence_gaps ir tos pačios dienos D1 memory readback. Jei po 13:20 nėra naujo ciklo – STALE; nekartoti, 1 ciklas per dieną.
3. **14:00 verifier:** palikti esamą greičio/post-cycle verifier atsakingą už šiandienos AI ciklo galutinę patikrą. Nedaryti papildomo Control Center dispatch, kol nėra tikro Daily-suite schedule / tinkamo workflow_run trigerio.

## Patvirtinti faktai

### GitHub / automatizacijos

- Main HEAD: `da3c2d872b4d1e22432d85c596a38acf8f0a54df`; paskutinis commit keitė tik `reports/work-log/README.md`.
- 2026-11-27 iki 10:13Z Daily-suite `event=schedule` nerasta. 06:10 ir 08:10 UTC slotų 60 min. grace jau buvo pasibaigę; 10:10 slotas dar grace lange iki 11:10Z; 11:10 slotas dar ateityje.
- Owner bridge comment #7215536153 → bridge #45979663985 success → Daily-suite #45979691648 workflow_dispatch success. Job'ai: schedule-gate, analytics, live-check, topic-radar – visi success. Artifact IDs: analytics #15188946504, topic radar #15188711554.
- Live-check: 12 vidinių URL, sitemap.xml, robots.txt, 404 ir 20 nuolatinių 301 redirectų – PASSED.
- D1 sync comment #7215621640 → bridge #45980251694 success → sync #45980279823 success; source #45979691648 validuotas kaip owner_bridge_fallback; OIDC ir 2/2 D1 write/readback success.
- Automation-history: analytics/2026-11-27.json ir topic-radar/2026-11-27.json turi source run #45979691648. Project-state/latest.md/json lieka automatinis 2026-11-26T16:46:54Z snapshot; rankiniu būdu nekeisti.
- Control Center paskutinis patvirtintas run #45861883263 (`workflow_run`, 2026-11-26, success). Po manual fallback naujo Control Center run nėra, nes šiandien nėra Daily-suite schedule event.
- Issue #145 lieka open.
- 8 PR open: #312, #306, #301, #298, #280, #267, #266, #264. Visi diverged nuo main ir 28–204 commitais behind; #301 non-draft, bet 51 behind; kiti draft. Nemerginti be atnaujinimo ir naujų patikrų.

### Analytics / SEO / UX

- GA4 property 563539278, 2026-11-20–26: 0 active/new users, 0 sessions, 0 pageviews; organic sessions nepatvirtintos dėl trūkstamo channel TOTAL.
- GSC 2026-11-18–24: 0 impressions/clicks/CTR/average position; sitemap submitted 2026-11-10, pending, last downloaded nenurodytas; penki prioritetiniai URL NEUTRAL / Google URL nežinomas / last crawl dar netikrintas.
- RSS radar: 32 unikalios antraščių nuorodos, 7 temos, 0 tuščių rezultatų; tai nėra paieškų apimtys.
- Homepage turi title/description/canonical/OG/JSON-LD, bet Twitter image skiriasi nuo OG image. About ir privacy neturi OG/JSON-LD. Keturi gidai turi pilną title/description/canonical/OG/Twitter ir po 2 JSON-LD. 404 canonical nebuvimas tyčinis.
- Visi tikrinti HTML turi viewport ir favicon nuorodą; homepage tiesiogiai veda į keturis gidus. robots.txt leidžia crawl, sitemap turi 7 URL. Consent code GA4 įkelia tik po accepted; browser E2E neatliktas. Viešame site nėra ARO Vet ar affiliate elementų.
- Paskutinis patvirtintas Cloudflare Pages deployment ID `cc006d08-3148-40a6-b43c-26e94be38b7a` (#139326898282 success, 2026-11-25). Nuo jo main keitė tik dokumentus; šiandienos GitHub runner live-check success. Tiesioginis curl/web bandymas iš šios aplinkos nepavyko dėl DNS resolverio, tai nėra produkcijos gedimo įrodymas.
- Lighthouse #45191443021 buvo push, success 2026-11-23; artifact #14826272555 turi 10 HTML + 10 JSON. Palyginus su #45173330353, LCP pagerėjo visuose 10, TBT=0, CLS=0. INP nėra; render-blocking 55–235 ms, image sizing 12–87 KiB. Sėkmingas auditas per paskutines 7 dienas, todėl manual audit nedarytas; kitas weekly slotas 2026-11-30.
- Weekly growth review #45323581220 sugeneruota 2026-11-24; dar per paskutines 7 dienas.

## Laukiančios / nepatvirtintos patikros

- 10:10 UTC Daily-suite retry event ir jo grace iki 11:10Z; 11:10 UTC retry slotas ir jo vėlesnė grace.
- 2026-11-27 13:20 LT Worker AI ciklas ir 14:00 LT post-cycle verifier.
- Browser consent E2E ir vizualus mobilus E2E neatlikti.
- Search Console penki prioritetiniai URL dar nežinomi Google; sitemap pending. Pakartotinai neteikti sitemap be naujo įrodymo.
- Lighthouse INP laboratorinis laukas nepateiktas.

## Saugumo ribos

Jokio viešo turinio, SEO metaduomenų, Worker/D1 production, DNS, secrets, permissions, billing ar ARO Vet pakeitimo. Jokių mokamų paslaugų. Issue #145 paliktas open. `automation-history/reports/history/project-state/latest.md/json` automatiniai snapshot'ai rankiniu būdu nekeičiami.


## 2026-11-27 15:11 LT – naujausia sesijos būsena po PR #320

- PR #320 sujungtas į main: merge commit d2d448afabb7efd96dbedaa6f31d865aab932df7.
- Pataisa įdiegia owner-approved fallback grandinę: Daily-suite → D1 sync/readback → Control Center → Control Center D1 sync/readback → SELECT-only diagnostics. Maksimali trukmė 25 min.; bendras polling deadline 24 min.
- CI: site-check #46004643555 success (164 testai); Sync API PR test success; Deploy API validate/test success, production deploy skipped.
- Po merge: site-check #46004827527 success; Control Center #46004827639 success; D1 sync #46004902261 success (2 event'ai, write/readback); diagnostics #46004944841 success.
- D1 2026-11-27 snapshot'ai: analytics=1, topics=1, control_center=1, recommendations=1. Kontrolės centro ir rekomendacijų įrodymai jau D1 ir perskaityti atgal.
- Live site: homepage, keturi pagrindiniai gidai, sitemap.xml, robots.txt – 200; neegzistuojantis URL – 404.
- Worker /health=200, D1 connected, heartbeat=200. 2026-11-27 AI run completed, 5 calls, error_code=null, memory updated. Control Core vis dar needs_evidence (5 gap'ai), nes AI ciklas vyko 11:20 UTC, o Control Center snapshot D1 įrašytas 13:11 UTC. Šiandien AI ciklo nekartoti; kitas ciklas 2026-11-28 13:20 Europe/Vilnius.
- 2026-11-27 Daily-suite event=schedule nerastas; owner fallback workflow_dispatch nėra schedule įrodymas. Naujas orchestratorius po merge dar neišbandytas per owner-fallback kelią; atskira post-merge push → Control Center → sync → diagnostics grandinė PATIKRINTA.
- automation-history latest.md/json snapshot #46004827639 sukurtas prieš D1 sync #46004902261; automatinio failo rankiniu būdu neperrašyti. Issue #145 lieka open.
- Kitas žingsnis: rytoj tikrinti tikrą schedule event ir po 13:20 LT vienintelio AI ciklo specialistų įrodymus bei D1 memory readback. Lighthouse weekly slotas 2026-11-30.
