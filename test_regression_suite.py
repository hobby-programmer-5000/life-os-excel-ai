"""
=============================================================================
🧪 ALL-IN-ONE LIFE OS : Comprehensive Regression & Integration Test Suite
=============================================================================
엑셀 수식, 파이썬 코어(오프라인 다국어 NLP), SQLite 3-Way 양방향 동기화, 봇 웹훅/텔레그램,
Tkinter 플로팅 UI, 그리고 빌드된 실행 파일(.exe) 실제 구동까지 전방위 회귀 검증.

모든 테스트는 격리된 임시 디렉토리에서 실행되므로 사용자의 실제 life_os.db 및
Life_OS_Successful_Habits.xlsx 데이터를 손상시키지 않습니다.
=============================================================================
"""

import os
import re
import sys
import json
import time
import socket
import sqlite3
import tempfile
import datetime
import subprocess
import contextlib
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import openpyxl
import requests
import tkinter as tk

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from generate_excel import build_life_os_workbook
from ai_secretary import HABITS_CATALOG, LocalHabitNLP, LifeOSSecretary
from database import DatabaseManager, resolve_base_dir
from assistant_engine import AssistantEngine, PERSONAS, WindowsAutostartManager, HABIT_ALLOWED_HOURS, is_habit_suitable_for_hour
from bot_bridge import BotBridgeServer
from telegram_bot import TelegramBotRunner
from discord_bot import DiscordBotRunner, _MinimalWebSocketClient
from floating_widget import FloatingAssistantWidget
from tray_manager import SystemTrayManager, create_tray_icon_image
from app_icon import get_app_icon_paths
from ui_theme import THEME, get_lucide_dir, render_lucide_icon
from i18n import detect_system_language, get_app_name, resolve_language, SHEET_TITLES, tr, format_date_nav_labels
from i18n_habits import get_habits_catalog
from i18n_personas import get_personas
from build_exe import generate_version_info_file, verify_clean_exe_bundle


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestExcelRegression(unittest.TestCase):
    """1. 엑셀 워크북 구조 및 100개 수식 무결성 회귀 테스트"""

    def test_generated_workbook_structure_and_formulas(self):
        with tempfile.TemporaryDirectory() as td:
            xlsx = Path(td) / "Life_OS_Successful_Habits.xlsx"
            build_life_os_workbook(str(xlsx), lang="ko")
            self.assertTrue(xlsx.is_file())

            wb = openpyxl.load_workbook(xlsx, data_only=False)
            try:
                expected_sheets = ["📊 대시보드", "🏆 성공인 습관DB", "📅 일일트래커", "📈 주간회고", "🤖 AI비서 연동로그"]
                self.assertEqual(wb.sheetnames, expected_sheets)

                ws_db = wb["🏆 성공인 습관DB"]
                db_ids = [ws_db.cell(r, 2).value for r in range(5, 40)]
                self.assertEqual(db_ids, list(range(1, 36)))

                ws_track = wb["📅 일일트래커"]
                self.assertEqual(ws_track.cell(40, 2).value, "📊 일일 총 달성률 (35개 기준)")

                formula_count = 0
                for sname in wb.sheetnames:
                    ws = wb[sname]
                    for row in ws.iter_rows(values_only=True):
                        for val in row:
                            if isinstance(val, str):
                                for err in ("#DIV/0!", "#REF!", "#NAME?", "#VALUE!", "#N/A", "#NUM!"):
                                    self.assertNotIn(err, val, f"Formula error literal {err} found in {sname}")
                                if val.startswith("="):
                                    formula_count += 1
                                    if "AVERAGE(" in val or "/7" in val or "/35" in val:
                                        self.assertIn("IFERROR", val, f"Unsafe division/average without IFERROR: {val}")
                self.assertGreaterEqual(formula_count, 90)
            finally:
                wb.close()

    def test_live_excel_file_integrity(self):
        live_xlsx = PROJECT_ROOT / "Life_OS_Successful_Habits.xlsx"
        if not live_xlsx.is_file():
            self.skipTest("Personal Life_OS_Successful_Habits.xlsx not yet generated")
        wb = openpyxl.load_workbook(live_xlsx, data_only=False)
        try:
            self.assertEqual(wb.sheetnames, ["📊 대시보드", "🏆 성공인 습관DB", "📅 일일트래커", "📈 주간회고", "🤖 AI비서 연동로그"])
            self.assertIn("IFERROR", str(wb["📊 대시보드"]["F28"].value))
        finally:
            wb.close()


class TestLocalNLPRegression(unittest.TestCase):
    """2. 100% 오프라인 다국어 로컬 NLP 35대 키워드, 자연어 문장 입력, 오체크 방지 회귀 테스트"""

    def test_all_35_habits_every_keyword_matches(self):
        nlp = LocalHabitNLP(lang="ko")
        for habit in get_habits_catalog("ko"):
            hid = habit["id"]
            for kw in habit["keywords"]:
                matched, msg = nlp.analyze_checkin(f"오늘 {kw} 실천 완료했습니다", lang="ko")
                self.assertIn(hid, matched, f"Habit {hid} failed to match keyword '{kw}'")
                self.assertTrue(bool(msg.strip()))

    def test_unrelated_text_never_triggers_false_positives(self):
        nlp = LocalHabitNLP(lang="ko")
        for noise in ("dk", "asdfqwer", "ㅋㅋㅋ", "테스트", "오늘 날씨 좋네", "", "   "):
            matched, coaching = nlp.analyze_checkin(noise, lang="ko")
            self.assertEqual(matched, [], f"Noise '{noise}' falsely matched {matched}")
            self.assertIn("찾지 못했습니다", coaching)

    def test_multi_habit_and_spacing_insensitivity(self):
        nlp = LocalHabitNLP()
        matched, _ = nlp.analyze_checkin("가장 중요한 일 정하고 찬물 샤워 후 Zone 2 달리기!")
        self.assertTrue({1, 7, 10}.issubset(set(matched)), f"Matched: {matched}")

    def test_realistic_conversational_inputs_across_4_languages(self):
        cases = [
            ("ko", "아침에 일어나자마자 햇빛 15분 쬐고 찬물 샤워했어", {6, 7}),
            ("ko", "달리기 유산소 30분 뛰고 잠들기 전 스마트폰 멀리둠", {8, 10}),
            ("en", "Read for 1 hour and wrote 5 things in my gratitude journal", {15, 17}),
            ("en", "Did zone 2 cardio workout and put my phone away before bed", {8, 10}),
            ("en", "Applied the 2-minute rule and meditated for 20 minutes", {12, 31}),
            ("ja", "1時間読書して寝る前に感謝日記を5つ書いた", {15, 17}),
            ("ja", "Zone 2の有酸素運動をして寝る前はスマホを見なかった", {8, 10}),
            ("zh", "早上晒了15分钟太阳还洗了冷水澡", {6, 7}),
            ("zh", "做完2分钟法则然后冥想20分钟", {12, 31}),
        ]
        for lang, text, expected_ids in cases:
            nlp = LocalHabitNLP(lang=lang)
            matched, msg = nlp.analyze_checkin(text, lang=lang)
            self.assertTrue(
                expected_ids.issubset(set(matched)),
                f"[{lang}] '{text}' expected {expected_ids}, got {matched}",
            )
            self.assertTrue(bool(msg.strip()))


