# Pet traffic – handover 2026-11-28

## Pirmas neužbaigtas veiksmas (atnaujinta 2026-11-28 12:20 LT)

1. **PR #323 CI ir saugumo vartai:** DRAFT PR #323 `fix/owner-bridge-child-sync-lifecycle-20261128` sprendžia patvirtintą tėvinio owner bridge / child D1 sync ciklinę priklausomybę. Sync workflow test #46135981250 success; site-check #46135981226 tuo metu in_progress. Vietinis pilnas testų paleidimas blokuotas DNS resolverio. Prieš merge sulaukti visų CI rezultatų ir gauti aiškų savininko patvirtinimą, nes keičiasi owner-bridge kilmės validacija.
2. **2026-11-28 Daily-suite:** tikro `event=schedule` nėra. Owner fallback #46132934330 `workflow_dispatch` success su 3/3 darbais ir live-check; tačiau bridge #46132925488 failure, nes child sync #46132981101 atmetė dar vykstantį tėvinį bridge. Pakartotinis sync #46133674274 taip pat failure. D1 write/readback nėra. Šiandienos Daily-suite/sync komandų nekartoti; workflow_dispatch nėra schedule įrodymas.
3. **Worker AI ciklas:** iki 13:20 LT būsena WAITING. Po 13:20 patikrinti naujausią /health: tos pačios dienos run_date, started_at po 13:20, completed, 5 AI calls, error_code=null, 4 specialistai, Control Core ir to paties ciklo D1 memory readback. Kadangi nėra validžių šiandienos D1 snapshot'ų, ciklas gali likti nepaleistas; jei po lango nėra naujo ciklo – STALE, nekartoti. 14:00 verifier paliekamas galutinei patikrai.
4. **Control Center / Issue #145:** po fallback Control Center nebuvo paleistas, nes D1 sync nepavyko. Naujo /pettraffic-run-control-center komentaro nedėti. Issue #145 palikti open iki pilno recovery įrodymo.

## Patvirtinta diagnostika

- 2026-11-27 AI ciklas: run_date=2026-11-27, started_at=2026-11-27T11:20:23.466Z, 5 AI kvietimai, completed, error_code=null.
- Control Center / recommendations D1 snapshot'ai įrašyti apie 2026-11-27T13:11Z – po AI ciklo. Technical-SEO specialistui trūko Control Center snapshot'o.
- Ankstesnis vartas reikalavo tik bent vieno analytics/topic snapshot, o ne visų keturių rūšių.
- Kiti specialistų trūkumai (analytics, content-review) turi būti vertinami atskirai; vien laiko pataisa jų automatiškai neišsprendžia.

## PR #322

- Šaka: fix/ai-evidence-gate-require-all-snapshots-20261128.
- PR: https://github.com/Pershore/PetTraffic-AI/pull/322 (draft).
- Pataisa reikalauja analytics, topics, control_center ir recommendation snapshot'ų iš tos pačios Vilniaus dienos.
- Control Center snapshot'ams tikrinama workflow ID 416336983, source provenance, laiko ribos ir owner-bridge fallback laukai.
- Control Center ir recommendation įrašai privalo būti iš to paties Control Center run.
- Trūkstant įrodymų AI ciklas dar nepradedamas ir dienos run nerezervuojamas; esamas 15 min. heartbeat catch-up gali pakartoti tik vartų patikrą.

## CI įrodymai

- Site-check #46121610160: success, 164 testai.
- Worker API #46121610183: success, 83 Node testai, 27 Python testai, Cloudflare resource validation success.
- Sync API #46121610243: success.
- Cloudflare Pages preview: success.
- Worker production deploy ir snapshot sync PR event metu skipped.
- PR #322 nėra sujungtas; runtime pataisa nepatvirtinta.

## Saugumas

Nekeista main, Worker production, D1 schema/duomenys, DNS, secrets, permissions, billing, ARO Vet ar viešas turinys. Automation-history latest.md/json yra automatiškai generuojami ir rankiniu būdu nekeistini. Issue #145 paliktas open.


## Papildoma 2026-11-28 content-review patikra

