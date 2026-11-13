# PetTraffic AI – projekto perdavimas ir tęstinumo būsena

**Atnaujinta:** 2026-11-13  
**Saugykla:** `Pershore/PetTraffic-AI`  
**Pagrindinė šaka:** `main`  
**Istorijos šaka:** `automation-history`  
**Svetainė:** https://pettraffic-ai.pages.dev/

## 1. Projekto tikslas ir nekintamos taisyklės

PetTraffic AI yra lietuviška gyvūnų tematikos SEO svetainė, kurios tikslas – pritraukti organinį lankytojų srautą ir nukreipti jį į ARO Vet vaistinę / svetainę.

- Tikslas – maksimalus saugus automatizavimas ir minimalus vartotojo rankinis darbas.
- Jokio mokamo API ar paslaugų plano be aiškaus biudžeto patvirtinimo.
- Svetainės turinį galima rengti automatiškai, bet publikuoti tik gavus vartotojo patvirtinimą.
- ARO Vet svetainės, kodo ar infrastruktūros nekeisti be atskiro aiškaus leidimo.
- Nekeisti DNS, Cloudflare teisių, Worker/D1 production konfigūracijos ar secrets be atskiro leidimo.
- Niekada neprašyti slaptažodžių, MFA kodų, Global API Key ar slaptų raktų įklijuoti pokalbyje.
- Atskirti patikrintus faktus, hipotezes, laukiančius patikrinimus ir planus.
- Neteigti, kad funkcija veikia, kol tai nepatvirtinta realiu testu.
- Prieš kiekvieną techninį darbą perskaityti naujausią projekto būseną ir darbo žurnalą.

## 2. Ilgalaikės atminties / tęstinumo architektūra

Šaltiniai turi skirtingas paskirtis ir neturi būti painiojami:

1. **ChatGPT projekto instrukcijos ir ilgalaikė atmintis** – naudotojo tikslai, pageidaujamas darbo stilius ir nekintamos ribos. Tai nėra pilnas pokalbių archyvas ir negali būti vienintelis techninės būsenos šaltinis.
2. **GitHub `AGENTS.md` ir `docs/`** – pastovios projekto taisyklės, architektūra ir perdavimo dokumentacija.
3. **`automation-history` šaka** – automatiškai archyvuojamos, privatumo požiūriu filtruotos JSON būsenų momentinės kopijos po `reports/history/**`. Šioje šakoje nelaikyti svetainės šaltinio kodo ar darbo žurnalo.
4. **`reports/work-log/README.md` main šakoje** – darbo įrašai, atlikti veiksmai, testai, trukmė ir kiti tęstinumui svarbūs sprendimai.
5. **`reports/history/project-state/latest.md` ir `latest.json`** – automatiškai generuojama paskutinės patikrintos techninės būsenos santrauka; dienos snapshot'ai saugomi `YYYY-MM-DD.json`.
6. **Šis perdavimo dokumentas** – žmogui ir kitam ChatGPT pokalbiui skirta aiški kito veiksmo instrukcija.

Techninė būsena turi būti tikrinama GitHub. ChatGPT atmintis padeda prisiminti kontekstą, bet nepakeičia GitHub įrodymų.

## 3. Patvirtinti faktai 2026-11-13

- GitHub saugykla: `Pershore/PetTraffic-AI`.
- Paskutinė patikrinta `main` būsena: commit `40abf6a0ff5cf4565a8b8ec16e28e7e8d55ec354`.
- `automation-history` paskutinis patikrintas commit: `73a522b6f4e664765cf91c312edeb2b1d7a2ea5c`.
- Istorijos šakoje yra `reports/history/project-state/latest.md`, `latest.json`, dienos būsenų, analitikos, control-center ir rekomendacijų JSON archyvai.
- `reports/work-log/README.md` yra `main` šakoje. Jo nėra `automation-history` šakoje – tai atitinka istorijos šakos apribojimą saugoti tik agreguotą istoriją.
- PR #131 „Prevent Worker redeploys on workflow-only edits“ sujungtas.
- PR #131 deploy patikra #54 – success; site checks #388 – success.
- Control-center run #107 (`43456177377`) baigėsi success; visi jo job žingsniai buvo success.
- Run #107 sugeneruota projekto būsena pažymėta **REIKIA DĖMESIO**, nes AI agentų / control-core atminties patikra grąžino failure: `Unexpected_end_of_JSON_input`.
- Tame pačiame snapshot Worker API ir D1 pažymėti success, įskaitant svetainės heartbeat.
- GA4 ir Search Console snapshot paskutiniame būsenos dokumente dar buvo laukiamas kito ciklo; ankstesnėse diagnostikose GA4 Data API `runReport` kartotinai timeoutino. Stabilus GA4 veikimas nepatvirtintas.
- Jokių ARO Vet svetainės pakeitimų, DNS pakeitimų ar naujų production konfigūracijos pakeitimų šios tęstinumo sesijos metu neatlikta.

