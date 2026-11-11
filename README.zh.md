# 🌟 ALL-IN-ONE LIFE OS : 35项成功习惯与 AI 教练系统（Excel + 桌面悬浮窗）

> 🌐 **Languages:** [🇺🇸 English](README.md) · [🇰🇷 한국어](README.ko.md) · [🇯🇵 日本語](README.ja.md) · **🇨🇳 简体中文**

> **“卓越不是一种行为，而是一种习惯。” —— 亚里士多德**

---

## 🎬 功能演示视频（简体中文界面）

![Life OS 简体中文演示](assets/demo_zh.gif)

* 🎥 [MP4 高清视频 (`assets/demo_zh.mp4`)](assets/demo_zh.mp4) *(※ 演示视频略去了外部 Bot 令牌配置画面；Telegram · Discord · 局域网 Webhook 配置方法请参阅 [BOT_INTEGRATION_GUIDE.zh.md](BOT_INTEGRATION_GUIDE.zh.md)。)*

---

## 🎯 核心亮点

1. **7大人生领域 × 5项日常原则 = 35项科学成功习惯:**  
   涵盖商业效率、身体能量、心理思维、创造学习、人际领导力、财富理财与系统日常（完整文献来源见 [`REFERENCES.zh.md`](REFERENCES.zh.md)）。
2. **本地 SQLite 与 5表全自动公式 Excel 双向同步 (`Life_OS_Successful_Habits.xlsx`):**  
   `📊 仪表盘`、`🏆 成功习惯库`、`📅 每日追踪表`、`📈 每周复盘`、`🤖 AI助手日志` 实时联动，所有除法/均值公式均内置 `IFERROR` 防报错。
3. **轻量化桌面悬浮助手 (`LifeOS_Assistant_v2.exe`):**
   * **全局快捷键 (`Ctrl + Shift + H`)** 与系统托盘后台常驻
   * **实时横向透明度滑块 (`30%–100%`)**: 拖动滑块即可实时预览窗口半透明效果，未保存关闭自动还原
   * **分时段智能提醒 (`HABIT_ALLOWED_HOURS`)**: 晨间阳光、上午核心决策、凌晨写作、睡前戒屏、晚间关机等时间限定习惯仅在对应时段弹出，其余习惯保持随机推荐
   * **4位导师人格切換**: 安德鲁·休伯曼 / 沃伦·巴菲特 / 埃隆·马斯克 & Grok / 马可·奥勒留
   * **动态日期导航 (`◀ 昨天/前一天` · `今天` · `明天 ▶/后一天 ▶`)**: 切换到非当天日期时自动显示「前一天 / 后一天」，避免歧义
   * **4国语言自动检测与热切换 (`ko`/`en`/`ja`/`zh`)**: 支持在设置中实时切换 UI、托盘、数据库与 Excel 表格语言

---

## 🚀 快速开始

### 方式 A：Windows 免安装独立程序 (`.exe`)
从 GitHub **[Releases](https://github.com/hobby-programmer-5000/life-os-excel-ai/releases)** 下载 `LifeOS_Assistant_v2.exe` 直接双击运行（无需安装 Python，首次运行在同目录自动初始化本地数据库和 Excel）。

> **Windows SmartScreen 与哈希校验说明：** 本程序为无付费商业签名的个人开源软件，首次运行时可能会弹出 *"Windows 已保护你的电脑"* 提示（点击 `更多信息` → `仍要运行` 即可）。您可通过发布页公布的 SHA-256 校验和（`certutil -hashfile LifeOS_Assistant_v2.exe SHA256`）核对文件完整性，或使用 [`build_exe.py`](build_exe.py) 从源码自行编译。

### 方式 B：从源码运行（Windows / macOS / Linux）
```bash
git clone <repository-url>
cd life-os-excel-ai
pip install -r requirements.txt

python main_app.py
# 命令行自然语言打卡示例:
python ai_secretary.py --checkin "早上晒太阳15分钟，完成90分钟深度工作！"
```

---

## 🔗 文档与隐私保护

* [🤖 Telegram / Discord / 手机快捷指令联动指南 (`BOT_INTEGRATION_GUIDE.zh.md`)](BOT_INTEGRATION_GUIDE.zh.md) *(含外部平台更新导致设置界面变化的提示说明)*
* [🛠️ 项目演进、开发历程与分工 (`DEVELOPMENT_HISTORY.zh.md`)](DEVELOPMENT_HISTORY.zh.md)
* [📚 科学与 UI/HCI 设计参考文献 (`REFERENCES.zh.md`)](REFERENCES.zh.md) · [📐 Harness² 架构规范 (`HARNESS_SPEC.zh.md`)](HARNESS_SPEC.zh.md)
* [📜 第三方可商用免费图标素材声明 (`THIRD-PARTY-NOTICES.md`)](THIRD-PARTY-NOTICES.md) — 收录 **Lucide Icons**（`ISC License` / Feather `MIT License`）全部 29 枚开源矢量素材与授权全文
* 个人数据文件（`*.db`, `*.xlsx`, `.env`, `*.spec`, `build/`, `dist/`）均已在 `.gitignore` 中严格屏蔽，且 `build_exe.py` 内置自动打包内容审计 (`verify_clean_exe_bundle`)。

---

## 👥 共同贡献者 (Contributors)

* **[hobby-programmer-5000](https://github.com/hobby-programmer-5000)** — *Product Owner · 领域架构 · UX/UI 总监 · 真机测试*: 策划7大领域×35习惯体系与Excel本地数据主权理念，决定移除付费外部 LLM API 坚持零门槛本地 NLP，主导**现代极简（Anti-Slop）UI 改造**、统一增长曲线应用图标选型及免费开源图标/文献引用规范，主抓桌面与真机体验（动态日期按钮、分时段智能提醒、实时横滑透明度条、Bot卡片排序）及零隐私/零令牌安全边界。
* **[Gemini (Antigravity)](https://github.com/gemini-code-assist)** — *AI 结对编程工程师 · 全栈、UI 与自动化测试*: 构建 [`ui_theme.py`](ui_theme.py)（60-30-10 深色令牌 + 纯 Python SVG 光栅器）与 29 枚 Lucide 图标集成，重塑悬浮窗极简 UI、Python核心引擎、SQLite WAL三向同步、4语言i18n、Telegram/Discord/局域网Webhook桥接、PyInstaller隐私审计、自动化回归/E2E套件、沙盒演示视频及 [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) 与多语言设计文献。

---

## 📄 开源许可证与素材致谢 (License & Credits)

本项目遵循 [MIT License](LICENSE) 开源发布。桌面界面与图标基于 **Lucide Icons** ([lucide.dev](https://lucide.dev), `ISC License` 含 Feather `MIT License`) 构建，完整授权见 [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)。
