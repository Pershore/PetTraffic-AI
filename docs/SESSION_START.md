# Pet traffic – naujos sesijos pradžios protokolas

Atnaujinta: 2026-11-15

Šis dokumentas yra trumpas sesijos pradžios kontrolinis sąrašas. Visa ilgalaikė atmintis, sprendimai, architektūra, prieigų matrica ir blokatoriai laikomi `docs/PROJECT_MEMORY.md`.

## Privaloma skaitymo seka

1. `AGENTS.md` iš `main` – tikslai, saugumo ribos ir darbo taisyklės.
2. `docs/SESSION_START.md` – šis protokolas.
3. `reports/history/project-state/latest.md` iš `automation-history` – naujausia automatiškai patikrinta būsena.
4. `reports/work-log/README.md` iš `main` – atliktų darbų ir testų istorija.
5. `docs/PROJECT_MEMORY.md` iš `main` – vienintelė kanoninė ilgalaikė atmintis.
6. Naujausias `docs/PETTRAFFIC_AI_HANDOVER_*.md` – konkrečios sesijos perdavimas.

Jeigu privalomų istorijos failų perskaityti nepavyksta, pranešti apie tai ir nekeisti kodo, infrastruktūros ar produkcijos.

## Patikrinimai prieš tęsiant

- Patikrinti `main` HEAD, naujausius commit, atvirus PR ir issues.
- Patikrinti tik naujausius aktualius GitHub Actions vykdymus; atskirti `schedule`, `push`, `pull_request`, `workflow_run` ir rankinius paleidimus.
- Patikrinti PR jobs ir artifacts prieš teigiant, kad pataisa veikia.
- Gyvą Worker /health ar svetainę tikrinti tik kai tai keičia sprendimą; nekartoti šviežio patikrinimo be priežasties.
- Prieš pakeitimą perskaityti esamą failą ir susijusius testus.
- Kodo / reikšmingus dokumentacijos pakeitimus daryti atskiroje šakoje per PR; nesujungti, kol privalomos patikros nebaigtos.
- Po sujungimo patikrinti realų workflow ir gyvą rezultatą, jei taikoma.

## Dabartinė būsena po 2026-11-15 patikrų (16:17 LT)

1. **Cloudflare saugumas:** Cloudflare API tokeno rotacija ir GitHub Actions secret CLOUDFLARE_API_TOKEN pakeitimas vartotojo patvirtinti. Worker deploy run #43698484769 patvirtino tokeną, D1 migracijas, Worker deploy ir health/auth ribą; visi job success.
2. **Worker / D1:** /health HTTP 200, D1 ir Control Core schema connected, heartbeat patvirtina svetainės HTTP 200. Worker deploy commit 645849f įdiegtas 2026-11-15 09:16 UTC.
3. **AI agentai:** paskutinis D1 ciklas pradėtas 2026-11-15 08:20 UTC (10:20 LT), prieš naują deploy ir prieš 13:20 LT tikslinį laiką. 5 kvietimai completed, error_code=null, tačiau Control Core needs_evidence, 8 spragos, memory present. Tai seno prieš-deploy ciklo duomenys, ne naujos versijos gedimo įrodymas. Dėl run_date idempotency šiandien ciklas nekartojamas; kitas pilnas po-deploy ciklas laukiamas 2026-11-16 13:20 LT.
4. **Daily-suite:** tikras event=schedule run #43721211747 – success, visi 3 job (analytics, topic-radar, live-check) success. Pradžia 13:51:47 UTC (15:51:47 LT), apie 7 val. 42 min. vėliau už 06:10 UTC cron. GA4 2026-11-08–14: 7 aktyvūs naudotojai, 24 sesijos, 88 peržiūros, 0 patvirtintų organinių sesijų. GSC 2026-11-06–12: 0 parodymų ir 0 paspaudimų; sitemap submitted/pending; 5 prioritetiniai URL Google dar nežinomi. Temų radaras: 31 unikali RSS nuoroda iš 7 temų.
5. **Google API:** connectivity run #43722887365 success; job log patvirtino GA4 API OK ir Search Console API OK.
6. **Control Center:** atskiro kasdienio cron nebėra. PR #233 pašalino perteklinį grafiką; PR #234 pašalino klaidingą savęs-vykdymo būseną ir atnaujino dashboard. Control Center run #43723293460 push success, vėlesnis Control Center run #43723668274 success, D1 sync #43723329232 success. Lighthouse push/site-change run #43723293496 success; kitas weekly schedule numatytas 2026-11-16 07:27 UTC. Live /control/ JS patvirtintas su nauju event-driven žymėjimu.
7. **Automatizacijos:** esami ChatGPT procesai įjungti: pagrindinis koordinatorius 11:45 LT, būklės patikra 12:00 LT, greičio / post-cycle tikrintojas 14:00 LT. Jų instrukcijos atnaujintos, kad nereikalautų neegzistuojančio Control Center schedule. Naujų dublikatų nesukurta.
8. **Valdymo skydas:** https://pettraffic-ai.pages.dev/control/ – viešas, noindex, su 7 fiksuotomis komandų kortelėmis. Jis kopijuoja komandas; vykdymas vyksta per owner-only GitHub issue #145 bridge. Noindex nėra autentifikacija. Worker /v1/tasks* lieka tyčia išjungta iki atskiros agentų OIDC tapatybės ir privataus autentifikavimo.
9. **Kiti ribojimai:** nėra tiesioginės Android Termux shell prieigos; viešo turinio publikavimui vis dar būtinas vartotojo patvirtinimas; ARO Vet, DNS, billing ir mokamos paslaugos neliečiamos.