## 4. Būsenos klasifikacija

### Patvirtinta
- PR #131 sujungtas.
- PR #131 susijusios deploy ir site checks patikros sėkmingos.
- Automatinis projekto būsenos generatorius veikia: control-center run #107 įvykdė testus, sugeneravo ataskaitą, įkėlė artefaktą ir archyvavo istoriją.
- Worker/D1 buvo patvirtinti kaip veikiantys paskutiniame snapshot.

### Reikia taisyti / tikrinti
- AI agentų + control-core atminties ciklo klaida: `Unexpected_end_of_JSON_input`.
- GA4 `runReport` stabilumas ir naujausio snapshot turinys.
- Ar GSC duomenys neprarandami, kai GA4 API neatsako.
- Ar suplanuoti workflow realiai paleidžiami laiku, ne vien ar cron aprašytas.

### Paruošta, bet nepatvirtinta
- Automatinis projekto būsenos snapshot archyvavimas veikia, tačiau tai nėra pilnas pokalbių ar visų darbo sesijų automatinis transkriptas.
- Darbo žurnale nustatytos apskaitos taisyklės; aktyvaus darbo laikas turi būti matuojamas tik kai yra patikimi laiko žymenys. Nežinomų valandų neišgalvoti.

## 5. Kitas prioritetas – AI atminties klaidos diagnostika

1. Perskaityti Worker AI agentų orchestration / control-core kodą ir atitinkamus testus.
2. Perskaityti naujausią D1 `agent_runs`, `control_core_runs` ir `control_core_memory` būseną tik per jau esamą saugų, read-only diagnostikos kelią.
3. Išsiaiškinti, kuri JSON įvestis ar modelio atsakymas baigiasi netikėtai; nepriimti prielaidos, kad kalta konkreti paslauga.
4. Pridėti regresijos testą netaisyklingam / nepilnam JSON atsakymui ir saugų klaidos apdorojimą.
5. Pakeitimus pateikti PR, paleisti testus ir patikrinti workflow.
6. Nekeisti Worker/D1 production secrets, teisių ar duomenų be atskiro patvirtinimo.

## 6. Tolesnė darbo seka

1. AI agentų / control-core klaidos diagnostika ir taisymas.
2. GA4/GSC naujausio snapshot ir archyvo patikra.
3. Suplanuotų automatizacijų realių schedule-trigger paleidimų patikra.
4. Darbo žurnalo atnaujinimas po kiekvienos reikšmingos darbo sesijos; tikslus laikas – tik jei išmatuotas.
5. Kito perdavimo dokumento ir automatinio project-state snapshot suderinamumo patikra.

## 7. Saugumo ir privatumo ribos

- Istorijoje laikyti tik agreguotas procesų būsenas ir rekomendacijų santraukas.
- Nearchyvuoti lankytojų lygmens duomenų, žalių paieškos užklausų ar paslapčių.
- AI rekomendacijos yra patariamosios; modelio išvestys nesuteikia vykdymo teisių.
- Jokių automatiškai publikuojamų straipsnių.
- Jokių mokamų API ar paslaugų be vartotojo biudžeto patvirtinimo.
- ARO Vet atskira sistema; jos neliesti.

---
**Paskutinio techninės būsenos šaltinio run:** https://github.com/Pershore/PetTraffic-AI/actions/runs/43456177377  
**Paskutinė istorijos šaka:** https://github.com/Pershore/PetTraffic-AI/tree/automation-history/reports/history/project-state


