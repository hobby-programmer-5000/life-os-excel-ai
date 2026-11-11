# 🛠️ ALL-IN-ONE LIFE OS : 개발 히스토리 (Development History)

> 🌐 **Languages:** [🇺🇸 English](DEVELOPMENT_HISTORY.md) · **🇰🇷 한국어** · [🇯🇵 日本語](DEVELOPMENT_HISTORY.ja.md) · [🇨🇳 简体中文](DEVELOPMENT_HISTORY.zh.md)

이 문서는 **"세계적 성취자들의 핵심 성공 습관을 엑셀 하나로 통합하고, AI 비서와 실시간으로 실천을 관리한다"** 는 아이디어에서 출발해, 데스크톱 플로팅 위젯 · 다국어 지원 · 개방형 모바일 봇 생태계까지 함께 단계적으로 다듬어 온 공동 개발 과정을 정리한 기록입니다.

---

## 📌 타임라인 및 단계별 진화 과정

### Phase 1. 올인원 성공 습관 엑셀 & AI 비서 코어 구축
* **배경:** 여러 서적·강연·프로토콜에 흩어진 핵심 루틴을 **7대 라이프 영역 × 5개 핵심 습관 = 35대 성공 습관** 체계로 정렬하고, 특정 폐쇄형 앱 대신 누구나 소유·분석할 수 있는 표준 엑셀(`.xlsx`) 중심 구조를 채택했습니다.
* **구현 내용:**
  * [`generate_excel.py`](generate_excel.py): 5개 시트(`📊 대시보드`, `🏆 성공인 습관DB`, `📅 일일트래커`, `📈 주간회고`, `🤖 AI비서 연동로그`) 자동 생성 및 100여 개 집계 수식에 `IFERROR`를 적용해 초기 빈 시트에서 `#DIV/0!` 오류를 원천 차단했습니다.
  * [`REFERENCES.ko.md`](REFERENCES.ko.md): 35가지 일과 각각의 출처(저서·논문·강연)와 선정 근거를 체계적으로 문서화했습니다.
  * [`ai_secretary.py`](ai_secretary.py): 자연어 일과 문장에서 다중 습관 키워드를 인식해 체크하고 페르소나 코칭을 생성하는 100% 오프라인 4개 국어 로컬 NLP 엔진(`LocalHabitNLP`)을 구축했습니다.

---

### Phase 2. Google Research Harness² 응용 & Windows 플로팅 트레이 앱
* **배경:** *"매일 엑셀 파일을 직접 열어 체크하는 마찰을 없애고, 바탕화면에 떠서 먼저 말을 걸어주는 가벼운 비서가 있으면 좋겠다"* 는 요구에 따라, Google Research **Harness²** 개념을 응용 소프트웨어 엔지니어링 규격([`HARNESS_SPEC.ko.md`](HARNESS_SPEC.ko.md))으로 치환했습니다.
* **구현 내용:**
  * **Storage Harness ([`database.py`](database.py)):** SQLite(`life_os.db`, WAL 모드)를 도입해 당일/1주일 한계를 넘어 **어제·과거·며칠 뒤(Date Traversal)** 타임라인을 자유롭게 기록하고, 엑셀·SQLite·위젯 간 3-Way 양방향 동기화를 구현했습니다.
  * **Assistant Engine ([`assistant_engine.py`](assistant_engine.py)):** 4대 거인 롤모델 페르소나(앤드루 후버만, 워런 버핏, 일론 머스크 & Grok, 마르쿠스 아우렐리우스), 시간대별 스마트 넛지, `[✅ 완료]` · `[🚀 지금 할게!]` · `[⏸️ 일단 보류]` 3-상태 머신을 구축했습니다.
  * **Desktop UI & OS Harness ([`floating_widget.py`](floating_widget.py), [`tray_manager.py`](tray_manager.py), [`hotkey_manager.py`](hotkey_manager.py), [`main_app.py`](main_app.py), [`build_exe.py`](build_exe.py)):** 반투명 플로팅 위젯, 시스템 트레이, `Ctrl+Shift+H` 글로벌 단축키, 차임벨·토스트 알림, 그리고 Python 미설치 Windows PC에서도 실행되는 단일 실행 파일(`LifeOS_Assistant_v2.exe`) 패키징을 완성했습니다.

