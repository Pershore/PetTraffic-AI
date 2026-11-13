# PetTraffic AI — sesijos pradžios ir tęstinumo protokolas

Atnaujinta: 2026-11-13

Šis failas skirtas ChatGPT, Codex, GitHub Copilot ir žmogui, kuris tęsia projektą po pertraukos.

## Vienintelė teisinga darbo pradžios seka

1. Perskaityti `AGENTS.md` — projekto tikslai, darbo taisyklės, saugumas ir testai.
2. Perskaityti `reports/history/project-state/latest.md` iš `automation-history` šakos — naujausia automatiškai patikrinta techninė būsena.
3. Perskaityti `reports/work-log/README.md` iš `main` šakos — atlikti GitHub pakeitimai, testai ir tęstinumo įrašai.
4. Perskaityti naujausią `docs/PETTRAFFIC_AI_HANDOVER_*.md` — paaiškinimas ir konkretus kitas veiksmas.
5. Patikrinti tik tą workflow / PR / gyvą read-only būseną, kuri būtina kitam veiksmui. Jei paskutinis įrodymas dar galioja, jo nekartoti.
6. Tęsti nuo pirmo neužbaigto veiksmo. Jei būtinas suplanuotas ciklas dar neįvyko, pažymėti `WAITING` ir laukti; nekurti fiktyvaus rezultato.

## Šakų paskirtys — nekopijuoti vienos į kitą

- `main`: kodas, dokumentacija, `AGENTS.md`, darbo žurnalas.
- `automation-history`: tik privatumo požiūriu filtruoti `reports/history/**` JSON ir būsenų snapshot'ai.
- `reports/work-log/README.md` turi būti skaitomas iš `main`. Jo nebuvimas `automation-history` šakoje nėra klaida ir nėra priežastis blokuoti darbą.

## Būsenų žymėjimas

- **ATLIKTA IR PATIKRINTA** — yra konkretus testas, workflow run, commit ar gyvas atsakymas.
- **PARUOŠTA, BET NEAKTYVUOTA** — kodas / dokumentacija yra, bet realus veikimas nepatvirtintas.
- **NEBAIGTA / WAITING** — laukiama suplanuoto ciklo, vartotojo sprendimo ar trūkstamų įrodymų.
- **PLANUOJAMA** — dar nepradėta; nevadinti įgyvendinta.

## Naujausias tęstinumo taškas (2026-11-13 17:12 UTC)

- PR #150, #151, #152 ir #153 sujungti. #151, #152 ir #153 site-check patikros – success; po sujungimų main site-check run 43469741292 – success.
- Voice-first / zero-manual-work taisyklė įrašyta į AGENTS.md ir docs/SESSION_START.md; detali architektūra docs/VOICE_FIRST_AUTONOMY.md.
- Pagrindinis kasdienis priežiūros agentas aktyvus, kitas vykdymas 2026-11-14 09:45 Europe/Vilnius. Vienkartinė AI atminties patikra suplanuota 10:35, po Worker agentų ciklo 10:20.
- Naujausias analytics snapshot run 43443849180: GA4 ReadTimeout (15 s), Search Console API veikia, bet 2026-11-04–2026-11-10 rodikliai 0 parodymų / 0 paspaudimų; sitemap apdorojimas laukiamas, prioritetiniai URL Google dar nežinomi.
- Peržiūrėjus 100 naujausių Actions vykdymų nerasta event=schedule. Cron YAML yra, bet tikroji Actions nustatymų priežastis nepatvirtinta; dabartinė GitHub jungtis neturi Actions settings skaitymo / keitimo funkcijos.
- Kitas prioritetas: po 2026-11-14 10:20 ciklo įrodyti D1 AI atminties įrašymą arba taisyti pagal tikslų stage klaidos kodą. Tada tęsti schedule ir GA4 diagnostiką.
- Žr. visą naujausią įrašą `docs/PETTRAFFIC_AI_HANDOVER_2026-11-13.md`, 9 skyrių.

