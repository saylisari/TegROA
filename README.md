# TegROA
### AI-Assisted Network Traffic Monitoring and Security Detection

TegROA is a network security monitoring project combining live traffic
capture, network event storage, rule-based security detection, and
machine-learning-based traffic analysis.

## Features

- Live TCP and UDP traffic monitoring using Scapy.
- TCP port scan detection.
- Network event and security alert storage.
- AI-based network flow classification.
- CICFlowMeter integration.
- FastAPI monitoring backend.
- PostgreSQL and SQLite database support.
- React and Tauri desktop application.
- Systemd-based continuous monitoring services.

## Architecture

```text
Network Interface
       |
       v
Scapy Live Capture
       |
       v
Network Events
       |
       +------> Live Port Scan Detector
       |                  |
       |                  v
       |             Security Alerts
       |
       v
CICFlowMeter
       |
       v
Feature Adapter
       |
       v
Machine Learning Inference
       |
       v
AI Predictions

FastAPI Backend
       |
       v
PostgreSQL / SQLite
       |
       v
React + Tauri Desktop UI
```

## Technology Stack

- Python 3.14
- FastAPI
- SQLAlchemy
- Scapy
- CICFlowMeter
- Random Forest
- Pandas and Joblib
- PostgreSQL / SQLite
- React 19
- Vite 8
- Tauri 2
- Rust

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | API information |
| GET | /api/health | Health check |
| POST | /api/events | Store network event |
| GET | /api/events | List network events |
| GET | /api/alerts | List security alerts |
| GET | /api/stats | Monitoring statistics |
| GET | /api/monitoring/status | Monitoring status |
| POST | /api/monitoring/start | Start monitoring |
| POST | /api/monitoring/stop | Stop monitoring |
| GET | /api/ai/predictions | AI predictions |

## Live Port Scan Detection

The rule-based detector monitors TCP SYN packets.

Default configuration:
- Threshold: 5 distinct destination ports.
- Detection window: 60 seconds.
- Alert type: LIVE_PORT_SCAN.
- Severity: medium.

## Laboratory Test Results

A controlled test was performed:

- Source IP: 192.168.77.10
- Destination IP: 192.168.77.20
- Interface: eth1
- Test: TCP port scan.

Verified database record:

- Alert ID: 2509
- Alert type: LIVE_PORT_SCAN
- Severity: medium
- Detection threshold: 5 distinct ports.

The test confirms successful rule-based detection and database persistence.

## AI Classification Status

The AI inference pipeline processed 859 network flows during testing.

The inspected predictions were classified as BENIGN.

Therefore, successful rule-based detection does not establish successful AI-based port scan classification. Further model validation is required.

## Running the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

API documentation: http://127.0.0.1:8000/docs

## Running the Desktop Application

```bash
cd desktop
npm install
npm run dev
```

Build:

```bash
npm run build
```

## Running Tests

```bash
cd backend
.venv/bin/python -m pytest
```

## Security

Never commit credentials, .env files, local databases, virtual environments, private traffic captures, or generated build artifacts.

See .gitignore for excluded files.

## Project Status

Rule-based live port scan detection and database persistence have been demonstrated in a controlled laboratory environment.

AI-based attack classification requires further validation.