---

### Phase 3. 실사용 피드백 기반 UX 정교화 & 디버깅
실제 바탕화면에 띄워 사용하면서 발견한 세세한 UX·엣지 케이스를 하나씩 해결했습니다.
* **위젯 개인화 & 레이아웃 버그 수정:**
  * 위젯 표시 개수를 `1~35개` 중 자유롭게 고정하고 `[🎲 셔플]` / `[📌 핀]` 및 **`35개 전체 스크롤 모드`** 를 추가했습니다.
  * 긴 코칭 메시지가 표시될 때 하단 자연어 입력창이 화면 아래로 밀려 잘리는 문제를 Tkinter `side=tk.BOTTOM` 우선 패킹 순서 개선으로 해결했습니다.
* **오체크 방지 & 키워드 탐색 팝업:**
  * `"dk"` 같은 무관한 단어가 우발적으로 습관 완료로 인식되지 않도록 공백 제거 정규화·어절 가드를 정비했고, `[?]` 버튼 클릭 시 검색 가능한 **35대 습관 키워드 가이드**가 열리도록 개선했습니다.
* **테스트 샌드박스 격리:**
  * 자동 테스트 실행 시 실제 사용자 DB/엑셀이 오염되지 않도록 `LIFE_OS_DATA_DIR` 환경 변수 및 `TemporaryDirectory()` 격리를 강제하고, `database.py` 파일 잠금(`wb.close()`) 누수까지 점검했습니다.
* **직관적인 날짜·시간·투명도 UX 개선:**
  * **동적 날짜 버튼 라벨:** 오늘(`diff == 0`)을 볼 때는 **`◀ 어제` / `오늘` / `내일 ▶`** 로, 다른 날짜로 이동하면 **`◀ 전날` / `오늘` / `다음날 ▶`** 로 바뀌어 날짜 문맥 혼동을 없앴습니다.
  * **시간대별 넛지 필터 (`HABIT_ALLOWED_HOURS`):** 새벽(`00~04시`)에 저녁·취침 습관이 잘못 추천되던 조건 버그를 수정해, 시간이 포함된 습관(아침 자연광, 오전 의사결정, 새벽 기상, 저녁 셧다운, 취침 전 디톡스·감사일기 등)은 해당 시간대에만 묻고 일반 습관은 무작위 다양성을 유지하도록 재설계했습니다.
  * **실시간 가로 투명도 슬라이더:** 추상적인 숫자(`0.5 ~ 1.0`) 입력칸을 **`30% ~ 100%` 가로 슬라이더(`tk.Scale`)** 로 교체해 드래그 즉시 위젯 투명도를 실시간 미리보고, 미저장 닫기(`✕`) 시 원래 투명도로 복원되도록 개선했습니다.

---

### Phase 4. 글로벌 4개 국어 통합 아키텍처
* **배경:** 단일 한국어 사용자뿐 아니라 전 세계 사용자가 OS 언어에 맞춰 바로 쓸 수 있도록 전체 시스템을 다국어화했습니다.
* **구현 내용:**
  * [`i18n.py`](i18n.py), [`i18n_habits.py`](i18n_habits.py), [`i18n_personas.py`](i18n_personas.py): `ko` / `en` / `ja` / `zh` 4개 국어 UI, 35대 습관 키워드(교차 언어 인식 포함), 4인 페르소나, 4개 국어 엑셀 워크북 생성 및 시트 이름 호환 매핑(`_find_sheet`), 설정 내 실시간 UI·트레이 핫스위치, 그리고 OS 로캘별 `.exe` PE 메타데이터(`VSVersionInfo`)까지 통합했습니다.

