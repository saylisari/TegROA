import signal
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parents[2]
SESSION_ID = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
FLOW_FILE = BASE_DIR / f"runtime/ai/continuous/live_flows_{SESSION_ID}.csv"


def main():
    FLOW_FILE.parent.mkdir(parents=True, exist_ok=True)

    commands = [
        [
            str(BASE_DIR / ".venv/bin/cicflowmeter"),
            "-i", "eth0",
            "-c", str(FLOW_FILE),
        ],
        [
            sys.executable,
            "-m", "app.ml.live_inference",
            str(FLOW_FILE),
            "--watch",
        ],
    ]

    processes = []

    try:
        for command in commands:
            processes.append(
                subprocess.Popen(command, cwd=BASE_DIR)
            )

        print("Continuous AI monitoring started", flush=True)

        while True:
            for process in processes:
                if process.poll() is not None:
                    print(
                        f"Monitoring process exited: {process.returncode}",
                        flush=True,
                    )
                    return

            import time
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping continuous AI monitoring", flush=True)

    finally:
        if processes:
            capture = processes[0]

            if capture.poll() is None:
                capture.send_signal(signal.SIGINT)

            try:
                capture.wait(timeout=20)
            except subprocess.TimeoutExpired:
                capture.terminate()
                capture.wait(timeout=5)

        if len(processes) > 1:
            inference = processes[1]

            if inference.poll() is None:
                print("Waiting for final AI flow analysis", flush=True)
                import time
                time.sleep(7)
                inference.send_signal(signal.SIGINT)

            try:
                inference.wait(timeout=10)
            except subprocess.TimeoutExpired:
                inference.terminate()
                inference.wait(timeout=5)

        print("Continuous AI monitoring stopped", flush=True)


if __name__ == "__main__":
    main()
