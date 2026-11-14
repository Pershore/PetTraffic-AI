# Pet traffic – naujos sesijos pradžios protokolas

Atnaujinta: 2026-11-14

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

## Dabartinė būsena po 2026-11-14 Worker diegimo

1. Cloudflare API tokeno rotacija ir GitHub Actions secret CLOUDFLARE_API_TOKEN pakeitimas: vartotojas patvirtino abu veiksmus; pakartotinė CI patikra sėkminga.
2. PR #183 sujungtas squash commit 6a285a5505e88853a77fb1e31c08fa4fb1d9ad63. Worker JSON išvesties pataisa įdiegta per Actions run #43592016509; Worker versija a34f8850-e1bf-42c0-a055-3e9c9c8714c0.
3. Po deploy patvirtinta: D1 connected, control-core schema connected, /health ok=true, neautentifikuotas /v1/events grąžina 401. D1 migracijų taikyti nereikėjo.
4. AI agentų pataisos veiksmingumas dar NEPATVIRTINTAS: gyvas /health vis dar rodo ankstesnį 2026-11-14 08:20 UTC ciklo gedimą model_content-review_model_output_invalid_json. Kitas numatytas agentų ciklas – 2026-11-15 08:20 UTC (10:20 Europe/Vilnius).
5. GitHub Actions schedule problema lieka NEPATVIRTINTA / REIKIA DĖMESIO: YAML cron yra, bet ankstesnėje istorijoje suplanuotų paleidimų trūko; tiksli priežastis nežinoma. Nekeisti cron spėliojant.
6. Android Termux / Codex lokali aplinka PATIKRINTA pagal 2026-11-14 vartotojo bootstrap išvestį: proot, Git, GitHub CLI, Codex CLI, Codex autentifikacija OK; main...origin/main. Tai nėra foninio agento įrodymas.
7. GA4 30 s timeout pataisa turi vieną sėkmingą realų analytics ciklą; ilgalaikį stabilumą reikia vertinti pagal kitus suplanuotus ciklus.
8. Worker /v1/tasks* API lieka tyčia išjungta iki atskiros agentų tapatybės ir leidimų politikos.

Prieš tęsiant perskaityti docs/PROJECT_MEMORY.md 12 skyrių ir naujausius Actions / Worker įrodymus. Nelaikyti seno agentų gedimo naujos pataisos nesėkme – kol naujas ciklas neįvyko, būsena yra LAUKIA.

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
