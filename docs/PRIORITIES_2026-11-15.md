# Pet traffic – patvirtintas prioritetų planas

**Atnaujinta:** 2026-11-15 20:46 Europe/Vilnius  
**Strategija:** C – autonomijos patikimumas ir SEO/organinis augimas vykdomi lygiagrečiai.

## Prioritetai

| Prioritetas | Kryptis | Būsena | Kitas patikrinamas rezultatas |
|---|---|---|---|
| P0 | AI agentai / atmintis | NEPATVIRTINTA | Vieno po-deploy ciklo specialistų ir D1 readback įrodymai |
| P0 | SEO URL / canonical | NEPATVIRTINTA | Viena canonical extensionless URL forma visuose puslapiuose |
| P1 | GitHub schedule vėlavimai | NEPATVIRTINTA | Eilės laukimas atskirtas nuo job trukmės |
| P1 | Homepage mobile greitis | NEPATVIRTINTA | Pakartotinis Lighthouse ir 994 ms long task šaltinio nustatymas |
| P1 | Google indeksavimas | LAUKIA | Search Console sitemap ir prioritetinių URL atnaujinta būsena |
| P2 | Dashboard / privatus valdymas | LAUKIA | Issue #248 saugus auth / read-only ribų sprendimas |
| P2 | Analitika | PATIKRINTA rinkimo kelias | Savaitinė GA4/GSC ataskaita ir įrodymais paremti veiksmai |

## 1. Autonomija

Kitas tikslinis Worker AI ciklas: **2026-11-16 13:20 Europe/Vilnius**. Tikrinti pagal tą patį run_date ir ciklą:

1. run_date atitinka 2026-11-16; started_at po 13:20 LT.
2. status=completed, ai_calls=5, error_code=null.
3. Visi penki specialistai turi validžius atsakymus ir konkrečius įrodymus.
4. Užfiksuoti evidence_gaps; Control Core sprendimas turi derėti su specialistų išvestimi.
5. D1 memory įrašas ir memory_updated_at priklauso tam pačiam ciklui; readback grąžina tą patį įrašą.
6. Nekartoti dienos run_date; vienas ciklas per dieną. Issue #145 neuždaryti, kol įrodymai nepilni ir recovery_confirmed neįrodytas.

Po šio etapo tirti schedule vėlavimus pagal event=schedule, created_at, run_started_at, queue delay, job duration ir conclusion. push, workflow_dispatch, pull_request ar workflow_run nėra cron įrodymas. Saugus task runner lieka tik fiksuotas read-only check_site; jokio savavališko shell ar modelio generuoto kodo.

## 2. SEO / organinis augimas

Cloudflare Pages numatytai peradresuoja HTML .html URL į extensionless variantą, pvz. /puslapis.html → /puslapis (žr. [Cloudflare dokumentaciją](https://developers.cloudflare.com/pages/configuration/serving-pages/)). Lighthouse 2026-11-15 JSON rodo, kad keturių gidų requestedUrl buvo su .html, o finalUrl – be jo.

Reikia suderinti canonical, og:url, JSON-LD @id / item, sitemap, pradžios puslapio korteles, gidų vidines nuorodas ir About / Privacy navigaciją į extensionless URL. Išsaugoti visus 20 senų 301 source kelių ir 301 statusą, bet destinations nukreipti tiesiai į canonical URL. Validator ir live monitor turi įrodyti, kad canonical / sitemap / vidinės nuorodos grąžina 200 be redirect ir kad visi 20 senųjų URL vis dar gauna teisingą 301. PR nėra publikavimas; sujungimui reikia review ir atskiro sprendimo.

Toliau tikrinti Search Console sitemap, URL Inspection, indexing state, last crawl, parodymus, paspaudimus, CTR ir poziciją. Nuliniai ar vėluojantys duomenys nėra automatinis gedimo įrodymas. RSS antraštės nėra Google paieškų apimtys. Naujas turinys tik esant aiškiai spragai ir patikimam veterinariniam poreikio įrodymui.

## 3. Greitis ir UX

Lighthouse run #43745229308 buvo event=push, ne schedule; artefaktas #14173977237. 10 auditų: homepage mobile performance 81/100, TBT 769 ms, CLS 0; viena 994 ms long task Unattributable ir 70 ms puslapio užduotis. Keturių gidų mobile performance 98–99/100; SEO, accessibility ir best-practices 100/100. JS/CSS nekeisti spėliojant; pakartoti auditą po canonical URL pataisos.

## 4. Atskaitos taškas

GA4 2026-11-08–14: 7 aktyvūs naudotojai, 24 sesijos, 88 peržiūros, 0 patvirtintų organinių sesijų. GSC 2026-11-06–12: 0 parodymų, 0 paspaudimų; sitemap submitted/pending, penki prioritetiniai URL tuomet Google nežinomi. Tai istorinis atskaitos taškas, ne dabartinis matavimas.

## 5. Periodinis atnaujinimas ir ribos

- Kasdien: esamas koordinatorius 11:45 LT perskaito šį planą, naujausią automation-history snapshot ir main work-log; prioritetus keičia tik pagal naujus įrodymus.
- Kasdien: esamas 14:00 LT post-cycle verifier tikrina tos pačios dienos Worker ciklą, suplanuotą 13:20 LT. Jei dar neatliktas – LAUKIA.
- Kas savaitę: esamas weekly-growth-review.yml pirmadienį 18:30 UTC apjungia GA4, GSC, RSS, Lighthouse ir Control Center. Naujų ChatGPT grafikų nedubliuoti.
- Po reikšmingų darbų: per branch + PR atnaujinti PROJECT_MEMORY.md, SESSION_START.md jei reikia, work-log ir handover. automation-history latest.md/latest.json automatiškai generuojami – ranka neperrašyti.
- Į Pet traffic negrąžinti ARO Vet reklamos, produktų, kortelių, nuorodų, logotipų ar kitų elementų. ARO Vet svetainės / infrastruktūros nekeisti.
- Biudžetas 0 €/mėn.; be atskiro leidimo nekeisti DNS, Worker/D1 production, secrets, paskyrų teisių, billing ar production konfigūracijos.
- Viešo turinio automatiškai nepublikuoti. Vieši /control/ ir /dashboard/ lieka READ-ONLY; noindex nėra autentifikacija.
