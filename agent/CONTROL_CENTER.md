# Pet traffic – centrinio valdymo centro planas

## Tikslas

Sujungti esamas automatizacijas į vieną valdymo sluoksnį, kuris parodo sistemos būklę, nustato prioritetus ir ilgainiui vertina, ar atlikti pakeitimai davė naudą.

## Etapai

### 1 etapas – esama infrastruktūra

- GitHub Actions vykdo esamas SEO, analitikos, temų, svetainės būklės ir Lighthouse užduotis.
- agent/control_center.py tik skaitymo režimu patikrina naujausių suplanuotų darbo eigų būsenas.
- Kasdienė suvestinė parodo klaidas, pasenusius paleidimus ir veiksmų prioritetus.
- Ataskaita išsaugoma GitHub Actions artefakte 90 dienų.
- Jokie pakeitimai svetainėje ar main šakoje neatliekami.

### 2 etapas – ilgalaikė atmintis

Kai patvirtinsime, kad pirmasis etapas patikimai veikia, pridėsime struktūruotą istoriją: datą, rodiklius, klaidas, pasiūlymus, pakeitimus ir vėlesnius rezultatus. Pradžioje galima naudoti GitHub artefaktus / versijuojamus JSON išrašus; istorinių duomenų apimtį ir saugojimo trukmę reikės sąmoningai valdyti.

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
- Nėra rašymo teisių, kurios nereikalingos diagnostikai.
- Vėliau kiekvienas siūlomas SEO pakeitimas turi pradinį rodiklį ir po pakeitimo pamatuojamą rezultatą.
