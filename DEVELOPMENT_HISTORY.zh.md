# 🛠️ ALL-IN-ONE LIFE OS : 开发历程与分工（Development History）

> 🌐 **Languages:** [🇺🇸 English](DEVELOPMENT_HISTORY.md) · [🇰🇷 한국어](DEVELOPMENT_HISTORY.ko.md) · [🇯🇵 日本語](DEVELOPMENT_HISTORY.ja.md) · **🇨🇳 简体中文**

本文记录了 **All-in-One Life OS** 如何从“用 Excel 统一管理 35 项科学成功习惯并与 AI 助手实时打卡”的初心出发，逐步演进为多语言桌面悬浮窗、系统托盘助手及开放式移动端 Bot 生态的人机协同开发历程。

---

## 📌 开发时间线与各阶段演进

### Phase 1. 一体化成功习惯 Excel 与核心 AI 助手引擎
* **背景：** 将分散在不同书籍、论文与演讲中的日常原则梳理为 **7大人生领域 × 5项核心习惯 = 35项成功习惯**，并采用用户永久拥有的本地 Excel (`.xlsx`) 作为数据中心，而非封闭式订阅软件。
* **实现内容：**
  * [`generate_excel.py`](generate_excel.py)：自动生成 5 张工作表（`📊 仪表盘`、`🏆 成功习惯库`、`📅 每日追踪表`、`📈 每周复盘`、`🤖 AI助手日志`），并在百余处统计公式中添加 `IFERROR` 保护，彻底避免空表初期出现 `#DIV/0!` 报错。
  * [`REFERENCES.zh.md`](REFERENCES.zh.md)：系统标注全部 35 项习惯的原著出处与科学机制。
  * [`ai_secretary.py`](ai_secretary.py)：实现支持一句话识别多项习惯的离线 NLP 引擎，以及可选官方 LLM API 客户端（Grok / OpenAI / Gemini）。

---

### Phase 2. 借鉴 Google Research Harness² 构建 Windows 悬浮托盘应用
* **背景：** 消除每天手动打开 Excel 勾选的摩擦，让轻量级 AI 伙伴常驻桌面并主动提醒，据此参考 Google Research **Harness²** 理念制定软件架构规范（[`HARNESS_SPEC.zh.md`](HARNESS_SPEC.zh.md)）。
* **实现内容：**
  * **Storage Harness ([`database.py`](database.py))：** 引入 SQLite（`life_os.db`，WAL 模式），突破传统周表限制实现跨昨天/过去/未来的 **时间轴漫游（Date Traversal）**，完成 SQLite・Excel・UI 三向实时同步。
  * **Assistant Engine ([`assistant_engine.py`](assistant_engine.py))：** 内置 4 位导师人格（安德鲁·休伯曼、沃伦·巴菲特、埃隆·马斯克 & Grok、马可·奥勒留）、分时段智能提醒以及 `[✅ 完成]` · `[🚀 立即执行!]` · `[⏸️ 稍后处理]` 三态交互流。
  * **Desktop UI & OS Harness ([`floating_widget.py`](floating_widget.py), [`tray_manager.py`](tray_manager.py), [`hotkey_manager.py`](hotkey_manager.py), [`main_app.py`](main_app.py), [`build_exe.py`](build_exe.py))：** 实现半透明悬浮窗、系统托盘、`Ctrl+Shift+H` 全局快捷键、提示音/系统通知，以及无需安装 Python 即可双击运行的单文件版 `LifeOS_Assistant_v2.exe`。

---

### Phase 3. 基于真实桌面使用反馈的 UX 打磨与缺陷修复
在真实桌面长期挂机试用中发现并逐一解决了一系列体验问题：
* **窗口个性化与底部输入框遮挡修复：**
  * 支持自由设置展示习惯数（`1–35项`）、`[🎲 换一批]` / `[📌 固定]` 以及 **全部 35 项滚动视图**。
  * 修复长文教练回复导致底部自然语言输入框被挤出屏幕的排版问题（改为 Tkinter `side=tk.BOTTOM` 优先布局）。
* **防误触与实时搜索关键词弹窗：**
  * 修复短词误匹配问题（增强空格规范化与词边界校验），将 `[?]` 升级为可实时搜索的 **35习惯关键词手册**。