Prieš tęsiant perskaityti šį dabartinės būsenos bloką, naujausią automation-history snapshot ir naujausią handover addendum. Senesnės toliau pateiktos datos / grafikai yra istoriniai, jei prieštarauja šiam blokui.
## Šakų paskirtys

- `main`: kodas, dokumentacija, `AGENTS.md`, darbo žurnalas.
- `automation-history`: tik privatumo požiūriu filtruoti `reports/history/**` snapshot'ai.
- `reports/work-log/README.md` visada skaityti iš `main`; jo nebuvimas `automation-history` yra tyčinis.

## Būsenos

- **ATLIKTA** – pakeitimas įgyvendintas.
- **PATIKRINTA** – yra tikras testas, workflow run ar gyvas atsakymas.
- **PARUOŠTA** – kodas yra, bet aktyvus veikimas neįrodytas.
- **NEVEIKIA** – nustatyta konkreti klaida.
- **LAUKIA** – reikalingas žmogaus veiksmas, išorinis įvykis ar prieiga.
- **PLANUOJAMA** – dar nepradėta.
- **NEPATVIRTINTA** – įrodymų nepakanka.

## Darbo pabaiga

Atnaujinti `reports/work-log/README.md`, `reports/history/project-state/latest.md` ir naujausią handover. Registruoti tik realius pakeitimus, testus, workflow run nuorodas, klaidas, likusius blokatorius ir konkretų kitą veiksmą. Neteigti, kad vyksta nuolatinis darbas tarp sesijų.


## Termux / Codex – naujausias veiksmas (2026-11-14)

- PR #191 sujungtas: `9eacbd44636a9110b74878e7735ee5536e5e6bdd`.
- Ubuntu npm/glob klaidos atkūrimo scenarijus dabar naudoja oficialų npm 10.9.10 su SHA-512 patikra; Termux CI, site-check ir Cloudflare Pages po merge – success.
- Vartotojo 2026-11-14 pateikta reali Termux išvestis patvirtino proot, Git, GitHub CLI, Codex CLI, Codex autentifikaciją ir švarią sinchronizuotą main šaką.


## Termux / Codex patikslinimas (2026-11-14)

