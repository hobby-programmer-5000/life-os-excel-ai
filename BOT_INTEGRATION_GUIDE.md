# 🤖 AI Assistant & Mobile Bot (Telegram · Discord · Android/Wi-Fi Shortcuts) Integration Guide

> 🌐 **Languages:** **🇺🇸 English** · [🇰🇷 한국어](BOT_INTEGRATION_GUIDE.ko.md) · [🇯🇵 日本語](BOT_INTEGRATION_GUIDE.ja.md) · [🇨🇳 简体中文](BOT_INTEGRATION_GUIDE.zh.md)

Your mobile bots, local LAN webhooks, and the desktop floating widget share the **exact same SQLite timeline (`life_os.db`) and Excel workbook (`Life_OS_Successful_Habits.xlsx`)** in real time.  
A check-in sent from your phone while away immediately updates both your PC widget and Excel file!

---

## 1. Unified Architecture Overview

```text
[Mobile / Messenger / Shortcut Channels]
  ├─► 1) Telegram Bot (/start, /status, /nudge, /review, /yesterday, natural text) [Best over LTE/5G]
  ├─► 2) Discord Built-in Bot (DM auto-reply · Dedicated Channel ID · @mention / !status / !nudge)
  ├─► 3) Android HTTP Request Shortcuts / MacroDroid · Wi-Fi iPhone Shortcuts · Local Webhook (/checkin)
  └─► 4) CLI Mode & 100% Offline Local Multilingual NLP Engine (Zero API Tokens Required)
         │
         ▼
[Life OS Unified Core (AssistantEngine + DatabaseManager + i18n)]
  ├─► 1) Multilingual 35-habit NLP matching (en/ko/ja/zh) + 4 Role-Model Persona coaching
  ├─► 2) Persistent SQLite WAL timeline (life_os.db)
  ├─► 3) Real-time Desktop Floating Widget toast & auto-refresh
  └─► 4) Automatic 5-sheet Excel sync (Daily Tracker, Dashboard, AI Assistant Log)
```

---

## 2. Easiest Setup (1-Click GUI Inside the App — Recommended)

Without running external servers, port forwarding, or tunnels, configure everything inside **`LifeOS_Assistant_v2.exe`**:

1. Right-click the floating widget (or click `⚙️` → **`🌐 Mobile Bots & Webhook...`**) → **`🌐 Mobile Bot & Webhook Settings`**
2. Toggle the channels you want and click **`[Save & Connect Live]`**:
   - **Telegram AI Assistant Bot:** Works over external cellular/Wi-Fi using only an official `@BotFather` token (HTTP Long-Polling).
   - **Discord AI Assistant Bot:** Connects directly via Gateway v10 (WSS) + REST using a Discord Developer Portal token — no external tunnel needed.
   - **Local Webhook Bridge (`127.0.0.1` / `0.0.0.0:8080`):** Connects Android `HTTP Request Shortcuts` / `MacroDroid`, Wi-Fi auxiliary iPhones (`Shortcuts`), and local HTTP scripts.

---

## 3. Step-by-Step Channel Setup Guides

> ⚠️ **External Platform UI & Policy Notice:** Menus, labels, permissions, and gateway policies inside Telegram (`@BotFather`), Discord (`Discord Developer Portal` & desktop/mobile clients), and Android/iOS shortcut apps can change at any time due to updates by those third-party platforms. If your screen looks slightly different, refer to each platform's latest official docs or match equivalent labels (`Bot`, `Reset Token`, `Message Content Intent`, `Developer Mode`, etc.).

### 🔹 Method A: Telegram Bot (Recommended for Android & iPhone Anywhere via LTE/5G)
> *(Note: Telegram onboarding menus and `@BotFather` prompts may change with Telegram updates.)*
> ⚠️ **Watch Out for Impersonators!** Telegram search contains fake `BotFather` accounts. Verify the **blue official verification checkmark (✓)** and **8M+ monthly users**!
> - **Official Link:** https://t.me/BotFather (or click `[🔗 Official @BotFather]` inside app settings)
> - **Safe Tip:** Type `@BotFather` into your own `Saved Messages` chat and tap the clickable handle — that always opens the real official bot.

