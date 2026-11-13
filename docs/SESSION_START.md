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

## ChatGPT projekto apribojimas

GitHub dokumentai gali išsaugoti tęstinumo būseną, bet negali patys priversti ChatGPT pokalbio automatiškai pradėti GitHub skaitymo, vos atidarius projektą. ChatGPT projekto instrukcijose turi būti nurodyta, kad pirmame vartotojo pranešime naujoje sesijoje asistentas tyliai perskaito aukščiau nurodytus šaltinius ir tęsia nuo kito veiksmo. Jei įrankių ryšys nepasiekiamas, jis turi aiškiai pasakyti, kad būsenos negalėjo patikrinti, ir nieko nekeisti.
