# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-27T12:18:47.545738+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 45997561126
- Šaltinio commit: 2fe9a6e27a28a621fa52ff9c67eff7ae2963c92e

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: GA4, temų radaras ir svetainės stebėjimas (warning). Suplanuotas ciklas nuo 2026-11-27 06:10 UTC dar neįvykdytas; paskutinis suplanuotas paleidimas buvo 2026-11-26T16:46:08Z. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 3 min.

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


## 2026-11-27 14:53 LT – post-cycle verifier

- **PATIKRINTA – Worker AI:** diagnostika #45997727040 / artefaktas #15195769794. `run_date=2026-11-27`, `started_at=2026-11-27T11:20:23.466Z` (13:20:23 LT), `status=completed`, `ai_calls=5`, `error_code=null`, `report_json_status=valid_object`; 4 specialistai, degraded=0, invalid_event_payload_count=0. Memory present, atnaujinta 11:21:17.382Z, tos pačios dienos run. Worker AI ciklas atitinka PATIKRINTA kriterijus.
- **PATIKRINTA – Worker / D1:** Control Center #45997561126 (workflow_dispatch, 25 s) nurodo Worker API ir D1 healthy, site heartbeat sėkmingą maždaug 3 min. iki report. D1 read-only diagnostika atliko 7 SELECT, visi sėkmingi, `rows_written=0`; diagnostinės lentelės pasiekiamos. Migracijos/schema versijos numeris nepateiktas.
- **NEPATVIRTINTA – Control Core:** present, bet `status=needs_evidence`, 5 evidence gaps, 1 recommendation; memory present, bet `last_status=needs_evidence`. Analytics ir topic snapshot'ai yra iš owner-bridge fallback #45979691648; `control_center_snapshot=0`, `recommendation_snapshot=0`. `recovery_confirmed=false`; Issue #145 lieka open.
- **NEPATVIRTINTA – schedule:** 2026-11-27 iki 12:53 UTC nėra Daily-suite, site-check ar Google API connectivity `event=schedule`. Paskutiniai tikri schedule įvyko 2026-11-26. Owner-bridge Daily-suite #45979691648 ir sync #45980279823 buvo `workflow_dispatch`, todėl cron įrodymu nelaikomi.
- **PATIKRINTA – post-cycle report:** Issue #145 komentaras #7218086342 paleido Control Center report po 13:20 LT; ataskaita sėkminga, bet manual fallback, ne automatinis `workflow_run` po schedule. Diagnostikos komentaras #7218110236 paleido read-only D1 ataskaitą. Papildomas Control Center komentaras nekartotas, nes sėkmingas report jau yra per paskutines 60 min.
- **PATIKRINTA – greitis:** Daily-suite fallback 38 s; analytics 28 s, live-check 19 s, topic-radar 19 s, visi duomenų job'ai lygiagretūs. Site-check #45981779314 runner job 14 s; sync #45980279823 job 10 s; Control Center 25 s; D1 diagnostics 14 s. Nėra pagrįsto greičio pagerėjimo teiginio.
- **ATLIKTA:** PR #301 aprašymas papildytas nauju docs-only matavimu; prieš merge baseline 285 s / 19 main push'ų. PR lieka open, 53 commits behind, nejungtas. Kiti PR #312/#306 draft ir diverged.
- **Kitas veiksmas:** laukti tikro Daily-suite `event=schedule`; po jo patvirtinti automatinį Control Center `workflow_run` ir D1 sync. Worker AI šiandien PATIKRINTA; Control Core recovery dar NEPATVIRTINTA. Issue #145 neuždaryti.


## 2026-11-27 15:07 LT – PR #320 CI ir saugumo peržiūra

- **PATIKRINTA:** naujas draft PR #320 siūlo užbaigti owner-bridge grandinę: Daily-suite → D1 sync → Control Center → Control Center D1 sync → read-only diagnostics, kad būtų įrašyti trūkstami control-center/recommendation snapshot'ai.
- **NEVEIKIA:** PR site-check #46004053655 – 6 testų assertion failures `tests/test_dispatch_bridge_workflow.py`, 163 testai per 6.080 s; testai tikisi senų bridge kodo tekstinių žymeklių. PR #320 lieka draft.
- **SAUGUMAS:** PR dispatch job prideda `id-token: write`, nors aprašyme teigiama, kad permissions nekeičiamos; ši teisė dispatch job nereikalinga. `timeout-minutes: 45` ir iki 18 min. polling limitai taip pat per platūs. Main nepakeistas.
- **PATIKRINTA:** PR Deploy API patikros sėkmingos, tikras deploy job skipped; Sync API PR test sėkmingas, sync job skipped. Produkcija nekeista.
- **ATLIKTA:** PR #320 komentare #7219075459 pateiktos CI, least-privilege ir timeout pastabos. PR paliktas draft, merge neatliktas.
- **PATIKRINTA:** po ankstesnio darbo žurnalo įrašo site-check #46004125231 (push iš `b27efa81`) success, 18 s wall / 14 s runner job.
- **Kitas veiksmas:** laukti pataisyto PR #320 CI, pašalintos nereikalingos OIDC teisės ir trumpesnio laiko biudžeto; tik po to vertinti owner-bridge D1 snapshot recovery. Issue #145 lieka open.


## 2026-11-27 15:09 LT – PR #320 CI atnaujinimas

- **PATIKRINTA:** PR #320 head atnaujintas į `ba18610d`; po ankstesnio CI failure naujas site-check #46004367761 success, Deploy API PR test/validation success (deploy skipped), Sync API PR test success (sync skipped).
- **NEPATVIRTINTA:** PR branch vis dar turi `id-token: write` dispatch job'e ir 45 min. timeout. Tai prieštarauja aprašymui ir least-privilege; PR lieka draft.
- **ATLIKTA:** follow-up komentaras #7219108916 įrašytas; merge/deploy neatliktas.
- **PATIKRINTA:** ankstesnio work-log commit'o site-check #46004432598 success, 17 s wall.
- **Kitas veiksmas:** laukti PR #320 permission/timeout pataisymo ir naujo CI; tik po to vertinti D1 snapshot readback. Main ir production nepakeisti.
