# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-23T12:15:18.572634+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 45172518607
- Šaltinio commit: 0107e429f9da05a43ee3a49bb2c282b46edcea21

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-23 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-22T14:27:51Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 0 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-23 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-22T14:27:51Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/45158543329
- **Lighthouse auditas** (warning): Suplanuotas ciklas nuo 2026-11-23 07:27 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-16T17:10:54Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43915631789
- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-22. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Nėra.

## AI agentų ir atminties patikra

- Būsena: **stale** – Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-22.
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


## 2026-11-23 14:00 LT – greičio ir Worker AI post-cycle patikra

- **Būsena: REIKIA DĖMESIO.** Šiandien, 2026-11-23, naujausių 100 GitHub Actions įrašų sąraše nėra tikro Daily-suite `event=schedule`, site-check, Google API connectivity ar Lighthouse schedule. Paskutiniai tikri Daily-suite/site-check/connectivity schedule yra 2026-11-22 ir vėlavo apie 8 val.; šiandienos manual/push paleidimai schedule nepakeičia.
- **PATIKRINTA – atsarginiai procesai:** Daily-suite #45158543329 workflow_dispatch success (35 s, 3/3 job); sync #45158713578 success (18 s); site-check #45158716443 success (16 s); Control Center #45172518607 workflow_dispatch success (28 s); Worker D1 diagnostika #45172869024 success (14 s, 7 SELECT, rows_written=0); connectivity #45173334230 success (17 s); Lighthouse #45173330353 success (158 s). Šiandienos 17 susijusių Actions vykdymų sąraše nėra failed/cancelled.
- **Worker/D1 – PATIKRINTA sveikata, AI LAUKIA:** Control Center #45172518607 artifact #14817312217 rodo Worker API + D1 success, heartbeat šviežias, bet `recovery_confirmed=false`. D1 diagnostika #45172869024 artifact #14817142647: `run_date=2026-11-23`, agent run missing, `ai_calls=0`, `started_at=null`, `error_code=null`; visi 4 specialistai missing, coordinator missing, Control Core missing. Memory present, bet pasenusi: updated 2026-11-22T14:30:22.711Z, last_status=needs_evidence, gap codes insufficient_evidence/other. Coordinator ir Control Core recommendation_count=0. Šiandienos analytics/topic snapshots yra iš manual run #45158543329 (`workflow_dispatch`), todėl Worker schedule provenance vartai neatsidaro. AI ciklas nepatvirtintas.
- **Schema / heartbeat:** Worker health kontrolė tikrina D1 ir `control_core_runs` / `control_core_memory` lentelių pasiekiamumą; Control Center report patvirtino API/D1 ir heartbeat. Septynios D1 SELECT užklausos sėkmingos. Diagnostikos `schema_version=1` yra artefakto formatas, ne DB migracijos numeris; atskiro migracijos numerio nebuvo.
- **Lighthouse palyginimas:** 2026-11-23 #45173330353 prieš 2026-11-16 #43915631789: dog-diarrhea mobile LCP 9.779→2.765 s; vet-visit desktop 8.078→0.576 s; vet-visit mobile 5.548→2.281 s; dog desktop 1.677→0.554 s. Home-mobile TBT pablogėjo 27→416 ms (balas 100→89); cat-diarrhea mobile LCP 2.031→2.450 s, cat-emergency mobile 2.347→2.723 s. CLS=0, accessibility/best-practices/SEO=100. Vienas pakartojimas, priežastinis kodo pagerėjimas neįrodytas; kodas nekeistas.
- **JSON klaida:** paskutinis žinomas `content-review_model_output_invalid_json` įvykis 2026-11-14. Šiandien AI run nėra, todėl pasikartojimas neįvertinamas. Dabartinis parser atmeta visą specialisto objektą, jei trūksta privalomo lauko; riboto taisymo bandymo nėra. PR #261 vis dar open, nesujungtas.
- **PR #301 – PARUOŠTA:** PR aprašymas papildytas 2026-11-23 docs-only site-check #45159340833 (16 s); baseline dabar 101 s per 8 docs-only push (97 s completed + 4 s cancelled). PR open, mergeable, nesujungtas; main dar neturi paths-ignore, po-merge sutaupymas nepatvirtintas.
- **Issue #145:** paliktas open; per bridge pridėti Control Center, agent diagnostics, Lighthouse ir connectivity komandų komentarai. Nėra `recovery_confirmed=true`.
- **Saugumas:** Worker/D1 kodas ir duomenys šiame cikle nekeisti; diagnostika tik SELECT. Nekeista ARO Vet, DNS, secrets, production, viešas turinys ar billing. Aktyvus darbo laikas NEMATUOTAS.
- **Kitas veiksmas:** sulaukti tikro Daily-suite `event=schedule`; po jo patikrinti automatinį Control Center workflow_run ir D1 diagnostiką. Worker AI žymėti PATIKRINTA tik su tos dienos run_date, started_at po 13:20 LT, completed, 5 AI calls, null error ir present memory. PR #301 nejungti automatiškai.
