from pathlib import Path
from datetime import datetime, timezone

from scapy.all import IP, TCP, UDP, PcapReader

from app.database.db import SessionLocal
from app.database.models import NetworkEvent


def import_pcap(file_path: str) -> int:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"PCAP file not found: {path}")

    imported_count = 0
    batch_size = 1000

    with SessionLocal() as db:
        with PcapReader(str(path)) as packets:
            for packet in packets:
                if IP not in packet:
                    continue

                if TCP in packet:
                    protocol = "TCP"
                    destination_port = int(packet[TCP].dport)
                elif UDP in packet:
                    protocol = "UDP"
                    destination_port = int(packet[UDP].dport)
                else:
                    continue

                event = NetworkEvent(
                    timestamp=datetime.fromtimestamp(
                        float(packet.time),
                        tz=timezone.utc
                    ),
                    source_ip=packet[IP].src,
                    destination_ip=packet[IP].dst,
                    destination_port=destination_port,
                    protocol=protocol,
                )

                db.add(event)
                imported_count += 1

                if imported_count % batch_size == 0:
                    db.commit()
                    db.expunge_all()

        db.commit()

    return imported_count
