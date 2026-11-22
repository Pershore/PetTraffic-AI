# Pet traffic – perdavimo ataskaita (2026-11-22)

## Pirmas neužbaigtas veiksmas

2026-11-22 13:20 LT tikrinti vienintelį šiandienos Worker AI ciklą per /health; 14:00 LT naudoti esamą verifier. Reikalauti run_date=2026-11-22, started_at po 13:20 LT, status=completed, ai_calls=5, error_code=null, keturių specialistų validžių atsakymų su konkrečiais įrodymais, Control Core sprendimo, evidence_gaps ir to paties ciklo D1 memory readback. Nekartoti ciklo. Issue #145 palikti open iki pilno įrodymo.

## Patikrinti faktai

- **Main:** HEAD 6aee359a1e7c157263a228a15769fd91228a3141; paskutinių 100 Actions run: 83 success, 5 skipped, 12 cancelled, 0 failure, 0 aktyvių. Main commit turi sėkmingą Cloudflare Pages check-run; gyvas site-check sėkmingas.
- **PR:** 9 atviri PR. #301 site-check optimizavimo PR ne draft, GitHub site-check ir Cloudflare Pages preview success; nejungtas. #298 clean URL/canonical PR draft, mergeable=false, viešo URL/canonical/sitemap pakeitimai laukia atskiro patvirtinimo. Likusių draft PR check'ai baigti success arba skipped; nėra pending/failure.
- **Daily-suite schedule:** 2026-11-22 06:10 UTC event=schedule nerasta po 60 min. grace. Issue #145 komentaras #7077367633 -> bridge #45009216953 success -> Daily-suite #45009228733 workflow_dispatch success; visi 3 job success. Artifacts: analytics #14749146491, topic-radar #14749132519. Live-check: 12 vidinių URL, sitemap, robots, 404 ir 20 istorinių 301 redirectų. Tai fallback, ne schedule įrodymas ir neatveria Worker AI vartų.
- **D1:** komentaras #7077405322 -> bridge #45009496867 success -> sync #45009507913 success, source run #45009228733. OIDC autentifikacija success, 2 privatumo filtruoti eventai, 2 D1 write/readback patvirtinimai. automation-history turi reports/history/analytics/2026-11-22.json ir reports/history/topic-radar/2026-11-22.json, abu iš source run #45009228733.
- **Site-check schedule:** 2026-11-22 05:37 UTC event=schedule nerasta. Komentaras #7077421270 -> bridge #45009615349 success -> site-check #45009628108 workflow_dispatch success. Static validator, JS syntax, compileall ir 151 Python testas success. Manual run nėra schedule įrodymas.
- **Schedule vėlavimo signalas:** paskutinis Daily-suite schedule #44914516893 sukurtas 2026-11-21 14:33:09Z (~8 h 23 min. po 06:10); site-check schedule #44910110156 sukurtas 13:41:26Z (~8 h 4 min. po 05:37). Abiem atvejais created_at ir run_started_at sutapo, o job'ai truko apie 29 s / 20 s. Vėlavimas iki run sukūrimo, ne runner eilėje; tiksli scheduler priežastis nepatvirtinta.
- **Control Center:** po Daily-suite schedule #44914516893 automatiškai suveikė #44914568958 per workflow_run, success; artefaktas #14710659852. Manual 22 d. fallback nelaikytas schedule trigerio patikra; atskiro CC catch-up nekūrėme.
- **Analytics:** GA4 2026-11-15–21: 2 aktyvūs, 2 nauji, 2 sesijos, 2 pageviews, 0 organinių sesijų; sesijos -91,7 %, peržiūros -97,7 % prieš 2026-11-08–14. GSC 2026-11-13–19: 0 impressions, 0 clicks, CTR 0 %, average position 0 (be parodymų nėra prasmingas reitingo įrodymas); 5 prioritetiniai URL Google nežinomi / dar netikrinti, sitemap pateiktas 11-10 ir pending. Ads duomenų nėra.
- **Topic radar:** 30 unikalių viešų Google News RSS nuorodų, 7 temos; tai antraščių stebėsena, ne paieškų apimtys.
- **Worker / AI:** /health 2026-11-22 09:45:19Z rodo Worker/D1 connected, site HTTP 200. Paskutinis AI ciklas 2026-11-21: started 14:45:13.639Z (16:45 LT, po 13:20), completed, 5 calls, error_code=null. Tačiau Control Core needs_evidence, 3 spragos; analytics ir content-review needs_evidence, topics ir technical-seo reviewed; memory_updated_at 14:45:20.579Z. Diagnostikos artefaktas #14711286031 yra iš 14:34Z – prieš šį ciklą, todėl jo negalima laikyti to ciklo readback. To paties ciklo D1 SELECT-only readback dar nepatvirtintas. 22 d. 11:45 LT dar prieš 13:20; šiandienos būsena WAITING, ne STALE.
- **Lighthouse:** paskutinis sėkmingas schedule #43915631789 (2026-11-16 17:10:54Z), artifact #14249118806, 10 HTML/JSON reportų; ankstesnis #43855151465 / artifact #14221237452. Dog mobile LCP 1.855→9.779 s, TTFB 97→4 347 ms; vet desktop LCP 0.536→8.078 s, TTFB 35→2 564 ms; vet mobile LCP 1.852→5.548 s, TTFB 90→2 143 ms. TBT 0 ms, CLS 0, transfer sizes stabilūs, main-thread mažas; labiau tikėtina server-response / render delay anomalija, bet priežastis nepatvirtinta. Kodo nekeista. Kadangi sėkmingas auditas dar per 7 d., papildomo dispatch nereikia. Kitas weekly schedule – 2026-11-23 07:27 UTC.
- **Svetainė / SEO:** 7 pagrindiniai puslapiai HTTP 200; 4 gidai turi po 1 H1, title, description, canonical, OG ir po 2 JSON-LD; homepage turi po 1 H1 ir JSON-LD. About/privacy neturi OG/JSON-LD. Homepage Twitter image skiriasi nuo og:image. Canonical ir sitemap naudoja .html; sitemap 7 URL, robots Allow:/, 404 ir 20 senų 301 patvirtinti live-check. Favicon.svg egzistuoja main ir yra nurodytas puslapiuose; tiesioginis SVG HTTP statusas šioje peržiūros priemonėje nepatvirtintas. Slapukų kodas GA įjungia tik po sutikimo; atmetimas išjungia GA ir pašalina analytics cookies. CSS turi 900/680/600/390 px breakpoint'us; mobile viewport screenshot užfiksuotas, vizualinė peržiūra nepatvirtinta.
- **Viešas prekės ženklas / saugumas:** site failuose nėra ARO Vet, vaistinės, affiliate ar partner tracking elementų. Viešas brand Pet traffic. Jokių production, DNS, secrets, permissions, billing ar mokamų paslaugų pakeitimų nebuvo.