class TestSQLiteAndBidirectionalSync(unittest.TestCase):
    """3. SQLite 스키마, 다중 날짜, 엑셀↔SQLite 3-Way 양방향 동기화, 이식성 테스트"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        self.db_path = self.tmp / "life_os.db"
        self.xlsx_path = self.tmp / "Life_OS_Successful_Habits.xlsx"
        self.db = DatabaseManager(db_path=self.db_path)
        self.db.set_setting("excel_path", str(self.xlsx_path))
        self.engine = AssistantEngine(self.db)

    def tearDown(self):
        self._td.cleanup()

    def test_schema_and_35_habits_seeded(self):
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        self.assertTrue({"habits", "daily_checks", "daily_logs", "app_settings"}.issubset(tables))
        self.assertEqual(len(self.db.get_habits()), 35)

    def test_cli_secretary_writes_sqlite_and_excel(self):
        env = os.environ.copy()
        env["LIFE_OS_DATA_DIR"] = str(self.tmp)
        res = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "ai_secretary.py"), "--checkin", "찬물샤워와 90분 딥워크 완료!"],
            env=env, capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        today_str = datetime.date.today().isoformat()
        chk = self.db.get_checks_for_date(today_str)
        self.assertEqual(chk.get(2, {}).get("status"), 1)
        self.assertEqual(chk.get(7, {}).get("status"), 1)
        self.assertTrue(self.xlsx_path.is_file())

    def test_multi_temporal_date_traversal(self):
        today = datetime.date.today()
        yesterday = (today - datetime.timedelta(days=1)).isoformat()
        future = (today + datetime.timedelta(days=4)).isoformat()

        self.db.toggle_check(yesterday, 1, status=1, memo="retro")
        self.db.save_log_for_date(future, summary_text="D+4 plan")

        self.assertEqual(self.db.get_checks_for_date(yesterday)[1]["status"], 1)
        self.assertEqual(self.db.get_log_for_date(future)["summary_text"], "D+4 plan")

    def test_three_way_bidirectional_sync_and_lock_resilience(self):
        today = datetime.date.today()
        today_str = today.isoformat()
        col_idx = 4 + today.weekday()

        # Baseline creation + App -> Excel
        self.db.toggle_check(today_str, 5, status=1)
        ok, _ = self.db.sync_to_excel(excel_path=str(self.xlsx_path))
        self.assertTrue(ok)
        self.assertTrue(self.xlsx_path.is_file())

        # Excel manual check (No.12 = '✓') & uncheck (No.5 = '')
        time.sleep(0.12)
        wb = openpyxl.load_workbook(self.xlsx_path)
        ws = wb["📅 일일트래커"]
        ws.cell(row=12 + 4, column=col_idx, value="✓")
        ws.cell(row=5 + 4, column=col_idx, value="")
        wb.save(self.xlsx_path)
        wb.close()

        # Simulate concurrent App toggle (No.14 = 1) before explicit Excel pull
        self.db.toggle_check(today_str, 14, status=1)
        ok2, _ = self.db.sync_to_excel(excel_path=str(self.xlsx_path))
        self.assertTrue(ok2)

        checks = self.db.get_checks_for_date(today_str)
        self.assertEqual(checks.get(5, {}).get("status", 0), 0)
        self.assertEqual(checks.get(12, {}).get("status", 0), 1)
        self.assertEqual(checks.get(14, {}).get("status", 0), 1)

        # Simulate locked Excel PermissionError
        with patch("openpyxl.Workbook.save", side_effect=PermissionError("locked")):
            ok_lock, msg_lock = self.db.sync_to_excel(excel_path=str(self.xlsx_path))
            self.assertFalse(ok_lock)
            self.assertIn("열려 있습니다", msg_lock)

    def test_cross_platform_base_dir_and_autostart(self):
        dist_dir = self.tmp / "repo" / "dist"
        repo_dir = self.tmp / "repo"
        dist_dir.mkdir(parents=True)
        (repo_dir / "main_app.py").write_text("# dummy", encoding="utf-8")

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("LIFE_OS_DATA_DIR", None)
            with patch.object(sys, "frozen", True, create=True), \
                 patch.object(sys, "executable", str(dist_dir / "LifeOS_Assistant_v2.exe")):
                self.assertEqual(resolve_base_dir(), repo_dir)

        orig_p = sys.platform
        try:
            sys.platform = "linux"
            self.assertFalse(WindowsAutostartManager.is_autostart_enabled())
            ok_a, _ = WindowsAutostartManager.set_autostart(True)
            self.assertFalse(ok_a)
        finally:
            sys.platform = orig_p


class TestBotConnectionsRegression(unittest.TestCase):
    """4. HTTP 웹훅 브릿지 & 텔레그램 봇 핸들러 (+ 실서버 연결) 테스트"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        self.db = DatabaseManager(db_path=self.tmp / "life_os.db")
        self.db.set_setting("language", "ko")
        self.xlsx = self.tmp / "Life_OS_Successful_Habits.xlsx"
        self.db.set_setting("excel_path", str(self.xlsx))
        self.engine = AssistantEngine(self.db)

    def tearDown(self):
        self._td.cleanup()

    def test_bot_bridge_full_http_suite(self):
        events = []
        bridge = BotBridgeServer(self.db, self.engine, host="127.0.0.1", port=0, on_checkin=lambda r: events.append(r))
        ok, _ = bridge.start()
        self.assertTrue(ok)
        base = f"http://127.0.0.1:{bridge.port}"
        try:
            self.assertEqual(requests.get(f"{base}/", timeout=5).status_code, 200)
            self.assertEqual(requests.get(f"{base}/stats", timeout=5).status_code, 200)
            self.assertEqual(requests.get(f"{base}/habits", timeout=5).json()["count"], 35)
            self.assertEqual(requests.get(f"{base}/unknown", timeout=5).status_code, 404)
            self.assertEqual(requests.options(f"{base}/checkin", timeout=5).status_code, 200)

            # Malformed JSON -> 400
            r_bad = requests.post(f"{base}/checkin", data="{not-json", headers={"Content-Type": "application/json"}, timeout=5)
            self.assertEqual(r_bad.status_code, 400)

            # Empty message -> 400
            self.assertEqual(requests.post(f"{base}/checkin", json={"message": ""}, timeout=5).status_code, 400)

            # Valid check-in with day_offset=-1
            y_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
            r_ok = requests.post(
                f"{base}/checkin",
                json={"message": "어제 90분 딥워크 완료", "channel": "Discord Regression", "day_offset": -1},
                timeout=5
            )
            self.assertEqual(r_ok.status_code, 200)
            self.assertEqual(r_ok.json()["data"]["date"], y_str)
            self.assertIn(2, r_ok.json()["data"]["matched_ids"])
            self.assertEqual(len(events), 1)
            self.assertEqual(self.db.get_checks_for_date(y_str)[2]["status"], 1)

            # Nudge & Review
            self.assertIn("question", requests.post(f"{base}/nudge", json={}, timeout=5).json()["nudge"])
            self.assertTrue(requests.post(f"{base}/review", json={}, timeout=5).json()["excel_synced"])
        finally:
            bridge.stop()

    def test_telegram_bot_commands_and_edge_cases(self):
        tg = TelegramBotRunner("123:ABC", self.db, self.engine)
        self.assertIn("/status", tg.handle_text_message("/start"))
        self.assertIn("오늘의 현황", tg.handle_text_message("/status"))
        self.assertIn("넛지", tg.handle_text_message("/nudge"))
        self.assertIn("주간 회고", tg.handle_text_message("/review"))
        self.assertIn("적어주세요", tg.handle_text_message("/어제"))
        self.assertIn("적어주세요", tg.handle_text_message("/yesterday   "))

        y_reply = tg.handle_text_message("/어제 감사일기 작성")
        y_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        self.assertEqual(self.db.get_checks_for_date(y_str)[15]["status"], 1)
        self.assertIn("감사일기", y_reply)

        bogus_reply = tg.handle_text_message("dk")
        self.assertIn("매칭된 습관 키워드가 없습니다", bogus_reply)

    def test_live_configured_telegram_connection_readonly(self):
        root_db = PROJECT_ROOT / "life_os.db"
        tok = ""
        if root_db.is_file():
            with contextlib.closing(sqlite3.connect(f"file:{root_db}?mode=ro", uri=True)) as conn:
                row = conn.execute("SELECT value FROM app_settings WHERE key = 'telegram_token'").fetchone()
                tok = row[0] if row and row[0] else ""
        tok = tok or os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not tok:
            self.skipTest("No Telegram token configured in root DB")
        ok, info = TelegramBotRunner.verify_token(tok)
        self.assertTrue(ok, f"Live Telegram getMe failed: {info}")

    def test_discord_bot_commands_routing_and_rfc6455_websocket(self):
        import base64, hashlib, struct, threading

        self.assertEqual(DiscordBotRunner.normalize_token("Bot abc.def"), "abc.def")
        ok_empty, _ = DiscordBotRunner.verify_token("", lang="ko")
        self.assertFalse(ok_empty)

        mock_me = MagicMock()
        mock_me.status_code = 200
        mock_me.content = b'{"id":"1"}'
        mock_me.json.return_value = {"id": "777", "username": "LifeOSDiscordBot"}
        with patch("discord_bot.requests.get", return_value=mock_me):
            ok_dc, info_dc = DiscordBotRunner.verify_token("dc-token", lang="ko")
            self.assertTrue(ok_dc)
            self.assertIn("LifeOSDiscordBot", info_dc)

        events = []
        dc = DiscordBotRunner("Bot test.tok", self.db, self.engine, on_checkin=lambda r: events.append(r))
        dc.bot_user_id = "999000"

        # Ignore own/bot messages
        self.assertIsNone(dc.handle_message_event({"author": {"id": "1", "bot": True}, "channel_id": "10", "content": "90분 딥워크"}))

        # Direct message accepts natural check-in directly
        ch, rep = dc.handle_message_event({"author": {"id": "42"}, "channel_id": "dm1", "content": "90분 딥워크 완료!"})
        self.assertEqual(ch, "dm1")
        self.assertIn("딥워크", rep)
        self.assertEqual(self.db.get_checks_for_date(datetime.date.today().isoformat()).get(2, {}).get("status"), 1)
        self.assertEqual(len(events), 1)

        # Guild channel ignores ambient chatter unless @mentioned or '!' command or dedicated channel_id
        self.assertIsNone(dc.handle_message_event({
            "guild_id": "g1", "channel_id": "c1", "author": {"id": "42"}, "content": "오늘 점심 뭐먹지"
        }))
        ch_m, rep_m = dc.handle_message_event({
            "guild_id": "g1", "channel_id": "c1", "author": {"id": "42"}, "content": "<@!999000> !status"
        })
        self.assertEqual(ch_m, "c1")
        self.assertIn("오늘의 현황", rep_m)

        ch_y, rep_y = dc.handle_message_event({
            "guild_id": "g1", "channel_id": "c1", "author": {"id": "42"}, "content": "!어제   "
        })
        self.assertEqual(ch_y, "c1")
        self.assertIn("적어주세요", rep_y)

        # Dedicated channel_id accepts natural messages directly without @mention
        dc.allowed_channel_id = "dedicated-ch"
        ch_d, _ = dc.handle_message_event({
            "guild_id": "g1", "channel_id": "dedicated-ch", "author": {"id": "42"}, "content": "찬물샤워 완료"
        })
        self.assertEqual(ch_d, "dedicated-ch")
        self.assertEqual(self.db.get_checks_for_date(datetime.date.today().isoformat()).get(7, {}).get("status"), 1)

        # Real loopback TCP RFC 6455 WebSocket handshake + PING/PONG + HELLO/IDENTIFY + MESSAGE_CREATE test
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        ws_port = srv.getsockname()[1]
        server_seen = {}

        def _send_srv_frame(conn, opcode, payload_bytes):
            ln = len(payload_bytes)
            hdr = bytearray([0x80 | opcode])
            if ln < 126:
                hdr.append(ln)
            elif ln <= 65535:
                hdr.append(126)
                hdr.extend(struct.pack("!H", ln))
            conn.sendall(bytes(hdr) + payload_bytes)

        def _recv_cli_frame(conn):
            def _ex(n):
                b = bytearray()
                while len(b) < n:
                    c = conn.recv(n - len(b))
                    if not c:
                        raise EOFError()
                    b.extend(c)
                return bytes(b)
            b1, b2 = _ex(2)
            op = b1 & 0x0F
            masked = bool(b2 & 0x80)
            ln = b2 & 0x7F
            if ln == 126:
                ln = struct.unpack("!H", _ex(2))[0]
            mask = _ex(4) if masked else b"\x00\x00\x00\x00"
            pl = _ex(ln)
            if masked:
                pl = bytes(v ^ mask[i & 3] for i, v in enumerate(pl))
            return op, pl

        def _ws_server_worker():
            conn, _ = srv.accept()
            conn.settimeout(5.0)
            try:
                raw_req = conn.recv(4096).decode("latin-1")
                key_line = [ln for ln in raw_req.splitlines() if ln.lower().startswith("sec-websocket-key:")][0]
                cli_key = key_line.split(":", 1)[1].strip()
                acc = base64.b64encode(hashlib.sha1((cli_key + _MinimalWebSocketClient.WS_MAGIC.decode()).encode()).digest()).decode()
                conn.sendall((
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {acc}\r\n\r\n"
                ).encode("latin-1"))

                # Send HELLO immediately after 101
                _send_srv_frame(conn, 0x1, json.dumps({"op": 10, "d": {"heartbeat_interval": 30000}}).encode())
                # Expect HB + IDENTIFY from client
                frames = []
                for _ in range(2):
                    frames.append(_recv_cli_frame(conn))
                server_seen["ident"] = [json.loads(pl.decode()) for op, pl in frames if op == 0x1]

                # Send PING and verify client echoes PONG
                _send_srv_frame(conn, 0x9, b"ping-check")
                pong_op, pong_pl = _recv_cli_frame(conn)
                server_seen["pong"] = (pong_op, pong_pl)

                # Send READY + DM MESSAGE_CREATE
                _send_srv_frame(conn, 0x1, json.dumps({"op": 0, "s": 1, "t": "READY", "d": {"user": {"id": "888", "username": "LoopBot"}}}).encode())
                _send_srv_frame(conn, 0x1, json.dumps({
                    "op": 0, "s": 2, "t": "MESSAGE_CREATE",
                    "d": {"author": {"id": "42"}, "channel_id": "dm-ws", "content": "감사일기 작성 완료"}
                }).encode())
                time.sleep(0.25)
                _send_srv_frame(conn, 0x8, struct.pack("!H", 1000))
            finally:
                conn.close()
                srv.close()

        t_srv = threading.Thread(target=_ws_server_worker, daemon=True)
        t_srv.start()

        sent_replies = []
        dc_ws = DiscordBotRunner("dc-tok", self.db, self.engine)
        dc_ws._running = True
        with patch.object(dc_ws, "_get_gateway_url", return_value=f"ws://127.0.0.1:{ws_port}/?v=10&encoding=json"), \
             patch.object(dc_ws, "_send_reply", side_effect=lambda cid, txt: sent_replies.append((cid, txt))):
            dc_ws._connect_and_listen()
        t_srv.join(timeout=3)

        self.assertEqual(server_seen.get("pong"), (0xA, b"ping-check"))
        ident_ops = {p["op"]: p for p in server_seen.get("ident", [])}
        self.assertIn(2, ident_ops)
        self.assertEqual(ident_ops[2]["d"]["intents"], DiscordBotRunner.INTENTS_FULL)
        self.assertTrue(len(sent_replies) == 1 and sent_replies[0][0] == "dm-ws")
        self.assertEqual(self.db.get_checks_for_date(datetime.date.today().isoformat()).get(15, {}).get("status"), 1)


