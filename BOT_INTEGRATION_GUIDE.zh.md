# 🤖 AI 助手与移动端 Bot（Telegram · Discord · Android/Wi-Fi 快捷指令）集成指南

> 🌐 **Languages:** [🇺🇸 English](BOT_INTEGRATION_GUIDE.md) · [🇰🇷 한국어](BOT_INTEGRATION_GUIDE.ko.md) · [🇯🇵 日本語](BOT_INTEGRATION_GUIDE.ja.md) · **🇨🇳 简体中文**

现在，手机机器人、局域网 Webhook 与电脑桌面悬浮窗可以实时共享**同一份 SQLite 时间轴数据库（`life_os.db`）和 Excel 工作簿（`Life_OS_Successful_Habits.xlsx`）**。  
出门在外用手机发送一句打卡记录，PC 悬浮窗和 Excel 会立刻同步更新！

---

## 1. 统一架构概览

```text
[手机 / 即时通讯 / 快捷指令通道]
  ├─► 1) Telegram Bot (/start, /status, /nudge, /review, /昨天, 自然语言) [外出移动网络主推]
  ├─► 2) Discord 内置 Bot (私信自动回复 · 专用 Channel ID · @提及 / !status / !nudge)
  ├─► 3) Android HTTP Request Shortcuts / MacroDroid · Wi-Fi iPhone 快捷指令 · 本地 Webhook (/checkin)
  └─► 4) CLI 模式 & 100% 离线四语言本地 NLP 引擎（零 API 令牌消耗）
         │
         ▼
[Life OS 统一核心 (AssistantEngine + DatabaseManager + i18n)]
  ├─► 1) 4语言 35习惯自然语言解析 (zh/en/ko/ja) + 4大导师人格个性化教练
  ├─► 2) life_os.db (SQLite WAL) 持久化存储
  ├─► 3) 桌面悬浮窗实时弹窗提醒与自动刷新
  └─► 4) Life_OS_Successful_Habits.xlsx（每日追踪、仪表盘、AI日志）自动双向同步
```

---

## 2. 最简配置方式（应用内 GUI 一键开关 — 推荐）

无需额外搭建服务器、端口映射或内网穿透，在 **`LifeOS_Assistant_v2.exe`** 内部即可直接开关：

1. 右键桌面悬浮窗（或点击 `⚙️` → **`🌐 机器人与Webhook...`**）
2. 勾选需要启用的服务，点击 **`[保存并立即应用连接]`**：
   - **Telegram AI 助手 Bot：** 只需一个 `@BotFather` Token，即可在外网（4G/5G）全天候后台接收（HTTP Long-Polling）
   - **Discord AI 助手 Bot：** 无需任何穿透工具，使用纯 Python Gateway v10 (WSS) + REST 直连 Discord
   - **本地 Webhook 桥接 (`127.0.0.1` / `0.0.0.0:8080`)：** 支持 Android `HTTP Request Shortcuts` / `MacroDroid` 以及连接家庭 Wi-Fi 的备用 iPhone 快捷指令触发

---

## 3. 各渠道详细联动步骤

> ⚠️ **外部平台界面与政策变更声明：** Telegram（`@BotFather`）、Discord（`Discord Developer Portal` 及客户端设置）与 Android/iOS 快捷指令应用的菜单位置、名称或机器人权限政策可能会随各自官方更新而调整，恕不另行通知。如实际界面与本指南略有出入，请以对方最新官方文档或对应选项名（`Bot`、`Reset Token`、`Message Content Intent`、`Developer Mode` 等）为准。

### 🔹 方式 A：Telegram Bot（Android / iPhone 外出随时使用首选）
> *(注：Telegram 注册流程及 `@BotFather` 引导文案可能随官方版本迭代而微调。)*
> ⚠️ **谨防假冒 Bot！** Telegram 搜索框中存在大量高仿 `BotFather` 账号。务必认准 **官方蓝色认证对勾 (✓)** 及 **800万+ 月活用户标识**！
> - **官方直达：** https://t.me/BotFather （或在软件设置内点击 `[🔗 打开官方 @BotFather]`）
> - **防骗技巧：** 在 Telegram 自己的 `Saved Messages（收藏夹）` 中输入并发送 `@BotFather`，直接点击蓝色文字即可百分之百进入真身对话。

1. **获取 Token：** 打开官方 `@BotFather` → `[START]` → `/newbot` → 输入机器人名称及以 `bot` 结尾的英文用户名 → 复制 **HTTP API Token**
2. **接入应用：** 在悬浮窗设置填入 **`Bot Token:`** → 点击 **`[测试连接]`** → 勾选 **`📱 启用 Telegram AI 助手 Bot`** → 点击 **`[保存并立即应用连接]`** → 进入 `t.me/你的机器人ID` 点击 `[START]`
3. **常用指令：** `/status`、`/nudge`、`/review`、`/昨天 <内容>`（亦支持 `/yesterday`、`/어제`、`/昨日`），或直接发送自然语言

