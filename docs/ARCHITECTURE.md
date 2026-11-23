# TegROA — System Architecture and Design

## System Overview

TegROA combines network traffic collection, rule-based port-scan detection, machine-learning inference, PostgreSQL storage, a FastAPI backend, and a React/Tauri desktop dashboard.

## System Architecture

Network Traffic / PCAP Files
    |
    v
Scapy Traffic Collection
    |
    +--> Network Events --> PostgreSQL
    |
    +--> Port-Scan Detection --> Security Alerts --> PostgreSQL
    |
    +--> CICFlowMeter --> Feature Adapter --> Random Forest
                                               |
                                               v
                                        AI Predictions
                                               |
                                               v
                                           PostgreSQL
                                               |
                                               v
                                         FastAPI REST API
                                               |
                                               v
                                      React / Tauri Desktop

## Main System Components

### Traffic Collection
Scapy captures TCP and UDP packets from network interfaces and imports supported packets from PCAP files.

### Rule-Based Threat Detection
The live detector analyzes initial TCP SYN packets and identifies potential port scans using distinct destination ports within a time window.

### Machine Learning
CICFlowMeter extracts network flow features. A feature adapter prepares the features for a Random Forest classifier trained on CIC-IDS2017 PortScan data.

### PostgreSQL Database
The database stores network events, security alerts, and AI flow predictions.

### FastAPI Backend
The backend provides REST endpoints for monitoring statistics, events, alerts, predictions, and monitoring controls.

### Desktop Application
The React and Tauri desktop dashboard displays network statistics, recent events, security alerts, and AI predictions.

## Security Considerations

- Database credentials are loaded from environment variables.
- Secrets, packet captures, and runtime data are excluded from the public repository.
- Live packet capture uses restricted Linux capabilities.
- API authentication and authorization require further hardening before production deployment.

## Verified Tests

- PCAP traffic import into PostgreSQL was tested.
- A controlled TCP SYN port scan generated a live security alert.
- Continuous network traffic collection was observed.
- AI flow predictions were stored in PostgreSQL and displayed in the desktop dashboard.

## Known Limitations

- Live AI detection of malicious port-scan flows has not yet been validated.
- Dataset evaluation accuracy does not guarantee real-world detection accuracy.
- Desktop Start/Stop controls require integration testing across both monitoring services.
- CICFlowMeter compatibility patches must be documented for reproducible installation.

## Future Improvements

- Complete monitoring-service coordination.
- Expand automated security and integration tests.
- Improve deployment documentation and reproducibility.
- Add stronger API access controls.