## Paskutinis žinomas tęstinumo taškas (2026-11-13)

- PR #147 tęstinumo ir automatinio darbo žurnalo pakeitimai sujungti.
- Automatinis darbo žurnalas įrašė GitHub commit'us į `main`; jis nematuoja aktyvaus darbo laiko ar pokalbių.
- PR #148 stage-aware AI agentų JSON diagnostika sujungta ir Worker įdiegta.
- Paskutinis `automation-history` snapshot (run `43458770880`, commit `97551e8`) dar rodo ankstesnio 2026-11-13 AI ciklo nesėkmę: `ai_calls=1`, `Unexpected_end_of_JSON_input`; tuo metu `control_core.status=not_started`, `memory_status=missing`.
- Po diagnostikos pataisos dar nėra patvirtinto naujo AI agentų ciklo, kuris įrodytų D1 įrašymą.
- **Kitas konkretus veiksmas:** po suplanuoto 2026-11-14 10:20 Europe/Vilnius agentų ciklo perskaityti naujausią `latest.md`, darbo žurnalą iš `main`, patikrinti gyvą Worker `/health`, naujausio ciklo `agent_orchestration.error_code` ir D1 `control_core_runs` bei `control_core_memory` būseną per esamą read-only kelią. Jei ciklas nepavyko, taisyti tik pagal tikslų etapo prefiksą ir logus. Jei ciklas dar neįvyko, patikrą palikti WAITING.

## Nemokamų AI įrankių naudojimas

- GitHub Copilot Free: naudoti esamiems kodo pasiūlymams, ribotam chat/agent naudojimui ir lokaliam CLI/IDE darbui, jei aplinka prieinama. Nemanyti, kad Free planas suteikia Copilot cloud/background agentą.
- OpenAI Codex Free: naudoti trumpoms, aiškiai apribotoms kodo peržiūros, testų ar pataisų užduotims, jei funkcija prieinama vartotojo paskyroje. Free prieiga nereiškia neriboto cloud agento vykdymo.
- ChatGPT su prijungta GitHub integracija: naudoti saugyklos būsenos skaitymui, PR paruošimui ir patikrinamiems pakeitimams, kai įrankiai suteikia prieigą.
- Nenaudoti kelių agentų tam pačiam failui vienu metu. Vienas koordinatorius paskiria atskiras, nesikertančias užduotis; visi pakeitimai grįžta per PR ir testus.
- Jokio mokamo plano ar API be atskiro biudžeto patvirtinimo.

## Voice-first / naudotojo be rankinio darbo principas

- Vartotojas valdo projektą balsu arba trumpais pranešimais. Įprastų techninių veiksmų (terminalo komandų, failų kopijavimo, GitHub naršymo, testų paleidimo, statusų rinkimo) neperduoti vartotojui, jei juos gali atlikti prijungti įrankiai.
- Koordinatorius pats perskaito būseną, parenka saugų kitą veiksmą, vykdo jį per GitHub / prijungtas integracijas, paleidžia testus ir užrašo įrodymus.
- Vartotojo klausti tik dėl išankstinio leidimo mokamoms paslaugoms, publikavimui, production / DNS / Cloudflare teisių / secrets pakeitimams ar kitiems didelės rizikos veiksmams.
- Nesiųsti tarpinių „dirbu“ pranešimų be rezultato. Pateikti trumpą atsakymą, kai yra patikrintas etapas arba būtinas vartotojo sprendimas.
- Pokalbio ar įrankio vykdymas nėra nuolatinis foninis procesas. Fone gali veikti tik realiai aktyvuoti suplanuoti GitHub Actions arba ChatGPT automatizavimai. Jų vykdymą būtina įrodyti realiais run'ais, ne vien konfigūracija.
- Vienas pagrindinis kasdienis priežiūros agentas koordinuoja darbą; nekuriami dubliuojantys kasdieniai agentai. GitHub Actions atlieka aiškiai apibrėžtas specialistų užduotis, Worker agentai vykdo ribotą analizę ir saugo atmintį.
- Jei trūksta prieigos, pateikti tikslų blokatorių ir vieną mažiausią reikalingą vartotojo veiksmą; niekada neprašyti slaptažodžių, MFA ar slaptų raktų pokalbyje.

