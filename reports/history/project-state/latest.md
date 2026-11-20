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


## 2026-11-20 15:10 LT – po-ciklo D1 ir patikimumo būsena

- **PATIKRINTA – šakų protokolas:** latest.md perskaitytas iš `automation-history` (pradinis blob SHA `4c10f7142b95f073409a266350465b191ccd6451`); work-log perskaitytas iš `main` (blob SHA prieš atnaujinimą `7b108780de20a7dc5e23da28051a48b6b20aede6`). `main/reports/work-log/README.md` atnaujintas atskirai, commit `1af39ba542515afde310d9b25436fa3adcb987b2`, naujas blob SHA `bcc3eee68a2f8dc3352a9ccf3de6e58f144ea942`.
- **PATIKRINTA – naujausias main:** po darbo žurnalo įrašo `main` HEAD `1af39ba542515afde310d9b25436fa3adcb987b2`. Naujausias prieš šį įrašą buvęs commit `e1cfda9b5d4ea9ad068976460a2e1bddf0f9fe28` buvo dokumentavimo įrašas. Atviri draft PR: #297, #294, #280, #267, #266, #264, #263, #261. PR #297 3 commits ahead / 1 behind main, lieka draft ir nesujungtas.
- **NEVEIKIA – Daily-suite schedule:** 2026-11-20 `event=schedule` nėra. Paskutinis žinomas tikras Daily-suite schedule #44557115983 (2026-11-19T15:38:40Z). Šiandienos #44716442982 `workflow_dispatch` success per 54 s; analytics, topic-radar ir live-check jobai success, bet manual fallback nepakeičia schedule provenance ir neatveria AI vartų. Site-check šiandienos #44741406520 buvo `push`, success per 15 s; tikro site-check schedule šiandien nėra.
- **PATIKRINTA – vykdymų trukmės:** Control Center #44740427191 success, 27 s; artifact #14630686343, generated_at `2026-11-20T12:59:59Z` (14:59:59 LT). Snapshot sync #44740503319 success, 10 s. Read-only D1 diagnostics #44740538647 success, 13 s; artifact #14630811146, generated_at `2026-11-20T13:00:45Z` (15:00:45 LT). Site-check #44741406520 success, 15 s. Palyginimas su ankstesniais: Control Center 24 s, sync 10 s, diagnostics 10 s; patikimo pagreitėjimo nėra.
- **PATIKRINTA – Worker/D1:** Control Center reportas Worker API ir D1 žymi success; heartbeat sėkmingas prieš 14 min. reporto generavimo metu. SELECT-only diagnostika sėkminga. D1 atskiro schema-health lauko artefakte nėra, todėl visos schemos būsenos atskirai nepatvirtinu.
- **LAUKIA – AI/D1 atmintis:** šiandien `run_date=2026-11-20`, `agent_run.present=false`, status `missing`, `ai_calls=0`, `started_at=null`, `error_code=null`; visi 4 specialistai missing su `specialist_report_missing`; coordinator ir `control_core` missing; coordinator `recommendation_count=0`. Memory present, bet paskutinis įrašas 2026-11-19T15:45:21.548Z, status `needs_evidence`, gap codes `insufficient_evidence`, `search_console_data_missing`, `search_volume_not_available`. Control Center pateikė 3 rekomendacijas; `recovery_confirmed=false`.
- **JSON klaida:** šiandien nėra agentų vykdymo, todėl `content-review_model_output_invalid_json` negalima įvertinti. `report_json_status=missing_or_invalid` šiame artefakte atitinka neegzistuojantį `agent_run`, o ne patvirtintą netaisyklingą šiandienos modelio JSON. Paskutinis žinomas 2026-11-19 ciklas šios klaidos nerodė; content-review buvo `needs_evidence`.
- **Bridge / issue #145:** issue #145 lieka open. Sėkmingas post-cycle Control Center reportas #44740427191 ir D1 diagnostika #44740538647 yra paskutinių 60 min. lange, todėl papildomas `/pettraffic-run-control-center` ar agent-diagnostics komentaras nepridėtas. Nenaudoti `/v1/tasks` ir rankinių agentų paleidimo endpointų.
- **ATLIKTA / NEKEISTA:** `main` work-log įrašas sėkmingai įrašytas ir perskaitytas po commit. Šiame vykdyme kodo, workflow, PR, Worker/D1 produkcijos, D1 schemos, DNS, secrets, paskyrų ar repository nustatymų, ARO Vet, viešo turinio ir billing pakeitimų nebuvo. Papildomų scrape ar mokamų paslaugų nenaudota.
- **Kitas veiksmas:** laukti tikro Daily-suite `event=schedule`; po jo patikrinti Control Center → snapshot sync → SELECT-only D1 diagnostiką ir vienintelį dienos Worker AI ciklą po 13:20 LT. Issue #145 neuždaryti, kol schedule, AI ciklas, D1 atmintis ir `recovery_confirmed=true` nepatvirtinti. Aktyvus darbo laikas NEMATUOTAS.

