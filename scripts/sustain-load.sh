#!/usr/bin/env bash
# Sustained load for Grafana/Prometheus dashboards (run 3+ minutes before screenshots).
set -euo pipefail
GATEWAY="${GATEWAY:-http://localhost:8088}"
DURATION="${DURATION:-180}"
echo "Generating load to $GATEWAY for ${DURATION}s..."
end=$((SECONDS + DURATION))
while [ "$SECONDS" -lt "$end" ]; do
  curl -s -o /dev/null "$GATEWAY/api/v1/products" || true
  curl -s -o /dev/null "$GATEWAY/api/v1/products/1" || true
  curl -s -o /dev/null "$GATEWAY/api/v1/orders" || true
  curl -s -o /dev/null -X POST "$GATEWAY/api/v1/orders" \
    -H 'Content-Type: application/json' \
    -d "{\"user_id\":\"load-$RANDOM\",\"product_id\":1,\"quantity\":1}" || true
  curl -s -o /dev/null -X POST "$GATEWAY/api/v1/payments" \
    -H 'Content-Type: application/json' \
    -d '{"order_id":1,"amount":49.99}' || true
  curl -s -o /dev/null -X POST "$GATEWAY/api/v1/notify" \
    -H 'Content-Type: application/json' \
    -d '{"user_id":"load","message":"alert-demo"}' || true
  curl -s -o /dev/null "$GATEWAY/api/v1/users/demo" || true
  curl -s -o /dev/null -X POST "$GATEWAY/api/v1/login" \
    -H 'Content-Type: application/json' \
    -d '{"username":"load"}' || true
  # Occasional client errors (~2%) so error panels show live data (not "No data")
  if [ $((RANDOM % 50)) -eq 0 ]; then
    curl -s -o /dev/null "$GATEWAY/api/v1/products/99999" || true
    curl -s -o /dev/null -X POST "$GATEWAY/api/v1/orders" \
      -H 'Content-Type: application/json' -d '{}' || true
  fi
  sleep 0.15
done
echo "Load complete."
