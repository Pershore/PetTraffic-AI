# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-13T21:14:04.420048+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 43508810788
- Šaltinio commit: 67c2d0dcb4efeb01a12539a584964474ad0e3851

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: AI agentai + control-core atmintis (failure). AI agentų ciklas nepavyko (2026-11-13); AI kvietimų: 1; klaida: Unexpected_end_of_JSON_input.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 13 min.

## Problemos

- **AI agentai + control-core atmintis** (failure): AI agentų ciklas nepavyko (2026-11-13); AI kvietimų: 1; klaida: Unexpected_end_of_JSON_input. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- GA4 ir Search Console: Workflow atnaujintas 2026-11-13 14:27 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.
- Temų radaras: Workflow atnaujintas 2026-11-13 12:09 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.
- Svetainės stebėjimas: Workflow atnaujintas 2026-11-13 12:09 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.
- Lighthouse auditas: Workflow atnaujintas 2026-11-13 12:09 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.
- Centrinis valdymo centras: Vyksta (in_progress).

## AI agentų ir atminties patikra

- Būsena: **failure** – AI agentų ciklas nepavyko (2026-11-13); AI kvietimų: 1; klaida: Unexpected_end_of_JSON_input.
- Patikros šaltinis: https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Rekomendacijos

- **[high] Patikrinti GA4 duomenų prieigą** – Patikrinti GA4 paslaugos paskyros skaitymo prieigą ir API atsakymą.
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


## Rankinis sesijos papildymas – 2026-11-13 21:15 UTC

- PR #164 sujungtas: GPT-OSS 20B `max_output_tokens` 256→1024; Worker Node.js testai 47/47, Python testai 4/4, Cloudflare validacija ir site checks sėkmingi.
- Worker deploy run `43508721169` – SUCCESS; D1 ir control-core schema connected, apsaugotas API patikrintas HTTP 401.
- **AI atmintis vis dar nepatvirtinta:** gyvas `/health` rodo 2026-11-13 seną `failed` įrašą, `ai_calls=1`, `Unexpected_end_of_JSON_input`; `control_core.status=not_started`, `memory_status=missing`. Naujas modelio biudžetas dar netikrintas realiu agentų ciklu; kitas ciklas 2026-11-14 10:20 Europe/Vilnius.
- GA4 metadata veikia, tačiau minimalus `runReport` timeoutina ir po 25 s; GSC API veikia. 2026-11-13 analytics artefaktas perskaitytas: GSC ataskaita išsaugota, 0 parodymų / 0 paspaudimų 2026-11-04–2026-11-10, sitemap pateiktas, Google fetch dar nepatvirtintas.
- Paskutinių 100 GitHub Actions vykdymų `schedule` įvykių nerasta; YAML cron yra, tačiau Actions nustatymų prieiga per šią integraciją nepasiekiama.
- Termux/Codex bootstrap ir login telefone neatlikti. ChatGPT Remote `localhost` Offline nėra Termux jungtis; reikalingas vienkartinis bootstrap telefone.
- Darbo žurnalas ir perdavimo dokumentai papildyti PR #165; visi duomenys ir senoji istorija išsaugoti.
