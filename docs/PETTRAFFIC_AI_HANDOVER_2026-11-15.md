# Pet traffic – 2026-11-15 ryto tęstinumo ataskaita

**Audito laikas:** 2026-11-15 08:26 Europe/Vilnius (06:26 UTC)  
**Saugykla:** `Pershore/PetTraffic-AI`  
**Svetainė:** https://pettraffic-ai.pages.dev/

## Patvirtinta

- GitHub jungtis veikia; saugyklos default branch yra `main`, turimos admin / maintain / push / pull teisės.
- Audito metu naujausias main commit: `7ae8d1370b679b47816820797f3f0ea97f41a450`.
- PR #131 „Prevent Worker redeploys on workflow-only edits“ yra sujungtas (merge commit `046a5747bc1e0d6c078e96575a70d25fa9582440`).
- Atvirų PR nerasta.
- Naujausias automatinis projekto būsenos snapshot: `automation-history/reports/history/project-state/latest.md`, sugeneruotas 2026-11-14 23:08 UTC. Jis patvirtina PR #208 ir #209 sujungimą, Worker deploy #96 sėkmę, D1 / control-core ryšį ir po-merge workflow patikras.
- Daily-suite workflow faile yra tiesioginis cron `10 6 * * *` UTC. Jo job'ai atskirai vykdo GA4/GSC, temų radarą ir gyvos svetainės patikrą.
- Worker agentų grafikas yra `20 7,8 * * *` UTC su Europe/Vilnius 10:20 laiko vartais; heartbeat – kas 15 minučių.
- Control Center cron yra 08:40 UTC (10:40 LT). Vienintelis ChatGPT priežiūros koordinatorius suplanuotas 11:00 LT.

## Laukiančios patikros

1. **Daily-suite schedule:** 08:26 LT (06:26 UTC) naujausių 100 GitHub Actions vykdymų sąraše dar nebuvo naujo paleidimo po 2026-11-14 23:08 UTC. Šios dienos 06:10 UTC `event=schedule` vykdymas nepatvirtintas. Cron gali vėluoti; rankinis paleidimas nėra schedule įrodymas. Nežymėti kaip galutinio gedimo be papildomų įrodymų.
2. **Worker AI agentai:** šiandienos 10:20 LT ciklas dar neįvyko. Ankstesnė klaida lieka istorine iki naujo ciklo; po jo būtina patikrinti agentų ataskaitą ir D1 atminties išsaugojimą.
3. **Control Center:** po daily-suite ir Worker ciklo tikrinti 10:40 LT ataskaitą, issue #145 būseną ir naują projekto snapshot.
4. **GA4 / GSC:** tikrinti daily-suite artefaktus; jei GA4 vėl nepasiekiamas, išsaugoti atskirai gautą GSC rezultatą ir nelaikyti timeout nuliu.
5. **Termux / Codex:** ankstesnė vartotojo išvestis patvirtino lokalią parengtį, bet ChatGPT neturi tiesioginės Android shell prieigos. Nepradėti dubliuojančio bootstrap be naujos priežasties.

## Saugumo ir biudžeto ribos

- 0 €/mėn. papildomų išlaidų; Firecrawl nemokamos kvotos perspėjimas nurodė 80 % iš 1 000 kreditų panaudojimą – vengti nebūtinų scrape/search užklausų.
- Cloudflare tokeno rotacija ir GitHub secret atnaujinimas anksčiau vartotojo patvirtinti ir CI patikra sėkminga; raktų pokalbyje neprašyti.
- Worker/D1 production, DNS, secrets, ARO Vet ir viešas svetainės turinys šio audito metu nekeisti.
- Automatinis turinio publikavimas ir `/v1/tasks*` savavališkas užduočių vykdymas lieka išjungti.
- Issue #145 palikti atvirą, kol naujas AI ciklas ir atminties išsaugojimas nepatvirtins atsistatymo.

## Kitas konkretus etapas

Sulaukti suplanuotų vykdymų: daily-suite 08:10 LT, Worker AI 10:20 LT, Control Center 10:40 LT, ChatGPT koordinatorius 11:00 LT. Vertinti tik realius `event=schedule` vykdymus, jobs, artefaktus ir D1 įrodymus. Jokio rankinio paleidimo, kuris užmaskuotų cron būseną.


