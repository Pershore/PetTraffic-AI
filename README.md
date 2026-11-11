# Pet traffic – augintinių informacinė svetainė

Lietuviška informacinė svetainė šunų ir kačių šeimininkams. Svetainės failai yra kataloge `site/`, o turinio, SEO ir automatizavimo dokumentacija – `agent/`.

## Vietinis paleidimas
```bash
cd site
python -m http.server 8000
``
Naršyklėje atidarykite http://127.0.0.1:8000.

## Publikavimas
Svetainė konfigūruota Cloudflare Pages, publikavimo katalogas – `site/`. Viešo diegimo būseną tikrinkite Cloudflare Pages ir GitHub Actions; vien kodo sujungimas dar nepatvirtina sėkmingo diegimo.

## Projekto principai
- Nepriklausomas informacinis turinys; svetainė nėra veterinarijos klinika.
- Sveikatos temose remiamasi patikimais šaltiniais ir nediagnozuojama.
- Reklama ar partnerystė aiškiai žymima ir nevykdoma be patvirtintų sąlygų.
- Nenaudojami botai, fiktyvūs atsiliepimai ar netikri lankomumo skaičiai.
