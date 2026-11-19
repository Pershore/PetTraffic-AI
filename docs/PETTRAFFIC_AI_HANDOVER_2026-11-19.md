# Pet traffic – perdavimo ataskaita (2026-11-19)

## Sesijos išvada

AI ciklas lapkričio 18 d. techniškai įvyko ir įrašė Control Core bei atmintį į D1, tačiau įrodymų kokybė liko nepakankama. Svarbiausias sisteminis incidentas – kelių GitHub Actions schedule paleidimų vėlavimas apie 9 val.; tiksli priežastis dar nepatvirtinta.

## Patvirtinta AI / D1 būsena

- Gyvas Worker /health 2026-11-19 08:00:13Z: Worker API ir D1 connected, Control Core schema connected, heartbeat site HTTP 200.
- Paskutinis AI ciklas: run_date=2026-11-18, started_at=15:45:13Z, completed_at=15:45:25Z, status=completed, ai_calls=5, error_code=null.
- Control Core: run_date=2026-11-18, status=needs_evidence, decision_json_status=valid, 4 evidence gaps; specialist statuses: analytics/topics/content-review=needs_evidence, technical-seo=reviewed.
- Memory updated_at=2026-11-18T15:45:25.164Z, tas pats ciklas; /health patvirtina agreguotą D1 readback.
- D1 diagnostikos artifact #14441572873 / run #44336957542 sukurtas 15:33:21Z – prieš AI ciklą 15:45Z. Jo agent_run=missing yra prieš-ciklo momentinė būsena, ne po-ciklo nesėkmė. Konkrečios spragų eilutės dar nepatikrintos.
- Nekartoti 2026-11-18 ciklo. Issue #145 lieka open, kol nėra recovery_confirmed ir visų specialistų pagrįstų rezultatų.

## Schedule incidentas

| Workflow | Cron UTC | Tikras schedule start 2026-11-18 UTC | Vėlavimas |
|---|---:|---:|---:|
| Site-check | 05:37 | 14:29:58 | ~8 val. 53 min. |
| Daily-suite | 06:10 | 15:32:01 | ~9 val. 22 min. |
| Google API connectivity | 06:57 | 16:11:28 | ~9 val. 14 min. |

- Daily-suite #44336724612: event=schedule, 3/3 job success, ~36 s. Sync #44336852000: source event=schedule, workflow ID 418322987, source run ID #44336724612; analytics/topic snapshot D1 write/readback success.
- Worker AI catch-up įvyko 15:45Z / 17:45 LT, po vėlyvo snapshot sync. Tai rodo, kad pati job trukmė nėra 9 val. vėlavimo priežastis.
- 2026-11-19 11:46 LT: naujų tos dienos site-check, Daily-suite ir connectivity schedule run dar nėra. Tai laukianti būsena prieš 13:20 AI ciklą, ne šios dienos AI nesėkmė.
- Tiksli GitHub schedule vėlavimo priežastis NEPATVIRTINTA; Actions administravimo nustatymai per dabartinę integraciją nematomi.

## Įvesties duomenų kokybė (Daily-suite #44336724612)

- GA4 laikotarpis 2026-11-11–17: 4 aktyvūs naudotojai, 2 nauji, 18 sesijų, 51 puslapių peržiūra, 0 organinių sesijų.
- GSC laikotarpis 2026-11-09–15: 0 parodymų, 0 paspaudimų, nėra užklausų ar puslapių eilučių; sitemap pateiktas, apdorojimas pending.
- Temų radaras: 27 unikalios RSS nuorodos, 7 temos. Tai viešų antraščių signalas, ne paieškų apimtys.
- Šie duomenys neleidžia išgalvoti paklausos ar tendencijų; `needs_evidence` yra tinkamas atsargus statusas, kol nėra papildomų įrodymų.

## PR / automatizacijos

- PR #288 draft: diagnostikos triggerio perkėlimas po D1 sync. Head CI buvo success; production deploy neatliktas. PR nekeičia AI ciklo ar evidence status.
- Issue #145 ir #248 lieka open.
- Esamas pagrindinis koordinatorius numatytas 11:45 LT, nepriklausoma patikra 12:00 LT, Worker AI 13:20 LT, post-cycle verifier 14:00 LT.
- 2026-11-18 14:00 LT verifier realiai startavo 15:05 LT ir baigė 15:17 LT, prieš vėlyvą 17:45 LT AI catch-up. Todėl jis negalėjo patvirtinti vėlyvo ciklo. 2026-11-19 verifier numatytas 14:00 LT; jei šiandienos schedule vėluos ir AI catch-up įvyks po verifier, būtina vėlesnė to paties run_date patikra (be antro AI ciklo).

