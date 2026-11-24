# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-24T12:11:58.600137+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 45391175690
- Šaltinio commit: a43b1ca519058c742330c2c13f2e6b4df982dc12

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-24 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-22T14:27:51Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 11 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-24 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-22T14:27:51Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/45374802744
- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-22. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Lighthouse auditas: Workflow atnaujintas 2026-11-23 14:10 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.

## AI agentų ir atminties patikra

- Būsena: **stale** – Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-22.
- Patikros šaltinis: https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Rekomendacijos

- **[medium] Patikrinti Google paieškos matomumą** – Patikrinti URL indeksavimo būseną, sitemap apdorojimą ir ar svarbiausi puslapiai prieinami Googlebot.
- **[info] Stebėti Google sitemap apdorojimą** – Pakartotinai patikrinti kitame cikle; sitemap pakartotinai neteikti, jei jis jau pateiktas.
- **[low] Stebėti tuščias temų RSS užklausas** – Patikrinti, ar tai laikinas Google News RSS rezultatų nebuvimas; nekurti temų paklausos išvadų iš šių skaičių.
- **[high] Pašalinti automatizacijų būklės problemas** – Atidaryti centrinio valdymo GitHub įspėjimą ir taisyti konkretaus proceso klaidą.

## Nekeičiamos saugumo ribos

- ARO Vet svetainės, kodo ir infrastruktūros nekeisti be atskiro leidimo.
- Svetainės turinio automatiškai nepublikuoti; būtinas vartotojo patvirtinimas.
- Jokių mokamų API ar paslaugų be atskiro biudžeto patvirtinimo.
- Nekeisti DNS, Cloudflare teisių ar produkcinės infrastruktūros be atskiro patvirtinimo.
- AI rekomendacijos yra patariamosios; modelio išvestys nesuteikia vykdymo teisių.

> Tik agreguotos procesų būsenos ir rekomendacijų santrauka; be lankytojų lygmens duomenų, žalių paieškos užklausų ar paslapčių.


## Papildoma 2026-11-24 14:00 LT verifier patikra

- **PATIKRINTA – post-cycle report:** po 13:20 LT nebuvo sėkmingo Control Center report ir per ankstesnes 60 min. nebuvo sėkmingo run; issue #145 prieinamas. Komentaras `/pettraffic-run-control-center` #7131095190, bridge #45391150116 success, Control Center #45391175690 `workflow_dispatch` success per 32 s, artifact #14919131550. Report sugeneruotas 2026-11-24T12:11:58Z; Worker API/D1 success, heartbeat ~11 min., `needs_attention=true`, `recovery_confirmed=false`, Daily-suite schedule warning ir AI stale.
- **PATIKRINTA – D1 read-only:** komentaras `/pettraffic-run-agent-diagnostics` #7131136602, bridge #45391431300 success, diagnostika #45391456758 success per 11 s, artifact #14918771747. `run_date=2026-11-24`; agent_run missing, status missing, ai_calls=0, started_at=null, error_code=null; 4 specialistai, coordinator ir Control Core missing; coordinator/control_core recommendation_count=0. Memory present, bet paskutinis update 2026-11-22T14:30:22.711Z, last_status=needs_evidence, gaps `insufficient_evidence`, `other`. Šiandienos analytics/topic snapshot'ai tik iš manual Daily-suite #45374802744; schedule provenance nėra. D1 diagnostika atliko SELECT-only patikras, `rows_written=0`; perskaitytos agent_runs, control_core_runs, control_core_memory ir events lentelės; migracijos numeris nepateiktas.
- **PATIKRINTA – schedule:** Daily-suite 2026-11-24 event=schedule nėra po retry slotų 06:10/08:10/10:10/11:10 UTC; site-check 05:37 UTC ir connectivity 06:57 UTC taip pat be šiandienos schedule. Manual #45374802744 nėra cron įrodymas. Weekly growth review #45323581220 schedule success; po jo Control Center #45323614807 workflow_run success. Control Center neturi atskiro cron.
- **NEPATVIRTINTA / LAUKIA:** Worker AI šiandien neįvyko; memory stale; issue #145 open. JSON klaidos pasikartojimo šiandien įvertinti negalima, nes agent_run missing; paskutinis istorinis atvejis 2026-11-14.
- **ATLIKTA / PARUOŠTA:** PR #312 bounded topic-radar concurrency, max 3, 2 failai, CI #45392427667 success 16 s, Control Center PR #45392428013 success 25 s; synthetic fixture 1.401 s → 0.605 s (-56.8 %), live post-change matavimas laukia. PR #301 baseline atnaujintas iki 157 s per 11 docs-only push'ų; PR #301 ir #312 open, nejungti.
- **Kitas žingsnis:** laukti tikro Daily-suite schedule, automatinio Control Center workflow_run ir pilno 5/5 Worker AI + šviežios atminties įrodymo. Nekeisti production, Worker/D1, ARO Vet, DNS ar secrets.