## 2026-11-20 15:11 LT – PR #297 bazės pakartotinė patikra

- **PATIKRINTA – PR #297 būklė po šio audito work-log commit:** naujausias `main` HEAD `1af39ba542515afde310d9b25436fa3adcb987b2`; `compare_commits(main...perf/dedupe-control-center-bridge-20261120)` rodo 3 commits ahead / 2 behind, o PR API `mergeable=false`. PR lieka draft, nesujungtas.
- Ankstesniame 15:10 įraše nurodyti 3 ahead / 1 behind atitiko tuometinį `main` HEAD `e1cfda9`; po work-log commit main pasistūmėjo dar vienu commit, todėl dabartinis atsilikimas yra 2.
- **ATLIKTA:** PR neperbazavau ir nekeičiau, nes tam reikia naujos izoliuotos šakos/CI ciklo; jokių merge veiksmų neatlikta. Kitas žingsnis – atnaujinti PR šaką nuo dabartinio main ir iš naujo paleisti visus reikalingus testus tik prieš svarstant žmogaus peržiūrą.

## 2026-11-20 15:12 LT – galutinė po-įrašo patikra

- **PATIKRINTA – dabartinis main:** po dviejų šios sesijos darbo žurnalo commit `main` HEAD yra `87e5e29d3f4a67585ab96f58c6ca7fb277b55445`; `reports/work-log/README.md` blob SHA `98d5aad5879df52f76ce8157ac48f4d65cc3a0d6`.
- **PATIKRINTA – po-įrašo CI:** site-check #44743287988 (`push` ant `1af39ba`) success, 18 s; site-check #44743563069 (`push` ant dabartinio `main` `87e5e29`) success, 21 s. Tai dokumentavimo commitų patikros, ne Daily-suite schedule įrodymai.
- **PR #297 dabartinė būklė:** po paskutinio main dokumentavimo commit palyginimas rodo 3 commits ahead / 3 behind; PR lieka draft, `mergeable=false`, nesujungtas. Ankstesnis 2-behind matavimas buvo teisingas prieš paskutinį korekcijos work-log commit; dabar branch drift dar vienu commit didesnis. PR šakos neatnaujinau ir CI nepaleidau iš naujo.
- **Kitas žingsnis:** PR #297 tik atnaujinti nuo dabartinio main atskiroje šakoje ir pakartoti CI po žmogaus peržiūros; Daily-suite schedule ir Worker AI recovery lieka pagrindiniai projekto blokatoriai.

## 2026-11-20 15:23 LT – Daily-suite ciklo atkūrimo diagnozė

- **PATIKRINTA:** pradžios dokumentai perskaityti teisingose šakose; latest.md pradinis blob SHA `27213d1b10e07fa4f4fd5af4b00bdb3ab0d12e8c`. main darbo žurnalas atskirai papildytas commit `5e2ce7b0e437a168d9548392ac256ea2f1111519`.
- **PATIKRINTA:** `main/.github/workflows/daily-suite.yml` turi `schedule: "10 6 * * *"` ir `workflow_dispatch`; suplanuoto įvykio konfigūracija faile yra.
- **NEVEIKIA:** 2026-11-20 tikras Daily-suite `event=schedule` nevyksta / neaptiktas. #44716442982 yra sėkmingas `workflow_dispatch` fallback (~54 s), ne cron įrodymas.
- **PATIKRINTA:** esamas issue #145 bridge `/pettraffic-run-daily-suite` yra savininko autorizuotas, tačiau guard deduplikuoja, jei tą pačią UTC dieną jau yra sėkmingas ar vykdomas manual fallback. Kadangi #44716442982 jau sėkmingas, pakartotinis komentaras tik būtų no-op; jo nepridėjome.
- **LAUKIA:** Worker AI šiandienos ciklas nepatvirtintas; manual fallback negali atitikti Worker `source_event=schedule` vartų. Nenaudoti `/v1/tasks` ar rankinių agentų endpointų.
- **Blokatorius:** prieinama GitHub integracija neatskleidžia Actions scheduled-workflow aktyvumo/suspendavimo nustatymo. Reikalingas vienas tikslinis patikrinimas GitHub repo **Settings → Actions → General**: patvirtinti, kad Actions ir scheduled workflows nėra išjungti / pristabdyti. Repository settings nekeisti šio vykdymo metu.
- **NEKEISTA:** jokie workflow/kodas, Worker/D1 produkcija, DNS, secrets, repo nustatymai, ARO Vet ar billing.
- **Kitas veiksmas:** patvirtinus Actions schedule aktyvumą, laukti kito 06:10 UTC cron ir patikrinti tikrą `event=schedule` → Control Center → snapshot sync → SELECT-only D1 diagnostiką → AI 5/5 bei atmintį. Issue #145 lieka open iki `recovery_confirmed=true`. Aktyvus darbo laikas NEMATUOTAS.


## 2026-11-20 15:48 LT – pakartotinis ciklo atkūrimo bandymas