## 2026-11-15 08:43 LT – tęstinė patikra

- PR #210 jau sujungtas į `main` (`0ac4f3e9be21d52df3a4d681e23b21c3a7b744a4`); Cloudflare Pages, shell-validation ir static website / automation testai sėkmingi. Po merge site-check, Termux bridge ir work-log workflow sėkmingi.
- Worker `/health` grąžina HTTP 200, D1 ir control-core schema connected, heartbeat `2026-11-15T06:30:47.076Z`, svetainės HTTP 200.
- AI agentų ciklas dar neatsistatęs: paskutinis įrašas 2026-11-14 `failed`, 4 AI calls, klaida `model_content-review_model_output_invalid_json`. Control Core: `needs_evidence`, 4 evidence gaps, memory present, 0 recommendations. Naujas ciklas laukiamas 10:20 LT.
- Daily-suite 08:10 LT cron vykdymo 08:43 LT dar nėra naujausių 100 Actions sąraše; priežastis nenustatyta. Grafiko nekeisti be priežasties; rankinis paleidimas nėra schedule įrodymas.
- Issue #145 lieka open iki naujo sėkmingo agentų ciklo ir D1 atminties įrašo patvirtinimo.
- Projekto būsenos snapshot atnaujintas `automation-history` šakoje, commit `aea2e6d85ca159d44a78f6f418397ac748aa4d92`.


## 2026-11-15 10:41 LT – naujausia patikra

- Daily-suite workflow metadata: active (ID 418322987), tačiau 06:10 UTC suplanuoto event=schedule vykdymo nėra; 60 min. grace jau praėjęs. Paskutinis failo pakeitimas buvo prieš numatytą ciklą. Priežastis nepatvirtinta.
- Control Center workflow metadata: active (ID 416336983). 08:40 UTC ciklas 10:41 LT dar nematomas; grace galioja iki 11:40 LT.
- Worker /health HTTP 200, D1 ir Control Core schema connected. 10:20 LT AI agentų ciklas completed, 5 kvietimai, klaidos nėra. Atmintis present, 2 rekomendacijos, 8 evidence gaps; statusas needs_evidence.
- Issue #145 paliekamas atviras iki Control Center recovery_confirmed=true. GA4/GSC naujos ataskaitos nėra, kol daily-suite nepasileido.
- Jokių produkcinių, DNS, secrets, ARO Vet ar viešo turinio pakeitimų. Papildomų paslaugų / išlaidų nėra.

## Kitas veiksmas

Iki 11:40 LT patikrinti Control Center schedule įvykį ir jo ataskaitą. Jei jo nėra, atskirai užregistruoti praleistą aktyvaus workflow schedule ir perduoti kaip GitHub Actions scheduler / administravimo prieigos blokatorių. Daily-suite priežastį tirti tik gavus papildomą GitHub workflow vykdymo / scheduler įrodymą.


## 2026-11-15 10:47 LT – gyvos būklės ir schedule pakartotinė patikra

- Vieša pradžia `https://pettraffic-ai.pages.dev/` grąžina HTTP 200; pagrindinis turinys yra lietuviškas „Pet traffic“, matomi keturi pagrindiniai gidai.
- Gyvas Worker `/health` grąžina HTTP 200; D1 ir Control Core schema connected. Heartbeat `2026-11-15T08:45:46.913Z` (10:45:46 LT), site HTTP 200, DB OK.
- 2026-11-15 AI agentų ciklas `completed`, 5 AI calls, `error_code=null`. Control Core vis dar `needs_evidence`: 2 rekomendacijos, 8 evidence gaps, memory present; tai nėra pilnas įrodymų patvirtinimas.
- GitHub Actions paskutinių 100 vykdymų `event=schedule` sąraše yra 4 įrašai, naujausias Control Center 2026-11-14 15:18:42 UTC. 2026-11-15 `daily-suite` 08:10 LT schedule vykdymo nėra; 60 min. grace praėjęs. `control-center` 10:40 LT schedule vykdymo 10:47 LT dar nėra; jo grace galioja iki 11:40 LT. Abu workflow metaduomenys 10:41 LT buvo `active`; tiksli scheduler priežastis nepatvirtinta.
- Naujausias `Pet traffic site checks` run `43695815389` (push) – success. PR #212 patikra `43695723083` – success, 103 Python testai `OK`. PR #212 paliktas open, automatinis merge neatliktas.
- Issue #145 atnaujintas komentaru `6891910501`; paliktas open, nes schedule ir Control Core evidence problemos neišspręstos.
- ChatGPT pagrindinė priežiūros automatizacija enabled, kitas paleidimas 11:00 LT. Greičio priežiūros automatizacija enabled, pirmas paleidimas laukiamas 2026-11-16 09:00 LT. ARO Vet analitikos automatizacija enabled, kitas paleidimas 2026-11-15 18:24 LT. Penkios senesnės automatikos paused; dublikatų neįjungti.
- Firecrawl kredito likutis prieš dvi gyvas patikras: 197/1 000; šios patikros panaudojo 2 kreditus. Jokie kodo, Worker/D1, DNS, secrets, ARO Vet, viešo turinio ar mokami pakeitimai neatlikti.

