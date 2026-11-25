# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-25T12:46:11.621385+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 45616929438
- Šaltinio commit: 309a513b93768dfefbe72d534e4085a73fc2bff5

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-25 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-24T17:33:36Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 1 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-25 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-24T17:33:36Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/45589661930
- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-24. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Lighthouse auditas: Workflow atnaujintas 2026-11-23 14:10 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.

## AI agentų ir atminties patikra

- Būsena: **stale** – Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-24.
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


## 2026-11-25 – operator post-cycle verification addendum

- **PATIKRINTA:** 2026-11-25 naujausių 100 Actions vykdymų sąraše nėra `event=schedule`. Paskutiniai tikri schedule: Daily-suite #45449912631 (2026-11-24 17:33:36Z), site-check #45435762586 (16:19:22Z), analytics-connectivity #45461901195 (18:39:36Z). Manual Daily-suite #45589661930 (43 s) nėra schedule įrodymas.
- **PATIKRINTA:** Daily-suite manual report: analytics ~10,1 s; topic-radar ~2,4 s ir 31 antraštė be 503; D1 sync #45589984865 success (2/2 write/readback); site-check #45590420563 success, 160 testų. Docs-only site-check #45591650776 19 s ir #45593125077 18 s.
- **ATLIKTA:** po 13:20 LT pridėtas `/pettraffic-run-control-center` (#7162816137); bridge #45616872767 success; Control Center #45616929438 `workflow_dispatch` success (24 s), artifact #15020914764. Worker API/D1 success, heartbeat ~1 min.; schedule warning, AI stale; `recovery_confirmed=false`.
- **ATLIKTA / PATIKRINTA:** pridėtas `/pettraffic-run-agent-diagnostics` (#7162866555); bridge #45617196748 success; read-only diagnostika #45617216545 success (12 s), artifact #15021629151. Septynios SELECT užklausos, `rows_written=0`; diagnostikos D1 lentelės/stulpeliai pasiekiami. `run_date=2026-11-25`, agent run missing, `ai_calls=0`, `started_at=null`, `error_code=null`; visi 4 specialistai, coordinator ir Control Core missing; memory present, bet pasenusi (`2026-11-24T17:45:24.093Z`, `needs_evidence`, gap `other`). Šios dienos source snapshots analytics/topic tik iš manual #45589661930; Control Center/recommendation snapshot 0.
- **LAUKIA / NEPATVIRTINTA:** Worker AI ciklas neatliktas; Issue #145 lieka open. Content-review JSON klaidos pasikartojimo šiandien patikrinti negalima, nes nėra agent run; main parser vis dar griežtai atmeta nepilną schemą, PR #306 draft turi dalinių laukų išsaugojimo pataisą.
- **ATLIKTA:** PR #301 aprašyme baseline atnaujintas iki 211 s / 14 docs-only push'ų; PR #312 aprašyme pridėtas 2,4 s realus main topic-radar matavimas (ne po-pakeitimo benchmark). Abu PR atviri, nejungti.
- **SAUGUMAS:** produkcija, Worker/D1 duomenys, ARO Vet, DNS, secrets, viešas turinys ir billing nepakeisti. Aktyvus darbas NEMATUOTAS.
- **Kitas veiksmas:** tikrinti kitą tikrą Daily-suite schedule ir po jo automatinį Control Center / D1 / Worker AI įrodymų ciklą.
