#!/usr/bin/env bash
# Simulates Order Service DB misconfiguration (Assignment 4)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Breaking order-service DB password..."
docker compose exec -T order-service sh -c 'export POSTGRES_PASSWORD=wrong_password' || true
docker compose stop order-service
echo "To simulate: set POSTGRES_PASSWORD=wrong_password on order-service in docker-compose.yml"
echo "Then: docker compose up -d --force-recreate order-service"
echo "Observe OrderServiceDown in Prometheus alerts and Grafana error panels."
echo "Recovery: restore password sre_password and recreate order-service."
