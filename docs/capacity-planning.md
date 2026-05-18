# Capacity Planning (Assignment 6)

## Load analysis (observed in demo)

| Component | CPU | Memory | Notes |
|-----------|-----|--------|-------|
| order-service | High | Medium | DB round-trips per request |
| payment-service | Medium | Low | Stateless simulation |
| postgres | Medium | High | Write-heavy during order bursts |
| notification-service | Low | Low | Redis queue |

## Bottlenecks

1. PostgreSQL connection pool under concurrent order creation
2. Order + Payment path on synchronous checkout flow

## Strategies

1. **Horizontal scaling** — Swarm/K8s replicas for stateless services (`order-service`, `payment-service` HPA in `k8s/microservices.yaml`)
2. **Vertical scaling** — Increase Postgres memory/CPU limits in production
3. **Database optimization** — Indexes on `orders(user_id)`, read replicas for listing
4. **Async notifications** — Decouple via Redis (already used by notification-service)

## Targets

- Sustain 200 RPS on order API with P95 < 200 ms
- Scale order-service replicas 2 → 5 when CPU > 70%
