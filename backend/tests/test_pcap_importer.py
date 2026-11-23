from scapy.all import IP, TCP, UDP, wrpcap
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.db import Base
from app.database.models import NetworkEvent
from app.traffic import pcap_importer


def test_pcap_importer(tmp_path, monkeypatch):
    pcap_file = tmp_path / "test_traffic.pcap"

    packets = [
        IP(src="192.0.2.10", dst="192.0.2.20")
        / TCP(sport=50001, dport=22),

        IP(src="192.0.2.11", dst="192.0.2.20")
        / UDP(sport=50002, dport=53),
    ]

    wrpcap(str(pcap_file), packets)

    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}"
    )
    Base.metadata.create_all(engine)

    def test_session():
        return Session(engine)

    monkeypatch.setattr(
        pcap_importer,
        "SessionLocal",
        test_session
    )

    count = pcap_importer.import_pcap(str(pcap_file))

    assert count == 2

    with Session(engine) as db:
        events = db.scalars(
            select(NetworkEvent).order_by(NetworkEvent.id)
        ).all()

        assert len(events) == 2
        assert events[0].destination_port == 22
        assert events[0].protocol == "TCP"
        assert events[1].destination_port == 53
        assert events[1].protocol == "UDP"

    engine.dispose()