* **测试沙盒严格隔离：**
  * 强制通过 `LIFE_OS_DATA_DIR` 和 `TemporaryDirectory()` 运行自动化测试，杜绝污染用户个人 DB/Excel，并排查 `wb.close()` 文件锁释放。
* **日期按钮、分时段筛选与实时透明度体验升级：**
  * **动态相对日期按钮：** 查看今天（`diff == 0`）时显示 **`◀ 昨天` / `今天` / `明天 ▶`**；切换至历史或未来日期后自动变为 **`◀ 前一天` / `今天` / `后一天 ▶`**，彻底消除时间指向歧义。
  * **分时段适宜性过滤 (`HABIT_ALLOWED_HOURS`)：** 修复凌晨（`00–04点`）误推睡前习惯的条件漏洞，将晨间光照、上午决策、早起写作、下班关机仪式、睡前排毒/感恩日记等限定在合理时段询问，通用习惯则保留多样化随机抽取。
  * **实时横向透明度滑块：** 用 **`30%–100%` 横向 `tk.Scale` 滑块** 替代生硬的小数输入框，拖动即刻预览桌面半透明效果；未保存点 `✕` 关闭时自动恢复原透明度。

---

### Phase 4. 全球 4 语言统一架构 (`en` / `ko` / `ja` / `zh`)
* **背景：** 从单一韩语体验扩展为根据操作系统语言自动适配的全球多语言版。
* **实现内容：**
  * [`i18n.py`](i18n.py), [`i18n_habits.py`](i18n_habits.py), [`i18n_personas.py`](i18n_personas.py)：统一实现英/韩/日/简中四语界面、跨语言 35 习惯关键词识别、4 大导师语料、4 语言 Excel 工作簿生成与跨语言 Sheet 自动定位（`_find_sheet`）、设置窗口内界面与托盘实时热切换，以及 [`build_exe.py`](build_exe.py) 内建的多语言 PE `VSVersionInfo` 版本信息。

---

### Phase 5. 开放移动端 Bot · 局域网 Webhook 与隐私安全发布防护
* **技术路线决策：** 坚持对接对个人免费用户开放官方 Bot API 的开放生态（**Telegram**、**Discord**、**局域网 HTTP Webhook**），主动剔除存在条款风险或依赖复杂转发的封闭/非官方渠道。
* **实现与真机联调验证：**
  * **Telegram 机器人 ([`telegram_bot.py`](telegram_bot.py))：** 零外部依赖的 HTTP Long-Polling 后台轮询与 `@BotFather` 防仿冒官方验证提示卡片。
  * **内置 Discord 机器人 ([`discord_bot.py`](discord_bot.py), [`bot_commands.py`](bot_commands.py))：** 纯 Python 标准库实现 RFC 6455 TLS WebSocket（Gateway v10）+ REST API，无需安装 `discord.py` 或内网穿透；文档化了最新版入口（`⚙️ → </> 开发者 → 开发者模式`）、`Clyde` 私信限制排查以及 `专用 Channel ID` 机制。
  * **Android 与 Wi-Fi 备用 iPhone Webhook ([`bot_bridge.py`](bot_bridge.py))：** 经 Android (`HTTP Request Shortcuts`) 与 Wi-Fi 备用 iPhone (`快捷指令`) 真机实测，沉淀出 **Windows `公用(Public)`→`专用(Private)` 防火墙策略**、**`http://` 替代 `https://` 防 TLS 包头错误**、**`Custom Text` (`application/json`) + 英文直引号** 等关键避坑指南。
  * **设置卡片顺序梳理：** 将移动端设置面板卡片排序与引导文档顺序统一为 `Telegram → Discord → 本地 Webhook → LLM API`。
  * **打包与仓库隐私护栏 ([`.gitignore`](.gitignore), [`build_exe.py`](build_exe.py))：** 严禁推送或打包个人 `*.db`、`*.xlsx`、`.env`、`*.spec`、`build/`、`dist/`，并在编译 `.exe` 后自动审计二进制归档（`verify_clean_exe_bundle`）。

---

## 👥 共同贡献与角色分工（Contributors & Role Division）

本项目由人类开发者（**Product Owner / 架构与真机审校**）与 AI 结对编程助手（**实现与自动化验证**）以清晰分工的 Human-in-the-loop 模式共同完成：

