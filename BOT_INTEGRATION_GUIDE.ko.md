# 🤖 AI 비서 & 모바일 봇(Telegram · Discord · Android/Wi-Fi 단축어) 통합 가이드

> 🌐 **Languages:** [🇺🇸 English](BOT_INTEGRATION_GUIDE.md) · **🇰🇷 한국어** · [🇯🇵 日本語](BOT_INTEGRATION_GUIDE.ja.md) · [🇨🇳 简体中文](BOT_INTEGRATION_GUIDE.zh.md)

이제 모바일 봇·웹훅과 데스크톱 플로팅 위젯이 **동일한 SQLite 타임라인(`life_os.db`) 및 엑셀(`Life_OS_Successful_Habits.xlsx`)**을 실시간 공유합니다.  
외출 중 스마트폰으로 보낸 체크인이 즉시 PC 플로팅 위젯과 엑셀에 동시에 반영됩니다!

---

## 1. 통합 아키텍처 개요

```text
[모바일 / 메신저 / 단축어 채널]
  ├─► 1) Telegram 봇 (/start, /status, /nudge, /review, /어제, 자연어) [외출 시 LTE/5G 메인 추천]
  ├─► 2) Discord 내장 봇 (DM 자동 응답 · 전용 Channel ID · @멘션 / !status / !nudge)
  ├─► 3) Android HTTP Request Shortcuts / MacroDroid · Wi-Fi iPhone 단축어 · 로컬 웹훅 (/checkin)
  └─► 4) CLI 모드 & 100% 오프라인 다국어 로컬 NLP 엔진 (외부 API 토큰 불필요)
         │
         ▼
[Life OS 통합 코어 (AssistantEngine + DatabaseManager + i18n)]
  ├─► 1) 35대 습관 자연어 분석 (4개 국어: ko/en/ja/zh) + 거인 페르소나 맞춤 코칭 생성
  ├─► 2) life_os.db (SQLite WAL) 영구 저장
  ├─► 3) 데스크톱 플로팅 위젯 실시간 알림/자동 새로고침
  └─► 4) Life_OS_Successful_Habits.xlsx ('일일트래커', '대시보드', 'AI비서 연동로그') 자동 동기화
```

---

## 2. 가장 쉬운 설정 방법 (GUI 원클릭 - 추천!)

별도 터미널이나 외부 서버(포트포워딩·터널링)를 열지 않아도 플로팅 비서 앱(`LifeOS_Assistant_v2.exe`) 안에서 바로 켜고 끌 수 있습니다:

1. 플로팅 위젯 우클릭(또는 `⚙️` 아이콘 → **`🌐 모바일 봇/웹훅...`**) → **`🌐 모바일 봇 · Telegram · Discord · 웹훅 연동 설정`**
2. 원하는 항목을 켜고 **`[저장 및 즉시 연결 적용]`** 클릭!
   - **텔레그램 AI 비서 봇:** `@BotFather` 토큰만으로 외부망(LTE/5G) 포함 백그라운드 상시 수신
   - **디스코드(Discord) AI 비서 봇:** Discord Developer Portal 봇 토큰만으로 외부 터널 없이 Gateway v10(WSS) 실시간 수신
   - **로컬 웹훅 브릿지 (`127.0.0.1` / `0.0.0.0:8080`):** Android `HTTP Request Shortcuts` / `MacroDroid`, Wi-Fi 연결된 보조 iPhone 단축어 등 로컬 HTTP 자동화 연동

---

## 3. 채널별 상세 연동 가이드

> ⚠️ **외부 플랫폼 UI·정책 변경 고지:** Telegram(`@BotFather`), Discord(`Discord Developer Portal` · 앱 설정), Android/iOS 앱의 메뉴 위치, 화면 구성, 봇 권한/인텐트 정책은 각 서비스 회사의 업데이트에 따라 예고 없이 달라질 수 있습니다. 실제 화면이 본 문서와 조금 다를 경우 최신 공식 문서 또는 변경된 메뉴 명칭(`Bot`, `Reset Token`, `Message Content Intent`, `Developer Mode` 등)을 기준으로 적용해 주세요.