## 8. Patvirtintas tęstinumo atnaujinimas – 2026-11-13 16:04 UTC

- PR #147 „Document durable project continuity and automatic work log“ sujungtas commit `8afc64961b3d9116f8c6218e9f380f51fa464e37`.
- Automatinio darbo žurnalo workflow pirmą kartą realiai įvykdytas sėkmingai: run `43458230606`; commit #147 automatiškai įrašytas į `reports/work-log/README.md`.
- PR #148 „Diagnose and harden AI agent memory JSON failures“ sujungtas commit `97551e833b2ae8a8494752595237688de1962bc9`.
- PR #148 Worker testai, Cloudflare token/resource validation ir site checks – success. Production Worker diegimas run `43458770826` – success; D1 migracijų žingsnis ir Worker deploy sėkmingi; galutinis health/auth smoke testas sėkmingas.
- Gyvas `/health` po diegimo grąžino HTTP 200, `database=connected`, `control_core_schema=connected` ir `decision_json_status=not_available`. AI atmintis dar nepatvirtinta: ankstesnio 2026-11-13 10:20 Europe/Vilnius agentų ciklo būsena liko `failed`, `ai_calls=1`, `Unexpected_end_of_JSON_input`; `control_core.status=not_started`, `memory_status=missing`.
- Naujas Worker kodas įdiegia stage-aware klaidų kodus (pvz., `reserve_topics:...`), saugiai praleidžia sugadintus istorinių įvykių JSON ir /health nebekrenta dėl sugadinto control-core sprendimo JSON. Tačiau konkreti senojo klaidos įvykio priežastis dar neįrodyta, nes ji atsirado iki stage diagnostikos diegimo.
- Naujas agentų ciklas suplanuotas kitam 10:20 Europe/Vilnius vykdymui – 2026-11-14. Tik po jo galima patvirtinti, ar agentai sėkmingai išsaugojo `control_core_runs` ir `control_core_memory`.
- Naujausias projekto būsenos snapshot: run `43458770880`, šaltinio commit `97551e833b2ae8a8494752595237688de1962bc9`; būsena vis dar **REIKIA DĖMESIO** dėl ankstesnio AI ciklo failure.
- Jokie ARO Vet pakeitimai, DNS pakeitimai, Cloudflare leidimų ar secrets pakeitimai neatlikti.

### Kitas privalomas veiksmas

Po 2026-11-14 10:20 Europe/Vilnius suplanuoto agentų ciklo perskaityti naujausią `reports/history/project-state/latest.md`, `reports/work-log/README.md` ir gyvą `/health`. Jei agentų ciklas sėkmingas, patvirtinti, kad control-core sprendimas ir kompaktiška atmintis įrašyti į D1. Jei nepavykęs, naudoti naują stage prefiksą iš `agent_orchestration.error_code` ir taisyti tik konkrečią įrodytą vietą.


## 9. Patvirtintas vakarinis tęstinumo atnaujinimas – 2026-11-13 17:12 UTC

### Įgyvendinta ir patikrinta
- PR #150 sujungtas commit `9d0bec49c37d8f3efc161b41dd9b8c87c3c258a8`: Copilot / Codex instrukcijos ir agentų sesijos tęstinumas.
- PR #151 sujungtas commit `1f046bfc34697460c5c7d712dcf732f97e8c9ee1`: `AGENTS.md` ir `docs/SESSION_START.md` papildytos voice-first / zero-manual-work taisyklėmis; sukurtas `docs/VOICE_FIRST_AUTONOMY.md`.
- PR #152 sujungtas commit `2f2abd72dea29a1f3fe11fd97f791b606cb524c1`: dokumentuoti GitHub Actions ir Worker cron laikai sulyginti su tikrais workflow failais.
- PR #153 sujungtas commit `aedbb0e059475c2708569b9679622ebece7fcfce`: į darbo žurnalą įrašyti #151 ir #152 darbai bei schedule audit rezultatas.
- PR #151 site-check run `43469054324` – success; PR #152 run `43469355419` – success; PR #153 run `43469659349` – success.
- Po sujungimų pagrindinės šakos site-check run `43469741292` – success. Automatinio darbo žurnalo run `43469472067` – success.
- Pagrindinis kasdienis ChatGPT priežiūros agentas yra aktyvus. Paskutinis vykdymas baigėsi 2026-11-13 08:22 UTC (10:22 Europe/Vilnius), truko apie 21 min. Kitas suplanuotas vykdymas: 2026-11-14 09:45 Europe/Vilnius.
- Papildoma vienkartinė AI atminties patikra jau suplanuota 2026-11-14 10:35 Europe/Vilnius; Worker agentų ciklas laukiamas 10:20 Europe/Vilnius.
- `AGENTS.md` dokumentuoti cron laikai dabar atitinka YAML: site-check 05:37 UTC, topic radar 06:23 UTC, analytics 06:47 UTC, live-site monitor 07:11 UTC, Lighthouse pirmadienį 07:27 UTC, central control center 08:40 UTC. Worker heartbeat – kas 15 min.; agentų orchestration laiko patikra 07:20 ir 08:20 UTC.
- ARO Vet atskira svetainė / kodas, DNS, Cloudflare leidimai ir secrets šios sesijos metu nekeisti. Mokamų paslaugų ar priklausomybių nepridėta.

