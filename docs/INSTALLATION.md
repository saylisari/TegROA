# TegROA — Installation and Setup Guide

## Supported Development Environment

TegROA was developed and tested on Kali Linux in a VirtualBox environment.

The backend uses Python, FastAPI, PostgreSQL, and Scapy. The desktop application uses React and Tauri.

## Prerequisites

- Kali Linux or a compatible Linux distribution
- Python and pip
- PostgreSQL server
- Node.js and npm
- Rust and Cargo for building the Tauri application
- Network capture permissions for live monitoring

## Python Backend Setup

From the backend directory, create a Python virtual environment and install the listed dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Note: Additional CICFlowMeter compatibility adjustments are required and will be documented separately.

Note: The trained AI model is not included in this public repository.

## PostgreSQL Configuration

Install and start PostgreSQL before running the backend.

Create a dedicated database and database user with appropriate permissions.

The application reads its database connection from the DATABASE_URL environment variable.

Example configuration:

```text
DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/tegroa_db
```

Replace the placeholders with your own database credentials.
Never commit real passwords or local .env files to GitHub.

The database connection is configured in backend/app/database/db.py.

Database models are defined in backend/app/database/models.py and backend/app/ml/models.py.

## Running the FastAPI Backend

Activate the Python virtual environment from the backend directory:

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The API will be available at http://127.0.0.1:8000.
Interactive API documentation is available at http://127.0.0.1:8000/docs.

On the development machine, the backend also runs as a systemd service named tegroa-backend.service.
The service loads database settings from backend/.env and starts after PostgreSQL.

The systemd unit contains machine-specific paths and must be adapted for other installations.

## Running the Desktop Application

Open a terminal in the desktop directory and install the JavaScript dependencies:

```bash
npm install
```

Start the React/Vite development interface:

```bash
npm run dev
```

To launch the full Tauri desktop application, use:

```bash
npx tauri dev
```

To build a production desktop package, use:

```bash
npx tauri build
```

The Tauri commands require Rust and the appropriate Linux system libraries.
The FastAPI backend must be running separately for live dashboard data.
