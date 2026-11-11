# 🛠️ ALL-IN-ONE LIFE OS : 開発ヒストリー（Development History）

> 🌐 **Languages:** [🇺🇸 English](DEVELOPMENT_HISTORY.md) · [🇰🇷 한국어](DEVELOPMENT_HISTORY.ko.md) · **🇯🇵 日本語** · [🇨🇳 简体中文](DEVELOPMENT_HISTORY.zh.md)

本書は、**「世界的成功者の習慣を1つの Excel に統合し、AI アシスタントと共に日々の実践を管理する」**という構想から出発し、デスクトップ常駐ウィジェット・多言語対応・オープンなモバイル Bot エコシステムへと段階的に磨き上げてきた共同開発の記録です。

---

## 📌 タイムラインとフェーズ別進化

### Phase 1. オールインワン成功習慣 Excel ＆ AI コーチコア構築
* **背景:** 書籍・論文・講演に分散した重要ルーティンを **7ライフ領域 × 5大習慣 ＝ 35大成功習慣** として体系化し、有料の閉鎖サービスではなくユーザー自身が所有・分析できる標準 Excel (`.xlsx`) を中核に据えました。
* **実装内容:**
  * [`generate_excel.py`](generate_excel.py): 5シート構成（`📊 ダッシュボード`・`🏆 成功習慣DB`・`📅 日次トラッカー`・`📈 週次レビュー`・`🤖 AI連携ログ`）を自動生成し、約100箇所の集計数式に `IFERROR` を適用して初期状態での `#DIV/0!` エラーを防止しました。
  * [`REFERENCES.ja.md`](REFERENCES.ja.md): 35習慣それぞれの一次文献・出典・科学的メカニズムを整理しました。
  * [`ai_secretary.py`](ai_secretary.py): 自然文から複数習慣を自動検出してチェックし、ペルソナ別コーチングを生成する 100% オフライン 4言語ローカル NLP エンジン (`LocalHabitNLP`) を構築しました。

---

### Phase 2. Google Research Harness² 応用 ＆ Windows 常駐トレイアプリ化
* **背景:** 「毎日 Excel を手動で開く摩擦をなくし、デスクトップに浮遊して話しかけてくれる軽量パートナーが欲しい」という要望を受け、Google Research **Harness²** の思想を [`HARNESS_SPEC.ja.md`](HARNESS_SPEC.ja.md) のソフトウェア規格へ落とし込みました。
* **実装内容:**
  * **Storage Harness ([`database.py`](database.py)):** SQLite（`life_os.db`・WAL モード）を導入し、昨日・過去・未来（Date Traversal）を横断するタイムライン記録と、SQLite・Excel・UI 間の **3-Way 双方向同期** を実現しました。
  * **Assistant Engine ([`assistant_engine.py`](assistant_engine.py)):** 4人のロールモデル・ペルソナ（アンドリュー・フーバーマン、ウォーレン・バフェット、イーロン・マスク＆Grok、マルクス・アウレリウス）、スマートナッジ、`[✅ 完了]`・`[🚀 今すぐやる!]`・`[⏸️ 後で]` の3状態ステートマシンを実装しました。
  * **Desktop UI & OS Harness ([`floating_widget.py`](floating_widget.py), [`tray_manager.py`](tray_manager.py), [`hotkey_manager.py`](hotkey_manager.py), [`main_app.py`](main_app.py), [`build_exe.py`](build_exe.py)):** 半透明フローティングウィジェット、システムトレイ、`Ctrl+Shift+H` グローバルホットキー、チャイム＆Windows トースト通知、Python 不要の単一 `.exe`（`LifeOS_Assistant_v2.exe`）パッケージングを完成させました。

---

### Phase 3. 実利用フィードバックによる UX 洗練＆不具合修正
実際のデスクトップ運用から見つかった細かな使い勝手・境界条件を順次改善しました。
* **ウィジェット表示カスタマイズ＆入力欄の見切れ修正:**
  * 表示習慣数を `1〜35個` で設定でき、`[🎲 シャッフル]` / `[📌 ピン]` および **全35項目スクロールモード** を追加しました。
  * 長文コーチング表示時に下部の自然文入力バーが押し出されて隠れる問題を、Tkinter `side=tk.BOTTOM` 優先パッキングで解決しました。
