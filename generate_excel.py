"""
=============================================================================
📊 ALL-IN-ONE LIFE OS : Localized Excel Workbook Generator (4 Languages)
=============================================================================
Generates the 5-sheet Life OS workbook (Dashboard, Habit DB, Daily Tracker,
Weekly Review, AI Assistant Log) in Korean (ko), English (en), Japanese (ja),
or Simplified Chinese (zh), with live cross-sheet formulas intact.
=============================================================================
"""

import argparse
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from i18n import resolve_language, SHEET_TITLES, get_excel_font
from i18n_habits import get_habits_catalog, get_domain_rows


EXCEL_UI = {
    "ko": {
        "dash_title": "🌟 ALL-IN-ONE LIFE OS : 성공한 사람들의 습관 & 실행 대시보드",
        "dash_sub": "워런 버핏, 일론 머스크, 앤드루 후버만 등 글로벌 거인들의 7대 원칙 기반 일일/주간 라이프 시스템 (AI 비서 연동형)",
        "kpi_done_lbl": "오늘 완료 습관",
        "kpi_done_unit": "개",
        "kpi_today_rate": "오늘 달성률",
        "kpi_week_rate": "주간 평균 달성률",
        "kpi_ai_lbl": "AI 비서 코칭 상태",
        "kpi_ai_val": "정상 연결 (실시간 동기화 중)",
        "sec_top5": "📌 오늘의 핵심 집중 5대 습관 (워런 버핏의 5/25 법칙)",
        "top5_headers": ["분야", "대표 인물", "습관 프로토콜", "오늘 실천 여부", "자가 피드백 / 메모"],
        "status_done": "✅ 완료",
        "status_todo": "⏳ 미완료",
        "top5_notes": ["", "", "", "", ""],
        "sec_ai": "🤖 AI 비서 데일리 피드백 & 코칭 브리핑 (AI Secretary)",
        "ai_welcome": (
            "💡 [AI 비서 시작 가이드]\n\n"
            "\"환영합니다! 아침 15분 햇빛 노출과 워런 버핏의 5/25 최우선 과제부터 하루를 시작해 보세요.\n"
            "데스크톱 위젯, CLI, Telegram, Discord, 로컬 웹훅 어디서든 자연어로 오늘 실천한 일과를 남기면 SQLite와 엑셀이 실시간 동기화됩니다.\""
        ),
        "sec_domains": "📊 7대 라이프 영역별 주간 누적 달성률",
        "dom_headers": ["영역 코드", "라이프 영역", "핵심 구루(Guru)", "습관 수", "주간 달성률", "달성 상태 평가"],
        "tier_excellent": "🟢 최우수",
        "tier_good": "🟡 양호",
        "tier_progress": "🔵 진행중",
        "tier_idle": "⚪ 대기",
        "db_banner": "🏆 성공한 사람들의 7대 분야별 핵심 습관 & 실행 프로토콜 마스터 DB",
        "db_headers": ["No", "라이프 영역", "대표 롤모델", "습관 명칭", "핵심 철학 및 원리", "구체적 실행 프로토콜 (Checklist)", "권장 주기", "실천 난이도"],
        "track_banner": "📅 35대 습관 데일리 실천 트래커 (완료 시 숫자 1 또는 체크 입력)",
        "track_headers": ["No", "대표 습관 명칭", "월 (Day 1)", "화 (Day 2)", "수 (Day 3)", "목 (Day 4)", "금 (Day 5)", "토 (Day 6)", "일 (Day 7)", "주간 달성률", "스트릭"],
        "streak_high": "🔥 주 4회+",
        "streak_mid": "🌱 진행중",
        "streak_idle": "대기",
        "track_sum_lbl": "📊 일일 총 달성률 (35개 기준)",
        "track_week_tot": "주간 종합",
        "rev_banner": "📈 주간 회고 프레임워크 (KPT + 레이 달리오 원칙 회고)",
        "rev_sections": [
            ("B4:H4", "🎯 이번 주 핵심 성취 및 Keep (지속해야 할 긍정적 습관)", ""),
            ("B8:H8", "⚠️ 문제점 및 개선 과제 Problem (장애물 및 실패 분석)", ""),
            ("B12:H12", "🚀 다음 주 실행 실험 Try (새롭게 도입할 마이크로 액션)", ""),
            ("B16:H16", "🤖 AI 비서의 주간 종합 평가 & 피드백 (AI Weekly Report)", ""),
        ],
        "log_banner": "🤖 AI 비서 연동 및 대화형 체크인 기록 로그 (Telegram / Webhook / Widget)",
        "log_headers": ["일시 (Timestamp)", "입력 채널", "사용자 입력 메시지 (Check-in)", "AI 분석 및 체크된 습관", "AI 코칭 & 응원 메시지", "처리 상태"],
        "log_samples": [],
    },
    "en": {
        "dash_title": "🌟 ALL-IN-ONE LIFE OS : Master Habits & Execution Dashboard",
        "dash_sub": "Daily & Weekly Life Operating System built on 7 Science & Mentor Domains (Buffett, Huberman, Aurelius)",
        "kpi_done_lbl": "Completed Today",
        "kpi_done_unit": "/35",
        "kpi_today_rate": "Today's Rate",
        "kpi_week_rate": "Weekly Avg Rate",
        "kpi_ai_lbl": "AI Coach Status",
        "kpi_ai_val": "Connected (Live Sync Active)",
        "sec_top5": "📌 Top 5 Focus Habits Today (Warren Buffett's 5/25 Rule)",
        "top5_headers": ["Domain", "Role Model", "Habit Protocol", "Today Status", "Self Feedback / Note"],
        "status_done": "✅ Done",
        "status_todo": "⏳ Todo",
        "top5_notes": ["", "", "", "", ""],
        "sec_ai": "🤖 AI Coach Daily Briefing & Sync Feed",
        "ai_welcome": (
            "💡 [AI Coach Morning Briefing]\n\n"
            "\"Welcome to Life OS! Anchor your morning energy with Andrew Huberman's 15m sunlight and Warren Buffett's #1 priority.\n"
            "Send natural check-ins from your Desktop Widget, CLI, Webhook, Telegram, or Discord anytime to keep SQLite and Excel in sync.\""
        ),
        "sec_domains": "📊 Weekly Completion by 7 Life Domains",
        "dom_headers": ["Code", "Life Domain", "Core Mentors", "Habits", "Weekly Rate", "Tier"],
        "tier_excellent": "🟢 Elite",
        "tier_good": "🟡 Solid",
        "tier_progress": "🔵 Building",
        "tier_idle": "⚪ Idle",
        "db_banner": "🏆 35 Science & Mentor Habits Master Protocol Database",
        "db_headers": ["No", "Life Domain", "Role Model", "Habit Title", "Core Principle", "Actionable Protocol (Checklist)", "Cadence", "Difficulty"],
        "track_banner": "📅 35 Habits Daily Tracker (Enter 1 or ✓ when completed)",
        "track_headers": ["No", "Habit Protocol", "Mon (D1)", "Tue (D2)", "Wed (D3)", "Thu (D4)", "Fri (D5)", "Sat (D6)", "Sun (D7)", "Weekly Rate", "Streak"],
        "streak_high": "🔥 4+/wk",
        "streak_mid": "🌱 Active",
        "streak_idle": "Idle",
        "track_sum_lbl": "📊 Daily Completion Rate (35 Habits)",
        "track_week_tot": "Weekly Avg",
        "rev_banner": "📈 Weekly Executive Review Framework (KPT + Dalio Principles)",
        "rev_sections": [
            ("B4:H4", "🎯 Keep — Key Wins & Repeatable Habits", ""),
            ("B8:H8", "⚠️ Problem — Friction Points & Root Causes", ""),
            ("B12:H12", "🚀 Try — Next Week Micro-Experiments", ""),
            ("B16:H16", "🤖 AI Coach Weekly Summary & Leverage Insight", ""),
        ],
        "log_banner": "🤖 AI Assistant Real-Time Check-in Integration Log",
        "log_headers": ["Timestamp", "Channel", "Check-in Message", "Matched Habits", "AI Coaching Feedback", "Sync Status"],
        "log_samples": [],
    },
    "ja": {
        "dash_title": "🌟 ALL-IN-ONE LIFE OS : 成功習慣＆実行ダッシュボード",
        "dash_sub": "バフェット、フーバーマン、アウレリウスら巨人の7領域原則に基づく日次/週次習慣OS",
        "kpi_done_lbl": "本日達成数",
        "kpi_done_unit": "/35件",
        "kpi_today_rate": "本日の達成率",
        "kpi_week_rate": "週間平均達成率",
        "kpi_ai_lbl": "AIコーチ連携状態",
        "kpi_ai_val": "正常接続 (リアルタイム同期中)",
        "sec_top5": "📌 本日の最重要5習慣 (バフェットの5/25ルール)",
        "top5_headers": ["領域", "ロールモデル", "習慣プロトコル", "本日達成", "セルフメモ"],
        "status_done": "✅ 完了",
        "status_todo": "⏳ 未完了",
        "top5_notes": ["", "", "", "", ""],
        "sec_ai": "🤖 AIコーチ 日次フィードバック＆同期ログ",
        "ai_welcome": (
            "💡 [AIコーチ・モーニングブリーフィング]\n\n"
            "「おはようございます！フーバーマン博士の朝日15分とバフェットの5/25最優先タスクから1日を始めましょう。\n"
            "ウィジェット・CLI・Telegram Botから報告を送ると、SQLiteとExcelへ即座に同期されます。」"
        ),
        "sec_domains": "📊 7ライフ領域別 週間達成率サマリー",
        "dom_headers": ["コード", "ライフ領域", "主要メンター", "習慣数", "週間達成率", "状態評価"],
        "tier_excellent": "🟢 最優秀",
        "tier_good": "🟡 良好",
        "tier_progress": "🔵 進行中",
        "tier_idle": "⚪ 待機",
        "db_banner": "🏆 世界の巨人35成功習慣 ＆ 実行プロトコル・マスターDB",
        "db_headers": ["No", "ライフ領域", "ロールモデル", "習慣名", "核となる原則", "実行プロトコル (Checklist)", "推奨頻度", "難易度"],
        "track_banner": "📅 35習慣 デイリー実践トラッカー (達成時は 1 または ✓ を入力)",
        "track_headers": ["No", "代表習慣プロトコル", "月 (D1)", "火 (D2)", "水 (D3)", "木 (D4)", "金 (D5)", "土 (D6)", "日 (D7)", "週間達成率", "継続"],
        "streak_high": "🔥 週4+",
        "streak_mid": "🌱 進行中",
        "streak_idle": "待機",
        "track_sum_lbl": "📊 日次総合達成率 (35項目基準)",
        "track_week_tot": "週間平均",
        "rev_banner": "📈 週次レビュー フレームワーク (KPT + ダリオ原則)",
        "rev_sections": [
            ("B4:H4", "🎯 Keep — 今週の成果と継続したい良い習慣", ""),
            ("B8:H8", "⚠️ Problem — 課題と摩擦要因の分析", ""),
            ("B12:H12", "🚀 Try — 来週のマイクロ改善アクション", ""),
            ("B16:H16", "🤖 AIコーチ 週次総合フィードバック", ""),
        ],
        "log_banner": "🤖 AIアシスタント連携＆チェックイン記録ログ",
        "log_headers": ["日時 (Timestamp)", "入力チャネル", "チェックイン内容", "一致した習慣", "AIコーチングメッセージ", "処理状態"],
        "log_samples": [],
    },
    "zh": {
        "dash_title": "🌟 ALL-IN-ONE LIFE OS : 35项成功习惯与执行力仪表盘",
        "dash_sub": "融合巴菲特、休伯曼、奥勒留等巨人七大领域原则的日/周生命系统 (AI 实时联动)",
        "kpi_done_lbl": "今日已完成",
        "kpi_done_unit": "/35项",
        "kpi_today_rate": "今日达成率",
        "kpi_week_rate": "本周平均达成率",
        "kpi_ai_lbl": "AI教练同步状态",
        "kpi_ai_val": "已连接 (双向实时同步)",
        "sec_top5": "📌 今日聚焦5大核心习惯 (巴菲特 5/25 法则)",
        "top5_headers": ["领域", "代表导师", "习惯行动方案", "今日状态", "自我反馈 / 备注"],
        "status_done": "✅ 已完成",
        "status_todo": "⏳ 待完成",
        "top5_notes": ["", "", "", "", ""],
        "sec_ai": "🤖 AI 教练每日简报与联动反馈",
        "ai_welcome": (
            "💡 [AI 教练晨间简报]\n\n"
            "“您好！今天建议优先落实休伯曼的晨间日照15分钟与巴菲特5/25首要任务。\n"
            "通过桌面悬浮窗、命令行或 Telegram / Discord 机器人随时打卡，数据会自动同步至 SQLite 与本表格。”"
        ),
        "sec_domains": "📊 七大生命领域每周累计达成率",
        "dom_headers": ["代码", "生命领域", "核心导师", "习惯数", "本周达成率", "状态评级"],
        "tier_excellent": "🟢 卓越",
        "tier_good": "🟡 良好",
        "tier_progress": "🔵 进行中",
        "tier_idle": "⚪ 待启动",
        "db_banner": "🏆 35项成功人士核心习惯与科学执行协议主库",
        "db_headers": ["No", "生命领域", "代表人物", "习惯名称", "核心原则与哲学", "具体执行方案 (Checklist)", "建议频率", "实践难度"],
        "track_banner": "📅 35项习惯每日打卡追踪表 (完成请输入 1 或 ✓)",
        "track_headers": ["No", "核心习惯方案", "周一 (D1)", "周二 (D2)", "周三 (D3)", "周四 (D4)", "周五 (D5)", "周六 (D6)", "周日 (D7)", "周达成率", "连续度"],
        "streak_high": "🔥 周4次+",
        "streak_mid": "🌱 进行中",
        "streak_idle": "待定",
        "track_sum_lbl": "📊 每日总达成率 (以35项为基准)",
        "track_week_tot": "周综合",
        "rev_banner": "📈 每周复盘框架 (KPT + 达利欧原则复盘)",
        "rev_sections": [
            ("B4:H4", "🎯 Keep — 本周成果与值得坚持的好习惯", ""),
            ("B8:H8", "⚠️ Problem — 阻碍与待改进问题", ""),
            ("B12:H12", "🚀 Try — 下周微行动实验", ""),
            ("B16:H16", "🤖 AI 教练周度综合评估反馈", ""),
        ],
        "log_banner": "🤖 AI 助手多端联动打卡日志 (Telegram / Webhook / 悬浮窗)",
        "log_headers": ["时间 (Timestamp)", "输入渠道", "用户打卡内容", "识别匹配的习惯", "AI 教练鼓励反馈", "同步状态"],
        "log_samples": [],
    },
}


