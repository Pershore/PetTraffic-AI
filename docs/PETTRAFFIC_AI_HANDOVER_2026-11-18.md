# Pet traffic – perdavimo ataskaita (2026-11-18)

## Patvirtinta būsena

- Main HEAD: 0cbace2e8fa6fb93cdc81c5c4fdb72d744a94a82. Po paskutinio live-site check commit 3cfe8a56 iki dabartinio main nebuvo pakeista nė vieno site/** failo; vėlesni skirtumai – workflow, docs ir Worker failai.
- Paskutinis live-site check: Daily-suite #44119444026, tikras event=schedule, 3/3 job success. Patikrinta 12 vidinių URL, robots.txt, sitemap.xml, 404 ir 20 senų URL 301 nukreipimų. Tiesioginis Cloudflare Pages deployment ID per GitHub įrankį nepasiekiamas; viešo puslapio prieinamumą patvirtino live check.
- Paskutinis static site-check: #44177692313 success. Main skirtumas po šio run buvo tik work-log įrašas.

## Daily-suite schedule incidentas

- 2026-11-18 cron 06:10 UTC: iki 10:14 UTC nėra tikro event=schedule.
- Paskutinis schedule: #44119444026, 2026-11-17 15:53:16 UTC (apie 9 val. 43 min. po cron), 3/3 job success, apie 43 s trukmė. Vėlavimas įvyko iki workflow starto, ne job viduje.
- Vienas tikslus owner bridge komentaras /pettraffic-run-daily-suite pridėtas 2026-11-18 10:13 UTC (#6975502506). Bridge #44283389091 success, bet daily-suite dispatch buvo praleistas dėl ankstesnio schedule 20 val. deduplikavimo lango. Langas baigiasi 2026-11-18 11:53:16 UTC / 13:53:16 LT. Naujo daily-suite workflow_dispatch run nėra; komandos nekartoti, kol nėra naujų įrodymų.
- Po bridge įvykio Control Center #44283434049 (workflow_run) success, o D1 sync #44283516916 įrašė 2 Control Center įvykius ir patvirtino jų readback. Tai nėra Daily-suite analytics/topic snapshot sync.

## Worker AI ir D1

- Control Center ataskaitos /health santrauka: WAITING iki 13:20 LT. Worker API/D1 healthy, heartbeat buvo prieš ~14 min. nuo 10:14 UTC ataskaitos.
- Read-only D1 diagnostics #44283516906 success: 2026-11-18 ciklo iki 13:20 dar nėra; paskutinis memory įrašas 2026-11-17 12:00:21.622 UTC, Control Core needs_evidence, 5 spragos. Tai laukimas prieš dienos ciklą, ne šiandienos ciklo nesėkmė.
- 13:20 LT – patikrinti naują /health: run_date, started_at, status, ai_calls, error_code, visų 5 specialistų validumą, konkrečius evidence, Control Core spragas ir to paties ciklo D1 memory readback. 14:00 LT esamas verifier turi tikrinti tą patį run. Nekartoti ciklo ir neuždaryti issue #145 be recovery_confirmed=true.

## Analitika ir organinis augimas

- Paskutinis Daily-suite GA4 artefaktas #14344656865: 2026-11-10–16 – 9 aktyvūs naudotojai, 26 sesijos, 90 peržiūrų, 0 patvirtintų organinių sesijų.
- GSC 2026-11-08–14 – 0 parodymų, 0 paspaudimų; sitemap pateiktas, bet pending; 5 prioritetinių URL indeksavimo būsena nežinoma. Nulis laikomas tik šio laikotarpio šaltinio reikšme, ne gedimo įrodymu.
- Temų radaras #14344522242: 4 dienos, 29 unikalios viešų RSS antraščių nuorodos; tai ne Google paieškų apimtis.
- Savaitinė augimo peržiūra #43999680694 success. Ji naudojo senesnius GA4/GSC langus (Nov 9–15 / Nov 7–13), todėl prioritetą teikti naujesniam Daily-suite artefaktui.

## Lighthouse

- Paskutinis savaitinis auditas #43915631789, 2026-11-16 17:10 UTC, 10 HTML/JSON ataskaitų.
- Palyginus su #43699958471 (Nov 15), dog-diarrhea mobile LCP 1.873 → 9.779 s; vet-visit desktop 0.551 → 8.078 s; vet-visit mobile 1.880 → 5.548 s. TBT=0, CLS=0; didesnis server response time. Vienas blogas matavimas neįrodo kodo regresijos. Nekeisti kodo ir nedubliuoti audito, nes sėkmingas auditas yra paskutinių 7 dienų lange. Kitas savaitinis grafikas – pirmadienį 2026-11-23.

## SEO / PR / saugumo ribos

- Main canonical ir sitemap nuosekliai naudoja .html; PR #264 siūlo clean URL ir metadata/navigation pakeitimus, bet yra draft ir reikalauja atskiro viešo SEO pakeitimo patvirtinimo. Nemerginti.
- About/privacy turi title, description ir canonical, bet neturi OG žymų. Tai nedidelė, neblokuojanti SEO galimybė.
- GA4 skriptas įkeliamas tik po aiškaus slapukų sutikimo; ARO Vet, reklamos ir affiliate nuorodų nerasta.
- Visi 6 atviri PR (#261, #263, #264, #266, #267, #280) yra draft; kelių šakos pasenusios / mergeable=false. Main nėra apsaugota (protected=false); repository settings nekeisti.
- Vienas work-log run #44177670499 nepavyko dėl GitHub 409 SHA konflikto; vėlesnis #44177683776 success. Stebėti, bet nelaikyti produkcijos gedimu.
- Nekeisti DNS, secrets, teisių, billing, Worker/D1 production, viešo turinio, ARO Vet ar mokamų paslaugų.

## Pirmas neužbaigtas veiksmas

1. 2026-11-18 13:20 LT – vienintelis Worker AI ciklas ir /health + D1 readback.
2. 14:00 LT – esamas post-cycle verifier.
3. Kitame koordinatoriaus vykdyme patikrinti Daily-suite tikrą event=schedule; jei jo nėra ir 20 val. deduplikavimo sąlygos leidžia, naudoti tik esamą owner bridge. Issue #145 palikti open iki pilno įrodymo.
