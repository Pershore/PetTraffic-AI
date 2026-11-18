# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-18T13:00:00.366780+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 44309248812
- Šaltinio commit: af870781e24d473157893961dca396cb8389b4b6

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-18 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-17T15:53:16Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Lighthouse auditas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 14 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-18 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-17T15:53:16Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/44307684666
- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-17. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Nėra.

## AI agentų ir atminties patikra

- Būsena: **stale** – Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-17.
- Patikros šaltinis: https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Rekomendacijos

- **[medium] Patikrinti Google paieškos matomumą** – Patikrinti URL indeksavimo būseną, sitemap apdorojimą ir ar svarbiausi puslapiai prieinami Googlebot.
- **[info] Stebėti Google sitemap apdorojimą** – Pakartotinai patikrinti kitame cikle; sitemap pakartotinai neteikti, jei jis jau pateiktas.
- **[high] Pašalinti automatizacijų būklės problemas** – Atidaryti centrinio valdymo GitHub įspėjimą ir taisyti konkretaus proceso klaidą.

## Nekeičiamos saugumo ribos

- ARO Vet svetainės, kodo ir infrastruktūros nekeisti be atskiro leidimo.
- Svetainės turinio automatiškai nepublikuoti; būtinas vartotojo patvirtinimas.
- Jokių mokamų API ar paslaugų be atskiro biudžeto patvirtinimo.
- Nekeisti DNS, Cloudflare teisių ar produkcinės infrastruktūros be atskiro patvirtinimo.
- AI rekomendacijos yra patariamosios; modelio išvestys nesuteikia vykdymo teisių.

> Tik agreguotos procesų būsenos ir rekomendacijų santrauka; be lankytojų lygmens duomenų, žalių paieškos užklausų ar paslapčių.

## Papildoma nepriklausoma patikra – 2026-11-18 13:00 UTC