### Naujausi analitikos įrodymai
- Analytics snapshot run `43443849180` baigėsi success ir sukūrė artefaktą `pettraffic-analytics-7d`.
- GA4 laikotarpis 2026-11-06–2026-11-12: duomenų gauti nepavyko dėl `ReadTimeout` (15 s).
- Search Console API tame pačiame snapshot veikė. 2026-11-04–2026-11-10: 0 parodymų, 0 paspaudimų; užklausų ir puslapių eilučių nėra. Sitemap pateiktas 2026-11-10, Google atsisiuntimas dar nenurodytas, apdorojimas laukiamas. Penkių prioritetinių URL patikros grąžino URL nežinomas Google / indeksavimo būsena neapibrėžta.
- Atskiras connectivity run `43441823755`: Search Console OK, GA4 FAILED su `ReadTimeout` (25 s). GA4 stabilumas nepatvirtintas; nekeisti leidimų ar paslaugos paskyros raktų be aiškaus poreikio.

### Svarbus fono automatizacijų blokatorius
- Peržiūrėjus 100 naujausių GitHub Actions vykdymų, nerasta nė vieno `event=schedule` paleidimo. Workflow failuose cron tvarkaraščiai yra, o push / pull_request / workflow_run paleidimai veikia.
- Dabartinė GitHub jungtis leidžia skaityti repo, PR ir Actions vykdymus, tačiau neleidžia perskaityti repo Actions nustatymų ar juos keisti. Todėl tiksli priežastis, kodėl nėra schedule paleidimų, dar nepatvirtinta. Nespėti, kad cron failai klaidingi.
- Pagrindinis ChatGPT priežiūros agentas vis tiek aktyvus ir gali atlikti kasdienį koordinavimą; tai nėra 24/7 nenutrūkstamas programavimo procesas. Vartotojui įprastų ataskaitų nesiųsti.

### Kitas konkretus veiksmas
1. Po 2026-11-14 10:20 Europe/Vilnius Worker agentų ciklo patikrinti `/health`, tikslų `agent_orchestration.error_code`, D1 `control_core_runs` ir `control_core_memory`. Vienkartinė automatizacija 10:35 jau suplanuota.
2. Jei AI ciklas nepavyko, taisyti tik pagal naują stage prefiksą ir logus; jei pavyko, patvirtinti tikrą atminties įrašymą.
3. Toliau diagnozuoti GitHub Actions schedule paleidimų nebuvimą. Jei Actions nustatymų skaitymas / keitimas lieka neprieinamas per jungtį, prašyti vieno minimalaus vartotojo veiksmo, neperduodant kitų techninių darbų.
4. Tęsti GA4 timeout diagnostiką tik gavus naujus įrodymus; Search Console duomenis išsaugoti nepriklausomai.


## 10. Patvirtintas techninis atnaujinimas – 2026-11-13 19:47 UTC

