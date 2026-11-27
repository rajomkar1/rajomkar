"""Session log: one master clock + crash-safe JSON-lines writer."""
import gzip, json, os, queue, shutil, threading, time
from datetime import datetime, timezone


class SessionLog:
    def __init__(self, out_dir: str, session_code: str):
        self.session_code = session_code
        self.start_wall = datetime.now(timezone.utc)
        self._t0 = time.monotonic()
        stamp = self.start_wall.strftime("%Y%m%d_%H%M%S")
        self.dir = os.path.join(out_dir, f"{stamp}_{session_code}")
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, "events.jsonl")
        self._q: "queue.Queue[dict | None]" = queue.Queue()
        self._thread = threading.Thread(target=self._writer, daemon=True)
        self._thread.start()
        self.log("session_start", code=session_code, wall=self.start_wall.isoformat())

    def now_ms(self) -> int:
        """Master clock: ms since session start. Every module uses this."""
        return int((time.monotonic() - self._t0) * 1000)

    def log(self, type_: str, **data):
        self._q.put({"t": self.now_ms(), "type": type_, **data})

    def _writer(self):
        # Line-buffered plain text, flushed every ~2 s: survives crashes.
        with open(self.path, "a", encoding="utf-8") as f:
            last_flush = time.monotonic()
            while True:
                try:
                    ev = self._q.get(timeout=0.5)
                except queue.Empty:
                    ev = ...
                if ev is None:
                    break
                if ev is not ...:
                    f.write(json.dumps(ev, ensure_ascii=False) + "\n")
                if time.monotonic() - last_flush > 2:
                    f.flush(); os.fsync(f.fileno()); last_flush = time.monotonic()
            f.flush()

    def close(self):
        self.log("session_end")
        self._q.put(None)
        self._thread.join()
        with open(self.path, "rb") as src, gzip.open(self.path + ".gz", "wb") as dst:
            shutil.copyfileobj(src, dst)
        os.remove(self.path)