## ChatGPT projekto apribojimas

GitHub dokumentai gali išsaugoti tęstinumo būseną, bet negali patys priversti ChatGPT pokalbio automatiškai pradėti GitHub skaitymo, vos atidarius projektą. ChatGPT projekto instrukcijose turi būti nurodyta, kad pirmame vartotojo pranešime naujoje sesijoje asistentas tyliai perskaito aukščiau nurodytus šaltinius ir tęsia nuo kito veiksmo. Jei įrankių ryšys nepasiekiamas, jis turi aiškiai pasakyti, kad būsenos negalėjo patikrinti, ir nieko nekeisti.


## Naujausias patvirtintas tęstinumo taškas (2026-11-13 19:47 UTC)

- PR #156 „Recover safely from ambiguous D1 AI call reservations“ sujungtas commit `a74ad11f755f4bd39a9b17c92999d5172f045326`; Worker pakeitimas įdiegtas.
- PR #156 testai ir Cloudflare read-only validacija – success; post-merge Worker deploy run `43495408320` – success, įskaitant D1 migracijų žingsnį, gyvą /health ir API autentifikacijos ribą. Site checks `43495408435`, control center `43495408385`, work log `43495408363` ir central sync `43495504768` – success.
- PR #156 atkuria D1 AI kvietimo skaitiklį po dviprasmiško `UPDATE ... RETURNING` atsakymo: prieš pakartojimą atliekamas read-back, todėl nebedubliuojamas jau įrašytas kvietimas.
- 2026-11-13 ankstesnis agentų ciklas vis dar saugomas kaip failed; tos pačios dienos ciklas automatiškai nekartojamas. Kitas Worker ciklas: 2026-11-14 10:20 Europe/Vilnius. Esama vienkartinė ChatGPT atminties patikra: 10:35 Europe/Vilnius.
- GitHub Actions cron yra YAML failuose, tačiau peržiūrėjus `event=schedule` vykdymus rasta tik viena eilutė (site checks); kitų pagrindinių workflow schedule paleidimai nepatvirtinti. Repo Actions settings per dabartinę jungtį nepasiekiami.
- Naujausias analytics archyvas: GA4 unavailable, Search Console available; GA4 runReport timeout problema lieka atvira.
- Tęsti nuo 2026-11-14 agentų ciklo patikros; nekartoti jau sėkmingų PR #156 testų ar diegimo patikros be naujų įrodymų.


## 2026-11-13 – Termux / Codex / GitHub prijungimo etapas

- Atidarytas PR #159: `Add Termux Codex and GitHub local setup bridge`.
- PR prideda Termux bootstrap, Debian proot setup, Codex CLI + GitHub CLI diegimą ir atskirą shell sintaksės / saugumo patikrų workflow.
- Naujausias PR commit: `a6e06e9035ad431f3f5c90fb038ac99ffef8d5d8`.
- Termux / Codex bridge patikra run `43497203181` – success; bendro site-check run `43497203198` dar vyksta (paskutinė patikra: analytics testų žingsnis in_progress).
- Tai paruošia vietinį Codex ir GitHub CLI telefonui, bet dar nepatvirtina realaus diegimo Android įrenginyje ir nesukuria fone veikiančio užduočių pollerio.
- ChatGPT tiesioginis valdymas per GitHub užduočių eilę ir automatinis Codex PR kūrimas – kitas atskiras etapas; Cloudflare Worker diegimai lieka esamuose GitHub Actions.
- Nėra tiesioginės Termux prieigos iš ChatGPT. Po PR sujungimo reikės vieną kartą paleisti dokumentuotą bootstrap komandą Termux programoje ir atlikti GitHub / ChatGPT oficialius prisijungimus. Jokie slapti raktai pokalbyje neprašomi.