class TestFloatingWidgetUIRegression(unittest.TestCase):
    """5. 플로팅 위젯 레이아웃, 고급 모드, 팝업 창 회귀 테스트"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        self.db = DatabaseManager(db_path=self.tmp / "life_os.db")
        self.xlsx = self.tmp / "Life_OS_Successful_Habits.xlsx"
        self.db.set_setting("excel_path", str(self.xlsx))
        self.db.set_setting("sound_enabled", "false")
        self.db.set_setting("toast_enabled", "false")
        self.engine = AssistantEngine(self.db)
        self.root = tk.Tk()
        self.widget = FloatingAssistantWidget(self.root, self.db, self.engine)
        self.root.update()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass
        self._td.cleanup()

    def test_widget_modes_popups_and_input_visibility(self):
        # Navigate dates
        self.widget.navigate_date(-1)
        self.widget.go_to_today()
        self.root.update()

        # Long coaching message never pushes entry_checkin offscreen
        self.widget.lbl_nudge_text.config(text="긴 코칭 메시지 테스트 " * 15)
        self.widget._adjust_window_height()
        self.root.update()
        rel_bottom = self.widget.entry_checkin.winfo_rooty() - self.root.winfo_rooty() + self.widget.entry_checkin.winfo_height()
        self.assertLessEqual(rel_bottom, self.root.winfo_height())

        # Bogus natural check-in does not mark any habits
        before_cnt = len(self.db.get_checks_for_date(datetime.date.today().isoformat()))
        self.widget.entry_checkin.delete(0, tk.END)
        self.widget.entry_checkin.insert(0, "dk")
        self.widget.submit_natural_checkin()
        self.root.update()
        after_cnt = len(self.db.get_checks_for_date(datetime.date.today().isoformat()))
        self.assertEqual(before_cnt, after_cnt)

        # Custom count=8 & shuffle & all_scroll 35 mode
        self.db.set_setting("quick_habit_limit", "8")
        self.widget.shuffle_quick_habits()
        self.root.update()
        self.assertEqual(len(self.widget.custom_habit_ids), 8)

        self.db.set_setting("quick_view_mode", "all_scroll")
        self.widget._populate_quick_habits()
        self.root.update()
        self.assertIsNotNone(self.widget._quick_canvas)

        # Duplicate window protection on 35-list, keyword help, bot settings
        self.widget.open_full_checklist_window()
        win1 = self.widget._full_checklist_win
        self.widget.open_full_checklist_window()
        self.assertIs(win1, self.widget._full_checklist_win)
        win1.destroy()

        self.widget.open_keyword_help_dialog()
        self.assertTrue(self.widget._keyword_help_win.winfo_exists())
        self.widget._keyword_help_win.destroy()

        # Unified Growth Graph icon + Modern Minimal Theme & Lucide Stock checks
        ico_p, png_p = get_app_icon_paths()
        self.assertTrue(ico_p.is_file() and png_p.is_file())
        tray_img = create_tray_icon_image()
        self.assertEqual(tray_img.size, (64, 64))
        self.assertTrue(hasattr(self.widget, "_app_icon_photo"))
        self.assertEqual(THEME["bg"], "#09090B")
        self.assertEqual(self.widget.cget_bg() if hasattr(self.widget, "cget_bg") else self.widget.c_bg, "#09090B")
        lucide_svgs = list(get_lucide_dir().glob("*.svg"))
        self.assertGreaterEqual(len(lucide_svgs), 25)
        self.assertTrue((get_lucide_dir() / "LICENSE").is_file())
        rendered_ico = render_lucide_icon("trending-up", size=24, color=THEME["green"])
        self.assertEqual(rendered_ico.size, (24, 24))

        self.widget.open_bot_settings_dialog()
        bot_win = self.widget._bot_settings_win
        self.assertTrue(bot_win.winfo_exists())
        self.root.update()
        cards = bot_win._bot_cards
        self.assertEqual(set(cards.keys()), {"telegram", "discord", "webhook"})
        for card in cards.values():
            self.assertEqual(card.cget("highlightbackground"), THEME["border"])
        self.assertLess(cards["telegram"].winfo_y(), cards["discord"].winfo_y())
        self.assertLess(cards["discord"].winfo_y(), cards["webhook"].winfo_y())
        bot_win.destroy()

        # Opacity horizontal slider live preview, cancel revert, and persist
        set_win = self.widget.open_settings_dialog()
        self.root.update()
        self.assertEqual(str(set_win._scale_opacity.cget("orient")), "horizontal")
        set_win._scale_opacity.set(55)
        self.root.update()
        self.assertEqual(set_win._lbl_opacity_val.cget("text"), "55%")
        self.assertAlmostEqual(float(self.root.attributes("-alpha")), 0.55, places=2)
        set_win._cancel_settings()
        self.root.update()
        self.assertAlmostEqual(float(self.root.attributes("-alpha")), 0.94, places=2)

        set_win2 = self.widget.open_settings_dialog()
        self.root.update()
        set_win2._scale_opacity.set(72)
        self.root.update()
        with patch("floating_widget.messagebox.showinfo"):
            set_win2._save_settings()
        self.root.update()
        self.assertEqual(float(self.db.get_setting("opacity")), 0.72)
        self.assertAlmostEqual(float(self.root.attributes("-alpha")), 0.72, places=2)

    def test_relative_date_buttons_and_time_aware_nudge(self):
        # 1) Relative date button labels adapt accurately when navigating away from today
        self.assertEqual(format_date_nav_labels(0, "ko"), ("◀ 어제", "오늘", "내일 ▶"))
        self.assertEqual(format_date_nav_labels(-1, "ko"), ("◀ 전날", "오늘", "다음날 ▶"))
        self.assertEqual(format_date_nav_labels(2, "ko"), ("◀ 전날", "오늘", "다음날 ▶"))
        self.assertEqual(format_date_nav_labels(0, "ja"), ("◀ 昨日", "今日", "明日 ▶"))
        self.assertEqual(format_date_nav_labels(-3, "ja"), ("◀ 前日", "今日", "翌日 ▶"))
        self.assertEqual(format_date_nav_labels(0, "zh"), ("◀ 昨天", "今天", "明天 ▶"))
        self.assertEqual(format_date_nav_labels(1, "zh"), ("◀ 前一天", "今天", "后一天 ▶"))

        self.assertEqual(self.widget.btn_prev.cget("text"), "◀ 어제")
        self.assertEqual(self.widget.btn_next.cget("text"), "내일 ▶")

        self.widget.navigate_date(-1)
        self.root.update()
        self.assertEqual(self.widget.btn_prev.cget("text"), "◀ 전날")
        self.assertEqual(self.widget.btn_next.cget("text"), "다음날 ▶")

        self.widget.navigate_date(-2)
        self.root.update()
        self.assertEqual(self.widget.btn_prev.cget("text"), "◀ 전날")
        self.assertEqual(self.widget.btn_next.cget("text"), "다음날 ▶")

        self.widget.go_to_today()
        self.root.update()
        self.assertEqual(self.widget.btn_prev.cget("text"), "◀ 어제")
        self.assertEqual(self.widget.btn_next.cget("text"), "내일 ▶")

        self.widget.navigate_date(1)
        self.root.update()
        self.assertEqual(self.widget.btn_prev.cget("text"), "◀ 전날")
        self.assertEqual(self.widget.btn_next.cget("text"), "다음날 ▶")

        self.widget.go_to_today()
        self.root.update()

        # 2) Time-of-day suitability rules prevent dawn/morning/evening mismatches
        today_str = datetime.date.today().isoformat()
        for hr in (0, 2, 3):
            picked_ids = {self.engine.get_smart_nudge(today_str, now_hour=hr)["habit_id"] for _ in range(50)}
            # Dawn 00..03 never nudges morning, cold-shower, dawn-wake, or evening/bedtime habits
            self.assertTrue(picked_ids.isdisjoint({5, 6, 7, 8, 9, 15, 16, 33, 34}), f"Unexpected IDs at {hr}: {picked_ids}")

        picked_4am = {self.engine.get_smart_nudge(today_str, now_hour=4)["habit_id"] for _ in range(60)}
        self.assertTrue(picked_4am.isdisjoint({5, 6, 7, 8, 9, 15, 33, 34}), f"Unexpected evening/day IDs at 4am: {picked_4am}")

        picked_9am = {self.engine.get_smart_nudge(today_str, now_hour=9)["habit_id"] for _ in range(60)}
        self.assertTrue(picked_9am.isdisjoint({8, 9, 15, 34}), f"Unexpected evening/bed IDs at 9am: {picked_9am}")

        picked_2pm = {self.engine.get_smart_nudge(today_str, now_hour=14)["habit_id"] for _ in range(60)}
        self.assertTrue(picked_2pm.isdisjoint({5, 6, 8, 9, 15, 16, 33, 34}), f"Unexpected time-locked IDs at 2pm: {picked_2pm}")
        self.assertGreaterEqual(len(picked_2pm), 8, "Should maintain random variety across timeless habits")

        picked_9pm = {self.engine.get_smart_nudge(today_str, now_hour=21)["habit_id"] for _ in range(60)}
        self.assertTrue(picked_9pm.isdisjoint({5, 6, 16}), f"Unexpected dawn/morning IDs at 9pm: {picked_9pm}")

        # 3) If ONLY out-of-window habits remain uncompleted (e.g. only bedtime at 3 AM), report window_done safely
        for hid in range(1, 36):
            if hid not in {8, 9, 15, 34}:
                self.db.toggle_check(today_str, hid, status=1)
        res_dawn_only_bed = self.engine.get_smart_nudge(today_str, now_hour=3)
        self.assertIsNone(res_dawn_only_bed["habit_id"])
        self.assertTrue(res_dawn_only_bed["all_done"])
        self.assertTrue(res_dawn_only_bed.get("window_done"))
        self.assertTrue(all(is_habit_suitable_for_hour(hid, 21) for hid in (8, 9, 15)))
        self.assertFalse(any(is_habit_suitable_for_hour(hid, 3) for hid in (8, 9, 15, 34)))


class TestBuiltExecutableLive(unittest.TestCase):
    """6. 빌드된 dist/LifeOS_Assistant_v2.exe 실전 프로세스 기동 및 HTTP/DB/엑셀 E2E 테스트"""

    def test_compiled_exe_live_startup_and_checkin(self):
        exe_path = PROJECT_ROOT / "dist" / "LifeOS_Assistant_v2.exe"
        self.assertTrue(exe_path.is_file(), f"Executable missing: {exe_path}")

        port = find_free_port()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            db_path = tmp / "life_os.db"
            db = DatabaseManager(db_path=db_path)
            db.set_setting("webhook_enabled", "true")
            db.set_setting("webhook_host", "127.0.0.1")
            db.set_setting("webhook_port", str(port))
            db.set_setting("sound_enabled", "false")
            db.set_setting("toast_enabled", "false")
            db.set_setting("telegram_enabled", "false")

            env = os.environ.copy()
            env["LIFE_OS_DATA_DIR"] = str(tmp)

            proc = subprocess.Popen([str(exe_path)], env=env)
            try:
                stats_ok = False
                for _ in range(30):
                    if proc.poll() is not None:
                        self.fail(f"Built exe exited unexpectedly with code {proc.returncode}")
                    try:
                        r = requests.get(f"http://127.0.0.1:{port}/stats", timeout=1)
                        if r.status_code == 200:
                            stats_ok = True
                            break
                    except Exception:
                        time.sleep(0.5)

                self.assertTrue(stats_ok, "Built exe built-in webhook did not become ready within 15s")

                # Execute real POST /checkin against the running .exe
                r_post = requests.post(
                    f"http://127.0.0.1:{port}/checkin",
                    json={"message": "아침 햇빛 15분 보고 90분 딥워크 완료!", "channel": "EXE Probe"},
                    timeout=8
                )
                self.assertEqual(r_post.status_code, 200)
                data = r_post.json()["data"]
                self.assertTrue({2, 6}.issubset(set(data["matched_ids"])))
                self.assertTrue(data["excel_synced"])

                # Verify exe created and updated isolated Excel & SQLite inside tmp
                xlsx_out = tmp / "Life_OS_Successful_Habits.xlsx"
                self.assertTrue(xlsx_out.is_file())
                today_str = datetime.date.today().isoformat()
                col_idx = 4 + datetime.date.today().weekday()
                wb = openpyxl.load_workbook(xlsx_out, read_only=True)
                try:
                    ws = wb["📅 일일트래커"]
                    self.assertEqual(ws.cell(row=2 + 4, column=col_idx).value, 1)
                    self.assertEqual(ws.cell(row=6 + 4, column=col_idx).value, 1)
                finally:
                    wb.close()

                verify_db = DatabaseManager(db_path=db_path)
                chk = verify_db.get_checks_for_date(today_str)
                self.assertEqual(chk[2]["status"], 1)
                self.assertEqual(chk[6]["status"], 1)
            finally:
                if sys.platform.startswith("win"):
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
                else:
                    proc.terminate()
                try:
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()
                    proc.wait(timeout=3)
                time.sleep(0.3)

    def test_privacy_gitignore_and_no_secrets_in_repo_or_exe(self):
        gitignore_txt = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
        for req_entry in ("life_os.db", "*.xlsx", ".env", "!.env.example", "*.spec", "build/", "dist/"):
            self.assertIn(req_entry, gitignore_txt, f"Missing .gitignore rule: {req_entry}")

        secret_patterns = {
            "private_lan_ip": re.compile(r"\b192\.168\.\d+\.\d+\b"),
            "tg_token": re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{25,}\b"),
            "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
            "xai_key": re.compile(r"\bxai-[A-Za-z0-9_-]{20,}\b"),
            "gemini_key": re.compile(r"\bAIza[A-Za-z0-9_-]{20,}\b"),
            "discord_snowflake": re.compile(r"\b\d{17,20}\b"),
        }
        for p in PROJECT_ROOT.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in (".py", ".md", ".txt", ".example"):
                continue
            if any(part in p.parts for part in (".git", "__pycache__", "build", "dist")):
                continue
            txt = p.read_text(encoding="utf-8", errors="ignore")
            for label, pat in secret_patterns.items():
                self.assertIsNone(pat.search(txt), f"Unexpected {label} leak in {p.name}")

        exe_path = PROJECT_ROOT / "dist" / "LifeOS_Assistant_v2.exe"
        if exe_path.is_file():
            self.assertEqual(verify_clean_exe_bundle(exe_path), [])


def _read_pe_version_strings(exe_path: Path) -> dict:
    """Read ProductName & FileDescription from Windows PE Version Resource via version.dll."""
    if not sys.platform.startswith("win"):
        return {}
    import ctypes
    from ctypes import wintypes

    version_dll = ctypes.WinDLL("version")
    path_str = str(exe_path)
    handle = wintypes.DWORD(0)
    size = version_dll.GetFileVersionInfoSizeW(path_str, ctypes.byref(handle))
    if not size:
        return {}
    buf = ctypes.create_string_buffer(size)
    if not version_dll.GetFileVersionInfoW(path_str, 0, size, buf):
        return {}

    trans_ptr = ctypes.c_void_p()
    trans_len = wintypes.UINT(0)
    if not version_dll.VerQueryValueW(buf, "\\VarFileInfo\\Translation", ctypes.byref(trans_ptr), ctypes.byref(trans_len)):
        return {}
    if trans_len.value < 4:
        return {}
    arr = ctypes.cast(trans_ptr, ctypes.POINTER(wintypes.WORD))
    lang_hex = f"{arr[0]:04X}{arr[1]:04X}"

    out = {}
    for field in ("ProductName", "FileDescription", "OriginalFilename"):
        val_ptr = ctypes.c_void_p()
        val_len = wintypes.UINT(0)
        sub_block = f"\\StringFileInfo\\{lang_hex}\\{field}"
        if version_dll.VerQueryValueW(buf, sub_block, ctypes.byref(val_ptr), ctypes.byref(val_len)) and val_ptr.value:
            out[field] = ctypes.wstring_at(val_ptr.value)
    return out


class TestMultilingualAndLocaleSandbox(unittest.TestCase):
    """7. 4개 국어(ko/en/ja/zh) 다국어, 시스템 언어 샌드박스 시뮬레이션 및 빌드 앱 이름 회귀 테스트"""

    def test_os_locale_detection_and_fallbacks(self):
        env_cases = [
            ({"LANG": "ko_KR.UTF-8"}, "ko", "Life OS 습관 비서"),
            ({"LANG": "en_US.UTF-8"}, "en", "Life OS Habit Assistant"),
            ({"LC_ALL": "ja_JP.UTF-8"}, "ja", "Life OS 習慣アシスタント"),
            ({"LANG": "zh_CN.UTF-8"}, "zh", "Life OS 习惯助手"),
            ({"LANGUAGE": "zh_TW:en_US"}, "zh", "Life OS 习惯助手"),
            ({"LANG": "fr_FR.UTF-8"}, "en", "Life OS Habit Assistant"),
        ]
        for env_patch, expected_lang, expected_app in env_cases:
            clean_base = {k: "" for k in ("LIFE_OS_LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE", "LANG")}
            clean_base.update(env_patch)
            with patch.dict(os.environ, clean_base, clear=False):
                det = detect_system_language()
                self.assertEqual(det, expected_lang)
                self.assertEqual(get_app_name(det), expected_app)
                self.assertEqual(resolve_language("auto"), expected_lang)
                self.assertEqual(resolve_language("ja"), "ja")

        if sys.platform.startswith("win"):
            clean_env = {k: "" for k in ("LIFE_OS_LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE", "LANG")}
            with patch.dict(os.environ, clean_env, clear=False):
                for lcid, expected in ((0x0412, "ko"), (0x0409, "en"), (0x0411, "ja"), (0x0804, "zh"), (0x040C, "en")):
                    with patch("i18n.ctypes.windll.kernel32.GetUserDefaultUILanguage", return_value=lcid):
                        self.assertEqual(detect_system_language(), expected)

    def test_all_4_languages_35_habits_and_false_positive_guard(self):
        noise_inputs = [
            "dk", "asdf", "", "   ",
            "hello world how are you",
            "why did it rain today?",
            "오늘 점심 뭐 먹지",
            "いい天気ですね",
            "今天天气真好",
        ]
        for lang in ("ko", "en", "ja", "zh"):
            cat = get_habits_catalog(lang)
            self.assertEqual([h["id"] for h in cat], list(range(1, 36)))
            nlp = LocalHabitNLP(lang=lang)
            for h in cat:
                for kw in h["keywords"]:
                    matched, msg = nlp.analyze_checkin(f"Practiced {kw}", lang=lang)
                    self.assertIn(h["id"], matched, f"[{lang}] Habit {h['id']} missed keyword '{kw}'")
                    self.assertTrue(bool(msg.strip()))

            for noise in noise_inputs:
                if lang == "ko" and "why" in noise:
                    continue
                matched, _ = nlp.analyze_checkin(noise, lang=lang)
                self.assertEqual(matched, [], f"[{lang}] Noise '{noise}' falsely matched {matched}")

        # Cross-language check-in support while UI language differs
        en_ids, _ = LocalHabitNLP(lang="en").analyze_checkin("찬물샤워와 90분 딥워크 완료", lang="en")
        self.assertTrue({2, 7}.issubset(set(en_ids)))
        ko_ids, _ = LocalHabitNLP(lang="ko").analyze_checkin("15m morning sunlight and cold shower", lang="ko")
        self.assertTrue({6, 7}.issubset(set(ko_ids)))

    def test_excel_multilingual_generation_and_cross_language_sync(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for lang in ("ko", "en", "ja", "zh"):
                xlsx = tmp / f"Life_OS_{lang}.xlsx"
                build_life_os_workbook(str(xlsx), lang=lang)
                wb = openpyxl.load_workbook(xlsx, data_only=False)
                try:
                    expected_tabs = [
                        SHEET_TITLES[lang]["dashboard"],
                        SHEET_TITLES[lang]["db"],
                        SHEET_TITLES[lang]["tracker"],
                        SHEET_TITLES[lang]["review"],
                        SHEET_TITLES[lang]["log"],
                    ]
                    self.assertEqual(wb.sheetnames, expected_tabs)
                    formula_cnt = 0
                    for sname in wb.sheetnames:
                        for row in wb[sname].iter_rows(values_only=True):
                            for val in row:
                                if isinstance(val, str):
                                    for err in ("#DIV/0!", "#REF!", "#NAME?", "#VALUE!", "#N/A", "#NUM!"):
                                        self.assertNotIn(err, val)
                                    if val.startswith("="):
                                        formula_cnt += 1
                    self.assertGreaterEqual(formula_cnt, 90)
                finally:
                    wb.close()

            # Cross-language bidirectional sync: English UI <-> Japanese Excel workbook
            ja_xlsx = tmp / "Life_OS_ja.xlsx"
            db = DatabaseManager(db_path=tmp / "cross.db")
            db.set_setting("language", "en")
            db.set_setting("excel_path", str(ja_xlsx))
            today = datetime.date.today()
            today_str = today.isoformat()
            col_idx = 4 + today.weekday()

            db.toggle_check(today_str, 6, status=1)
            ok, msg = db.sync_to_excel()
            self.assertTrue(ok, msg)
            self.assertIn("Bidirectional Excel sync complete", msg)

            time.sleep(0.12)
            wb = openpyxl.load_workbook(ja_xlsx)
            ws_tr = wb[SHEET_TITLES["ja"]["tracker"]]
            ws_tr.cell(row=15 + 4, column=col_idx, value="✓")
            wb.save(ja_xlsx)
            wb.close()

            ok2, _ = db.sync_to_excel()
            self.assertTrue(ok2)
            checks = db.get_checks_for_date(today_str)
            self.assertEqual(checks.get(6, {}).get("status"), 1)
            self.assertEqual(checks.get(15, {}).get("status"), 1)

    def test_sandbox_cli_telegram_bridge_under_simulated_locales(self):
        # Test CLI subprocess in simulated English & Japanese OS environments inside sandbox
        for env_lang, exp_lang, checkin_txt, expected_hid in (
            ("en_US.UTF-8", "en", "cold shower and deep work 90 min done", 7),
            ("ja_JP.UTF-8", "ja", "朝日15分と冷水シャワー完了", 6),
            ("zh_CN.UTF-8", "zh", "晒太阳15分钟 洗冷水澡完成", 6),
        ):
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td)
                env = os.environ.copy()
                env["LIFE_OS_DATA_DIR"] = str(tmp)
                env["LANG"] = env_lang
                env["LC_ALL"] = env_lang
                res = subprocess.run(
                    [sys.executable, str(PROJECT_ROOT / "ai_secretary.py"), "--checkin", checkin_txt],
                    env=env, capture_output=True, text=True, encoding="utf-8"
                )
                self.assertEqual(res.returncode, 0, res.stderr)
                today_str = datetime.date.today().isoformat()
                db = DatabaseManager(db_path=tmp / "life_os.db")
                self.assertEqual(db.get_checks_for_date(today_str).get(expected_hid, {}).get("status"), 1)
                xlsx = tmp / "Life_OS_Successful_Habits.xlsx"
                self.assertTrue(xlsx.is_file())
                wb = openpyxl.load_workbook(xlsx, read_only=True)
                try:
                    self.assertEqual(wb.sheetnames[0], SHEET_TITLES[exp_lang]["dashboard"])
                finally:
                    wb.close()

        # Test TelegramBotRunner & BotBridgeServer in English / Japanese / Chinese settings
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            db = DatabaseManager(db_path=tmp / "bot_i18n.db")
            engine = AssistantEngine(db)
            tg = TelegramBotRunner("123:ABC", db, engine)

            db.set_setting("language", "en")
            engine.refresh_language()
            self.assertIn("Welcome to Life OS Habit Assistant", tg.handle_text_message("/start"))
            self.assertIn("Please include", tg.handle_text_message("/yesterday"))
            self.assertIn("Deep Work Block", tg.handle_text_message("90 min deep work done"))

            db.set_setting("language", "ja")
            engine.refresh_language()
            self.assertIn("ようこそ！Life OS 習慣アシスタント", tg.handle_text_message("/start"))
            self.assertIn("昨日の日付", tg.handle_text_message("/昨日"))
            y_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
            tg.handle_text_message("/昨日 感謝日記完了")
            self.assertEqual(db.get_checks_for_date(y_str).get(15, {}).get("status"), 1)

            bridge = BotBridgeServer(db, engine, host="127.0.0.1", port=0)
            ok, _ = bridge.start()
            self.assertTrue(ok)
            try:
                base = f"http://127.0.0.1:{bridge.port}"
                st = requests.get(f"{base}/stats", timeout=5).json()
                self.assertEqual(st["language"], "ja")
                hb = requests.get(f"{base}/habits", timeout=5).json()
                self.assertEqual(hb["language"], "ja")
                self.assertEqual(hb["count"], 35)
            finally:
                bridge.stop()

    def test_widget_live_language_switch_and_tray(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            db = DatabaseManager(db_path=tmp / "ui_i18n.db")
            db.set_setting("language", "en")
            db.set_setting("sound_enabled", "false")
            db.set_setting("toast_enabled", "false")
            db.set_setting("excel_path", str(tmp / "Life_OS_Successful_Habits.xlsx"))
            engine = AssistantEngine(db)

            tray_updates = []
            tray = SystemTrayManager(lang_getter=db.get_language)
            tray.update_language("en")  # Safe no-op before icon.run

            root = tk.Tk()
            widget = FloatingAssistantWidget(
                root, db, engine,
                on_language_changed=lambda nl: (tray_updates.append(nl), tray.update_language(nl))
            )
            try:
                root.update()
                self.assertEqual(root.title(), "Life OS Habit Assistant")
                self.assertEqual(widget.btn_done.cget("text"), tr("btn_done", "en"))

                # Settings dialog includes language dropdown
                set_win = widget.open_settings_dialog()
                self.assertIn("auto", [c for c, _ in set_win._lang_options])
                set_win.destroy()

                # Bot settings warning in English
                widget.open_bot_settings_dialog()
                self.assertTrue(widget._bot_settings_win.winfo_exists())
                widget._bot_settings_win.destroy()

                # Hot-switch live to Japanese
                db.set_setting("language", "ja")
                widget.apply_language_change()
                root.update()
                self.assertEqual(root.title(), "Life OS 習慣アシスタント")
                self.assertEqual(widget.btn_done.cget("text"), tr("btn_done", "ja"))
                self.assertIn("ja", tray_updates)

                # Hot-switch live to Chinese
                db.set_setting("language", "zh")
                widget.apply_language_change()
                root.update()
                self.assertEqual(root.title(), "Life OS 习惯助手")
                self.assertEqual(widget.btn_done.cget("text"), tr("btn_done", "zh"))
            finally:
                root.destroy()

    def test_build_exe_localized_version_metadata_and_sandbox_exe_locales(self):
        # 1. Verify PE VSVersionInfo file generator produces valid metadata for all 4 languages
        with tempfile.TemporaryDirectory() as td:
            from PyInstaller.utils.win32 import versioninfo
            for lang in ("ko", "en", "ja", "zh"):
                vfile = generate_version_info_file(Path(td) / f"ver_{lang}.txt", lang)
                txt = vfile.read_text(encoding="utf-8")
                self.assertIn(get_app_name(lang), txt)
                if sys.platform.startswith("win"):
                    parsed = eval(txt, {
                        "VSVersionInfo": versioninfo.VSVersionInfo,
                        "FixedFileInfo": versioninfo.FixedFileInfo,
                        "StringFileInfo": versioninfo.StringFileInfo,
                        "StringTable": versioninfo.StringTable,
                        "StringStruct": versioninfo.StringStruct,
                        "VarFileInfo": versioninfo.VarFileInfo,
                        "VarStruct": versioninfo.VarStruct,
                    })
                    self.assertIsNotNone(parsed)

        exe_path = PROJECT_ROOT / "dist" / "LifeOS_Assistant_v2.exe"
        self.assertTrue(exe_path.is_file(), f"Executable missing: {exe_path}")

        # 2. Verify compiled EXE PE ProductName matches host build system language
        if sys.platform.startswith("win"):
            clean_env = {k: "" for k in ("LIFE_OS_LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE", "LANG")}
            with patch.dict(os.environ, clean_env, clear=False):
                host_lang = detect_system_language()
            pe_meta = _read_pe_version_strings(exe_path)
            self.assertEqual(pe_meta.get("ProductName"), get_app_name(host_lang))
            self.assertEqual(pe_meta.get("OriginalFilename"), "LifeOS_Assistant_v2.exe")

        # 3. Boot compiled .exe inside sandbox under simulated English & Japanese system locales
        for env_lang, exp_lang, exp_persona, checkin_msg, exp_hid in (
            ("en_US.UTF-8", "en", "Dr. Andrew Huberman", "15m morning sunlight and cold shower", 6),
            ("ja_JP.UTF-8", "ja", "アンドリュー・フーバーマン博士", "朝日15分と冷水シャワー完了", 7),
        ):
            port = find_free_port()
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td)
                db = DatabaseManager(db_path=tmp / "life_os.db")
                db.set_setting("language", "auto")
                db.set_setting("webhook_enabled", "true")
                db.set_setting("webhook_host", "127.0.0.1")
                db.set_setting("webhook_port", str(port))
                db.set_setting("sound_enabled", "false")
                db.set_setting("toast_enabled", "false")
                db.set_setting("telegram_enabled", "false")

                env = os.environ.copy()
                env["LIFE_OS_DATA_DIR"] = str(tmp)
                env["LANG"] = env_lang
                env["LC_ALL"] = env_lang

                proc = subprocess.Popen([str(exe_path)], env=env)
                try:
                    ready = False
                    for _ in range(30):
                        if proc.poll() is not None:
                            self.fail(f"EXE exited early ({env_lang}) code={proc.returncode}")
                        try:
                            r = requests.get(f"http://127.0.0.1:{port}/stats", timeout=1)
                            if r.status_code == 200:
                                ready = True
                                self.assertEqual(r.json().get("language"), exp_lang)
                                self.assertEqual(r.json().get("persona"), exp_persona)
                                break
                        except Exception:
                            time.sleep(0.5)
                    self.assertTrue(ready, f"EXE webhook timeout in {env_lang}")

                    r_post = requests.post(
                        f"http://127.0.0.1:{port}/checkin",
                        json={"message": checkin_msg, "channel": f"Sandbox-{exp_lang}"},
                        timeout=8,
                    )
                    self.assertEqual(r_post.status_code, 200)
                    self.assertIn(exp_hid, r_post.json()["data"]["matched_ids"])

                    xlsx_out = tmp / "Life_OS_Successful_Habits.xlsx"
                    self.assertTrue(xlsx_out.is_file())
                    wb = openpyxl.load_workbook(xlsx_out, read_only=True)
                    try:
                        self.assertEqual(wb.sheetnames[0], SHEET_TITLES[exp_lang]["dashboard"])
                        self.assertEqual(wb.sheetnames[2], SHEET_TITLES[exp_lang]["tracker"])
                    finally:
                        wb.close()
                finally:
                    if sys.platform.startswith("win"):
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
                    else:
                        proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except Exception:
                        proc.kill()
                        proc.wait(timeout=3)
                    time.sleep(0.3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