| 贡献者 | 角色 (Role) | 核心负责领域 (Owned Contributions) |
| :--- | :--- | :--- |
| **[hobby-programmer-5000](https://github.com/hobby-programmer-5000)** | **Product Owner · 领域架构 · 真机测试** | • **产品愿景与领域设计：** 梳理 7 大领域 × 35 项成功习惯体系，确立用户本地 Excel 主权与桌面悬浮协同架构<br>• **Harness² 与交互方向：** 提出 Harness² 工程落地方向，定义 4 大导师人格、主动提醒及自然语言打卡体验<br>• **桌面 UX 评审与重构要求：** 指出非当日界面按钮歧义（`◀ 昨天/明天 ▶` vs `◀ 前一天/后一天 ▶`）、排查凌晨睡前习惯误推、提出 `30%–100%` 实时横向透明度滑块及 Bot 配置卡片重排<br>• **真机验证与安全边界把关：** 决策聚焦开放官方 API 并移除封闭/非官方渠道，开展 Android (`HTTP Request Shortcuts`) 与 iPhone Wi-Fi (`快捷指令`) 真机联调并定位 `http://` / `Custom Text JSON` / 防火墙关键细节，制定严格的零隐私/零令牌防泄漏发布标准<br>• **发布验收与多语言策略：** 统筹 4 语言演示录制、全文档多语言覆盖及第三方平台界面变更风险提示 |
| **[Gemini (Antigravity)](https://github.com/gemini-code-assist)** | **AI 结对编程工程师 · 全栈与自动化测试** | • **核心后端与算法实现：** 编写 [`generate_excel.py`](generate_excel.py)、[`database.py`](database.py)（SQLite WAL・跨天漫游・三向同步）、[`ai_secretary.py`](ai_secretary.py)、[`assistant_engine.py`](assistant_engine.py) 及 `HABIT_ALLOWED_HOURS` 分时段过滤逻辑<br>• **桌面悬浮窗与 OS 集成：** 实现 [`floating_widget.py`](floating_widget.py)、[`tray_manager.py`](tray_manager.py)、[`hotkey_manager.py`](hotkey_manager.py)、[`main_app.py`](main_app.py)（动态日期按钮、实时 `tk.Scale` 透明度条、可搜索 `[?]` 手册）<br>• **4 语言 i18n 架构：** 开发 [`i18n.py`](i18n.py)、[`i18n_habits.py`](i18n_habits.py)、[`i18n_personas.py`](i18n_personas.py) (`en`/`ko`/`ja`/`zh`) 全界面、跨语种识别、Excel 表适配与语言热切换，及 `.exe` 多语言元数据<br>• **移动端 Bot 与桥接服务：** 实现 [`telegram_bot.py`](telegram_bot.py)、[`discord_bot.py`](discord_bot.py)（纯标准库 RFC 6455 TLS WebSocket Gateway v10）、[`bot_commands.py`](bot_commands.py) 与 [`bot_bridge.py`](bot_bridge.py)<br>• **打包审计、沙盒演示与测试：** 完善 [`build_exe.py`](build_exe.py) + `verify_clean_exe_bundle`，录制隔离沙盒多语言演示（`assets/demo_*.gif/.mp4`），构建 25 项回归测试 [`test_regression_suite.py`](test_regression_suite.py) 与 7 步 E2E 套件 [`test_e2e_scenarios.py`](test_e2e_scenarios.py) 并编写多语言文档 |

---

## 🔍 关键工程经验总结

1. **真机实测胜过纸面假设：** Windows 网络防火墙类型、Discord 最新菜单路径、Android 客户端默认的 `https://` 与 JSON 格式要求，都是在真实设备和网络环境中实测后才彻底理顺的。
2. **Privacy by Design（隐私设计内建）：** 个人效率工具必须将 `.gitignore` 规则与编译期自动审计（`verify_clean_exe_bundle`）结合，从机制上杜绝个人习惯记录或密钥混入分发产物。
3. **人机协同的倍增效应：** 当人类精准把控使用手感、优先级与安全红线，AI 负责快速工程落地、多语言扩展与严格沙盒回归验证时，能够稳定产出高质量且可维护的开源级作品。
