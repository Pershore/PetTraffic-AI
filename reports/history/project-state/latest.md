# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-15T13:33:18.024869+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 43719590317
- Šaltinio commit: e8efb79cc800814f4862d36a2c198cd83c139cb5

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-15 06:10 UTC dar neįvykdytas; suplanuotų paleidimų istorijoje nėra. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 3 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-15 06:10 UTC dar neįvykdytas; suplanuotų paleidimų istorijoje nėra. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43696960921
- **Centrinis valdymo centras** (warning): Suplanuotas ciklas nuo 2026-11-15 08:40 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-14T15:18:42Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43719590317
- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-15. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Lighthouse auditas: Workflow atnaujintas 2026-11-13 12:09 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.

## AI agentų ir atminties patikra

- Būsena: **stale** – Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-15.
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


## Produkcinio Control Center dashboard patikra – 2026-11-15 15:34 LT

- PR [#225](https://github.com/Pershore/PetTraffic-AI/pull/225) GitHub'e pažymėtas kaip **merged** 2026-11-15 13:33:09 UTC; merge commit `e8efb79cc800814f4862d36a2c198cd83c139cb5`.
- Naujausias main commit po automatinio darbo žurnalo įrašo: `fa526242a005b60a99e1b9f103245bf00b71ca1b`.
- Po merge site-check [#43719590484](https://github.com/Pershore/PetTraffic-AI/actions/runs/43719590484) – success: Node JS sintaksė, HTML/SEO/sitemap, compileall ir testų žingsniai success.
- Po merge Control Center [#43719590317](https://github.com/Pershore/PetTraffic-AI/actions/runs/43719590317) – success; ataskaita sugeneruota ir archyvuota.
- Produkcinis URL `https://pettraffic-ai.pages.dev/control/` gyvai atidarytas; puslapyje yra architektūros, agentų/atminties, atvirų PR, svetainės puslapių ir įrankių skyriai. Tai patvirtina, kad dashboard HTML publikuotas produkcijoje.
- Dashboard JavaScript sintaksė patikrinta CI, tačiau šio audito metu realaus naudotojo naršyklės vykdomo JS fetch/refresh sesijos pilnas E2E patikrinimas dar neatliktas. Worker CORS leidžia tik oficialų production origin; branch preview Worker fetch sąmoningai praleidžiamas.
- Dashboard read-only; DNS, Worker/D1, secrets, production konfigūracija ir mokami planai nekeisti.
