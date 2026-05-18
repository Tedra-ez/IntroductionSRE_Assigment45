#!/usr/bin/env python3
"""Build End Term PDF report with embedded screenshots and Git repository link."""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    print("Install: pip install fpdf2", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "report" / "screenshots"
OUTPUT = ROOT / "report" / "End_Term_SRE_Report.pdf"
GIT_URL = os.environ.get(
    "GIT_REPO_URL",
    "https://github.com/Tedra-ez/IntroductionSRE_End",
)


class Report(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, "End Term Project - Comprehensive SRE Implementation", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    def section(self, title: str):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 14)
        self.multi_cell(self.epw, 8, title)
        self.ln(2)

    def body(self, text: str):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 11)
        self.multi_cell(self.epw, 6, text)
        self.ln(2)

    def image_if_exists(self, name: str, caption: str, w: float = 170):
        path = SCREENSHOTS / name
        if path.exists():
            if self.get_y() > 200:
                self.add_page()
            self.image(str(path), w=w)
            self.ln(2)
            self.set_font("Helvetica", "I", 9)
            self.multi_cell(0, 5, caption)
            self.ln(4)
        else:
            self.set_font("Helvetica", "I", 10)
            self.multi_cell(0, 5, f"[Missing screenshot: {name}]")
            self.ln(4)


def main():
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    pdf = Report()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 10, "End-to-End SRE Practices in a Multi-Orchestrated Microservices System")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(
        0,
        7,
        f"Date: {date.today().isoformat()}\n"
        f"Repository: {GIT_URL}\n"
        "Stack: Docker Compose / Swarm, Kubernetes, Terraform, Ansible\n"
        "Prometheus http://localhost:9091 | Grafana http://localhost:3001 (admin/admin)",
    )
    pdf.ln(6)

    pdf.section("1. Abstract")
    pdf.body(
        "This project implements Site Reliability Engineering across a distributed shop "
        "with six microservices, API gateway, Nginx frontend, PostgreSQL, and Redis. "
        "Observability uses Prometheus and Grafana with SLO-based alerts. A simulated "
        "order-service database incident was detected, mitigated, and documented in a postmortem."
    )

    pdf.section("2. Objectives Met")
    for item in [
        "6+ microservices with health checks and /metrics",
        "Docker Compose and Docker Swarm (docker-stack.yml)",
        "Kubernetes manifests with HPA for order-service",
        "Terraform inventory provisioning (extensible to cloud VMs)",
        "Ansible site playbook for Docker and stack deployment",
        "SLIs/SLOs: 99% availability, 200ms P95, 1% error rate",
        "Prometheus + Grafana + alert rules",
        "Incident simulation and postmortem",
        "Capacity planning document",
    ]:
        pdf.body(f"- {item}")

    pdf.section("3. Architecture")
    pdf.body(
        "User -> Frontend (Nginx :8088) -> API Gateway -> Auth, Product, Order, Payment, "
        "Notification, User Profile -> PostgreSQL / Redis. Monitoring: Prometheus :9091 -> Grafana :3001."
    )

    pdf.section("4. Microservices")
    pdf.body(
        "auth-service, product-service, order-service, payment-service, "
        "notification-service, user-profile-service (+ api-gateway, frontend)."
    )

    pdf.section("5. SLI / SLO")
    pdf.body(
        "SLIs: availability, latency, error rate, success rate. "
        "SLOs: availability >=99%, P95 latency <=200ms, error rate <=1%. "
        "Rules: monitoring/prometheus/alerts.yml. Details: docs/SLI_SLO.md."
    )

    pdf.section("6. Prometheus - Targets and Metrics")
    pdf.image_if_exists("prometheus-targets.png", "Figure 1: Prometheus targets (microservices UP)")
    pdf.image_if_exists("prometheus-graph.png", "Figure 2: Prometheus query - http_requests_total rate")

    pdf.section("7. Grafana Dashboard")
    pdf.image_if_exists("grafana-dashboard.png", "Figure 3: SRE Microservices Overview dashboard")
    pdf.image_if_exists("grafana-alerts.png", "Figure 4: Grafana - error rate and latency panels")

    pdf.section("8. Incident Response (Assignment 4)")
    pdf.body(
        "Scenario: order-service failed due to incorrect PostgreSQL password. "
        "Detection: OrderServiceDown alert and Grafana error spike. "
        "Recovery: restore env vars, recreate container. Full timeline: docs/postmortem.md."
    )

    pdf.section("9. Infrastructure as Code")
    pdf.body(
        "Terraform: terraform/ generates Ansible inventory. "
        "Ansible: ansible/site.yml installs Docker and deploys compose stack."
    )

    pdf.section("10. Multi-Orchestration")
    pdf.body(
        "Swarm: docker swarm init && docker stack deploy -c docker-stack.yml sre. "
        "Kubernetes: kubectl apply -f k8s/ (namespace, deployments, services, HPA)."
    )

    pdf.section("11. Capacity Planning")
    pdf.body(
        "Order and payment services dominate CPU under load; PostgreSQL is the primary bottleneck. "
        "Mitigations: horizontal replicas, vertical DB scaling, async notifications. "
        "See docs/capacity-planning.md."
    )

    pdf.section("12. Conclusion")
    pdf.body(
        "The system demonstrates the full SRE lifecycle: design, deploy, monitor, alert, "
        "respond, automate, and plan capacity across Swarm and Kubernetes."
    )

    pdf.add_page()
    pdf.set_x(pdf.l_margin)
    pdf.section("13. Deliverables and Git Repository")
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(pdf.epw, 8, "Source code and IaC:")
    pdf.set_font("Helvetica", "", 11)
    for part in [GIT_URL[i : i + 55] for i in range(0, len(GIT_URL), 55)]:
        pdf.multi_cell(pdf.epw, 6, part)
    pdf.ln(2)
    pdf.body(
        "Submit this PDF only, with the Git link above. "
        "Clone the repo and run: docker compose up -d --build"
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
