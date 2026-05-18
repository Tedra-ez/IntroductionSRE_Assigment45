#!/usr/bin/env bash
# Prepare environment, run tests, load metrics, capture screenshots, build PDF.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Starting stack..."
docker compose up -d --build
docker compose restart grafana prometheus 2>/dev/null || true
sleep 15

echo "==> Running integration tests..."
pip3 install -q -r tests/requirements.txt
mkdir -p report
pytest tests/ -v --tb=short 2>&1 | tee report/test-results.txt

echo "==> Sustained load (background 90s)..."
bash scripts/sustain-load.sh &
LOAD_PID=$!
sleep 90

echo "==> Capture screenshots (manual fallback if headless unavailable)..."
bash scripts/capture-screenshots.sh || true

wait "$LOAD_PID" 2>/dev/null || true

echo "==> Building PDF..."
pip3 install -q fpdf2
python3 scripts/build-report.py
echo "Done: report/End_Term_SRE_Report.pdf"
