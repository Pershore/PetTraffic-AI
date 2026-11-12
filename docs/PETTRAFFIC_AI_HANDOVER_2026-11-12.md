# PetTraffic AI — techninė perdavimo būsena

**Atnaujinta:** 2026-11-13 01:10 Europe/Vilnius  
**Saugykla:** `Pershore/PetTraffic-AI`  
**Pagrindinė šaka:** `main`  
**Paskutinis žinomas commit:** `fba60e6` (pilnas SHA: `fba60e6fb09c40c43fe5a5c1a2147efa862b0477`)

## Nekintančios saugumo taisyklės

- Jokio mokamo API ar paslaugų plano be atskiro biudžeto patvirtinimo.
- Svetainės turinys gali būti rengiamas, bet publikavimui būtinas savininko patvirtinimas.
- ARO Vet svetainės, kodo ir infrastruktūros nekeisti be atskiro leidimo.
- Niekada neprašyti slaptažodžių, MFA kodų, Cloudflare Global API Key ar paslapčių įklijuoti į pokalbį.
- Prieš infrastruktūros pakeitimus patikrinti būseną; atskirti patikrintą, paruoštą, bet neaktyvuotą ir planuojamą.
- GitHub istorija lieka pagrindiniu duomenų šaltiniu, kol D1 atsarginės kopijos ir atkūrimas nėra patikrinti.

## Atlikta ir patikrinta kode

### GitHub → Cloudflare autentifikacija

- PR #83 sujungtas: statinis `PETTRAFFIC_CONTROL_API_TOKEN` pakeistas trumpalaikiu GitHub OIDC JWT.
- Worker tikrina GitHub parašą pagal oficialų JWKS, issuer, audience, galiojimo laiką, repo, `main` šaką, tikslų workflow kelią ir `workflow_run` įvykį.
- `id-token: write` suteikiama tik `sync` darbui, ne PR testams.
- `PETTRAFFIC_CONTROL_API_TOKEN` ir Worker `API_TOKEN` nebereikalingi.
- Dabartinis OIDC identitetas apribotas tik `/v1/events` maršrutais. Užduočių API sąmoningai grąžina `503 task_api_not_enabled`, kol nebus atskiro agentų identiteto ir teisių politikos.
- PR #91 sujungtas ir šis apribojimas patikrintas testais.
- PR #93 sujungtas: papildomi testai patvirtina, kad neteisingos saugyklos, workflow arba pakeisto parašo OIDC žetonai atmetami.

### Worker diegimas ir stebėsena

- PR #84 sujungtas: pridėta diegimo pabaigos patikra — Worker `/health` turi patvirtinti D1 ryšį, o neautentifikuotas `/v1/events` turi grąžinti HTTP 401.
- PR #88 sujungtas: Worker diegimai serializuojami; automatinis diegimas vykdomas tik pakeitus runtime kodą, migracijas, Wrangler konfigūraciją arba diegimo workflow.
- PR #86 sujungtas: centrinis valdymo centras tikrina Cloudflare Worker + D1 sveikatą.
- PR #89 sujungtas: centrinis valdymo centras stebi ir `sync-control-api.yml` workflow būseną.
- PR #90 sujungtas: netaisyklinga Worker health JSON struktūra nebegali sugadinti visos centrinės ataskaitos.
- PR #85 ir #87 sujungti: dokumentacija atnaujinta pagal dabartinę architektūrą.

### Patikros

- PR #83: Worker Node testai, Python payload builder testai, svetainės statinės patikros ir Cloudflare išteklių/prieigos validacija — sėkmingi.
- PR #84: Worker Node ir Python testai, Cloudflare validacija, statinės svetainės patikros — sėkmingi.
- PR #86, #89, #90: centrinio valdymo centro Python testai ir statinės patikros — sėkmingi.
- PR #88, #91: Worker Node/Python testai, Cloudflare validacija ir statinės patikros — sėkmingi.
- Visi PR #83–#91 sujungti į `main`.

## Cloudflare ir GitHub konfigūracija

- Worker: `pettraffic-control-api`
- Worker URL: `https://pettraffic-control-api.pauliusgrubliauskis.workers.dev`
- D1: `pettraffic-control`
- GitHub secret `CLOUDFLARE_API_TOKEN` ir variable `CLOUDFLARE_ACCOUNT_ID` egzistavimas / prieiga patvirtinti per sėkmingą Cloudflare validavimo job.
- D1 ID aptinkamas automatiškai, jei `PETTRAFFIC_D1_DATABASE_ID` variable nėra.
- `PETTRAFFIC_CONTROL_API_URL` yra pasirenkamas; numatytas Worker URL įrašytas workflow.
- Tiesioginė Cloudflare ChatGPT integracija šiame projekte neprijungta; šiuo metu diegimas vykdomas per GitHub Actions.

## Svarbu: kas dar nepatvirtinta gyvoje aplinkoje

- Nors automatinis diegimas po `main` pakeitimų sukonfigūruotas, dabartinė integracija neparodė atskiro post-merge deploy run rezultato. Todėl galutinė naujos OIDC versijos gyvo Worker diegimo ir smoke testų sėkmė dar nelaikoma patvirtinta.
- Kitas centrinio valdymo centro suplanuotas vykdymas patikrins Worker + D1 sveikatą ir `sync-control-api.yml` būseną; nesėkmė turi sukurti / atnaujinti vieną techninį GitHub Issue.
- OIDC event sinchronizavimo realus veikimas bus patvirtintas tik po kito sėkmingo `analytics-snapshot`, `daily-topic-radar` arba `control-center` vykdymo, kuris sukels `workflow_run` įvykį.
- Užduočių vykdymo agentai dar neaktyvuoti. Nėra patvirtinto mokamo LLM API; joks mokamas API neįjungtas.

