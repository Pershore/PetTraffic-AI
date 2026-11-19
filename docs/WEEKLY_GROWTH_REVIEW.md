# Pet traffic – savaitinė augimo ataskaita

## Paskirtis

Kiekvieną savaitę sujungti jau surinktus SEO, lankomumo, turinio temų, techninės kokybės ir automatizacijų duomenis į vieną aiškią ataskaitą. Tai turi atsakyti, kas keičiasi, kas veikia, kas stringa ir kokie trys veiksmai yra svarbiausi.

## Vykdymas

- GitHub Actions workflow: .github/workflows/weekly-growth-review.yml
- Grafikas: pirmadienį 18:30 UTC (20:30 Lietuvos laiku žiemą / 21:30 vasarą).
- Rankinis workflow_dispatch paliktas testams ir savininko inicijuotai peržiūrai.
- Ataskaita saugoma automation-history šakoje: reports/history/weekly-review/latest.md, latest.json ir dienos JSON įraše.
- Kiekvienas workflow vykdymas taip pat sukuria GitHub Actions suvestinę ir 90 dienų artefaktą.
- Centrinis Control Center perskaičiuoja būseną po savaitinės darbo eigos pabaigos.

## Duomenų šaltiniai

| Šaltinis | Ką apima | Interpretavimo riba |
|---|---|---|
| GA4 | Aktyvūs ir nauji naudotojai, sesijos, puslapių peržiūros, patvirtintos organinės sesijos, populiariausi puslapiai | Organinės sesijos rodomos tik kai GA4 kanalų išklotinė patikimai sutampa su bendra sesijų suma |
| Google Search Console | Parodymai, paspaudimai, CTR, vidutinė pozicija, puslapiai, sitemap ir indeksavimo būsena | Search Console duomenys gali vėluoti keliomis dienomis; trūkstami duomenys nėra nulis |
| Paieškos temų grupės | Paieškos frazės vykdymo metu priskiriamos plačioms temoms: sveikata, mityba, veterinarinė pagalba, priežiūra, auginimas ir kita | Pačios paieškos frazės neįrašomos į ataskaitą ar ilgalaikę istoriją |
| Temų radaras | Viešų RSS / naujienų šaltinių antraščių skaičiai ir unikalių nuorodų suma | RSS antraštės nėra Google paieškų apimtys ir neįrodo paieškos paklausos |
| Lighthouse | Mobiliosios ir kompiuterio versijos našumas, prieinamumas, gerosios praktikos, SEO ir pagrindiniai Web Vitals | Vieno paleidimo svyravimas nėra automatinis pagrindas keisti kodą; vertinami konkretūs rodikliai |
| Control Center / Worker | Paskutinė patikrinta projektų būklė, aktyvios problemos, laukiančios patikros, AI agentų ir Control Core atminties būsena | „PARUOŠTA“ ar „vyksta“ nėra „PATIKRINTA“ |

## Palyginimas ir kokybės taisyklės

- GA4 ir Search Console dabartinis septynių dienų langas lyginamas su maždaug prieš savaitę užfiksuotu atskiru septynių dienų langu. Jei tinkamos bazės nėra, pokytis rodomas kaip neapskaičiuotas.
- Search Console CTR pokytis rodomas procentiniais punktais. Vidutinės pozicijos mažėjimas reiškia geresnę poziciją.
- Temų radaro ataskaita rodo surinktų dienų padengimą. Jei surinkta mažiau nei septynios dienos, ataskaita tai aiškiai nurodo.
- Visų šaltinių data ir būklė pateikiama atskirai.
- 0 rodomas tik kai šaltinis realiai pateikė nulį. Nepasiekiamas, pasenęs ar nepatvirtintas rodiklis žymimas „duomenų nėra“ arba „nepatvirtinta“.
- Trys rekomenduojami veiksmai sudaromi iš Control Center problemų ir esamų įrodymais grįstų rekomendacijų. Ataskaita pati nekeičia svetainės ir nepublikuoja turinio.

## Privatumas ir biudžetas

- Nenaudojami visitor-level GA4 duomenys, vartotojų identifikatoriai ar žalios paieškos frazės.
- Search Console frazės klasifikuojamos tik vykdymo atmintyje; į istoriją patenka tik temų kategorijų skaičiai, paspaudimai, parodymai, CTR ir agreguota pozicija.
- Puslapių adresuose pašalinami query parametrai ir fragmentai.
- Lighthouse istorijoje saugomi tik kategorijų balai ir pagrindiniai Web Vitals, ne visas diagnostikos payload.
- Naudojami jau turimi GA4, Search Console, RSS, Lighthouse, GitHub Actions ir Python įrankiai. Savaitinė peržiūra neatlieka papildomų AI kvietimų ir neprideda mokamų paslaugų.

## Turinio ir komercinės veiklos ribos

- Ataskaita gali siūlyti redakcinį darbą tik pagal realius Search Console / GA4 duomenis, skaitytojų klausimus ir patikrintus pirminius veterinarinius šaltinius. RSS antraštės nėra paieškų apimtys.
- Ataskaita nesuteikia leidimo automatiškai publikuoti turinio, keisti title/meta ar navigacijos.
- Pet traffic yra nepriklausomas informacinis prekės ženklas. ARO Vet, vaistinės skiltis, produktų kortelės, affiliate nuorodos, reklama ir partnerių sekimas negali būti grąžinami.
- 2026-11-15 buvęs laikinas ARO Vet produktų šaltinio leidimas panaikintas 2026-11-16; jis nebegalioja. Istorinis sprendimas paliktas tik kanoninėje projekto atmintyje kaip panaikintas.
- Leidžiama esama pirmosios šalies GA4 analitika tik po aiškaus slapukų sutikimo, kaip aprašyta privatumo politikoje.