## Kiti veiksmai

1. Po 13:20 LT tikrinti 2026-11-19 Worker /health: run_date, started_at, status, 5 AI calls, error_code, Control Core ir memory readback. Jei dar nėra eligible schedule snapshot, palikti LAUKIA – nekartoti ciklo.
2. Patikrinti tikrą 2026-11-19 Daily-suite event=schedule ir D1 source provenance/readback. Manual/push/workflow_run nelaikyti schedule įrodymu.
3. Po 14:00 LT verifier peržiūrėti jo rezultatą. Jei Daily-suite vėluos ir AI catch-up bus po verifier, patikrinti tą patį ciklą vėliau, nekurti antro.
4. Toliau tirti GitHub Actions schedule vėlavimą; tiksli priežastis lieka nežinoma, kol nepatikrinti repository Actions enablement nustatymai.
5. PR #288 nejungti aklai; jo paskirtis tik diagnostikos eiliškumas.

## Saugumo ribos

Šio audito metu nebuvo keistas kodas, Worker/D1 produkcija, DNS, secrets, permissions, billing, ARO Vet ar viešas turinys. Naujų mokamų paslaugų nėra. Issue #145 neuždarytas.


## 2026-11-19 11:46 LT – atnaujinta patikra

- Main HEAD `ba208461e8d07026dadeb35163a26119b2a5f83d`; paskutinis commit pakeitė tik work-log. PR #289 turi 2 sėkmingas patikras (static site-check ir Cloudflare Pages), bet lieka draft; nesujungtas.
- Gyvi puslapiai: homepage, keturi gidai, about, privacy, robots ir sitemap HTTP 200; netikras URL HTTP 404. Live-check #44336724612 patvirtino 12 vidinių URL ir 20 senų straipsnių 301. Sitemap turi 7 URL. Keturi gidai turi canonical/title/description/OG/Article + BreadcrumbList JSON-LD; homepage WebSite JSON-LD. About/privacy OG/JSON-LD trūksta; tai tik neblokuojanti galimybė. GA4 paleidžiamas tik po sutikimo.
- 2026-11-19 Daily-suite event=schedule nėra iki 09:45:13Z. Paskutinis tikras schedule #44336724612 – Nov 18 15:32:01Z, 3/3 job success (~36 s). Bridge 20h dedupe baigiasi Nov 19 11:32:01Z / 13:32 LT; šiuo metu jis dar aktyvus, todėl /pettraffic-run-daily-suite komentaras nebuvo siunčiamas – bridge atmestų.
- 2026-11-18 Control Center #44336851843 workflow_run success; D1 sync #44336852000 patvirtino schedule provenance ir abiejų analytics/topic snapshot write/readback. Site-check ir connectivity schedule vėlavo atitinkamai apie 8h53m ir 9h14m; Daily-suite apie 9h22m. Job trukmės trumpos, tiksli GitHub priežastis nepatvirtinta.
- Worker /health 09:45:13Z: Worker/D1 healthy, site 200. AI run 2026-11-18 completed 5 calls, error_code=null; Control Core needs_evidence, 4 spragos (3 insufficient_evidence, 1 other), 3 specialistai needs_evidence, technical-seo reviewed; memory readback updated 15:45:25.164Z, tas pats ciklas. 2026-11-19 ciklas iki 13:20 LT LAUKIA. Diagnostika #44485513822 08:11Z buvo prieš dienos ciklą, todėl jos missing nėra nesėkmės įrodymas.
- Control Center #44485441791 workflow_run success, artifact #14511010012; `recovery_confirmed=false`. Issue #145 lieka open.
- GA4 artifact #14442635651: 2026-11-11–17, 4 active, 18 sessions, 51 views, 0 organic. GSC 2026-11-09–15: 0 impressions/clicks, no query/page rows, sitemap pending. Topic radar #14442685485: 27 RSS links, 7 topics, not search volume.
- Lighthouse schedule #43915631789 (Nov 16) 10 HTML/JSON reports; dog-diarrhea mobile and vet-visit desktop/mobile show high TTFB/LCP outliers, TBT=0/CLS=0; no code regression proven. Next weekly audit Nov 23.
- `docs/WEEKLY_GROWTH_REVIEW.md` pasenęs ARO Vet produktų šaltinio leidimas pataisytas šio PR šakoje pagal dabartinį draudimą. Jokio viešo turinio ar produkcijos pakeitimo nėra.

