from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.db import Base, engine, get_db
from app.database.models import NetworkEvent, SecurityAlert


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TegROA Security Monitoring API",
    version="0.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://tauri.localhost", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class EventInput(BaseModel):
    source_ip: str
    destination_ip: str
    destination_port: int = Field(ge=0, le=65535)
    protocol: str


@app.get("/")
def root():
    return {
        "application": "TegROA",
        "version": "0.2.0",
        "message": "Security monitoring backend is running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/events")
def create_event(event: EventInput, db: Session = Depends(get_db)):
    record = NetworkEvent(**event.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "status": "stored"}


@app.get("/api/events")
def list_events(db: Session = Depends(get_db)):
    records = db.scalars(
        select(NetworkEvent).order_by(NetworkEvent.id.desc()).limit(100)
    ).all()

    return [
        {
            "id": event.id,
            "source_ip": event.source_ip,
            "destination_ip": event.destination_ip,
            "destination_port": event.destination_port,
            "protocol": event.protocol
        }
        for event in records
    ]


@app.get("/api/alerts")
def list_alerts(db: Session = Depends(get_db)):
    records = db.scalars(
        select(SecurityAlert).order_by(SecurityAlert.id.desc()).limit(100)
    ).all()

    return [
        {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "description": alert.description
        }
        for alert in records
    ]


@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    from app.ml.models import AIFlowPrediction
    total_events = db.scalar(
        select(func.count()).select_from(NetworkEvent)
    ) or 0

    total_alerts = db.scalar(
        select(func.count()).select_from(SecurityAlert)
    ) or 0

    critical_alerts = db.scalar(
        select(func.count()).select_from(SecurityAlert)
        .where(SecurityAlert.severity == "critical")
    ) or 0

    total_ai_predictions = db.scalar(
        select(func.count()).select_from(AIFlowPrediction)
    ) or 0

    return {
        "total_events": total_events,
        "active_incidents": total_alerts,
        "critical_alerts": critical_alerts,
        "total_ai_predictions": total_ai_predictions,
        "monitoring_status": "database_ready"
    }


import subprocess


MONITOR_SERVICE = "tegroa-monitor.service"


@app.get("/api/monitoring/status")
def monitoring_status():
    result = subprocess.run(
        ["systemctl", "is-active", MONITOR_SERVICE],
        capture_output=True,
        text=True,
        timeout=5,
    )

    return {
        "running": result.stdout.strip() == "active",
        "status": result.stdout.strip(),
    }


@app.post("/api/monitoring/start")
def start_monitoring():
    result = subprocess.run(
        ["sudo", "-n", "systemctl", "start", MONITOR_SERVICE],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        return {
            "status": "error",
            "message": result.stderr.strip(),
        }

    return {"status": "started"}


@app.post("/api/monitoring/stop")
def stop_monitoring():
    result = subprocess.run(
        ["sudo", "-n", "systemctl", "stop", MONITOR_SERVICE],
        capture_output=True,
        text=True,
        timeout=15,
    )

    if result.returncode != 0:
        return {
            "status": "error",
            "message": result.stderr.strip(),
        }

    return {"status": "stopped"}


@app.get("/api/ai/predictions")
def get_ai_predictions():
    from app.database.db import SessionLocal
    from app.ml.models import AIFlowPrediction

    with SessionLocal() as db:
        predictions = (
            db.query(AIFlowPrediction)
            .order_by(AIFlowPrediction.id.desc())
            .limit(100)
            .all()
        )

        return [
            {
                "id": item.id,
                "timestamp": item.timestamp.isoformat(),
                "source_ip": item.source_ip,
                "destination_ip": item.destination_ip,
                "destination_port": item.destination_port,
                "prediction": item.prediction,
                "confidence": item.confidence,
            }
            for item in predictions
        ]
