# TegROA — Automated Test Results

## Test Environment

- Operating system: Kali Linux
- Python: 3.14.8
- pytest: 9.2.0

## Test Execution

Command:

```bash
cd backend
.venv/bin/python -m pytest tests/ -v
```

## Results

| Test | Result |
|---|---|
| test_api.py::test_health | PASSED |
| test_api.py::test_initial_stats | PASSED |
| test_database.py::test_event_storage | PASSED |
| test_database.py::test_database_stats | PASSED |
| test_pcap_importer.py::test_pcap_importer | PASSED |
| test_port_scan.py::test_port_scan_detection | PASSED |

**Summary: 6 passed, 1 warning in 1.31 seconds.**

## Warning

The test run reported one StarletteDeprecationWarning related to httpx and starlette.testclient.
The warning did not cause any test failures.

## Scope and Limitations

These tests cover API behavior, database operations, PCAP importing, and rule-based port scan detection.
They do not establish complete validation of live AI threat detection or production deployment.
