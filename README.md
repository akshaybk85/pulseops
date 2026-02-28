✅ loki          → port 3100
✅ prometheus    → port 9090
✅ grafana       → port 3000
✅ alertmanager  → port 9093
✅ node-exporter → port 9100
✅ promtail      → running

Here's a clean copy:

---

**Grafana** → http://localhost:3000

**Prometheus** → http://localhost:9090

**Alertmanager** → http://localhost:9093

**Loki** → http://localhost:3100/ready

🚀 Now Setup Grafana Data Sources
Open http://localhost:3000 and login.
Add Prometheus:

Left sidebar → Connections → Data Sources
Click Add data source → Select Prometheus
URL: http://prometheus:9090
Click Save & Test → should show ✅

Add Loki:

Click Add data source again → Select Loki
URL: http://loki:3100
Click Save & Test → should show ✅

 Now Import Dashboards
Dashboard 1 — Node Exporter (System Metrics)

Left sidebar → Dashboards → New → Import
Type 1860 → Click Load
Select Prometheus as data source
Click Import

Dashboard 2 — Loki Logs

Left sidebar → Dashboards → New → Import
Type 13639 → Click Load
Select Loki as data source
Click Import