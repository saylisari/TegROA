from collections import defaultdict
from datetime import timedelta

from sqlalchemy import select

from app.database.db import SessionLocal
from app.database.models import NetworkEvent, SecurityAlert


def detect_port_scans(
    threshold: int = 5,
    window_seconds: int = 60
) -> int:
    """
    Detect possible TCP port scans from stored network events.

    A scan is detected when one source IP contacts at
    least `threshold` distinct destination ports on
    the same destination IP within `window_seconds`.
    """

    if threshold < 2 or window_seconds <= 0:
        raise ValueError("Invalid detection configuration")

    alerts_created = 0

    with SessionLocal() as db:
        events = db.scalars(
            select(NetworkEvent)
            .where(NetworkEvent.protocol == "TCP")
            .order_by(NetworkEvent.timestamp, NetworkEvent.id)
        ).all()

        groups = defaultdict(list)

        for event in events:
            key = (event.source_ip, event.destination_ip)
            groups[key].append(event)

        for (source_ip, destination_ip), records in groups.items():
            for index, current in enumerate(records):
                window_start = current.timestamp - timedelta(
                    seconds=window_seconds
                )

                recent = [
                    event
                    for event in records[:index + 1]
                    if event.timestamp >= window_start
                ]

                distinct_ports = {
                    event.destination_port
                    for event in recent
                }

                if len(distinct_ports) < threshold:
                    continue

                existing_alert = db.scalar(
                    select(SecurityAlert).where(
                        SecurityAlert.alert_type == "PORT_SCAN",
                        SecurityAlert.event_id == current.id
                    )
                )

                if existing_alert is not None:
                    continue

                alert = SecurityAlert(
                    event_id=current.id,
                    alert_type="PORT_SCAN",
                    severity="medium",
                    description=(
                        f"Possible TCP port scan: {source_ip} "
                        f"contacted {len(distinct_ports)} distinct "
                        f"ports on {destination_ip} within "
                        f"{window_seconds} seconds."
                    )
                )

                db.add(alert)
                alerts_created += 1

        db.commit()

    return alerts_created
