#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3.10+ and re-run this script."
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10+ is required")
print(f"Using Python {sys.version.split()[0]}")
PY

if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .

if [ ! -f .env ]; then
  cp .env.example .env
fi

if ! grep -q '^OPENAI_API_KEY=.' .env 2>/dev/null; then
  echo
  read -r -s -p "Paste your OpenAI API key (stored only in local .env): " OPENAI_KEY
  echo
  python - "$OPENAI_KEY" <<'PY'
from pathlib import Path
import sys
key = sys.argv[1].strip()
p = Path('.env')
lines = p.read_text().splitlines() if p.exists() else []
out = []
found = False
for line in lines:
    if line.startswith('OPENAI_API_KEY='):
        out.append(f'OPENAI_API_KEY={key}')
        found = True
    else:
        out.append(line)
if not found:
    out.append(f'OPENAI_API_KEY={key}')
p.write_text('\n'.join(out).rstrip() + '\n')
PY
fi

mkdir -p secrets data

echo
wealth-os doctor || true

echo
read -r -p "Launch the Wealth OS dashboard now? [Y/n] " ANSWER
ANSWER="${ANSWER:-Y}"
if [[ "$ANSWER" =~ ^[Yy]$ ]]; then
  wealth-os dashboard
else
  echo "Setup complete. Later run: source .venv/bin/activate && wealth-os dashboard"
fi
