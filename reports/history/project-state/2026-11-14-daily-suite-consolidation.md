# Pet traffic – 2026-11-14 automatizacijų suvienodinimo istorija

## Pakeitimai

- PR [#194 – daily automation suite](https://github.com/Pershore/PetTraffic-AI/pull/194) sujungtas commit `ba7385bf45ac4f091212556ffac80c6a82162583`.
  - GA4 / Search Console, temų radaras ir live-site monitor perkeliami į vieną `.github/workflows/daily-suite.yml`.
  - Rinkinys paleidžiamas tik po patvirtinto `Pet traffic site checks` suplanuoto įvykio (cron 05:37 UTC).
  - Atskiri moduliai išlieka atskirais job ir saugo atskiras ataskaitas bei istoriją.
  - Ankstesni atskiri workflow palikti push / rankinėms patikroms; cron pašalintas, kad nebūtų dubliuojamų vykdymų.
  - Central API sync palaiko abu rinkinio agreguotus artefaktus ir dalinius rezultatus.
- Daily-suite trigeris PATIKRINTAS ne suplanuotu įvykiu: [run 43600907737](https://github.com/Pershore/PetTraffic-AI/actions/runs/43600907737) turėjo pavadinimą `Non-scheduled site-check run #43600881588`; analytics, topic-radar ir live-check job teisingai buvo `skipped`. Tai patvirtina trigerio filtrą, bet ne tikrą suplanuotą vykdymą.
- PR [#195 – cancelled run status fix](https://github.com/Pershore/PetTraffic-AI/pull/195) sujungtas commit `7ab97db2ac8dfd0e07d525264860affe923678a9`.
  - Valdymo centras atskiria schedule vykdymus nuo push / rankinių vykdymų.
  - Atšauktas arba dar vykstantis ne suplanuotas paleidimas nebeužmaskuoja suplanuoto ciklo būsenos.
  - Pašalinti pertekliniai workflow_run trigeriai, kuriuos dabar pakeičia daily-suite.

## Patikros

- PR #194 CI: site checks, central control center, sync tests ir Cloudflare Pages patikra – success; Worker deploy – skipped.
- PR #195 CI: site checks, central control center ir Cloudflare Pages patikra – success.
- Po-merge kontrolės paleidimai [43601159634](https://github.com/Pershore/PetTraffic-AI/actions/runs/43601159634) ir [43601309176](https://github.com/Pershore/PetTraffic-AI/actions/runs/43601309176) – success.
- [Kontrolės ataskaita 43601309176](https://github.com/Pershore/PetTraffic-AI/actions/runs/43601309176) rodo: daily-suite waiting, Lighthouse waiting, central API success, Worker/D1 success, AI agents failure. Klaidingo cancelled įspėjimo nėra.
- Push patikros: site-check [43600881588](https://github.com/Pershore/PetTraffic-AI/actions/runs/43600881588) ir [43601123268](https://github.com/Pershore/PetTraffic-AI/actions/runs/43601123268) – success; analytics [43600881631](https://github.com/Pershore/PetTraffic-AI/actions/runs/43600881631) – success; topic radar [43600881695](https://github.com/Pershore/PetTraffic-AI/actions/runs/43600881695) – success; live-site monitor [43600881611](https://github.com/Pershore/PetTraffic-AI/actions/runs/43600881611) – success.
- GA4 laikotarpis 2026-11-07–13: 7 aktyvūs naudotojai, 7 nauji naudotojai, 24 sesijos, 88 puslapių peržiūros.
- Search Console laikotarpis 2026-11-05–11: 0 parodymų, 0 paspaudimų, CTR 0; sitemap pateiktas, bet dar pending; 5 prioritetiniai URL Google dar nežinomi.
- Temų radaras: 31 unikali nuoroda, 0 tuščių patikrų iš 7. Šaltinis Google News RSS; tai nėra Google paieškos apimčių matavimas.
- Centrinės API sync paleidimai [43600907662](https://github.com/Pershore/PetTraffic-AI/actions/runs/43600907662), [43600987929](https://github.com/Pershore/PetTraffic-AI/actions/runs/43600987929) ir [43601193788](https://github.com/Pershore/PetTraffic-AI/actions/runs/43601193788) – success; žurnaluose patvirtintas D1 įrašymas ir perskaitymas atgal.

## SEO patikros pastabos

- `robots.txt` leidžia indeksuoti svetainę ir nurodo sitemap.
- Sitemap turi pradžios, apie, privatumo ir keturis pagrindinius straipsnius.
- Pagrindinis puslapis ir keturi straipsniai turi canonical, `index,follow`, aprašymus ir struktūruotus duomenis; straipsniai turi Article ir BreadcrumbList JSON-LD.
- `site/_redirects` yra tuščias sąmoningai: PR #60 pašalino neekvivalenčius senų straipsnių peradresavimus į pradžios ar bendrą veterinarijos puslapį. Šių peradresavimų neatkurti; retires URL turi grąžinti tikrą 404, kol nėra lygiaverčio turinio.

## Laukiantys darbai

- 2026-11-15 05:37 UTC (07:37 Europe/Vilnius): kitas site-check schedule; po jo turi įvykti pirmas tikras daily-suite ciklas. Patikrinti tris job, ataskaitas, automation-history ir D1 sync.
- 2026-11-15 07:27 UTC (09:27 Europe/Vilnius): savaitinis Lighthouse auditas.
- 2026-11-15 08:20 UTC (10:20 Europe/Vilnius): Worker AI agentų ciklas po PR #183 deploy. Klaida `model_content-review_model_output_invalid_json` buvo iš 08:20 UTC ciklo iki deploy 11:51 UTC, todėl pataisos veiksmingumas dar nepatikrintas.
- Issue [#145](https://github.com/Pershore/PetTraffic-AI/issues/145) paliktas atviras iki AI agentų ciklo realaus atsigavimo patvirtinimo.

## Saugumo ribos

- ARO Vet svetainė, kodas ir infrastruktūra neliesti.
- Viešas svetainės turinys nepublikuotas ir nekeistas.
- Worker runtime, D1 schema ir konfigūracija, DNS, secrets ir Cloudflare teisės nekeistos.
- D1 įrašyti tik agreguoti analitikos / temų snapshot duomenys per jau veikiančią OIDC sinchronizaciją.
- Naujų mokamų paslaugų ar API neaktyvuota.
- Termux / Codex vietinis Android terminalas šioje sesijoje nebuvo tiesiogiai pasiekiamas, todėl jo būsena nebuvo pakeista ar laikoma patikrinta.
