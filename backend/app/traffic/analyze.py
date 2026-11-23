from app.traffic.pcap_importer import import_pcap
from app.detection.port_scan import detect_port_scans


def analyze_pcap(file_path: str):
    imported = import_pcap(file_path)
    alerts = detect_port_scans(
        threshold=5,
        window_seconds=60
    )

    return {
        "imported_events": imported,
        "new_alerts": alerts
    }
