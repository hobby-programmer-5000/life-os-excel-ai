# 📐 ALL-IN-ONE LIFE OS : 응용프로그램 제작을 위한 Harness² 규격서
> **참조 프레임워크:** [Google Research Harness² (Recursive Agent & Application Harnessing)](https://github.com/google-research/harness2)  
> **목적:** 윈도우 시스템 트레이(Tray) 및 플로팅 위젯(Floating Desktop App) 형태의 초경량 라이프 OS 애플리케이션 개발을 위한 아키텍처 규칙, 컴포넌트 인터페이스 계약(Contract), 그리고 Propose-Probe-Compose 검증 체계 수립

---

## 1. Google Research Harness² 철학의 응용프로그램 접목

Google Research의 **Harness²**는 LLM 자체를 수정하는 대신 모델을 둘러싼 **실행 환경(Execution Harness: 메모리, 도구, 가드레일, 인터페이스, 스크립트)**을 모듈형 데이터로 취급하여 지속적으로 적응·최적화합니다.

본 프로젝트에서는 이를 데스크톱 소프트웨어 엔지니어링 규칙으로 다음과 같이 치환하여 적용합니다:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HARNESS² SYSTEM MODEL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [Fixed Core] ─── 35대 거인 습관 데이터베이스 & LLM 자연어 분석 엔진         │
│         ▲                                                                   │
│         │ (Contract / Data Invariant)                                       │
│         ▼                                                                   │
│   [Execution Harness] ──────────────────────────────────────────────────┐   │
│   │ 1. Storage Harness : SQLite (시간축/과거·미래 탐색) + Excel 양방향 Sync │   │
│   │ 2. View Harness    : Floating Desktop Widget (항상 위, 미니멀, 반투명) │   │
│   │ 3. OS Harness      : System Tray + Windows 시작프로그램 레지스트리 제어  │   │
│   │ 4. Agent Harness   : 자연어 입력 -> 습관 자동 매핑 & 코칭 웹훅 / 봇    │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   [Propose - Probe - Compose Cycle]                                         │
│   • Propose : 모듈별 명세(Spec) 및 데이터 계약 정의                         │
│   • Probe   : 개별 윈도우 OS API, GUI 루프, DB 트랜잭션의 독립 검증         │
│   • Compose : 검증된 컴포넌트를 조립하여 단일 무충돌 프로세스로 통합        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 하네스 핵심 원칙 (Core Principles)

### 원칙 1: Zero-Friction Visibility (초경량 상시 가시성)
- 별도의 대형 프로그램을 매번 켤 필요 없이, 작업 표시줄 트레이와 바탕화면 플로팅 위젯(Floating Widget)을 통해 항상 1초 만에 습관과 일정을 확인/기록할 수 있어야 합니다.
- **메모리 풋프린트**: Idle 상태 기준 30MB 이하 유지 (파이썬 내장 Tkinter 기반 최적화).

### 원칙 2: Multi-Temporal Traversal (시간축 자유 이동 및 미래/과거 기록)
- 기존 엑셀의 "당일 또는 1주일" 단위 기록의 한계를 극복합니다.
- **D-Day 및 날짜 탐색 (Date Traversal)**:
  - 과거 날짜(어제, 3일 전)의 미체크 습관 소급 기록 및 일지 수정
  - 미래 날짜(내일, D+3, 특정 요일)의 할 일/습관 목표 사전 예약
  - 영구 타임라인 데이터베이스(SQLite) 기반 일별 인덱싱

### 원칙 3: Dual-Sync Architecture (SQLite + Excel 상호 보완)
- **로컬 고속 엔진**: 실시간 조회 및 날짜 탐색, 초고속 렌더링은 `Local SQLite DB`가 담당.
- **사용자 공유/열람**: 필요 시 또는 주기적으로 사용자가 선호하는 `Life_OS_Successful_Habits.xlsx`와 100% 양방향 자동 동기화.

### 원칙 4: Non-Invasive OS Integration (비침습적 시스템 통합)
- 윈도우 시작 시 자동 실행 여부를 설정 창에서 체크박스 하나로 토글 (레지스트리 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 안전 제어).
- 트레이 닫기 동작 시 프로세스 강제 종료 대신 백그라운드 최소화 / 완전 종료 옵션 분리.

### 원칙 5: Proactive Assistant Interaction (능동적 넛지 & 3-상태 응답 머신)
- 사용자가 프로그램을 찾아 열지 않아도, 떠다니는 비서가 유기적으로 말을 걸어 실행을 촉진(Nudge)합니다.
- **스마트 넛지 알고리즘**: 오늘 아직 실천하지 않은 습관 중 시간대(오전: 햇빛/딥워크, 오후: 경청/의사결정, 저녁: 감사일기/디톡스)에 맞추어 랜덤 또는 지정 주기로 팝업 질문:
  * *"혹시 오늘 앤드루 후버만의 아침 햇빛 15분 노출은 하셨나요?"*
- **3-상태 빠른 응답 상태 머신 (State Machine)**:
  1. `[✅ 완료]`: 즉시 오늘자 DB 체크 + 칭찬 코칭 + 엑셀 자동 동기화.
  2. `[🚀 지금 할게]`: 제임스 클리어 2분 규칙 발동, 실행 카운트다운/격려 알림.
  3. `[⏸️ 일단 보류]`: 미체크 상태 유지, 설정된 시간 후 부드럽게 재알림.
- **글로벌 단축키 (Global Hotkey Harness)**:
  - 윈도우 OS 표준 `RegisterHotKey` (MOD_CONTROL | MOD_SHIFT, 'H') 기반으로 다른 작업 중 언제든 `Ctrl + Shift + H`로 비서 즉시 팝업/숨김 토글.
- **알림 & 사운드 (Notification & Audio Harness)**:
  - 넛지 발생 시 부드러운 시스템 차임벨(winsound) 및 윈도우 10/11 네이티브 토스트 알림 팝업.
- **거인 페르소나 코칭 (Persona Harness)**:
  - 4대 거인 페르소나 선택 지원:
    1. 💼 워런 버핏 모드 (단호한 5/25 우선순위 & 복리의 힘)
    2. ⚡ 앤드루 후버만 모드 (신경과학 & 생체리듬/도파민 프로토콜)
    3. 🚀 일론 머스크 & Grok 모드 (제1원칙 사고 & 위트 있는 팩트 폭격)
    4. 🧠 마르쿠스 아우렐리우스 모드 (스토아 철학 & 통제의 이분법 평정심)
  - LLM API(Grok, Gemini, OpenAI) 및 내장형 고성능 로컬 페르소나 엔진 듀얼 지원.
- **우클릭 컨텍스트 메뉴**: 플로팅 비서 또는 트레이 아이콘 우클릭 시 즉시 설정, 캘린더 타임라인(과거/미래), 엑셀 동기화 접근.
- **Standalone Binary Packaging**: Python 환경이 없는 일반 윈도우 PC에서도 즉시 더블클릭 실행 가능한 독립형 `LifeOS_Assistant.exe` 빌드 파이프라인 탑재.

---

## 3. 컴포넌트별 계약 명세 (Component Contracts)

### [Component 1] View Harness: Floating Widget & Tray UI
* **역할**: 바탕화면 우측 또는 사용자가 지정한 위치에 머무르는 반투명 미니멀 위젯.
* **계약(Contract)**:
  - `toggle_floating_window()`: 보이기/숨기기 토글.
  - `set_always_on_top(bool)`: 항상 위 고정 옵션.
  - `set_opacity(float)`: 위젯 투명도 제어 (예: 0.85 ~ 1.0).
  - `navigate_date(offset_days: int)`: 날짜 이동 (← 어제 / 오늘 / 내일 →).
  - `render_habits(date_str: str)`: 해당 일자의 35대 습관 및 체크 상태 고속 렌더링.
  - `quick_checkin(text: str)`: 한 줄 자연어 일과 입력창 제공.

### [Component 2] Storage Harness: Timeline Database (`life_os.db`)
* **역할**: 과거-현재-미래의 모든 날짜별 습관 체크 및 메모를 보관.
* **스키마 계약**:
  ```sql
  -- 일자별 습관 체크 기록 테이블
  CREATE TABLE IF NOT EXISTS daily_checks (
      check_date TEXT NOT NULL,      -- 'YYYY-MM-DD'
      habit_id INTEGER NOT NULL,     -- 1 ~ 35 (성공인 습관 DB)
      status INTEGER DEFAULT 1,      -- 1: 완료, 0: 미완료
      memo TEXT,                     -- 특정 습관에 대한 일자별 메모
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (check_date, habit_id)
  );

  -- 일자별 종합 일지 / 미래 메모 테이블
  CREATE TABLE IF NOT EXISTS daily_logs (
      log_date TEXT PRIMARY KEY,     -- 'YYYY-MM-DD'
      summary_text TEXT,             -- 당일 일과 / 미래 계획 메모
      ai_coaching TEXT,              -- AI 비서 코칭 메시지
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- 시스템 설정 테이블
  CREATE TABLE IF NOT EXISTS app_settings (
      key TEXT PRIMARY KEY,
      value TEXT
  );
  ```

### [Component 3] OS Harness: System Tray & Auto-Start Controller
* **역할**: 윈도우 OS 시스템과 안전하게 결합.
* **계약(Contract)**:
  - `init_tray_icon()`: 트레이 아이콘 등록 (메뉴: 열기/닫기, 오늘 체크, 엑셀 동기화, 설정, 종료).
  - `set_autostart(enable: bool)`: 윈도우 부팅 시 자동 시작 등록/해제.
  - `get_autostart_status() -> bool`: 현재 자동 시작 등록 여부 조회.
  - `minimize_to_tray()`: 창 닫기 버튼 클릭 시 트레이로 축소.

### [Component 4] Sync Harness: Excel Dual Synchronizer
* **역할**: SQLite의 일주일 치 체크 상태를 기존 `Life_OS_Successful_Habits.xlsx`의 `📅 일일트래커` 및 `📊 대시보드`에 자동 기입.

---

## 4. Propose - Probe - Compose 검증 사이클

Harness²의 핵심 방법론인 **Propose-Probe-Compose**에 따라 개발을 진행합니다:

1. **Step 1: Propose (설계 완료 - 본 문서)**
   - 스키마, UI 위젯 구조, 트레이/시작프로그램 연동 사양을 명문화.
2. **Step 2: Probe (단위 기능 실측 검증)**
   - `probe_db.py`: 날짜 이동(어제/오늘/며칠 뒤 미래) 쿼리 및 성능 검증.
   - `probe_os.py`: 윈도우 시작프로그램 등록/해제 레지스트리 API 안전성 검증.
   - `probe_gui.py`: Tkinter 무프레임 플로팅 윈도우(항상 위, 드래그 이동) 검증.
3. **Step 3: Compose (최종 애플리케이션 통합 조립)**
   - 검증된 부품들을 `life_os_app.py`로 결합하여 단일 실행 파일 형태로 패키징.

---

## 5. 사용자 옵션 매트릭스 (Config Matrix)

| 설정 항목 | 옵션 값 | 기본값 | 설명 |
|:---|:---:|:---:|:---|
| **시작 옵션** | `autostart_enabled` | `False` | 윈도우 시작 시 자동 실행 여부 |
| **창 동작** | `close_to_tray` | `True` | 'X' 클릭 시 종료 대신 트레이 상주 |
| **위젯 형태** | `always_on_top` | `True` | 플로팅 위젯을 항상 화면 최상단에 표시 |
| **위젯 투명도** | `opacity` | `0.92` | 작업 방해 없는 반투명 디자인 (0.5~1.0) |
| **동기화** | `auto_sync_excel`| `True` | 체크 시 엑셀 파일 자동 백그라운드 동기화 |
