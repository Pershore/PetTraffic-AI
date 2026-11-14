#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/tools/termux/ensure-npm.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin"

cat > "$TMP/bin/npm" <<'MOCK'
#!/usr/bin/env bash
if [ -f "$STATE_DIR/repaired" ]; then
  echo "10.9.0"
  exit 0
fi
if [ "${NPM_INITIAL_OK:-0}" = "1" ]; then
  echo "10.9.0"
  exit 0
fi
exit 1
MOCK

cat > "$TMP/bin/apt-get" <<'MOCK'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$STATE_DIR/apt.log"
if [ "${1:-}" = "install" ] && [ "${APT_REPAIR_FAIL:-0}" = "1" ]; then exit 1; fi
if [ "${1:-}" = "install" ]; then touch "$STATE_DIR/repaired"; fi
MOCK
chmod +x "$TMP/bin/npm" "$TMP/bin/apt-get"

run_case() {
  local name="$1" initial_ok="$2" repair_fail="$3" expected="$4"
  local state="$TMP/$name"
  mkdir -p "$state"
  local status=0
  PATH="$TMP/bin:$PATH" STATE_DIR="$state" NPM_INITIAL_OK="$initial_ok" APT_REPAIR_FAIL="$repair_fail" \
    bash "$SCRIPT" >"$state/output.log" 2>&1 || status=$?
  [ "$status" -eq "$expected" ] || { cat "$state/output.log"; return 1; }
  if [ "$name" = "already-works" ]; then
    [ ! -f "$state/apt.log" ]
  elif [ "$name" = "repairs" ]; then
    grep -Fq "install --reinstall -y nodejs npm node-glob" "$state/apt.log"
    grep -Fq "ATKURTA" "$state/output.log"
  else
    grep -Fq "nepavyko atkurti" "$state/output.log"
  fi
}

run_case "already-works" 1 0 0
run_case "repairs" 0 0 0
run_case "repair-fails" 0 1 1
echo "PASS: npm health check, one-time apt repair, and clear failure handling."
