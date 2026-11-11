# 📐 ALL-IN-ONE LIFE OS : アプリケーション構築のための Harness² 設計仕様書

> 🌐 **Languages:** [🇺🇸 English](HARNESS_SPEC.md) · [🇰🇷 한국어](HARNESS_SPEC.ko.md) · **🇯🇵 日本語** · [🇨🇳 简体中文](HARNESS_SPEC.zh.md)

> **参照フレームワーク:** [Google Research Harness² (Recursive Agent & Application Harnessing)](https://github.com/google-research/harness2)  
> **目的:** Windows システムトレイおよびフローティングウィジェット型超軽量 Life OS アプリのアーキテクチャ規約・コンポーネント契約・`Propose → Probe → Compose` 検証ループの定義

---

## 1. Google Research Harness² のデスクトップソフトウェア適用

Google Research の **Harness²** は、モデル本体ではなく周囲の **実行環境（Execution Harness：メモリ・ツール・ガードレール・UI・スクリプト）** をモジュール化されたデータとして扱い適応・最適化します。

本プロジェクトではこの分離原則をデスクトップアプリ設計へ次のようにマッピングしています：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HARNESS² SYSTEM MODEL                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [Fixed Core] ─── 35大成功習慣マスターDB ＆ オフライン多言語 NLP エンジン  │
│         ▲                                                                   │
│         │ (Contract / Data Invariant)                                       │
│         ▼                                                                   │
│   [Execution Harness] ──────────────────────────────────────────────────┐   │
│   │ 1. Storage Harness : SQLite WAL (日付横断) + 5シート Excel 双方向同期 │   │
│   │ 2. View Harness    : 浮動ウィジェット (最前面固定, 透過スライダー)   │   │
│   │ 3. OS Harness      : システムトレイ + Windows スタートアップ制御     │   │
│   │ 4. Agent Harness   : 自然文記録・時間帯ナッジ・モバイル Bot / Webhook│   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   [Propose - Probe - Compose Cycle]                                         │
│   • Propose : モジュール仕様・DBスキーマ・UIステートマシン契約の策定          │
│   • Probe   : OS API・GUIイベントループ・DBロックの独立実測検証              │
│   • Compose : 検証済み部品を main_app.py・単一EXE・自動テスト群へ統合       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. コア原則 (Core Principles)

### 原則 1: Zero-Friction Visibility (超軽量・常時可視性)
- 大規模アプリを毎回立ち上げることなく、システムトレイとデスクトップ浮動ウィジェットから 1秒以内に習慣を確認・記録可能。
- **軽量構成:** Python 標準 Tkinter 採用により常駐リソース消費を抑制。

### 原則 2: Multi-Temporal Traversal (時間軸の自由移動)
- 単日・週間固定のExcel制約を超え、過去日の遡及記録や未来日の事前計画を SQLite WAL (`life_os.db`) で永続管理。
- **動的日付ナビゲーション:** 今日を見ている時は **`◀ 昨日 / 今日 / 明日 ▶`**、別日では **`◀ 前日 / 今日 / 翌日 ▶`** に切り替え。

### 原則 3: Dual-Sync Architecture (SQLite + Excel 相互補完)
- **高速ローカルエンジン:** 日付横断検索やモバイル Bot との同時アクセスを `life_os.db`（WAL モード）が担当。
- **ユーザー所有ワークブック:** 4言語対応 5シート `Life_OS_Successful_Habits.xlsx` と数式（`IFERROR`）を保持したまま自動双方向同期。

### 原則 4: Non-Invasive OS Integration (非侵襲的な OS 統合)
- 設定のチェックボックス1つで Windows 自動起動（`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`）を安全にトグル。
- ウィンドウを閉じてもバックグラウンドトレイへ最小化し、リマインダーや Bot 受信を継続。

### 原則 5: Proactive Assistant Interaction (時間帯別ナッジ & 3状態ステートマシン)
- `HABIT_ALLOWED_HOURS` により深夜・日中の不適切な就寝習慣提案を抑止しつつ、時間軸に合う習慣を能動的に質問（Nudge）。
- **3状態クイック応答:** `[✅ 完了]` / `[🚀 今すぐやる!]` / `[⏸️ 後で]`
- **グローバルホットキー (`Ctrl + Shift + H`):** OS 標準 `RegisterHotKey` により作業中でも即時表示/非表示をトグル。
- **4大ロールモデルペルソナ:** 💼 ウォーレン・バフェット / ⚡ アンドリュー・フーバーマン / 🚀 イーロン・マスク & Grok / 🧠 マルクス・アウレリウス。
- **スタンドアロンビルド (`build_exe.py`):** `LifeOS_Assistant_v2.exe` 単一ファイル生成 ＋ アーカイブ自動プライバシー監査 (`verify_clean_exe_bundle`)。

---

## 3. コンポーネント契約 (Component Contracts)

### [Component 1] View Harness (`floating_widget.py`, `tray_manager.py`)
- 表示/非表示トグル、最前面固定、**リアルタイム横透明度スライダー (`30%〜100%` / `0.30〜1.00`, デフォルト `0.92`, 未保存時は復元)**、表示件数 (`1〜35`)・`[🎲 シャッフル]`・`[📌 ピン]`・全件スクロール、1行自然文入力欄および検索可能な `[?]` ガイド。

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

### [Component 3 & 4] OS Harness & Excel Dual Synchronizer (`tray_manager.py`, `hotkey_manager.py`, `generate_excel.py`, `database.py`)
- 4言語シート解決（`_find_sheet`）、`Ctrl+Shift+H` ホットキー、Windows レジストリ自動起動管理。

---

## 4. Propose - Probe - Compose 検証サイクル

1. **Step 1: Propose (設計契約策定)** — 本仕様書によるスキーマ・UI・OS契約の明文化。
2. **Step 2: Probe (モジュール個別プローブ)** — [`probe_harness.py`](probe_harness.py) および隔離テストにより DB 時間移動・レジストリ安全性・Excel 同期・GUI 描画を独立検証。
3. **Step 3: Compose (統合組み立てと継続テスト)** — [`main_app.py`](main_app.py) へ統合し [`build_exe.py`](build_exe.py) で EXE 化、[`test_regression_suite.py`](test_regression_suite.py)（25件）と [`test_e2e_scenarios.py`](test_e2e_scenarios.py)（7段階）で全体検証。

---

## 5. オプション設定マトリクス (Config Matrix)

| 項目 | 設定キー | デフォルト | 説明 |
|:---|:---:|:---:|:---|
| **自動起動** | `autostart_enabled` | `False` | Windows ログオン時の自動起動 |
| **終了動作** | `close_to_tray` | `True` | `×` ボタンで終了せずトレイへ格納 |
| **最前面固定** | `always_on_top` | `True` | 他ウィンドウの上へ常に表示 |
| **透過度** | `opacity` | `0.92` | リアルタイムスライダー半透明調整 (`0.30〜1.00`) |
| **Excel 自動同期** | `auto_sync_excel` | `True` | チェック操作時にバックグラウンド同期 |
