# CICFlowMeter Compatibility Notes

## Environment

- Python: 3.14
- CICFlowMeter: 0.5.0
- Operating system: Kali Linux

## Local Compatibility Changes

The development environment uses a locally modified installation of CICFlowMeter.

### 1. Command-Line Output Argument

File: `cicflowmeter/sniffer.py`

The argument parser accepts a positional `output` argument:

```python
parser.add_argument(
    "output",
    help="output file name (in csv mode), url (in url mode), or output directory (in directory mode)",
)
```

### 2. Flow Timestamp Initialization

File: `cicflowmeter/flow.py`

The flow constructor initializes timestamp attributes using the first packet:

```python
self.start_timestamp = packet.time
self.latest_timestamp = packet.time
self.protocol = packet.proto
```

The packet-processing logic calculates interarrival times and updates the latest timestamp.

### 3. Active/Idle Processing

The local implementation includes `update_active_idle(current_time)` and related timestamp handling.

## Reproducibility Limitations

These changes were made inside the local Python virtual environment. They are not automatically included when installing the published `cicflowmeter==0.5.0` package.

A fresh installation may require additional compatibility adjustments before live AI flow monitoring functions correctly.

The trained AI model file is excluded from the public repository. Therefore, the repository does not currently provide a fully reproducible AI deployment.
