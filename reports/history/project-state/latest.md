# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-18T10:52:35+00:00
- Būsena: **REIKIA DĖMESIO**
- GitHub run: 44289410034
- Šaltinio commit: a5d6c51ac16e5aae0ce3d3f0441c14235002706f

## Paskutinis patikrintas etapas

Nepriklausoma patikra: Control Center #44288823686 success, D1 sync #44288897205 success, read-only Worker diagnostika #44288897470 success. Po work-log commit papildomas site-check push #44289410034 taip pat success. Main HEAD nepasikeitė nuo 3aaf95c.

## Kitas veiksmas

1. Peržiūrėti draft [PR #288](https://github.com/Pershore/PetTraffic-AI/pull/288): CI praėjo, bet PR nesujungtas.
2. Sulaukti 2026-11-18 13:20 LT AI ciklo ir po jo tikrinti specialistus, Control Core bei memory readback.
3. Stebėti tikrus Daily-suite ir site-check `event=schedule` paleidimus; 2026-11-18 tokių įvykių dar nėra.

## Schedule įvykiai – patvirtinti pagal event=schedule

- **Daily-suite:** paskutinis #44119444026, 2026-11-17 15:53:16 UTC, 3/3 job success. 2026-11-18 schedule įvykio nėra. Cron konfigūracija: kasdien 06:10 UTC.
- **Site-check:** paskutinis #44107609945, 2026-11-17 14:50:56 UTC, success. 2026-11-18 schedule įvykio nėra. Naujausias push #44289410034 success nėra schedule. Cron konfigūracija: kasdien 05:37 UTC.
- **Lighthouse:** paskutinis #43915631789, 2026-11-16 17:10:54 UTC, success; 21 ataskaitos failas išsaugotas. Savaitinis cron pirmadieniais 07:27 UTC; kitas numatytas 2026-11-23.
- **Control Center:** #44288823686 success, event-driven `workflow_run`; atskiro schedule nereikia.

## Worker / D1 / heartbeat

- Control Center #44288823686 nurodė Worker API ir D1 healthy; svetainės heartbeat buvo prieš 3 min. ataskaitos sudarymo metu.
- D1 sync #44288897205 success; du privatumo filtruoti įvykiai įrašyti ir perskaityti atgal.
- Tiesioginis HTTP GET iš šios vykdymo aplinkos nepatvirtintas dėl DNS resolution klaidos; remiamasi GitHub live-check ir Control Center ataskaitomis.

## AI ciklas ir Control Core

- Worker diagnostika #44288897470 (2026-11-18 10:48:54 UTC): `agent_run=missing`, `ai_calls=0`, `error_code=null`; tai patikros metu dar neįvykęs 13:20 LT ciklas, ne įrodymas apie nesėkmingą vykdymą.
- Visi specialistai: `missing`; šiandienos Control Core įrašas: `missing`.
- Memory: yra; atnaujinta 2026-11-17T12:00:21.622Z; paskutinė būsena `needs_evidence`; kodai `insufficient_evidence` ir `other`.
- Diagnostika naudojo 7 SELECT-only D1 užklausas; jos pačios nieko neįrašė.

## Diagnostikos ir sync eiliškumo problema

- Diagnostika #44288897470 baigėsi 10:48:54 UTC, o sync #44288897205 – 10:49:01 UTC.
- Todėl diagnostika dar nematė naujausių Control Center #44288823686 ir recommendation įrašų; naujausias matytas šaltinio run ID buvo #44285662210.
- **PARUOŠTA:** [PR #288](https://github.com/Pershore/PetTraffic-AI/pull/288) perkelia read-only diagnostiką po sėkmingo snapshot sync.
- PR CI: [site-check #44288811752](https://github.com/Pershore/PetTraffic-AI/actions/runs/44288811752), [sync tests #44288811926](https://github.com/Pershore/PetTraffic-AI/actions/runs/44288811926), [Cloudflare validation #44288811938](https://github.com/Pershore/PetTraffic-AI/actions/runs/44288811938) – visi success; production deploy skipped. PR lieka draft ir nesujungtas.

## Išsaugoti snapshot duomenys

- GA4 artefaktas #44119444026, laikotarpis 2026-11-10–16: 9 aktyvūs naudotojai, 9 nauji, 26 sesijos, 90 puslapių peržiūrų; Direct 15, AI Assistant 11, organinės sesijos 0.
- GSC artefaktas #44119444026, laikotarpis 2026-11-08–14: 0 parodymų, 0 paspaudimų, CTR 0,0 %, vidutinė pozicija 0,0; užklausų ir puslapių eilučių nepateikta, sitemap laukia apdorojimo.
- Temų radaras: 2026-11-17 15:53 UTC, 29 unikalios viešų RSS antraščių nuorodos, 7 temos; tai nėra paieškų apimtys.
- Lighthouse: paskutinis savaitinis artefaktas #43915631789; silpniausi našumo balai dog-diarrhea mobile 55, vet-visit desktop 55 ir mobile 60; accessibility, best practices ir SEO 100.

## Atviri PR ir issue

- 7 atviri draft PR: #288, #280, #267, #266, #264, #263, #261. GitHub API visiems grąžino `mergeable=false`; automatinio merge neatlikta.
- #264 keičia viešus canonical URL ir lieka be atskiro savininko patvirtinimo.
- #261 ir #263 – susieti schedule provenance pakeitimai; #267 – missing analytics metrics pataisa.
- Atviri issue: [#145](https://github.com/Pershore/PetTraffic-AI/issues/145) – automation alert; [#248](https://github.com/Pershore/PetTraffic-AI/issues/248) – secure task control plane.

## Nekeičiamos saugumo ribos

- ARO Vet svetainės, kodo ir infrastruktūros nekeisti be atskiro leidimo.
- Svetainės turinio automatiškai nepublikuoti; būtinas vartotojo patvirtinimas.
- Jokių mokamų API ar paslaugų be atskiro biudžeto patvirtinimo.
- Nekeisti DNS, Cloudflare teisių ar produkcinės infrastruktūros be atskiro patvirtinimo.
- AI rekomendacijos yra patariamosios; modelio išvestys nesuteikia vykdymo teisių.

> Tik agreguotos procesų būsenos ir rekomendacijų santrauka; be lankytojų lygmens duomenų, žalių paieškos užklausų ar paslapčių.
