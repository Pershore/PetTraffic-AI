# Pet traffic – handover 2026-11-28

## Pirmas neužbaigtas veiksmas

1. **PR #322 production vartai:** PR #322 yra draft, visi PR CI patikrinimai sėkmingi, bet pataisa dar neįdiegta. Reikia aiškaus savininko patvirtinimo sujungti PR ir paleisti Worker production deploy. Be šio patvirtinimo nekeisti produkcijos.
2. **Po deploy:** patikrinti Worker deploy workflow rezultatą, D1 migracijų būseną (tik jei workflow jas numato), gyvą /health, D1/Control Core ryšį ir heartbeat. Production deploy įrodymas nėra AI recovery įrodymas.
3. **Kitas AI ciklas:** laikytis vieno ciklo per dieną. Tikrinti run_date, started_at, status, 5 AI kvietimus, error_code, keturių specialistų įrodymus, Control Core sprendimą ir to paties ciklo D1 memory readback. Jei 13:20 LT metu trūksta snapshot'ų, pataisytas vartas turi palaukti; 15 min. heartbeat gali tęsti patikrą po 13:20. Nekartoti jau rezervuoto ciklo.
4. **Issue #145:** palikti open, kol recovery_confirmed ir visos įrodymų grandys nepatvirtintos.

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
