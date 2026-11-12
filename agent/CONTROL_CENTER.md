# Pet traffic – centrinio valdymo centro planas

## Tikslas

Sujungti esamas automatizacijas į vieną valdymo sluoksnį, kuris parodo sistemos būklę, nustato prioritetus ir ilgainiui vertina, ar atlikti pakeitimai davė naudą.

## Etapai

### 1 etapas – esama infrastruktūra

- GitHub Actions vykdo esamas SEO, analitikos, temų, svetainės būklės ir Lighthouse užduotis.
- agent/control_center.py tik skaitymo režimu patikrina naujausių suplanuotų darbo eigų būsenas.
- Kasdienė suvestinė parodo klaidas, pasenusius paleidimus ir veiksmų prioritetus.
- Mašininė JSON suvestinė leidžia automatizuotai įvertinti būseną.
- Aptikus klaidą, pasenusį ar neaiškų procesą sukuriamas arba atnaujinamas vienas GitHub įspėjimas; po atsistatymo jis automatiškai uždaromas.
- Pirmo paleidimo būsena „nėra paleidimų“ pati savaime nesukuria klaidingo įspėjimo.
- Ataskaita išsaugoma GitHub Actions artefakte 90 dienų.
- Kiekvieno suplanuoto paleidimo agreguota būklė archyvuojama atskiroje `automation-history` šakoje (`reports/history/control-center/YYYY-MM-DD.json`); keli tos pačios dienos paleidimai išsaugomi, pakartotinis tas pats paleidimas nedubliuojamas.
- Istorijoje saugomi tik darbo eigų pavadinimai, būsenos, techninės pastabos, paleidimų nuorodos ir datos; lankytojų duomenys bei paslaptys nerenkami.
- Jokie pakeitimai svetainėje ar main šakoje neatliekami.

### 2 etapas – ilgalaikė atmintis

- Pradinis istorijos sluoksnis: valdymo centro paleidimų ir automatizacijų būsenų JSON archyvas `automation-history` šakoje.
- Kitas šio etapo plėtinys: agreguotų GA4 / Search Console rodiklių savaitiniai įrašai, techninių klaidų pasikartojimo istorija, rekomendacijų registras ir pakeitimų rezultatų palyginimas.
- Archyvas laikomas atskiroje šakoje, kad istorijos įrašai nekeistų `main` svetainės šaltinių ir nekeltų nereikalingų Cloudflare Pages publikavimų.
- Istorijoje nerenkami atskirų lankytojų duomenys, paieškos užklausų tekstai ar paslaptys.

### 3 etapas – Cloudflare Worker + D1

Worker taps centrine API / įvykių priėmimo vieta, o D1 – ilgalaike duomenų baze, kai atsiras realus poreikis:
- kelių agentų užduočių eilei ir būsenoms;
- istorinių metrikų bei eksperimentų rezultatų saugojimui;
- vienam valdymo skydeliui;
- įvykių priėmimui iš GitHub ir suplanuotų darbų paleidimui.

Šių komponentų dabar nediegiame, nes jie dubliuotų dalį GitHub Actions funkcijų, kol neįrodėme poreikio. Prieš diegimą patikrinsime Cloudflare plano limitus ir išlaidas.

## Sprendimų saugumo taisyklės

- Pirmiausia read-only diagnostika.
- Automatiniai pakeitimai kuriami atskiroje GitHub šakoje ir siūlomi PR.
- main, Cloudflare produkcinė aplinka, DNS, slapti raktai ir trečiųjų šalių paskyros nekeičiami be atskiro patvirtinimo.
- Veterinarinis turinys nepublikuojamas be faktų ir redakcinės patikros.
- Jokių netikrų lankytojų, paspaudimų, atsiliepimų ar dirbtinio paieškos aktyvumo.
- AI API išlaidos neįjungiamos be atskiro biudžeto patvirtinimo.

## Sėkmės kriterijai

- Kasdienė suvestinė teisingai atpažįsta sėkmingus, nepavykusius, vykdomus ir pasenusius darbus.
- Klaidos turi tiesioginę nuorodą į GitHub Actions paleidimą.
- Rašymo teisės apribotos vieno techninio GitHub įspėjimo sukūrimui / uždarymui; svetainės ir kodo pakeitimams jos nenaudojamos.
- Vėliau kiekvienas siūlomas SEO pakeitimas turi pradinį rodiklį ir po pakeitimo pamatuojamą rezultatą.
