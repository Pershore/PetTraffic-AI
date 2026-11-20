# Pet traffic – perdavimo ataskaita (2026-11-20)

## Naujausia patikrinta būsena (2026-11-20 12:11 LT)

- **Main / PR:** `main` HEAD `55bd6d207b7ef3abbb723e03305b4c295f98c766`; 7 atviri PR. #294 – draft, 4 ahead / 2 behind; #264 clean-URL canonical pataisa – draft, 1 ahead / 117 behind. Nė vienas nejungtas.
- **Schedule incidentas:** šiandienos Daily-suite `event=schedule` po 60 min. grace nerasta. Paskutinis tikras schedule #44557115983 (2026-11-19 15:38:40Z; `created_at=run_started_at`, baigėsi po 35 s); site-check schedule #44546115868 (14:39:25Z; `created_at=run_started_at`, baigėsi po 16 s). Vėlavimas įvyko iki GitHub run sukūrimo, ne runner eilėje. Tiksli scheduler priežastis nepatvirtinta.
- **Atsarginis Daily-suite – ATLIKTA:** saugus bridge #44716426141 success; Daily-suite #44716442982 `workflow_dispatch` success; `live-check`, `topic-radar`, `analytics` visi success. Live-check: 12 vidinių URL, sitemap, robots, 404 ir 20 senų URL 301. Topic radar: 29 unikalios Google News RSS nuorodos, 7 temos. Tai duomenų surinkimas, ne schedule įrodymas ir neatveria Worker AI vartų.
- **GA4 / GSC:** GA4 2026-11-13–19: 3 aktyvūs, 2 nauji naudotojai, 7 sesijos, 8 peržiūros, 0 patvirtintų organinių sesijų. GSC 2026-11-11–17: 0 parodymų, 0 paspaudimų; sitemap submitted/pending nuo 2026-11-10; 4 prioritetiniai URL nežinomi Google, vienas URL inspection baigėsi `ReadTimeout` (25 s). API statusas `available`.
- **D1 – PATIKRINTA:** sync #44716942089 (`workflow_dispatch`) patvirtino source run #44716442982, workflow ID 418322987, paruošė 2 privacy-filtered event ir abiem atliko D1 write/readback. Po Control Center #44716957805 sync #44717015938 ir SELECT-only diagnostika #44717051367 success. Artifact #14619109891: analytics_snapshot=1 ir topic_snapshot=1, abu iš run #44716442982; control_center_snapshot=7, recommendation_snapshot=7. Source event išlieka `workflow_dispatch`.
- **Worker AI – LAUKIA:** `/health` 10:00:13Z patvirtino Worker/D1 connected ir site HTTP 200. Paskutinis AI run – 2026-11-19 completed, 5 calls, `error_code=null`, Control Core `needs_evidence`, 4 spragos. 10:11Z diagnostika dar rodo 2026-11-20 agent_run missing, 0 calls ir specialist reports missing – iki 13:20 LT tai laukiama būsena. Manual fallback nėra tinkamas AI schedule evidence. Nekviesti AI rankiniu būdu.
- **Lighthouse / greitis:** paskutinis sėkmingas schedule #43915631789 (2026-11-16), 10 HTML/JSON ataskaitų. Palyginus su #43855151465, dog mobile LCP 2.00→9.78 s / TTFB 90→4 347 ms; vet desktop LCP 0.54→8.08 s / TTFB 35→2 564 ms; vet mobile LCP 1.85→5.55 s / TTFB 90→2 143 ms. TBT ir CLS=0, perdavimo dydžiai stabilūs. Kodo regresija neįrodyta.
- **SEO / URL neatitikimas:** Cloudflare Pages automatiškai nukreipia `.html` į extensionless URL ([Cloudflare docs](https://developers.cloudflare.com/pages/configuration/serving-pages/)), tačiau esami canonical ir sitemap dar `.html`. Tai sukuria nereikalingą redirect ir padidina LCP jautriuose puslapiuose. Esamas draft PR #264 siūlo clean URL canonical, bet 117 commitų atsilikęs; nejungti. Viešo URL/canonical pakeitimo be atskiro patvirtinimo nedaryti. About/privacy trūksta OG; homepage Twitter image nesutampa su OG.
- **Gyva svetainė:** homepage, 4 gidai, about, privacy, robots, sitemap ir 404 patikrinti; 404=404, robots/sitemap=200. Keturi gidai turi canonical, meta, OG, Article/BreadcrumbList JSON-LD ir H1. GA4 kodas aktyvuojamas tik po sutikimo. Favicon source egzistuoja ir yra susietas, bet SVG HTTP statuso atskirai patvirtinti nepavyko.
- **Cloudflare Pages deploy:** GitHub deployments API grąžino tuščią sąrašą, GitHub Pages API 404; gyvas puslapis pasiekiamas, Daily-suite live-check success, bet Cloudflare Pages deployment ID per GitHub neprieinamas. Jokio production pakeitimo nedaryta.

### Pirmas neužbaigtas veiksmas

13:20 LT patikrinti šiandienos Worker ciklą per `/health`; manual `workflow_dispatch` snapshot jo neatstoja. 14:00 LT esamas verifier patikrina tą patį ciklą. Jei po 13:20 nėra šiandienos run, žymėti STALE ir nekartoti. Issue #145 lieka open.

### Šios sesijos ribos

Jokių viešo turinio, canonical, sitemap, DNS, Cloudflare Pages/Worker/D1 production, secrets, paskyrų teisių, ARO Vet, billing ar mokamų paslaugų pakeitimų. `docs/SESSION_START.md` nekeitėme, nes sesijos protokolas nepasikeitė.

---

## Ankstesnė patikrinta būsena (2026-11-20 10:25 LT)

- **Main / PR būklė – PATIKRINTA:** main HEAD `afeea3106d4c52dac221a9c88406dc251ae1e36b`; atvirų PR buvo 6 prieš šią sesiją. Sukurtas atskiras draft PR [#294](https://github.com/Pershore/PetTraffic-AI/pull/294), head `1fb282e7a9b4f804ef880bfc5354cb3b34824cf3`, tik Worker turinio peržiūros įvesties ir testų pakeitimai.
- **Worker / D1 / AI – PATIKRINTA:** gyvas `/health` HTTP 200; D1 ir Control Core schema connected; heartbeat `2026-11-20T08:15:13.555Z`, site HTTP 200, database_ok=true. Paskutinis AI ciklas yra 2026-11-19: completed, 5 AI calls, `error_code=null`; Control Core `needs_evidence`, 4 spragos; memory `2026-11-19T15:45:21.548Z`.
- **2026-11-20 D1 diagnostika – PATIKRINTA:** [#44674851624](https://github.com/Pershore/PetTraffic-AI/actions/runs/44674851624), artifact #14602195843, success; 7 SELECT-only užklausos, visoms `rows_written=0`. Šiandienos `agent_run` missing, 0 AI calls, keturi specialistų raportai ir Control Core dar missing; tai tikėtina prieš 13:20 LT ciklą, ne ciklo gedimo įrodymas. Memory readback vis dar rodo 2026-11-19.
- **Specialistų turinio aprėpties priežastis – PATIKRINTA kode ir gyvuose puslapiuose:** dabartinis `getPublicContent` perduoda tik pirmus 900 simbolių kiekvieno straipsnio. Keturių gidų pagrindinio turinio ilgiai gyvai išmatuoti apie 4 524–7 634 simbolius; veterinarinių šaltinių nuorodos yra pabaigoje, todėl dabartinis agentas jų nemato.
- **PR #294 – PARUOŠTA, CI PATIKRINTA:** įvestis apribota `<main>`, išsaugoma įžanga, H1–H3 skyrių santrauka, išorinių šaltinių pavadinimai / domenai ir straipsnio pabaiga / disclaimer; kiekvienam puslapiui iki 1 150 simbolių, visi 4 įrašai telpa į esamą 6 000 simbolių įvesties ribą. Regresijos testai tikrina šaltinius, navigacijos triukšmo atmetimą ir bendrą biudžetą. [Site-check PR #44701819393](https://github.com/Pershore/PetTraffic-AI/actions/runs/44701819393) success; [Worker test + Cloudflare validation #44701819438](https://github.com/Pershore/PetTraffic-AI/actions/runs/44701819438) success; Worker production deploy ir snapshot sync PR įvykyje skipped. PR draft, nesujungtas; pilno teksto peržiūra neteigta.
- **Daily-suite / site-check schedule – NEĮVYKO 2026-11-20 patikros metu:** šiandienos `event=schedule` vykdymų nerasta. Daily-suite paskutinis schedule #44557115983 (`2026-11-19T15:38:40Z)); site-check paskutinis schedule #44546115868 (`2026-11-19T14:39:25Z`). Šiandienos push, PR ir workflow_run nėra schedule įrodymas.
- **Control Center / Issue #145 – PATIKRINTA:** [#44701833679](https://github.com/Pershore/PetTraffic-AI/actions/runs/44701833679), `workflow_run`, success; Issue #145 liko open ir atnaujintas su šiandienos Daily-suite schedule warning. AI recovery nepatvirtintas; issue neuždaryti.
- **Laukiantys etapai:** pagrindinis koordinatorius numatytas 11:45 LT (Daily-suite catch-up / D1 sync); vienintelis Worker AI ciklas – 13:20 LT; esamas greičio / post-cycle verifier – 14:00 LT. Iki jų nekartoti Daily-suite ar AI ciklo rankiniu būdu; po 13:20 tikrinti to paties `run_date` 5 kvietimus, specialistų įrodymus, Control Core, D1 memory ir readback.
- **Saugumas:** nebuvo keista Worker/D1 produkcija, DNS, secrets, Cloudflare teisės, ARO Vet, viešas turinys, billing ar mokamos paslaugos. Dashboard lieka READ-ONLY. Aktyvus darbo laikas NEMATUOTAS.

## Sesijos išvada

**D1 diagnostikos grandinė PATIKRINTA ir pataisa sujungta.** Ankstesnė Worker/D1 diagnostika buvo paleidžiama tiesiai po Control Center ir galėjo perskaityti senesnį D1 snapshot. Naujas workflow trigeris laukia sėkmingo snapshot sync, o tai patvirtinta dviem gyvais vykdymais.

## Pakeitimas

- PR #290 buvo 15 commitų atsilikęs nuo main; jo nejungėme.
- Sukurtas naujas PR #293 nuo tuo metu naujausio main, pakeisti tik workflow trigeris ir regresijos testas.
- PR #293 sujungtas squash į main: `00402eafc94a26a66b5c5bee71f1b18d6f80f55c`.
- Senas PR #290 uždarytas kaip superseded; komentaras išsaugo paaiškinimą.

## CI įrodymai

- Worker diagnostic testai: 11/11 OK.
- Cloudflare resource validation: success; Worker deploy: skipped.
- Snapshot sync PR test: success; real sync PR event metu skipped.
- Site-check PR #930: success.
- Po merge site-check #931: success.
- Post-merge Worker diagnostics #44: success; 11/11 testai, SELECT-only D1 užklausos, rows_written=0.

## Gyvos grandinės įrodymai

| Etapas | Run | Rezultatas |
|---|---:|---|
| Control Center | #44674550008 | success |
| D1 snapshot sync | #44674604295 | success; 2 write/readback |
| Post-sync diagnostika | #44674631557 | success; event=workflow_run; 11 s |
| Control Center | #44674590442 | success |
| D1 snapshot sync | #44674641788 | success; 2 write/readback |
| Post-sync diagnostika | #44674688061 | success; event=workflow_run; 11 s |

Diagnostikos artefaktas #14601127810 patvirtino Control Center source run ID #44674550008. Artefaktas #14601302134 patvirtino naujausią Control Center source run ID #44674590442. Abiem atvejais diagnostika vyko po sinchronizacijos, ne prieš ją.

## Worker / D1 / AI būsena

- Gyvas `/health`: `ok=true`, D1 connected, Control Core schema connected.
- Heartbeat: site HTTP 200, database healthy.
- Paskutinis AI ciklas: `run_date=2026-11-19`, `completed`, 5 AI calls, `error_code=null`.
- Control Core: `needs_evidence`, 4 evidence gaps.
- Memory readback: `2026-11-19T15:45:21.548Z`, tas pats ciklas.
- 2026-11-20 06:30 LT diagnostika teisingai rodo šiandienos agent run kaip missing, nes šiandienos 13:20 LT ciklas dar neįvyko. Tai nėra klaida ar įrodymas, kad ciklas sugedo.
- Issue #145 lieka open; `recovery_confirmed=false` iki įrodymų kokybės atsistatymo.

## Toliau

1. Po 2026-11-20 13:20 LT tikrinti vienintelį dienos AI ciklą: 5 kvietimus, error_code, visų 4 specialistų rezultatus ir įrodymus.
2. Po D1 sync patikrinti automatinį diagnostikos artefaktą: tas pats run_date, specialistų ataskaitos, Control Core ir memory readback.
3. Issue #145 neuždaryti, kol `recovery_confirmed=true` ir specialistų įrodymai pakankami.
4. Atskirai tęsti Google Search Console sitemap / indeksavimo stebėseną ir GitHub schedule vėlavimų analizę. Push / workflow_run nepainioti su schedule.

## Saugumo ribos

Diagnostika tik SELECT; 7 užklausose `rows_written=0`. Snapshot sync vykdė tik esamą privatumo filtruotų įvykių kelią per trumpalaikį OIDC, 2 įvykiams patvirtintas D1 write/readback. Worker produkcinis deploy, D1 schema, DNS, Cloudflare paskyros nustatymai, secrets, ARO Vet, viešas turinys, billing ir mokamos paslaugos nekeisti.

Aktyvus darbo laikas NEMATUOTAS. Įrankių laiko žymos: 06:22–06:30 LT.
