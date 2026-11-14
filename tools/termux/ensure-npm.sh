#!/usr/bin/env bash
# Recover npm when Ubuntu's split nodejs/npm/node-glob packages are inconsistent.
set -euo pipefail

NPM_VERSION="10.9.10"
NPM_ROOT="${PETTRAFFIC_NPM_ROOT:-/opt/pettraffic-npm/${NPM_VERSION}}"
BIN_DIR="${PETTRAFFIC_NPM_BIN_DIR:-/usr/local/bin}"

if npm --version >/dev/null 2>&1; then
  echo "npm veikia."
  exit 0
fi

NODE_VERSION="$(node --version 2>/dev/null || true)"
if [[ ! "$NODE_VERSION" =~ ^v(20\.(1[7-9]|[2-9][0-9])|22\.([9]|[1-9][0-9])|2[3-9]\.|[3-9][0-9]\.) ]]; then
  echo "KLAIDA: npm ${NPM_VERSION} reikia Node.js 20.17+ arba 22.9+. Rasta: ${NODE_VERSION:-nerasta}" >&2
  exit 1
fi

echo "Aptiktas neveikiantis sistemos npm. Diegiamas atskiras, SHA-512 patikrintas npm ${NPM_VERSION} paketas..."
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ARCHIVE="$TMP/npm.tgz"
STAGE="$TMP/unpacked"
mkdir -p "$STAGE"

# Read the official npm registry metadata, download its tarball, and verify
# the tarball against the registry's SHA-512 integrity value before extraction.
if ! python3 - "$NPM_VERSION" "$ARCHIVE" <<'PY'
import base64
import hashlib
import json
import sys
import urllib.parse
import urllib.request

version, destination = sys.argv[1:3]
metadata_url = f"https://registry.npmjs.org/npm/{version}"
with urllib.request.urlopen(metadata_url, timeout=30) as response:
    metadata = json.load(response)

dist = metadata.get("dist") or {}
tarball_url = dist.get("tarball", "")
integrity = dist.get("integrity", "")
parsed = urllib.parse.urlparse(tarball_url)
if parsed.scheme != "https" or parsed.hostname != "registry.npmjs.org":
    raise SystemExit("Atsisakyta: npm tarball šaltinis nėra oficialus registry.npmjs.org.")
sha512 = next((item[7:] for item in integrity.split() if item.startswith("sha512-")), None)
if not sha512:
    raise SystemExit("Atsisakyta: npm registry nepateikė SHA-512 vientisumo reikšmės.")

with urllib.request.urlopen(tarball_url, timeout=60) as response:
    payload = response.read(20 * 1024 * 1024 + 1)
if len(payload) > 20 * 1024 * 1024:
    raise SystemExit("Atsisakyta: npm paketas viršija 20 MiB saugumo ribą.")
actual = base64.b64encode(hashlib.sha512(payload).digest()).decode("ascii")
if actual != sha512:
    raise SystemExit("Atsisakyta: npm paketo SHA-512 patikra nepraėjo.")
with open(destination, "wb") as archive:
    archive.write(payload)
print("Oficialaus npm paketo SHA-512 patikra: PASS.")
PY
then
  echo "KLAIDA: nepavyko saugiai atsisiųsti arba patikrinti npm paketo." >&2
  exit 1
fi

# Accept only the expected package/ archive root and reject traversal paths.
if ! tar -tzf "$ARCHIVE" | awk '
  /^\// { bad=1 }
  /(^|\/)\.\.(\/|$)/ { bad=1 }
  $0 !~ /^package(\/|$)/ { bad=1 }
  END { exit bad }
'; then
  echo "KLAIDA: npm archyvo struktūra netinkama." >&2
  exit 1
fi

tar -xzf "$ARCHIVE" -C "$STAGE" --no-same-owner --no-same-permissions
if [ ! -f "$STAGE/package/bin/npm-cli.js" ]; then
  echo "KLAIDA: npm archyve nerastas CLI failas." >&2
  exit 1
fi

install -d -m 0755 "$(dirname "$NPM_ROOT")" "$BIN_DIR"
if [ -e "$NPM_ROOT" ]; then
  rm -rf -- "$NPM_ROOT"
fi
mv "$STAGE/package" "$NPM_ROOT"

cat > "$BIN_DIR/npm" <<EOF
#!/usr/bin/env sh
exec node "$NPM_ROOT/bin/npm-cli.js" "\$@"
EOF
cat > "$BIN_DIR/npx" <<EOF
#!/usr/bin/env sh
exec node "$NPM_ROOT/bin/npx-cli.js" "\$@"
EOF
chmod 0755 "$BIN_DIR/npm" "$BIN_DIR/npx"
export PATH="$BIN_DIR:$PATH"

INSTALLED_VERSION="$(npm --version 2>/dev/null || true)"
if [ "$INSTALLED_VERSION" != "$NPM_VERSION" ]; then
  echo "KLAIDA: įdiegtas npm neatitinka tikėtinos versijos. Tikėtasi ${NPM_VERSION}, rasta ${INSTALLED_VERSION:-neveikia}." >&2
  exit 1
fi

echo "ATKURTA: npm ${NPM_VERSION} veikia; Ubuntu sistemos npm/glob paketai nepakeisti."
