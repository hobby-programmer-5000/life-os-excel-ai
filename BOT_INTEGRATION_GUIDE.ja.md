# 🤖 AI アシスタント ＆ モバイル Bot（Telegram · Discord · Android/Wi-Fi ショートカット）連携ガイド

> 🌐 **Languages:** [🇺🇸 English](BOT_INTEGRATION_GUIDE.md) · [🇰🇷 한국어](BOT_INTEGRATION_GUIDE.ko.md) · **🇯🇵 日本語** · [🇨🇳 简体中文](BOT_INTEGRATION_GUIDE.zh.md)

モバイル Bot・ローカル Webhook とデスクトップ浮動ウィジェットが、**同一の SQLite タイムライン（`life_os.db`）と Excel（`Life_OS_Successful_Habits.xlsx`）**をリアルタイムで共有します。  
外出先のスマートフォンから送ったチェックインが、即座に PC ウィジェットと Excel の両方に反映されます。

---

## 1. 統合アーキテクチャ概要

```text
[モバイル / メッセンジャー / ショートカット]
  ├─► 1) Telegram Bot (/start, /status, /nudge, /review, /昨日, 自然文) [外出先 LTE/5G 推奨]
  ├─► 2) Discord 内蔵 Bot (DM 自動応答・専用チャンネルID・@メンション / !status / !nudge)
  ├─► 3) Android HTTP Request Shortcuts / MacroDroid · Wi-Fi iPhone ショートカット · ローカル Webhook (/checkin)
  └─► 4) CLI モード ＆ 100% オフライン多言語ローカル NLP エンジン（API トークン不要）
         │
         ▼
[Life OS 統合コア (AssistantEngine + DatabaseManager + i18n)]
  ├─► 1) 4言語対応 35習慣自然文解析 (ja/en/ko/zh) ＋ 4大ペルソナコーチング生成
  ├─► 2) life_os.db (SQLite WAL) 永続保存
  ├─► 3) デスクトップ浮動ウィジェット リアルタイム通知・自動更新
  └─► 4) Life_OS_Successful_Habits.xlsx（日次トラッカー・ダッシュボード・AI連携ログ）自動同期
```

---

## 2. 一番簡単な設定方法（アプリ内 GUI ワンクリック推奨）

別ターミナルや外部公開サーバー（トンネル・ポート開放）を用意しなくても、`LifeOS_Assistant_v2.exe` 画面内からそのまま有効化できます：

1. 浮動ウィジェットを右クリック（または `⚙️` → **`🌐 モバイルBot / Webhook...`**）
2. 使いたい連携をオンにして **`[保存して即時接続]`** をクリック：
   - **Telegram AI アシスタント Bot:** `@BotFather` のトークンだけで外部回線（LTE/5G）からも常時受信可能（HTTP Long-Polling）
   - **Discord AI アシスタント Bot:** 外部トンネル不要で Discord Gateway v10（WSS）+ REST に直接接続
   - **ローカル Webhook ブリッジ (`127.0.0.1` / `0.0.0.0:8080`):** Android `HTTP Request Shortcuts` / `MacroDroid`、自宅 Wi-Fi 専用補助 iPhone（`ショートカット`）等からのローカル HTTP 自動化に対応

---

## 3. チャネル別 詳細連携ガイド

> ⚠️ **外部プラットフォームの UI・仕様変更に関するご注意:** Telegram（`@BotFather`）、Discord（`Discord Developer Portal` およびクライアント設定）、Android/iOS アプリのメニュー構成や権限仕様は、各提供元のアップデートにより予告なく変更される場合があります。画面表記が本ガイドと一部異なる場合は、最新の公式 UI や対応するメニュー名（`Bot`、`Reset Token`、`Message Content Intent`、`Developer Mode` 等）に読み替えて設定してください。

### 🔹 方法 A: Telegram Bot（Android / iPhone 外出時メイン利用に最適）
> *(※ Telegram の画面遷移や `@BotFather` の文言はアップデートにより変わる場合があります。)*
> ⚠️ **なりすまし Bot に注意！** Telegram 検索には偽の `BotFather` が多数存在します。必ず **公式青い認証バッジ (✓)** と **月間利用者 800万人+** を確認してください。
> - **公式リンク:** https://t.me/BotFather （またはアプリ設定画面の `[🔗 公式 @BotFather を開く]` ボタン）
> - **安全なコツ:** Telegram の `Saved Messages` に `@BotFather` と送信して青いリンクをタップすると偽物を確実に回避できます。

