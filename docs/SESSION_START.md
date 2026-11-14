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
6. Android Termux / Codex autentifikacija ir lokalaus repo būsena telefone vis dar LAUKIA; CI bridge testai nėra telefono prisijungimo įrodymas.
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
- Kitas žingsnis: vartotojui vieną kartą pakartoti bootstrap iš Termux. Iki realios telefono išvesties gh/Codex autentifikacija lieka LAUKIA.


## Termux / Codex patikslinimas (2026-11-14)

Tikras bootstrap iš Termux patvirtintas: Linux proot, Git, GitHub CLI, Codex CLI įdiegti; Codex autentifikacija OK; `main...origin/main`. Tai nėra nuolatinio fono agento ar automatinio GitHub užduočių paėmimo įrodymas. Kitas etapas – saugios užduočių eilės ir atskiros agento tapatybės projektavimas; `/v1/tasks*` palikti išjungtą iki saugumo patikros.