---

### Phase 5. 개방형 모바일 봇 · LAN 웹훅 연동 & 보안·배포 가드
* **설계 방향 논의:** 외부 메신저·자동화 채널 확장 과정에서 무료 사용자에게도 공식 봇 API가 열려 있는 개방형 생태계에 집중하기로 결정하고, 복잡하거나 제3자 서비스 약관 우려가 있는 비공식/폐쇄형 연동은 배제했습니다.
* **구현 및 실기기 검증 내용:**
  * **Telegram 봇 ([`telegram_bot.py`](telegram_bot.py)):** 외부 추가 설치 없이 HTTP Long-Polling 백그라운드 수신 구현 및 `@BotFather` 사칭 봇 예방 경고 카드 UI 반영.
  * **Discord 내장 봇 ([`discord_bot.py`](discord_bot.py), [`bot_commands.py`](bot_commands.py)):** `discord.py`나 외부 터널 없이 순수 Python 표준 라이브러리 RFC 6455 TLS WebSocket(Gateway v10) + REST API 연동. 실제 연동 과정에서 확인된 Discord 최신 설정 경로(`⚙️ → </> 개발자 → 개발자 모드`)와 `Clyde` DM 차단 대응, `전용 Channel ID` 동작 방식을 정리했습니다.
  * **Android & Wi-Fi 보조 iPhone 웹훅 ([`bot_bridge.py`](bot_bridge.py)):** 집 Wi-Fi 내 Android(`HTTP Request Shortcuts`)와 보조 iPhone 공기계(`단축어`) 실기기 테스트를 통해 확인된 **Windows `Public`→`Private` 네트워크 프로필/방화벽**, **`https://` → `http://` TLS 헤더 오류**, **`Parameters` → `Custom Text` (`application/json`)** 주의사항을 가이드에 반영했습니다.
  * **무료 로컬 NLP 강화 · 3단 봇 설정창 · 성장 그래프 아이콘 통일:** 4개 국어 실제 일상 문장 입력 테스트를 거쳐 `LocalHabitNLP`의 구두점·하이픈 정규화와 구어체 패턴 인식을 보강하고 선택적 외부 유료 LLM API를 제거했으며(`Telegram → Discord → 로컬 웹훅`), [`app_icon.py`](app_icon.py)(`assets/app_icon.ico`)를 통해 `.exe` 파일·시스템 트레이·모든 팝업 타이틀바 앱 아이콘을 상승 그래프 심볼로 통일했습니다.
  * **빌드 & Git Push 보안 가드 ([`.gitignore`](.gitignore), [`build_exe.py`](build_exe.py)):** 개인 `*.db`, `*.xlsx`(체크인 이력 및 AI 연동 로그 포함), `.env`, `*.spec`, `build/`, `dist/`를 Git 추적에서 원천 배제하고, 빌드 시 `.exe` 내부 아카이브에 개인 데이터·토큰이 포함되지 않도록 자동 검증(`verify_clean_exe_bundle`)을 추가했습니다.

---

