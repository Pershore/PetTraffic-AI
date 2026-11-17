# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-17T13:06:37.137360+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 44089409856
- Šaltinio commit: d00d8578b931f156b83ff09a58086a8196382d9a

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-17 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-16T15:34:13Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Lighthouse auditas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 6 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-17 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-16T15:34:13Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/44077181860
- **AI agentai + control-core atmintis** (warning): AI agentų ciklas ir atminties įrašymas baigti; rekomendacijų: 1; trūksta įrodymų: 5. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Nėra.

## AI agentų ir atminties patikra

- Būsena: **warning** – AI agentų ciklas ir atminties įrašymas baigti; rekomendacijų: 1; trūksta įrodymų: 5.
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

## Operatoriaus patikros priedas – 2026-11-17 15:07 LT

- PATIKRINTA: main HEAD `d00d8578b931f156b83ff09a58086a8196382d9a`; daily-suite 2026-11-17 `event=schedule` nerasta. Paskutinis schedule #43897746978 – 34 s (2026-11-16); šiandienos #44077181860 buvo tik workflow_dispatch – 39 s. Site-check schedule šiandien taip pat nerasta; paskutinis #43880800208 – 21 s.
- PATIKRINTA: Lighthouse schedule #43915631789 success per 223 s, bet sukurtas ~9 val. 44 min. po cron; weekly growth review #43999680694 schedule success per 24 s. Daily-suite job'ai vykdomi lygiagrečiai: topic 10 s, live-check 15 s, analytics 35 s; analytics loge tests ~9,8 s, pip install ~4,3 s, API užklausos ~12,4 s. Jokio nepagrįsto speed-gain teiginio.
- PATIKRINTA: Control Center #44089409856 workflow_run success per 36 s; sync-control-api #44089342641 success per 15 s. Worker cron diagnostic #44077019257 success per 847 s dėl sąmoningo 15 min. heartbeat lango; D1/schema/site/DB healthy.
- PATIKRINTA: Worker AI run_date 2026-11-17, started_at 12:00:13.704Z (14:00:13.704 LT), completed, ai_calls=5, error_code=null, memory present. Control Core needs_evidence, 5 spragos, 1 rekomendacija; recovery_confirmed=false. Content-review šiame cikle needs_evidence/insufficient_evidence, ne invalid_json; analytics ir technical-seo dar turi generic other.
- ATLIKTA: PR #277 draft paruošia automatinę SELECT-only D1 diagnostiką po sėkmingo Control Center workflow_run; CI success, deploy skipped, PR nesujungtas. Issue #145 lieka open.
