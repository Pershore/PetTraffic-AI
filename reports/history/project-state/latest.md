# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-14T13:43:12.256343+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 43601159634
- Šaltinio commit: 4e5934370242118ab44626fcc5c9376bf2e9f1e9

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

2026-11-15: po 05:37 UTC site-check schedule patikrinti daily-suite GA4/GSC, temų radaro ir live-check darbus bei D1 sinchronizavimą; po 08:20 UTC patikrinti Worker agentų ciklą po PR #183 pataisos; po 07:27 UTC patikrinti savaitinį Lighthouse auditą.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: sėkmingai įrašyti ir perskaityti agreguoti snapshot duomenys (run 43601193788).
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 12 min.

## Problemos

- **AI agentai + control-core atmintis** (failure): AI agentų ciklas nepavyko (2026-11-14); AI kvietimų: 4; klaida: model_content-review_model_output_invalid_json. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- GA4, temų radaras ir svetainės stebėjimas: Workflow atnaujintas 2026-11-14 13:39 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.
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


## 2026-11-14 – suplanuotų automatizacijų suvienodinimas

- PR #194 sujungtas: `ba7385bf45ac4f091212556ffac80c6a82162583`. Sukurtas `.github/workflows/daily-suite.yml`; GA4/GSC, temų radaras ir live-site monitor kasdien paleidžiami po patvirtinto `site-check` schedule įvykio (05:37 UTC). Atskiri workflow išliko push / rankinėms patikroms, o jų cron trigeriai pašalinti, kad nebūtų dubliavimo.
- Daily-suite trigeris PATIKRINTAS ne suplanuotu įvykiu: run 43600907737 gavo pavadinimą `Non-scheduled site-check run #43600881588`; visi trys job teisingai buvo `skipped`. Tikras schedule ciklas dar LAUKIA 2026-11-15.
- PR #195 sujungtas: `7ab97db2ac8dfd0e07d525264860affe923678a9`. Valdymo centras atskirai vertina suplanuotus paleidimus ir nebeleidžia atšauktam / vykstančiam push paleidimui užmaskuoti cron būsenos. Testai ir po-merge kontrolės paleidimas 43601159634 – success; klaidingas cancelled įspėjimas pašalintas.
- Push patikros: site-check 43600881588 ir 43601123268 – success; analytics 43600881631 – success; topic radar 43600881695 – success; live-site monitor 43600881611 – success.
- GA4 paskutinio prieinamo laikotarpio suvestinė: 7 aktyvūs naudotojai, 7 nauji, 24 sesijos, 88 puslapių peržiūros. Search Console: 0 parodymų, 0 paspaudimų; sitemap pateiktas, bet dar pending; 5 prioritetiniai URL Google dar nežinomi. Temų radaras: 31 unikali nuoroda, 0 tuščių temų patikrų iš 7; šaltinis Google News RSS, ne paieškos apimtys.
- Centrinės API sync paleidimai 43600907662, 43600987929 ir 43601193788 – success; žurnaluose patvirtintas D1 įrašymas ir perskaitymas atgal.
- Worker agentų klaida `model_content-review_model_output_invalid_json` liko iš 2026-11-14 08:20 UTC ciklo, kuris buvo iki PR #183 deploy 11:51 UTC. Pataisos veiksmingumas dar nepatikrintas; kitas agentų ciklas 2026-11-15 08:20 UTC.
- Lighthouse savaitinis ciklas laukia 2026-11-15 07:27 UTC.
- Nekeista svetainės turinys, Worker runtime / D1 schema ar konfigūracija, DNS, secrets, ARO Vet ar mokamos paslaugos. D1 gavo tik esamų OIDC integracijų agreguotus analitikos snapshot duomenis.
