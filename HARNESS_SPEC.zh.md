# 📐 ALL-IN-ONE LIFE OS : Harness² 应用工程架构规范

> 🌐 **Languages:** [🇺🇸 English](HARNESS_SPEC.md) · [🇰🇷 한국어](HARNESS_SPEC.ko.md) · [🇯🇵 日本語](HARNESS_SPEC.ja.md) · **🇨🇳 简体中文**

> **参考框架：** [Google Research Harness² (Recursive Agent & Application Harnessing)](https://github.com/google-research/harness2)  
> **目标：** 建立超轻量 Windows 系统托盘与桌面悬浮窗 Life OS 应用的架构不变量、组件契约接口与 `Propose → Probe → Compose` 验证闭环。

---

## 1. Google Research Harness² 哲学在桌面应用中的落地

Google Research **Harness²** 主张将包裹核心模型的 **执行框架（Execution Harness：记忆、工具、护栏、界面、脚本）** 视为模块化可演进组件，而非孤立调优模型本身。

本项目将其精准映射为桌面应用架构：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HARNESS² SYSTEM MODEL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [Fixed Core] ─── 35项成功习惯库 ＆ 100% 离线多语言本地 NLP 引擎          │
│         ▲                                                                   │
│         │ (Contract / Data Invariant)                                       │
│         ▼                                                                   │
│   [Execution Harness] ──────────────────────────────────────────────────┐   │
│   │ 1. Storage Harness : SQLite WAL（跨日期漫游）+ 5表 Excel 双向同步   │   │
│   │ 2. View Harness    : 桌面悬浮窗（置顶、实时透明度滑块）             │   │
│   │ 3. OS Harness      : 系统托盘 + Windows 开机自启注册表安全控制      │   │
│   │ 4. Agent Harness   : 自然语言打卡 · 分时段提醒 · 手机 Bot / Webhook │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   [Propose - Probe - Compose Cycle]                                         │
│   • Propose : 明确模块规格、SQLite 表结构及 UI 状态机契约                   │
│   • Probe   : 独立实测 Windows API、Tkinter 渲染回路与数据库并发锁定        │
│   • Compose : 将验证通过的模块集成进 main_app.py、单文件 EXE 与回归测试集   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 核心设计原则 (Core Principles)

### 原则 1：Zero-Friction Visibility（零摩擦轻量常驻）
- 无需每次打开大型办公软件，通过系统托盘与桌面悬浮窗在 1 秒内完成查看与打卡。
- **轻量化占用：** 基于 Python 内置 Tkinter，空闲驻留内存与 CPU 开销极低。

### 原则 2：Multi-Temporal Traversal（时间轴自由漫游）
- 突破传统 Excel 按当天或单周限制的局限，支持补录过去日期与提前规划未来目标。
- **动态相对日期按键：** 在“今天”显示 **`◀ 昨天 / 今天 / 明天 ▶`**；切换至历史或未来日期后自动切为 **`◀ 前一天 / 今天 / 后一天 ▶`**。

### 原则 3：Dual-Sync Architecture（SQLite + Excel 双向互补）
- **高速本地引擎：** `life_os.db`（WAL 模式）负责即时查询、多客户端并发读写与 UI 秒级刷新。
- **用户完全拥有工作簿：** 与 4 语言 5 张工作表的 `Life_OS_Successful_Habits.xlsx` 自动双向同步并保留全部 `IFERROR` 公式。

### 原则 4：Non-Invasive OS Integration（无侵入系统集成）
- 设置窗一键勾选切换 Windows 开机启动（安全写入 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`）。
- 关闭主窗默认最小化到系统托盘，保持后台提醒与 Bot 监听不中断。

### 原则 5：Proactive Assistant Interaction（分时段智能推送与三态状态机）
- 结合 `HABIT_ALLOWED_HOURS` 时段适宜性过滤机制，在恰当时间段主动弹出提醒并避免凌晨误推睡前习惯。
- **三态快速响应：** `[✅ 完成]` / `[🚀 立即执行!]` / `[⏸️ 稍后处理]`
- **全局快捷键 (`Ctrl + Shift + H`)：** 基于 Windows `RegisterHotKey`，在任意全屏或工作界面一键唤出/隐藏。
- **4 大导师人格：** 💼 沃伦·巴菲特 / ⚡ 安德鲁·休伯曼 / 🚀 埃隆·马斯克 & Grok / 🧠 马可·奥勒留。
- **单文件打包与隐私审计 (`build_exe.py`)：** 编译独立运行的 `LifeOS_Assistant_v2.exe` 并自动执行 `verify_clean_exe_bundle` 二进制脱敏检查。

---

## 3. 组件接口契约 (Component Contracts)

### [Component 1] View Harness (`floating_widget.py`, `tray_manager.py`)
- 显示/隐藏切换、窗口始终置顶、**实时横向透明度滑块 (`30%–100%` / `0.30–1.00`，默认 `0.92`，未保存关闭自动还原)**、展示条目数 (`1–35`)、`[🎲 换一批]` / `[📌 固定]`、全部 35 项滚动模式、底部自然语言输入框及可搜索 `[?]` 关键词弹窗。

### [Component 2] Storage Harness (`database.py` -> `life_os.db`)
```sql
CREATE TABLE IF NOT EXISTS daily_checks (
    check_date TEXT NOT NULL,      -- 'YYYY-MM-DD'
    habit_id INTEGER NOT NULL,     -- 1 ~ 35
    status INTEGER DEFAULT 1,
    memo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (check_date, habit_id)
);

CREATE TABLE IF NOT EXISTS daily_logs (
    log_date TEXT PRIMARY KEY,
    summary_text TEXT,
    ai_coaching TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

### [Component 3 & 4] OS Harness 与 Excel 双向同步器 (`tray_manager.py`, `hotkey_manager.py`, `generate_excel.py`, `database.py`)
- 跨语种 Sheet 自动匹配（`_find_sheet`）、`Ctrl+Shift+H` 热键、Windows 注册表开机启停控制。

---

## 4. Propose - Probe - Compose 验证闭环

1. **Step 1: Propose（架构提案）** — 本规格书明确数据结构、UI 状态机与系统契约。
2. **Step 2: Probe（独立沙盒探针）** — 通过 [`probe_harness.py`](probe_harness.py) 与隔离沙盒分别验证跨天查询、注册表安全启停、Excel 公式保留与 Tkinter 布局渲染。
3. **Step 3: Compose（成品集成与全量测试）** — 在 [`main_app.py`](main_app.py) 完成组装，由 [`build_exe.py`](build_exe.py) 输出 `LifeOS_Assistant_v2.exe`，并通过 [`test_regression_suite.py`](test_regression_suite.py)（25 项）与 [`test_e2e_scenarios.py`](test_e2e_scenarios.py)（7 步）持续回归保障。

---

## 5. 默认配置参数表 (Config Matrix)

| 配置项 | 字段名 | 默认值 | 说明 |
|:---|:---:|:---:|:---|
| **开机自启** | `autostart_enabled` | `False` | 是否随 Windows 启动自动运行 |
| **关闭行为** | `close_to_tray` | `True` | 点击关闭按钮时最小化至系统托盘 |
| **窗口置顶** | `always_on_top` | `True` | 悬浮窗始终保持在其他窗口上方 |
| **窗口透明度** | `opacity` | `0.92` | 实时横向滑块调节范围（`0.30–1.00`） |
| **自动同步** | `auto_sync_excel` | `True` | 每次打卡后自动后台同步写入 Excel |
