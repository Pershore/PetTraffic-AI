# Pet traffic – perdavimo ataskaita (2026-11-21)

## Naujausia patikrinta būsena

- **Main:** `a5f0a395f5a215fefd06662eac43a321a3298f50`; Cloudflare Pages production check-run patvirtino deploy success pagal šį commit 2026-11-20 14:49 UTC.
- **Gyva svetainė:** Daily-suite live-check #44895862888 success: 12 vidinių URL, sitemap, robots, 404 ir 20 istorinių 301 redirectų. Tiesioginis naršyklės fetch per šią aplinką neprieinamas, todėl remiamasi realiu GitHub Actions HTTP monitoriumi.
- **Daily-suite:** 2026-11-21 06:10 UTC schedule po 60 min. grace neįvyko. Saugus bridge #44895852313 paleido #44895862888 kaip `workflow_dispatch`; visi 3 job success. Tai fallback, ne schedule įrodymas ir neatveria Worker AI vartų.
- **Analytics:** GA4 2026-11-14–20: 2 aktyvūs, 2 nauji naudotojai, 2 sesijos, 2 peržiūros, 0 organinių sesijų. GSC 2026-11-12–18: 0 parodymų, 0 paspaudimų; sitemap submitted/pending nuo 11-10, penki prioritetiniai URL dar nežinomi Google. Duomenys prieinami; nulis nėra API klaida.
- **Topic radar:** 30 unikalių viešų RSS nuorodų, 7 temos; tai antraščių stebėsena, ne paieškų apimtis.
- **D1:** sync #44896017766 tiksliai apdorojo source run #44895862888, 2 privatumo filtruoti eventai turėjo sėkmingą D1 write/readback. Diagnostikos artifact #14704490608 patvirtina analytics_snapshot=1 ir topic_snapshot=1 iš to paties run ID.
- **Worker AI:** diagnostika #44896086631 10:48:43Z: šiandienos agent run missing, 0 calls, 4 specialistai missing, Control Core missing, memory paskutinį kartą atnaujinta 2026-11-20T15:30:36.388Z. Kadangi patikra iki 13:20 LT, būsena WAITING; rankiniu būdu ciklo nekviesti.
- **Lighthouse:** paskutinis sėkmingas auditas #43915631789 (11-16 17:10Z), 10 HTML/JSON. Dog mobile LCP 1.855→9.779 s, vet desktop 0.536→8.078 s, vet mobile 1.852→5.548 s; TTFB išaugo, TBT=0, CLS=0, transfer size stabilus. Tai server-response / render-delay anomalija, ne įrodyta kodo regresija. Per 7 d. yra sėkmingas auditas, todėl papildomas dispatch nereikalingas.
- **SEO:** robots Allow:/, sitemap 7 URL; 4 gidai turi title/description/canonical/OG/JSON-LD/H1. About/privacy trūksta OG; homepage Twitter image nesutampa su og:image; canonical/sitemap tebenaudoja .html. PR #298 preview deploy success, bet 5 commits behind main ir preview turinys / redirect grandinės nepatvirtintos; PR draft, nesujungtas.
- **Automatikų incidentas:** bridge #44895852313 sukėlė Control Center #44895876114 prieš Daily-suite pabaigą; bridge #44896007399 sukėlė #44896025044 prieš D1 sync pabaigą. Latest snapshot #44896025044 laikinai rodė sync in_progress ir liko pasenęs po sync completion.
- **PR #299:** draft, šaka `fix/control-center-bridge-trigger-20261121`; pašalina bridge iš Control Center workflow_run trigerių, prideda workflow_run deduplikaciją bridge Control Center komandai ir regresijos testą. Jokių produkcijos pakeitimų.

## Pirmas neužbaigtas veiksmas

Patikrinti PR #299 visus GitHub Actions check/job rezultatus. Jei bent vienas pending, failed ar neaiškus – nemerginti. Jei visi success, užbaigti PR, po merge patikrinti main site-check ir įsitikinti, kad Control Center nebesuveikia nuo bridge event, o lieka event-driven po tikrųjų stebimų workflow.

## Toliau

1. Po 13:20 LT patikrinti vienintelį 2026-11-21 Worker AI ciklą per `/health`: run_date, started_at, status, ai_calls, error_code, keturi specialistų raportai, Control Core, evidence_gaps ir D1 memory readback. Naudoti esamą 14:00 LT verifier; nekartoti ciklo.
2. 2026-11-22 Daily-suite patikrinti tikrą `event=schedule` po 06:10 UTC + 60 min. grace. Jei jo nėra, tik tada naudoti jau įdiegtą bridge ir atskirti fallback nuo schedule įrodymo.
3. Po kito tikro schedule + sync patikrinti Control Center ataskaitą ir D1 readback. automation-history latest.md/latest.json rankiniu būdu nekeisti.

## Saugumo ribos

Nekeisti DNS, Cloudflare Worker/D1 production, secrets, repo permissions, billing, ARO Vet ar viešo turinio. Jokio mokamo serviso, savavališko shell, naujų priklausomybių ar AI ciklo pakartojimo.
