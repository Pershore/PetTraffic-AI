# Pet traffic – perdavimo ataskaita (2026-11-19)

## Sesijos išvada

AI ciklas lapkričio 18 d. techniškai įvyko ir įrašė Control Core bei atmintį į D1, tačiau įrodymų kokybė liko nepakankama. Svarbiausias sisteminis incidentas – kelių GitHub Actions schedule paleidimų vėlavimas apie 9 val.; tiksli priežastis dar nepatvirtinta.

## Patvirtinta AI / D1 būsena

- Gyvas Worker /health 2026-11-19 08:00:13Z: Worker API ir D1 connected, Control Core schema connected, heartbeat site HTTP 200.
- Paskutinis AI ciklas: run_date=2026-11-18, started_at=15:45:13Z, completed_at=15:45:25Z, status=completed, ai_calls=5, error_code=null.
- Control Core: run_date=2026-11-18, status=needs_evidence, decision_json_status=valid, 4 evidence gaps; specialist statuses: analytics/topics/content-review=needs_evidence, technical-seo=reviewed.
- Memory updated_at=2026-11-18T15:45:25.164Z, tas pats ciklas; /health patvirtina agreguotą D1 readback.
- D1 diagnostikos artifact #14441572873 / run #44336957542 sukurtas 15:33:21Z – prieš AI ciklą 15:45Z. Jo agent_run=missing yra prieš-ciklo momentinė būsena, ne po-ciklo nesėkmė. Konkrečios spragų eilutės dar nepatikrintos.
- Nekartoti 2026-11-18 ciklo. Issue #145 lieka open, kol nėra recovery_confirmed ir visų specialistų pagrįstų rezultatų.

## Schedule incidentas

| Workflow | Cron UTC | Tikras schedule start 2026-11-18 UTC | Vėlavimas |
|---|---:|---:|---:|
| Site-check | 05:37 | 14:29:58 | ~8 val. 53 min. |
| Daily-suite | 06:10 | 15:32:01 | ~9 val. 22 min. |
| Google API connectivity | 06:57 | 16:11:28 | ~9 val. 14 min. |

- Daily-suite #44336724612: event=schedule, 3/3 job success, ~36 s. Sync #44336852000: source event=schedule, workflow ID 418322987, source run ID #44336724612; analytics/topic snapshot D1 write/readback success.
- Worker AI catch-up įvyko 15:45Z / 17:45 LT, po vėlyvo snapshot sync. Tai rodo, kad pati job trukmė nėra 9 val. vėlavimo priežastis.
- 2026-11-19 10:07 LT: naujų tos dienos site-check, Daily-suite ir connectivity schedule run dar nėra. Tai laukianti būsena prieš 13:20 AI ciklą, ne šios dienos AI nesėkmė.
- Tiksli GitHub schedule vėlavimo priežastis NEPATVIRTINTA; Actions administravimo nustatymai per dabartinę integraciją nematomi.

## Įvesties duomenų kokybė (Daily-suite #44336724612)

- GA4 laikotarpis 2026-11-11–17: 4 aktyvūs naudotojai, 2 nauji, 18 sesijų, 51 puslapių peržiūra, 0 organinių sesijų.
- GSC laikotarpis 2026-11-09–15: 0 parodymų, 0 paspaudimų, nėra užklausų ar puslapių eilučių; sitemap pateiktas, apdorojimas pending.
- Temų radaras: 27 unikalios RSS nuorodos, 7 temos. Tai viešų antraščių signalas, ne paieškų apimtys.
- Šie duomenys neleidžia išgalvoti paklausos ar tendencijų; `needs_evidence` yra tinkamas atsargus statusas, kol nėra papildomų įrodymų.

## PR / automatizacijos

- PR #288 draft: diagnostikos triggerio perkėlimas po D1 sync. Head CI buvo success; production deploy neatliktas. PR nekeičia AI ciklo ar evidence status.
- Issue #145 ir #248 lieka open.
- Esamas pagrindinis koordinatorius numatytas 11:45 LT, nepriklausoma patikra 12:00 LT, Worker AI 13:20 LT, post-cycle verifier 14:00 LT.
- 2026-11-18 14:00 LT verifier realiai startavo 15:05 LT ir baigė 15:17 LT, prieš vėlyvą 17:45 LT AI catch-up. Todėl jis negalėjo patvirtinti vėlyvo ciklo. 2026-11-19 verifier numatytas 14:00 LT; jei šiandienos schedule vėluos ir AI catch-up įvyks po verifier, būtina vėlesnė to paties run_date patikra (be antro AI ciklo).

## Kiti veiksmai

1. Po 13:20 LT tikrinti 2026-11-19 Worker /health: run_date, started_at, status, 5 AI calls, error_code, Control Core ir memory readback. Jei dar nėra eligible schedule snapshot, palikti LAUKIA – nekartoti ciklo.
2. Patikrinti tikrą 2026-11-19 Daily-suite event=schedule ir D1 source provenance/readback. Manual/push/workflow_run nelaikyti schedule įrodymu.
3. Po 14:00 LT verifier peržiūrėti jo rezultatą. Jei Daily-suite vėluos ir AI catch-up bus po verifier, patikrinti tą patį ciklą vėliau, nekurti antro.
4. Toliau tirti GitHub Actions schedule vėlavimą; tiksli priežastis lieka nežinoma, kol nepatikrinti repository Actions enablement nustatymai.
5. PR #288 nejungti aklai; jo paskirtis tik diagnostikos eiliškumas.

## Saugumo ribos

Šio audito metu nebuvo keistas kodas, Worker/D1 produkcija, DNS, secrets, permissions, billing, ARO Vet ar viešas turinys. Naujų mokamų paslaugų nėra. Issue #145 neuždarytas.