- **PATIKRINTA – pradžios protokolas:** prieš tikrinimą iš naujo perskaitytas šis failas iš `automation-history` (blob SHA `083ee16660fdb96c6e9c2967aab20f92565f5432`) ir `main/reports/work-log/README.md` (blob SHA `59df42b30e70e8042cd904310be58b6aace52b50`).
- **PATIKRINTA – naujausia GitHub būsena:** `main` naujausias commit `5e2ce7b0e437a168d9548392ac256ea2f1111519`; atviri draft PR: #297, #294, #280, #267, #266, #264, #263, #261. Nė vienas PR nesujungtas.
- **NEVEIKIA – Daily-suite schedule:** šiandienos run sąraše vis dar nėra `event=schedule`. Vienintelis šiandienos Daily-suite #44716442982 yra `workflow_dispatch`, success, 54 s; tai nėra cron provenance. `.github/workflows/daily-suite.yml` cron `10 6 * * *` konfigūracija išlieka.
- **PATIKRINTA – bridge saugikliai:** `dispatch-daily-suite.yml` patvirtina, kad dienos sėkmingas manual fallback #44716442982 deduplikuoja pakartotinį daily-suite komentarą. Todėl komandinis komentaras šį kartą nepridėtas – jis nebūtų atkūręs schedule.
- **LAUKIA – Control Center:** paskutinis sėkmingas Control Center #44740427191 (event `workflow_run`, 12:59:52Z / 14:59:52 LT). 15:48 LT patikros metu dar nepraėjo 60 min. deduplikavimo langas; papildomas Control Center komentaras nepridėtas.
- **PATIKRINTA – naujausi kiti procesai:** Worker read-only diagnostika #44740538647, snapshot sync #44740503319 ir Control Center #44740427191 success. Naujausi site-check #44744111845 success, tačiau jo `event=push` – ne schedule įrodymas.
- **ISSUE #145:** lieka open; paskutinis atnaujinimas 13:00:12Z. Naujausios komandos jau apima Control Center ir agent diagnostics; šiame pakartojime naujų komandų nepridėta.
- **Worker AI:** šiandienos 5/5 AI ciklas ir D1 memory recovery lieka nepatvirtinti. Manual fallback nesuteikia `source_event=schedule`; rankinių agentų endpointų nenaudota.
- **Blokatorius:** GitHub API integracija neleidžia perskaityti repo Actions permissions nustatymų; šiuo vykdymu nustatymai nekeisti. Reikia žmogaus patikros Settings → Actions → General, ar Actions ir scheduled workflows įjungti.
- **NEKEISTA:** jokie workflow/kodas, production Worker/D1, DNS, secrets, repo settings, ARO Vet, svetainės turinys, PR merge ar billing.
- **Laikas:** aktyvus darbas NEMATUOTAS; dabartinės patikros laikas 15:48 LT, GitHub run trukmės – atskiri workflow elapsed matavimai.
- **Kitas veiksmas:** patvirtinti Actions/scheduled workflows aktyvumą; po kito tikro cron tikrinti Daily-suite `event=schedule` → Control Center → sync → SELECT-only D1 diagnostika → AI 5/5 ir atmintį. Issue #145 palikti open iki `recovery_confirmed=true`.


## 2026-11-20 15:52 LT – Actions įjungimo patvirtinimas ir cron diagnostika

- **VARTOTOJO PATVIRTINIMAS:** GitHub Settings → Actions nustatyme Actions / scheduled workflows rodomi kaip įjungti. Tai patvirtina bendrą nustatymą, bet neatskleidžia konkretaus `daily-suite.yml` workflow aktyvumo būsenos.
- **PATIKRINTA – GitHub run API:** peržiūrėta iki 100 naujausių repo run. `daily-suite.yml` šiame lange turi tik šiandienos #44716442982 (`workflow_dispatch`, success, 54 s); 2026-11-20 `event=schedule` nėra. Naujausias `main` site-check #44744111845 success (`push`), tai nėra schedule įrodymas.
- **PATIKRINTA – repo aktyvumas:** `main` šiandien turėjo push ir site-check įvykių, todėl 60 dienų repo neaktyvumo išjungimas nėra tikėtinas paaiškinimas.
- **TIKĖTINAS Kitas tikrinimo taškas:** individualus `daily-suite.yml` workflow gali būti išjungtas atskirai nuo bendro Actions nustatymo, arba GitHub cron event pristatymas neveikia. Ši integracija nepateikia workflow enable/disable statuso API; jo neatspėju ir pats nekeičiu.
- **Kitas tikslus žingsnis:** atidaryti repo Actions → Daily automation suite workflow puslapį ir patikrinti, ar viršuje siūlomas mygtukas **Enable workflow** (tai reikštų, kad konkretus workflow išjungtas). Jei matomas **Disable workflow**, workflow jau įjungtas ir reikia tirti GitHub schedule event pristatymą.
- **NEKEISTA:** jokie workflow failai, Actions/repo nustatymai, secrets, Worker/D1 production, DNS, ARO Vet, PR ar billing.
