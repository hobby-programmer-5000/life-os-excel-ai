# 📐 ALL-IN-ONE LIFE OS : Harness² Application Architecture Specification

> 🌐 **Languages:** **🇺🇸 English** · [🇰🇷 한국어](HARNESS_SPEC.ko.md) · [🇯🇵 日本語](HARNESS_SPEC.ja.md) · [🇨🇳 简体中文](HARNESS_SPEC.zh.md)

> **Reference Framework:** [Google Research Harness² (Recursive Agent & Application Harnessing)](https://github.com/google-research/harness2)  
> **Purpose:** Establish architectural invariants, component interface contracts, and a `Propose → Probe → Compose` validation loop for a lightweight desktop tray and floating Life OS application.

---

## 1. Translating Google Research Harness² into Application Engineering

Google Research **Harness²** treats the **execution harness** wrapping a core model (memory, tools, guardrails, UI, scripts) as modular, evolvable artifacts rather than modifying weights alone.

This project maps that separation directly into local desktop software engineering:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HARNESS² SYSTEM MODEL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [Fixed Core] ─── 35 Master Habits DB & Multilingual NLP / LLM Engine      │
│         ▲                                                                   │
│         │ (Contract / Data Invariant)                                       │
│         ▼                                                                   │
│   [Execution Harness] ──────────────────────────────────────────────────┐   │
│   │ 1. Storage Harness : SQLite WAL (Date Traversal) + 2-Way Excel Sync │   │
│   │ 2. View Harness    : Floating Widget (Always-on-top, Live Opacity)  │   │
│   │ 3. OS Harness      : System Tray + Windows Startup Registry Control │   │
│   │ 4. Agent Harness   : Natural-Language Check-in, Nudges & Mobile Bots│   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   [Propose - Probe - Compose Cycle]                                         │
│   • Propose : Define component specs, schema & UI state-machine contracts   │
│   • Probe   : Independently verify OS APIs, GUI loop, DB locks & edge cases │
│   • Compose : Assemble verified modules into a unified EXE + test suite     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Harness Principles

### Principle 1: Zero-Friction Visibility
- Users can review and check off daily routines in under a second via the persistent **System Tray** and **Floating Desktop Widget**, without launching a heavy spreadsheet manually.
- **Lightweight Footprint:** Built on Python standard library Tkinter to keep idle memory footprint minimal.

### Principle 2: Multi-Temporal Traversal (Past & Future Timeline)
- Overcomes static single-day / single-week worksheet constraints.
- **D-Day & Date Traversal:**
  - Backfill missed habits or edit logs on past dates (yesterday, 3 days ago, etc.)
  - Schedule plans/goals ahead on future dates (tomorrow, `D+3`, etc.)
  - Indexed cleanly by date in SQLite WAL (`life_os.db`) with contextual dynamic buttons (`◀ Yesterday / Today / Tomorrow ▶` on today; `◀ Prev Day / Today / Next Day ▶` off today).

### Principle 3: Dual-Sync Architecture (SQLite + Excel)
- **Fast Local Engine:** `life_os.db` (SQLite WAL) serves instant date traversal, simultaneous desktop/bot queries, and UI rendering.
- **User-Owned Workbook:** Automatically syncs two-way with localized 5-sheet `Life_OS_Successful_Habits.xlsx` preserving workbook styling and `IFERROR` formulas.

### Principle 4: Non-Invasive OS Integration
- Toggle Windows auto-start on login with a single checkbox (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`).
- Closing the widget minimizes cleanly to the tray by default rather than force-terminating active reminders or mobile bot workers.

### Principle 5: Proactive Assistant Interaction (Time-Aware Nudges & 3-State Machine)
- Instead of waiting passively, the floating companion proactively checks in during time-appropriate windows (`HABIT_ALLOWED_HOURS` prevents dawn/daytime false recommendations of bedtime habits while randomizing timeless habits).
- **3-State Quick Response Loop:**
  1. `[✅ Done]`: Checks today's habit in SQLite, returns persona coaching, syncs Excel.
  2. `[🚀 Do It Now!]`: Triggers James Clear's 2-Minute Rule start prompt.
  3. `[⏸️ Later]`: Leaves unchecked and reminds gently on the next interval.
- **Global Hotkey (`Ctrl + Shift + H`):** Uses Windows `RegisterHotKey` (`MOD_CONTROL | MOD_SHIFT, 'H'`) to show/hide instantly from any workspace.
- **Notifications & Audio:** Gentle `winsound` chime + Windows toast notifications.
- **4 Giant Role-Model Personas:**
  1. 💼 **Warren Buffett** (5/25 prioritization & compounding discipline)
  2. ⚡ **Andrew Huberman** (Circadian light, dopamine & neurobiology protocols)
  3. 🚀 **Elon Musk & Grok** (First-principles thinking & witty directness)
  4. 🧠 **Marcus Aurelius** (Stoic dichotomy of control & equanimity)
- **Mobile Bot & Webhook Bridges + Dual NLP/LLM:** Supports local keyword engine + optional Grok / OpenAI / Gemini APIs, plus Telegram, Discord Gateway v10, and LAN HTTP Webhook (`/checkin`, `/stats`, `/habits`, `/nudge`, `/review`).
- **Standalone Packaging (`build_exe.py`):** Compiles into single-file `LifeOS_Assistant_v2.exe` with post-build privacy audit (`verify_clean_exe_bundle`).

---

## 3. Component Contracts

### [Component 1] View Harness: Floating Widget & Tray UI (`floating_widget.py`, `tray_manager.py`)
* **Role:** Translucent minimal desktop widget anchored cleanly on-screen with live slider preview.
* **Contract:**
  - Toggle window visibility (`toggle_window`)
  - Always-on-top lock (`always_on_top`)
  - Live horizontal opacity slider (`30%–100%` / `0.30–1.00`, default `0.92`, auto-reverts if closed unsaved)
  - Relative date traversal & contextual button updates (`◀ Yesterday / Tomorrow ▶` ↔ `◀ Prev Day / Next Day ▶`)
  - Visible habit count (`1–35`), `[🎲 Shuffle]` / `[📌 Pin]`, and full-35 scroll mode
  - One-line bottom natural-language check-in input + searchable `[?]` keyword helper

### [Component 2] Storage Harness: Timeline Database (`database.py` -> `life_os.db`)
* **Role:** Stores all dated habit checks, logs, and settings safely under WAL concurrency.
* **Core Schema:**
  ```sql
  CREATE TABLE IF NOT EXISTS daily_checks (
      check_date TEXT NOT NULL,      -- 'YYYY-MM-DD'
      habit_id INTEGER NOT NULL,     -- 1 ~ 35
      status INTEGER DEFAULT 1,      -- 1: completed, 0: incomplete
      memo TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (check_date, habit_id)
  );

  CREATE TABLE IF NOT EXISTS daily_logs (
      log_date TEXT PRIMARY KEY,     -- 'YYYY-MM-DD'
      summary_text TEXT,
      ai_coaching TEXT,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS app_settings (
      key TEXT PRIMARY KEY,
      value TEXT
  );
  ```

### [Component 3] OS Harness: System Tray, Hotkeys & Auto-Start (`tray_manager.py`, `hotkey_manager.py`, `database.py`)
* **Role:** Safe integration with Windows tray icon, `Ctrl+Shift+H` hotkey registration, and `HKCU\...\Run`.

### [Component 4] Sync Harness: 4-Language Excel Dual Synchronizer (`database.py`, `generate_excel.py`)
* **Role:** Resolves sheet names across `en`/`ko`/`ja`/`zh` workbooks (`_find_sheet`) and syncs `Daily Tracker`, `Dashboard`, and `AI Assistant Log`.

---

## 4. Propose - Probe - Compose Validation Cycle

1. **Step 1: Propose (Architecture Spec)** — Formalize schema, UI state machine, and OS/sync contracts in this document.
2. **Step 2: Probe (Isolated Component Probing)** — Implemented in [`probe_harness.py`](probe_harness.py) plus sandboxed unit/integration probes verifying SQLite timeline traversal, Windows Registry auto-start safety, Excel sync, and Tkinter UI packing/date labels.
3. **Step 3: Compose (Production Assembly & Continuous Verification)** — Assembled cleanly in [`main_app.py`](main_app.py), packaged via [`build_exe.py`](build_exe.py) (`LifeOS_Assistant_v2.exe`), and verified via [`test_regression_suite.py`](test_regression_suite.py) (25 tests) and [`test_e2e_scenarios.py`](test_e2e_scenarios.py) (7 steps).

---

## 5. User Option Matrix

| Setting Key | Option Key | Default | Description |
|:---|:---:|:---:|:---|
| **Auto-Start** | `autostart_enabled` | `False` | Launch automatically on Windows startup |
| **Close Action** | `close_to_tray` | `True` | Minimize widget to system tray when closed |
| **Always On Top** | `always_on_top` | `True` | Keep floating widget above active windows |
| **Widget Opacity** | `opacity` | `0.92` | Live slider translucent opacity (`0.30–1.00`) |
| **Excel Auto Sync** | `auto_sync_excel` | `True` | Automatically sync check-ins to Excel |
