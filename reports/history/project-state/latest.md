# PetTraffic AI – paskutinė patikrinta projekto būsena

- Atnaujinta: 2026-11-19T10:19:55Z
- Būsena: **REIKIA DĖMESIO**
- Main HEAD po audito žurnalo įrašo: `34ef34f594b39b66b61290ac63c72e20ecc9eb05` (audito pradžioje buvo `00d8bee31ffc7fb9f0aec2c726a20d641f46357e`).
- Control Center run: [44485441791](https://github.com/Pershore/PetTraffic-AI/actions/runs/44485441791)
- Worker D1 diagnostics run: [44485513822](https://github.com/Pershore/PetTraffic-AI/actions/runs/44485513822)

## Patikros rezultatai

- **PATIKRINTA** – GitHub main HEAD yra `00d8bee`; naujausi commit: `00d8bee` ir `ec23c40`.
- **PATIKRINTA** – Daily-suite paskutinis tikras `event=schedule`: [#44336724612](https://github.com/Pershore/PetTraffic-AI/actions/runs/44336724612), 2026-11-18 15:32:01 UTC, success. Analytics, topic-radar ir live-check darbai visi success.
- **LAUKIA** – 2026-11-19 Daily-suite `event=schedule` paleidimo iki 10:19 UTC nematyti. Workflow faile yra cron `10 6 * * *`, bet cron konfigūracija nėra paleidimo įrodymas.
- **PATIKRINTA** – Po darbo žurnalo įrašo main šakoje site-check push run [#44505988093](https://github.com/Pershore/PetTraffic-AI/actions/runs/44505988093) baigėsi success 2026-11-19 10:28:46 UTC; tai nėra schedule įrodymas.
- **PATIKRINTA** – Site-check paskutinis tikras `event=schedule`: [#44324894236](https://github.com/Pershore/PetTraffic-AI/actions/runs/44324894236), 2026-11-18 14:29:58 UTC, success. Naujausias push patikrinimas [#44501750138](https://github.com/Pershore/PetTraffic-AI/actions/runs/44501750138) 2026-11-19 10:01:26 UTC, success.
- **LAUKIA** – 2026-11-19 Site-check `event=schedule` įvykio iki 10:19 UTC nematyti. Workflow faile yra cron `37 5 * * *`.
- **PATIKRINTA** – Lighthouse paskutinis tikras `event=schedule`: [#43915631789](https://github.com/Pershore/PetTraffic-AI/actions/runs/43915631789), 2026-11-16 17:10:54 UTC, success. Tai savaitinis pirmadienio workflow; kitas suplanuotas langas – 2026-11-23.
- **PATIKRINTA** – Control Center [#44485441791](https://github.com/Pershore/PetTraffic-AI/actions/runs/44485441791) ir Worker D1 diagnostika [#44485513822](https://github.com/Pershore/PetTraffic-AI/actions/runs/44485513822) sėkmingi. Control Center paleidžiamas pagal įvykius; atskiro `event=schedule` jam nereikia.
- **PATIKRINTA** – Worker/D1 Control Center ataskaitoje pažymėti GERAI; svetainės heartbeat buvo sėkmingas maždaug 11 min. iki 08:11 UTC ataskaitos. Tiesioginis `/health` ir viešos svetainės HTTP atsakas šiame vykdyme nepriklausomai nepatvirtintas: išorinės užklausos ir DNS iš vykdymo aplinkos neveikė.
- **PATIKRINTA** – 2026-11-19 read-only D1 diagnostika: AI agento įrašo nėra, `ai_calls=0`, `error_code=null`, `report_json_status=missing_or_invalid`. Analytics, topics, technical-seo ir content-review specialistų ataskaitos – missing; Control Core – missing. Atmintis yra, atnaujinta 2026-11-18T15:45:25Z; paskutinis atminties ciklas 2026-11-18, būsena `needs_evidence`, spragos `insufficient_evidence` ir `search_volume_not_available`. 2026-11-19 D1 source snapshot įrašų skaičius: analytics=0, topic=0, control_center=0, recommendation=0.
- **LAUKIA** – AI ciklo 13:20 Lietuvos laiku langas šios patikros metu dar nebuvo prasidėjęs; dabartinio ciklo nebuvimas nelaikomas nesėkme iki šio lango.
- **PATIKRINTA** – naujausi išsaugoti analytics ir topic-radar artefaktai yra iš 2026-11-18 Daily-suite paleidimo. GA4 artefaktas [#14442635651](https://github.com/Pershore/PetTraffic-AI/actions/runs/44336724612): laikotarpis 2026-11-11–2026-11-17, 4 aktyvūs naudotojai, 18 sesijų, 51 puslapių peržiūra, 0 organinės paieškos sesijų. GSC laikotarpis 2026-11-09–2026-11-15: 0 parodymų, 0 paspaudimų; sitemap pateiktas 2026-11-10, Google dar neatsisiuntė ir apdorojimas laukia. Šie skaičiai rodomi tik pagal šį autorizuotą artefaktą ir jo intervalus.
- **PATIKRINTA** – topic-radar artefaktas [#14442685485](https://github.com/Pershore/PetTraffic-AI/actions/runs/44336724612): 27 unikalios viešų RSS antraščių nuorodos, 7 temų grupės. Tai antraščių stebėsena, ne Google paieškų apimtis ar lankomumo matas. Analytics ir topic-radar istorijos failai išsaugoti iki 2026-11-18.
- **PATIKRINTA** – atviri 7 draft PR: #288, #280, #267, #266, #264, #263, #261. Atviri issue #145 (centrinis automatizacijų įspėjimas) ir #248 (autonominio valdymo plokštuma).

## Problemos ir rekomendacijos

- **LAUKIA** – Daily-suite ir site-check 2026-11-19 tikrų schedule įvykių. Push, pull_request, workflow_dispatch ar workflow_run jų nepakeičia.
- **LAUKIA** – AI ciklo po 13:20 Lietuvos laiku patikra: agent_run, ai_calls, error_code, specialistų rezultatai, Control Core, memory/evidence ir rekomendacijos.
- **PLANUOJAMA** – tiesioginį viešos svetainės HTTP ir Worker `/health` pakartoti, kai vykdymo aplinkoje bus pasiekiamas išorinis tinklas.
- **PLANUOJAMA** – stebėti Search Console sitemap apdorojimą; pakartotinai neteikti, kol nėra pagrindo.
- **PATIKRINTA** – kodo ar workflow defekto, kurį būtų saugu taisyti atskira šaka pagal šiuos įrodymus, nenustatyta. PR nekurtas ir niekas nesujungta.

## Nekeičiamos saugumo ribos

- ARO Vet svetainės, kodo ir infrastruktūros nekeisti.
- Svetainės turinio automatiškai nepublikuoti; būtinas vartotojo patvirtinimas.
- Jokių mokamų API ar paslaugų; biudžetas 0 €/mėn.
- Nekeisti DNS, Cloudflare production Worker/D1/secrets ar paskyrų teisių.
- AI rekomendacijos yra patariamosios; modelio išvestys nesuteikia vykdymo teisių.
- Niekada neprašyti slaptažodžių, MFA kodų ar slaptų raktų.

> Tik agreguotos procesų būsenos ir rekomendacijų santrauka; be lankytojų lygmens duomenų, žalių paieškos užklausų ar paslapčių.