---

### 🔹 方式 B：内置 Discord Bot（`discord_bot.py` — 无需内网穿透）
完全基于 Python 标准库实现的 RFC 6455 TLS WebSocket（**Gateway v10**）+ **REST API** 直连 Discord。
> *(注：Discord Developer Portal 及客户端设置路径可能随 Discord 版本更新发生变化。)*

#### 1) 在 Discord 开发者后台创建机器人并获取 Token
1. 打开 **[Discord Developer Portal](https://discord.com/developers/applications)** 并登录你的 Discord 账号。（也可在软件设置卡内直接点击 `[🔗 Discord 开发者后台]`）
2. 点击右上角 **`New Application`** → 输入名称（例如 `Life OS 助手`）→ 同意条款并点 **`Create`**
3. 点击左侧栏 **`Bot`** 菜单。  
   *(💡 若浏览器窗口较窄导致左侧菜单隐藏，点击左上角 `DEVELOPER PORTAL` 旁的 **`☰`（三条横线菜单）** 即可找到 **`Bot`**。)*
4. 点击 **`Token`** 下方的 **`Reset Token`** 并完成确认后，**复制 Bot Token**。  
   *(⚠️ 令牌关闭页面后无法再次明文查看，请妥善保存切勿外泄。)*
5. 留在 **`Bot`** 页面向下滚动找到 **`Privileged Gateway Intents`**：
   * 打开 **`MESSAGE CONTENT INTENT`** 开关，并点击底部 **`Save Changes`**！
   * *(若未开启此开关，机器人无法读取服务器文字频道的内容，只能在 1对1 私信中响应。)*

#### 2) 将机器人邀请进你的 Discord 服务器 (`OAuth2 URL Generator`)
1. 点击左上角 **`☰` → `OAuth2` → `URL Generator`**
2. 在 **`SCOPES`** 中勾选 **`bot`**
3. 在下方展开的 **`BOT PERMISSIONS`** 中至少勾选以下 **3 项权限**：
   * **`View Channels`**（查看频道）
   * **`Send Messages`**（发送消息）
   * **`Read Message History`**（读取历史消息）
4. 复制最底部的 **`Generated URL`** → 在浏览器新标签页打开 → 选择你的服务器 → **`Continue` → `Authorize`**

#### 3) 创建专用打卡频道并复制 Channel ID（推荐）
1. 在你的 Discord 服务器左侧 **文字频道** 旁点击 **`+`**，例如新建 **`#habit-checkin`** 频道。
   * *(🔒 若设为**私密频道**，请在频道 **`⚙️ 编辑频道 → 权限 → 添加成员或角色`** 中务必把**机器人账号**加进去。)*
2. 点击 Discord 左下角头像旁的 **`⚙️（用户设置）`**
3. 左侧滑到底部点击 **`</> 开发者` (`Developer`)** → 开启 **`开发者模式` (`Developer Mode`)** *(最新版界面已直接归入 `</> 开发者` 菜单)*
4. 关闭设置（`ESC`），**右键 `#habit-checkin` → 最底部 `复制频道 ID`**

#### 4) 在 Life OS 应用填写并启用
1. 打开 **`LifeOS_Assistant_v2.exe`** → 右键悬浮窗 → **`🌐 移动机器人 / Webhook 设置`**
2. 向下找到 **Discord 卡片**：
   * **`Bot Token:`** 粘贴第1步的令牌 → 点击 **`[测试连接]`** 确认显示连接成功
   * **`专用 Channel ID (可选):`**
     * **填入频道 ID 时：** 在该专用频道直接发普通日常句子即可打卡，无需 `@提及`。
     * **留空时：** 支持与机器人的 **全部 1对1 私信（DM）**，以及服务器频道中 **`@机器人`** 或 **`!status` / `!nudge` / `!review` / `!昨天 <内容>`** 指令触发。
   * 勾选 **`💬 启用 Discord AI 助手 Bot`**
3. 点击最下方 **`[保存并立即应用连接]`** → 顶部状态栏显示 **`🟢 监听中`** 即大功告成！

#### 5) 常用指令与常见问题排查
* **支持指令（1对1 私信 · 专用频道 · `@提及`）：**
  * `!help` *(或 `/start`)*：查看问候与指令说明
  * `!status` *(或 `!today`, `/status`)*：查看今日完成度（`X/35`）与待完成建议
  * `!nudge` *(或 `/nudge`)*：请求结合当前时段的智能提醒
  * `!review` *(或 `/review`)*：生成本周汇总并更新 Excel 周复盘表
  * `!昨天 <内容>` *(或 `!yesterday`, `!어제`, `!昨日`)*：补记昨天的习惯日志
  * **自然语言整句：** 如 `早上晒太阳15分钟，完成90分钟深度工作！`
* **高频报错排查 FAQ：**
  * **1对1 私信提示 `Clyde: 无法发送此消息` (`360060145013`)：**
    1. 先确认 Life OS 应用内已保存 Token 并处于 **`🟢 监听中`** 状态。
    2. 点击服务器顶部名称 → **`隐私设置` → 开启 `私信`**，或在用户设置（`⚙️`）**`内容与社交`** 中允许同服务器成员私信。*(若使用服务器内的 `#habit-checkin` 等频道，则不受私信开关限制可立即回复。)*
  * **🔒 私密频道无响应：** 请核对后台的 `MESSAGE CONTENT INTENT` 是否已保存开启，且该频道权限里已添加机器人成员。

---

### 🔹 方式 C：Android (`HTTP Request Shortcuts` / `MacroDroid`) · Wi-Fi 备用 iPhone · 本地 Webhook
可使用 **Android 主力机**、**仅连家庭 Wi-Fi 的备用 iPhone（无需插卡）** 或本地 HTTP 脚本实现桌面一键打卡。

1. 在应用 Bot 设置开启 **本地 Webhook 桥接**，将 **Host 设为 `0.0.0.0`**、**Port 设为 `8080`** 并保存。
   * *(💡 **Windows 防火墙提示：** 若电脑连接的家庭 Wi-Fi 在 Windows 中被设为 **`公用 (Public)`**，手机访问可能会被拦截；请在 Windows 网络设置中切换为 **`专用 (Private)`**，或放行 TCP `8080` 入站端口。)*
2. 点击设置页内的 **`[🧪 测试 Webhook]`**，确认 `http://127.0.0.1:8080/stats` 返回 `HTTP 200 OK`。
3. 查看电脑真实无线局域网 IP（执行 `ipconfig` → `无线局域网适配器 WLAN` 的 IPv4 地址，如 `192.168.x.x`，切勿误用 WSL/VirtualBox 虚拟网卡地址），先在手机浏览器打开 `http://<电脑局域网IP>:8080/stats` 确认能访问 JSON。
4. **Android 配置建议（推荐 Google Play 免费开源应用 `HTTP Request Shortcuts` — Roland Meyer）：**
   - 点击 `+` 新建 → **Regular Shortcut** → Method 选 **`POST`**
   - URL 填写 **`http://<电脑局域网IP>:8080/checkin`**  
     *(⚠️ 很多应用会默认预填 `https://`，请务必改为 **`http://`**！否则使用 `https://` 会报错 `unable to parse TLS packet header`。)*
   - Request Body Type：选择 **`Custom Text`**（不要选 `Parameters`），Content-Type 填 **`application/json`**
   - Body 内容 *(务必使用英文直引号 `"`，手机中文弯引号 `“ ”` 会导致 `400 Bad Request`)*：  
     `{"message": "{习惯内容}", "channel": "Android"}` *(可添加至手机桌面快捷小组件)*
5. **备用 Wi-Fi iPhone（桌面快捷按钮）：**
   - 苹果 **`快捷指令`** → **获取 URL 内容**（URL 填 `http://<电脑局域网IP>:8080/checkin`，方法 `POST`，请求体 JSON `{"message": "...", "channel": "iPhone Wi-Fi"}`）。

| 请求方式 | 接口路径 | 功能说明 |
|:---:|:---|:---|
| `GET` | `/stats` | 查询今日及本周习惯统计与已完成列表 |
| `GET` | `/habits` | 返回 35 项核心习惯与中英日韩识别关键词 JSON |
| `POST` | `/checkin` | 提交自然语言打卡（`message`，可选 `channel`、`date`、`day_offset`） |
| `POST` | `/nudge` | 请求符合当前时间段的智能推送问候 |
| `POST` | `/review` | 生成周报总结并写入 Excel 周复盘表 |

---

### 🔹 内置 100% 离线多语言本地 NLP 引擎（零 Token 费用）
所有自然语言习惯匹配（`ai_secretary.py` / `LocalHabitNLP`）及导师评语均 **完全在本地离线运行**，无需填写任何付费外部 LLM API 密钥或消耗额度。点击悬浮窗内的 **`[?]`** 按钮即可检索并一键填入中英日韩关键词。
