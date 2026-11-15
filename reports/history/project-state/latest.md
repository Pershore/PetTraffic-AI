# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-15T13:38:30+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 43719820823
- Šaltinio commit: 11438c15db521b2dd8bf02c3eb5450063dc91644

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-15 06:10 UTC dar neįvykdytas; suplanuotų paleidimų istorijoje nėra. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 6 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-15 06:10 UTC dar neįvykdytas; suplanuotų paleidimų istorijoje nėra. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43696960921
- **Centrinis valdymo centras** (warning): Suplanuotas ciklas nuo 2026-11-15 08:40 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-14T15:18:42Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43719848502
- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-15. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Centrinės API sinchronizavimas: Vyksta (in_progress).
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

## Rankinis tęstinis auditas – 2026-11-15 15:38 LT

- Main HEAD po PR #226: `e1c947a43da6380a87a547c1af349092ab538fe8`. PR #225 ir PR #226 sujungti; dashboard kodas ir gyvų šaltinių pataisa yra main.
- PR #226 pataisė refresh() šaltinių priskyrimą: vardinis map'as apima runs, prs, commit, health, site, analytics, topics ir issue; pridėtas GitHub issue #145 GET. Regresijos testas įtrauktas.
- Po merge site-check #43719820860 – success; Control Center #43719820823 – success; IndexNow #43719820885 – success. Lighthouse #43719820834 paskutinės patikros metu dar in_progress.
- Production `/control/` ir `/control/control.js` atsako HTTP 200. Gyvas JS asset iš Pages turi `const sources`, issue #145 GET, seno `assign(3,"issue")` nebėra. Production HTML `noindex,nofollow`, dashboard nėra sitemap; puslapis viešas, noindex nėra autentifikacija.
- Worker `/health` HTTP 200; D1 ir Control Core schema connected. Agent orchestration run_date 2026-11-15, status completed, 5 AI calls, error_code null, started_at 08:20 UTC (10:20 LT); Control Core `needs_evidence`, memory present, 2 rekomendacijos, 8 evidence gaps (model_output 2, insufficient_evidence 1, other 5). Tai senas iki 13:20 LT ciklas; kitas pilnas ciklas laukiamas 2026-11-16 13:20 LT.
- Analytics archyvas 2026-11-08–14: 7 aktyvūs naudotojai, 19 sesijų, 73 puslapių peržiūros, 0 organinių sesijų. Search Console 2026-11-06–12: 0 parodymų / 0 paspaudimų, sitemap submitted/pending, 5 prioritetiniai URL Google nežinomi. Topic radar: 28 unikalios RSS nuorodos iš 7 temų.
- `/v1/tasks*` 503 `task_api_not_enabled` yra sąmoningai išjungta užduočių API, ne dashboard gedimas. Dashboard tik GET/read-only; ChatGPT automatikų gyvas statusas ir Termux shell tiesiogiai neskaitomi.
- Pilnas realaus naudotojo naršyklės E2E fetch/refresh dar NEPATVIRTINTAS; Firecrawl browser bandymas timeout. Viešų failų HTTP 200, CI ir duomenų šaltinių tiesioginis pasiekiamumas patvirtinti, bet to nepateikiame kaip browser E2E.
- Atviras docs PR #227 atnaujintas pagal PR #226; laukia Cloudflare Pages preview check. PR #224 lieka draft. Jokių Worker/D1, DNS, secrets, ARO Vet, viešo turinio ar mokamų paslaugų pakeitimų.
- Kitas veiksmas: sulaukti Lighthouse #43719820834 pabaigos, PR #227 privalomų check'ų; 2026-11-16 13:20 LT patikrinti naują Worker AI ciklą ir Control Core evidence.