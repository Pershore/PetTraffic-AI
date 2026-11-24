# Pet traffic – perdavimo ataskaita (2026-11-24)

## Post-merge patikra – 2026-11-24 12:43 LT

- **PR #310 – ATLIKTA:** dokumentų PR sujungtas squash commit `90950241a9df8d3a0b1ddab27fc76f10a8e2f905`; automatinis work-log commit atnaujino main į `9576615e69c3f9c69df762f5ec7a12db74471fb9`.
- **Cloudflare Pages – PATIKRINTA:** merge commit check success, deployment ID `0830c6fa-a087-4c6f-9e5c-504877d1372e`; po merge homepage HTTP 200. Site-check #45377332777 ir automatinis work-log #45377332674 success.
- **CI:** PR #310 site-check #45377187885 success, 160 testų OK; Cloudflare Pages preview success. Po merge site-check success.
- **Pakeitimų ribos:** PR #310 keitė tik PROJECT_MEMORY, work-log ir handover dokumentus. Viešas puslapio turinys, Worker/D1 production, DNS, secrets ir teisės nepakeistos.

## Naujausias papildymas – 2026-11-24 12:35 LT

- **Main / produkcija – PATIKRINTA:** main HEAD `1f14b06db7729ca1a8a5c4f9f0b536015460233d`; Cloudflare Pages check success, paskutinis patvirtintas deployment ID `04f96fe5-d1c7-424b-bd10-003faac1c286`. Vieša svetainė veikia, produkcijos pakeitimų neatlikta.
- **Daily-suite schedule – NEPATVIRTINTA:** 2026-11-24 nėra `event=schedule` vykdymo. Po 60 min. grace savininko bridge #45374783438 sėkmingai paleido Daily-suite #45374802744 kaip `workflow_dispatch`; visi 3 job'ai success. Tai tik atsarginis duomenų rinkimas, ne schedule įrodymas ir neatveria Worker AI vartų. Kitas retry 11:10 UTC / 13:10 LT dar laukiamas.
- **Live-site check – PATIKRINTA:** Daily-suite live-check patikrino 12 vidinių URL, sitemap.xml, robots.txt, 404 ir 20 istorinių 301 redirectų. Homepage, keturi gidai, about ir privacy HTTP 200; nežinomas URL HTTP 404. Robots/sitemap HTTP 200.
- **D1 sync – PATIKRINTA:** bridge #45375375640 → sync #45375406125, source run #45374802744 (`workflow_dispatch`). OIDC success, du privatumo filtruoti snapshot'ai įrašyti ir perskaityti iš D1 (2/2); automation-history archyve yra 2026-11-24 analytics/topic snapshot'ai.
- **Site-check schedule – NEĮVYKO; fallback PATIKRINTA:** šiandien schedule nėra. Bridge #45375880205 → site-check #45375907195 workflow_dispatch success; validator, compileall, JS syntax ir 160 testų OK.
- **Control Center – PATIKRINTA:** bridge #45376125329 → Control Center #45376152167 workflow_dispatch success. automation-history latest snapshot generated_at 2026-11-24T10:35:07Z rodo REIKIA DĖMESIO dėl trūkstamo Daily-suite schedule. Nėra atskiro Control Center schedule.
- **GA4/GSC – prieiga PATIKRINTA, augimo signalas NEPATVIRTINTAS:** GA4 563539278 laikotarpis 2026-11-17–23: 0 aktyvių/naujų naudotojų, 0 sesijų, 0 peržiūrų; kanalų TOTAL neatitikimas, organinės sesijos nepatvirtintos. GSC 2026-11-15–21: 0 parodymų/paspaudimų, sitemap submitted 2026-11-10 ir pending, Google dar neatsisiuntė, 5 prioritetiniai URL nežinomi / dar netikrinti. Nulis nėra API klaidos ar neindeksavimo įrodymas.
- **Temų radaras – NEVEIKIA laikinai:** 7/7 Google News RSS užklausų HTTP 503, 0 antraščių; tai nėra keyword volume. Turinys nekurtas.
- **Lighthouse – PATIKRINTA kaip push:** #45191443021 event=push, 10 HTML + 10 JSON reportų. Mobile performance 98–100, LCP 1.66–2.37 s, TBT 0, CLS 0; desktop 100; accessibility/SEO/best-practices 100. Palyginus su ankstesniu #45173330353, visi pagrindiniai mobile LCP pagerėjo arba išliko panašūs, home TBT sumažėjo nuo 416.5 ms iki 0. Render-blocking 154–235 ms ir image sizing ~12–87 KiB tik optimizavimo kandidatai. 2026-11-23 schedule įvykio nerasta, tačiau sėkmingas push auditas per 7 dienas, todėl Lighthouse bridge nenaudotas.
- **Worker / D1 / AI – sveikata PATIKRINTA, AI LAUKIA:** /health 2026-11-24T10:30:14Z Worker/D1/Control Core schema connected, heartbeat HTTP 200. Paskutinis AI run 2026-11-22 completed, 5 calls, error_code=null; Control Core needs_evidence su 4 spragomis; analytics/topics/content-review needs_evidence, technical-seo reviewed; memory present, atnaujinta 2026-11-22T14:30:22.711Z. 12:35 LT dar iki 13:20, todėl WAITING. Nekartoti AI ciklo.
- **SEO / UX – PATIKRINTA:** keturi gidai turi title/meta/canonical .html, po 1 H1, Article + BreadcrumbList JSON-LD ir OG/Twitter metadata. About/privacy neturi OG ir JSON-LD; homepage Twitter image skiriasi nuo og:image. site.js įkeliamas visuose 7 puslapiuose; GA4 tik po sutikimo, atmetus išjungiamas ir pašalinami GA cookies; interaktyvus browser E2E neatliktas. Favicon.svg egzistuoja ir puslapiai jį nurodo, bet tiesioginis live SVG statusas nepatvirtintas. ARO Vet / affiliate elementų nerasta.
- **PR / CI:** 7 PR open. #306 draft: dabartinio head test + Cloudflare validation success, deploy skipped; #301 mergeable=false; #298/#264 draft canonical pataisoms; #280/#267/#266 seni docs/analytics draft'ai. 4 paskutinio 100 run lango failure buvo senų PR revizijų testų neatitikimai; dabartinis main site-check ir dabartinio #306 head patikros sėkmingos. Issue #145 paliktas open.
- **Saugumas:** jokių Worker/D1 production, DNS, secrets, permissions, billing, mokamų paslaugų, ARO Vet ar viešo turinio pakeitimų.

