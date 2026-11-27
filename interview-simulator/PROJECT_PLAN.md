# AI Interview Practice Assistant — Project Plan & Decisions

Saved project memory. Read this first in every new session.

## 1. Goal
A Windows desktop practice assistant for a training center. During practice interviews
(student and interviewer both know it is practice), it listens, reads the screens, and gives
the candidate live, short, human-style answers and hints. Every session is saved as a raw
chronological log for trainers to review manually.

## 2. Agreed decisions
- **Desktop app (.exe)** for the candidate's Windows PC (Python core + PyQt always-on-top panel,
  signed installer). Trainer side (session codes, reading logs) can be a simple website later.
- App runs **only on the candidate's computer**. Interviewer needs nothing.
- **Practice only**: window always visible (no hidden / screen-share-excluded mode),
  "PRACTICE SESSION" label on the panel, sessions start with a session code from the trainer.
- **No** scores, skill maps, dashboards or webcam analysis — trainers analyse logs manually
  (saves tokens and storage).
- Student data (name, resume, GitHub, background) is treated as real data.
- AI takeover of mouse/keyboard is not part of interviews (it was only a feasibility question).

## 3. Before the session
- Inputs: role / JD, resume, background, GitHub repo links.
- Read every repo: tech stack per project, approach, workflow, why choices were made, challenges.
- Pre-generate ~100 likely questions with ready answers (instant display for common questions).
- Build STT custom vocabulary from JD + project tech words.

## 4. The three agents

### Agent 1 — Listener (background only, never shows anything)
Keeps a live interview state, updated every second:
- Speaker: interviewer / candidate / silence (separate audio streams)
- Speech type: new question / sub-question / follow-up / instruction / small talk
- Round type (auto): technical / HR / client / group discussion / system design / practical
- Difficulty (for the AI only): easy / medium / hard / trap
- Topic source: general concept / resume / project X / JD domain
- Language: English / Hindi / Hinglish
- What the candidate already said
- Screen context: problem on screen, whiteboard, candidate editor, interviewer's shared screen
- Writes everything to the session log

### Agent 2 — Answer (main answer for each new question)
- Starts preparing from the partial question while interviewer is still speaking;
  streams once ~700 ms silence; first line in ~1 s; discards draft if the question changes.
- Style: 3–5 short lines, simple common words, natural Indian English,
  spoken order "what it is → how we used it → why". No textbook definitions.