### 🔹 방법 A: 텔레그램 비서 (Android/iPhone 외출용 메인 채널 추천)
> *(※ Telegram 정책 및 `@BotFather` 명령 흐름은 Telegram 업데이트에 따라 달라질 수 있습니다.)*
> ⚠️ **사칭 봇 주의!** 텔레그램 검색창에는 가짜 `BotFather` 사칭 계정이 많습니다. 반드시 **파란 공식 인증 체크마크(✓)** 와 **800만+ 이용자 수**를 확인하세요!
> - **공식 링크:** https://t.me/BotFather (또는 앱 내 `[🔗 공식 @BotFather 열기]` 버튼 클릭)
> - **안전한 팁:** 텔레그램 `Saved Messages(저장한 메시지)`에 `@BotFather`를 입력한 뒤 파란 링크를 클릭하면 사칭 없이 바로 열립니다.

1. **토큰 발급:** 공식 `@BotFather` → `[START]` → `/newbot` → 봇 이름·`~bot` 영문 아이디 입력 → **HTTP API Token** 복사
2. **앱 연결:** 위젯 설정창 **`Bot Token:`** 입력 → **`[연결 확인]`** → **`📱 텔레그램 AI 비서 봇 자동 수신`** 체크 → **`[저장 및 즉시 연결 적용]`** → `t.me/내봇아이디`에서 `[START]` 클릭
3. **명령어:** `/status`, `/nudge`, `/review`, `/어제 <내용>` (또는 `/yesterday`, `/昨日`, `/昨天`), 일반 일과 문장

---

### 🔹 방법 B: Discord 내장 봇 상세 연동 가이드 (`discord_bot.py` — 외부 터널 불필요)
외부 서버·ngrok 없이 Discord 공식 **Gateway v10(WSS) + REST API**로 직접 연결됩니다.
> *(※ Discord Developer Portal 및 Discord 앱 UI·권한 경로는 Discord 업데이트에 따라 달라질 수 있습니다.)*

