# End Term — Comprehensive SRE Microservices

Distributed shop demonstrating SRE practices: **6 microservices**, Docker Compose/Swarm, Kubernetes, Terraform, Ansible, Prometheus, Grafana.

## Quick start

```bash
docker compose up -d --build
# Frontend http://localhost:8088  |  Prometheus http://localhost:9091  |  Grafana http://localhost:3001 (admin/admin)
./scripts/sustain-load.sh   # 3 min traffic for dashboards
pytest tests/ -v            # integration tests
```

## Full PDF report (recommended before submission)

```bash
bash scripts/prepare-report.sh
# Output: report/End_Term_SRE_Report.pdf (cover page, tables, tests, screenshots)
```

## Layout

| Path | Purpose |
|------|---------|
| `services/` | auth, product, order, payment, notification, user-profile, api-gateway |
| `docker-compose.yml` | Local orchestration + monitoring |
| `docker-stack.yml` | Docker Swarm |
| `k8s/` | Kubernetes manifests + HPA |
| `terraform/` | IaC (inventory / VM template) |
| `ansible/` | Configuration management |
| `monitoring/` | Prometheus & Grafana |
| `docs/` | SLI/SLO, postmortem, capacity planning |
| `report/` | PDF output & screenshots |

## Swarm & Kubernetes

```bash
docker swarm init
docker stack deploy -c docker-stack.yml sre

kubectl apply -f k8s/
```

## Report (PDF for submission)

```bash
pip install fpdf2
export GIT_REPO_URL="https://github.com/YOUR_USERNAME/AdvancedProgramming_Final-main"
# Add PNGs to report/screenshots/ (prometheus-targets.png, prometheus-graph.png, grafana-dashboard.png)
python3 scripts/build-report.py
```

Output: `report/End_Term_SRE_Report.pdf`

## Incident demo

See `docs/postmortem.md`. Break order DB password, observe alerts, restore with `docker compose up -d --force-recreate order-service`.