- General concept → one-line idea + "in Python we do it like this…" (candidate's stack).
- Project question → only from GitHub notes; else "⚠️ Not in your project data".
- Resume facts → inserted verbatim.
- Depth follows Listener difficulty; trap questions check the hidden catch first.

### Agent 3 — Coach (instant help in the middle of things)
- A. Sub-question mid-answer → short answer in 2–5 s + one-line "come back" to main answer.
- B. Candidate stuck (long pause, repeated fillers, trailing sentence) → only the next missed point.
- C. Coding / practical round (any screen) → full answer first, background test, update if a fix
  is found; typing hints after 2–3 s stall or mistake (next word, click Run, Ctrl+S); works for
  code, Excel, SQL.
- D. Hotkeys: **F8** stuck (force fresh answer), **F9** retry with stronger model,
  **F10** make it shorter.

## 5. Tech stack
| Layer | Choice |
|---|---|
| Audio | WASAPI loopback (interviewer) + mic (candidate), two streams |
| STT | Deepgram or AssemblyAI streaming + custom vocabulary; faster-whisper local option |
| Fast draft | Claude Haiku 5.5 (`claude-haiku-5-5`) — Listener classification + first line |
| Full answer / Coach | Claude Opus 5.5 (`claude-opus-5-5`), fast mode; Sonnet 5.5 (`claude-sonnet-5-5`) cheaper option |
| LLM settings | Streaming, prompt caching (profile + GitHub notes + JD), refusal fallbacks |
| Screen | Windows UI Automation first, OCR fallback |
| Code test | Local sandbox run in background |
| Keys | Held on own server, never inside the .exe |
| Storage | Compressed JSON-lines session logs, encrypted |
| Rough cost / 2-hr session | ~$1–4 LLM (Opus) + ~$0.5–1 STT |

## 6. Risks & fixes — mapped to the three agents
Owner: **L** = Listener, **A** = Answer, **C** = Coach, **S** = System / app core.

### 6.1 Interruptions & turn-taking
| Situation | Owner | Fix |
|---|---|---|
| Interviewer interrupts mid-question / changes question | L → A | L marks new question; A cancels running stream, regenerates from newest question + context |
| Interviewer interrupts candidate's answer with sub-question | L → C | C answers sub-question in 2–5 s + "come back" line; A's main answer stays on panel |
| Pause inside a question | L | Wait 700–1000 ms silence; if speech resumes, cancel and regenerate |
| Non-question ("okay", "nice", "share your screen") | L | Classified as small talk / instruction; nothing shown, no tokens spent |
| Follow-up ("why not the other one?") | L → A | L passes recent history so A resolves "the other one" |
| Multi-part question | A | Split into ① ② and answer each |
| Candidate already answering well | L → C | C shows only missing points, never repeats |
| Candidate stuck mid-answer | L → C | Long pause / fillers detected; C shows the next point only |
| Round changes (technical → HR) | L → A | Round type switches automatically; A changes style |
| Group discussion | L → A | Track other speakers' points; suggest entry line + counter-point |
| Answers arrive out of order | S | Every question has an ID; panel shows only answers for the latest ID |

### 6.2 API & tokens
| Situation | Owner | Fix |
|---|---|---|
| Stream cancelled after interruption | S | Pay only input + output generated so far; cached profile keeps retries cheap |
| Rate limit 429 / API 5xx / overloaded | S | Retry-after + fallback model; panel shows "retrying…", never blank |
| Budget / credits run out | S | Balance check before session, spend alerts, low-budget warning |
| Internet drops 5–10 s | S | Local audio buffer, reconnect, resend missed audio; log autosaved locally |
| Answer too slow | A | Prepared answers, Haiku first line, Opus fast mode, streaming, small prompts |
| Refusal (`stop_reason: refusal`) | S | Handle + server-side fallbacks |
| Context grows over 2 hours | L | Recent turns in full, older turns summarized, fixed profile cached |
| Tokens wasted on small talk | L | Classifier filters before calling A or C |

### 6.3 Audio & speech-to-text
| Situation | Owner | Fix |
|---|---|---|
| Tech words misheard | S / L | Custom vocabulary from JD + GitHub; L corrects using context |
| Accents, fast speech | S | Indian-English capable STT; tested on real recordings |
| Hindi / Hinglish | L | Multilingual STT; L understands, A answers in simple English |
| Echo (speakers → mic) | S | Headphones required, or echo cancellation |
| Background noise / keyboard sound | S | Noise suppression + voice-activity detection |
| Wrong output device / Bluetooth headset mode | S | Device picker + sound test at start; auto-reconnect on device change |
| Low interviewer volume / laggy call | S / C | Volume normalize; F8 resends last 10 s |

### 6.4 Answer accuracy (most important)
| Situation | Owner | Fix |
|---|---|---|
| Invents project details | A | Project answers only from GitHub notes; else "⚠️ Not in your project data" |
| Wrong resume facts | A | Fixed facts inserted verbatim, never generated |
| Too long / textbook | A | 3–5 short human lines, simple words |
| Wrong on tricky question | A / C | Trap check first; F9 retry with stronger model + deeper thinking |
| Generic answer, not candidate's stack | A | "In Python we do it like this…" rule; JD domain in cached context |
| Contradicts candidate's earlier words | L → A | L passes what candidate already said |
| Wrong coding solution | C | Answer shown first, tested in background, panel updated with the fix |

### 6.5 Screen reading (coding, practical, whiteboard)
| Situation | Owner | Fix |
|---|---|---|
| OCR misreads code (l/1, O/0, indentation) | S | UI Automation first; full-resolution capture; OCR fallback |
| Small font / dark theme | S | Full-resolution capture; recommend minimum font size |
| Code scrolled out of view | L | Merge snapshots over time; note unseen parts |
| Problem on interviewer's shared screen / whiteboard | L | Read shared screen in Zoom/Meet window automatically; save problem text on first sight |
| Tab switched, problem disappears | L | Problem text already saved |
| False "stuck" hint while candidate is thinking | C | Adjustable stall time; hint only on real stall or error |
| Hint about code already fixed | C | Re-check latest snapshot before showing |

### 6.6 Windows & system
| Situation | Owner | Fix |
|---|---|---|
| Antivirus flags keyboard/screen capture | S | Code-signed .exe + whitelist guide |
| Mic / screen permissions | S | First-run setup wizard tests each one |
| High CPU on weak laptops | S | 1 fps capture, OCR only on change, cloud STT |
| Multi-monitor / DPI scaling | S | Store monitor + scale with every event |
| Crash / sleep mid-session | S | Autosave every few seconds; resume on restart |
| Clock mismatch audio / screen / keys | S | One master clock for all timestamps |
| API keys stolen from .exe | S | Keys on own server only |
| Passwords captured by key logging | S | Pause logging in password fields and login windows |

## 7. Build order
1. Windows capture service (system audio, mic, screen, mouse/keyboard) + session log storage
2. Live STT with speaker labels, Hinglish, custom vocabulary
3. Listener agent (classification, round, difficulty, state) + interruption/cancel logic
4. Answer agent + visible practice panel
5. Coach agent + hotkeys F8/F9/F10 + background code testing
6. Pre-session prep (GitHub/resume reading, prepared answers)
7. Trainer website (session codes, log viewer)

## 8. First tests
1. Interruption test (old answer cancelled, sub-question handled by Coach)
2. Tech-word STT test (100 sentences)
3. Project-hallucination test (30 questions, some about things not in the projects)
4. Latency test (< 2 s to first word; prepared answers instant)
5. Network-drop test (10 s Wi-Fi off)
6. Round-switch test (technical → HR → system design without any selection)
