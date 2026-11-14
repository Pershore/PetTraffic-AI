# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-14 (patikra po 10:38 UTC)
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 43586067171
- Šaltinio commit: b0cfcbe1ad7e6d73673c86dc1b3c7052b9a80b3a

## Paskutinis patikrintas etapas

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Pagrindinis kasdienis ChatGPT koordinatorius yra įjungtas ir kitą kartą numatytas 2026-11-15 09:45 Europe/Vilnius. GitHub Actions cron problema lieka nepaaiškinta: per 1 056 vykdymus (11 puslapių) rastas tik vienas `event=schedule` vykdymas 2026-11-13; 2026-11-14 schedule įvykių nėra. Patikrinti Actions workflow/repository aktyvumo nustatymus reikia per paskyros sąsają, nes dabartinė jungtis jų nepasiekia. Cloudflare tokeno rotacija ir GitHub secret atnaujinimas taip pat nepatvirtinti; PR #183 production deploy lieka sustabdytas.

## Patvirtinti procesai

- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 5 min.

## Problemos

- **GA4 ir Search Console** (warning): suplanuotas `schedule` ciklas 06:47 UTC neįvyko (naujausių 100 Actions vykdymų sąraše nėra `event=schedule`). Tačiau po PR #184 sujungimo push-trigger analytics run #46 (#43586027796) sėkmingai nuskaitytas: GA4 7 aktyvūs naudotojai, 24 sesijos, 88 puslapių peržiūros; Search Console 0 parodymų ir 0 paspaudimų. Duomenys patvirtinti ataskaitos artefaktu. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43586027796
- **Temų radaras** (warning): Suplanuotas ciklas nuo 2026-11-14 06:23 UTC dar neįvykdytas; suplanuotų paleidimų istorijoje nėra. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43422828353
- **Svetainės stebėjimas** (warning): Suplanuotas ciklas nuo 2026-11-14 07:11 UTC dar neįvykdytas; suplanuotų paleidimų istorijoje nėra. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia. – https://github.com/Pershore/PetTraffic-AI/actions/runs/43422828198
- **AI agentai + control-core atmintis** (failure): AI agentų ciklas nepavyko (2026-11-14); AI kvietimų: 4; klaida: model_content-review_model_output_invalid_json. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Centrinės API sinchronizavimas: Vyksta (in_progress).
- Lighthouse auditas: Workflow atnaujintas 2026-11-13 12:09 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.
- Centrinis valdymo centras: Vyksta (in_progress).

## AI agentų ir atminties patikra

- Būsena: **failure** – AI agentų ciklas nepavyko (2026-11-14); AI kvietimų: 4; klaida: model_content-review_model_output_invalid_json.
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


## 2026-11-14 – GA4 timeout pataisa patvirtinta realiu nuskaitymu

- PR #184 sujungtas squash commit `1d23e3211748b8866767b2e1cbfa64506799afc3`: GA4 `runReport` read timeout padidintas nuo 15 iki 30 sekundžių; regresijos testas atnaujintas.
- Po merge automatiškai paleistas analytics workflow #46 (run `43586027796`), baigėsi success. Testai, API nuskaitymo žingsnis, ataskaitos artefakto įkėlimas ir agreguotos istorijos archyvavimas sėkmingi.
- Patvirtintas GA4 laikotarpis 2026-11-07–13: 7 aktyvūs naudotojai, 7 nauji naudotojai, 24 sesijos, 88 puslapių peržiūros. Kanalai: Direct 13 sesijų, AI Assistant 11; organinės paieškos sesijos 0.
- Search Console laikotarpis 2026-11-05–11: 0 parodymų, 0 paspaudimų, CTR 0.0 %, vidutinė pozicija 0.0; užklausų ir puslapių eilučių nepateikta. Sitemap pateiktas, bet Google atsisiuntimo laikas dar nenurodytas, apdorojimas laukia. Nelaikyti 0 parodymų indeksavimo įrodymu.
- Svarbu: GA4 duomenų gavimas atkurtas per push-trigger paleidimą, bet suplanuotas cron paleidimas vis dar nepatvirtintas. Šių dviejų būsenų nemaišyti.
- PR: https://github.com/Pershore/PetTraffic-AI/pull/184; run: https://github.com/Pershore/PetTraffic-AI/actions/runs/43586027796.


- Po analitikos ir istorijos dokumentavimo pakeitimų main site-check #526 (run `43586152253`) baigėsi success. Analytics run #46 (`43586027796`) ir centrinio valdymo run #127 (`43586067171`) taip pat success; sync-control-api run #138 (`43586103335`) success.


## 2026-11-14 – papildoma autonomijos patikra

- GitHub Actions API: patikrinta 1 056 vykdymų istorija per 11 puslapių. Vienintelis rastas `event=schedule` – site-check run `43433299383`, 2026-11-13 13:23:57 UTC, success. 2026-11-14 schedule įvykių nerasta.
- Workflow YAML cron eilutės egzistuoja. Tiksli priežastis nenustatyta, nes GitHub integracija neleidžia skaityti ar keisti Actions workflow/repository aktyvumo nustatymų. Push / PR / workflow_run vykdymai nelaikomi suplanuotų ciklų įrodymu.
- Pagrindinis ChatGPT koordinatorius „Pet traffic – kasdienė savarankiška priežiūra“: enabled; paskutinis vykdymas completed 2026-11-14 08:13:35 UTC; kitas 2026-11-15 09:45 Europe/Vilnius. Dubliuojantis agentas nesukurtas.
- PR #183 lieka open; Worker testai ir Cloudflare token/resource validation success, tačiau deploy job skipped. Worker JSON pataisa neaktyvi produkcijoje.
- Cloudflare API tokenas laikomas galimai atskleistu; rotacijos ir GitHub Actions secret atnaujinimo įrodymo nėra. Jokių paslapčių keitimų neatlikta.
- Issue #145 papildytas komentaru `6876095236`; handover ir work-log atnaujinti.
- Kodo, repo nustatymų, Worker/D1, DNS, secrets, ARO Vet, viešo turinio ar mokamų paslaugų pakeitimų neatlikta.