1. **トークン発行:** 公式 `@BotFather` → `[START]` → `/newbot` → 表示名と末尾が `bot` の英数字 ID を入力 → **HTTP API Token** をコピー
2. **アプリ接続:** 設定画面 **`Bot Token:`** に貼り付け → **`[接続テスト]`** → **`📱 Telegram AI アシスタント Bot`** にチェック → **`[保存して即時接続]`** → `t.me/自分のBotID` で `[START]`
3. **コマンド例:** `/status`、`/nudge`、`/review`、`/昨日 <内容>`（または `/yesterday`、`/어제`、`/昨天`）、通常の自然文

---

### 🔹 方法 B: Discord 内蔵 Bot（`discord_bot.py` — 外部トンネル不要）
標準ライブラリ実装の RFC 6455 TLS WebSocket（**Gateway v10**）＋ **REST API** により、ngrok なしで直接通信します。
> *(※ Discord Developer Portal およびアプリ側の設定項目位置は Discord の更新により変更されることがあります。)*

#### 1) Discord Developer Portal で Bot 作成 ＆ トークン発行
1. **[Discord Developer Portal](https://discord.com/developers/applications)** を開き、自身の Discord アカウントでログインします。（設定ダイアログ内の `[🔗 Discord 開発者ポータル]` ボタンからも開けます）
2. 右上 **`New Application`** → 名前（例: `Life OS Assistant`）を入力 → 規約同意して **`Create`**
3. 左メニューから **`Bot`** を開きます。  
   *(💡 ブラウザ幅が狭い場合は左メニューが折りたたまれます。左上の `DEVELOPER PORTAL` 文字横にある **`☰`（三本線アイコン）** をクリックすると **`Bot`** が表示されます。)*
4. **`Token`** 欄の **`Reset Token`** をクリックし、認証後に表示される **Bot Token** をコピーします。  
   *(⚠️ トークンは再表示できないため厳重に保管し、他人に共有しないでください。)*
5. 同 **`Bot`** 画面を下にスクロールし、**`Privileged Gateway Intents`** 欄で：
   * **`MESSAGE CONTENT INTENT`** を **ON** にしてページ下部の **`Save Changes`** をクリック！
   * *(※ これが OFF だとサーバーのチャット本文を読み取れず、1対1 DM のみ動作します。)*

#### 2) 自分の Discord サーバーへ招待 (`OAuth2 URL Generator`)
1. 左上 **`☰` → `OAuth2` → `URL Generator`** を開きます。
2. **`SCOPES`** で **`bot`** にチェックを入れます。
3. 下に展開される **`BOT PERMISSIONS`** で最低限以下の **3つ** をチェックします：
   * **`View Channels`**（チャンネルを見る）
   * **`Send Messages`**（メッセージを送信）
   * **`Read Message History`**（メッセージ履歴を読む）
4. 最下部 **`Generated URL`** の **`Copy`** をクリック → 新規タブで開く → 自分のサーバーを選択 → **`Continue` → `Authorize`**

#### 3) 専用チェックインチャンネル作成 ＆ チャンネル ID 取得（推奨）
1. サーバー左側のテキストチャンネル一覧横 **`+`** から、例として **`#habit-checkin`** チャンネルを作成します。
   * *(🔒 **プライベートチャンネル**にした場合は、該当チャンネルの **`⚙️ チャンネル編集 → 権限 → メンバーまたはロールを追加`** で必ず **Bot アカウント** も追加してください。)*
2. Discord アプリ左下のプロフィール横 **`⚙️（ユーザー設定）`** をクリック
3. 左メニュー最下部付近の **`</> 開発者` (`Developer`)** を開き、**`開発者モード` (`Developer Mode`)** を **ON** にします。
4. 設定を閉じて（`ESC`）、作成した **`#habit-checkin` を右クリック → `チャンネル ID をコピー`**

#### 4) Life OS アプリへ登録・接続確認
1. **`LifeOS_Assistant_v2.exe`** 上で右クリック → **`🌐 モバイルBot / Webhook設定`**
2. **Discord** カードで以下を入力します：
   * **`Bot Token:`** 手順1のトークンを貼り付け → **`[接続テスト]`** で接続確認
   * **`専用 Channel ID（任意）:`**
     * **ID を入力した場合:** その専用チャンネル内では `@メンション` なしの通常文も即時チェックインされます。
     * **空欄のままの場合:** Bot との **1対1 DM 全体**、およびサーバー内で **`@Bot名` メンション** または **`!status` / `!nudge` / `!review` / `!昨日 <内容>`** にのみ反応します。
   * **`💬 Discord AI アシスタント Bot`** をチェック
3. 最下部 **`[保存して即時接続]`** をクリックし、上部ステータスに **`🟢 受信中`** が表示されれば完了です。

#### 5) コマンド一覧 ＆ トラブルシューティング FAQ
* **利用可能コマンド (1対1 DM・専用チャンネル・`@メンション` 対応):**
  * `!help` *(または `/start`)*: 使い方案内
  * `!status` *(または `!today`, `/status`)*: 本日の達成率（`X/35`）と未達成習慣
  * `!nudge` *(または `/nudge`)*: 現在時間帯に合ったナッジ質問
  * `!review` *(または `/review`)*: 週間サマリー生成 ＆ Excel 週次レビュー更新
  * `!昨日 <内容>` *(または `!yesterday`, `!어제`, `!昨天`)*: 昨日の日付へ遡及チェックイン
  * **通常の自然文:** 例) `朝15分日光を浴びて90分ディープワーク完了！`
