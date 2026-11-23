import subprocess
import threading


class MonitoringController:
    def __init__(self):
        self._process = None
        self._lock = threading.Lock()

    def status(self):
        with self._lock:
            running = (
                self._process is not None
                and self._process.poll() is None
            )
            return {"running": running}

    def start(self, command):
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                return {"status": "already_running"}

            self._process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return {"status": "started", "pid": self._process.pid}

    def stop(self):
        with self._lock:
            if self._process is None or self._process.poll() is not None:
                return {"status": "not_running"}

            self._process.terminate()

            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()

            self._process = None
            return {"status": "stopped"}


controller = MonitoringController()
