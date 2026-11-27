# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-27T13:10:40.298717+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 46004827639
- Šaltinio commit: d2d448afabb7efd96dbedaa6f31d865aab932df7

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-27 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-26T16:46:08Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 10 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-27 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-26T16:46:08Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/45979691648
- **AI agentai + control-core atmintis** (warning): AI agentų ciklas ir atminties įrašymas baigti; rekomendacijų: 1; trūksta įrodymų: 5. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Lighthouse auditas: Workflow atnaujintas 2026-11-23 14:10 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.

## AI agentų ir atminties patikra

- Būsena: **warning** – AI agentų ciklas ir atminties įrašymas baigti; rekomendacijų: 1; trūksta įrodymų: 5.
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


## Papildomas auditas 2026-11-27 – post-cycle ir PR #321

- **PATIKRINTA:** Daily-suite `event=schedule` 2026-11-27 nerastas; paskutinis schedule #45861785605 (2026-11-26 16:46:08 UTC). Šiandienos Daily-suite #45979691648 buvo owner-bridge `workflow_dispatch`, ne schedule. Site-check ir analytics-connectivity paskutiniai schedule taip pat 2026-11-26.
- **PATIKRINTA:** post-cycle Control Center #46004827639 (`push`, success, report 13:10:40 UTC) ir po jo sync #46004902261 bei SELECT-only diagnostics #46004944841 success. Worker AI run_date 2026-11-27, started_at 11:20:23 UTC (13:20:23 LT), completed, 5/5 AI calls, error_code=null, valid report JSON, 0 degraded specialists, 0 invalid payloads. Worker API/D1 healthy, heartbeat 200; D1 turi po vieną analytics/topic/control-center/recommendation snapshot įrašą.
- **PATIKRINTA:** Control Core ir memory present, tačiau `needs_evidence`, 5 spragos, 1 rekomendacija; `recovery_confirmed=false`. Control Center/recommendation snapshot'ai D1 įrašyti po AI ciklo pradžios, todėl jų trūkumas šios dienos agentų spragose paaiškinamas laiko seka. Issue #145 lieka open.
- **PATIKRINTA:** content-review šiandien invalid JSON nekartojo; report JSON validus, invalid payload count 0; content-review `needs_evidence/insufficient_evidence`. Jei klaida pasikartos, naudoti vieną ribotą deterministinį JSON normalizavimo/validavimo bandymą ir išsaugoti validžius dalinius laukus.
- **ATLIKTA:** PR #321 atskiroje šakoje pašalintas dubliuotas JS const, apribotas manual diagnostics reuse iki tikslaus title/10 min. lango, atnaujinti regression testai. Naujausias CI: site-check #46008334749 success, 165 testai, 21 s; sync-control-api PR #46008334700 test success. PR #321 draft, 12 ahead/0 behind, nesujungtas.
- **PARUOŠTA:** PR #321 baseline 53 s wall / 42 s runner per tris etapus; po pakeitimo sutaupymas dar neišmatuotas. PR aprašyme nurodytos rizikos ir bounded legacy compatibility.
- **LAUKIA:** kito tikro Daily-suite schedule, Control Center po schedule, kito Worker AI ciklo 2026-11-28 13:20 LT ir `recovery_confirmed=true`. D1 schema versija report'e neatskleista; jokie production, Worker/D1, DNS, secrets, permissions, ARO Vet ar viešo turinio pakeitimai neatlikti. Aktyvus darbo laikas NEMATUOTAS.