### PR #156 – D1 AI kvietimų rezervacijos atkūrimas
- PR #156 „Recover safely from ambiguous D1 AI call reservations“ sujungtas į main; merge commit `a74ad11f755f4bd39a9b17c92999d5172f045326`.
- Pakeista `worker/src/agents.mjs` rezervacijos logika: jei D1 `UPDATE ... RETURNING` atsakymas nutrūksta, pirmiausia perskaitomas `ai_calls` skaitiklis. Jei rezervacija jau įrašyta, ji nebekartojama; jei neįrašyta, leidžiamas vienas saugus pakartojimas. Taip išvengiama dvigubo AI kvietimų skaičiavimo.
- Pridėti testai: nutrūkęs atsakymas po commit, klaida prieš commit ir nepasiekiamas read-back.
- PR patikros: deploy workflow testai ir Cloudflare read-only validacija – success; site checks – success; snapshot sync PR patikra – success.
- Pagrindinės šakos Worker deploy run `43495408320` – success: Worker testai, Cloudflare token/resource validacija, D1 migracijų žingsnis, Worker deploy, gyvas `/health` (D1 ir control-core schema connected) ir neautentifikuoto API užklausos HTTP 401 patikra – success.
- Site checks run `43495408435` – success; control-center run `43495408385` – success; automatic work-log run `43495408363` – success; central API sync run `43495504768` – success.

### Kas dar nepatvirtinta
- 2026-11-13 ankstesnio agentų ciklo D1 įrašas vis dar pažymėtas `failed` su `Unexpected_end_of_JSON_input`. PR #156 išsprendžia dviprasmiškos rezervacijos atkūrimą ir yra įdiegtas, tačiau jis nepaleidžia tos pačios dienos agentų ciklo iš naujo (idempotentiškumo užraktas jau panaudotas).
- Kitas Worker agentų ciklas numatytas 2026-11-14 10:20 Europe/Vilnius. Tik po jo galima patvirtinti sėkmingą AI agentų darbą ir `control_core_runs` / `control_core_memory` D1 įrašus. ChatGPT patikra suplanuota 10:35 Europe/Vilnius.
- GitHub Actions cron konfigūracijos yra, bet patikros metu `event=schedule` vykdymų sąraše rasta tik viena vykdymo eilutė (site checks); atskirų schedule vykdymų analytics, topic radar, live-site monitor, control-center ir Lighthouse workflow nepastebėta. Dabartinė GitHub jungtis neleidžia patikrinti ar pakeisti repo Actions nustatymų. Nevadinti cron veikimo patvirtintu.
- Naujausias archyvuotas analytics snapshot run `43443849180` (2026-11-13 14:34 UTC): GA4 `unavailable`, Search Console `available`. GA4 runReport timeout problema neišspręsta; GSC laikotarpio 2026-11-04–2026-11-10 rodikliai 0 parodymų ir 0 paspaudimų, prioritetiniai URL dar nurodyti kaip Google nežinomi.

### Kitas konkretus veiksmas
Po 2026-11-14 10:20 Europe/Vilnius Worker ciklo perskaityti naujausią `reports/history/project-state/latest.md`, darbo žurnalą ir gyvą `/health`. Patikrinti, ar agentų būsena pasikeitė į `completed`, ar yra galiojantis control-core sprendimas ir atminties įrašas. Jei ne, naudoti naują `agent_orchestration.error_code` etapo prefiksą ir taisyti tik patvirtintą gedimo vietą. Atskirai tęsti GitHub Actions schedule ir GA4 diagnostiką. Nekeisti ARO Vet, DNS, secrets ar Cloudflare teisių.


## 11. Termux / Codex / GitHub vietinio tilto paruošimas – 2026-11-13 20:00 UTC

### Įgyvendinta ir patikrinta GitHub pusėje
- PR #159 `Add Termux Codex and GitHub local setup bridge` sujungtas commit `28ec11f4b97caae608d9cd4619d5ec7a36778ecf`.
- Pridėta `tools/termux/bootstrap.sh`: Termux įdiegia `proot-distro`, paruošia Debian aplinką ir iškviečia setup.
- Pridėta `tools/termux/setup-debian.sh`: Debian aplinkoje įdiegiami Git, GitHub CLI, Node.js, Python ir OpenAI Codex CLI; prisijungiama oficialiais GitHub ir ChatGPT device/browser srautais; klonuojama `Pershore/PetTraffic-AI`.
- Pridėta `docs/TERMUX_CODEX_BRIDGE.md` ir `.github/workflows/termux-bridge-check.yml`.
- PR bridge check run `43497319872` ir site checks run `43497319830` – success. Po merge bridge check `43497432740`, site checks `43497432744` ir work-log run `43497432741` – success.

