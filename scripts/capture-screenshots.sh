#!/usr/bin/env bash
# Open monitoring UIs for manual or automated capture into report/screenshots/
set -euo pipefail
OUT="$(cd "$(dirname "$0")/.." && pwd)/report/screenshots"
mkdir -p "$OUT"
PROM="${PROM:-http://localhost:9091}"
GRAFANA="${GRAFANA:-http://localhost:3001}"

echo "Capture these URLs into $OUT:"
echo "  prometheus-targets.png  <- $PROM/targets"
echo "  prometheus-graph.png    <- $PROM/graph?g0.expr=sum(rate(http_requests_total%5B1m%5D))"
echo "  prometheus-alerts.png   <- $PROM/alerts"
echo "  grafana-dashboard.png   <- $GRAFANA/d/sre-overview/sre-microservices-overview"
echo "  grafana-stats.png       <- same dashboard (top stat row)"

if command -v screencapture >/dev/null; then
  open "$PROM/targets" && sleep 4 && screencapture -x "$OUT/prometheus-targets.png" || true
  open "$PROM/alerts" && sleep 3 && screencapture -x "$OUT/prometheus-alerts.png" || true
  open "$PROM/graph?g0.expr=sum(rate(http_requests_total%5B1m%5D))&g0.tab=1" && sleep 4 && screencapture -x "$OUT/prometheus-graph.png" || true
  open "$GRAFANA/d/sre-overview/sre-microservices-overview?orgId=1&refresh=5s&kiosk" && sleep 8 && screencapture -x "$OUT/grafana-dashboard.png" || true
  cp "$OUT/grafana-dashboard.png" "$OUT/grafana-stats.png" 2>/dev/null || true
fi
ls -la "$OUT"/*.png 2>/dev/null || echo "No PNG files yet - use Cursor browser capture."