* **誤判定ガード＆検索可能キーワードポップアップ:**
  * `"dk"` のような無関係な語が誤ってチェックされる問題に対し、スペース正規化と語単位境界ガードを強化し、`[?]` ボタンをライブ検索可能な **35大習慣キーワードガイド** へ刷新しました。
* **テストサンドボックス完全隔離:**
  * `LIFE_OS_DATA_DIR` と `TemporaryDirectory()` による環境分離を徹底し、実運用 DB/Excel を一切汚さず検証できるよう整備、`wb.close()` のファイルロック漏れも解消しました。
* **直感的な日付・時間帯・リアルタイム透明度 UX 改善:**
  * **動的日付ボタンラベル:** 今日（`diff == 0`）を見ている時は **`◀ 昨日` / `今日` / `明日 ▶`**、別日へ移動すると **`◀ 前日` / `今日` / `翌日 ▶`** へ自動切替し、日付文脈の誤解を解消しました。
  * **時間帯別ナッジフィルタ (`HABIT_ALLOWED_HOURS`):** 未明（`00〜04時`）に夜間・就寝習慣が誤提案される条件バグを修正し、朝光・午前意思決定・早朝執筆・仕事終了儀式・就寝前デジタル断ち/感謝日記など時刻依存の習慣を適切な時間帯のみへ限定しつつ、汎用習慣はランダム性を維持しました。
  * **リアルタイム横透明度スライダー:** 数値直接入力（`0.5〜1.0`）を **`30%〜100%` の横型 `tk.Scale` スライダー** へ置き換え、ドラッグ中に透過度を即時プレビューし、未保存で閉じた（`✕`）場合は元の透過度へ自動復元するようにしました。

---

### Phase 4. グローバル4言語統合アーキテクチャ (`en` / `ko` / `ja` / `zh`)
* **背景:** OS のロケールに合わせて世界中のユーザーがすぐに使える完全多言語化を実施しました。
* **実装内容:**
  * [`i18n.py`](i18n.py), [`i18n_habits.py`](i18n_habits.py), [`i18n_personas.py`](i18n_personas.py): 4言語 UI、クロス言語35習慣キーワード認識、4ペルソナ、4言語 Excel ワークブック生成およびシート互換解決（`_find_sheet`）、設定画面からの UI・トレイ即時言語切替、[`build_exe.py`](build_exe.py) の言語別 Windows PE `VSVersionInfo` メタデータまで統合しました。

---

### Phase 5. オープンモバイル Bot・LAN Webhook 連携 ＆ セキュリティ検証ガード
* **設計方針の意思決定:** 無料ユーザーにも公式 Bot API が開かれているオープン生態系（**Telegram**・**Discord**・**LAN HTTP Webhook**）へ注力し、規約面・保守面でリスクのある非公式・閉鎖型手法は除外しました。
* **実装および実機検証:**
  * **Telegram Bot ([`telegram_bot.py`](telegram_bot.py)):** 追加ライブラリ不要の HTTP Long-Polling 受信と `@BotFather` なりすまし防止警告 UI を実装。
  * **Discord 内蔵 Bot ([`discord_bot.py`](discord_bot.py), [`bot_commands.py`](bot_commands.py)):** 標準ライブラリのみで RFC 6455 TLS WebSocket（Gateway v10）＋ REST API を実装。実機確認した最新ポータル手順（`⚙️ → </> 開発者 → 開発者モード`）、`Clyde` DM ブロック対処、`専用チャンネルID` 運用を文書化しました。
  * **Android ＆ Wi-Fi 補助 iPhone Webhook ([`bot_bridge.py`](bot_bridge.py)):** Android（`HTTP Request Shortcuts`）と Wi-Fi 接続補助 iPhone（`ショートカット`）の実機検証で判明した **Windows `Public`→`Private` ファイアウォール設定**、**`https://` ではなく `http://`**（TLS ヘッダーエラー回避）、**`Parameters` ではなく `Custom Text` (`application/json`)** と半角直線引用符の注意点をガイドへ反映しました。
  * **ゼロコスト・ローカル NLP 強化・3カード UI・成長グラフアイコン統一:** 4言語の日常入力文テストを経て `LocalHabitNLP` の記号正規化と会話表現パターンを強化し、外部有料 LLM API 連携を撤廃（`Telegram → Discord → ローカル Webhook`）するとともに、[`app_icon.py`](app_icon.py) で EXE・システムトレイ・全ダイアログを統一アイコン化しました。
  * **ビルド ＆ Git プライバシー保護 ([`.gitignore`](.gitignore), [`build_exe.py`](build_exe.py)):** 個人用 `*.db`・`*.xlsx`・`.env`・`*.spec`・`build/`・`dist/` を Git 追跡対象外とし、`.exe` 生成後に秘密情報が含まれていないかを自動検証（`verify_clean_exe_bundle`）する仕組みを追加しました。