### Phase 6. 모던 미니멀 "Anti-Slop" UI 재설계 · 무료 벡터 스톡 · 디자인 문헌 체계화
* **UX 비평 & 전환 배경:** 다색 네온 테두리(`#38BDF8` / `#818CF8` / `#F59E0B`), 버튼 내 이모지 중첩, 밝은 기본 폼 입력창 등 전형적인 "AI slop" 인상을 걷어내고 오래 띄워 두어도 눈이 편안한 차분한 도구로 거듭나기 위해, Product Owner의 지시로 verified HCI·디자인 문헌([`REFERENCES.ko.md`](REFERENCES.ko.md): Dieter Rams, Edward Tufte, Weiser & Brown Calm Technology, John Sweller, Josef Müller-Brockmann, Nielsen Norman Group)에 근거한 **모던 미니멀 UI** 개편을 단행했습니다.
* **구현 및 시각 전수 점검 내용:**
  * **60-30-10 옵시디언-징크 토큰 & 순수 파이썬 SVG 엔진 ([`ui_theme.py`](ui_theme.py)):** `#09090B` / `#111216` / `#18181B` 중립 다크 표면, `1px` `#27272A` 헤어라인, 다크 입력 폼 & `ttk` 스크롤바/콤보박스, 단일 핵심 CTA(`#F4F4F5`/`#09090B`), 완료·수신 상태 전용 에메랄드(`#10B981`/`#059669`), 그리고 29개 SVG 아이콘을 선명하게 렌더링하는 자체 W3C SVG 래스터라이저를 구축했습니다.
  * **상업적 이용 가능 무료 스톡 & 크레딧 고지 ([`assets/icons/lucide/`](assets/icons/lucide/), [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)):** `ISC License`(및 상위 Feather `MIT License`) 기반의 **Lucide SVG 29종**을 프로젝트 및 [`build_exe.py`](build_exe.py) 번들에 통합해 UI 내 불필요한 이모지 장식을 제거([`floating_widget.py`](floating_widget.py), [`i18n.py`](i18n.py), [`assistant_engine.py`](assistant_engine.py))하고, 상승 그래프 앱 아이콘([`app_icon.py`](app_icon.py))과 모든 스톡 라이선스 고지를 공식 문서화했습니다.
  * **픽셀 단위 레이아웃 검증:** `en/ko/ja/zh` 메인 위젯, 설정창, 3단 봇 연동창, 35대 체크리스트, `[?]` 키워드 가이드 스크린샷을 직접 검증해 긴 영어/일본어 헤더에서의 우측 닫기 버튼 잘림 및 줄바꿈 잘림을 해결했습니다.

---

## 👥 공동 기여 및 역할 분담 (Contributors & Role Division)

이 프로젝트는 사람 개발자(**Product Owner / UX·UI 디렉터 / 실기기 QA**)와 AI 페어 프로그래머(**구현 / 디자인 리서치 / 자동 검증 파트너**)가 역할을 명확히 나누어 Human-in-the-loop 방식으로 함께 구축했습니다.

