# TegROA — API Design

## Overview

The TegROA backend is built with FastAPI and exposes a local REST API.
API version: 0.2.0
Base URL: http://127.0.0.1:8000
Interactive documentation: http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | Application information |
| GET | /api/health | Backend health and UTC timestamp |
| POST | /api/events | Store a network event |
| GET | /api/events | Retrieve the latest 100 network events |
| GET | /api/alerts | Retrieve the latest 100 security alerts |
| GET | /api/stats | Retrieve dashboard statistics |
| GET | /api/monitoring/status | Check the network monitoring service |
| POST | /api/monitoring/start | Start the network monitoring service |
| POST | /api/monitoring/stop | Stop the network monitoring service |
| GET | /api/ai/predictions | Retrieve the latest 100 AI predictions |

## Network Event Input

POST /api/events accepts JSON with these fields:

| Field | Type | Validation |
|---|---|---|
| source_ip | string | Required |
| destination_ip | string | Required |
| destination_port | integer | 0 to 65535 |
| protocol | string | Required |

Successful storage returns an event ID and status "stored".

## Dashboard Statistics

GET /api/stats returns total_events, active_incidents, critical_alerts, total_ai_predictions, and monitoring_status.
The active_incidents field currently represents the total number of stored security alerts, not a separate incident lifecycle.
The monitoring_status field currently reports "database_ready" rather than the actual capture service state.

## Monitoring Controls

The start and stop endpoints control tegroa-monitor.service through systemctl.
They do not start or stop the separate tegroa-ai.service.
Service control requires appropriate local sudo permissions.

## Current Security Limitations

The API currently has no authentication or authorization layer.
It is bound to the local loopback address in the development deployment and must not be exposed publicly without additional security controls.
