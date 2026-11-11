# PetTraffic AI automatizavimo prijungimas

Šiame faile aprašyti tik tie prisijungimai, kurių negalima saugiai sukurti vien iš GitHub kodo. Niekada nedėkite slaptažodžių, API raktų ar JSON raktų į Git failus.

## 1–2. GA4 ir Google Search Console

Repozitorijoje yra read-only ataskaitos programa: `agent/analytics_report.py`, o jos kasdienį paleidimą aprašo `.github/workflows/analytics-snapshot.yml`.

Vieną kartą reikia:

1. Google Cloud projekte įjungti Google Analytics Data API ir Google Search Console API.
2. Sukurti paslaugos paskyrą ir JSON raktą.
3. GA4 nuosavybėje suteikti paslaugos paskyros el. paštui Viewer (skaitymo) prieigą.
4. Search Console svetainės nuosavybėje pridėti tą pačią paskyrą su ribota skaitymo prieiga.
5. GitHub repo Settings → Secrets and variables → Actions pridėti:
   - Secret: `GOOGLE_SERVICE_ACCOUNT_JSON` – visas paslaugos paskyros JSON turinys.
   - Variable: `GA4_PROPERTY_ID` – skaitinis GA4 nuosavybės ID (ne matavimo ID, kuris prasideda G-).
   - Variable: `GSC_SITE_URL` – tikslus patvirtintos nuosavybės adresas, pvz. `https://pettraffic-ai.pages.dev/`.

Darbo eiga renka tik agreguotus skaičius: aktyvius naudotojus, sesijas, puslapių peržiūras ir Search Console užklausų paspaudimus / parodymus. Ji neidentifikuoja atskirų lankytojų. Jei nustatymų nėra, ataskaita aiškiai pažymi, kad duomenys neprijungti.

## 3. Temų tyrimas ir straipsnių rengimas

`agent/topic_radar.py` renka viešų Google News RSS antraščių rinkinį lietuviškomis augintinių temomis. Kasdienė GitHub Actions darbo eiga išsaugo Markdown ataskaitą 30 dienų.

Svarbu: naujienų antraštės nėra Google paieškų apimtys. Straipsnio publikavimui būtina patikrinti pirminius veterinarinius šaltinius ir faktus. Visiškai automatinis AI straipsnių generavimas per API neįjungtas, nes tam reikėtų papildomo mokamo modelio API rakto ir atskiro biudžeto patvirtinimo.

## 4. Aro Vet reklama ir matavimas

Svetainėje esančios nuorodos pažymėtos kaip reklama. `site/assets/site.js` registruoja agreguotą `ad_click` įvykį GA4 tik tada, kai lankytojas sutiko su analitika.

Šis įvykis rodo paspaudimus, o ne pardavimus ar pajamas. Komisiniai, partnerystė, nuolaidos ir prekių likučiai negali būti teigiami, kol nėra atskiro patvirtinto susitarimo ar patikimų duomenų.

## 5. Cloudflare Pages publikavimas – patikrinta

2026-11-11 vartotojo pateikta Cloudflare Pages ekrano nuotrauka patvirtino:
- Cloudflare Pages GitHub integracija veikia.
- Automatic deployments yra įjungti.
- Production šaka yra `main`.
- Gamybinis domenas: `pettraffic-ai.pages.dev`.
- Projekto pakeitimų šakos kuriamos kaip Preview deploy.

Todėl atskiro Wrangler Direct Upload ar antro publikavimo mechanizmo kurti nereikia. Pakeitimai šakoje `content/nov-2026-articles-ads` skirti peržiūrai; jie nepakeičia Production, kol nesujungiami į `main`.

Statinio projekto build output katalogas turi būti `site`; build command gali būti tuščias, jei Cloudflare projekto nustatymuose tai jau patvirtinta.

## Sauga

- Niekada neįkelti Google JSON rakto, Cloudflare API tokeno ar kitų paslapčių į repo.
- Analitikos prieigos yra tik skaitymo.
- Į `main` sujungti pakeitimus ir publikuoti produkcijoje tik po PR peržiūros.
