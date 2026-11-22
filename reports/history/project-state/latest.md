# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-22T12:12:50.513913+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 45021095099
- Šaltinio commit: 9e2044e7859510619d38ff9eff33717dcdd8ec44

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-22 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-21T14:33:09Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Lighthouse auditas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 12 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-22 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-21T14:33:09Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/45009228733
- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-21. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Nėra.

## AI agentų ir atminties patikra

- Būsena: **stale** – Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-21.
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

## 2026-11-22 14:00 LT – papildomas post-cycle Worker AI ir greičio auditas

- Daily-suite, site-check ir analytics-connectivity šiandien neturi tikro `event=schedule`; paskutiniai schedule įvykiai yra 2026-11-21 (Daily-suite #44914516893, site-check #44910110156, connectivity #44917396545), su 8 val. 04 min.–8 val. 23 min. vėlavimais pagal jų cron. Rankinis Daily-suite #45009228733 success nėra schedule įrodymas.
- Šios dienos patikrintos trukmės: Daily-suite job'ai analytics 29 s, topic-radar 10 s, live-check 17 s; sync #45009507913 12 s; site-check #45009628108 15 s ir docs-only push #45010406492 14 s; Control Center #45021095099 24 s; D1 diagnostika #45021278018 9 s. Nėra pagrindo teigti išmatuotą optimizacijos pagerėjimą.
- PR #301 open + ready-for-review, mergeable/clean, 1 failas / +8 eilučių; CI #44904330583 success (17 s), 1 ahead / 3 behind main. Main vis dar paleido docs-only site-check #45010406492 (14 s); po-merge sutaupymas dar nepatikrintas. PR nesujungtas.
- Po 60 min. be CC paleidimo issue #145 komentaras #7078948028 paleido bridge #45021081236 ir Control Center #45021095099 (workflow_dispatch, success); artifact #14754290435 rodo Worker API + D1 gerai, heartbeat prieš ~12 min., Daily-suite warning, AI stale, `recovery_confirmed=false`.
- Read-only diagnostikos komentaras #7078974094 paleido bridge #45021267579 ir D1 diagnostics #45021278018 (success); artifact #14754186215 patvirtina 7 SELECT / `rows_written=0`. 2026-11-22 `agent_run` missing / 0 AI calls, 4 specialistai missing, coordinator ir Control Core missing, memory present bet paskutinis įrašas 2026-11-21 `needs_evidence`; šiandienos snapshots yra tik iš manual run #45009228733, todėl Worker schedule provenance vartai neužsidaro.
- JSON klaidos paskutinis žinomas atvejis 2026-11-14; PR #183 su JSON ribomis jau merged. Šiandienos AI run nėra, todėl pasikartojimo vertinti negalima. Siūlomas būsimas 1 retry panaudojant penktą kvietimą vietoj coordinator modelio, su deterministiniu fallback; šiame cikle Worker/D1 kodas nekeistas.
- Schema lentelių prieinamumą patvirtina D1 SELECT, bet atskiro migracijos numerio artefaktai nerodo. Issue #145 lieka open; jokie production, Worker/D1, ARO Vet, DNS, secrets ar billing pakeitimai neatlikti. Aktyvus darbo laikas NEMATUOTAS.
- Kitas veiksmas: tikrinti kitą tikrą Daily-suite `event=schedule`, po jo automatinį Control Center `workflow_run`, D1 readback ir 13:20 LT AI ciklo 5/5 + memory įrodymus.
