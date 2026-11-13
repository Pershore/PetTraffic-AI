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

if ! proot-distro login debian -- true >/dev/null 2>&1; then
  proot-distro install debian
fi

echo
echo "Paruošiama Debian aplinka. Toliau reikės prisijungti prie GitHub ir ChatGPT per oficialius prisijungimo langus."
proot-distro login debian -- bash -lc "curl -fsSL '${RAW_BASE}/${SETUP_PATH}' | bash"
