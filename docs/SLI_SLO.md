# SLI / SLO Design (Assignment 2)

## Service Level Indicators (SLIs)

| SLI | Definition | Prometheus signal |
|-----|------------|-------------------|
| Availability | Successful health checks / total checks | `up{job="microservices"}` |
| Latency | Request duration | `http_request_duration_seconds` histogram |
| Error rate | HTTP 5xx / all requests | `http_requests_total{status=~"5.."}` |
| Request success rate | HTTP 2xx / all requests | `http_requests_total{status=~"2.."}` |

## Service Level Objectives (SLOs)

| SLO | Target | Alert rule |
|-----|--------|------------|
| Availability | ≥ 99% monthly | `ServiceDown`, `OrderServiceDown` |
| Latency (P95) | ≤ 200 ms | `HighLatencyP95` |
| Error rate | ≤ 1% | `HighErrorRate` |
| Success rate | ≥ 99% | Derived from error-rate SLO |

## Error budget

With 99% availability, allowed downtime ≈ 7.2 hours/month. Incidents consuming budget are tracked in `docs/postmortem.md`.
