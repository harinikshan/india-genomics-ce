#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m pip install -r requirements.txt
python3 scripts/fetch_data.py --source all --accept-licenses "$@"

echo
echo "Bootstrap complete."
echo "Run the app with: python3 app.py"
echo "Or run analysis: python3 scripts/run_full_analysis.py examples/genome_demo.txt --name Demo"
