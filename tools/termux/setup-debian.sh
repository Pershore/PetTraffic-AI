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

# Codex CLI uses the ChatGPT sign-in flow; no API key is required for this setup.
npm install --global @openai/codex

if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  echo
  echo "1/2 – GitHub prisijungimas:"
  gh auth login --hostname github.com --git-protocol https --web
fi
gh auth setup-git

if ! codex login status >/dev/null 2>&1; then
  echo
  echo "2/2 – Codex prisijungimas per ChatGPT:"
  if ! codex login --device-auth; then
    echo "Codex įrenginio kodo prisijungimas nepavyko." >&2
    echo "Patikrinkite ChatGPT Settings → Security → Device code login (beta)." >&2
    echo "Jei naudojate valdomą darbo sritį, šį nustatymą turi įjungti administratorius." >&2
    exit 1
  fi
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
codex login status
codex --version
codex doctor
git -C "$WORKDIR" status --short --branch

cat <<'EOF'

ĮDIEGTA: Debian proot + Git + GitHub CLI + Codex CLI.
ATKREIPK DĖMESĮ: tai dar nėra nuolatinis foninis agentas. Termux turi likti aktyvus,
o Codex užduotis kol kas paleidžiama rankiniu būdu. Automatinį užduočių paėmimą
iš GitHub ir PR kūrimą įjungsime atskiru, patikrintu etapu.
Cloudflare paslaptys į telefoną nekeliamos – Worker diegimus toliau atlieka
esami GitHub Actions procesai.
EOF
