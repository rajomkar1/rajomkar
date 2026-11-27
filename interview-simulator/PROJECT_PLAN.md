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

### Agent flow
```
            ┌────────────────────────────────────┐
 Audio ───▶ │  AGENT 1: LISTENER (background)    │──▶ Session log
 Screen ──▶ │  hears + sees everything           │
            └──────────────┬─────────────────────┘
                           │ "what is happening now"
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌─────────────────────┐   ┌─────────────────────┐
   │ AGENT 2: ANSWER     │   │ AGENT 3: COACH      │
   │ main answer for     │   │ mid-answer sub-Qs,  │
   │ each new question   │   │ stuck moments,      │
   └─────────┬───────────┘   │ coding hints        │
             │               └─────────┬───────────┘
             └────────── Panel ◀───────┘
```

### Answer style example
- ❌ Textbook: "Indexing is a data structure technique used to efficiently retrieve records…"
- ✅ Human: "Index is basically like a book index. Instead of checking every row, Postgres
  directly jumps to the data. In my hotel booking project I added an index on booking date,
  so search became much faster."

## 4a. Situations the app must handle
| Situation | What happens |
|---|---|
| Interviewer changes the question halfway | Old answer cancelled, new one starts |
| Two questions in one sentence | Answer split into ① and ② |
| "Why not the other one?" | Listener supplies what "the other one" means from history |
| Interviewer uses a Hindi phrase ("ye wala kaise kaam karta hai?") | Understood; answered in simple English |
| Interviewer says "Okay, nice" | Nothing shown, no tokens used |
| Long silence after a question | Coach shows the first point to start with |
| Round changes to HR mid-interview | Style changes automatically (STAR-style, short, personal) |
| Group discussion | Tracks other speakers' points; suggests entry line + counter-point |
| System design question on interviewer's whiteboard | Reads the board; answers with components, flow, trade-offs |
| AI answer is wrong | F9 retries with stronger model; background code test catches coding mistakes |
| Internet drops | Local audio buffer, reconnect, catch up |

## 4b. Ways to improve accuracy
1. **Prep before the interview** — from JD + resume + GitHub, prepare ~100 likely questions
   with ready answers; common questions show in 0 s, AI only for new ones.
2. **Two-model speed trick** — Haiku 5.5 writes the first line, Opus 5.5 completes and corrects it.
3. **Custom vocabulary for STT** — tech words from JD + projects ("Postgres" never "post grass").
4. **Answer cache per question type** — same question asked a different way reuses the matching
   ready answer.
5. **Logs as a question bank** — hard questions from every session are saved so the app gets
   stronger over time (and nobody can easily beat it with tricky questions).

## 4c. Advanced in-session features (final, agreed)
Rule: **the screen shows only what is happening right now.** Everything else runs in the background.
Rule: **fully automatic** — candidate clicks Start once; everything runs until the interview ends.
No buttons needed for features (F8/F9/F10 hotkeys stay only as emergency backup).

1. **Background question prediction** — after each answer, predict 2–3 likely follow-ups and
   pre-generate them silently. Never displayed; used only to make the next answer instant.
2. **Project example only when relevant** — add a "in my project…" line only when the question
   truly relates to a project in the prepared notes. No forced examples.
3. **Honest line when the candidate hasn't used it** — only when the topic is genuinely not in
   resume/projects (not for every topic). Shows: "I haven't used it in production, but it works
   like…". Directly below: a **2–3 bullet short summary** of how that topic works, so the
   candidate is ready if the interviewer asks deeper.
4. **Clarify / repeat** —
   - Question has two meanings → "Ask: Do you mean … or …?"
   - STT confidence low / audio unclear → "Ask: Sorry, could you please repeat that?"
5. **Line following** — lines the candidate already spoke fade; next line highlighted.
6. **Layered coding help** — approach (1 line) → code → edge cases → time/space complexity.
7. **Instant error explanation** — reads terminal/editor errors; cause + fix in one line.
8. **Whiteboard as boxes** — component list in drawing order for system design.
9. **Conversation memory** — remembers everything discussed; suggests linking lines like
   "As I mentioned about indexing earlier…".
10. **Automatic pace cue** — adjusts from interviewer's style and candidate's speed; no clicks.
11. **Responsive panel** — adapts to any window size:
    - Small: only the current card (2–3 key lines)
    - Medium: current card + code view below
    - Large: answer and code side by side
12. **Synced code view (follows the editor)** —
    - Listener reads the active editor (VS Code etc.) via UI Automation: current file, cursor line
      (e.g. status bar "Ln 10"), visible lines; OCR fallback.
    - Panel shows a window around the cursor (cursor −2 to +8, e.g. line 10 → lines 8–18),
      updating automatically as the candidate moves.
    - Works for any file size (20 or 200+ lines); only the nearby window is shown.
13. **Interruption during coding** —
    - Interviewer asks about a line ("why this loop?", "what does line 25 do?") → Listener maps it
      to the line; code view jumps to and highlights it; Coach answer card appears on top.
    - When the answer is done (candidate finished, interviewer moves on), the card collapses
      automatically and the code view returns to the candidate's current cursor position so they
      can continue writing. Previous Q&A stays only in the session log.

Removed (not wanted): visible predictions, keyword-first lines, offline backup answers,
panel-near-webcam placement.

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
