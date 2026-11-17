# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-17T10:16:21.943877+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 44063255054
- Šaltinio commit: a375f02ec0743e894cfd1620d9ee1800f89522ce

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-17 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-16T15:34:13Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Lighthouse auditas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 1 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-17 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-16T15:34:13Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43897746978

## Laukiančios patikros

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

## Papildomas audito radinys – Lighthouse (2026-11-17)

- **PATIKRINTA:** schedule run #43915631789 artefaktas #14249118806 turi 21 failą ir 10 puslapio / įrenginio ataskaitų. Našumas: dog-diarrhea mobile 55/100, vet-visit desktop 55/100, vet-visit mobile 60/100; likę 7 balai 86–100. Visų ataskaitų prieinamumas, geriausia praktika ir SEO – 100. Lėtiems variantams LCP 9,779 s / 8,078 s / 5,548 s, TBT=0, CLS=0; šakninis dokumento atsako laikas 4,35 s / 2,56 s / 2,14 s.
- **PLANUOJAMA:** pakartoti matavimą kitame savaitiniame Lighthouse cikle (2026-11-23); vieno audito nepakanka kodo pakeitimui pagrįsti.