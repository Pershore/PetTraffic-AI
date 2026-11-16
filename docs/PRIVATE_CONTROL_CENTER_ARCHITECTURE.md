# Privataus Pet traffic valdymo centro architektūra

Atnaujinta: 2026-11-16

## Tikslas

Sukurti patogų privatų valdymo centrą, kuris leidžia savininkui matyti gyvą Pet traffic architektūrą, procesus, agentų būsenas ir leisti tik iš anksto apibrėžtas saugias komandas. Vieša Pet traffic svetainė ir dabartinis /control/ puslapis lieka vieši ir READ-ONLY.

## Esama būklė

- Vieša svetainė ir /control/ naudoja tą patį Cloudflare Pages projektą pettraffic-ai.
- /control/ renka viešus GitHub Actions metaduomenis, Worker /health, HEAD svetainės būklę ir privacy-filtered istorijos agregatus.
- /control/ kopijuoja fiksuotas komandų eilutes; jis nevykdo POST, workflow dispatch, D1 write ar Worker task API kvietimų.
- Worker /health atskleidžia tik agreguotus sveikatos metaduomenis; CORS leidžia tik https://pettraffic-ai.pages.dev. CORS nėra autentifikacija.
- Worker /v1/tasks* tyčia lieka išjungtas, kol nėra atskiros patikrintos tapatybės ir autentifikuoto valdymo kelio.
- noindex,nofollow riboja paieškos indeksavimą, bet nėra prieigos kontrolė.

## Rekomenduojama architektūra

### 1 etapas – atskira privati Pages aplikacija

Sukurti atskirą Cloudflare Pages projektą tik valdymo UI, atskiru pages.dev hostname. Viešo Pet traffic Pages projekto, DNS ir viešo turinio nekeisti.

Cloudflare Access turi saugoti ir production pages.dev hostname, ir preview deployments hostname; jei kada nors atsiranda custom domain, jam reikalinga atskira Access application/policy. Vien preview apsauga neapsaugo production pages.dev hostname, ir atvirkščiai.

Leisti prisijungti tik savininko tapatybei (konkreti IdP/email allowlist taisyklė nustatoma Access). Nenaudoti bendro slaptažodžio, URL slaptumo ar noindex kaip autentifikacijos.

Oficiali Cloudflare dokumentacija:
- Pages pages.dev apsauga ir atskiros preview politikos: https://developers.cloudflare.com/pages/platform/known-issues/
- Access su Workers ir hostname/patvirtinimo galimybės: https://developers.cloudflare.com/workers/configuration/cloudflare-access/
- Zero Trust kainodara: https://www.cloudflare.com/plans/zero-trust-services/

Cloudflare Zero Trust Free šiuo metu skelbia $0 iki 50 naudotojų. Kainodarą ir limitą reikia patikrinti prieš įjungimą. Jokio mokamo plano ar billing neaktyvuoti.

### 2 etapas – privati read-only duomenų prieiga

Pirmame etape UI tik skaito:
- GitHub PR, Issues, Actions runs ir job metadata.
- Viešos svetainės HEAD/health ir sitemap patikrų santraukas.
- Worker health ir privatumo filtruotas D1 diagnostikos santraukas.
- GA4/GSC ir RSS tik agreguotus, jau privatumo filtruotus snapshot.
- AI agentų run_date, status, ai_calls, error_code, specialistų būsenas/evidence-gap kodus, Control Core status ir D1 memory timestamps.

API srautas turi eiti per server-side BFF arba autentifikuotą Worker. Naršyklės kodas negali turėti GitHub/Cloudflare/Google raktų. Worker privalo tikrinti Cf-Access-Jwt-Assertion / Access JWT: parašą pagal JWKS, issuer, audience, expiry ir savininko tapatybės allowlist. CORS tikrinimas nėra saugumo kontrolė.

### 3 etapas – fiksuotos owner-only komandos

Tik po read-only etapo ir atskiro saugumo review:
- Priimti tik griežtai apibrėžtą JSON payload su task_type, target, request_id ir ribotais parametrais.
- Leisti tik allowlist task types; pirmasis vienintelis task tipas – check_site.
- Worker tikrina Access JWT ir owner identity; atskiros OIDC dispatcher/runner tapatybės turi tik mažiausias reikalingas teises.
- Runner vykdo tik fiksuotą versijuotą handlerį; jokio shell/eval/arbitrary command/model-generated code ar vartotojo pateikto kodo.
- Taikyti idempotency key, rate-limit, request expiry, audit metadata ir D1 write/readback.
- Po execution atskirai perskaityti D1 būseną ir parodyti task ID, status, exit code bei saugų rezultatą.
- PR merge, Worker deploy, DNS, viešo turinio publikavimas, billing ir paskyrų/security pakeitimai lieka už atskirų leidimų vartų.

## Saugumo ribos ir testų priėmimas

Prieš įjungiant privatų valdymą būtina patikrinti:
- Anoniminis vartotojas gauna Access login/deny; savininkas gauna prieigą.
- JWT invalid signature, netinkamas aud/iss, expiry, netinkama tapatybė ir trūkstamas tokenas atmetami.
- Viešas origin, CORS ir tiesioginis Worker URL neapeina autorizacijos.
- Neteisinga schema, neleidžiamas task type, per didelis payload, pakartotas request_id ir expiry atmetami.
- Tik fiksuotas handleris; nėra shell/exec kelių; success/failure/timeout ir D1 readback testuojami.
- Preview aplinkos atskirai apsaugotos; nėra paslapčių browser bundle ar public HTML.
- Kaina patvirtinta $0/mėn.; billing neįjungiamas.

## Įgyvendinimo būsena

PARUOŠTA kaip architektūros pasiūlymas. Šio dokumento sukūrimas nekeičia Cloudflare Pages projektų, DNS, Access, Worker/D1, GitHub secrets, paskyrų teisių ar billing. Jokia privati aplikacija dar nesukurta ir jokios Access politikos neįjungtos. Tam reikalingas atskiras konkretus leidimas.
