"""Mouse + keyboard events. Mouse moves throttled to 10/s.
Key text is not recorded while a password/login window is focused."""
import time
from pynput import keyboard, mouse
from screen import active_window

SENSITIVE = ("password", "sign in", "log in", "login", "otp", "pin")
MOVE_INTERVAL = 0.1


class InputCapture:
    def __init__(self, log):
        self.log = log
        self._last_move = 0.0
        self._sensitive = False
        self._last_check = 0.0
        self.m = mouse.Listener(on_move=self._move, on_click=self._click, on_scroll=self._scroll)
        self.k = keyboard.Listener(on_press=self._press)

    def _is_sensitive(self):
        now = time.monotonic()
        if now - self._last_check > 0.5:
            title = active_window()["title"].lower()
            self._sensitive = any(w in title for w in SENSITIVE)
            self._last_check = now
        return self._sensitive

    def _move(self, x, y):
        now = time.monotonic()
        if now - self._last_move >= MOVE_INTERVAL:
            self._last_move = now
            self.log.log("mouse_move", x=x, y=y)

    def _click(self, x, y, button, pressed):
        self.log.log("mouse_click", x=x, y=y, button=button.name, pressed=pressed)

    def _scroll(self, x, y, dx, dy):
        self.log.log("mouse_scroll", x=x, y=y, dx=dx, dy=dy)

    def _press(self, key):
        if self._is_sensitive():
            self.log.log("key", hidden=True)
            return
        k = key.char if hasattr(key, "char") and key.char else str(key).replace("Key.", "")
        self.log.log("key", key=k)

    def start(self):
        self.m.start(); self.k.start()

    def stop(self):
        self.m.stop(); self.k.stop()
