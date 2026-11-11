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

## 5. Cloudflare Pages publikavimas

Rekomenduojamas kelias šiam statiniam projektui – Cloudflare Pages Git integracija su GitHub:
- Repository: `Pershore/PetTraffic-AI`
- Production branch: `main`
- Build command: tuščias (statiniam HTML projektui build žingsnio nereikia)
- Build output directory: `site`

Jei Git integracija jau įjungta, Cloudflare automatiškai sukuria preview deploy kitoms šakoms ir production deploy po pakeitimų `main`. Jei integracija dar neįjungta, ją reikia vieną kartą susieti Cloudflare dashboarde. Nenaudokite Wrangler Direct Upload workflow nepatikrinę projekto tipo: Git-integrated Pages projektas ir Direct Upload turi skirtingą diegimo kelią.

## Sauga

- Niekada neįkelti Google JSON rakto, Cloudflare API tokeno ar kitų paslapčių į repo.
- Analitikos prieigos yra tik skaitymo.
- Į `main` sujungti pakeitimus ir publikuoti produkcijoje tik po PR peržiūros.
