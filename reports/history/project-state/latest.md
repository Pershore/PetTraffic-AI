# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-14T14:07:54.478250+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 43603233560
- Šaltinio commit: 07922ad2384e27249f01f438f7bf6dc44399da06

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: AI agentai + control-core atmintis (failure). AI agentų ciklas nepavyko (2026-11-14); AI kvietimų: 4; klaida: model_content-review_model_output_invalid_json.

## Patvirtinti procesai

- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 7 min.

## Problemos

- **AI agentai + control-core atmintis** (failure): AI agentų ciklas nepavyko (2026-11-14); AI kvietimų: 4; klaida: model_content-review_model_output_invalid_json. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- GA4, temų radaras ir svetainės stebėjimas: Workflow atnaujintas 2026-11-14 13:39 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.
- Centrinės API sinchronizavimas: Vyksta (in_progress).
- Lighthouse auditas: Workflow atnaujintas 2026-11-13 12:09 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.
- Centrinis valdymo centras: Workflow atnaujintas 2026-11-14 13:42 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.

## AI agentų ir atminties patikra

- Būsena: **failure** – AI agentų ciklas nepavyko (2026-11-14); AI kvietimų: 4; klaida: model_content-review_model_output_invalid_json.
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
