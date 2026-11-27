"""Two audio streams: interviewer (WASAPI loopback) and candidate (mic).
Saves 30 s WAV segments and exposes raw chunks for live STT (step 2)."""
import array, os, queue, threading, time, wave
import pyaudiowpatch as pyaudio

SEGMENT_SEC = 30
CHUNK_MS = 100
MIC_GAIN = 4.0  # candidate mic boost (laptop mics are quiet)


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
    def __init__(self, p, device, speaker, log, out_dir, gain=1.0):
        super().__init__(daemon=True)
        self.gain = gain
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

    def _write(self, data):
        """Write to the current segment, rolling to a new file every SEGMENT_SEC."""
        bpf = 2 * self.channels  # bytes per frame
        while data:
            room = (self.rate * SEGMENT_SEC - self._seg_frames) * bpf
            part, data = data[:room], data[room:]
            self._seg.writeframes(part)
            self._seg_frames += len(part) // bpf
            self.total_frames += len(part) // bpf
            if self._seg_frames >= self.rate * SEGMENT_SEC:
                self._seg.close(); self._seg_idx += 1; self._seg_frames = 0
                self._seg = self._new_segment(self._seg_idx)

    def _gain(self, data):
        if self.gain == 1.0:
            return data
        a = array.array("h", data)
        g = self.gain
        for i, x in enumerate(a):
            y = int(x * g)
            a[i] = 32767 if y > 32767 else (-32768 if y < -32768 else y)
        return a.tobytes()

    def run(self):
        stream = self.p.open(format=pyaudio.paInt16, channels=self.channels, rate=self.rate,
                             input=True, input_device_index=self.dev["index"],
                             frames_per_buffer=self.frames)
        self.log.log("audio_start", speaker=self.speaker, device=self.dev["name"],
                     rate=self.rate, channels=self.channels, gain=self.gain)
        self._seg_idx, self._seg_frames, self.total_frames = 0, 0, 0
        self._seg = self._new_segment(0)
        t0 = time.monotonic()
        try:
            while not self._stop.is_set():
                avail = stream.get_read_available()
                if avail > 0:
                    data = self._gain(stream.read(avail, exception_on_overflow=False))
                    self._write(data)
                    try:
                        self.live.put_nowait((self.log.now_ms(), data))
                    except queue.Full:
                        pass  # STT not consuming yet; file copy is kept
                else:
                    # Loopback sends nothing while the PC is silent: pad with silence
                    # so the file stays in sync with the session clock.
                    expected = int((time.monotonic() - t0) * self.rate)
                    missing = expected - self.total_frames
                    if missing > self.rate // 5:
                        self._write(b"\x00" * (missing * 2 * self.channels))
                    time.sleep(0.02)
        except OSError as e:  # device unplugged / changed
            self.log.log("audio_error", speaker=self.speaker, error=str(e))
        finally:
            self._seg.close(); stream.stop_stream(); stream.close()

    def stop(self):
        self._stop.set()


def start_audio(log, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    p = pyaudio.PyAudio()
    streams = [
        AudioStream(p, _loopback_device(p), "interviewer", log, out_dir),
        AudioStream(p, p.get_default_input_device_info(), "candidate", log, out_dir, gain=MIC_GAIN),
    ]
    for s in streams:
        s.start()
    return p, streams
