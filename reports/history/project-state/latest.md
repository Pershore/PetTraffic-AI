# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-14T14:13:30.136214+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 43603715907
- Šaltinio commit: 7be86f45f1ac82bb3a0a5086a6e579d063af1b95

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: AI agentai + control-core atmintis (failure). AI agentų ciklas nepavyko (2026-11-14); AI kvietimų: 4; klaida: model_content-review_model_output_invalid_json.

## Patvirtinti procesai

- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 12 min.

## Problemos

- **AI agentai + control-core atmintis** (failure): AI agentų ciklas nepavyko (2026-11-14); AI kvietimų: 4; klaida: model_content-review_model_output_invalid_json. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- GA4, temų radaras ir svetainės stebėjimas: Workflow atnaujintas 2026-11-14 14:12 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.
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


## Rankinis auditas po Worker deploy (2026-11-14 14:15:47 UTC)

Šis skyrius yra rankinis papildymas; automatinio snapshot metaduomenys aukščiau nekeičiami.

- PR #196 sujungtas: Termux / Codex lokali aplinka patvirtinta pagal vartotojo bootstrap išvestį; tai nėra foninis agentas.
- PR #197 sujungtas ir production Worker įdiegtas. Worker versija 71dfa69f-88bf-4c04-9b6c-5a124be3dbc9; deploy run #43603199126 success; D1 migracijų nereikėjo.
- Post-deploy gyvas heartbeat PATIKRINTAS 2026-11-14 14:15:47 UTC: svetainė HTTP 200, D1 connected, control-core schema connected.
- Nauja agentų atsparumo logika CI patikrinta: blogas vieno specialisto JSON nebestabdo ciklo; blogo koordinatoriaus atveju naudojamas deterministinis read-only fallback; jei visi specialistai blogi, penktas AI kvietimas praleidžiamas. Pirmas realus po-deploy AI ciklas dar laukia 2026-11-15 08:20 UTC.
- PR #199 sujungtas: daily-suite tiesioginis cron 06:10 UTC (08:10 LT), nepriklausomas nuo site-check. Pirmas realus schedule paleidimas laukia 2026-11-15 06:10 UTC.
- Vienintelė ChatGPT priežiūros automatizacija perkelta į 11:00 Europe/Vilnius; ji lieka įjungta, dublikatų nėra.
- Worker heartbeat kas 15 min. ir dienos AI ciklas 10:20 LT yra realiai užregistruoti Cron trigeriai. Tai nėra nuolatinis AI mąstymas kiekvieną sekundę.
- Worker /v1/tasks API lieka tyčia išjungta iki atskiros agento tapatybės ir PR-only užduočių vykdymo saugumo peržiūros. 100 % uptime garantuoti negalima.