## Toliau

1. Po 13:20 LT patikrinti vienintelį 2026-11-19 Worker AI ciklą; 14:00 LT esamas verifier.
2. Jei eligible Daily-suite schedule vis dar nėra, nekurti antro AI ciklo. Daily-suite bridge naudoti tik po 13:32 LT, jei dedupe pasibaigęs ir nėra kito vykstančio/sėkmingo run.
3. Issue #145 neuždaryti, kol `recovery_confirmed=true` ir specialistų įrodymai pakankami.


## 2026-11-19 – schedule incidento sprendimas ir atsarginio paleidimo pataisa

- **PATIKRINTA – vėlavimo vieta:** Daily-suite #44336724612, site-check #44324894236 ir Google API connectivity #44344302960 turėjo `created_at == run_started_at`; patys darbai truko atitinkamai apie 36 s, 23 s ir 21 s, nors buvo sukurti maždaug 9 val. po cron laiko. Tai rodo, kad vėlavimas įvyko iki runner/job pradžios, o ne vykdymo eilėje ar pačiame kode.
- **Šaltinis / ribotumas:** oficiali GitHub Actions dokumentacija nurodo, kad `schedule` yra best-effort, gali vėluoti didelės apkrovos metu ir gali būti praleistas. Tikroji vidinė GitHub priežastis šiai saugyklai nepasiekiama per turimą integraciją; repo pakeitimas negali priversti GitHub schedulerio sukurti trūkstamo `schedule` įvykio. Nuoroda: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- **ATLIKTA – PR #291:** sujungtas commit `7ff766701b1877ceacf145c7e8b44bdfd7a0f400`. `.github/workflows/dispatch-daily-suite.yml` dabar atskiria dabartinės UTC dienos 06:10 schedule nuo vakarykščio pavėluoto įvykio, išsaugo 60 min. grace, o schedule ir manual fallback deduplikuoja pagal UTC dieną. Ankstesnės dienos run nebegali blokuoti šiandienos atsarginio paleidimo.
- **Saugumo / kilmės vartai:** atsarginis paleidimas lieka tik `workflow_dispatch`; jo pranešimas aiškiai nurodo, kad tai nėra `event=schedule` įrodymas ir jis neatveria Worker AI vartų. Tikras suplanuotas run ir jo D1 provenance vis dar privalomi AI ciklui.
- **PATIKRINTA – testai:** PR site-check #44540850250 success; HTML/SEO/sitemap, dashboard JavaScript, Python compile ir 150 unit testų success. Po merge site-check #44541010333 (push) success; Control Center #44541010391 success; automatinis work-log #44541010359 success. Pakeisti tik workflow ir testas; svetainės turinys, Cloudflare Worker/D1, DNS, secrets, ARO Vet ir billing nepaliesti.
- **ATLIKTA – pagrindinis koordinatorius:** esama kasdienė Pet traffic priežiūros automatizacija atnaujinta, kad po grace ieškotų dabartinės UTC dienos workflow_dispatch, o vakarykščiai vėluojantys run neužblokuotų šiandienos fallback. Automatizacija enabled; kitas vykdymas 2026-11-20 11:45 Europe/Vilnius.
- **LAUKIA – realus fallback patvirtinimas:** šiandienos manual Daily-suite jau buvo sėkmingai paleistas iki PR merge, todėl papildomas live bridge dispatch sąmoningai nedarytas. Naujos taisyklės realus vykdymas bus tikrinamas kitame koordinatoriaus lange; nedubliuoti šiandienos duomenų rinkimo.
- **NEPATVIRTINTA – GitHub schedulerio atstatymas:** PR #291 sutvarko mūsų atsarginio paleidimo blokavimo klaidą, bet neištaiso GitHub platformos `schedule` įvykių pristatymo vėlavimo. Jei tikras schedule ir toliau vėluos, ilgalaikiam patikimam suplanuotam AI paleidimui reikės GitHub platformos pusės sprendimo arba atskiro, saugiai autentifikuoto išorinio schedulerio. Jokio naujo mokamo serviso, tokeno ar secret neįdiegta.
- **AI būklė nepasikeitė:** paskutinis Worker AI ciklas lieka 2026-11-18 `needs_evidence`; 2026-11-19 ciklas nebuvo paleistas, nes tikros schedule provenance trūko. Issue #145 lieka open.

