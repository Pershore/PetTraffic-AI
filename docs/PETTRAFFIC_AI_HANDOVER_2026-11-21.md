# Pet traffic – perdavimo ataskaita (2026-11-21, po-merge)

## Naujausia patikrinta būsena

- **Main / produkcija:** main HEAD `3d62e4d9cea69ff2a7138b0e434d2345c69e1754`; PR #299 squash merge commit `60317ea258880ed2bb1e41bae0ee934bcbe816a1`. Cloudflare Pages production check-run success 2026-11-21 10:59:17 UTC. Main site-check push #44896871042 success; Control Center push #44896871017 success.
- **Daily-suite:** 2026-11-21 06:10 UTC schedule po 60 min. grace neįvyko. Saugus bridge #44895852313 paleido #44895862888 kaip `workflow_dispatch`; visi 3 job success. Tai fallback, ne schedule įrodymas ir neatveria Worker AI vartų.
- **Site-check:** 05:37 UTC event=schedule šiandien neįvyko. Bridge #44896801810 paleido #44896813463 kaip `workflow_dispatch`, job success; po merge main push site-check #44896871042 taip pat success. Manual run nėra schedule įrodymas.
- **Gyva svetainė:** live-check #44895862888 success: 12 vidinių URL, sitemap, robots, custom 404 ir 20 istorinių 301 redirectų. Tiesioginis browser fetch šioje aplinkoje neprieinamas; naudotas GitHub Actions HTTP monitorius.
- **Analytics:** GA4 2026-11-14–20: 2 aktyvūs / 2 nauji naudotojai, 2 sesijos, 2 peržiūros, 0 organinių sesijų. GSC 2026-11-12–18: 0 parodymų / 0 paspaudimų; sitemap submitted/pending nuo 11-10, 5 prioritetiniai URL dar nežinomi Google. GA4 30 s report timeout kode yra; šiandienos report pavyko vieną kartą, kelių ciklų stabilumas dar neįrodytas.
- **Topic radar:** 30 unikalių viešų RSS nuorodų, 7 temos; tai antraščių stebėsena, ne paieškų apimtis.
- **D1:** sync #44896017766 tiksliai apdorojo source run #44895862888, 2 privacy-filtered eventai turėjo sėkmingą D1 write/readback. Po-merge sync #44896902196 success; diagnostikos artifact #14704292595 patvirtina analytics_snapshot=1, topic_snapshot=1, control_center_snapshot=6, recommendation_snapshot=6.
- **Worker AI:** read-only D1 diagnostika #44896924905 (10:59:49Z): šiandienos agent run missing, 0 calls, 4 specialistai missing, Control Core missing, memory paskutinį kartą atnaujinta 2026-11-20T15:30:36.388Z. Iki 13:20 LT tai WAITING, ne STALE; AI ciklo rankiniu būdu nekviesti.
- **Control Center pataisa:** PR #299 merged; bridge pašalintas iš Control Center workflow_run šaltinių, deduplikacija atsižvelgia į workflow_run. Po merge Control Center paleistas nuo main push #44896871017. Senas PR #297 uždarytas kaip superseded.
- **Lighthouse:** paskutinis sėkmingas #43915631789 (11-16 17:10Z), 10 HTML/JSON. Dog mobile LCP 1.855→9.779 s, vet desktop 0.536→8.078 s, vet mobile 1.852→5.548 s; TTFB išaugo, TBT=0, CLS=0, transfer size stabilus. Tai server-response / render-delay anomalija, ne įrodyta kodo regresija; papildomas dispatch nedarytas, nes per 7 d. yra sėkmingas auditas.
- **SEO:** robots Allow:/, sitemap 7 URL; 4 gidai turi title/description/canonical/OG/JSON-LD/H1. About/privacy trūksta OG; homepage Twitter image nesutampa su og:image; canonical/sitemap tebenaudoja .html. PR #298 draft, 5 commits behind main. Cookie consent loads GA only after consent; reject disables GA and removes analytics cookies. Responsive CSS breakpoints present.

## Pirmas neužbaigtas veiksmas

Po 13:20 LT patikrinti vienintelį 2026-11-21 Worker AI ciklą per `/health`: run_date, started_at, status, ai_calls, error_code, keturi specialistų raportai, Control Core, evidence_gaps ir D1 memory readback. Naudoti esamą 14:00 LT verifier; nekartoti ciklo.

## Toliau

1. Rytoj po 06:10 UTC + 60 min. grace patikrinti tikrą Daily-suite `event=schedule`; jei jo nėra, tik tada naudoti jau įdiegtą bridge ir atskirti fallback nuo schedule įrodymo.
2. Atskirai patikrinti site-check `event=schedule` po jo 05:37 UTC laiko; manual run nėra schedule įrodymas.
3. Pirmadienį 07:27 UTC patikrinti Lighthouse `event=schedule` ir 10 HTML/JSON reportų.

## Saugumo ribos

Nekeisti DNS, Cloudflare Worker/D1 production, secrets, repo permissions, billing, ARO Vet ar viešo turinio. Jokio mokamo serviso, savavališko shell, naujų priklausomybių ar AI ciklo pakartojimo. automation-history latest.md/latest.json rankiniu būdu nekeisti.
