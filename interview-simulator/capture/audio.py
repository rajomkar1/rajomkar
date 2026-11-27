"""Two audio streams: interviewer (WASAPI loopback) and candidate (mic).
Saves 30 s WAV segments and exposes raw chunks for live STT (step 2)."""
import os, queue, threading, wave
import pyaudiowpatch as pyaudio

SEGMENT_SEC = 30
CHUNK_MS = 100


def _loopback_device(p):
    wasapi = p.get_host_api_info_by_type(pyaudio.paWASAPI)
    spk = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
    if spk.get("isLoopbackDevice"):
        return spk
    for dev in p.get_loopback_device_info_generator():
        if spk["name"] in dev["name"]:
            return dev
    raise RuntimeError("No WASAPI loopback device found for the default speakers.")


class AudioStream(threading.Thread):
    def __init__(self, p, device, speaker, log, out_dir):
        super().__init__(daemon=True)
        self.p, self.dev, self.speaker, self.log = p, device, speaker, log
        self.out_dir = out_dir
        self.rate = int(device["defaultSampleRate"])
        self.channels = max(1, min(2, int(device["maxInputChannels"])))
        self.frames = int(self.rate * CHUNK_MS / 1000)
        self.live: "queue.Queue[tuple[int, bytes]]" = queue.Queue(maxsize=600)  # for STT
        self._stop = threading.Event()

    def _new_segment(self, idx):
        path = os.path.join(self.out_dir, f"{self.speaker}_{idx:04d}.wav")
        w = wave.open(path, "wb")
        w.setnchannels(self.channels); w.setsampwidth(2); w.setframerate(self.rate)
        self.log.log("audio_segment", speaker=self.speaker, file=os.path.basename(path))
        return w

    def run(self):
        stream = self.p.open(format=pyaudio.paInt16, channels=self.channels, rate=self.rate,
                             input=True, input_device_index=self.dev["index"],
                             frames_per_buffer=self.frames)
        self.log.log("audio_start", speaker=self.speaker, device=self.dev["name"],
                     rate=self.rate, channels=self.channels)
        idx, written = 0, 0
        seg = self._new_segment(idx)
        try:
            while not self._stop.is_set():
                data = stream.read(self.frames, exception_on_overflow=False)
                seg.writeframes(data)
                try:
                    self.live.put_nowait((self.log.now_ms(), data))
                except queue.Full:
                    pass  # STT not consuming yet; drop live copy, file copy is kept
                written += self.frames
                if written >= self.rate * SEGMENT_SEC:
                    seg.close(); idx += 1; written = 0
                    seg = self._new_segment(idx)
        except OSError as e:  # device unplugged / changed
            self.log.log("audio_error", speaker=self.speaker, error=str(e))
        finally:
            seg.close(); stream.stop_stream(); stream.close()

    def stop(self):
        self._stop.set()


def start_audio(log, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    p = pyaudio.PyAudio()
    streams = [
        AudioStream(p, _loopback_device(p), "interviewer", log, out_dir),
        AudioStream(p, p.get_default_input_device_info(), "candidate", log, out_dir),
    ]
    for s in streams:
        s.start()
    return p, streams
