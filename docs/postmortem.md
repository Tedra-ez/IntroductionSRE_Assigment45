# Postmortem — Order Service Database Misconfiguration (Assignment 4)

**Date:** 2026-05-19  
**Severity:** SEV-2  
**Duration:** ~18 minutes  
**Author:** SRE Team

## Summary

Order creation failed after a simulated misconfiguration of PostgreSQL credentials on `order-service`. Monitoring detected elevated 5xx responses and `OrderServiceDown` alerts.

## Impact

- Order API returned HTTP 503
- Checkout flow blocked; other services remained healthy
- ~12% of API traffic affected during the window

## Timeline (UTC)

| Time | Event |
|------|-------|
| T+0 | Wrong `POSTGRES_PASSWORD` deployed to order-service |
| T+2 | Prometheus alert `OrderServiceDown` fired |
| T+5 | On-call acknowledged Grafana dashboard spike in error rate |
| T+8 | Logs showed `psycopg2.OperationalError: password authentication failed` |
| T+12 | Config corrected in compose env; service recreated |
| T+18 | Metrics normalized; SLO burn stopped |

## Root cause

`order-service` could not authenticate to PostgreSQL due to incorrect `POSTGRES_PASSWORD` environment variable (simulated incident per assignment scenario).

## Detection

- Prometheus scrape target `order-service:8003` down / unhealthy
- Grafana panel: error rate & P95 latency
- Alert rules in `monitoring/prometheus/alerts.yml`

## Recovery

1. Restored correct credentials in `docker-compose.yml`
2. `docker compose up -d order-service`
3. Verified `/health` and sample order POST

## Action items

| Action | Owner | Status |
|--------|-------|--------|
| Add startup probe failing on DB auth | Platform | Done (healthcheck) |
| Secret management via K8s Secret / Vault | Platform | Planned |
| Runbook for order-service DB failures | SRE | Done |

## Lessons learned

Health checks tied to database connectivity accelerated detection. Centralized dashboards reduced MTTR compared to log-only investigation.