**Kitas veiksmas:** po 11:40 LT patikrinti Control Center tikrą schedule įvykį; jei jo nėra, užregistruoti antrą praleistą aktyvaus workflow schedule. Daily-suite priežastis perduota kaip GitHub Actions scheduler / nustatymų prieigos blokatorius.

## 2026-11-15 10:50 LT – visų viešų puslapių gyvas HTTP testas

- Patikrinta 8 viešų URL: `about.html`, `privacy.html`, keturi pagrindiniai straipsniai, `robots.txt`, `sitemap.xml`. Visi atsakė HTTP 200.
- HTML puslapių content-type `text/html; charset=utf-8`; robots `text/plain; charset=utf-8`; sitemap `application/xml`.
- Kartu su 10:47 LT patikrinta pradžia ir Worker `/health`, viešos svetainės pasiekiamumas patvirtintas. Tai nepatvirtina Google indeksavimo ar naujų GA4/GSC duomenų.
- Firecrawl kredito balansas po patikros: 197/1 000. Jokie svetainės ar produkcijos pakeitimai neatlikti.


## 2026-11-15 – workflow dispatch tiltas, daily-suite atkūrimas ir D1 sinchronizavimas

- PR #213 sujungtas. Komentaras /pettraffic-run-daily-suite iš savininko Pershore sukėlė helper run 43696946923 (success), kuris paleido daily-suite run 43696960921 (event=workflow_dispatch, success). Visi trys darbai – analytics, topic-radar, live-check – success.
- Analytics ir topic-radar artefaktai išsaugoti automation-history šakoje. GA4 2026-11-08–14: 7 aktyvūs naudotojai, 19 sesijų, 73 peržiūros, 0 patvirtintų organinių sesijų. GSC 2026-11-06–12: 0 parodymų, 0 paspaudimų; sitemap pending; 5 svarbūs URL nežinomi Google. Topic radar: 28 unikalios antraščių nuorodos iš 7 temų.
- Daily-suite run neįjungė naujo workflow_run sync / Control Center paleidimo; D1 snapshot write/readback iš šio rankinio run dar nepatvirtintas.
- PR #214 praplečia owner-only tiltą: /pettraffic-run-daily-suite, /pettraffic-sync-latest, /pettraffic-run-control-center. Komandos tik iš Pershore, tik nauji komentarai issue #145, tik fiksuoti workflow veiksmai.
- PR #214 sync workflow priima source_run_id tik patikrinęs workflow ID 418322987, main branch, source event, completed status ir bent vieną sėkmingą analytics/topic-radar job; D1 įrašymas vyksta per GitHub OIDC su readback.
- Pagrindinis kasdienis koordinatorius perplanuotas į 11:45 Europe/Vilnius, po Control Center 60 min. grace (11:40 LT). Naujos automatizacijos nesukurtos.
- PR #214 CI ir realus D1 sync / Control Center fallback dar laukia. Tikras event=schedule trūkumas lieka atskiras blokatorius; workflow_dispatch nėra cron įrodymas.


## 2026-11-15 – PR #214 D1 ir Control Center fallback