## Pirmas neužbaigtas veiksmas

1. Laukti 2026-11-24 11:10 UTC / 13:10 LT Daily-suite retry. Tik `event=schedule` įrodo schedule. Po sėkmės patikrinti tris job'us, retry gate, Control Center `workflow_run` per 60 min. ir atitinkamą D1 sync/readback. Nedubliuoti.
2. Po 13:20 LT patikrinti vienintelį 2026-11-24 Worker AI ciklą per /health ir esamą 14:00 LT verifier: run_date, started_at po 13:20, completed, ai_calls=5, error_code=null, visų keturių specialistų įrodymai, Control Core sprendimas, evidence_gaps ir to paties ciklo memory readback. Issue #145 neuždaryti be pilno recovery įrodymo.
3. 2026-11-30 patikrinti tikrą Lighthouse Monday `event=schedule` ir retry gate; 2026-11-23 push audito nelaikyti schedule įrodymu.
4. Paruošti, bet nepublikuoti SEO metaduomenų pataisas homepage Twitter/OG vaizdo neatitikimui ir about/privacy OG/JSON-LD trūkumui. Viešus metaduomenis keisti tik po atskiro patvirtinimo.

## Patikrinti workflow įrodymai

- Daily-suite bridge #45374783438 → run #45374802744 success (3/3 jobs).
- Snapshot sync #45375375640 → run #45375406125 success; D1 write/readback 2/2.
- Site-check bridge #45375880205 → run #45375907195 success; 160 tests OK.
- Control Center bridge #45376125329 → run #45376152167 success; latest snapshot 10:35:07Z.
- Lighthouse push audit #45191443021 success; 10 HTML/JSON pairs.
- Cloudflare Pages deployment ID `04f96fe5-d1c7-424b-bd10-003faac1c286` success.

## Nekeičiamos saugumo ribos

Viešo turinio automatiškai nepublikuoti. Nekeisti ARO Vet, DNS, Cloudflare production Worker/D1, secrets, paskyrų teisių, billing ar mokamų paslaugų. automation-history latest.md/latest.json atnaujina tik automatiniai workflow; jų rankiniu būdu neperrašyti.
