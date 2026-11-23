from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.db import Base
from app.database.models import NetworkEvent, SecurityAlert
from app.detection import port_scan


def test_port_scan_detection(tmp_path, monkeypatch):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'detection_test.db'}"
    )
    Base.metadata.create_all(engine)

    def test_session():
        return Session(engine)

    monkeypatch.setattr(
        port_scan,
        "SessionLocal",
        test_session
    )

    start_time = datetime.now(timezone.utc)

    with Session(engine) as db:
        for index, port in enumerate(
            [21, 22, 23, 80, 443, 8080]
        ):
            db.add(
                NetworkEvent(
                    source_ip="198.51.100.10",
                    destination_ip="198.51.100.20",
                    destination_port=port,
                    protocol="TCP",
                    timestamp=start_time + timedelta(
                        seconds=index
                    )
                )
            )

        db.commit()

    count = port_scan.detect_port_scans(
        threshold=5,
        window_seconds=60
    )

    assert count == 2

    with Session(engine) as db:
        alerts = db.scalars(
            select(SecurityAlert)
        ).all()

        assert len(alerts) == 2
        assert all(
            alert.alert_type == "PORT_SCAN"
            for alert in alerts
        )
        assert all(
            alert.severity == "medium"
            for alert in alerts
        )

    engine.dispose()