### Kas dar neįjungta / nepatvirtinta
- Termux bootstrap dar nepaleistas vartotojo telefone; Codex CLI Android / Debian proot suderinamumas turi būti patvirtintas realiu `codex doctor` ir read-only užduotimi.
- Tiesioginio ChatGPT → Termux valdymo kanalo nėra. GitHub yra bendras kodo ir darbo šaltinis, bet automatinė užduočių eilė, kurią Termux Codex agentas pats paima ir paverčia PR, dar nesukurta.
- Nuolatinis Termux fono procesas / automatinis startas po telefono perkrovimo dar neįjungtas.
- Cloudflare prisijungimo duomenys į telefoną nekeliami; Worker diegimus toliau atlieka esami GitHub Actions procesai. Jokių Cloudflare teisių, secrets ar DNS pakeitimų neatlikta.

### Kitas konkretus veiksmas
Po PR #159 sujungimo vartotojas turi vieną kartą paleisti `docs/TERMUX_CODEX_BRIDGE.md` nurodytą bootstrap komandą Termux programoje ir užbaigti oficialius prisijungimus. Tada patikrinti `gh auth status`, `codex login status`, `codex doctor` ir read-only projekto aprašymo užduotį. Tik po šio realaus testo projektuoti / aktyvuoti GitHub užduočių eilę ir Codex automatinį PR kūrimą. Jokio mokamo API rakto ar Cloudflare rakto nereikia.


## 12. Patvirtintas Android Codex prisijungimo instrukcijos pataisymas – 2026-11-13 20:40 UTC

### Įgyvendinta ir patikrinta
- PR #160 „Clarify Codex device-code sign-in on Android“ sujungtas commit `230ccd62f6ce6939381b8ddc3d494fdf07154bb5`.
- `docs/TERMUX_CODEX_BRIDGE.md` dabar aiškiai nurodo privalomą ChatGPT **Settings → Security → Device code login (beta)** nustatymą. Valdomoje darbo srityje jį turi įjungti administratorius.
- Instrukcija paaiškina vienkartinio patvirtinimo URL ir kodo naudojimą naršyklėje bei Android atvejį, kai nuorodą perima ChatGPT programėlė.
- `tools/termux/setup-debian.sh` po nesėkmingo `codex login --device-auth` pateikia aiškų nustatymo patikros paaiškinimą.
- PR patikros: Termux bridge run `43503585504` – success; site checks `43503578139` – success.
- Po merge: Termux bridge run `43503672152` – success; site checks `43503671906` – success; automatinio darbo žurnalo run `43503672813` – success.
- Jokių API raktų, mokamų paslaugų, Cloudflare, DNS, ARO Vet ar produkcinės svetainės pakeitimų neatlikta.

### Kas dar nepatvirtinta
- Termux bootstrap dar nepaleistas vartotojo Android telefone. Codex CLI prisijungimas, `codex doctor` ir read-only užduotis realiame įrenginyje dar nepatikrinti.
- GitHub integracija šiame ChatGPT pokalbyje veikia (repo, PR ir Actions skaitymas / PR kūrimas patvirtinti), bet tai nėra tas pats, kas vietinis Codex CLI prisijungimas telefone.
- Tiesioginis ChatGPT → Termux valdymas ir automatinė Codex užduočių eilė dar neįjungti.

### Kitas konkretus veiksmas
Vartotojui reikia įjungti ChatGPT Settings → Security → Device code login (beta), tada vieną kartą paleisti `docs/TERMUX_CODEX_BRIDGE.md` nurodytą bootstrap komandą Termux programoje. Prisijungimo kodą įvesti tik oficialiame OpenAI puslapyje, niekada nekelti jo į pokalbį. Po diegimo patikrinti `gh auth status`, `codex login status`, `codex doctor` ir read-only projekto aprašymo užduotį. Tik po šio testo pradėti projektuoti automatinį GitHub užduočių paėmimą.
