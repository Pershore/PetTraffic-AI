# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-15T09:17:35.436710+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 43698524976
- Šaltinio commit: e31877cb3d25680377879a73b9021a926c5675dc

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-15 06:10 UTC dar neįvykdytas; suplanuotų paleidimų istorijoje nėra. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 1 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-15 06:10 UTC dar neįvykdytas; suplanuotų paleidimų istorijoje nėra. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43696960921
- **AI agentai + control-core atmintis** (warning): AI agentų ciklas ir atminties įrašymas baigti; rekomendacijų: 2; trūksta įrodymų: 8. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Lighthouse auditas: Workflow atnaujintas 2026-11-13 12:09 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.

## AI agentų ir atminties patikra

- Būsena: **warning** – AI agentų ciklas ir atminties įrašymas baigti; rekomendacijų: 2; trūksta įrodymų: 8.
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


## 2026-11-15 11:18 LT – catch-up ir Worker grafiko patikra

- Daily-suite cron 08:10 LT vis dar neturi event=schedule. Owner-only fallback run 43696960921 (workflow_dispatch) success: analytics, topic-radar, live-check. Tai atkuria dienos duomenų rinkimą, bet nėra cron įrodymas.
- GA4 2026-11-08–14: 7 active users, 19 sessions, 73 pageviews, organic sessions 0. GSC 2026-11-06–12: 0 impressions, 0 clicks; sitemap pending; 5 priority URLs unknown. Topic radar 28 unique links / 7 topics.
- D1 daily-suite analytics/topic write+readback success run 43698010982. D1 Control Center/recommendation write+readback success run 43698006099.
- PR #216 sujungtas; Worker OIDC workflow_dispatch leidžiamas tik pinned sync-control-api.yml@main, kiti eventai atmetami. Deploy 43697913727 success; post-deploy health/D1/schema/auth boundary patikrinta.
- PR #217 sujungtas; Worker AI ciklo cron perkelta į 13:20 Europe/Vilnius, Cloudflare UTC cron 10:20 ir 11:20. Deploy 43698484769 success; Wrangler log aiškiai rodo abu cron trigerius ir 15 min. heartbeat; Worker/D1/schema health success.
- Šiandienos 10:20 AI ciklas completed, 5 AI calls, error_code=null, tačiau jis įvyko prieš 11:11 LT D1 sync. Dėl vieno run_date per dieną idempotency naujas grafikas šiandien ciklo nekartos; kitas pilnas AI ciklas laukiamas 2026-11-16 13:20 LT. Control Core vis dar needs_evidence: 2 rekomendacijos, 8 evidence gaps.
- ChatGPT pagrindinis koordinatorius enabled 11:45 LT. Esama greičio stebėjimo automatizacija papildyta post-cycle Worker patikra ir perkelta į 14:00 LT. ARO Vet analitikos automatizacija enabled 18:24 LT. Naujų automatizacijų nesukurta (3 aktyvių užduočių planas išnaudotas).
- Issue #145 paliktas open. Kitas veiksmas: 11:45 koordinatorius patikrina schedule ir catch-up; 14:00 post-cycle patikra tikrina naują Worker ciklą; jei šiandien ciklas nepasileidžia dėl jau panaudoto run_date, laukiamas kitas 2026-11-16 13:20 LT ciklas.

