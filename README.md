# PulseOps 
### Cloud Observability & AI Alerting System

## 📌 What is PulseOps?

PulseOps is a **production-grade cloud observability platform** that combines real-time infrastructure monitoring, centralized log aggregation, and AI-powered incident response — all deployed on AWS EC2 using Terraform and Docker Compose.

When an alert fires, PulseOps doesn't just send a notification — it automatically analyzes the issue using an LLM and delivers actionable remediation steps, reducing Mean Time To Resolve (MTTR).

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────┐
                    │           AWS EC2 Server             │
                    │                                      │
                    │  ┌──────────┐    ┌──────────┐       │
                    │  │Prometheus│    │   Loki   │       │
                    │  │(metrics) │    │  (logs)  │       │
                    │  └─────┬────┘    └────┬─────┘       │
                    │        │              │              │
                    │  ┌─────▼──────────────▼─────┐       │
                    │  │         Grafana            │       │
                    │  │   (unified dashboards)     │       │
                    │  └───────────────────────────┘       │
                    │                                      │
                    │  ┌──────────┐  ┌──────────────────┐ │
                    │  │  Node    │  │   Alertmanager   │ │
                    │  │ Exporter │  │  → AI Responder  │ │
                    │  └──────────┘  │  → Groq LLM API  │ │
                    │                └──────────────────┘ │
                    │  ┌──────────┐  ┌──────────────────┐ │
                    │  │Promtail  │  │      Nginx       │ │
                    │  │ (logs)   │  │  (reverse proxy) │ │
                    │  └──────────┘  └──────────────────┘ │
                    └─────────────────────────────────────┘
                              ▲
                    ┌─────────┴──────────┐
                    │  Terraform (IaC)   │
                    │  Provisions EC2,   │
                    │  Security Groups,  │
                    │  Key Pairs         │
                    └────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Tool | Purpose |
|---|---|---|
| Metrics Collection | Prometheus | Scrapes and stores time-series metrics |
| Log Aggregation | Loki + Promtail | Collects and indexes container logs |
| Visualization | Grafana | Real-time dashboards for metrics and logs |
| Alerting | Alertmanager | Routes alerts to AI responder and email |
| AI Diagnosis | Groq (Llama 3) | Analyzes alerts and suggests fixes |
| Reverse Proxy | Nginx | Single entry point for all services |
| Containerization | Docker Compose | Orchestrates all 8 services |
| Infrastructure | Terraform | Provisions AWS resources as code |
| Cloud | AWS EC2 | Hosts the entire platform |

---

## ✨ Features

- **Real-time Metrics** — CPU, memory, disk, network monitoring via Prometheus + Node Exporter
- **Centralized Logging** — Container log aggregation via Loki + Promtail
- **Unified Dashboards** — Beautiful Grafana dashboards for both metrics and logs
- **Smart Alerting** — Threshold-based alerts for CPU, memory, disk, and instance health
- **AI Incident Response** — Automatic root cause analysis and remediation steps via Groq LLM
- **Reverse Proxy** — Nginx routing all traffic through a single endpoint
- **Infrastructure as Code** — Full AWS infrastructure provisioned via Terraform
- **Secrets Management** — All credentials managed via `.env` file, never hardcoded

---

## 📁 Project Structure

```
pulseops/
├── terraform/                 # AWS infrastructure as code
│   ├── main.tf                # EC2, security groups, key pairs
│   ├── variables.tf           # Configurable variables
│   ├── outputs.tf             # Server IP, URLs after deployment
│   ├── data.tf                # Auto-fetches latest Ubuntu AMI
│   └── provider.tf            # AWS provider config
├── prometheus/
│   ├── prometheus.yml         # Scrape configs and alert routing
│   └── alert_rules.yml        # CPU, memory, disk, uptime alert rules
├── loki/
│   └── loki-config.yml        # Log storage and schema config
├── promtail/
│   └── promtail-config.yml    # Log collection and shipping config
├── alertmanager/
│   └── alertmanager.yml       # Alert routing to AI responder + email
├── nginx/
│   └── nginx.conf             # Reverse proxy routing rules
├── ai-responder/
│   ├── app.py                 # Flask app — receives alerts, calls LLM
│   └── Dockerfile             # Container definition for AI service
├── grafana/
│   └── dashboards/            # Dashboard JSON exports
├── scripts/
│   └── backup.sh              # Prometheus + Grafana backup to S3
├── .env.example               # Template for required environment variables
├── docker-compose.yml         # Orchestrates all 8 services
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- Terraform
- AWS CLI configured
- Groq API key (free at console.groq.com)

### 1. Clone the Repository

```bash
git clone https://github.com/akshaybk85/pulseops.git
cd pulseops
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
nano .env  # Fill in your values
```

### 3. Provision AWS Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Note the output `server_public_ip` for accessing services.

### 4. Deploy to EC2

```bash
# Copy project to EC2
scp -i ~/.ssh/pulseops -r ~/pulseops ubuntu@YOUR-EC2-IP:~/