## Analitikos istorija

- `automation-history` šakoje patikrintas `reports/history/analytics/2026-11-12.json`.
- Jame yra trys tos pačios ataskaitos laikotarpio GA4/GSC snapshot'ai; rekomendacijų kodas GSC laikotarpius deduplikuoja, kad pakartotiniai paleidimai nebūtų palaikyti augimu.
- Patvirtintas to laikotarpio GA4: 7 aktyvūs naudotojai, 14 sesijų, 67 puslapių peržiūros.
- GSC: 0 parodymų ir 0 paspaudimų nurodytame laikotarpyje; ankstyvas rezultatas nelaikomas įrodymu apie ilgalaikį nematomumą.
- Organinių sesijų skaičius nepatvirtintas dėl GA4 kanalų sumos neatitikimo.

## Kitas suplanuotas ciklas (Lietuvos laiku)

- 08:17 — temų radaras
- 08:43 — GA4 / Search Console snapshot
- 09:05 — svetainės stebėjimas
- 10:00 — centrinis valdymo centras, dabar tikrinantis ir Worker/D1, ir API sync workflow
- Pirmadieniais 09:20 — Lighthouse

## Tęsti nuo čia

1. Patikrinti po sujungimo paleisto Worker deploy workflow rezultatą ir jo post-deploy health/auth smoke testus.
2. Patikrinti kitą realų OIDC snapshot sync vykdymą; patvirtinti, kad `/v1/events` GET/POST veikia ir D1 gauna tik privatumo filtruotus agregatus.
3. Patikrinti `automation-history` šakos failų struktūrą po pilno suplanuoto ciklo ir ar išsaugomi analytics, topic-radar, control-center bei recommendations snapshot'ai.
4. Tik tada spręsti dėl atskiro agentų OIDC identiteto ir užduočių API aktyvavimo. Iki tol task queue lieka išjungta.


## Tęsinio atnaujinimas — 2026-11-13

### Atskiras AI valdymo branduolys — sujungta į main

- PR #108 sujungtas į `main`: https://github.com/Pershore/PetTraffic-AI/pull/108
- Įdiegtas `worker/src/control-core.mjs`: deterministinis valdymo ir saugumo politikos sluoksnis atskirtas nuo modelio promptų.
- Keturios specialistų analizės ir koordinatorius lieka riboti iki penkių Workers AI kvietimų per dieną; branduolys pats neleidžia modelio išvestims suteikti naujų vykdymo teisių.
- D1 migracija `0003_control_core.sql` sukuria `control_core_runs` ir `control_core_memory): saugomas dienos sprendimas ir kompaktiška paskutinės būsenos atmintis.
- Specialisto trūkstami duomenys perduodami į bendrą sprendimą; koordinatorius negali jų paslėpti pateikdamas tuščią ataskaitą.
- Publikavimas, gyvos svetainės keitimas, DNS, ARO Vet, išlaidos, Cloudflare teisių keitimas ir savavališko kodo vykdymas lieka blokuoti. Rekomendacijos yra patariamosios.
- Projekto ilgalaikė istorija lieka GitHub; D1 atmintis yra operacinė santrauka, ne viso GitHub archyvo pakaitalas.

### Grafikas — sujungta į main

- PR #109 sujungtas: https://github.com/Pershore/PetTraffic-AI/pull/109
- Dienos AI agentų paleidimo tikslas: 10:20 Europe/Vilnius visus metus.
- Worker cron paleidžia 07:20 ir 08:20 UTC; IANA `Europe/Vilnius` laiko patikra leidžia tik tą kvietimą, kuris atitinka vietos 10:20. Taip išvengiama vasaros/žiemos laiko poslinkio ir dvigubo vykdymo.
- Senasis konfliktavęs PR #107 uždarytas; jį pakeitė #109.

### Testai ir rastų klaidų taisymas

- PR #108 pirmas CI bandymas aptiko neteisingai escape'intą datos validavimo regex: galiojančią `YYYY-MM-DD` datą jis atmesdavo. Klaida pataisyta prieš sujungimą.
- Po pataisymo GitHub Actions Worker testai (`npm test`) ir Python testai praėjo sėkmingai; Cloudflare išteklių/prieigos validacija taip pat praėjo.
- PR #109 Node/Python testai, Cloudflare validacija ir svetainės statinės patikros praėjo.
- Papildomai lokaliai patikrinti 9 Node testai (9/9) ir D1 migracijų SQL seka (0001, 0002_agent_runs, 0003_control_core) — sėkmingai.
- Tai patvirtina šiuos testų rinkinius, bet negarantuoja, kad ateityje neatsiras naujų klaidų; reikalingas nuolatinis CI ir gyvos aplinkos stebėjimas.

### Dar nepatvirtinta gyvoje Cloudflare aplinkoje

- PR patikros tyčia praleido Worker deploy darbą (deploy job: skipped). Pakeitimų sujungimas į `main` turėtų sukelti automatinį deploy pagal `.github/workflows/deploy-control-api.yml`, nes pakeisti Worker kodas ir migracijos.
- Šio tęsinio metu negautas patikimas post-merge deploy run rezultatas, todėl **nežymėti D1 migracijos 0003 ar naujo Worker kodo kaip gyvai aktyvuotų**.
- Privaloma patvirtinti deploy sėkmę, `GET /health` atsakymą su `database: connected`, neautentifikuoto `/v1/events` HTTP 401 ir pirmą realų suplanuotą AI vykdymą su įrašais abiejose control-core D1 lentelėse.
- Task API lieka išjungta; atskiras agentų OIDC identitetas, agentų užduočių claim/complete ir platesnės autonominės teisės dar neįjungti.
