# Pet traffic – projekto perdavimas ir sistemos auditas

**Data:** 2026-11-14  
**Saugykla:** `Pershore/PetTraffic-AI`  
**Šakos:** `main`, `automation-history`  
**Vieša svetainė:** https://pettraffic-ai.pages.dev/

## Trumpa išvada

Sistema turi veikiančius GitHub, Cloudflare Worker ir D1 komponentus, tačiau 2026-11-14 auditas nepatvirtino periodinių Worker cron vykdymų, AI agentų sėkmės, D1 atminties atnaujinimo ar GitHub Actions suplanuotų vykdymų. Vieša svetainė pasiekiama, o straipsnių paieškos CSS regresija pateikta taisyti PR.

## 1. Patikrinta gyva Worker būsena

2026-11-14 atliktas tiesioginis, be cache `GET /health`:

- HTTP 200.
- `ok=true`, `database=connected`, `control_core_schema=connected`.
- Paskutinis heartbeat: `2026-11-13T22:00:47.423Z`; `site_ok=true`, `site_status=200`, `database_ok=true`.
- Paskutinis agentų vykdymas: `run_date=2026-11-13`, `status=failed`, `ai_calls=1`, klaida `Unexpected_end_of_JSON_input`.
- Control-core: `status=not_started`, `decision_json_status=not_available`, `memory_status=missing`, `memory_updated_at=null`.

**Išvada:** API ir D1 pasiekiami, bet heartbeat daugiau kaip parą neatnaujintas, o AI agentų ciklas ir ilgalaikės atminties įrašymas nepatvirtinti. Vien cron konfigūracija neįrodo, kad įvykiai vykdomi.

### Kodo būklė

- PR #162: netaisyklingas / nepilnas modelio JSON nebėra tyliai laikomas sėkmingu; įrašoma klaida ir dalinė atmintis.
- PR #164: Workers AI atsakymo limitas padidintas iki 1024 žetonų.
- PR #166: agentų vykdymo laikas vertinamas pagal Cloudflare `controller.scheduledTime`.
- Worker deploy run #43509823943 buvo sėkmingas; anksčiau loge patvirtinti cron įrašai `*/15 * * * *` ir `20 7,8 * * *`.
- Dabartinė `wrangler.toml` konfigūracija turi abu cron. Migrations apibrėžia heartbeat lentelę, jos laukai atitinka įrašymo kodą. Tačiau dabartinių Cloudflare runtime logų skaitymo prieigos nėra, todėl negalima atskirti, ar cron įvykiai nepristatomi, ar heartbeat INSERT nepavyksta.

## 2. GitHub Actions

- GitHub Actions API užklausa `created >= 2026-11-14T00:00:00Z` grąžino 0 workflow vykdymų.
- Peržiūrėti 100 naujausių vykdymų; naujų 2026-11-14 vykdymų nerasta.
- YAML failuose suplanuoti cron tvarkaraščiai yra, tačiau šiandieninių `event=schedule` vykdymų nėra.
- Pagrindinis `control-center.yml` turi `schedule`, `workflow_run`, `push` ir `workflow_dispatch` trigerius; jo paskutinė patikrinta sėkminga ataskaita buvo lapkričio 13 d.
- Issue #145 „PetTraffic: central automation alert“ vis dar open; jame nurodyta sena AI agentų klaida.
- GitHub integracija neleidžia perskaityti ar keisti repository Actions settings, taip pat nepateikia tiesioginio workflow dispatch veiksmo.

**Išvada:** Actions grafikai aprašyti, bet šiandien neįvykdyti. Priežastis nepatvirtinta; nekeisti repository permissions ar settings spėliojant.

## 3. Viešos svetainės patikra

2026-11-14 Firecrawl live fetch grąžino HTTP 200:

- Pagrindinis puslapis.
- `kada-kreiptis-i-veterinara.html`.
- `kate-negali-pasislapinti-skubi-pagalba.html`.
- `kate-viduriuoja-ka-daryti.html`.
- `suo-viduriuoja-ka-daryti.html`.
- `about.html`, `privacy.html`, `robots.txt`, `sitemap.xml`.

### Rasta ir pataisoma paieškos regresija

Naršyklės sąveikos testas įvedus `šuo` patvirtino:

- Rezultatų būsena: `Rodoma 1 iš 4 straipsnių.`
- Viena kortelė turi `hidden=false`; trys kitos `hidden=true`.
- Tačiau visų kortelių apskaičiuotas `display` buvo `flex`, nes `.article-card { display:flex }` autoriaus CSS taisyklė perrašo naršyklės numatytą `[hidden]` stilių.
- Išvalius paiešką visos keturios kortelės vėl pažymėtos kaip rodomos.

Pataisymas: pridėti `.article-card[hidden]{display:none!important}` ir regresijos testą. Pakeitimas pateiktas atskirame PR; kol CI ir gyvas po-merge testas nepraeiti, jo nelaikyti publikuotu.

## 4. Analitika

- Paskutinis turimas analytics snapshot (2026-11-13): GA4 `ReadTimeout`, todėl GA4 metrikų nėra.
- Search Console API tame pačiame cikle veikė nepriklausomai nuo GA4.
- Naujo 2026-11-14 snapshot nėra, nes atitinkamas suplanuotas GitHub Actions vykdymas nerastas.
- Neišgalvoti srauto, parodymų ar paspaudimų skaičių.

## 5. Termux / Codex

- Termux bootstrap, Debian proot, GitHub CLI ir Codex CLI diegimo kodas yra saugykloje; ankstesni CI patikrinimai praėjo.
- Tikras diegimas Android telefone, `gh auth status`, `codex login status`, `codex doctor` ir vietinis užduočių polleris nepatvirtinti.
- Dabartiniai įrankiai nesuteikia tiesioginės Android shell / Termux prieigos. GitHub integracija veikia atskirai.

## 6. Saugumas ir išlaidos

- Naujas mokamas API, planas ar priklausomybė neaktyvuota.
- Firecrawl naudotas tik viešų URL skaitymui su esama kvota.
- ARO Vet, DNS, Cloudflare Worker/D1 production konfigūracija, paskyros teisės ir secrets nekeisti.
- Turinys nepublikuotas; rekomendacijos ir kodo pataisos lieka peržiūrimos PR.

## 7. Kiti veiksmai

1. Užbaigti straipsnių filtro CSS pataisą: PR patikros, merge tik po sėkmingo CI, tada gyvai patikrinti „šuo“, „katė“ ir tuščią paiešką.
2. Gauti read-only Cloudflare Worker cron/logų įrodymus ir nustatyti, kodėl heartbeat nuo 2026-11-13 22:00:47 UTC neatsinaujino. Nevykdyti antro AI ciklo ir nekeisti D1 rankiniu būdu.
3. Atkurti GitHub Actions schedule paleidimus; priežasties neįmanoma patvirtinti per dabartinę GitHub integraciją, nes repository Actions settings neprieinami.
4. Tęsti GA4 `runReport` timeout diagnostiką, išsaugant nepriklausomus Search Console duomenis.
5. Tik po realaus naujo agentų ciklo ir /health atnaujinimo patvirtinti control-core atmintį bei uždaryti Issue #145.