Tikras bootstrap iš Termux patvirtintas: Linux proot, Git, GitHub CLI, Codex CLI įdiegti; Codex autentifikacija OK; main...origin/main. PR #196 sujungtas. Tai nėra nuolatinio fono agento ar automatinio GitHub užduočių paėmimo įrodymas. Telefonas nėra naudojamas kaip serverio agento vykdymo aplinka; nuolatiniai procesai turi veikti Worker / GitHub Actions pusėje. /v1/tasks API lieka išjungta iki atskiros agento tapatybės ir užduočių leidimų politikos.


## Nuolatinių agentų būsena (2026-11-14, 14:08 UTC)

- Worker Cron trigeriai po deploy realiai užregistruoti: */15 * * * * (svetainės + D1 heartbeat) ir 20 7,8 * * * (10:20 Europe/Vilnius AI agentų langas). Deploy run #43603199126 – success; Worker versija 71dfa69f-88bf-4c04-9b6c-5a124be3dbc9.
- PR #197 sujungtas commit 6c88f7b3437a753973dfe45108874f4a6c4f4456. Worker testai, Cloudflare prieigos ir konfigūracijos patikra bei site-check – success; production deploy patvirtino D1/control-core ryšį ir apsaugoto API 401 ribą.
- Pataisa: vieno specialisto netaisyklingas AI JSON atsakymas nebestabdo viso ciklo; koordinatorius naudoja deterministinį read-only atsarginį sujungimą, jei jo AI atsakymas netinkamas. Jei visi specialistai negrąžina tinkamų rezultatų, penktas AI kvietimas praleidžiamas ir išsaugoma evidence-gap ataskaita.
- Gyvas /health po deploy patvirtina ok=true, D1 connected, control-core schema connected; naujas Worker heartbeat po deploy PATIKRINTAS 2026-11-14 14:15:47 UTC (site HTTP 200, D1 connected). Jis dar rodo seną 2026-11-14 08:20 UTC agentų gedimą, įvykusį iki naujo deploy. Naujos agentų pataisos realus veikimas dar LAUKIA kito 2026-11-15 08:20 UTC (10:20 LT) ciklo.
- GitHub Actions kasdienio rinkinio grafikai lieka dalinai NEPATVIRTINTI: vienas suplanuotas Google API connectivity run #43602315641 – success, tačiau analytics/topic/live-site schedule ciklo dar nepatvirtinome. Push ir workflow_run nėra schedule įrodymas.
- ChatGPT kasdienė koordinatoriaus automatizacija lieka vienintelė ir įjungta; dublikato nekurti. Termux Codex autentifikacija patvirtinta, bet tiesioginės Android shell prieigos šiame pokalbyje nėra.
- /v1/tasks API lieka tyčia išjungta. Tai reiškia, kad AI specialistai analizuoja ir teikia rekomendacijas, bet negali savavališkai vykdyti GitHub užduočių ar keisti produkcijos. Publikavimui, production, DNS, saugumo teisių ir išlaidų pakeitimams lieka žmogaus patvirtinimo vartai.


## Daily-suite ir pagrindinio koordinatoriaus grafikas (2026-11-14)

- PR #199 sujungtas commit abcd5072e51c98d0b68d2d6a948fd09488245c5b. Daily suite dabar turi nepriklausomą GitHub Actions cron 06:10 UTC (08:10 Europe/Vilnius), atskirai nuo site-check; Control Center stebi šį naują laiką. Pirmas realus schedule paleidimas laukia 2026-11-15 06:10 UTC.
- Esama vienintelė ChatGPT priežiūros automatizacija perkelta iš 09:45 į 11:00 Europe/Vilnius, kad vykdytųsi po daily-suite 08:10, Worker AI agentų 10:20 ir Control Center 10:40. Ji lieka enabled; naujos automatikos nesukurtos.
- Naujo grafiko realus veikimas dar LAUKIA rytojaus schedule įrodymo; push ir workflow_run paleidimai nėra schedule įrodymas.