- PR #214 išplečia saugų issue #145 tiltą trimis fiksuotomis komandomis: /pettraffic-run-daily-suite, /pettraffic-sync-latest, /pettraffic-run-control-center. Guard leidžia tik Pershore paskyros naują komentarą, tik issue #145; PR komentarai ir kiti veiksmai atmetami.
- sync-control-api.yml gauna workflow_dispatch source_run_id. Prieš atsisiųsdamas artefaktus patikrina daily-suite workflow ID 418322987, main šaką, event schedule/workflow_dispatch, completed status ir bent vieną sėkmingą analytics/topic-radar job. D1 įrašai lieka agreguoti, autentifikacija per trumpalaikį OIDC, po įrašymo daromas readback.
- Control Center workflow jau turėjo workflow_dispatch, todėl bridge gali jį paleisti po 11:40 LT grace, tačiau tai bus manual run, ne schedule įrodymas.
- Po PR #214 merge: paleisti sync-latest ir patikrinti D1 write/readback; paleisti Control Center ir patikrinti ataskaitą/issue #145. PR CI ir realus D1 sync dar laukia.


## 2026-11-15 – Worker OIDC sync pataisa (PR #216)

- Daily-suite catch-up run 43696960921 baigėsi success ir išsaugojo GA4/GSC bei topic radar artefaktus.
- D1 sync workflow_dispatch run 43697692423 gavo HTTP 401. Patikrinus Worker kodą nustatyta tiksli priežastis: OIDC verifier leido tik event_name=workflow_run.
- Įprastas workflow_run sync iš Control Center run 43697658367 sėkmingai įrašė 2 įvykius ir patvirtino D1 readback; tai nėra daily-suite sync įrodymas.
- PR #216 leidžia papildomą event_name=workflow_dispatch tik jei workflow_ref lieka tiksliai sync-control-api.yml@refs/heads/main ir visi immutable repo ID, ref, audience, parašas bei exp patikrinimai praeina. Push, schedule, issue_comment ir kiti eventai lieka atmetami.
- Worker testai papildyti priėmimo ir atmetimo atvejais. PR CI ir realus deploy / D1 retry dar laukia. Jokių naujų secrets ar platesnių Worker API teisių nėra.


## 2026-11-15 – Worker AI ciklo grafiko korekcija

- D1 analytics/topic snapshots write/readback patvirtinti run 43698010982; Control Center/recommendation snapshots write/readback patvirtinti run 43698006099.
- 10:20 LT Worker AI ciklas buvo completed prieš duomenų sinchronizavimą, todėl šiandienos 8 evidence gaps dar neįvertino naujų snapshot'ų.
- PR #217 perkelia Worker AI ciklą į 13:20 Europe/Vilnius (UTC cron 10:20/11:20 pagal vasaros/žiemos laiką), po 11:45 LT koordinatoriaus. Šiandienos run_date jau užregistruotas, todėl naujas ciklas šiandien nesikartos; kitas pilnas ciklas laukiamas 2026-11-16 13:20 LT.
- PR #217 CI ir post-deploy patikra dar laukia.


## 2026-11-15 11:18 LT – automatizacijų grafiko užbaigimas

- Pagrindinis catch-up koordinatorius: 11:45 LT. Esamas greičio stebėjimo automation papildytas Worker AI post-cycle patikra ir perkeltas į 14:00 LT. ARO Vet analitikos automation lieka 18:24 LT.
- Nauja automatizacija nesukurta, nes pasiektas 3 aktyvių užduočių plano limitas; panaudota esama greičio automatizacija, išsaugant jos greičio audito funkciją.
- 14:00 patikra tikrina 13:20 Worker AI ciklo rezultatą per Control Center ataskaitą; ji nenaudoja išjungto /v1/tasks API ir negali priverstinai vykdyti Worker AI.


## 2026-11-15 11:49 LT – Lighthouse, Worker diagnostika ir AI agentų patikimumas

