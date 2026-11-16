# PetTraffic AI – paskutinė patikrinta projekto būsena

- Nepriklausomas auditas: 2026-11-16T10:23:45+00:00 (read-only)
- Būsena: **REIKIA DĖMESIO**
- Main HEAD: `6ae86dd9e95fe58602b8e7d2e5e049f2d9523979`
- Paskutinis Control Center run: `43745604154` (`workflow_run`, success, 2026-11-15T18:14:23Z); šiame audite naujo event-driven Control Center run nebuvo.
- Šis įrašas yra nepriklausomas audito papildymas, ne nauja Control Center sugeneruota ataskaita.

## Nepriklausomas auditas 2026-11-16 12:23 LT

- **PATIKRINTA – schedule:** iki 12:23 LT nerasta 2026-11-16 `event=schedule` paleidimų Daily-suite, site-check ar Lighthouse. Paskutiniai tikri schedule: Daily-suite [#43721211747](https://github.com/Pershore/PetTraffic-AI/actions/runs/43721211747) ir site-check [#43716344579](https://github.com/Pershore/PetTraffic-AI/actions/runs/43716344579), abu 2026-11-15 ir success, bet vėlavo apie 7 val. 42 min. / 7 val. 19 min. Lighthouse cron pirmadieniais 07:27 UTC; event=schedule įrašo nėra. Naujausias Lighthouse [#43745229308](https://github.com/Pershore/PetTraffic-AI/actions/runs/43745229308) buvo push. Control Center yra event-driven; paskutinis [#43745604154](https://github.com/Pershore/PetTraffic-AI/actions/runs/43745604154) success, atskiro schedule nereikalaujama.
- **PATIKRINTA – svetainė:** paskutinis gyvas patikrinimas [#43740434516](https://github.com/Pershore/PetTraffic-AI/actions/runs/43740434516) 2026-11-15 17:19:17 UTC success: 12 vidinių URL, sitemap, robots.txt, 404 ir 20 senų 301; D1 task readback verified. Tiesioginis šios dienos HTTP patikrinimas šiame konteineryje nepavyko dėl DNS resolve klaidos; dabartinė HTTP būsena šiame audite **NEPATVIRTINTA**.
- **PATIKRINTA – Worker/D1:** Worker cron diagnostika [#43740245726](https://github.com/Pershore/PetTraffic-AI/actions/runs/43740245726) 2026-11-15 success; Cloudflare cron `*/15 * * * *` ir `20 10,11 * * *` patvirtinti; D1, Control Core schema, site ir DB healthy, heartbeat 17:15:13.439Z → 17:30:13.485Z. Vėlesnis D1 sync [#43745654612](https://github.com/Pershore/PetTraffic-AI/actions/runs/43745654612) success, 2 įvykių write/readback. Dabartinis /health nepasiektas, todėl dabartinė Worker būklė **NEPATVIRTINTA**.
- **LAUKIA – AI:** 2026-11-16 ciklas numatytas 13:20 LT; 12:23 LT dar nebuvo laikas jį vertinti kaip stale. Paskutinis žinomas 2026-11-15 10:20 LT ciklas: completed, 5 AI calls, error_code=null; Control Core needs_evidence, memory present, 8 evidence gaps, 2 recommendations. Paskutinės žinomos specialistų būsenos (senas ciklas): analytics=error, topics=no data, technical-seo=monitor, content-review=invalid_json. Po naujo deploy ciklas dar **NEPATVIRTINTAS**; nekartoti rankiniu būdu dėl run_date idempotency.
- **PATIKRINTA – analitika:** GA4 2026-11-08–14: 7 aktyvūs, 7 nauji, 24 sesijos, 88 peržiūros, 0 patvirtintų organinių sesijų. GSC 2026-11-06–12: 0 parodymų, 0 paspaudimų, CTR 0,0 %, pozicija 0,0; užklausų / puslapių eilučių nėra; sitemap pateiktas, pending. Šaltiniai: [Daily-suite run #43721211747](https://github.com/Pershore/PetTraffic-AI/actions/runs/43721211747), [naujesnis push snapshot #43745229251](https://github.com/Pershore/PetTraffic-AI/actions/runs/43745229251).
- **PATIKRINTA – temų radaras:** [artefaktas #14164462613](https://github.com/Pershore/PetTraffic-AI/actions/runs/43721211747/artifacts/14164462613): 31 unikali RSS antraščių nuoroda, 7 temos, 0/7 tuščių. Tai viešų RSS antraščių stebėsena, ne paieškų apimčių matas.
- **PATIKRINTA – Lighthouse:** [artefaktas #14173977237](https://github.com/Pershore/PetTraffic-AI/actions/runs/43745229308/artifacts/14173977237): 10 ataskaitų; desktop performance 100; mobile homepage 81, TBT 769 ms, LCP 1,70 s, CLS 0; kiti mobile puslapiai 98–99. Vienas matavimas – reikia pakartoti prieš keičiant kodą.
- **PATIKRINTA – istorija:** automation-history turi analytics, topic-radar, Lighthouse, Control Center ir recommendations snapshot failus už 2026-11-15; D1 sync write/readback patvirtintas.
- **PARUOŠTA – PR #253:** naujausio head site-check ir Termux bridge CI success; PR atviras, nesusijungtas, production nepakeista. PR šaka prieštarauja `main` ARO Vet produkto šaltinio leidimui: PR nurodo pašalinti visus ARO Vet elementus, o `main` leidžia aktualius produktus ir tiesiogines nuorodas. Nejungti, kol ši kryptis nesuderinta.
- **PATIKRINTA – atviri issue:** [#145](https://github.com/Pershore/PetTraffic-AI/issues/145) ir [#248](https://github.com/Pershore/PetTraffic-AI/issues/248) tebėra open.
- **ATLIKTA:** tik read-only patikros ir šios būsenos dokumentavimas. Jokio kodo, PR šakų, production Worker/D1, DNS, secrets, ARO Vet, viešo turinio, paskyrų teisių ar billing pakeitimo.

**Kitas veiksmas:** po 2026-11-16 13:20 LT patikrinti AI ciklą, specialistų išvestis, Control Core memory/evidence ir D1 readback; vėliau pakartotinai patikrinti tikrus `event=schedule` įvykius.

## Ankstesnis Control Center snapshot (2026-11-15T18:14:37Z; istorinis)

Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje.

## Kitas veiksmas

Spręsti pirmą aptiktą problemą: AI agentai + control-core atmintis (stale). Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-15.

## Patvirtinti procesai

- GA4, temų radaras ir svetainės stebėjimas: Paskutinis paleidimas sėkmingas.
- Centrinės API sinchronizavimas: Paskutinis paleidimas sėkmingas.
- Centrinis valdymo centras: Paskutinis paleidimas sėkmingas.
- Debesijos read-only užduočių vykdytojas: Paskutinis debesijos užduoties vykdymas sėkmingas.
- Cloudflare Worker + D1: Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš 14 min.

## Problemos

- **AI agentai + control-core atmintis** (stale): Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-15. – https://pettraffic-control-api.pauliusgrubliauskis.workers.dev/health

## Laukiančios patikros

- Lighthouse auditas: Workflow atnaujintas 2026-11-15 18:10 UTC po paskutinio suplanuoto laiko; laukiama kito ciklo.

## AI agentų ir atminties patikra

- Būsena: **stale** – Po 13:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: 2026-11-15.
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

