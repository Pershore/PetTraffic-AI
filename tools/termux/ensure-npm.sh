#!/usr/bin/env bash
# Repair the Ubuntu/Debian packaged npm dependency tree once before using npm.
set -euo pipefail

if npm --version >/dev/null 2>&1; then
  echo "npm veikia."
  exit 0
fi

echo "Aptiktas neveikiantis npm. Atkuriami Node.js, npm ir glob paketai..."
if ! apt-get update || ! apt-get install --reinstall -y nodejs npm node-glob; then
  echo "KLAIDA: nepavyko atkurti nodejs/npm/node-glob paketų." >&2
  exit 1
fi

if ! npm --version >/dev/null 2>&1; then
  echo "KLAIDA: npm vis dar neveikia po paketų atkūrimo." >&2
  echo "Diagnostika: node=$(node --version 2>&1 || true); npm=$(command -v npm || echo nerastas)" >&2
  exit 1
fi

echo "ATKURTA: npm veikia po nodejs/npm/node-glob paketų atkūrimo."
