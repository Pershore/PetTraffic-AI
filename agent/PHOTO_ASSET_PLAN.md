# PetTraffic AI – nuotraukų ir socialinių vaizdų planas

Auditas atliktas 2026-11-11 pagal pagrindinės šakos HTML failus.

## Dabartinė būklė
- Patikrinta 16 HTML failų (įskaitant techninį reklamos fragmentą).
- Pagrindiniame puslapyje yra viena SVG hero iliustracija.
- Straipsnių puslapiuose nerasta nė vienos nuotraukos.
- Nė viename iš patikrintų puslapių nerasta Open Graph `og:image` ar Twitter Card vaizdo metaduomenų.
- Visuose pagrindiniuose puslapiuose yra title, meta description, canonical ir vienas H1; patikrintose vidinėse nuorodose klaidų nerasta.
- Mobilusis CSS turi 900 px, 680 px ir 390 px lūžio taškus; naujam Gargždų gidui pridėtos mobiliesiems pritaikytos kortelės ir paspaudžiami telefono numeriai.

## Vaizdų prioritetai

### 1 etapas – dalijimosi vaizdas
Sukurti originalų 1200×630 socialinio dalijimosi vaizdą su PetTraffic AI identitetu, aiškiu pavadinimu ir viena autentiška augintinio nuotrauka. Pridėti `og:image`, `og:image:alt`, `twitter:card` ir Twitter image metaduomenis pagrindiniam puslapiui bei vietiniam gidui.

### 2 etapas – pagrindinis puslapis
Pakeisti arba papildyti abstrakčią SVG hero iliustraciją licencijuota, natūralia šuns ir katės nuotrauka namų aplinkoje. Išlaikyti pakankamą kontrastą, aiškų fokusą ir mobiliajame ekrane neiškirpti gyvūnų.

### 3 etapas – svarbiausi straipsniai
Pirmiausia parinkti vaizdus šioms temoms:
1. Katės kvėpavimas miegant – ramiai miegančios katės nuotrauka, ne medicininis simptomas.
2. Katė negali pasišlapinti – neutrali katės ir kraiko dėžės aplinka, be bauginančio ar klaidinančio vaizdo.
3. Kada kreiptis į veterinarą – ramus veterinaro konsultacijos vaizdas, tik su tinkama licencija.
4. Kaip pripratinti katę prie transportavimo dėžės – katė savanoriškai įsitaisiusi atviroje dėžėje.
5. Šuns mityba – šuo prie maisto dubenėlio, aiškus ir natūralus kadras.

### 4 etapas – likę straipsniai
Vaizdus kurti pagal konkretų puslapio tikslą, o ne dėti vieną bendrą šuns ar katės nuotrauką į visus puslapius. Jei vaizdas nieko nepaaiškina ir nesuteikia emocinio ar praktinio konteksto, geriau jo nedėti.

## Techniniai reikalavimai
- Pirmenybė originalioms nuotraukoms arba aiškiai licencijuotam turiniui.
- Kiekvienam failui saugoti šaltinį, autorių, licenciją, įsigijimo datą ir leidžiamą naudojimo būdą.
- Naudoti WebP arba AVIF, kai tai palaikoma, ir pateikti tinkamus dydžius per `srcset`.
- Nurodyti vaizdo `width` ir `height`, kad sumažėtų layout shift.
- Pirmo ekrano pagrindinį vaizdą krauti prioritetiškai; kitus – su `loading="lazy"`.
- Alt tekstas turi aprašyti konkrečią nuotrauką ir jos kontekstą, o ne kartoti raktažodžius.
- Nenaudoti klinikų, prieglaudų ar kitų įstaigų nuotraukų ir logotipų be leidimo.
- ARO Vet produktų nuotraukoms, logotipui ir prekių aprašymams taip pat būtinas raštiškas naudojimo leidimas; iki tol rodyti savo sukurtas iliustracijas ir tiesiogines nuorodas į oficialius produktų puslapius.
- Nenaudoti dirbtinai sugeneruotų vaizdų taip, kad jie atrodytų kaip tikri pacientai, veterinarai ar realios procedūros.

## Failų struktūros pasiūlymas
`site/assets/images/` – optimizuoti vaizdai.
`agent/ASSET_LICENSES.md` – kiekvieno naudojamo vaizdo šaltinis, licencija ir leidimo įrodymas.

## Sėkmės matavimas
- Socialinių tinklų nuorodų peržiūra ir paspaudimai (kai GA4/UTM matavimas veikia).
- Puslapio greitis ir Core Web Vitals prieš/po vaizdų įkėlimo.
- Search Console vaizdų paieškos parodymai ir paspaudimai, jei pateikiami.
- Nenaudoti vien nuotraukų skaičiaus kaip sėkmės rodiklio.
