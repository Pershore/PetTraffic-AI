# Termux + Codex + GitHub prijungimas

Atnaujinta: 2026-11-13

## Tikslas

Suteikti Android telefone veikiančiam Termux atskirą Linux aplinką, kurioje lokaliai veiktų Codex CLI ir GitHub CLI. ChatGPT šiame projekte lieka koordinatorius ir gali dirbti su ta pačia GitHub saugykla per jau prijungtą GitHub integraciją.

## Architektūra

1. **ChatGPT** – priima vartotojo užduotį, patikrina projekto būseną ir gali kurti / peržiūrėti GitHub užduotis bei PR per prijungtą GitHub integraciją.
2. **GitHub** – bendras šaltinis kodui, užduotims, PR, testų rezultatams ir istorijai.
3. **Codex CLI Termux aplinkoje** – lokaliai analizuoja ir keičia klonuotą saugyklą, vykdo testus ir gali dirbti su Git.
4. **GitHub Actions** – vykdo CI, svetainės patikras ir esamus Worker diegimus.
5. **Cloudflare** – pasiekiamas per jau sukonfigūruotus GitHub Actions diegimus. Termux nereikia saugoti Cloudflare API raktų.

## Kodėl Debian per proot-distro

Termux naudoja Android aplinką, o Codex CLI oficialiai skelbiamas Linux/macOS/Windows terminalams. Todėl diegimas numatytas Debian Linux naudotojo aplinkoje per Termux `proot-distro`, o ne kaip patvirtintas natyvus Android vykdymas. Suderinamumas turi būti patvirtintas realiu `codex doctor` ir paprasta read-only užduotimi telefone.

## Vienkartinis diegimas

### Prieš paleidžiant

ChatGPT paskyros **Settings → Security** įjunkite **Device code login** (beta). Jei naudojama valdoma darbo sritis, šią galimybę turi įjungti jos administratorius. Be šio leidimo Codex įrenginio kodo prisijungimas gali būti neprieinamas.

Kai `codex login --device-auth` prasidės, Termux terminalas pateiks vienkartinį patvirtinimo adresą ir kodą. Atidarykite adresą telefono naršyklėje, prisijunkite prie ChatGPT ir įveskite terminalo parodytą kodą. Kodo nesiųskite į pokalbį ir nedarykite jo ekrano nuotraukos.

Jei Android automatiškai atidaro ChatGPT programėlę, bet nematote kodo įvedimo puslapio, grįžkite į Termux ir tą patį patvirtinimo adresą atidarykite Chrome arba kita naršykle.

Po šio PR sujungimo paleisti Termux programoje:

```bash
curl -fsSL https://raw.githubusercontent.com/Pershore/PetTraffic-AI/main/tools/termux/bootstrap.sh | bash
```

Diegimo metu:
- įdiegiama Debian proot aplinka;
- įdiegiami Git, GitHub CLI, Node.js, Python ir Codex CLI;
- GitHub prisijungimas atliekamas oficialiu naršyklės / įrenginio patvirtinimo srautu;
- Codex prisijungimas atliekamas per ChatGPT device-code srautą;
- saugykla klonuojama į `~/PetTraffic-AI`.

**Niekada neįklijuok slaptažodžio, MFA kodo, GitHub tokeno, Codex auth failo ar Cloudflare rakto į ChatGPT pokalbį.** Prisijungimo kodus įvesk tik oficialiuose GitHub / OpenAI puslapiuose, kuriuos parodo CLI.

## Dabartinis valdymo srautas

- ChatGPT ir Codex dar nėra tiesiogiai sujungti tarpusavio API kanalu.
- Bendra darbo vieta yra GitHub saugykla.
- Codex gali lokaliai dirbti su klonuota saugykla ir naudoti GitHub CLI.
- Cloudflare diegimai lieka GitHub Actions pusėje; tiesioginė Cloudflare paskyros prieiga per šį tiltą neįjungiama.
- Automatinis GitHub užduočių paėmimas, Codex vykdymas fone ir automatinis PR kūrimas **dar neįjungti**. Tai atskiras etapas, kuriam reikalingas saugus užduočių eilės mechanizmas, vykdymo ribos ir realus Termux testas.

## Patikros po diegimo

1. `gh auth status --hostname github.com` – patvirtina GitHub CLI prisijungimą.
2. `codex login status` – patvirtina Codex prisijungimą.
3. `codex doctor` – patikrina CLI, aplinką ir autentifikaciją.
4. `cd ~/PetTraffic-AI && git status --short --branch` – patvirtina saugyklos kloną.

Pirmą Codex bandymą atlikti read-only režimu: paprašyti aprašyti saugyklos struktūrą ir nekurti pakeitimų.

## Saugumo ribos

- Jokio mokamo API rakto ar papildomos prenumeratos.
- Jokio Cloudflare tokeno telefone.
- Jokio automatinio PR sujungimo ar viešo turinio publikavimo.
- Codex pakeitimai turi grįžti per atskirą šaką ir PR; CI rezultatai turi būti patikrinti.
- ARO Vet sistemos, DNS, Cloudflare teisės ir production secrets neliečiami.
