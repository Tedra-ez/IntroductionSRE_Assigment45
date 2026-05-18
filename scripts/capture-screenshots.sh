#!/usr/bin/env bash
# Capture Prometheus/Grafana screenshots (macOS). Requires stack running.
set -euo pipefail
OUT="$(dirname "$0")/../report/screenshots"
mkdir -p "$OUT"
sleep 2
# Prometheus targets
if command -v screencapture >/dev/null; then
  open "http://localhost:9091/targets"
  sleep 3
  screencapture -x "$OUT/prometheus-targets.png" 2>/dev/null || true
  open "http://localhost:9091/graph?g0.expr=sum(rate(http_requests_total%5B1m%5D))&g0.tab=0"
  sleep 3
  screencapture -x "$OUT/prometheus-graph.png" 2>/dev/null || true
  open "http://localhost:3001/d/sre-overview/sre-microservices-overview?orgId=1"
  sleep 5
  screencapture -x "$OUT/grafana-dashboard.png" 2>/dev/null || true
fi
echo "Screenshots in $OUT (or use browser manually if headless)."