#### 1) Discord 개발자 포털에서 봇 생성 & 토큰 발급
1. 웹 브라우저에서 **[Discord 개발자 포털](https://discord.com/developers/applications)** 접속 후 본인 Discord 계정으로 로그인합니다. *(위젯 봇 설정창의 `[🔗 Discord 개발자 포털]` 버튼을 눌러도 바로 열립니다.)*
2. 오른쪽 상단 **`New Application`** 클릭 → 봇 이름(예: `Life OS 비서`) 입력 → 약관 체크 후 **`Create`**
3. 왼쪽 사이드바에서 **`봇` (`Bot`)** 메뉴를 클릭합니다.  
   *(💡 브라우저 창 너비가 좁으면 왼쪽 메뉴가 숨겨집니다. 왼쪽 맨 위 `DEVELOPER PORTAL` 글자 바로 옆 **`☰` (가로 세 줄 버튼)** 을 클릭하면 **`봇` (`Bot`)** 메뉴가 나타납니다.)*
4. **`토큰` (`Token`)** 항목의 **`토큰 재설정` (`Reset Token`)** 클릭 → 확인 팝업/인증 통과 후 표시되는 **Bot Token `복사`**  
   *(⚠️ 페이지를 벗어나면 다시 확인할 수 없으니 안전한 곳에 붙여넣고, 타인에게 절대 공유하지 마세요.)*
5. 같은 **`봇` (`Bot`)** 화면에서 아래로 스크롤해 **`특권 게이트웨이 인텐트` (`Privileged Gateway Intents`)** 영역을 찾은 뒤:
   * **`메시지 콘텐츠 인텐트` (`MESSAGE CONTENT INTENT`)** 스위치를 **ON(파란색)** 으로 켜고 하단 **`변경 사항 저장` (`Save Changes`)** 클릭!
   * *(※ 이 스위치가 꺼져 있으면 봇이 서버 채팅방의 텍스트 내용을 읽을 수 없어 1:1 DM에서만 응답합니다.)*

#### 2) 내 Discord 서버로 봇 초대 (`OAuth2 URL 재생기`)
1. 왼쪽 위 **`☰` → `OAuth2`** *(또는 하위 **`URL 재생기` / `URL Generator`**)* 메뉴로 이동합니다.
2. **`스코프` (`SCOPES`)** 목록에서 **`bot`** 을 체크합니다. *(예: 오른쪽 열 위에서 4번째)*
3. 아래쪽에 새로 펼쳐지는 **`봇 권한` (`Bot Permissions`)** 에서 최소 아래 **3개 권한**을 체크합니다:
   * **`채널 보기`** (`View Channels`)
   * **`메시지 보내기`** (`Send Messages`)
   * **`메시지 기록 보기`** (`Read Message History`)
4. 페이지 맨 아래 **`생성된 URL` (`Generated URL`)** 오른쪽 **`복사`** 클릭 → 새 브라우저 탭 주소창에 붙여넣어 이동 → 내 Discord 서버 선택 → **`계속하기` → `승인`**

#### 3) 전용 체크인 채널 만들기 & 채널 ID 복사 (추천)
1. 내 Discord 서버 왼쪽 채널 목록 **`채팅 채널` 옆 `+`** 클릭 → 예: **`#습관-체크인`** 채널을 만듭니다.
   * *(🔒 **비공개 채널**로 만들었다면, 해당 채널 옆 **`⚙️(채널 편집) → 권한 → 멤버 또는 역할 추가`** 에서 초대된 **봇 계정도 반드시 추가**해야 봇이 메시지를 읽고 답장할 수 있습니다.)*
2. Discord 앱 왼쪽 아래 본인 프로필 영역 옆 **`⚙️ (사용자 설정)`** 클릭
3. 사용자 설정 왼쪽 메뉴를 맨 아래까지 내려 **`</> 개발자` (`Developer`)** 클릭 → 오른쪽 **`개발자 모드` (`Developer Mode`)** 스위치 **ON** *(최신 Discord UI 기준 `고급` 메뉴를 거치지 않고 바로 `</> 개발자` 항목에 있습니다.)*
4. 설정 창을 닫고(`ESC`), 방금 만든 **`#습관-체크인`** 채널을 **마우스 우클릭 → 맨 아래 `채널 ID 복사`**

#### 4) Life OS 앱에 토큰/채널 등록 및 연결 확인
1. PC 바탕화면 **`LifeOS_Assistant_v2.exe`** 실행 → 플로팅 위젯 **우클릭 → `🌐 모바일 봇 / 웹훅 연동 설정`**
2. 스크롤을 내려 **Discord 카드**에서 아래 값을 입력합니다:
   * **`Bot Token:`** 1단계에서 복사한 토큰 붙여넣기 → 오른쪽 **`[연결 확인]`** 클릭 → `디스코드 연결 성공! (@봇이름)` 확인
   * **`전용 Channel ID (선택):`**
     * **3단계에서 복사한 채널 ID 입력 시:** 해당 전용 방(`#습관-체크인`)에 일반 문장만 입력해도 `@멘션` 없이 즉시 체크인됩니다.
     * **비워 둘 경우:** 봇과의 **1:1 DM 전체** + 서버 채널에서 **`@봇이름` 멘션** 또는 **`!status` / `!nudge` / `!review` / `!어제 <내용>`** 명령에만 반응합니다. *(일반 대화방 도배 방지)*
   * **`💬 디스코드(Discord) AI 비서 봇 자동 수신`** 체크박스 **ON**
3. 맨 아래 **`[저장 및 즉시 연결 적용]`** 클릭 → 맨 위 상태 카드에 **`• 디스코드 봇: 🟢 수신 중`** 이 표시되면 연결 완료!

#### 5) 사용 가능한 명령어 & 트러블슈팅 FAQ
* **명령어 예시 (DM · 전용 채널 · `@멘션` 지원):**
  * `!help` *(또는 `/start`)*: 인사말 및 명령어 안내
  * `!status` *(또는 `!today`, `/status`)*: 오늘 달성 현황(`X/35`) 및 남은 추천 습관
  * `!nudge` *(또는 `/nudge`)*: 현재 시간대 추천 습관 넛지 요청
  * `!review` *(또는 `/review`)*: 주간 종합 달성률 리포트 및 엑셀 주간회고 저장
  * `!어제 <내용>` *(또는 `!yesterday`, `!昨日`, `!昨天`)*: 어제 날짜로 소급 체크인
  * **일반 자연어 문장:** 예) `오늘 아침 햇빛 15분 쬐고 90분 딥워크 완료!` *(전용 Channel ID 지정 방 또는 1:1 DM에서 바로 인식)*
* **자주 겪는 오류 해결 FAQ:**
  * **`Clyde: 메시지를 전송할 수 없어요` (`360060145013`) 오류가 1:1 DM에서 뜨는 경우:**
    1. 먼저 Life OS 앱에서 **Bot Token 저장 및 연결(`🟢 수신 중`)** 이 켜져 있는지 확인하세요.
    2. 서버 상단 이름 클릭 → **`개인정보 보호 설정` → `다이렉트 메시지`** 스위치를 켜거나, 사용자 설정(`⚙️`) **`콘텐츠 및 소셜`** 에서 서버 멤버 DM 허용을 켜세요. *(단, 서버 내 `#습관-체크인` 같은 채팅 채널에서는 DM 허용 설정과 무관하게 즉시 응답합니다.)*
  * **🔒 비공개 채널에서 봇이 응답하지 않는 경우:**
    * 해당 채널 **`⚙️(편집) → 권한`** 에 초대된 봇 계정이 추가되어 있는지, 개발자 포털의 **`MESSAGE CONTENT INTENT`** 가 켜져 있는지 확인하세요.

