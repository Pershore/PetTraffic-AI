#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/tools/termux/bootstrap.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin"

cat > "$TMP/bin/pkg" <<'MOCK'
#!/usr/bin/env bash
exit 0
MOCK

cat > "$TMP/bin/proot-distro" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
command_name="$1"
case "$command_name" in
  login)
    distro="$2"
    shift 2
    [ "${1:-}" = "--" ] && shift
    installed=" ${INSTALLED_DISTROS:-} "
    if [[ "$distro" == "debian" && -f "$STATE_DIR/debian-installed" ]]; then
      installed="$installed debian "
    fi
    [[ "$installed" == *" $distro "* ]] || exit 1
    if [[ "${1:-}" == "bash" ]]; then
      echo "MOCK_SELECTED_DISTRO=$distro"
    fi
    ;;
  install)
    [ "$2" = "debian" ]
    touch "$STATE_DIR/debian-installed"
    ;;
  *)
    exit 2
    ;;
esac
MOCK
chmod +x "$TMP/bin/pkg" "$TMP/bin/proot-distro"

run_case() {
  local installed="$1"
  local expected="$2"
  local state="$TMP/state-$expected"
  mkdir -p "$state"
  local output
  output="$(PATH="$TMP/bin:$PATH" STATE_DIR="$state" INSTALLED_DISTROS="$installed" bash "$SCRIPT")"
  grep -Fq "Naudojama esama Linux aplinka: $expected" <<< "$output"
  grep -Fq "MOCK_SELECTED_DISTRO=$expected" <<< "$output"
}

run_case "ubuntu" "ubuntu"
run_case "debian" "debian"
run_case "" "debian"

echo "PASS: bootstrap reuses Ubuntu, reuses Debian, and installs Debian only when neither exists."
