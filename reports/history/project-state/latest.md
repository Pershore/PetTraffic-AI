# 2026-11-26 14:43 LT – papildyta patikrinta Pet traffic būsena

- **Būsena:** REIKIA DĖMESIO – tikras Daily-suite `event=schedule` šiandien iki 12:47 UTC nepastebėtas; Worker AI dienos ciklas pagal griežtus kriterijus PATIKRINTAS, tačiau Control Core/memory vis dar `needs_evidence`.
- **Main:** HEAD `dd8d7d91cc23a2b10b2b01e1f05a17c1d7b09b86`; atviri PR 8. PR #301 baseline atnaujintas iki 244 s / 16 docs-only push'ų, PR paliktas open ir nesujungtas; #312/#306 draft ir pasenę.
- **Daily-suite / schedule:** cron `10 6,8,10,11 * * *` UTC; 2026-11-26 iki 12:47 UTC nėra `event=schedule`. Paskutinis tikras schedule #45661106260 (2026-11-25 17:06:08Z). Owner-approved fallback #45804293548 buvo `workflow_dispatch`, success per 43 s; tai nėra schedule įrodymas.
- **Post-cycle Control Center:** issue #145 komentaras #7192419733 `/pettraffic-run-control-center`; bridge #45822650082 success; Control Center #45822677477 `workflow_dispatch` success per 27 s, artifact #15118153859 (2026-11-26T12:45:49Z). Worker API/D1 success, heartbeat šviežias; `needs_attention=true`, `recovery_confirmed=false`. Kontrolės ataskaita manual, ne schedule kilmės.
- **Worker AI – PATIKRINTA:** read-only D1 diagnostika #45822934692 success per 12 s, artifact #15118403594. `run_date=2026-11-26`, `started_at=2026-11-26T11:20:24.030Z` (13:20:24 LT), `status=completed`, `ai_calls=5`, `error_code=null`, `report_json_status=valid_object`; 4 specialistai, degraded=0, invalid event payload=0. Atmintis `present=true`, atnaujinta 11:20:39.166Z, bet `last_status=needs_evidence`.
- **Control Core – NEPATVIRTINTA recovery:** Control Core present, `status=needs_evidence`, 5 evidence gaps, 1 recommendation; coordinator `needs_evidence`, 1 recommendation. Specialistai: analytics needs_evidence, topics reviewed, technical-seo needs_evidence, content-review needs_evidence. D1 tą dieną neturi control_center_snapshot ir recommendation_snapshot; `recovery_confirmed=false`. Issue #145 lieka open.
- **D1/schema:** 7 SELECT sėkmingos, `rows_written=0`; diagnostikai reikalingos `agent_runs`, `control_core_runs`, `control_core_memory`, `events` lentelės pasiekiamos. Migracijos/schema versijos artefaktas nepateikia.
- **Content-review JSON:** šio ciklo bendras report JSON validus, `invalid_event_payload_count=0`; content-review grąžino `needs_evidence` / `other`, ne `invalid_json`. Paskutinis žinomas runtime invalid JSON įvykis – 2026-11-14. Main parser vis dar atmeta visą rezultatą, jei trūksta privalomų laukų; riboto taisymo kvietimo nėra.
- **Greitis:** Daily-suite 43 s (3/3 job success); topic-radar apie 1,92 s / 29 unikalios nuorodos; analytics reporto žingsnis baigėsi iki ~11,8 s artefakto upload pradžios; sync 13 s; site-check push 16 s ir PR 19 s; Control Center 27 s; D1 diagnostics 12 s. Nėra pagrindo teigti bendrą pagreitėjimą.
- **Kitas veiksmas:** laukti vėluojančio tikro Daily-suite schedule; po jo patikrinti automatinį Control Center ir sync `workflow_run`, D1 snapshot readback ir naują Worker ciklą. Issue #145 uždaryti tik po schedule, pilno Control Core/memory recovery ir `recovery_confirmed=true`.
- **Saugumas:** D1 tik SELECT; Worker/D1 production, ARO Vet, DNS, secrets, permissions, billing ir viešas turinys nepakeisti. Aktyvus techninio darbo laikas NEMATUOTAS.

---

# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-26T12:45:49.573285+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 45822677477
- Šaltinio commit: dd8d7d91cc23a2b10b2b01e1f05a17c1d7b09b86

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-26 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-25T17:06:08Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 0 min.

## Problemos

- **GA4, temų radaras ir svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-26 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-25T17:06:08Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/45804293548
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
