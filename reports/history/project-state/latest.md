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
