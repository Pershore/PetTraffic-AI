#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/tools/termux/ensure-npm.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin"

cat > "$TMP/bin/npm" <<'MOCK'
#!/usr/bin/env bash
if [ "${NPM_INITIAL_OK:-0}" = "1" ]; then
  echo "9.2.0"
  exit 0
fi
exit 1
MOCK

cat > "$TMP/bin/node" <<'MOCK'
#!/usr/bin/env bash
if [ "${1:-}" = "--version" ]; then
  echo "v22.22.1"
elif [[ "${1:-}" == */npm-cli.js ]]; then
  echo "10.9.10"
else
  exit 1
fi
MOCK

cat > "$TMP/bin/python3" <<'MOCK'
#!/usr/bin/env bash
[ "${PYTHON_DOWNLOAD_FAIL:-0}" = "0" ] || exit 1
touch "${3:?archive path missing}"
MOCK

cat > "$TMP/bin/tar" <<'MOCK'
#!/usr/bin/env bash
if [ "${1:-}" = "-tzf" ]; then
  printf '%s\n' package/ package/bin/ package/bin/npm-cli.js package/bin/npx-cli.js
  exit 0
fi
destination=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-C" ]; then destination="$2"; shift 2; else shift; fi
done
mkdir -p "$destination/package/bin"
: > "$destination/package/bin/npm-cli.js"
: > "$destination/package/bin/npx-cli.js"
MOCK
chmod +x "$TMP/bin/"*

run_case() {
  local name="$1" initial_ok="$2" download_fail="$3" expected="$4"
  local state="$TMP/$name"
  mkdir -p "$state/bin"
  cp "$TMP/bin/"* "$state/bin/"
  local status=0
  PATH="$state/bin:$PATH" PETTRAFFIC_NPM_ROOT="$state/opt/npm-10.9.10" \
    PETTRAFFIC_NPM_BIN_DIR="$state/bin" NPM_INITIAL_OK="$initial_ok" \
    PYTHON_DOWNLOAD_FAIL="$download_fail" bash "$SCRIPT" >"$state/output.log" 2>&1 || status=$?
  [ "$status" -eq "$expected" ] || { cat "$state/output.log"; return 1; }
  if [ "$name" = "already-works" ]; then
    grep -Fq "npm veikia" "$state/output.log"
    [ ! -e "$state/opt/npm-10.9.10" ]
  elif [ "$name" = "fallback" ]; then
    grep -Fq "ATKURTA: npm 10.9.10 veikia" "$state/output.log"
    [ -x "$state/bin/npm" ]
    [ -x "$state/bin/npx" ]
  else
    grep -Fq "nepavyko saugiai atsisiųsti" "$state/output.log"
    [ ! -e "$state/opt/npm-10.9.10" ]
  fi
}

run_case "already-works" 1 0 0
run_case "fallback" 0 0 0
run_case "download-fails" 0 1 1
echo "PASS: healthy npm, verified standalone fallback, and safe download failure."
