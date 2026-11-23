from collections import defaultdict, deque
from datetime import timedelta

from app.database.models import SecurityAlert


class LivePortScanDetector:
    def __init__(self, threshold=5, window_seconds=60):
        if threshold < 2 or window_seconds <= 0:
            raise ValueError("Invalid detection configuration")

        self.threshold = threshold
        self.window = timedelta(seconds=window_seconds)
        self.history = defaultdict(deque)
        self.last_alert = {}

    def process(self, event, db):
        if event.protocol != "TCP":
            return False

        if not getattr(event, "tcp_syn", False):
            return False

        key = (event.source_ip, event.destination_ip)
        timestamp = event.timestamp
        records = self.history[key]

        records.append((timestamp, event.destination_port))

        cutoff = timestamp - self.window

        while records and records[0][0] < cutoff:
            records.popleft()

        distinct_ports = {port for _, port in records}

        if len(distinct_ports) < self.threshold:
            return False

        previous = self.last_alert.get(key)

        if previous is not None and timestamp - previous < self.window:
            return False

        alert = SecurityAlert(
            event_id=event.id,
            alert_type="LIVE_PORT_SCAN",
            severity="medium",
            description=(
                f"Possible live TCP port scan: {event.source_ip} "
                f"contacted {len(distinct_ports)} distinct ports "
                f"on {event.destination_ip} within "
                f"{int(self.window.total_seconds())} seconds."
            ),
        )

        db.add(alert)
        self.last_alert[key] = timestamp
        return True
