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

## Dabartiniai pagrindiniai blokatoriai (2026-11-14)

1. Cloudflare API tokenas laikomas galimai atskleistu. Rotacijos ir GitHub Actions secret `CLOUDFLARE_API_TOKEN` atnaujinimo įrodymo nėra. PR #183 Worker deploy lieka sustabdytas.
2. GitHub Actions YAML grafikai egzistuoja, bet 2026-11-14 schedule paleidimai nepatvirtinti. Tiksli priežastis nežinoma; dabartinė GitHub jungtis neleidžia valdyti Actions nustatymų.
3. Worker AI agentų paskutinis žinomas ciklas failed `model_content-review_model_output_invalid_json`; PR #183 atviras, jo production deploy job skipped.
4. Android Termux / Codex CLI autentifikacija ir lokali repo būsena nepatvirtintos; ChatGPT neturi tiesioginės Android shell prieigos.
5. GA4 timeout 30 s pataisa sujungta ir vienas realus analytics run success, bet ilgalaikis stabilumas dar neįrodytas.

Prieš tęsiant šiuos punktus dar kartą perskaityti `docs/PROJECT_MEMORY.md` ir naujausius įrodymus. Neperrašyti jau patvirtintos būsenos spėjimais.

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