## Hipotezės ir ribotumai

- 21 d. Daily-suite ir site-check vėlavimas įvyko iki run sukūrimo; GitHub runner queue nėra įrodytas kaltininkas. Scheduler priežastis nepasiekiama / nepatvirtinta.
- Lighthouse regressions sutampa su dideliu TTFB, stabiliu transfer size, 0 TBT ir 0 CLS; tai labiau rodo atsako / render delay problemą nei front-end kodo regresiją. Nekeičiame kodo be pakartotinio matavimo.
- Favicon.svg HTTP statusas tiesiogiai nepatvirtintas, nes SVG parseris grąžino nepalaikomo tipo klaidą; failas yra repo ir puslapiai jį nurodo.

## Toliau

1. 2026-11-22 po 13:20 LT tikrinti AI ciklą ir po jo D1 memory readback; naudoti 14:00 LT verifier, nekartoti ciklo.
2. 2026-11-23 po 60 min. grace tikrinti tikrus site-check 05:37 UTC ir Daily-suite 06:10 UTC event=schedule; jei nėra, naudoti tik jau įdiegtą deduplikuojamą bridge. Manual fallback nėra schedule įrodymas.
3. Po sėkmingo Daily-suite schedule patikrinti Control Center workflow_run reportą; jei jis sėkmingas per 60 min., nedubliuoti.
4. 2026-11-23 07:27 UTC patikrinti Lighthouse schedule ir 10 HTML/JSON artefaktų; jei per 7 d. jau yra sėkmingas auditas, nedubliuoti.
5. Stebėti GA4 30 s timeout stabilumą per kelis tikrus ciklus ir Search Console sitemap apdorojimą. PR #298 nesujungti be atskiro savininko patvirtinimo.

## Saugumo ribos

Viešo turinio, ARO Vet, DNS, Cloudflare production Worker/D1, secrets, repo permissions, billing ir mokamų paslaugų nekeisti. Jokių savavališkų komandų, arbitrary shell ar papildomų AI ciklų. automation-history latest.md / latest.json yra automatiniai – jų rankiniu būdu neperrašyti.