def build_life_os_workbook(output_path, lang=None):
    resolved = resolve_language(lang)
    ui = EXCEL_UI.get(resolved, EXCEL_UI["en"])
    sheets = SHEET_TITLES.get(resolved, SHEET_TITLES["en"])
    habits = get_habits_catalog(resolved)
    domain_rows = get_domain_rows(resolved)

    tracker_title = sheets["tracker"]
    tracker_ref = f"'{tracker_title}'"

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    font_family = get_excel_font(resolved)
    title_font = Font(name=font_family, size=16, bold=True, color="FFFFFF")
    subtitle_font = Font(name=font_family, size=10, italic=True, color="94A3B8")
    section_font = Font(name=font_family, size=12, bold=True, color="1E293B")
    header_font = Font(name=font_family, size=11, bold=True, color="FFFFFF")
    bold_font = Font(name=font_family, size=10, bold=True, color="1E293B")
    regular_font = Font(name=font_family, size=10, color="334155")
    kpi_num_font = Font(name=font_family, size=20, bold=True, color="1E3A8A")
    kpi_label_font = Font(name=font_family, size=9, bold=True, color="64748B")

    navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_blue_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_slate_fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    header_emerald_fill = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")
    card_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    card_highlight_fill = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
    accent_gold_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")

    thin_border_side = Side(border_style="thin", color="CBD5E1")
    card_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    thick_bottom_side = Side(border_style="medium", color="1E293B")
    header_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thick_bottom_side)

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # -------------------------------------------------------------
    # SHEET 1: Dashboard
    # -------------------------------------------------------------
    ws_dash = wb.create_sheet(title=sheets["dashboard"])
    ws_dash.views.sheetView[0].showGridLines = True

    ws_dash.merge_cells("B2:J2")
    ws_dash["B2"] = ui["dash_title"]
    ws_dash["B2"].font = title_font
    ws_dash["B2"].fill = navy_fill
    ws_dash["B2"].alignment = Alignment(horizontal="center", vertical="center")

    ws_dash.merge_cells("B3:J3")
    ws_dash["B3"] = ui["dash_sub"]
    ws_dash["B3"].font = subtitle_font
    ws_dash["B3"].fill = navy_fill
    ws_dash["B3"].alignment = Alignment(horizontal="center", vertical="center")

    kpis = [
        ("B5:C7", ui["kpi_done_lbl"], f'=COUNTIF(INDEX({tracker_ref}!D5:J39, 0, WEEKDAY(TODAY(), 2)), 1)&" {ui["kpi_done_unit"]}"', card_highlight_fill, False),
        ("D5:E7", ui["kpi_today_rate"], f"=IFERROR(COUNTIF(INDEX({tracker_ref}!D5:J39, 0, WEEKDAY(TODAY(), 2)), 1)/35, 0)", card_fill, True),
        ("F5:G7", ui["kpi_week_rate"], f"=IFERROR({tracker_ref}!K40, 0)", card_fill, True),
        ("H5:J7", ui["kpi_ai_lbl"], ui["kpi_ai_val"], accent_gold_fill, False),
    ]

    for rng, label, formula_val, fill_color, is_pct in kpis:
        parts = rng.split(":")
        start_col, start_row = parts[0][0], int(parts[0][1:])
        end_col, end_row = parts[1][0], int(parts[1][1:])

        ws_dash.merge_cells(f"{start_col}{start_row}:{end_col}{start_row}")
        ws_dash[f"{start_col}{start_row}"] = label
        ws_dash[f"{start_col}{start_row}"].font = kpi_label_font
        ws_dash[f"{start_col}{start_row}"].alignment = align_center

        ws_dash.merge_cells(f"{start_col}{start_row+1}:{end_col}{end_row}")
        ws_dash[f"{start_col}{start_row+1}"] = formula_val
        ws_dash[f"{start_col}{start_row+1}"].font = kpi_num_font
        ws_dash[f"{start_col}{start_row+1}"].alignment = align_center
        if is_pct:
            ws_dash[f"{start_col}{start_row+1}"].number_format = "0.0%"

        for c_ord in range(ord(start_col), ord(end_col) + 1):
            c_let = chr(c_ord)
            for r in range(start_row, end_row + 1):
                cell = ws_dash[f"{c_let}{r}"]
                cell.fill = fill_color
                cell.border = card_border

    ws_dash.cell(row=9, column=2, value=ui["sec_top5"]).font = section_font
    dash_col_widths = {"B": 18, "C": 18, "D": 38, "E": 14, "F": 34, "G": 14, "H": 18, "I": 18, "J": 18}

    for col_idx, h_text in enumerate(ui["top5_headers"], start=2):
        cell = ws_dash.cell(row=10, column=col_idx, value=h_text)
        cell.font = header_font
        cell.fill = header_blue_fill
        cell.alignment = align_center
        cell.border = header_border

    top5_ids = [1, 6, 11, 16, 26]
    for i, hid in enumerate(top5_ids):
        h = habits[hid - 1]
        tracker_r = hid + 4
        r_idx = 11 + i
        row_data = (
            h["category"],
            h["role_model"],
            h["excel_name"],
            f'=IF(INDEX({tracker_ref}!D{tracker_r}:J{tracker_r}, WEEKDAY(TODAY(), 2))=1, "{ui["status_done"]}", "{ui["status_todo"]}")',
            ui["top5_notes"][i],
        )
        for c_idx, val in enumerate(row_data, start=2):
            cell = ws_dash.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = card_border
            if c_idx in (2, 3, 5):
                cell.alignment = align_center
                if c_idx == 5:
                    cell.font = bold_font
            else:
                cell.alignment = align_left

    ws_dash.cell(row=18, column=2, value=ui["sec_ai"]).font = section_font
    ws_dash.merge_cells("B19:J24")
    ai_box = ws_dash["B19"]
    ai_box.value = ui["ai_welcome"]
    ai_box.font = regular_font
    ai_box.fill = card_highlight_fill
    ai_box.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    for r in range(19, 25):
        for c in range(2, 11):
            ws_dash.cell(row=r, column=c).border = card_border

    ws_dash.cell(row=26, column=2, value=ui["sec_domains"]).font = section_font
    for c_idx, h_text in enumerate(ui["dom_headers"], start=2):
        cell = ws_dash.cell(row=27, column=c_idx, value=h_text)
        cell.font = header_font
        cell.fill = header_slate_fill
        cell.alignment = align_center
        cell.border = header_border

    for i, dom in enumerate(domain_rows):
        r_idx = 28 + i
        k_start = 5 + i * 5
        k_end = k_start + 4
        r_data = (
            dom["code"],
            dom["sheet_domain"],
            dom["gurus"],
            5,
            f"=IFERROR(AVERAGE({tracker_ref}!K{k_start}:K{k_end}), 0)",
            f'=IF(F{r_idx}>=0.8,"{ui["tier_excellent"]}",IF(F{r_idx}>=0.5,"{ui["tier_good"]}",IF(F{r_idx}>0,"{ui["tier_progress"]}","{ui["tier_idle"]}")))',
        )
        for c_idx, val in enumerate(r_data, start=2):
            cell = ws_dash.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = card_border
            if c_idx in (2, 5, 7):
                cell.alignment = align_center
            elif c_idx == 6:
                cell.alignment = align_center
                cell.number_format = "0.0%"
                cell.font = bold_font
            else:
                cell.alignment = align_left

    for col_let, width in dash_col_widths.items():
        ws_dash.column_dimensions[col_let].width = width

    # -------------------------------------------------------------
    # SHEET 2: Habit DB
    # -------------------------------------------------------------
    ws_db = wb.create_sheet(title=sheets["db"])
    ws_db.views.sheetView[0].showGridLines = True
    ws_db.merge_cells("B2:I2")
    ws_db["B2"] = ui["db_banner"]
    ws_db["B2"].font = title_font
    ws_db["B2"].fill = header_emerald_fill
    ws_db["B2"].alignment = Alignment(horizontal="center", vertical="center")

    for c_idx, h_text in enumerate(ui["db_headers"], start=2):
        cell = ws_db.cell(row=4, column=c_idx, value=h_text)
        cell.font = header_font
        cell.fill = header_slate_fill
        cell.alignment = align_center
        cell.border = header_border

    for r_idx, h in enumerate(habits, start=5):
        h_row = (
            h["id"], h["sheet_domain"], h["role_model"], h["excel_name"],
            h["philosophy"], h["protocol"], h["frequency"], h["difficulty"],
        )
        for c_idx, val in enumerate(h_row, start=2):
            cell = ws_db.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = card_border
            if c_idx in (2, 8, 9, 3, 4):
                cell.alignment = align_center
                if c_idx == 4:
                    cell.font = bold_font
            else:
                cell.alignment = align_left

    for col_let, width in {"B": 6, "C": 24, "D": 18, "E": 30, "F": 46, "G": 50, "H": 14, "I": 14}.items():
        ws_db.column_dimensions[col_let].width = width

    # -------------------------------------------------------------
    # SHEET 3: Daily Tracker
    # -------------------------------------------------------------
    ws_track = wb.create_sheet(title=tracker_title)
    ws_track.views.sheetView[0].showGridLines = True
    ws_track.merge_cells("B2:K2")
    ws_track["B2"] = ui["track_banner"]
    ws_track["B2"].font = title_font
    ws_track["B2"].fill = header_blue_fill
    ws_track["B2"].alignment = Alignment(horizontal="center", vertical="center")

    for c_idx, h_text in enumerate(ui["track_headers"], start=2):
        cell = ws_track.cell(row=4, column=c_idx, value=h_text)
        cell.font = header_font
        cell.fill = header_slate_fill
        cell.alignment = align_center
        cell.border = header_border

    for idx, h in enumerate(habits, start=1):
        r_num = idx + 4
        cell_no = ws_track.cell(row=r_num, column=2, value=idx)
        cell_no.font = regular_font
        cell_no.alignment = align_center
        cell_no.border = card_border

        cell_name = ws_track.cell(row=r_num, column=3, value=f"[{h['role_model']}] {h['excel_name']}")
        cell_name.font = bold_font
        cell_name.alignment = align_left
        cell_name.border = card_border

        for day_c in range(4, 11):
            cell_day = ws_track.cell(row=r_num, column=day_c)
            cell_day.value = ""
            cell_day.font = bold_font
            cell_day.alignment = align_center
            cell_day.border = card_border

        cell_rate = ws_track.cell(row=r_num, column=11, value=f"=IFERROR(COUNTIF(D{r_num}:J{r_num}, 1)/7, 0)")
        cell_rate.font = bold_font
        cell_rate.alignment = align_center
        cell_rate.number_format = "0.0%"
        cell_rate.border = card_border

        cell_streak = ws_track.cell(
            row=r_num, column=12,
            value=f'=IF(COUNTIF(D{r_num}:J{r_num}, 1)>=4, "{ui["streak_high"]}", IF(COUNTIF(D{r_num}:J{r_num}, 1)>=1, "{ui["streak_mid"]}", "{ui["streak_idle"]}"))'
        )
        cell_streak.font = regular_font
        cell_streak.alignment = align_center
        cell_streak.border = card_border

    summary_r = 40
    ws_track.merge_cells(f"B{summary_r}:C{summary_r}")
    sum_label = ws_track.cell(row=summary_r, column=2, value=ui["track_sum_lbl"])
    sum_label.font = header_font
    sum_label.fill = header_blue_fill
    sum_label.alignment = align_center
    sum_label.border = header_border

    for day_c in range(4, 11):
        col_let = get_column_letter(day_c)
        cell_sum = ws_track.cell(row=summary_r, column=day_c, value=f"=IFERROR(COUNTIF({col_let}5:{col_let}39, 1)/35, 0)")
        cell_sum.font = header_font
        cell_sum.fill = header_blue_fill
        cell_sum.alignment = align_center
        cell_sum.number_format = "0.0%"
        cell_sum.border = header_border

    cell_tot_rate = ws_track.cell(row=summary_r, column=11, value="=IFERROR(AVERAGE(K5:K39), 0)")
    cell_tot_rate.font = header_font
    cell_tot_rate.fill = header_blue_fill
    cell_tot_rate.alignment = align_center
    cell_tot_rate.number_format = "0.0%"
    cell_tot_rate.border = header_border

    cell_tot_lbl = ws_track.cell(row=summary_r, column=12, value=ui["track_week_tot"])
    cell_tot_lbl.font = header_font
    cell_tot_lbl.fill = header_blue_fill
    cell_tot_lbl.alignment = align_center
    cell_tot_lbl.border = header_border

    for col_let, width in {"B": 6, "C": 38, "D": 12, "E": 12, "F": 12, "G": 12, "H": 12, "I": 12, "J": 12, "K": 15, "L": 14}.items():
        ws_track.column_dimensions[col_let].width = width

    # -------------------------------------------------------------
    # SHEET 4: Weekly Review
    # -------------------------------------------------------------
    ws_rev = wb.create_sheet(title=sheets["review"])
    ws_rev.views.sheetView[0].showGridLines = True
    ws_rev.merge_cells("B2:H2")
    ws_rev["B2"] = ui["rev_banner"]
    ws_rev["B2"].font = title_font
    ws_rev["B2"].fill = header_slate_fill
    ws_rev["B2"].alignment = Alignment(horizontal="center", vertical="center")

    for title_rng, title_txt, body_txt in ui["rev_sections"]:
        ws_rev.merge_cells(title_rng)
        t_cell = ws_rev[title_rng.split(":")[0]]
        t_cell.value = title_txt
        t_cell.font = bold_font
        t_cell.fill = card_highlight_fill
        t_cell.alignment = align_left
        t_cell.border = header_border

        r_start = int(title_rng.split(":")[0][1:]) + 1
        r_end = r_start + 2
        ws_rev.merge_cells(f"B{r_start}:H{r_end}")
        b_cell = ws_rev[f"B{r_start}"]
        b_cell.value = body_txt
        b_cell.font = regular_font
        b_cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        for r in range(r_start, r_end + 1):
            for c in range(2, 9):
                ws_rev.cell(row=r, column=c).border = card_border

    ws_rev.column_dimensions["B"].width = 16
    for c in ["C", "D", "E", "F", "G", "H"]:
        ws_rev.column_dimensions[c].width = 15

    # -------------------------------------------------------------
    # SHEET 5: AI Assistant Log
    # -------------------------------------------------------------
    ws_log = wb.create_sheet(title=sheets["log"])
    ws_log.views.sheetView[0].showGridLines = True
    ws_log.merge_cells("B2:G2")
    ws_log["B2"] = ui["log_banner"]
    ws_log["B2"].font = title_font
    ws_log["B2"].fill = navy_fill
    ws_log["B2"].alignment = Alignment(horizontal="center", vertical="center")

    for c_idx, h_text in enumerate(ui["log_headers"], start=2):
        cell = ws_log.cell(row=4, column=c_idx, value=h_text)
        cell.font = header_font
        cell.fill = header_slate_fill
        cell.alignment = align_center
        cell.border = header_border

    for r_idx, s_log in enumerate(ui["log_samples"], start=5):
        for c_idx, val in enumerate(s_log, start=2):
            cell = ws_log.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font
            cell.border = card_border
            cell.alignment = align_center if c_idx in (2, 3, 7) else align_left

    for col_let, width in {"B": 18, "C": 18, "D": 38, "E": 34, "F": 45, "G": 16}.items():
        ws_log.column_dimensions[col_let].width = width

    target = Path(output_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(target))
    wb.close()
    print(f"Workbook successfully generated ({resolved}) at: {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate localized Life OS Excel workbook")
    parser.add_argument("output", nargs="?", default=str(Path(__file__).resolve().parent / "Life_OS_Successful_Habits.xlsx"))
    parser.add_argument("--lang", type=str, default=None, help="Language code: ko, en, ja, zh (default: OS locale)")
    args = parser.parse_args()
    build_life_os_workbook(args.output, lang=args.lang)
