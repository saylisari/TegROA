import argparse
import signal
from datetime import datetime, timezone

from scapy.all import sniff, IP, TCP, UDP

from app.database.db import SessionLocal
from app.database.models import NetworkEvent
from app.detection.live_port_scan import LivePortScanDetector


def capture_live(interface="eth0", count=10, timeout=20, continuous=False):
    saved = 0
    pending = []
    pending_syn = []
    detector = LivePortScanDetector()
    running = True

    def request_stop(signum, frame):
        nonlocal running
        running = False

    def save_batch(db):
        nonlocal saved

        if not pending:
            return

        db.add_all(pending)
        db.flush()

        alerts_created = 0

        for event in pending_syn:
            if detector.process(event, db):
                alerts_created += 1

        db.commit()
        saved += len(pending)
        pending.clear()
        pending_syn.clear()

        if alerts_created:
            print(f"New security alerts: {alerts_created}", flush=True)

        print(f"Saved events: {saved}", flush=True)

    def process(packet):
        if IP not in packet:
            return

        if TCP in packet:
            protocol = "TCP"
            port = int(packet[TCP].dport)
            flags = int(packet[TCP].flags)
            is_initial_syn = bool(flags & 0x02) and not bool(flags & 0x10)
        elif UDP in packet:
            protocol = "UDP"
            port = int(packet[UDP].dport)
        else:
            return

        event = NetworkEvent(
                timestamp=datetime.fromtimestamp(
                    float(packet.time),
                    tz=timezone.utc,
                ),
                source_ip=packet[IP].src,
                destination_ip=packet[IP].dst,
                destination_port=port,
                protocol=protocol,
            )

        pending.append(event)

        if protocol == "TCP" and is_initial_syn:
            event.tcp_syn = True
            pending_syn.append(event)

        if len(pending) >= 50:
            save_batch(db)

    previous_handler = signal.signal(signal.SIGTERM, request_stop)
    previous_interrupt_handler = signal.signal(signal.SIGINT, request_stop)

    try:
        with SessionLocal() as db:
            try:
                if continuous:
                    print(
                        f"Continuous capture started on {interface}",
                        flush=True,
                    )

                    while running:
                        sniff(
                            iface=interface,
                            filter="tcp or udp",
                            prn=process,
                            store=False,
                            timeout=5,
                            stop_filter=lambda packet: not running,
                        )
                        save_batch(db)
                else:
                    sniff(
                        iface=interface,
                        filter="tcp or udp",
                        prn=process,
                        store=False,
                        count=count,
                        timeout=timeout,
                    )
            finally:
                save_batch(db)
    finally:
        signal.signal(signal.SIGTERM, previous_handler)
        signal.signal(signal.SIGINT, previous_interrupt_handler)

    print(f"Capture finished. Total saved: {saved}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", default="eth0")
    parser.add_argument("--continuous", action="store_true")
    args = parser.parse_args()

    capture_live(
        interface=args.interface,
        continuous=args.continuous,
    )