- Nustatyta, kad content-review įvestis buvo apribota pirmomis 900 teksto raidėmis, o šaltinių nuorodos keturiuose straipsniuose pateiktos pabaigoje. PR #322 dabar perduoda 700 simbolių ištrauką ir iki 3 išorinių šaltinių nuorodų iš viso HTML. Vidinės nuorodos neįtraukiamos; papildomų fetch ar AI kvietimų nėra.
- Testas patikrina, kad šaltinių nuorodos, esančios po ilgo teksto, išlieka agento įvestyje.
- Analytics spraga atskira ir reali: 2026-11-27 snapshot metrikos nulinės, top pages/queries tušti, organinės sesijos nepatvirtintos, sitemap pending, prioritetiniai URL Google nežinomi. Nekeisti statuso į reviewed be naujų duomenų.
- Naujausias CI: site-check #46121855942 (164 testai) success; Worker API #46121855947 (84 Node + 27 Python testai, Cloudflare validation) success; Sync API #46121855949 success; Pages preview success. Production deploy skipped.


## 2026-11-28 09:39 LT – PR #322 sujungtas ir Worker įdiegtas

- Savininko patvirtinimu PR #322 pažymėtas ready ir squash sujungtas į main: `a1a3132b95c04fbca2110bf88571c06542e0c2c1`.
- Production Worker deploy workflow #46122167256 (event `push`) – success. D1 migracijų nebuvo; Worker versija `f771441b-6d64-4807-8573-9f0f9df9dbb5`.
- Deploy workflow realiai patikrino D1 ir Control Core schema ryšį, neautentifikuoto `/v1/events` 401 atsakymą ir abu Cron grafikus `*/15 * * * *`, `20 10,11 * * *`.
- Po merge: site-check #46122167222, automatic work-log #46122167317 ir central control center #46122167433 – success. Tai `push`, ne `schedule`.
- Gyvas `/health` 2026-11-28T07:39Z vis dar rodo 2026-11-27 AI ciklą: 5 kvietimai, `completed`, `error_code=null`, bet Control Core `needs_evidence`, 5 spragos. Todėl AI recovery **NEPATVIRTINTA**. Šiandien nekartoti ciklo; laukti vienintelio 13:20 LT lango, tada tikrinti visų specialistų įrodymus, Control Core ir to paties ciklo D1 memory readback.
- Analytics agentas atskirai lieka `needs_evidence`: 2026-11-27 GA4/GSC snapshot be pakankamų metrikų, top pages/queries nėra, organic sessions nepatvirtintos, sitemap pending. Issue #145 lieka open.
- `automation-history/reports/history/project-state/latest.md/json` yra automatiškai generuojami; nekeisti rankiniu būdu. 07:39Z snapshot pažymėjo daily-suite `schedule` 06:10Z kaip neįvykusį; vėlesni `push` paleidimai jo neatstoja.


## 2026-11-28 12:20 LT – patvirtintas owner-bridge sync ciklo gedimas

- Pirmo sync #46132981101 provenance validacija baigėsi 09:59:17Z; parent bridge #46132925488 baigėsi failure 09:59:28Z, nes laukė child sync. Tiksli priežastis – sync reikalavo completed/success tėvinio bridge, nors bridge tuo metu turėjo būti in_progress. DRAFT PR #323 išlaiko tikslius owner ir timestamp vartus, bet leidžia šią laukiančią tėvinio workflow būseną; bridge turi užbaigti visą grandinę success.
- Daily-suite #46132934330: analytics/topic/live-check success; artifacts #15258249312 ir #15257544109. Live-check: 12 vidinių URL, sitemap, robots, 404 ir 20 redirectų passed. Fallback nėra schedule įrodymas.
- Antras sync #46133674274 failure; D1 write/readback neįvyko. /pettraffic-sync-latest komentaras #7237685626 jau panaudotas; šiandien daugiau nebekartoti.
- GA4 2026-11-21–27: 0 naudotojų, sesijų ir pageviews; kanalų TOTAL nėra, organic sessions nepatvirtintos. GSC 2026-11-19–25: 0 parodymų/paspaudimų; sitemap pending, 5 prioritetiniai URL Google nežinomi. RSS radaras: 32 unikalios nuorodos, 7 temos – ne search volume.
- Lighthouse artifact #14826272555 (2026-11-23) prieš #14818555756: LCP pagerėjo visuose 10, TBT 0 ms, CLS 0; INP nėra. Render-blocking ~55–235 ms, image sizing ~12–87 KiB – nepatvirtintos regresijos.
- Worker paskutinė diagnostika #46122216652: D1/Control Core/site/DB healthy, heartbeat iki 07:45:12Z. Iki 13:20 LT AI ciklas WAITING. Pages production deploy nuo 11-25 nebuvo naujas, nes site kodas nepakito; 11-28 live-check success.
- Jokių production Worker/D1, DNS, secrets, permissions, billing, ARO Vet ar viešo turinio pakeitimų. automation-history latest.md/json nepakeisti rankiniu būdu.
