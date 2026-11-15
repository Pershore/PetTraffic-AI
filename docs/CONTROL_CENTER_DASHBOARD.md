# Pet traffic Control Center dashboard

## Paskirtis
Atskiras, read-only projekto stebėjimo puslapis: https://pettraffic-ai.pages.dev/control/. Patogus vartotojo adresas https://pettraffic-ai.pages.dev/dashboard/ Cloudflare Pages lygiu perrašomas į tą patį Control Center turinį (site/_redirects, HTTP 200 proxy), todėl naršyklės adreso juostoje lieka /dashboard/. Jis sujungia architektūros žemėlapį, GitHub Actions būsenas, paskutinius vykdymus, viešos svetainės būklę, Worker/D1/Control Core sveikatos signalus, GA4/GSC agregatus, temų radarą ir įrankių/prieigų inventorizaciją.

## Duomenų šaltiniai
- GitHub REST vieši repo endpointai: paskutiniai 100 Actions run, atviri PR, main commit ir issue #145.
- Worker GET /health: tik vieši agreguoti sveikatos metaduomenys; Worker leidžia CORS tik https://pettraffic-ai.pages.dev. Todėl branch preview domenas Worker būsenos tiesiogiai neskaito ir aiškiai rodo preview CORS ribojimą; produkciniame Pages domene šis šaltinis leidžiamas.
- Viešos svetainės HEAD / patikra.
- automation-history/reports/history/analytics/YYYY-MM-DD.json ir topic-radar/YYYY-MM-DD.json: tik privatumo požiūriu filtruoti agregatai; bandomi naujausi 7 kalendorinių dienų archyvai.
- Lighthouse naujausias sėkmingas GitHub Actions run rodomas kaip nuoroda į originalų įrodymą; balai neišgalvojami ir neperrašomi.
- Agentų skiltyje rodomi Worker orchestration, Control Core, D1 atminties metaduomenys, rekomendacijų / evidence-gap skaičiai ir specialistų būsenos; PR skiltyje – visi atviri PR; įrankių skiltyje – pagrindiniai vieši svetainės puslapiai.

## Atnaujinimas ir ribojimai
- Puslapis atnaujina duomenis atidarius, paspaudus „Atnaujinti“ arba kas 5 minutes, kol puslapis atidarytas.
- GitHub API viešų užklausų kiekis sąmoningai ribotas; agregatų archyvai lokaliai puslapio sesijoje pakartotinai neapkraunami dažniau nei kas 30 minučių.
- Nepasiekiami duomenys rodomi kaip nežinomi / nepasiekiami, o ne kaip nulis.
- Suplanuotas paleidimas patvirtinamas tik pagal tikrą event=schedule; rankinis workflow_dispatch rodomas atskirai.
- Worker agentų ciklas vertinamas pagal run_date, started_at, status, ai_calls ir error_code; 13:20 LT tikslas atskiriamas nuo ankstesnio tos pačios dienos ciklo.
- Cloudflare Pages deploy ID / Cloudflare paskyros nustatymai tiesiogiai nepasiekiami, todėl dashboard rodo tik viešos svetainės HTTP ir GitHub workflow įrodymus.
- ChatGPT automatikų vykdymo būsena šiame dashboard nėra tiesiogiai skaitoma; rodomas architektūrinis komponentas, ne išgalvotas live statusas.
- Termux/Codex shell nėra prijungtas prie ChatGPT; rodomas kaip išorinis kūrimo įrankis.
- /v1/tasks* sąsaja tyčia išjungta; dashboard nesiunčia POST/dispatch komandų ir nekeičia sistemų.

## Privatumas ir indeksavimas
- Dashboard yra viešai pasiekiamas tame pačiame Pages domene. noindex,nofollow yra paieškos robotų instrukcija, ne prisijungimo ar prieigos kontrolė.
- Rodomi tik vieši GitHub duomenys, Worker viešas agreguotas /health, viešos svetainės būsena ir agreguoti analitikos rodikliai.
- Nėra API raktų, GitHub tokenų, Google service account turinio, lankytojų lygmens duomenų ar žalių Search Console užklausų.
- Puslapis sąmoningai neįtrauktas į sitemap.xml; jis neturi canonical URL.
- Jei vėliau reikės privataus dashboard, reikės atskiro Cloudflare Access / autentifikacijos projekto ir atskiro patvirtinimo. Vien noindex nėra apsauga.

## Valdymo ribos
Puslapis suteikia vizualinę navigaciją, filtravimą, atnaujinimą ir nuorodas į tikrus GitHub run / workflow / issue įrodymus. Jis pats nekeičia main, nesujungia PR, nepaleidžia workflow, nekeičia Worker/D1, DNS, secrets ar billing.