* **よくあるエラー対処:**
  * **1対1 DM で `Clyde: メッセージを送信できませんでした` (`360060145013`) が出る場合:**
    1. Life OS 側で Discord Bot が有効かつ **`🟢 受信中`** か確認してください。
    2. サーバー名クリック → **`プライバシー設定` → `ダイレクトメッセージ`** を ON にするか、ユーザー設定（`⚙️`）**`コンテンツ＆ソーシャル`** でサーバーメンバーからの DM を許可してください。*(なお、`#habit-checkin` 等のサーバー内チャンネルは DM 許可設定に関係なく即時応答します。)*
  * **🔒 プライベートチャンネルで反応しない場合:** `MESSAGE CONTENT INTENT` の ON とチャンネル権限への Bot 追加を確認してください。

---

### 🔹 方法 C: Android (`HTTP Request Shortcuts` / `MacroDroid`) · Wi-Fi 補助 iPhone · ローカル Webhook
**Android 端末**、**SIM なし自宅 Wi-Fi 専用 iPhone**、またはローカル HTTP 自動化からワンタップ記録ができます。

1. アプリの Bot 設定画面で **Host を `0.0.0.0`**、**Port を `8080`** に設定して保存します。
   * *(💡 **Windows ファイアウォール注意:** Windows の Wi-Fi プロファイルが **`パブリック (Public)`** だとスマホからの着信が遮断されます。ネットワーク設定から **`プライベート (Private)`** に変更するか、TCP `8080` 番の受信規則を許可してください。)*
2. アプリ内の **`[🧪 テスト送信]`** で `http://127.0.0.1:8080/stats` が `HTTP 200 OK` になることを確認します。
3. PC の Wi-Fi IPv4 アドレス（`ipconfig` → Wireless LAN adapter Wi-Fi 例: `192.168.x.x`、WSL/VirtualBox 仮想 NIC は除く）を確認し、スマホのブラウザで `http://<PCのLAN_IP>:8080/stats` が開くことを先にテストします。
4. **Android 設定例（Google Play 無料アプリ推奨：`HTTP Request Shortcuts` — Roland Meyer 作）:**
   - `+` 新規作成 → **Regular Shortcut** → Method: **`POST`**
   - URL: **`http://<PCのLAN_IP>:8080/checkin`**  
     *(⚠️ 初期値で `https://` が入っていることが多いため、必ず **`http://`** へ変更してください。`https://` のまま送信すると `unable to parse TLS packet header` エラーになります。)*
   - Request Body 形式: `Parameters` ではなく **`Custom Text`** を選択、Content-Type: **`application/json`**
   - Body 本文 *(全角の丸括弧引用符 `“ ”` ではなく半角直線 `"` を使用してください。不正 JSON は `400 Bad Request` になります)*:  
     `{"message": "{習慣メッセージ}", "channel": "Android"}` *(ホーム画面ウィジェット配置が可能)*
5. **補助用 Wi-Fi iPhone（デスク設置用など）:**
   - Apple **`ショートカット`** → **URL の内容を取得**（`http://<PCのLAN_IP>:8080/checkin`、方法 `POST`、JSON 本文 `{"message": "...", "channel": "iPhone Wi-Fi"}`）

| メソッド | エンドポイント | 説明 |
|:---:|:---|:---|
| `GET` | `/stats` | 本日・週間達成状況と完了習慣 ID 一覧を取得 |
| `GET` | `/habits` | 35大習慣マスターと認識キーワード JSON を取得 |
| `POST` | `/checkin` | 自然文ログを登録（`message`、任意: `channel`, `date`, `day_offset`） |
| `POST` | `/nudge` | 現在時間帯に応じたスマートナッジを取得 |
| `POST` | `/review` | 週間レポート生成 ＆ Excel 週次レビュー更新 |

---

### 🔹 100% オフライン多言語ローカル NLP（API トークン消費ゼロ）
自然文からの習慣抽出（`ai_secretary.py` / `LocalHabitNLP`）およびメンター別コーチングは、外部の有料 LLM API キーや課金トークンを一切消費せず **ローカルで完結して動作**します。ウィジェットの **`[?]`** から全35習慣の認識キーワードも検索・入力できます。
