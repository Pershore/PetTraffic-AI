# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-19T12:52:48.095594+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 44527976145
- Šaltinio commit: 34ef34f594b39b66b61290ac63c72e20ecc9eb05

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-19 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-18T15:32:01Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Lighthouse auditas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 7 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-19 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-18T15:32:01Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/44524989314
- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-18. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Nėra.

## AI agentų ir atminties patikra

- Būsena: **stale** – Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-18.
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


## 2026-11-19 14:45 LT – post-cycle patikslinimas

- **Būsena:** REIKIA DĖMESIO. Šiandienos Daily-suite `event=schedule` nėra; paskutinis tikras schedule #44336724612 (2026-11-18 15:32:01Z, 36 s). Šiandienos manual fallback #44524989314 success per 35 s, bet `workflow_dispatch` neįrodo cron atkūrimo ir neatveria AI vartų.
- **PATIKRINTA:** Control Center #44525922276 (`workflow_run`) success per 23 s; ataskaita po 13:20 LT, artifact #14528424954, `recovery_confirmed=false`. Worker API/D1 sveiki, heartbeat prieš 9 min. sėkmingas.
- **PATIKRINTA:** Worker D1 diagnostika #44525986057 success per 10 s; artifact #14529209792, septynios SELECT-only užklausos, `rows_written=0`. `run_date=2026-11-19`, `agent_run=missing`, `ai_calls=0`, `started_at=null`, `error_code=null`; 4 specialistai ir Control Core missing. Memory present, bet paskutinis run 2026-11-18T15:45:25.164Z (`needs_evidence`), gap codes `insufficient_evidence` ir `search_volume_not_available`. Šios dienos analytics/topic snapshot yra iš manual `workflow_dispatch`, ne schedule.
- **PATIKRINTA:** diagnostikos eiliškumo lenktynė pakartota: Control Center #44525922276 baigėsi 12:39:55Z, diagnostikos artefaktas sugeneruotas 12:40:05Z, sync #44525986131 baigėsi 12:40:09Z. Diagnostika perskaitė ankstesnį Control Center snapshot #44525590774.
- **JSON:** paskutinė žinoma `model_content-review_model_output_invalid_json` klaida – 2026-11-15; PR #183 prompt guard sujungtas, Worker deploy #44165044215 success 2026-11-17. 2026-11-18 ciklo report JSON validus, content-review `needs_evidence`, ne `invalid_json`. 2026-11-19 ciklo nėra, todėl šiandien pakartojimas netestuotas.
- **ATLIKTA / PARUOŠTA:** PR #290 draft, 2 commits ahead / 0 behind; pakeistas tik Worker D1 diagnostikos workflow trigger ir regresijos testas. Worker Node/Python, Cloudflare validation, snapshot-sync PR testai ir site-check success; production deploy skipped. PR #288 uždarytas kaip pasenęs dublikatas. PR #290 po sync tikimasi pridėti ~11 s laukimo, tačiau užtikrinti naujausio D1 snapshot readback; after timing dar NEMATUOTA.
- **LAUKIA:** šiandienos Worker AI ciklas ir šviežia D1 atmintis; issue #145 paliktas open, `recovery_confirmed=false`.
- **Saugumas:** production Worker/D1, ARO Vet, DNS, secrets, paskyrų nustatymai, viešas turinys ir mokamos paslaugos nepakeisti. Aktyvus darbo laikas NEMATUOTAS.

Kitas žingsnis: laukti tikro Daily-suite schedule, po jo patikrinti Control Center → sync → D1 diagnostikos seką ir tik tada vertinti AI ciklo atkūrimą. PR #290 nejungti automatiškai.
