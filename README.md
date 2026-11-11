# Pet traffic – augintinių informacinė svetainė

Atnaujinta svetainės versija su mobiliam ekranui pritaikytu dizainu ir vietinėmis SVG iliustracijomis (interneto ryšys paveikslėliams nereikalingas).

## Paleidimas Termux
```bash
cd ~/storage/downloads
unzip -o PetTraffic_AI_visual.zip
cd PetTraffic_AI_visual/PetTraffic_AI/site
python -m http.server 8000
```
Naršyklėje: http://127.0.0.1:8000

Prieš viešinimą pakeisk `YOUR-PROJECT.pages.dev` į tikrą domeną `index.html`, `robots.txt` ir `sitemap.xml` failuose. Privatumo puslapis yra tik šablonas. Straipsnio tekstą prieš publikavimą būtina patikrinti. Projektas yra nepriklausoma informacinė svetainė. Svetainė publikuojama per Cloudflare Pages; diegimo būseną tikrinkite GitHub Actions.I agentas.