# SSH into server
ssh -i ~/.ssh/pulseops ubuntu@YOUR-EC2-IP

# Start all services
cd pulseops
docker-compose --env-file .env up -d
```

### 5. Access Services

| Service | URL |
|---|---|
| Grafana | http://YOUR-EC2-IP:3000 |
| Prometheus | http://YOUR-EC2-IP:9090 |
| Alertmanager | http://YOUR-EC2-IP:9093 |
| AI Responder | http://YOUR-EC2-IP:5000/health |

### 6. Import Grafana Dashboards

1. Login to Grafana → Connections → Data Sources
2. Add Prometheus: `http://prometheus:9090`
3. Add Loki: `http://loki:3100`
4. Import Dashboard ID `1860` (Node Exporter Full)
5. Import Dashboard ID `13639` (Logs / App)

---

## 🤖 AI Incident Response

When Prometheus detects an alert, Alertmanager sends a webhook to the AI Responder service which:

1. Receives the alert payload
2. Sends it to Groq LLM with a DevOps-specific prompt
3. Gets back root cause analysis + remediation commands
4. Returns the diagnosis as JSON

### Test the AI Responder

```bash
curl -X POST http://YOUR-EC2-IP:5000/alert \
  -H "Content-Type: application/json" \
  -d '{
    "alerts": [{
      "labels": {
        "alertname": "HighCPUUsage",
        "severity": "warning",
        "instance": "node-exporter:9100"
      },
      "annotations": {
        "description": "CPU usage is 92% for 2 minutes"
      },
      "status": "firing"
    }]
  }'
```

### Example AI Response

```json
{
  "status": "processed",
  "alert": "HighCPUUsage",
  "diagnosis": "1. Likely Cause: Resource-intensive process consuming excess CPU...\n2. Immediate Fix:\n   top -c -b -n 1 | sort -k 9 -nr | head -10\n   docker stats --no-stream\n3. Prevention: Implement CPU limits in Docker Compose..."
}
```

---

## 🚨 Alert Rules

| Alert | Condition | Severity |
|---|---|---|
| HighCPUUsage | CPU > 80% for 2 minutes | Warning |
| HighMemoryUsage | Memory > 80% for 2 minutes | Warning |
| LowDiskSpace | Disk < 20% for 5 minutes | Critical |
| InstanceDown | Target unreachable for 1 minute | Critical |

---

## 🔧 Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# Groq AI API
GROQ_API_KEY=your_groq_api_key

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_strong_password

# Email Alerts
SMTP_FROM=youremail@gmail.com
SMTP_USERNAME=youremail@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL_TO=youremail@gmail.com

# Slack (optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

---

## 🏗️ Infrastructure (Terraform)

Terraform provisions:
- **EC2 instance** — t2.micro, Ubuntu 24.04, 20GB storage
- **Security Group** — Opens ports 22, 80, 3000, 9090, 9093, 3100, 5000
- **Key Pair** — SSH access using your local public key
- **Auto-installs** — Docker and Docker Compose via user_data script

Destroy infrastructure when not in use:
```bash
cd terraform
terraform destroy
```

---

## 🔒 Security Notes

- Credentials stored in `.env` file — never committed to Git
- `.gitignore` excludes `.env`, Terraform state files
- Security group allows SSH from anywhere — restrict to your IP in production
- Use AWS IAM roles instead of access keys in production

---

## 📊 Services Overview

| Container | Port | Status |
|---|---|---|
| Prometheus | 9090 | Metrics collection |
| Node Exporter | 9100 | System metrics exporter |
| Loki | 3100 | Log aggregation |
| Promtail | — | Log shipper |
| Grafana | 3000 | Visualization |
| Alertmanager | 9093 | Alert routing |
| AI Responder | 5000 | AI diagnosis service |
| Nginx | 80 | Reverse proxy |

---

## 👤 Author

**Akshay** — Sysadmin transitioning to DevOps/SRE

- GitHub: [@akshaybk85](https://github.com/akshaybk85)