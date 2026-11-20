# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-20T12:59:59.622803+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 44740427191
- Šaltinio commit: b7768fe120a2f6e29d52e641f94b419f98343dac

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-20 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-19T15:38:40Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Lighthouse auditas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 14 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-20 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-19T15:38:40Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/44716442982
- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-19. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Nėra.

## AI agentų ir atminties patikra

- Būsena: **stale** – Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-19.
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


## 2026-11-20 14:53 LT – nepriklausoma post-cycle ir greičio patikra

- **PATIKRINTA – pradžios protokolas:** šios sesijos pradžioje perskaitytas `automation-history/reports/history/project-state/latest.md` (pradinis blob SHA `24fd8d08bd1910f0b78f7a3bce564839d830f210`) ir `main/reports/work-log/README.md` (pradinis blob SHA `e796da310e312991beb7f5f93a7ed06485707d48`). Šakų atskyrimas išlaikytas.
- **PATIKRINTA – GitHub:** main HEAD `b7768fe120a2f6e29d52e641f94b419f98343dac`. Atviri draft PR prieš šią sesiją: #294, #280, #267, #263, #261, #266, #264; parengtas naujas #297. Nė vienas PR nesujungtas.
- **NEVEIKIA – Daily-suite schedule:** 2026-11-20 nėra `event=schedule` Daily-suite vykdymo. Paskutinis tikras schedule #44557115983 (2026-11-19T15:38:40Z, success). Šiandienos #44716442982 yra `workflow_dispatch`, success, apie 54 s; jis nėra cron įrodymas. Site-check šiandien taip pat neturi `event=schedule`; paskutinis tikras schedule #44546115868 (2026-11-19T14:39:25Z). Šiandienos #44719519986 yra `push`, success, 17 s. Lighthouse paskutinis schedule #43915631789 (2026-11-16), success; kitas savaitinis grafikas 2026-11-23.
- **PATIKRINTA – Daily-suite etapai ir lėčiausias žingsnis:** dabartiniame manual #44716442982 analytics testai 8.154 s, Google priklausomybių diegimas 3.794 s, `agent/analytics_report.py` 28.717 s; topic-radar testai 2.427 s ir radaras 2.873 s; live-check 8.142 s. Ankstesniame tikrame schedule #44557115983 atitinkamai analytics testai 9.174 s, priklausomybės 3.485 s, analytics report 11.088 s; topic testai 1.504 s, radaras 2.078 s; live-check 12.798 s. Šiandien analytics logas aiškiai pranešė: `GA4 report read timed out; skipping duplicate retry to keep the daily cycle fast.` Ataskaita vis tiek sukurta ir job success. GA4 žingsnis šiandien 2.6 karto ilgesnis nei ankstesniame palygintame vykdyme; tai vienas timeout atvejis, todėl kodo timeout/retry nekeičiau.
- **PATIKRINTA – kiti vykdymai:** snapshot sync #44739053965 success, 8.295 s. Worker read-only diagnostika #44719051028 success, apie 10 s (iki 13:20 ciklo). Control Center #44738929050 success, 20.207 s; #44738942660 success, 18.280 s; po kito bridge veiksmo #44739464586 success, 18.764 s. Lighthouse #43915631789 success, 223 s. Site-check #44719519986 success, 17 s.
- **PATIKRINTA – post-cycle Control Center:** iki 13:20 LT nebuvo naujo sėkmingo reporto ir per ankstesnes 60 min. nebuvo sėkmingo Control Center run; issue #145 buvo pasiekiamas. Pridėtas tikslus komentaras `/pettraffic-run-control-center` (#7039938557). Naujausia po-ciklo ataskaita: Control Center #44739464586, artifact #14630266960, generated_at `2026-11-20T12:52:56Z` (14:52:56 LT), success. Ataskaita patvirtina Worker API + D1 success, heartbeat prieš 7 min., AI agentų būseną `stale` (po 13:20 šiandienos ciklo nėra; paskutinis įrašas 2026-11-19), `recovery_confirmed=false`, 3 Control Center rekomendacijas. Issue #145 lieka open.
- **LAUKIA – AI/D1 detalės:** Control Center artefakte nėra atskirų laukų `agent_orchestration.run_date/status/ai_calls/error_code`, `control_core.status`, `memory_status`, `evidence_gaps` ar D1 `recommendation_count`; šių reikšmių neišgalvoju. Papildomam SELECT-only readback pridėtas bridge komentaras `/pettraffic-run-agent-diagnostics` (#7040013748), tačiau šio atskiro workflow run ID ir artefakto šioje patikroje nepriklausomai ištraukti nepavyko. Todėl šiandienos Worker AI ciklas žymimas LAUKIA / nepatvirtintas, ne PATIKRINTA. Jokių /v1/tasks ar rankinių agentų paleidimo endpointų nenaudota.
- **JSON klaida:** paskutiniame patvirtintame 2026-11-19 AI cikle `content-review_model_output_invalid_json` nebuvo užfiksuota; content-review buvo `needs_evidence`, ne `invalid_json`. Šiandienos AI ciklo nėra, todėl naujo pasikartojimo patikrinti negalima.
- **ATLIKTA / PARUOŠTA – PR #297:** atskira šaka `perf/dedupe-control-center-bridge-20261120`, 3 commits ahead / 0 behind main, 3 failai pakeisti. Pašalintas secure bridge kaip papildomas Control Center `workflow_run` trigeris, išlaikytas tiesioginis `workflow_dispatch` komandai `/pettraffic-run-control-center`, deduplikacija apima `workflow_run`, `workflow_dispatch` ir `schedule`. Regresijos testas patvirtina vieną trigerio kelią ir išsaugo Daily-suite, Lighthouse, Worker deploy trigerius. CI #44740413005 success: naujas testas passed, 151 Python testų ir 31 agent testas passed; Control Center PR patikra #44740412988 success. PR #297 draft, mergeable=true, nesujungtas.
- **Greičio įrodymas PR #297:** vienas komentaras #7039938557 sukūrė du Control Center run: #44738929050 (20.207 s) ir #44738942660 (18.280 s), iš viso 38.487 s runner laiko vienam prašytam reportui. Po pataisos rezultatas dar NEMATUOTAS; prognozuojamas vienas 18–20 s run yra tik įvertis, ne faktinis pagerėjimas. Po galimo žmogaus patvirtinto merge būtina pamatuoti realų vieno run rezultatą.
- **NEKEISTA:** main programinis kodas, produkcinis Worker/D1, D1 schema/duomenys (išskyrus įprastus jau įvykusių workflow snapshot įrašus), DNS, secrets, paskyrų teisės, ARO Vet, viešas turinys, repository settings ir billing. Mokamų paslaugų nenaudota.
- **Darbo laikas:** aktyvus darbo laikas NEMATUOTAS; tikslios GitHub job/step trukmės pateiktos tik ten, kur jos ištrauktos iš run log timestamp.
- **Kitas žingsnis:** laukti tikro Daily-suite `event=schedule`; po jo patikrinti Control Center → snapshot sync → SELECT-only D1 diagnostiką ir šiandienos/rytojaus AI ciklo įrašą. PR #297 palikti draft iki žmogaus peržiūros; po galimo merge patikrinti, kad vienas bridge komentaras sukuria vieną Control Center run. Issue #145 neuždaryti, kol schedule, AI ciklas, D1 atmintis ir `recovery_confirmed=true` nepatvirtinti.
