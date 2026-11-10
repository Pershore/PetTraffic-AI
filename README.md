# PetTraffic AI – vizualus pradinis etapas

Atnaujinta svetainės versija su mobiliam ekranui pritaikytu dizainu ir vietinėmis SVG iliustracijomis (interneto ryšys paveikslėliams nereikalingas).

## Paleidimas Termux
```bash
cd ~/storage/downloads
unzip -o PetTraffic_AI_visual.zip
cd PetTraffic_AI_visual/PetTraffic_AI/site
python -m http.server 8000
```
Naršyklėje: http://127.0.0.1:8000

Prieš viešinimą pakeisk `YOUR-PROJECT.pages.dev` į tikrą domeną `index.html`, `robots.txt` ir `sitemap.xml` failuose. Privatumo puslapis yra tik šablonas. Straipsnio tekstą prieš publikavimą būtina patikrinti. Projektas nėra oficialiai susijęs su Aro Vet, jei nėra atskiro susitarimo. Ši versija dar nėra paskelbta internete ir nėra veikiantis automatinis AI agentas.
