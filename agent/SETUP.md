# Pet traffic automatizavimo prijungimas

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
   - GA4 nuosavybės ID `563539278` ir svetainės adresas `https://pettraffic-ai.pages.dev/` jau įrašyti kaip saugūs numatytieji nustatymai darbo eigoje; jų GitHub Variables kurti nereikia. Jei ateityje keisis GA4 nuosavybė ar Search Console adresas, juos galima perrašyti per `GA4_PROPERTY_ID` ir `GSC_SITE_URL` kintamuosius.

Darbo eiga renka tik agreguotus skaičius: aktyvius naudotojus, sesijas, puslapių peržiūras ir Search Console užklausų paspaudimus / parodymus. Ji neidentifikuoja atskirų lankytojų. Jei nustatymų nėra, ataskaita aiškiai pažymi, kad duomenys neprijungti.

## 3. Temų tyrimas ir straipsnių rengimas

`agent/topic_radar.py` renka viešų Google News RSS antraščių rinkinį lietuviškomis augintinių temomis. Kasdienė GitHub Actions darbo eiga išsaugo Markdown ataskaitą 30 dienų.

Svarbu: naujienų antraštės nėra Google paieškų apimtys. Straipsnio publikavimui būtina patikrinti pirminius veterinarinius šaltinius ir faktus. Visiškai automatinis AI straipsnių generavimas per API neįjungtas, nes tam reikėtų papildomo mokamo modelio API rakto ir atskiro biudžeto patvirtinimo.

## 4. Turinio ir reklamos skaidrumas

Svetainė yra nepriklausomas informacinis projektas. Bet kokia būsima reklama, partnerystė ar komercinė nuoroda turi būti aiškiai pažymėta ir patikrinta prieš publikavimą.
