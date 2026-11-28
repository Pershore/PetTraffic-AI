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