---

### 🔹 방법 C: Android (`HTTP Request Shortcuts` / `MacroDroid`) · Wi-Fi iPhone 공기계 · 로컬 웹훅
iPhone 단축어 대신 **안드로이드 메인폰**이나 **집 Wi-Fi에 연결된 보조 iPhone 공기계**, 그리고 **개인 HTTP 자동화**에서도 원터치 체크인을 쓸 수 있습니다.

1. 앱 봇 설정창에서 **Host를 `0.0.0.0`**, **Port를 `8080`**으로 두고 체크 후 저장합니다.
   * *(💡 **Windows 방화벽 확인:** PC의 Wi-Fi 네트워크 프로필이 `공용(Public)`이면 폰 접속이 차단될 수 있으므로, Windows 네트워크 설정에서 **`개인(Private)`**으로 변경하거나 `8080` TCP 인바운드 방화벽을 허용하세요.)*
2. 앱 내 **`[🧪 테스트 발송]`** 버튼으로 `http://127.0.0.1:8080/stats`가 `HTTP 200 OK`인지 확인합니다.
3. PC의 실제 Wi-Fi 내부 IP를 확인합니다 (`ipconfig` → `무선 LAN 어댑터 Wi-Fi`의 IPv4 주소 예: `192.168.x.x` — WSL/VirtualBox 등 가상 어댑터 IP 제외). 먼저 스마트폰 브라우저에서 `http://<PC_내부IP>:8080/stats`가 열리는지 확인하세요.
4. **안드로이드 설정 (추천: Google Play 무료 앱 `HTTP Request Shortcuts` — Roland Meyer):**
   - `+` 새 단축어 → **Regular Shortcut** → Method: **`POST`**
   - URL: **`http://<PC_내부IP>:8080/checkin`**  
     *(⚠️ 앱 기본값이 `https://`로 채워져 있는 경우가 많으니 반드시 **`http://`**로 변경하세요. `https://` 그대로 두면 `unable to parse TLS packet header` 오류가 발생합니다.)*
   - Request Body 유형: `Parameters`가 아닌 **`Custom Text`** 선택, Content-Type: **`application/json`**
   - Body 본문 *(모바일 둥근 따옴표 `“ ”` 대신 영문 직선 `"` 사용 — 형식이 다르면 `400 Bad Request` 발생)*:  
     `{"message": "{습관메시지}", "channel": "Android"}` *(홈 화면 위젯 버튼으로 배치 가능)*
5. **보조 iPhone 공기계 (집 Wi-Fi 전용):**
   - Apple `단축어` 앱 → **URL 내용 가져오기** (`http://<PC_내부IP>:8080/checkin`, Method: `POST`, JSON 본문 `{"message": "...", "channel": "iPhone Wi-Fi"}`) → 유심 없이 집 Wi-Fi만으로 데스크 체크인 버튼으로 활용 가능

| 메서드 | 엔드포인트 | 설명 |
|:---:|:---|:---|
| `GET` | `/stats` | 오늘/주간 달성 현황 및 완료 습관 목록 조회 |
| `GET` | `/habits` | 35대 습관 목록 및 인식 키워드 JSON 조회 |
| `POST` | `/checkin` | 자연어 일과 보고 (`message`, 선택: `channel`, `date`, `day_offset`) |
| `POST` | `/nudge` | 현재 시간대 스마트 넛지 질문 요청 |
| `POST` | `/review` | 주간 회고 리포트 생성 및 엑셀 저장 |

---

### 🔹 100% 오프라인 다국어 로컬 NLP 엔진 (API 토큰 비용 0원)
모든 자연어 습관 매칭(`ai_secretary.py` / `LocalHabitNLP`)과 페르소나 코칭은 외부 유료 LLM API 키나 토큰 소모 없이 **내 PC에서 100% 무료·오프라인**으로 즉시 동작합니다. 위젯의 **`[?]`** 버튼을 누르면 4개 국어 인식 키워드를 바로 검색해 입력할 수 있습니다.