| 기여자 | 역할 (Role) | 주요 담당 영역 (Owned Contributions) |
| :--- | :--- | :--- |
| **[hobby-programmer-5000](https://github.com/hobby-programmer-5000)** | **Product Owner · Domain Architect · UX/UI Director · Real-Device QA** | • **핵심 비전 & 도메인 설계:** 7대 라이프 영역 × 35대 성공 습관 프레임워크 선정, 사용자 소유 엑셀(`.xlsx`) + 바탕화면 비서 구조 방향 설정<br>• **Harness² & 무비용 로컬 지향:** Google Research Harness² 적용, 4대 거인 페르소나, 외부 유료 LLM API 제거(100% 로컬 NLP) 정책 확정<br>• **모던 미니멀 UI ("Anti-Slop") & 라이선스 원칙 수립:** 과한 다색 장식을 배제한 모던 미니멀 UI 전환, 성장 그래프 앱 아이콘 선정, 상업적 무료 스톡 채택과 [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)·UI 문헌 레퍼런스([`REFERENCES.ko.md`](REFERENCES.ko.md)) 필수 기록 기준 지시<br>• **실사용 UX 비평 & 실기기 QA:** 동적 날짜 버튼(`◀ 어제/내일 ▶` ↔ `◀ 전날/다음날 ▶`), 새벽 시간대 오추천 수정, 실시간 가로 투명도 슬라이더(`30%–100%`), Android(`HTTP Request Shortcuts`) 및 보조 iPhone(Wi-Fi `단축어`) 실기기 테스트와 개인정보·토큰 비노출 보안 감사 기준 확정<br>• **릴리즈 검수 & 다국어 정책:** MIT 라이선스 결정, 4개 국어 데모 영상 및 다국어 문서 체계 지시 |
| **[Gemini (Antigravity)](https://github.com/gemini-code-assist)** | **AI Pair Programmer · Full-Stack, UI & QA Engineer** | • **모던 미니멀 테마 & 벡터 아이콘 엔진:** [`ui_theme.py`](ui_theme.py)(60-30-10 옵시디언/징크 토큰 + 순수 파이썬 SVG 래스터라이저) 개발, 29종 Lucide SVG 통합, [`app_icon.py`](app_icon.py)·[`floating_widget.py`](floating_widget.py) 전면 UI 리뉴얼, [`i18n.py`](i18n.py)·[`assistant_engine.py`](assistant_engine.py) 클린업, [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) 및 HCI 디자인 참고문헌 집필<br>• **코어 백엔드 & AI 엔진 구현:** [`generate_excel.py`](generate_excel.py), [`database.py`](database.py)(SQLite WAL · Date Traversal · 3-Way Sync), [`ai_secretary.py`](ai_secretary.py)(`LocalHabitNLP`), [`assistant_engine.py`](assistant_engine.py), `HABIT_ALLOWED_HOURS` 시간대 필터 구현<br>• **데스크톱 위젯 & OS 통합:** [`floating_widget.py`](floating_widget.py), [`tray_manager.py`](tray_manager.py), [`hotkey_manager.py`](hotkey_manager.py), [`main_app.py`](main_app.py) UI/UX, 동적 날짜 라벨, 실시간 `tk.Scale` 투명도 슬라이더, 검색형 `[?]` 가이드 구현<br>• **글로벌 4개 국어 i18n 아키텍처:** [`i18n.py`](i18n.py), [`i18n_habits.py`](i18n_habits.py), [`i18n_personas.py`](i18n_personas.py) (`ko`/`en`/`ja`/`zh`) UI·키워드·엑셀 시트 호환·실시간 언어 전환 및 `.exe` PE 메타데이터 통합<br>• **모바일 봇 · 패키징 · 자동 검증:** [`telegram_bot.py`](telegram_bot.py), [`discord_bot.py`](discord_bot.py)(순수 Python RFC 6455 TLS WebSocket Gateway v10), [`bot_commands.py`](bot_commands.py), [`bot_bridge.py`](bot_bridge.py), [`build_exe.py`](build_exe.py)(`.exe` + `verify_clean_exe_bundle`), 격리 샌드박스 데모(`assets/demo_*.gif/.mp4`), [`test_regression_suite.py`](test_regression_suite.py) & [`test_e2e_scenarios.py`](test_e2e_scenarios.py) 구축 |

---

## 🔍 개발 과정에서 배운 핵심 엔지니어링 교훈

1. **도구·플랫폼 현실 검증의 가치:** 문서상 스펙과 실제 앱 화면·OS 환경(Windows 공용/개인 Wi-Fi 방화벽, Discord 최신 개발자 메뉴, Android 앱의 TLS 헤더/JSON 파라미터 동작)을 실기기에서 직접 검증했을 때 가장 가치 있는 가이드라인이 완성되었습니다.
2. **프라이버시 바이 디자인(Privacy by Design):** 로컬 개인용 비서 프로젝트일수록 `.gitignore`와 빌드 스크립트(`verify_clean_exe_bundle`)에 자동 검증을 걸어 DB·엑셀·사설 IP·토큰 유출을 구조적으로 막아야 안심하고 릴리즈할 수 있습니다.
3. **인간-AI 협업 시너지:** 사람이 실제 생활 속 사용감·우선순위·보안 경계를 정확히 짚어주고, AI가 아키텍처 구현·다국어 확장·샌드박스 자동 검증을 빠르게 실행·반증할 때 단일 개발 이상의 속도와 품질이 나옵니다.