- **PR #218 – PATIKRINTA:** pridėta savininko komanda `/pettraffic-run-lighthouse` per issue #145. PR testai: 109/109 PASS; PR sujungtas commit `82606323383e418ad0094eb68d0bb7801604ef60`. Rankinis Lighthouse run [#43699958471](https://github.com/Pershore/PetTraffic-AI/actions/runs/43699958471) baigtas success; gauta 10 HTML/JSON ataskaitų. Desktop Performance 100 visuose 5 puslapiuose; mobile: homepage 95, skubios pagalbos katė 98, kiti 3 puslapiai 99. Accessibility, Best Practices ir SEO – 100 visuose 10 bandymų. Homepage mobile pagrindinė smulki problema: TBT 270 ms, render-blocking resursų prognozuojamas sutaupymas ~140 ms. Tai nėra kritinis blokatorius.
- **PR #219 – PATIKRINTA:** pridėta privatumo požiūriu saugi Worker `/health` diagnostika – specialistų būsenos ir tik kategorijų skaitikliai, neatskleidžiant modelio teksto. Tame pačiame PR pataisytas senas Cloudflare cron validavimo lūkestis `20 7,8` į faktinį `20 10,11` UTC. PR sujungtas commit `8a76ff84850a12fca06e63cad6359119580bb9ed`; Worker deploy [#43700250573](https://github.com/Pershore/PetTraffic-AI/actions/runs/43700250573) – success, D1 /health ir 401 autentifikavimo riba patikrinti.
- **PR #220 – ATLIKTA / deploy PATIKRINTAS:** AI agentų statusai normalizuojami į `reviewed` arba `needs_evidence`; `error`, `no data`, `monitor` ir kitos reikšmės nebegali būti klaidingai interpretuojamos kaip sėkminga peržiūra. Išvestis apribota iki vieno trumpo įrašo kiekviename masyve, 120 simbolių, kad sumažėtų nukirsto JSON rizika. PR CI ir Cloudflare validacija success; sujungtas commit `217f8ad82abe4e724792a494c1a3cece334fbc29`; Worker deploy [#43700775930](https://github.com/Pershore/PetTraffic-AI/actions/runs/43700775930) – success. Gyvas /health po deploy HTTP 200, D1 connected, schema connected, heartbeat site HTTP 200.
- **AI agentų tikro veikimo rezultatas dar LAUKIA:** viešas /health vis dar rodo 2026-11-15 ankstesnį ciklą: completed, 5 AI calls, 2 rekomendacijos, 8 evidence gaps, memory present. Specialistų būsenos: analytics=`error`, topics=`no data`, technical-seo=`monitor`, content-review=`invalid_json`; kategorijos: model_output=2, insufficient_evidence=1, other=5. PR #220 pataisa dar neturėjo naujo realaus AI ciklo; kitas dėl daily run idempotency numatytas 2026-11-16 13:20 LT. Iki tol nežymėti 8 spragų kaip išspręstų.
- **Daily-suite / Control Center cron – NEPATVIRTINTA:** 2026-11-15 `event=schedule` paleidimų nėra po 60 min. grace. Savininko catch-up daily-suite [#43696960921](https://github.com/Pershore/PetTraffic-AI/actions/runs/43696960921) success, visi 3 darbai success; D1 sync [#43700319655](https://github.com/Pershore/PetTraffic-AI/actions/runs/43700319655) success; Control Center [#43700841420](https://github.com/Pershore/PetTraffic-AI/actions/runs/43700841420) success, bet teisingai rodo schedule warning. Rankiniai vykdymai nėra cron įrodymas. GitHub Actions repository settings endpoint per dabartinę integraciją neprieinamas; priežastis nepatvirtinta, nustatymai nebuvo keisti.
- **Svetainė – PATIKRINTA:** gyvai peržiūrėtas homepage, 4 pagrindiniai gidai, about, privacy, robots.txt, sitemap.xml ir 404 puslapis. Viešas prekės ženklas išlieka „Pet traffic“; ARO Vet ir AI žymens į svetainę negrąžinta. Site-check [#43700775967](https://github.com/Pershore/PetTraffic-AI/actions/runs/43700775967) success.
- Pagrindinė kasdienė priežiūros automatizacija atnaujinta: pridėta Lighthouse pirmadienio schedule patikra ir saugus /pettraffic-run-lighthouse atsarginis veiksmas, jei per 7 dienas nėra sėkmingo audito; ji lieka enabled. Jokios naujos automatikos nesukurta.
- Jokio papildomo mokamo plano, API, ARO Vet pakeitimo, DNS / secret keitimo ar svetainės turinio publikavimo neatlikta.

**Kitas konkretus etapas:** (1) užbaigti Worker cron diagnostikos run `43700250618` ir patvirtinti 15 min. heartbeat invokaciją; (2) 2026-11-16 13:20 LT patikrinti naują AI ciklą, statusų normalizavimą, JSON validumą ir D1 memory; (3) atskirai tęsti GitHub `event=schedule` problemos diagnozę, nekeisti repository settings be prieigos / leidimo.


## 2026-11-15 12:20 LT – Worker cron ir AI ciklo monitoringo patikslinimas

- Gyvas Worker `/health` patikrinimas 12:05 LT grąžino HTTP 200, D1 ir Control Core schema connected. Paskutinis `system_heartbeats.checked_at` buvo `2026-11-15T10:00:13.641Z` (12:00:13 LT), `site_ok=true`, HTTP 200, `database_ok=true`. Tai patvirtina, kad 15 min. Worker heartbeat cron įvyko po ankstesnio 17 min. stebėjimo lango.
- Worker cron diagnostikos run [#43700250618](https://github.com/Pershore/PetTraffic-AI/actions/runs/43700250618) nesėkmė (`0 structured invocations`) nėra įrodymas, kad cron neveikė: Wrangler tail stebėjo žurnalų įrašus, o scheduled handler neturėjo garantuoto `console` įrašo. PR #223 keičia patikrą į patikimą D1 heartbeat laiko palyginimą prieš ir po 15 min. intervalo; Cloudflare tokenas paliekamas tik atskiram schedules API žingsniui.
- Aptikta Control Center laiko neatitiktis: Worker AI ciklas nuo PR #217 numatytas 13:20 LT, bet `agent/control_center.py` dar naudojo 10:40 LT ribą. PR #223 sulygina tikrinimo ribą su 13:20 LT ir pagal `started_at` atskiria ankstesnį tos pačios dienos ciklą nuo naujo suplanuoto ciklo. Iki 13:20 būsena bus WAITING; po 13:20 trūkstant naujo ciklo – STALE; naujas ciklas tikrinamas pagal Control Core atmintį ir įrodymų spragas.
- Daily-suite catch-up [#43696960921](https://github.com/Pershore/PetTraffic-AI/actions/runs/43696960921) yra `workflow_dispatch`, visi 3 job success. D1 sync [#43698010982](https://github.com/Pershore/PetTraffic-AI/actions/runs/43698010982) patvirtino source run #43696960921, analytics/topic artefaktų atsisiuntimą, OIDC ir du `D1 snapshot write/read verified` įrašus.
- Control Center run [#43700841420](https://github.com/Pershore/PetTraffic-AI/actions/runs/43700841420) success, artefaktas [#14156700932](https://github.com/Pershore/PetTraffic-AI/actions/runs/43700841420) rodo trūkstamą 2026-11-15 schedule; jis buvo sėkmingas vykdymas po 11:40 LT grace, todėl papildomas Control Center dispatch nekartotas. Daily-suite ir Control Center `event=schedule` 2026-11-15 sąraše nėra; priežastis nepatvirtinta, repo nustatymai nekeisti.
- Dabartinis AI įrašas tebėra 2026-11-15 08:20 UTC senasis ciklas: completed, 5 AI calls, 2 rekomendacijos, 8 evidence gaps; PR #220 pataisos veikimas dar laukia kito pilno ciklo 2026-11-16 13:20 LT.
- PR #223 [atidarytas](https://github.com/Pershore/PetTraffic-AI/pull/223). Pradiniai CI run #43703063670 (site checks) ir #43703063657 (Control Center) – success; site checks įvykdė validate_site.py, compileall, 22 agent testus ir 120 testų tests/ rinkinyje. Po šio dokumentų papildymo privaloma patikrinti naujausius PR checks dar kartą; nesujungti, kol visi baigti ir success.
- Kiti veiksmai: patikrinti naujausius PR #223 check'us; po merge stebėti naują heartbeat diagnostiką; 2026-11-16 13:20 LT patikrinti naują AI ciklą ir D1 atmintį. 0 €/mėn. riba išlaikyta; ARO Vet, DNS, secrets, Worker production kodas/konfigūracija ir viešas turinys nekeisti.

## 2026-11-15 – galutinė tęstinė patikra po PR #223

- PR #223 sujungtas į main commit `e923a69458cf941fe3aaa3579205b5fb4c242530`; atvirų PR nėra.
- Po merge site-check #43703360121 – success; PR #223 site-check, Control Center ir Cloudflare Pages patikros taip pat success.
- Worker cron diagnostika [#43703245674](https://github.com/Pershore/PetTraffic-AI/actions/runs/43703245674) – **PATIKRINTA / success**. Cloudflare schedules API grąžino abu laukiamus cron: `*/15 * * * *` ir `20 10,11 * * *` UTC. D1 heartbeat pažengė nuo 2026-11-15T10:15:13.515Z iki 10:20:24.067Z; D1, Control Core schema, svetainė HTTP 200 ir DB OK.
- Daily-suite [#43696960921](https://github.com/Pershore/PetTraffic-AI/actions/runs/43696960921) yra `workflow_dispatch`, ne schedule; analytics, topic-radar ir live-check visi success. GA4/GSC artefaktas: 2026-11-08–14 – 7 aktyvūs naudotojai, 19 sesijų, 73 peržiūros, 0 organinių sesijų; GSC 0 parodymų / 0 paspaudimų, sitemap pending, 5 prioritetiniai URL Google nežinomi. Topic radar: 28 unikalios nuorodos iš 7 temų.
- D1 snapshot sync [#43698010982](https://github.com/Pershore/PetTraffic-AI/actions/runs/43698010982) – anksčiau patvirtintas analytics/topic snapshot write + readback; Control Center/recommendation snapshot write + readback [#43698006099](https://github.com/Pershore/PetTraffic-AI/actions/runs/43698006099).
- GitHub workflow metadata: daily-suite ID 418322987 ir Control Center ID 416336983 abu `active`. Tikrų schedule įvykių užklausa: daily-suite 2026-11-15 = 0; Control Center = tik vienas senas 2026-11-14T15:18:42Z; site-check = du seni įvykiai 2026-11-13 ir 2026-11-14. Todėl 2026-11-15 daily-suite ir Control Center schedule **neįvyko**. Repository Actions permissions endpoint grąžino 401 per turimą jungtį; nustatymų pakeisti / patikrinti nepavyko. Priežastis lieka NEPATVIRTINTA, nevadinti workflow išjungtais – jų metadata state=active.
- Gyvas Worker /health HTTP 200, D1 ir Control Core schema connected, heartbeat site 200. Paskutinis AI ciklas vis dar 2026-11-15T08:20:13Z, completed, 5 kvietimai, error_code=null. Tačiau šis ciklas įvyko iki PR #220 Worker deploy; specialistų būsenos atspindi seną ciklą (analytics error, topics no data, technical-seo monitor, content-review invalid_json), Control Core needs_evidence, 2 rekomendacijos, 8 spragos, memory present. PR #220 deploy patvirtintas, bet naujos normalizavimo pataisos realus ciklo veikimas ir D1 atminties atnaujinimas dar **LAUKIA**; dėl vieno ciklo per dieną idempotency kitas pilnas ciklas numatytas 2026-11-16 13:20 LT.
- Issue #145 paliktas open: cron schedule trūkumas ir naujo post-fix AI ciklo įrodymų nebuvimas neleidžia patvirtinti visiško atsistatymo.
- Saugumo ribos išlaikytos: jokio ARO Vet, DNS, Worker production konfigūracijos, D1 schemos, secrets, viešo turinio publikavimo ar mokamų paslaugų pakeitimo. Termux/Codex CI tiltas patikrintas, bet tiesioginės ChatGPT Android shell prieigos nėra; tai nėra debesų automatizacijų veikimo sąlyga.


## 2026-11-15 – GitHub Actions policy patikra pagal vartotojo ekrano kopiją

- Vartotojo pateiktoje `Settings → Actions → General` ekrano kopijoje pasirinkta **Allow all actions and reusable workflows**. Tai patvirtina, kad Actions leidimų politika neuždraudžia workflow veiksmų; šio nustatymo keisti nereikia.
- Ekrano kopijoje **Workflow permissions** skiltis nematoma, todėl numatytųjų `GITHUB_TOKEN` teisių reikšmė nepatvirtinta. Ankstesnis 401 per GitHub integraciją lieka galiojantis apribojimas skaityti repo Actions administravimo nustatymus.
- `daily-suite.yml`, `control-center.yml` ir `site-check.yml` patikrinti tiesiogiai `main` šakoje: cron įrašai yra, `workflow_dispatch` yra. `control-center.yml` turi aiškias job teises (`contents: write`, `actions: read`, `issues: write`); tai nepakeičia patikros dėl GitHub schedule įvykių.
- Išvada: Actions policy apribojimas atmestas kaip tikėtina priežastis; suplanuotų paleidimų dingimo priežastis **dar nenustatyta**. Jokių nustatymų ar produkcinių sistemų nekeista.

## 2026-11-15 – gyvo Control Center dashboard kūrimas

- Sukurtas atskiras puslapis `site/control/index.html` su atskiru CSS/JS, architektūros žemėlapiu, GitHub workflow kortelėmis, run istorija, GA4/GSC agregatais, Lighthouse nuorodomis, įrankių ir prieigų inventoriumi.
- Gyvi šaltiniai: GitHub REST, Worker `/health`, viešos svetainės HEAD, `automation-history` analytics/topic agregatai. Atnaujinimas kas 5 min.; GitHub REST užklausų skaičius sumažintas, istorijos archyvai cache'inami.
- Viešas dashboard `noindex,nofollow`, neįtraukiamas į sitemap ir neturi canonical. Svarbu: noindex nėra prieigos kontrolė; puslapis viešas, todėl rodomi tik agreguoti / vieši duomenys.
- Puslapis yra read-only: jokių workflow dispatch, API POST, secrets ar production pakeitimų. Worker `/v1/tasks*` lieka išjungtas. ChatGPT automatikų būsena ir Termux shell nėra tiesiogiai skaitomi.
- Sukurtas regresijos testas dashboard privatumo / noindex / read-only riboms; site-check papildomas `node --check` JS sintaksei. CI rezultatas dar laukiamas.
- Šaka `feature/live-control-dashboard`; production nepublikuota iki PR patikrų ir atskiro merge.


## 2026-11-15 15:32 LT – Control Center dashboard CI ir preview patvirtinti

- PR #225 atviras / mergeable / nesujungtas; paskutinis branch commit `44245f22335e963c8e6180b6d870c0f0799fec07`.
- Cloudflare Pages preview check – success; branch preview `https://feature-live-control-dashboa.pettraffic-ai.pages.dev/control/` atveria dashboard. Peržiūros turinyje patvirtintos architektūra, agentų/atminties panelė, atvirų PR sąrašas ir pagrindinių viešų puslapių katalogas.
- Site-check [#43719527898](https://github.com/Pershore/PetTraffic-AI/actions/runs/43719527898) – success. Node `--check`, `agent/validate_site.py`, `compileall`, agent testų žingsnis ir 124 testai iš `tests/` – success.
- Dashboard: GitHub run/PR/commit/issue, Worker /health, viešos svetainės HEAD, GA4/GSC agregatai, RSS archyvas, Lighthouse paskutinio sėkmingo run nuoroda; 14 workflow kortelių, įrankių inventorius, 5 specialistų būsenos, D1/Control Core atminties duomenys ir atvirų PR sąrašas.
- Atnaujinimas kas 5 min.; GitHub API užklausos ribojamos, archyvai cache 30 min. Nepasiekiami duomenys žymimi kaip nežinomi. Dashboard read-only; jokių POST/dispatch, PR merge ar production pakeitimų.
- Branch preview origin nepatenka į Worker CORS allowlist, todėl preview režime Worker skiltis aiškiai rodo CORS apribojimą. Oficialus production origin yra leidžiamas; Worker konfigūracija nekeista.
- Puslapis viešas ir tik noindex; tai nėra autentifikacija. Paslapčių ir lankytojų lygmens duomenų nėra; dashboard neįtrauktas į sitemap ir neturi canonical.
- Kitas žingsnis: vartotojo patvirtinimas PR #225 sujungimui; po merge patikrinti production deploy ir `/control/` gyvus duomenis.
