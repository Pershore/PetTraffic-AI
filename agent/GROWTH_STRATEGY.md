# Pet traffic: realistiškas organinio augimo planas

Atnaujinta: 2026-11-15

## Patikrinta dabartinė būklė

- Svetainėje sąmoningai palikti keturi pagrindiniai gidai: skubūs kačių šlapinimosi sutrikimai, kačių viduriavimas, šunų viduriavimas ir kada kreiptis į veterinarą.
- Viešą svetainės struktūrą sudaro pradžia, apie, privatumas ir šie keturi gidai. Sitemap turi septynis URL.
- Pagrindiniame puslapyje yra keturios gidų kortelės, temų filtrai ir paieška.
- Naudojamos originalios SVG iliustracijos. Jos nėra fotografijos ir neturi būti pristatomos kaip tikros klinikinės nuotraukos.
- GA4 ir Search Console duomenys renkami per GitHub Actions. Skaičius pateikti tik pagal sėkmingas ataskaitas; jei šaltinis nepasiekiamas, rodyti „duomenų nėra“, ne nulį.
- Temų radaras renka viešų naujienų RSS antraštes. Antraščių kiekis nėra Google paieškų apimtis ar svetainės paklausa.

## Tikslas

Auginti tikrą Lietuvos šunų ir kačių šeimininkų organinį srautą, jų pasitikėjimą ir pakartotinius apsilankymus. Pirmiausia gerinti esamus keturis gidus, matavimą ir skaitytojo kelią; nekurti puslapių vien dėl kiekio.

## Prioritetų tvarka

1. **Matavimas.** Patikrinti, ar veikia GA4 sutikimo mechanizmas ir ar GitHub Actions analitikos darbo eiga gauna tik skaitymo prieigą prie GA4 bei Search Console. Niekada nekelti raktų į Git ar pokalbį.
2. **Esami gidai.** Atnaujinti tik tada, kai randama konkreti faktinė spraga, pasenęs šaltinis, neveikianti nuoroda ar realus skaitytojų klausimas.
3. **Vidinės nuorodos.** Kiekviename gide pateikti aiškų kelią į kitą tikrai susijusį gidą, nekurti dirbtinių nuorodų.
4. **Techninė kokybė.** Stebėti canonical, sitemap, 301, alt tekstus, struktūrinius duomenis, mobiliąją versiją ir našumą.
5. **Platinimas.** Rengti socialinių įrašų ar vaizdo scenarijus tik kaip juodraščius. Nieko automatiškai neskelbti ir nesiųsti be atskiro leidimo.
6. **Naujas turinys.** Naują puslapį svarstyti tik tada, kai Search Console, skaitytojų klausimai ir pirminiai veterinariniai šaltiniai rodo aiškią spragą. Pirmiausia patikrinti, ar klausimo jau neatsako vienas iš keturių gidų.
7. **Produktai ir monetizacija.** Kai konkrečiam gidui tai naudinga, galima rengti subtilias produktų korteles su tiesioginėmis nuorodomis į ARO Vet Vaistinę – tai vartotojo patvirtintas prioritetinis produktų šaltinis. Naudoti tik aktualius, patikrintus produktų aprašymus, nuotraukas, kainas ir prieinamumą; nekurti gydomojo poveikio pažadų. Pet traffic išlieka nepriklausomas prekės ženklas. Jokio affiliate sekimo ar komisinių teiginių be atskiro leidimo. Produktų įtraukimas į viešą svetainę ir toliau reikalauja vartotojo patvirtinimo.

## Kaip vertinti paieškos temas

- Search Console užklausas atskirti nuo Google News antraščių.
- Žiūrėti į parodymus, paspaudimus, CTR, pozicijas ir puslapius; nekurti tariamų mėnesio paieškos kiekių.
- Patikrinti paieškos ketinimą ir esamų puslapių persidengimą.
- Sveikatos teiginius tikrinti pirminiuose veterinarijos universitetų, profesinių organizacijų ir gyvūnų gerovės organizacijų šaltiniuose.
- Nurodyti šaltinius prie susijusių teiginių, aiškiai atskirti bendrą informaciją nuo diagnozės ir gydymo.

## 30 / 60 / 90 dienų kryptis

- **1–30 dienos:** patvirtinti matavimą, patikrinti indeksavimą, technines klaidas ir keturių gidų šaltinius.
- **31–60 dienos:** pagal realias užklausas pagerinti title, description, atsakymų aiškumą, vidines nuorodas ir skaitymo patogumą.
- **61–90 dienos:** palyginti faktinius rezultatus, nuspręsti, ar esamiems gidams reikia atnaujinimų. Naujas turinys ar monetizacija svarstomi tik esant įrodymams ir atskiram sprendimui.

## Savaitinė augimo peržiūra

Kiekvieną pirmadienį GitHub Actions turi sugeneruoti vieną sujungtą `weekly-growth-review` ataskaitą iš jau surinktų ir privatumo požiūriu filtruotų duomenų. Ji turi aiškiai atsakyti:

- Ar GA4 lankytojai, sesijos, peržiūros ir patvirtintos organinės sesijos keičiasi, lyginant su ankstesniu laikotarpiu?
- Ką rodo Search Console: parodymai, paspaudimai, CTR, pozicija, geriausi puslapiai ir tik agreguotos paieškos temų grupės?
- Kurios RSS temos dažniausiai pasirodo naujienų šaltiniuose? Šį signalą aiškiai atskirti nuo Google paieškos paklausos.
- Ar Lighthouse ir techninės automatizacijos sveikos? Ar Worker AI ir Control Core atminties būsena patvirtinta?
- Kokie trys konkretūs kiti veiksmai turi didžiausią pagrindimą turimuose įrodymuose?

Ataskaita turi rodyti kiekvieno šaltinio datą ir būseną, palyginimo bazę, trūkstamus duomenis bei įrodymų ribas. Nenaudoti naujų mokamų AI kvietimų; pradžioje naudoti deterministinę analizę Python įrankiais. Nearchyvuoti neanonimizuotų Search Console frazių ar lankytojų lygmens duomenų.

## Matavimo lenta

Kas savaitę, kai prieiga veikia, fiksuoti:
- GA4: aktyvius naudotojus, sesijas, organinės paieškos sesijas, puslapių peržiūras ir įsitraukimą.
- Search Console: parodymus, paspaudimus, CTR, vidutinę poziciją, užklausas ir puslapius.
- Techninę būklę: 404, 301, neveikiančias nuorodas, sitemap, robots ir diegimo būseną.

Jei ataskaita neprieinama, žymėti „duomenų nėra“ ir nespėlioti.

## Apsaugos taisyklės

- Viešas prekės ženklas tik „Pet traffic“.
- ARO Vet Vaistinė yra patvirtintas prioritetinis produktų šaltinis; įtraukti tik aktualias, temai naudingas prekes su tiesioginėmis nuorodomis. Nekopijuoti ARO Vet logotipo ar vizualinio identiteto, nenaudoti konkuruojančių parduotuvių be atskiro sprendimo ir nekurti affiliate sekimo.
- Nenaudoti botų, netikrų apsilankymų, paspaudimų, atsiliepimų ar ekspertų patvirtinimų.
- Nenaudoti svetimų nuotraukų ar tekstų be aiškių teisių.
- Nepublikuoti automatiškai sveikatos turinio be redakcinės ir faktų patikros.
- Nepirkti paslaugų ir nekeisti paskyrų, DNS ar paslapčių.
