"""1 fps screen capture; saves a PNG only when the screen changes.
Also logs the active window (title, process, monitor, DPI)."""
import ctypes, hashlib, os, threading, time
import mss, mss.tools, psutil

user32 = ctypes.windll.user32


def set_dpi_aware():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor aware
    except Exception:
        user32.SetProcessDPIAware()


def active_window():
    hwnd = user32.GetForegroundWindow()
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        proc = psutil.Process(pid.value).name()
    except Exception:
        proc = "?"
    try:
        dpi = user32.GetDpiForWindow(hwnd)
    except Exception:
        dpi = 96
    return {"title": buf.value, "process": proc, "dpi": dpi}


class ScreenCapture(threading.Thread):
    def __init__(self, log, out_dir, fps=1.0):
        super().__init__(daemon=True)
        self.log, self.out_dir, self.interval = log, out_dir, 1.0 / fps
        self._stop = threading.Event()
        os.makedirs(out_dir, exist_ok=True)

    def run(self):
        last_hash, last_win = {}, None
        with mss.mss() as sct:
            monitors = sct.monitors[1:]
            self.log.log("monitors", list=[dict(m) for m in monitors])
            while not self._stop.is_set():
                t0 = time.monotonic()
                win = active_window()
                if win != last_win:
                    self.log.log("active_window", **win); last_win = win
                for i, mon in enumerate(monitors):
                    img = sct.grab(mon)
                    h = hashlib.md5(img.bgra[::64]).hexdigest()  # sampled: cheap
                    if h != last_hash.get(i):
                        last_hash[i] = h
                        name = f"m{i}_{self.log.now_ms():09d}.png"
                        mss.tools.to_png(img.rgb, img.size, output=os.path.join(self.out_dir, name))
                        self.log.log("screen", monitor=i, file=name)
                self._stop.wait(max(0, self.interval - (time.monotonic() - t0)))

    def stop(self):
        self._stop.set()