## Daily-suite snapshot sinchronizavimo patikslinimas (2026-11-14)

- PR #202 sujungtas commit 073bc8d96d81e174c0873061dbffee9aa4162714. sync-control-api dabar nustato daily-suite kilmę pagal GitHub workflow_run API lauką event=schedule, o ne seną display_title. Tai būtina, kad naujo tiesioginio 06:10 UTC grafiko GA4/GSC ir topic artefaktai būtų persiųsti į D1.
- PR #202 Worker snapshot builder test, central-control-center ir site-check – success. Pirmas realus direct schedule + D1 read-back patikrinimas laukia 2026-11-15 06:10 UTC.


## 2026-11-15 ryto patikra

- Naujausia automatiškai patikrinta projekto būsena: `automation-history/reports/history/project-state/latest.md`, sugeneruota 2026-11-14 23:08 UTC. Ji patvirtina PR #208 ir #209 sujungimą, Worker deploy #96 sėkmę, D1 ryšį ir po-merge patikras.
- Naujausias main commit audito metu: `7ae8d1370b679b47816820797f3f0ea97f41a450`. Atvirų PR nerasta; PR #131 patvirtintas kaip merged.
- Daily-suite `10 6 * * *` (06:10 UTC / 08:10 LT) yra konfigūruotas, bet 08:26 LT naujo schedule vykdymo dar nerasta. Būsena **LAUKIA / NEPATVIRTINTA**; nenaudoti rankinio paleidimo kaip cron įrodymo.
- Worker AI ciklas 10:20 LT dar laukia. Po jo patikrinti tikrą agentų rezultatą, D1 atminties įrašą ir Control Center; issue #145 palikti atvirą iki patvirtinto atsistatymo.
- Vienintelis ChatGPT koordinatorius suplanuotas 11:00 LT. Nedaryti dublikatų.
- Šio audito metu jokie kodo, Worker/D1, DNS, secrets, ARO Vet, viešo turinio ar mokamų paslaugų pakeitimai neatlikti.


## 2026-11-15 – pagrindinio koordinatoriaus laiko korekcija

- Vienintelė kasdienė priežiūros automatizacija perkelta iš 11:00 į 11:45 Europe/Vilnius. Priežastis: Control Center 08:40 UTC cron turi 60 min. grace iki 11:40 LT; ankstesnis 11:00 koordinatorius galėjo patikrinti būseną per anksti.
- Naujų kasdienių automatizacijų nesukurta; pagrindinė automatizacija lieka enabled.
- Saugus issue #145 komentarų tiltas leidžia tik savininkui Pershore paleisti tris fiksuotus workflow veiksmus: daily-suite, D1 snapshot sync ir Control Center. Rankiniai workflow_dispatch vykdymai nėra schedule įrodymas.


## 2026-11-15 – Worker AI ciklas po dienos duomenų sinchronizavimo

- Kasdienis koordinatorius lieka 11:45 LT; Worker AI ciklas perkeliamas į 13:20 LT, kad būtų po daily-suite catch-up, D1 sync ir Control Center grace.
- PR #217 keičia Cloudflare cron į 10:20 ir 11:20 UTC su Europe/Vilnius vartais 13:20 LT. Dabartinis run_date idempotency reiškia, kad šiandien jau atliktas 10:20 ciklas nebus pakartotas; pirmas pilnas naujo grafiko ciklas laukiamas 2026-11-16 13:20 LT.


## 2026-11-15 – po-ciklinė AI patikra

- Aktyvių suplanuotų užduočių limitas yra 3; nauja užduotis nebuvo sukurta. Esamas greičio stebėjimo agentas papildytas Worker AI 13:20 LT ciklo patikra ir perkeltas į 14:00 LT.
- Pagrindinis koordinatorius lieka 11:45 LT; ARO Vet analitika lieka 18:24 LT. 14:00 agentas tikrina Control Center artefaktą ir nebandys rankiniu būdu paleisti Worker AI.
