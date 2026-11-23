import sys
from app.traffic.analyze import analyze_pcap

if len(sys.argv) != 2:
    print("Usage: python analyze_traffic.py <file.pcap>")
    sys.exit(1)

result = analyze_pcap(sys.argv[1])

print("Imported events:", result["imported_events"])
print("New security alerts:", result["new_alerts"])
