# 📐 ALL-IN-ONE LIFE OS : 응용프로그램 제작을 위한 Harness² 규격서

> 🌐 **Languages:** [🇺🇸 English](HARNESS_SPEC.md) · **🇰🇷 한국어** · [🇯🇵 日本語](HARNESS_SPEC.ja.md) · [🇨🇳 简体中文](HARNESS_SPEC.zh.md)

> **참조 프레임워크:** [Google Research Harness² (Recursive Agent & Application Harnessing)](https://github.com/google-research/harness2)  
> **목적:** 윈도우 시스템 트레이(Tray) 및 플로팅 위젯(Floating Desktop App) 형태의 초경량 라이프 OS 애플리케이션 개발을 위한 아키텍처 규칙, 컴포넌트 인터페이스 계약(Contract), 그리고 `Propose-Probe-Compose` 검증 체계 수립

---

## 1. Google Research Harness² 철학의 응용프로그램 접목

Google Research의 **Harness²**는 LLM 자체를 수정하는 대신 모델을 둘러싼 **실행 환경(Execution Harness: 메모리, 도구, 가드레일, 인터페이스, 스크립트)**을 모듈형 데이터로 취급하여 지속적으로 적응·최적화합니다.

본 프로젝트에서는 이를 데스크톱 소프트웨어 엔지니어링 규칙으로 다음과 같이 치환하여 적용합니다:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HARNESS² SYSTEM MODEL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [Fixed Core] ─── 35대 거인 습관 DB & 다국어 자연어 / LLM 분석 엔진         │
│         ▲                                                                   │
│         │ (Contract / Data Invariant)                                       │
│         ▼                                                                   │
│   [Execution Harness] ──────────────────────────────────────────────────┐   │
│   │ 1. Storage Harness : SQLite WAL(시간축 탐색) + Excel 양방향 Sync    │   │
│   │ 2. View Harness    : Floating Widget (항상 위, 실시간 투명도 슬라이더)│   │
│   │ 3. OS Harness      : System Tray + Windows 시작프로그램 레지스트리  │   │
│   │ 4. Agent Harness   : 자연어 체크인 · 시간대 넛지 · 모바일 봇/웹훅   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   [Propose - Probe - Compose Cycle]                                         │
│   • Propose : 모듈별 명세(Spec) 및 데이터 계약 정의                         │
│   • Probe   : 개별 윈도우 OS API, GUI 루프, DB 트랜잭션의 독립 검증         │
│   • Compose : 검증된 컴포넌트를 main_app.py 및 단일 EXE·테스트로 통합       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 하네스 핵심 원칙 (Core Principles)

### 원칙 1: Zero-Friction Visibility (초경량 상시 가시성)
- 별도의 대형 프로그램을 매번 켤 필요 없이, 작업 표시줄 트레이와 바탕화면 플로팅 위젯(Floating Widget)을 통해 항상 1초 만에 습관과 일정을 확인/기록할 수 있어야 합니다.
- **메모리 풋프린트**: 파이썬 내장 Tkinter 기반 경량 UI 설계로 상시 상주 부담 최소화.

### 원칙 2: Multi-Temporal Traversal (시간축 자유 이동 및 미래/과거 기록)
- 기존 엑셀의 "당일 또는 1주일" 단위 기록의 한계를 극복합니다.
- **D-Day 및 날짜 탐색 (Date Traversal)**:
  - 과거 날짜(어제, 3일 전 등)의 미체크 습관 소급 기록 및 일지 수정
  - 미래 날짜(내일, D+3 등)의 할 일/습관 목표 사전 예약
  - 영구 타임라인 데이터베이스(SQLite WAL) 기반 일별 인덱싱 + 문맥형 날짜 버튼(`오늘` 기준 `◀ 어제/내일 ▶` ↔ 다른 날짜 `◀ 전날/다음날 ▶`)

### 원칙 3: Dual-Sync Architecture (SQLite + Excel 상호 보완)
- **로컬 고속 엔진**: 실시간 조회 및 날짜 탐색, 위젯·모바일 봇 동시 접근은 `life_os.db`(SQLite WAL)가 담당.
- **사용자 소유 워크북**: 4개 국어 5시트 `Life_OS_Successful_Habits.xlsx`와 서식·`IFERROR` 수식을 보존하며 100% 양방향 자동 동기화.

### 원칙 4: Non-Invasive OS Integration (비침습적 시스템 통합)
- 윈도우 시작 시 자동 실행 여부를 설정 창에서 체크박스 하나로 토글 (레지스트리 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 안전 제어).
- 창 닫기 시 프로세스 강제 종료 대신 백그라운드 트레이 최소화 지원.

### 원칙 5: Proactive Assistant Interaction (시간대 넛지 & 3-상태 응답 머신)
- 사용자가 프로그램을 찾아 열지 않아도, 떠다니는 비서가 시간대에 맞춰 말을 걸어 실행을 촉진(Nudge)합니다(`HABIT_ALLOWED_HOURS` 필터로 새벽 시간대 취침 습관 오추천 방지).
- **3-상태 빠른 응답 상태 머신 (State Machine)**:
  1. `[✅ 완료]`: 즉시 오늘자 DB 체크 + 칭찬 코칭 + 엑셀 자동 동기화.
  2. `[🚀 지금 할게!]`: 제임스 클리어 2분 규칙 발동 및 실행 격려.
  3. `[⏸️ 일단 보류]`: 미체크 상태 유지, 다음 주기에 부드럽게 재알림.
- **글로벌 단축키 (`Ctrl + Shift + H`)**: Windows OS 표준 `RegisterHotKey` (`MOD_CONTROL | MOD_SHIFT, 'H'`)로 언제든 즉시 표시/숨김 토글.
- **알림 & 사운드**: 부드러운 `winsound` 차임벨 및 Windows 네이티브 토스트 알림.
- **거인 페르소나 코칭 (Persona Harness)**:
  1. 💼 **워런 버핏** (5/25 우선순위 & 복리의 힘)
  2. ⚡ **앤드루 후버만** (신경과학 & 생체리듬/도파민 프로토콜)
  3. 🚀 **일론 머스크 & Grok** (제1원칙 사고 & 위트 있는 직설 코칭)
  4. 🧠 **마르쿠스 아우렐리우스** (스토아 철학 & 통제의 이분법 평정심)
- **개방형 모바일 봇 & 듀얼 NLP/LLM**: 무료 로컬 다국어 NLP + 선택적 Grok/OpenAI/Gemini API, 그리고 Telegram · Discord Gateway v10 · LAN HTTP 웹훅 지원.
- **Standalone Binary Packaging (`build_exe.py`)**: Python 미설치 PC에서도 실행되는 `LifeOS_Assistant_v2.exe` 빌드 및 `verify_clean_exe_bundle` 프라이버시 자동 감사 내장.

---

## 3. 컴포넌트별 계약 명세 (Component Contracts)

### [Component 1] View Harness: Floating Widget & Tray UI (`floating_widget.py`, `tray_manager.py`)
* **역할**: 바탕화면 지정 위치에 머무르는 반투명 미니멀 위젯.
* **계약(Contract)**:
  - 창 보이기/숨기기 토글 (`toggle_window`)
  - 항상 위 고정 옵션 (`always_on_top`)
  - 실시간 가로 투명도 슬라이더 (`30% ~ 100%` / `0.30 ~ 1.00`, 기본값 `0.92`, 미저장 닫기 시 원상 복원)
  - 문맥형 날짜 탐색 (`◀ 어제/내일 ▶` ↔ `◀ 전날/다음날 ▶`)
  - 표시 개수 (`1~35`) · `[🎲 셔플]` / `[📌 핀]` · 전체 35개 스크롤 모드
  - 하단 한 줄 자연어 입력창 & 실시간 검색 `[?]` 키워드 가이드 팝업

### [Component 2] Storage Harness: Timeline Database (`database.py` -> `life_os.db`)
* **역할**: 과거-현재-미래의 날짜별 습관 체크·메모·설정을 WAL 동시성으로 안전 보관.
* **스키마 계약**:
  ```sql
  CREATE TABLE IF NOT EXISTS daily_checks (
      check_date TEXT NOT NULL,      -- 'YYYY-MM-DD'
      habit_id INTEGER NOT NULL,     -- 1 ~ 35 (성공인 습관 DB)
      status INTEGER DEFAULT 1,      -- 1: 완료, 0: 미완료
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
* **역할**: Windows 트레이 아이콘, `Ctrl+Shift+H` 글로벌 핫키, 시작프로그램 레지스트리 제어.

### [Component 4] Sync Harness: 4개 국어 Excel Dual Synchronizer (`database.py`, `generate_excel.py`)
* **역할**: `ko`/`en`/`ja`/`zh` 워크북 시트 호환 탐지(`_find_sheet`) 및 `일일트래커`·`대시보드`·`AI비서 연동로그` 자동 동기화.

---

## 4. Propose - Probe - Compose 검증 사이클

1. **Step 1: Propose (아키텍처 명세)** — 본 문서에 스키마·UI·OS/Sync 계약 정의.
2. **Step 2: Probe (단위 프로브 검증)** — [`probe_harness.py`](probe_harness.py) 및 격리 샌드박스 프로브를 통해 SQLite 날짜 이동, 레지스트리 안전성, Excel 동기화, Tkinter UI를 독립 실측 검증.
3. **Step 3: Compose (프로덕션 통합 조립 & 자동 회귀)** — [`main_app.py`](main_app.py)로 통합 조립 후 [`build_exe.py`](build_exe.py)로 `LifeOS_Assistant_v2.exe` 빌드, [`test_regression_suite.py`](test_regression_suite.py)(25개) 및 [`test_e2e_scenarios.py`](test_e2e_scenarios.py)(7단계)로 상시 검증.

---

## 5. 사용자 옵션 매트릭스 (Config Matrix)

| 설정 항목 | 옵션 값 | 기본값 | 설명 |
|:---|:---:|:---:|:---|
| **시작 옵션** | `autostart_enabled` | `False` | 윈도우 시작 시 자동 실행 여부 |
| **창 동작** | `close_to_tray` | `True` | 'X' 클릭 시 종료 대신 트레이 상주 |
| **위젯 형태** | `always_on_top` | `True` | 플로팅 위젯을 항상 화면 최상단에 표시 |
| **위젯 투명도** | `opacity` | `0.92` | 실시간 슬라이더 반투명 제어 (`0.30 ~ 1.00`) |
| **동기화** | `auto_sync_excel`| `True` | 체크 시 엑셀 파일 자동 백그라운드 동기화 |