---

### Phase 6. モダンミニマル「Anti-Slop」UI 刷新・商用無料ストック・デザイン文献体系化
* **デザインの刷新方針:** 多色ネオン枠線（`#38BDF8` / `#818CF8` / `#F59E0B`）・ボタン内の絵文字多用・未装飾フォームといった「AI slop」感を払拭するため、Product Owner の指示に基づき検証済みの HCI・デザイン一次文献（[`REFERENCES.ja.md`](REFERENCES.ja.md): Dieter Rams、Edward Tufte、Weiser & Brown、John Sweller、Josef Müller-Brockmann、Nielsen Norman Group）に沿った **Modern Minimal UI** へ全面刷新しました。
* **実装および画面監査:**
  * **60-30-10 オブシディアン＆ジンク体系 ＋ 純粋 Python SVG ラスタライザ ([`ui_theme.py`](ui_theme.py)):** `#09090B` / `#111216` / `#18181B` の中立ダーク階層、`1px` `#27272A` ヘアライン、ダーク入力欄＆ `ttk` スタイル、単一主要 CTA（`#F4F4F5`/`#09090B`）、完了・オンライン専用エメラルド（`#10B981`/`#059669`）、および滑らかなベクターアイコン描画エンジンを実装しました。
  * **商用利用可能フリー素材とライセンス明記 ([`assets/icons/lucide/`](assets/icons/lucide/), [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)):** `ISC License`（一部 Feather `MIT License`）の公式 **Lucide SVG アイコン 29種** をバンドルし、ウィジェットや各設定ダイアログの絵文字を整理（[`floating_widget.py`](floating_widget.py), [`i18n.py`](i18n.py), [`assistant_engine.py`](assistant_engine.py)）するとともに、統一アプリアイコン（[`app_icon.py`](app_icon.py)）とクレジット表記を完備しました。
  * **全画面レンダリング検証:** 4言語のメイン画面・設定・Bot 3カード・35習慣一覧・検索ガイドを実機キャプチャ検証し、長文ロケール（`en`/`ja`）ヘッダーの閉じるボタン見切れや行末クリップを修正しました。

---

## 👥 共同貢献者 ＆ 役割分担（Contributors & Role Division）

本プロジェクトは、人間のプロダクトオーナーと AI ペアプログラマーが明確に役割を分担し、Human-in-the-loop の反復改善で構築しました。

