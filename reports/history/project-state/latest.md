# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-21T10:47:56.104865+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 44896025044
- Šaltinio commit: a5f0a395f5a215fefd06662eac43a321a3298f50

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-21 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-20T15:19:45Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Lighthouse auditas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 2 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-21 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-20T15:19:45Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/44895862888

## Laukiančios patikros

- Centrinės API sinchronizavimas: Vyksta (in_progress).
- AI agentai + control-core atmintis: Paskutinis AI agentų ciklas dar neįvyko 13:20 Lietuvos laiku lange; laukiama šiandienos suplanuoto ciklo.

## AI agentų ir atminties patikra

- Būsena: **waiting** – Paskutinis AI agentų ciklas dar neįvyko 13:20 Lietuvos laiku lange; laukiama šiandienos suplanuoto ciklo.
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
