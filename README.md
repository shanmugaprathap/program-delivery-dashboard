# Program Delivery Dashboard

An executive-facing program delivery dashboard built with Python and Streamlit. Demonstrates TPM skills in portfolio health tracking, milestone adherence, risk management, and SRE-aligned KPIs.

## Features

- **Executive Summary** — Clean leadership view with portfolio status, key highlights, and CSV export
- **Program Health** — Portfolio overview with status cards, completion bars, and program details
- **Milestone Tracker** — Gantt-style timeline, delivery predictability analysis, quarter navigation
- **Risk Management** — Risk heatmap (severity x likelihood), escalation tracking, risk trends
- **KPI Metrics** — DORA metrics (deploy frequency, lead time, CFR, MTTR), velocity trends, defect/incident tracking

## Architecture

```
app.py                          # Streamlit entry point, sidebar nav
├── src/data/
│   ├── models.py               # Pydantic models (Program, Milestone, RiskItem, etc.)
│   ├── mock_data.py            # 6 realistic programs with correlated data (seed=42)
│   ├── data_loader.py          # DataFrame interface, mock/JIRA abstraction
│   └── jira_client.py          # Optional JIRA REST API stub
├── src/pages/
│   ├── executive_summary.py    # Aggregated summary + export
│   ├── program_health.py       # Portfolio overview
│   ├── milestone_tracker.py    # Gantt + predictability
│   ├── risk_management.py      # Heatmap + escalations
│   └── kpi_metrics.py          # DORA + velocity + defects
├── src/components/
│   ├── status_cards.py         # Metric/status card renderers
│   ├── charts.py               # Plotly chart factories
│   ├── filters.py              # Shared filter widgets
│   └── tables.py               # Styled DataFrame displays
└── src/utils/
    ├── config.py               # YAML config loader
    ├── constants.py             # Colors, enums
    └── helpers.py               # Date utils, RAG logic
```

## Mock Data

Six programs telling a realistic portfolio story:

| Program | Status | % Complete | Department |
|---------|--------|-----------|------------|
| Cloud Platform Migration | On Track | 72% | Cloud Engineering |
| SRE Observability Rollout | On Track | 85% | SRE |
| Zero Trust Security | At Risk | 45% | Security |
| API Gateway Modernization | On Track | 60% | Platform |
| Disaster Recovery Automation | Off Track | 30% | SRE |
| Data Platform Consolidation | Completed | 100% | Data Engineering |

Each program includes correlated milestones, risks, escalations, and weekly delivery metrics.

## Setup

### Prerequisites

- Python 3.11+

### Install & Run

```bash
# Clone the repository
git clone https://github.com/shanmugaprathap/program-delivery-dashboard.git
cd program-delivery-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

The dashboard opens at http://localhost:8501.

### Configuration

```bash
# Copy example config
cp config/settings.example.yaml config/settings.yaml
```

Edit `config/settings.yaml` to switch between mock data and JIRA integration.

## Development

```bash
make install     # Install dependencies
make run         # Start Streamlit dev server
make test        # Run tests
make lint        # Check flake8, black, isort
make format      # Auto-format code
```

### JIRA Integration

To connect to JIRA instead of mock data:

1. Set `data_source: jira` in `config/settings.yaml`
2. Add your JIRA credentials (server, email, API token)
3. Implement the fetch functions in `src/data/jira_client.py`

## Tech Stack

- **Streamlit** — Dashboard framework
- **Plotly** — Interactive charts
- **Pandas** — Data manipulation
- **Pydantic** — Data validation and modeling
- **PyYAML** — Configuration management

## License

MIT