| 貢献者 | 役割（Role） | 主な担当領域（Owned Contributions） |
| :--- | :--- | :--- |
| **[hobby-programmer-5000](https://github.com/hobby-programmer-5000)** | **Product Owner · Domain Architect · UX/UI Director · Real-Device QA** | • **ビジョン＆領域設計:** 7領域×35習慣フレームワーク選定、ユーザー所有型 Excel＋常駐ウィジェット構想の策定<br>• **Harness² ＆ ゼロコストローカル方針:** Harness² 応用、4大ペルソナ、外部有料 LLM API 撤廃（完全ローカル NLP）の意思決定<br>• **モダンミニマル UI（「Anti-Slop」）＆ 素材・文献基準:** 多色装飾を排したミニマル UI 刷新、成長グラフアイコン選定、商用無料ベクター素材の採用と [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)・デザイン文献出典（[`REFERENCES.ja.md`](REFERENCES.ja.md)）の記録を指示<br>• **実利用 UX 批評 ＆ 実機 QA:** 動的日付ボタン、深夜帯ナッジ誤推薦の発見、リアルタイム透明度スライダー（`30%〜100%`）、Android（`HTTP Request Shortcuts`）・Wi-Fi iPhone 実機検証および個人情報・トークン非混入基準の確定<br>• **リリース品質・多言語化:** MIT ライセンス採択、4言語デモ動画と多言語ドキュメント網羅を指示 |
| **[Gemini (Antigravity)](https://github.com/gemini-code-assist)** | **AI Pair Programmer · Full-Stack, UI & QA Engineer** | • **モダンミニマルテーマ ＆ SVG 描画基盤:** [`ui_theme.py`](ui_theme.py)（60-30-10 トークン＋純粋 Python SVG ラスタライザ）実装、29種 Lucide SVG 統合、[`app_icon.py`](app_icon.py)・[`floating_widget.py`](floating_widget.py) 全面 UI 刷新、[`i18n.py`](i18n.py)・[`assistant_engine.py`](assistant_engine.py) 整理、[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) および UI 参考文献執筆<br>• **コア・ストレージ実装:** [`generate_excel.py`](generate_excel.py)、[`database.py`](database.py)（SQLite WAL・3-Way 同期）、[`ai_secretary.py`](ai_secretary.py)（`LocalHabitNLP`）、[`assistant_engine.py`](assistant_engine.py)、時間帯フィルタ `HABIT_ALLOWED_HOURS` 実装<br>• **デスクトップ UI ＆ OS 統合:** [`floating_widget.py`](floating_widget.py)、[`tray_manager.py`](tray_manager.py)、[`hotkey_manager.py`](hotkey_manager.py)、[`main_app.py`](main_app.py) 実装<br>• **4言語 i18n 基盤:** [`i18n.py`](i18n.py)、[`i18n_habits.py`](i18n_habits.py)、[`i18n_personas.py`](i18n_personas.py) (`en`/`ko`/`ja`/`zh`)、シート互換・ライブ言語切替・`.exe` メタデータ統合<br>• **Bot・パッケージング・検証:** [`telegram_bot.py`](telegram_bot.py)、[`discord_bot.py`](discord_bot.py)（RFC 6455 WebSocket Gateway v10）、[`bot_commands.py`](bot_commands.py)、[`bot_bridge.py`](bot_bridge.py)、[`build_exe.py`](build_exe.py) + `verify_clean_exe_bundle`、サンドボックスデモ動画（`assets/demo_*.gif/.mp4`）、[`test_regression_suite.py`](test_regression_suite.py) ＆ [`test_e2e_scenarios.py`](test_e2e_scenarios.py) 構築 |

---

## 🔍 開発を通じて得たエンジニアリングの学び

1. **実機検証の重要性:** 仕様書上の想定だけでなく、実際の Windows Wi-Fi プロファイル・Discord 最新画面・Android アプリの TLS/JSON 挙動を実機で検証することで初めて信頼できるガイドが完成しました。
2. **Privacy by Design:** ローカル個人データツールでは `.gitignore` とビルド後バンドル監査（`verify_clean_exe_bundle`）を自動化することで、個人情報・トークン漏洩を構造的に防げます。
3. **人間と AI の協働相乗効果:** 人間が実生活での使い勝手・優先順位・セキュリティ境界を見極め、AI が実装・多言語展開・サンドボックス検証を高速に反復することで、高い品質と開発速度を両立できました。
