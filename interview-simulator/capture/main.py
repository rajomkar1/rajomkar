"""Step 1: Windows capture service.
Usage:  python main.py --code ABC123 [--out sessions]
Stops with Ctrl+C. Everything is saved under sessions/<time>_<code>/."""
import argparse, os, signal, threading
from session_log import SessionLog


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", required=True, help="Practice session code from the trainer")
    ap.add_argument("--out", default="sessions")
    args = ap.parse_args()

    from screen import ScreenCapture, set_dpi_aware
    from input_events import InputCapture
    from audio import start_audio

    set_dpi_aware()
    log = SessionLog(args.out, args.code)
    print(f"PRACTICE SESSION {args.code} recording -> {log.dir}  (Ctrl+C to stop)")

    pa, streams = start_audio(log, os.path.join(log.dir, "audio"))
    screen = ScreenCapture(log, os.path.join(log.dir, "screen")); screen.start()
    inputs = InputCapture(log); inputs.start()

    done = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: done.set())
    while not done.wait(0.5):
        pass

    inputs.stop(); screen.stop()
    for s in streams:
        s.stop()
    for s in streams:
        s.join(timeout=2)
    screen.join(timeout=2)
    pa.terminate()
    log.close()
    print("Saved:", log.dir)


if __name__ == "__main__":
    main()
