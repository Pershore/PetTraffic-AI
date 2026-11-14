#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO="Pershore/PetTraffic-AI"
BRANCH="main"
SETUP_PATH="tools/termux/setup-debian.sh"
RAW_BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

if ! command -v pkg >/dev/null 2>&1; then
  echo "Šį failą paleisk Termux programoje, ne Debian ar kitame terminale." >&2
  exit 1
fi

pkg update -y
pkg install -y proot-distro curl

# Reuse the user's existing Ubuntu proot first; otherwise reuse Debian.
# Install Debian only when neither supported distro is already present.
DISTRO=""
for candidate in ubuntu debian; do
  if proot-distro login "$candidate" -- true >/dev/null 2>&1; then
    DISTRO="$candidate"
    break
  fi
done

if [ -z "$DISTRO" ]; then
  proot-distro install debian
  DISTRO="debian"
fi

echo
echo "Naudojama esama Linux aplinka: $DISTRO"
echo "Paruošiama aplinka. Toliau reikės prisijungti prie GitHub ir ChatGPT tik jei dar neprisijungta."
proot-distro login "$DISTRO" -- bash -lc "curl -fsSL '${RAW_BASE}/${SETUP_PATH}' | bash"
