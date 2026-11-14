#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Paleisk šį diegimą Debian proot aplinkoje su root teisėmis." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl git jq nodejs npm python3 python3-venv

# Install GitHub CLI from its official Debian package repository.
install -d -m 0755 /usr/share/keyrings
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  -o /usr/share/keyrings/githubcli-archive-keyring.gpg
chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
ARCH="$(dpkg --print-architecture)"
printf 'deb [arch=%s signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\n' "$ARCH" \
  > /etc/apt/sources.list.d/github-cli.list
apt-get update
apt-get install -y gh

# This setup is normally streamed into bash (curl | bash), so BASH_SOURCE
# may be empty under set -u. Fetch the helper to a fixed temporary path.
# The helper repairs Ubuntu/Debian's packaged npm dependency tree if needed.
curl -fsSL https://raw.githubusercontent.com/Pershore/PetTraffic-AI/main/tools/termux/ensure-npm.sh \
  -o /tmp/pettraffic-ensure-npm.sh
bash /tmp/pettraffic-ensure-npm.sh
npm --version

# Codex CLI uses the ChatGPT sign-in flow; no API key is required for this setup.
NPM_CONFIG_PREFIX=/usr/local npm install --global --prefix /usr/local @openai/codex

if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  echo
  echo "1/2 – GitHub prisijungimas:"
  gh auth login --hostname github.com --git-protocol https --web
fi
gh auth setup-git

CODEX_AUTH="OK"
if ! codex login status >/dev/null 2>&1; then
  CODEX_AUTH="WAITING"
  echo
  echo "LAUKIA: Codex dar neprisijungęs. Dėl ankstesnio 15 min. skirtojo laiko diegimas nebandys automatiškai laukti."
  echo "Pirmiausia įjunkite ChatGPT Settings → Security → Device code login (beta)."
  echo "Tada Ubuntu aplinkoje paleiskite: codex login --device-auth"
  echo "Jei paskyra valdoma darbo srities, leidimą turi įjungti administratorius."
fi

WORKDIR="$HOME/PetTraffic-AI"
if [ -d "$WORKDIR/.git" ]; then
  git -C "$WORKDIR" fetch origin
  git -C "$WORKDIR" switch main
  git -C "$WORKDIR" pull --ff-only origin main
else
  gh repo clone Pershore/PetTraffic-AI "$WORKDIR"
fi

echo
echo "Patikra:"
gh auth status --hostname github.com
if codex login status >/dev/null 2>&1; then
  CODEX_AUTH="OK"
  codex login status
else
  CODEX_AUTH="WAITING"
  echo "Codex prisijungimas: LAUKIA"
fi
codex --version
if [ "$CODEX_AUTH" = "OK" ]; then
  codex doctor || echo "ĮSPĖJIMAS: codex doctor rado aplinkos problemų; patikrinkite išvestį."
else
  echo "codex doctor praleistas, kol neužbaigtas ChatGPT prisijungimas."
fi
git -C "$WORKDIR" status --short --branch

cat <<EOF

ĮDIEGTA: esama Linux proot aplinka + Git + GitHub CLI + Codex CLI.
Codex autentifikacija: ${CODEX_AUTH}.
ATKREIPK DĖMESĮ: tai dar nėra nuolatinis foninis agentas. Termux turi likti aktyvus,
o Codex užduotis kol kas paleidžiama rankiniu būdu. Automatinį užduočių paėmimą
iš GitHub ir PR kūrimą įjungsime atskiru, patikrintu etapu.
Cloudflare paslaptys į telefoną nekeliamos – Worker diegimus toliau atlieka
esami GitHub Actions procesai.
EOF
