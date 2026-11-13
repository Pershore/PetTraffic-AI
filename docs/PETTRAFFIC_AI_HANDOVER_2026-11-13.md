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
- `reports/work-log/README.md` yra `main) šakoje. Jo nėra `automation-history` šakoje – tai atitinka istorijos šakos apribojimą saugoti tik agreguotą istoriją.
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
