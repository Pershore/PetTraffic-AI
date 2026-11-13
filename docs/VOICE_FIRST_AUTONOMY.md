# Pet traffic — voice-first autonomijos veikimo modelis

Atnaujinta: 2026-11-13

## Tikslas
Vartotojas turi galėti balsu pasakyti, ką reikia padaryti, ir gauti rezultatą. Įprastas techninis darbas neturi būti perkeliamas vartotojui, jei jį galima atlikti jau prijungtomis priemonėmis. Tikslas yra nulinis vartotojo rankinis darbas įprastoms, saugioms užduotims, o ne nekontroliuojama prieiga prie produkcijos.

## Vykdymo sluoksniai
1. **Balso / pokalbio sąsaja** — priima prašymą, paaiškina tik svarbiausią rezultatą ir prašo sprendimo tik tada, kai jo būtina.
2. **Vienas kasdienis koordinatorius** — esama aktyvi ChatGPT automatizacija „Pet traffic – kasdienė savarankiška priežiūra“, 09:45 Europe/Vilnius. Nedubliuoti.
3. **GitHub Actions specialistai** — svetainės testai, temų radaras, GA4/GSC snapshot, sveikatos stebėjimas, Lighthouse, centralizuotas valdymas, istorijos archyvavimas ir darbo žurnalas.
4. **Cloudflare Worker + D1** — ribotas API, įvykių priėmimas, agentų vykdymas ir projekto atmintis. Modelio išvestys yra patariamosios; vykdymo politika nustatoma kode.
5. **GitHub tęstinumas** — `AGENTS.md`, `docs/SESSION_START.md`, perdavimo dokumentai, `reports/work-log/README.md` ir privatumo požiūriu filtruoti `automation-history` snapshot'ai.

## Darbo ciklas
1. Perskaityti sesijos tęstinumo šaltinius ir naujausius įrodymus.
2. Pasirinkti vieną didžiausios vertės neužbaigtą darbą.
3. Patikrinti esamą kodą, testus ir paskutinį realų workflow / production įrodymą.
4. Atlikti mažą, izoliuotą pakeitimą atskiroje šakoje.
5. Pridėti regresijos testą, paleisti visus privalomus patikrinimus ir peržiūrėti visus PR job rezultatus.
6. Sujungti tik tada, kai patikros sėkmingos ir pakeitimas patenka į jau patvirtintą saugumo ribą.
7. Po sujungimo patikrinti realų diegimą / gyvą svetainę, jei pakeitimas tai liečia.
8. Atnaujinti darbo žurnalą, techninę būseną ir perdavimo dokumentą.

## Kada būtinas vartotojo sprendimas
- Naujos mokamos paslaugos, API ar prenumeratos.
- Viešo turinio publikavimas.
- DNS, domeno, Cloudflare teisių, production secrets ar kitų jautrių infrastruktūros nustatymų pakeitimai.
- ARO Vet atskiri darbai ar pakeitimai.
- Negrįžtami / destruktyvūs veiksmai arba veiksmai už repo ir patvirtintų integracijų ribų.

Visais kitais atvejais koordinatorius turi pats tęsti saugius veiksmus, jei įrankiai leidžia.

## Fono darbo realybė
- Pokalbio asistentas nevykdo nuolatinio proceso po to, kai baigia atsakymą ar įrankio sesiją.
- Nepertraukiamą arba periodinį darbą gali atlikti tik aktyvūs GitHub Actions, Worker cron ar ChatGPT automatizavimai.
- Kiekvienas fono darbas turi turėti patikrinamą tvarkaraštį, vykdymo ID, rezultatą ir klaidų būseną.
- Jei vykdymas dar neįvyko, žymėti WAITING. Jei vykdymas nepavyko, nustatyti priežastį pagal logus. Niekada neapsimesti, kad procesas veikia.
- Vartotojui nereikia matyti kiekvieno įrankio kvietimo; jam pateikiami tik patikrinti rezultatai, kritiniai blokatoriai ir prašymai dėl būtino leidimo.

## Nulinio papildomo biudžeto principas
Pirmiausia naudoti esamas GitHub Actions, Cloudflare Workers AI / D1 ribas, prijungtas ChatGPT/GitHub priemones ir Python / Node standartines bibliotekas. Jokių mokamų API, papildomų planų ar mokamų priklausomybių be aiškaus biudžeto patvirtinimo.

## Dabartinis svarbiausias techninis blokatorius
2026-11-13 paskutinis patikrintas projekto snapshot rodo, kad ankstesnis AI agentų vykdymas nepavyko su `Unexpected_end_of_JSON_input`; `control_core_runs` ir `control_core_memory` įrašymas tame cikle nepatvirtintas. PR #148 įdiegė etapų diagnostiką ir saugų JSON apdorojimą. Kitas agentų ciklas suplanuotas 2026-11-14 10:20 Europe/Vilnius. Po jo būtina patikrinti /health, tikslų `error_code` ir D1 atminties būseną; iki tol nespėlioti dėl gedimo priežasties.

## Dabartinės būsenos apribojimai
- Kasdienis koordinatorius yra aktyvus, bet tai nėra nuolatinis 24/7 programavimo procesas.
- Copilot instrukcijos saugykloje nereiškia, kad Copilot Cloud Agent aktyvuotas.
- Codex / Copilot naudojimas priklauso nuo realios paskyros prieigos ir limitų; mokamų funkcijų neaktyvuoti.
- Worker / D1 buvimas nereiškia, kad kiekvienas agento ciklas sėkmingai užbaigtas.
- Turinio rengimas gali būti automatizuotas, tačiau publikavimas lieka už žmogaus patvirtinimo vartų.
