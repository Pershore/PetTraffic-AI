# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-21T12:34:45+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 44903952296 (Control Center); D1 diagnostika: 44904090148
- Šaltinio commit: a19d0d03b2d5ede87e7abbb6744f5186d7b03a11

## Paskutinis patikrintas etapas

Po 13:20 LT patikrintas Control Center report ir atlikta D1 SELECT-only diagnostika: Worker/D1 veikia, tačiau šiandienos AI agentų ciklas ir Control Core įrašai nerasti. PR #301 paruoštas ir CI patvirtintas.

## Kitas veiksmas

Patikrinti ir atkurti tikrą Daily-suite `event=schedule` pristatymą; šiandienos 06:10 UTC ciklas neaptiktas. Po 13:20 LT D1 diagnostika patvirtino, kad 2026-11-21 agentų run nėra (0 AI calls), todėl AI recovery nepatvirtintas. PR #301 laukia savininko peržiūros; nejungti automatiškai.

## Patvirtinti procesai

- Centrinės API sinchronizavimas: #44896902196 success, job 10 s.
- Lighthouse auditas: paskutinis sėkmingas #43915631789 (2026-11-16); kitas savaitinis ciklas dar neatėjęs.
- Centrinis valdymo centras: #44903952296 `workflow_dispatch` success, 25 s, artifact #14706569792.
- Site-check: #44897130923 main push success, 16 s; PR #301 patikra #44904330583 success, 17 s.
- Cloudflare Worker + D1: Control Center /health patvirtino Worker ir D1 connected; heartbeat sėkmingas prieš 12 min. D1 SELECT-only agent diagnostics #44904090148 success, artifact #14707286726; jokio D1 write.

## Problemos

- **Daily-suite / site-check / analytics-connectivity schedule – neįvyko 2026-11-21:** nėra nė vieno šiandienos `event=schedule`. Paskutiniai tikri schedule: Daily-suite #44762160249 (2026-11-20T15:19:45Z; ~9 val. 10 min. po 06:10 UTC), site-check #44752353278 (14:19:33Z; ~8 val. 43 min. po 05:37 UTC), analytics-connectivity #44768218809 (15:56:01Z; ~8 val. 59 min. po 06:57 UTC). Rankiniai/push/PR run nėra cron įrodymas.
- **AI agentai + Control Core – LAUKIA / stale:** 2026-11-21 run nerastas, 0 AI calls, 4 specialistai missing, Control Core missing; memory paskutinį kartą atnaujinta 2026-11-20. `recovery_confirmed=false`.
- **Content-review JSON – istorinis rizikos taškas:** paskutinis žinomas `model_content-review_model_output_invalid_json` iš 2026-11-14. Šiandien pasikartojimo nustatyti negalima, nes agentų run nėra. PR #261 (partial schema) ir #294 (content evidence) lieka draft, neįdiegti.

## Laukiančios patikros

- Tikrinti kitą vienintelį Worker AI ciklą tik per jo realų schedule ir D1 readback; rankiniu būdu agentų nekviesti.
- Po PR #301 galimo merge patikrinti, kad docs-only push praleidžiamas, o kodo push vis dar paleidžia site-check.

## AI agentų ir atminties patikra

- Būsena: **LAUKIA / stale** – `run_date=2026-11-21`, `agent_run.present=false`, status `missing`, `ai_calls=0`, `error_code=null`, `started_at=null`.
- Specialistai: analytics, topics, technical-seo ir content-review – visi `missing` (`specialist_report_missing`). Coordinator missing; Control Core `present=false`, status `missing`; recommendation_count=0.
- Memory: present, bet paskutinis atnaujinimas 2026-11-20T15:30:36.388Z, `last_status=needs_evidence`; šiandienos memory update nepatvirtintas.
- D1 diagnostikos šaltinis: #44904090148 / artifact #14707286726 (SELECT-only). Worker/D1 /health status Control Center artefakte success, heartbeat prieš 12 min.; atskiro schema-version lauko privatumo artefakte nėra.
- `recovery_confirmed=false`; issue #145 paliekamas open.

## Greičio ir patikimumo auditas – 2026-11-21

- **Daily-suite – PATIKRINTA:** manual fallback #44895862888 success: analytics 28 s (GA4/GSC fetch 10 s), live-check 21 s, topic-radar 11 s. Palyginamas ankstesnis schedule #44762160249: analytics 50 s (API fetch 29 s), live-check 17 s, topic-radar 10 s. Kadangi vienas schedule, kitas dispatch, greičio pagerėjimas neteigiamas; GA4 API laikas kinta.
- **Site-check – PATIKRINTA:** paskutinis main push #44897130923 16 s; PR #301 #44904330583 17 s; paskutinis schedule #44752353278 14 s.
- **ATLIKTA – PR #301:** [perf: skip site checks for documentation-only changes](https://github.com/Pershore/PetTraffic-AI/pull/301), viena workflow byla, 8 papildytos eilutės. Keturi docs-only push anksčiau sunaudojo 37 runner sekundes (17 + 16 + 0 + 4); PR prideda `paths-ignore` docs/reports/Markdown tik push ir PR įvykiams. CI success, PR ready for review, mergeable, nesujungtas. Tikėtinas po-merge docs-only runner laikas 0 s; po-merge elgsena dar nematuota.
- **Analytics / RSS – PATIKRINTA:** GA4 2026-11-14–20: 2 aktyvūs, 2 sesijos, 2 pageviews, 0 organinių sesijų; GSC 2026-11-12–18: 0 parodymų ir paspaudimų. Topic radar: 30 unikalių RSS nuorodų, 7 temos; tai nėra paieškų apimtys.
- **Saugumo ribos:** PR #301 neįdiegtas į main; jokio production, Worker/D1, ARO Vet, DNS, secrets, billing ar mokamo serviso pakeitimo nėra. Aktyvus darbo laikas NEMATUOTAS.

- Papildomas docs-only work-log commit `6aee359` po šio audito įrašo dar sukėlė site-check #44904512073 (22 s). Todėl iš viso jau 5 dokumentacijos-only push'ai sunaudojo 59 runner sekundes (55 s užbaigti job, 4 s atšauktas); PR #301 aprašymas atnaujintas šiuo papildomu realiu matavimu. Po-merge 0 s dar tik laukiamas, nepatvirtintas.

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