- **PATIKRINTA – naujausi analitikos snapshot:** Daily-suite #44307684666 buvo `workflow_dispatch`, ne `schedule`; analytics #14427319612 ir topic-radar #14428862290 artefaktai išsaugoti. GA4 2026-11-11–17: 4 aktyvūs, 2 nauji, 18 sesijų, 51 peržiūra; AI Assistant 11 sesijų, Direct 7, organinės sesijos 0. GSC 2026-11-09–15: 0 parodymų, 0 paspaudimų, CTR 0,0 %, pozicija 0,0; query/page eilučių nėra. Sitemap apdorojimas laukia.
- **ATLIKTA – D1 sinchronizacija:** sync #44308657828 patvirtino Daily-suite šaltinį #44307684666 (`workflow_dispatch`, workflow ID 418322987), paruošė 2 privatumo filtruotus įvykius ir sėkmingai patvirtino D1 write/readback.
- **PATIKRINTA – po-sync D1 diagnostika:** run #44309206547, artifact #14428314798, sugeneruotas 2026-11-18T12:59:51.708Z; 7 SELECT-only užklausos, 0 D1 įrašymų. Šios dienos įvykiai: analytics_snapshot=1 ir topic_snapshot=1 (source run #44307684666), control_center_snapshot=9 ir recommendation_snapshot=9 (naujausias source run #44309126151).
- **NEVEIKIA / LAUKIA – AI:** po sėkmingo D1 duomenų perdavimo 2026-11-18 AI run vis dar `missing`, `ai_calls=0`, `error_code=null`; keturi specialistai, coordinator ir šiandienos Control Core įrašas `missing`. Memory present, bet paskutinis atnaujinimas 2026-11-17T12:00:21.622Z, `needs_evidence`. Manual snapshot įkėlimas AI ciklo nepaleido.
- **PATIKRINTA – schedule:** Daily-suite 2026-11-18 `event=schedule` nėra (paskutinis #44119444026, 2026-11-17 15:53 UTC); Site-check 2026-11-18 `event=schedule` nėra (paskutinis #44107609945, 2026-11-17 14:50 UTC; naujausias #44309206637 buvo push, success). Lighthouse paskutinis schedule #43915631789, 2026-11-16 17:10 UTC; savaitinis kitas numatomas 2026-11-23. Control Center #44309248812 buvo `workflow_run`, success, event-driven.
- **PATIKRINTA – GitHub priežiūra:** `main` prieš paskutinį dokumentavimo įrašą `af870781e24d473157893961dca396cb8389b4b6`; 7 atviri draft PR (#288, #280, #267, #266, #264, #263, #261), 2 atviri issue (#145, #248). PR #288 šaka 2 commits ahead, 4 behind main; draft, nesujungtas.
- **ATLIKTA:** papildyta nepriklausomos patikros būsena. ARO Vet, viešas turinys, produkcinis Worker/D1, DNS, secrets, paskyrų teisės ir mokamos paslaugos nekeistos.


## 2026-11-18 papildomas Worker cron ir AI provenance patikslinimas (13:00 UTC)

- **PATIKRINTA:** Cloudflare Worker schedules registruoti (`*/15 * * * *`, `20 10,11 * * *`); read-only cron diagnostika #44306925697 success, heartbeat pažengė nuo 12:45:13.387Z iki 13:00:13.463Z; D1, Control Core schema, site ir database healthy.
- **PATIKRINTA:** rankinis Daily-suite #44307684666 ir D1 sync #44308657828 success; D1 readback #44308744802 rodo vieną analytics ir vieną topic snapshot, abu iš `workflow_dispatch` šaltinio. Tikras 2026-11-18 `event=schedule` Daily-suite nėra.
- **LAUKIA – Worker AI:** `worker/src/agents.mjs` reikalauja tos pačios dienos snapshot su `provenance.source_event="schedule"` ir workflow ID `418322987`; rankinis fallback AI vartams netinka. D1 `agent_run` šiandien missing, `ai_calls=0`, `error_code=null`; Control Core šiandien missing; memory present, bet paskutinis run_date 2026-11-17 (`needs_evidence`, `insufficient_evidence` ir `other`). AI ciklas nepatvirtintas; jokių rankinių AI endpointų nekviesta.
- **PATIKRINTA:** Control Center #44308676333 success, bet `recovery_confirmed=false`; issue #145 paliktas open. PR #288 draft, 2 ahead / 4 behind main, mergeable=false; CI ant esamo head sėkmingas, PR nesujungtas.
- **NEPATVIRTINTA:** `content-review_model_output_invalid_json` šiandien negalima pakartotinai patikrinti, nes AI ciklas neįvyko. Greičio pagerėjimas neskaičiuotas; kontroliuojamo prieš/po matavimo nėra.

Kitas veiksmas: laukti tikro Daily-suite `event=schedule`, po jo patikrinti Control Center ataskaitą, Worker AI `started_at` po 13:20 LT, 5 AI calls, `status=completed`, `error_code=null`, memory present ir `recovery_confirmed=true`. Issue #145 neuždaryti iki visų šių įrodymų.

## Worker cron ir AI provenance vartai – patvirtinta 2026-11-18

- **PATIKRINTA:** Worker cron diagnostika #44306925697 buvo `workflow_dispatch` (ne schedule), tačiau Cloudflare API patvirtino registruotus cron grafikus `*/15 * * * *` ir `20 10,11 * * *`. Heartbeat sėkmingai pasistūmėjo nuo `2026-11-18T12:45:13.387Z` iki `2026-11-18T13:00:13.463Z`; D1, Control Core schema, svetainė ir DB healthy. Tai patvirtina Worker cron ir heartbeat veikimą, bet ne GitHub Actions Daily-suite schedule.
- **PATIKRINTA – AI vartų priežastis:** `worker/src/agents.mjs` funkcija `isEligibleScheduledDailySuiteSnapshot` reikalauja tos pačios Vilniaus dienos `analytics_snapshot` arba `topic_snapshot`, kurių `provenance.source_event` yra `schedule` ir `source_workflow_id` yra `418322987`. `20 10,11 * * *` Worker grafike pagrindinis AI laikas yra 13:20 Europe/Vilnius; `*/15 * * * *` heartbeat gali atlikti catch-up tik gavus tinkamą tos dienos schedule snapshot.
- **PATIKRINTA:** Daily-suite #44307684666 turi `source_event=workflow_dispatch`; net ir po sėkmingo D1 sync #44308657828 šis snapshot sąmoningai neatitinka AI vartų. Naujausia read-only diagnostika #44309206547 (2026-11-18T12:59:51Z, artifact #14428314798) patvirtina `analytics_snapshot=1`, `topic_snapshot=1`, bet `agent_run=missing`, `ai_calls=0`, `error_code=null`, visi specialistai missing, šiandienos Control Core missing; memory present, paskutinis run_date 2026-11-17.
- **IŠVADA:** Worker cron/heartbeat konfigūracija patvirtinta; šiandienos AI ciklą blokuoja tinkamo GitHub `event=schedule` Daily-suite šaltinio nebuvimas. Kodėl GitHub Daily-suite schedule įvykis neatsirado, dar nenustatyta; workflow YAML cron nėra paleidimo įrodymas.
- **Kitas veiksmas:** sulaukti tikro Daily-suite `event=schedule`; po jo patikrinti D1 provenance ir `isAgentCatchUpEvent` rezultatą, tada patvirtinti AI run, 5 AI calls, specialistų rezultatus, Control Core ir memory readback. Issue #145 palikti open iki `recovery_confirmed=true`.


## 2026-11-18 13:05 UTC – popietinis greičio ir Worker post-cycle auditas

- **Būsena: REIKIA DĖMESIO.** Pagrindinė kliūtis išlieka tikro Daily-suite `event=schedule` nebuvimas 2026-11-18. YAML cron `10 6 * * *` yra, tačiau šiandienos run istorijoje schedule įvykio nėra; paskutinis tikras schedule #44119444026 (2026-11-17 15:53:16Z, 43 s, 3/3 job success). Šiandienos #44307684666 buvo tik `workflow_dispatch` (33 s), todėl netinka AI provenance vartams.
- **PATIKRINTA – pagrindinė šaka:** main HEAD `9702a02cdd80612fcf1b034ba50a6042557632ae`; paskutiniai dokumentavimo commit 9702a02, fccf2ca, af870781. 7 atviri draft PR (#288, #280, #267, #266, #264, #263, #261). PR #288 draft, 2 ahead / 6 behind, mergeable=true; nesujungtas.
- **PATIKRINTA – realios trukmės:** Daily-suite manual #44307684666 33 s; analytics 29 s, topic-radar 14 s, live-check 20 s. Ankstesnis schedule #44119444026: 43 s; atitinkami job 40/14/28 s. Skirtumai užregistruoti kaip faktiniai matavimai, bet greičio pagerėjimas neteigiamas. Site-check #44309623892 push success 18 s; Control Center #44309248812 workflow_run success 32 s; sync #44309353178 workflow_run success 14 s; D1 diagnostika #44309353359 success 13 s; Lighthouse #43915631789 weekly schedule success 223 s. Worker cron diagnostika #44306925697 success 15 min. 13 s dėl suplanuoto heartbeat laukimo.
- **PATIKRINTA – Worker /health ir infrastruktūra:** cron grafikai `*/15 * * * *` ir `20 10,11 * * *`; heartbeat pasistūmėjo 12:45:13.387Z → 13:00:13.463Z. /health stebėsena patvirtino D1, Control Core schema, site ir DB healthy. Control Center artifact #14429127311 sukurtas 13:00:00Z, po 13:20 LT; report success, `recovery_confirmed=false`, 3 rekomendacijos.
- **LAUKIA – AI / D1:** naujausia diagnostika #44309353359, artifact #14429537030: 2026-11-18 `agent_run` missing, `ai_calls=0`, `started_at=null`, `error_code=null`; specialistai, coordinator ir Control Core missing; `recommendation_count=0`. D1 turi vieną analytics ir vieną topic snapshot, abu iš manual `workflow_dispatch` run #44307684666; jie neatitinka Worker AI `source_event=schedule` ir workflow ID 418322987 vartų. Memory present, bet paskutinis run_date 2026-11-17, `needs_evidence`, gap codes `insufficient_evidence` ir `other`. Issue #145 open; `recovery_confirmed=false`. Papildomas bridge komentaras nedėtas, nes sėkmingas Control Center report jau buvo sukurtas per paskutines 60 min.
- **PATIKRINTA – JSON:** paskutinio užbaigto AI ciklo 2026-11-17 diagnostika #44176706421 / artifact #14369058763: `report_json_status=valid_object`, `invalid_event_payload_count=0`, content-review `needs_evidence/insufficient_evidence`; žinoma `content-review_model_output_invalid_json` klaida tame cikle nefiksuota. 2026-11-18 ciklas neįvyko, todėl šiandienos JSON elgsena netestuota.
- **NEVEIKIA / LAUKIA – schedule priežastis:** workflow YAML grafikas patvirtintas, tačiau tikro schedule run nėra. Tiksli priežastis nepatvirtinta; dabartinė GitHub jungtis neparodo Actions enablement/repository settings būsenos. Nekeista repo konfigūracija.
- **ATLIKTA:** tik read-only auditai; jokio Worker/D1, ARO Vet, viešo turinio, DNS, secrets, permissions ar mokamų paslaugų pakeitimo. Jokio kodo pakeitimo ar PR kūrimo, nes nėra patikimo optimizavimo prieš/po matavimo.
- **Kitas veiksmas:** po kito tikro Daily-suite schedule patikrinti D1 source provenance, event-driven Control Center ir Worker AI ciklą po 13:20 LT (5 AI calls, completed, error_code=null, memory present). Issue #145 neuždaryti iki `recovery_confirmed=true`.


## 2026-11-18 – po darbo žurnalo commit atlikta CI patikra

- **PATIKRINTA:** darbo žurnalo atnaujinimas main sukūrė commit `15080e5e4ea387005962e6f3acaa7e7bf06490d6`. Jo `push` paleido site-check #44311774654; run success, 21 s (13:14:55Z–13:15:16Z), visi JavaScript, HTML/SEO/sitemap, automation compile, topic-radar ir analytics testų žingsniai success.
- **ATLIKTA:** po-commit patikra patvirtino, kad dokumentavimo pakeitimas nesulaužė statinės svetainės ar automatizavimo testų. Tai nėra Daily-suite `event=schedule` įrodymas ir nekeičia Worker AI būsenos.
