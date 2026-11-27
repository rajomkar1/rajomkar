# AI Interview Simulator — Project Plan & Decisions

Saved project memory for the training-center interview simulator. Read this first in every new session.

## 1. Goal
A Windows desktop training tool that helps students practice real-company interviews
(any job profile: backend developer, data analyst, etc.), gives live coaching, and records
every session so trainers can measure improvement (target: 30–40% better performance).

## 2. Agreed design boundaries
- The student panel is **visible** (normal window, shows in screen-share).
- **No** hidden / screen-share-invisible mode that feeds answers live.
- **No** AI takeover of mouse/keyboard during a live interview. AI "demo mode"
  (AI solves the same task) runs only after the session or in solo practice.
- Live answer feed is for **practice sessions** (AI interviewer or a trainer who knows the tool is on).
- Students consent to recording (line in the admission form).

## 3. Features
**Before session**
- Job profile setup: JD text, skills, domain (e.g. hotel PMS: Python, Node.js, PostgreSQL,
  REST API, GitHub, AWS CloudFormation).
- Student profile: resume, background, degree, year (stored facts, inserted verbatim — never generated).
- GitHub prep: read every repo → tech stack per project, approach, workflow, why choices
  were made, major challenges, likely tricky questions + strong answers.

**During session**
- Capture: system audio (interviewer, WASAPI loopback) + microphone (student), separate streams.
- Live speaker-labeled transcript.
- Question detection → instant first line (≤1–2 s) → full streamed answer.
- Live check of student's answer: covered ✅ / missed ⚠️ / wrong ❌.
- Coding round: read problem + code (UI Automation first, OCR fallback); hint after a 2–3 s stall.
- Assistance levels: Full → Hints → Off.
- AI interviewer (voice) for solo practice.

**Recording (event logs, not video)**
- Mouse position / clicks / scrolls, keystrokes & shortcuts, active window / Excel cell,
  screen text snapshots, transcript, AI suggestions — all timestamped on one master clock.
- Saved as chat-style sessions (one session = full raw chronological log, no extra summaries).

**After session**
- Trainer website / Android app: live view, session replay, per-student history.
- "Watch AI do it" demo mode on the same task for side-by-side comparison.

## 4. Tech stack
| Layer | Choice |
|---|---|
| Desktop app | Python (Windows), tray app + visible panel |
| Audio | WASAPI loopback (system) + mic, two streams |
| Speech-to-text | Deepgram or AssemblyAI streaming (custom vocabulary from JD + GitHub); faster-whisper as local option |
| LLM — instant draft | Claude Haiku 5.5 (`claude-haiku-5-5`) |
| LLM — full answer | Claude Opus 5.5 (`claude-opus-5-5`), fast mode; Sonnet 5.5 (`claude-sonnet-5-5`) as cheaper option |
| LLM settings | Streaming, prompt caching (profile + GitHub notes + JD), server-side refusal fallbacks |
| Text-to-speech (AI interviewer) | ElevenLabs or Azure Speech |
| Backend | Own server holds API keys; app never stores keys |
| Storage | Compressed JSON-lines event logs, encrypted |
| Rough cost / 2-hr session | ~$1–4 LLM (Opus) + ~$0.5–1 STT |

## 5. Build order
1. Windows capture service (screen, system audio, mic, mouse/keyboard) + session storage
2. Live transcription with speaker labels
3. Interruption / cancellation logic + question detection
4. Answer engine (Haiku draft + Opus full) + student panel
5. GitHub & resume prep module
6. Trainer website / Android app
7. AI interviewer voice + AI demo mode

## 6. Known risks & fixes (checklist)
**Interruptions / turn-taking**
- Interviewer interrupts → cancel running answer, regenerate from newest question + context.
- Pause inside question → wait 700–1000 ms silence; cancel & regenerate if speech resumes.
- Non-questions ("okay", "good") → classify: question / follow-up / instruction / chit-chat.
- Follow-ups ("why not the other one?") → always send recent history.
- Multi-part questions → split and answer each part.
- Student already answering well → show only missing points.

**API**
- Cancelled stream: pay only for input + output generated so far; caching keeps retries cheap.
- 429 / 5xx → retry-after + fallback model; never show a blank panel.
- Budget runs out → pre-session balance check + spend alerts.
- Network drop → local audio buffer, reconnect, resend; autosave logs locally.
- Out-of-order answers → question IDs; display only answers for the latest question.
- `stop_reason: refusal` → handle + fallbacks.
- 2-hr context growth → recent turns in full, older summarized, fixed profile cached.

**Audio / STT**
- Tech words misheard → custom vocabulary.
- Echo → headphones required, or echo cancellation.
- Noise → suppression + voice-activity detection.
- Wrong output device / Bluetooth headset mode → device picker, sound test, auto-reconnect.

**Answer accuracy**
- Project hallucination → answer only from GitHub notes; else "Not in your project data".
- Resume facts → inserted verbatim.
- Too long / textbook → 2–3 spoken lines first, first person, simple words.
- Low confidence → mark ⚠️ and log for trainer review.
- Hidden traps / edge cases → prompt to check assumptions first.
- Stay consistent with student's earlier answers.

**Screen / coding**
- OCR misreads → UI Automation first; full-resolution capture; min font size.
- Scrolled code / switched tabs → merge snapshots; save problem text on first sight.
- False "stuck" hints → configurable stall time; verify snapshot is current.

**Windows / system**
- Antivirus flags → code signing + whitelist guide.
- Permissions → first-run wizard.
- CPU load → 1 fps capture, OCR only on change, cloud STT.
- Multi-monitor / DPI → record monitor + scale per event.
- Crash / sleep → autosave every few seconds, resume.

**Privacy**
- Keys on own server; pause key logging in password fields; encrypt sessions; retention policy.

## 7. First tests
1. Interruption test  2. Tech-word STT test (100 sentences)  3. Project-hallucination test (30 Qs)
4. Latency test (target < 2 s to first word)  5. Network-drop test (10 s Wi-Fi off)
