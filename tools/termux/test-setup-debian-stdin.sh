#!/usr/bin/env bash
set -euo pipefail

# Reproduce the setup script's streamed (curl | bash) execution context.
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"; rm -f /tmp/pettraffic-ensure-npm.sh' EXIT
mkdir -p "$TMP_DIR/bin"

cat > "$TMP_DIR/bin/curl" <<'MOCK_CURL'
#!/usr/bin/env bash
set -euo pipefail
output=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then
    output="$2"
    shift 2
  else
    shift
  fi
done
[ -n "$output" ]
cat > "$output" <<'MOCK_HELPER'
#!/usr/bin/env bash
printf 'helper-ran\n' >> "$TEST_LOG"
MOCK_HELPER
MOCK_CURL
chmod +x "$TMP_DIR/bin/curl"

(
  export PATH="$TMP_DIR/bin:$PATH"
  export TEST_LOG="$TMP_DIR/result.log"
  cat <<'STREAMED_SETUP' | bash -s
set -euo pipefail
curl -fsSL https://raw.githubusercontent.com/Pershore/PetTraffic-AI/main/tools/termux/ensure-npm.sh \
  -o /tmp/pettraffic-ensure-npm.sh
bash /tmp/pettraffic-ensure-npm.sh
STREAMED_SETUP
)

grep -Fxq 'helper-ran' "$TMP_DIR/result.log"
echo "PASS: streamed setup works with set -u and no BASH_SOURCE."