1. **Create Bot & Copy Token:** Open official `@BotFather` → **`[START]`** → `/newbot` → enter display name and a username ending in `bot` → copy the **HTTP API Token**.
2. **Connect in App:** Paste into **`Bot Token:`** in widget settings → click **`[Test Connection]`** → check **`📱 Enable Telegram AI Assistant Bot`** → click **`[Save & Connect Live]`** → open `t.me/<your_bot_username>` and tap **`[START]`**.
3. **Commands:** `/status`, `/nudge`, `/review`, `/yesterday <text>` (or `/어제`, `/昨日`, `/昨天`), or any plain daily sentence.

---

### 🔹 Method B: Built-in Discord Bot (`discord_bot.py` — Zero Tunnels Required)
Connects directly via pure Python stdlib RFC 6455 TLS WebSocket (**Gateway v10**) + **REST API** without ngrok or external hosting.
> *(Note: Discord Developer Portal and Discord client paths may change with future Discord updates.)*

#### 1) Create the Bot & Token in Discord Developer Portal
1. Open **[Discord Developer Portal](https://discord.com/developers/applications)** and sign in. *(Or click `[🔗 Discord Dev Portal]` in the widget's bot dialog.)*
2. Click **`New Application`** (top-right) → name it (e.g., `Life OS Assistant`) → accept terms → **`Create`**.
3. Open the **`Bot`** tab on the left sidebar.  
   *(💡 If your browser window is narrow, the left sidebar collapses — click the **`☰` hamburger menu** next to `DEVELOPER PORTAL` at the top-left to reveal **`Bot`**.)*
4. Click **`Reset Token`** under **`Token`**, complete confirmation/2FA, and **Copy** the Bot Token.  
   *(⚠️ Never share this token publicly; store it safely.)*
5. Scroll down on the same **`Bot`** page to **`Privileged Gateway Intents`**:
   * Toggle **`MESSAGE CONTENT INTENT`** **ON** and click **`Save Changes`** at the bottom!
   * *(Without this intent enabled, the bot cannot read messages posted in server text channels and will only work in 1:1 DMs.)*

#### 2) Invite the Bot to Your Discord Server (`OAuth2 URL Generator`)
1. Open **`☰` → `OAuth2` → `URL Generator`**.
2. Under **`SCOPES`**, check **`bot`**.
3. Under **`BOT PERMISSIONS`** below it, check at least these **3 permissions**:
   * **`View Channels`**
   * **`Send Messages`**
   * **`Read Message History`**
4. Click **`Copy`** beside **`Generated URL`** at the bottom → open it in a new tab → pick your server → **`Continue` → `Authorize`**.

#### 3) Create a Dedicated Check-in Channel & Copy Its Channel ID (Recommended)
1. In your Discord server sidebar, click **`+`** next to **Text Channels** and create e.g. **`#habit-checkin`**.
   * *(🔒 If you make it a **Private Channel**, open **`⚙️ Edit Channel → Permissions → Add members or roles`** and explicitly add your **Bot account**.)*
2. Click **`⚙️ (User Settings)`** near your profile avatar (bottom-left).
3. Scroll down to **`</> Developer`** *(modern Discord UI places it directly under `</> Developer`)* → turn **`Developer Mode`** **ON**.
4. Close settings (`ESC`), **right-click `#habit-checkin` → `Copy Channel ID`** at the bottom.

#### 4) Register Token & Channel ID in Life OS
1. Open **`LifeOS_Assistant_v2.exe`** → right-click widget → **`🌐 Mobile Bot & Webhook Settings`**.
2. Scroll to the **Discord** card:
   * **`Bot Token:`** Paste your token → click **`[Test Connection]`** → confirm `Connected (@YourBot)`.
   * **`Dedicated Channel ID (Optional):`**
     * **When filled:** Any natural sentence posted inside that channel logs immediately without needing `@mention`.
     * **When left empty:** The bot replies to all **1:1 DMs**, plus server messages that **`@mention` the bot** or start with **`!status` / `!nudge` / `!review` / `!yesterday <text>`** *(keeps general chat channels noise-free)*.
   * Check **`💬 Enable Discord AI Assistant Bot`**.
3. Click **`[Save & Connect Live]`** → confirm the top status box shows **`Discord Bot: 🟢 Listening`**.

#### 5) Commands & Troubleshooting FAQ
* **Supported Commands (1:1 DM · Dedicated Channel · `@mention`):**
  * `!help` *(or `/start`)*: Greeting & command overview
  * `!status` *(or `!today`, `/status`)*: Today's progress (`X/35`) & remaining suggestions
  * `!nudge` *(or `/nudge`)*: Request a time-appropriate habit nudge
  * `!review` *(or `/review`)*: Weekly summary & update Excel `Weekly Review` sheet
  * `!yesterday <text>` *(or `!어제`, `!昨日`, `!昨天`)*: Backfill yesterday's log
  * **Natural text:** e.g. `Got 15 min morning sunlight and 90 min deep work done!`
* **Common Issues:**
  * **`Clyde: Your message could not be delivered` (`360060145013`) in 1:1 DMs:**
    1. Confirm the Discord bot is enabled and **`🟢 Listening`** inside Life OS.
    2. Click your server name → **`Privacy Settings` → enable `Direct Messages`**, or enable server DMs under **`User Settings → Content & Social`**. *(Server text channels like `#habit-checkin` work immediately even if DMs are restricted.)*
  * **🔒 Bot doesn't respond in a private channel:** Verify both **`MESSAGE CONTENT INTENT`** (Developer Portal) AND the bot role/member in **`Edit Channel → Permissions`**.

---

### 🔹 Method C: Android (`HTTP Request Shortcuts` / `MacroDroid`) · Wi-Fi Auxiliary iPhone · Local Webhook
Use one-tap home-screen check-in buttons on **Android**, an **auxiliary Wi-Fi iPhone (no SIM needed)**, or local automation tools.

1. In Life OS bot settings, enable **Local Webhook Bridge** with **Host `0.0.0.0`** and **Port `8080`**, then save.
   * *(💡 **Windows Firewall:** If Windows sets your home Wi-Fi to **`Public`**, inbound LAN phone requests are blocked. Switch it to **`Private`** in Windows Network Settings or allow TCP port `8080` inbound.)*
2. Click **`[🧪 Test Webhook]`** inside the app to confirm `http://127.0.0.1:8080/stats` returns `HTTP 200 OK`.
3. Find your PC's Wi-Fi IPv4 address (`ipconfig` → Wireless LAN adapter Wi-Fi, e.g. `192.168.x.x` — ignore WSL/VirtualBox virtual adapters). Verify `http://<YOUR_PC_LAN_IP>:8080/stats` opens in your phone browser first.
4. **Android Setup (Recommended free app on Google Play: `HTTP Request Shortcuts` by Roland Meyer):**
   - Tap `+` → **Regular Shortcut** → Method: **`POST`**
   - URL: **`http://<YOUR_PC_LAN_IP>:8080/checkin`**  
     *(⚠️ Many apps pre-fill `https://`. You **must** change it to **`http://`**; otherwise `https://` triggers `unable to parse TLS packet header`.)*
   - Request Body Type: choose **`Custom Text`** *(NOT `Parameters`)*, Content-Type: **`application/json`**
   - Body *(use straight ASCII quotes `"`, never curved quotes `“ ”`, which cause `400 Bad Request`)*:  
     `{"message": "{habit message}", "channel": "Android"}` *(pin to your Android home screen!)*
5. **Auxiliary Wi-Fi iPhone (Desk Button Over Home Wi-Fi):**
   - Apple `Shortcuts` app → **Get Contents of URL** (`http://<YOUR_PC_LAN_IP>:8080/checkin`, Method: `POST`, JSON body `{"message": "...", "channel": "iPhone Wi-Fi"}`).

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/stats` | Fetch today's / weekly stats and completed habit IDs |
| `GET` | `/habits` | Retrieve all 35 habits and keywords as JSON |
| `POST` | `/checkin` | Submit natural-language log (`message`, optional `channel`, `date`, `day_offset`) |
| `POST` | `/nudge` | Generate a time-appropriate smart nudge |
| `POST` | `/review` | Generate weekly report and sync Excel `Weekly Review` |

---

### 🔹 Built-in Offline Local Multilingual NLP (Zero Token Cost)
All natural-language habit recognition (`ai_secretary.py` / `LocalHabitNLP`) and mentor coaching run **100% locally offline** without external LLM API keys or recurring token fees. Click **`[?]`** inside the floating widget to inspect or insert any keyword in English, Korean, Japanese, or Simplified Chinese.
