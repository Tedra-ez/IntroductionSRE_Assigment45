#!/usr/bin/env bash
set -euo pipefail
GATEWAY="${GATEWAY:-http://localhost:8088}"
for i in $(seq 1 100); do
  curl -s -o /dev/null "$GATEWAY/api/v1/products" || true
  curl -s -o /dev/null -X POST "$GATEWAY/api/v1/orders" \
    -H 'Content-Type: application/json' \
    -d '{"user_id":"load","product_id":1,"quantity":1}' || true
  sleep 0.1
done
echo "Traffic generation complete."
