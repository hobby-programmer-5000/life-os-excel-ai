"""
=============================================================================
💾 ALL-IN-ONE LIFE OS : SQLite Timeline Database & Dual Excel Synchronizer
=============================================================================
과거-현재-미래 날짜 탐색(Date Traversal) 및 습관/일지/설정 영구 보관
엑셀(Life_OS_Successful_Habits.xlsx) 양방향 자동 동기화 지원
=============================================================================
"""

import os
import sys
import json
import sqlite3
import datetime
import threading
import subprocess
import contextlib
from pathlib import Path
import openpyxl
from i18n import resolve_language, tr, SHEET_CANDIDATES

EXCEL_LOCK = threading.RLock()

# Cross-platform Base Directory Resolution (PyInstaller & cloned repo portable)
def resolve_base_dir():
    env_dir = os.getenv("LIFE_OS_DATA_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).resolve().parent
        # When launched from repo's dist/ subfolder, share the project root DB & Excel
        if exe_dir.name.lower() == "dist" and (
            (exe_dir.parent / "main_app.py").is_file()
            or (exe_dir.parent / "life_os.db").is_file()
            or (exe_dir.parent / "Life_OS_Successful_Habits.xlsx").is_file()
        ):
            return exe_dir.parent
        for cand in (exe_dir, exe_dir.parent):
            if (cand / "Life_OS_Successful_Habits.xlsx").is_file() or (cand / "life_os.db").is_file():
                return cand
        return exe_dir
    return Path(__file__).resolve().parent

BASE_DIR = resolve_base_dir()
DB_PATH = BASE_DIR / "life_os.db"
DEFAULT_EXCEL_PATH = BASE_DIR / "Life_OS_Successful_Habits.xlsx"

def load_env_file(env_path: Path = None):
    """Lightweight zero-dependency .env loader into os.environ."""
    target = env_path or (BASE_DIR / ".env")
    if not target.exists():
        return
    try:
        for line in target.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except Exception:
        pass

load_env_file()

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)
        self._init_db()

    @contextlib.contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute("PRAGMA journal_mode=WAL;")
            except Exception:
                pass
            # Master 35 Habits table (Self-contained relational catalog inside SQLite)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                keywords_json TEXT DEFAULT '[]',
                is_active INTEGER DEFAULT 1
            )
            """)

            # Daily checks table (check_date: YYYY-MM-DD, habit_id: 1..35, status: 0 or 1)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_checks (
                check_date TEXT NOT NULL,
                habit_id INTEGER NOT NULL,
                status INTEGER DEFAULT 1,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (check_date, habit_id)
            )
            """)

            # Daily logs and future notes table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_logs (
                log_date TEXT PRIMARY KEY,
                summary_text TEXT,
                ai_coaching TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Settings key-value store
            cur.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """)

            # Default settings (portable relative paths by default)
            defaults = {
                "autostart_enabled": "false",
                "close_to_tray": "true",
                "always_on_top": "true",
                "opacity": "0.94",
                "nudge_interval_minutes": "45",
                "sound_enabled": "true",
                "toast_enabled": "true",
                "persona": "huberman",
                "language": "auto",
                "excel_path": "",
                "auto_sync_excel": "true",
                "quick_view_mode": "custom",
                "quick_habit_limit": "5",
                "webhook_enabled": "false",
                "webhook_host": "127.0.0.1",
                "webhook_port": "8080",
                "telegram_enabled": "false",
                "telegram_token": "",
                "discord_enabled": "false",
                "discord_token": "",
                "discord_channel_id": "",
                "db_sync_seq": "0",
                "last_remote_event": "",
                "sync_baseline": ""
            }
            for k, v in defaults.items():
                cur.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?)", (k, v))
            conn.commit()

    def seed_habits(self, catalog: list):
        """Seed or update the 35 master habits catalog inside SQLite."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            for h in catalog:
                cur.execute("""
                INSERT OR REPLACE INTO habits (id, category, name, keywords_json, is_active)
                VALUES (?, ?, ?, ?, 1)
                """, (
                    int(h["id"]),
                    str(h["category"]),
                    str(h["name"]),
                    json.dumps(h.get("keywords", []), ensure_ascii=False)
                ))
            conn.commit()

    def get_habits(self) -> list:
        """Load habits catalog directly from SQLite."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, category, name, keywords_json FROM habits WHERE is_active = 1 ORDER BY id")
            rows = cur.fetchall()
            out = []
            for hid, cat, name, kw_raw in rows:
                try:
                    kws = json.loads(kw_raw or "[]")
                except Exception:
                    kws = []
                out.append({"id": hid, "category": cat, "name": name, "keywords": kws})
            return out

    def import_from_excel(self, excel_path: str = None) -> int:
        """Migrate existing checks from Excel tracker sheet (Mon-Sun) into SQLite if missing."""
        target_path = self._resolve_excel_target(excel_path, auto_create=False)
        if not target_path.exists():
            return 0
        imported = 0
        with EXCEL_LOCK:
            wb = None
            try:
                wb = openpyxl.load_workbook(target_path, data_only=True)
                ws = self._find_sheet(wb, "tracker")
                if ws is None:
                    return 0
                today = datetime.date.today()
                start_of_week = today - datetime.timedelta(days=today.weekday())
                with self._get_connection() as conn:
                    cur = conn.cursor()
                    for day_offset in range(7):
                        d_str = (start_of_week + datetime.timedelta(days=day_offset)).isoformat()
                        col_idx = 4 + day_offset
                        for habit_id in range(1, 36):
                            val = ws.cell(row=habit_id + 4, column=col_idx).value
                            if val == 1:
                                cur.execute("""
                                INSERT OR IGNORE INTO daily_checks (check_date, habit_id, status, memo)
                                VALUES (?, ?, 1, 'Imported from Excel')
                                """, (d_str, habit_id))
                                if cur.rowcount > 0:
                                    imported += 1
                    conn.commit()
            except Exception:
                return imported
            finally:
                if wb is not None:
                    try:
                        wb.close()
                    except Exception:
                        pass
        return imported

    def open_excel_file(self):
        """Open the target Excel file on Windows, macOS, or Linux."""
        lang = self.get_language()
        target_path = self._resolve_excel_target(auto_create=True)
        if not target_path.exists():
            return False, tr("db_excel_not_found", lang, path=target_path)

        try:
            if sys.platform.startswith("win"):
                os.startfile(str(target_path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(target_path)])
            else:
                subprocess.Popen(["xdg-open", str(target_path)])
            return True, tr("db_excel_open_ok", lang, name=target_path.name)
        except Exception as e:
            return False, tr("db_excel_open_err", lang, err=e)

    def get_language(self) -> str:
        """Resolve active UI/bot language ('ko', 'en', 'ja', 'zh') from DB setting or OS locale."""
        return resolve_language(self.get_setting("language", "auto"))

    @staticmethod
    def _find_sheet(wb, kind: str):
        """Find worksheet regardless of the language the workbook was originally generated in."""
        for name in SHEET_CANDIDATES.get(kind, []):
            if name in wb.sheetnames:
                return wb[name]
        idx_map = {"dashboard": 0, "db": 1, "tracker": 2, "review": 3, "log": 4}
        if len(wb.sheetnames) >= 5 and kind in idx_map:
            return wb[wb.sheetnames[idx_map[kind]]]
        return None
    def get_setting(self, key: str, default=None):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else default

    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()

    def _bump_sync_seq(self, conn=None):
        """Increment db_sync_seq atomically so desktop widget detects remote/bot updates."""
        if conn is None:
            with self._get_connection() as c:
                return self._bump_sync_seq(c)
        cur = conn.cursor()
        cur.execute("SELECT value FROM app_settings WHERE key = 'db_sync_seq'")
        row = cur.fetchone()
        next_seq = int(row[0]) + 1 if row and str(row[0]).isdigit() else 1
        cur.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('db_sync_seq', ?)", (str(next_seq),))
        return next_seq

    def record_remote_checkin_event(self, channel: str, message: str, coaching: str, matched_ids: list):
        payload = json.dumps({
            "channel": channel,
            "message": message,
            "coaching": coaching,
            "matched_ids": matched_ids,
            "timestamp": datetime.datetime.now().isoformat()
        }, ensure_ascii=False)
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('last_remote_event', ?)", (payload,))
            self._bump_sync_seq(conn)
            conn.commit()

    def get_sync_state(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM app_settings WHERE key IN ('db_sync_seq', 'last_remote_event')")
            rows = dict(cur.fetchall())
            seq = int(rows.get("db_sync_seq", "0")) if str(rows.get("db_sync_seq", "0")).isdigit() else 0
            raw_evt = rows.get("last_remote_event", "")
            evt = None
            if raw_evt:
                try:
                    evt = json.loads(raw_evt)
                except Exception:
                    evt = None
            return seq, evt

    # --- Habit Checks APIs ---
    def get_checks_for_date(self, date_str: str) -> dict:
        """Returns {habit_id: {'status': int, 'memo': str}} for given date (YYYY-MM-DD)"""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT habit_id, status, memo FROM daily_checks WHERE check_date = ?", (date_str,))
            rows = cur.fetchall()
            return {r[0]: {"status": r[1], "memo": r[2] or ""} for r in rows}

    def toggle_check(self, date_str: str, habit_id: int, status: int = None, memo: str = None):
        """Toggle or set status for habit on date_str"""
        with self._get_connection() as conn:
            cur = conn.cursor()
            if status is None:
                cur.execute("SELECT status FROM daily_checks WHERE check_date = ? AND habit_id = ?", (date_str, habit_id))
                row = cur.fetchone()
                current = row[0] if row else 0
                status = 0 if current == 1 else 1

            cur.execute("""
            INSERT OR REPLACE INTO daily_checks (check_date, habit_id, status, memo, created_at)
            VALUES (?, ?, ?, COALESCE(?, (SELECT memo FROM daily_checks WHERE check_date = ? AND habit_id = ?)), CURRENT_TIMESTAMP)
            """, (date_str, habit_id, status, memo, date_str, habit_id))
            self._bump_sync_seq(conn)
            conn.commit()
            return status

    def get_uncompleted_habits_for_date(self, date_str: str) -> list:
        """Returns list of habit IDs (1..35) that are not completed on date_str"""
        checks = self.get_checks_for_date(date_str)
        uncompleted = []
        for hid in range(1, 36):
            if checks.get(hid, {}).get("status", 0) != 1:
                uncompleted.append(hid)
        return uncompleted

    def get_weekly_stats(self, ref_date: datetime.date = None) -> dict:
        """Calculate completed habits and rate for the current Mon-Sun week from SQLite."""
        today = ref_date or datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM daily_checks WHERE check_date >= ? AND check_date <= ? AND status = 1",
                (start_of_week.isoformat(), end_of_week.isoformat())
            )
            completed_count = cur.fetchone()[0]

        today_checks = self.get_checks_for_date(today.isoformat())
        today_done = sum(1 for hid in range(1, 36) if today_checks.get(hid, {}).get("status", 0) == 1)
        total_slots = 35 * 7
        rate = (completed_count / total_slots) * 100 if total_slots else 0.0
        return {
            "week_start": start_of_week.isoformat(),
            "week_end": end_of_week.isoformat(),
            "completed_count": completed_count,
            "total_slots": total_slots,
            "weekly_rate": round(rate, 1),
            "today_date": today.isoformat(),
            "today_completed": today_done
        }

    # --- Daily Log / Future Plan APIs ---
    def get_log_for_date(self, date_str: str) -> dict:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT summary_text, ai_coaching FROM daily_logs WHERE log_date = ?", (date_str,))
            row = cur.fetchone()
            if row:
                return {"summary_text": row[0] or "", "ai_coaching": row[1] or ""}
            return {"summary_text": "", "ai_coaching": ""}

    def save_log_for_date(self, date_str: str, summary_text: str = None, ai_coaching: str = None):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT OR REPLACE INTO daily_logs (log_date, summary_text, ai_coaching, updated_at)
            VALUES (?, 
                    COALESCE(?, (SELECT summary_text FROM daily_logs WHERE log_date = ?)),
                    COALESCE(?, (SELECT ai_coaching FROM daily_logs WHERE log_date = ?)),
                    CURRENT_TIMESTAMP)
            """, (date_str, summary_text, date_str, ai_coaching, date_str))
            conn.commit()

    def _resolve_excel_target(self, excel_path: str = None, auto_create: bool = True) -> Path:
        sibling_excel = self.db_path.parent / "Life_OS_Successful_Habits.xlsx"
        if excel_path is not None and str(excel_path).strip():
            target_path = Path(str(excel_path).strip())
        else:
            stored = str(self.get_setting("excel_path", "") or "").strip()
            if stored:
                cand = Path(stored)
                target_path = cand if (cand.is_file() or cand.parent.is_dir()) else sibling_excel
            else:
                target_path = sibling_excel

        if not target_path.is_file() and auto_create:
            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                from generate_excel import build_life_os_workbook
                build_life_os_workbook(str(target_path), lang=self.get_language())
            except Exception:
                pass
        return target_path

    # --- Bidirectional 3-Way Excel <-> SQLite Synchronization ---
    @staticmethod
    def _cell_to_flag(val) -> int:
        if val is True or val == 1 or val == 1.0:
            return 1
        if isinstance(val, str) and val.strip().lower() in ("1", "1.0", "o", "v", "✓", "✅", "true"):
            return 1
        return 0

    def _get_week_dates(self, ref_date: datetime.date = None):
        today = ref_date or datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        return start_of_week, [(start_of_week + datetime.timedelta(days=i)).isoformat() for i in range(7)]

    def _get_week_matrix_from_sqlite(self, week_dates: list) -> dict:
        matrix = {}
        for d_str in week_dates:
            checks = self.get_checks_for_date(d_str)
            for hid in range(1, 36):
                if checks.get(hid, {}).get("status", 0) == 1:
                    matrix[f"{d_str}:{hid}"] = 1
        return matrix

    def _load_baseline(self) -> dict:
        raw = self.get_setting("sync_baseline", "")
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def _save_baseline(self, week_start_str: str, matrix: dict, excel_mtime: float):
        self.set_setting("sync_baseline", json.dumps({
            "week_start": week_start_str,
            "excel_mtime": float(excel_mtime),
            "matrix": matrix
        }))

    def _pull_excel_changes_locked(self, target_path: Path) -> int:
        """Read Excel tracker and 3-way merge any manual Excel edits into SQLite."""
        if not target_path.is_file():
            return 0
        start_of_week, week_dates = self._get_week_dates()
        week_start_str = start_of_week.isoformat()
        baseline = self._load_baseline()
        has_week_baseline = (baseline.get("week_start") == week_start_str) and isinstance(baseline.get("matrix"), dict)
        b_matrix = baseline.get("matrix", {}) if has_week_baseline else {}

        wb = openpyxl.load_workbook(target_path, read_only=True, data_only=False)
        try:
            ws = self._find_sheet(wb, "tracker")
            if ws is None:
                return 0
            excel_matrix = {}
            for row_idx, row_vals in enumerate(ws.iter_rows(min_row=5, max_row=39, min_col=4, max_col=10, values_only=True), start=5):
                hid = row_idx - 4
                for day_offset, val in enumerate(row_vals):
                    if self._cell_to_flag(val) == 1:
                        excel_matrix[f"{week_dates[day_offset]}:{hid}"] = 1
        finally:
            wb.close()

        sqlite_matrix = self._get_week_matrix_from_sqlite(week_dates)
        changes = 0
        with self._get_connection() as conn:
            cur = conn.cursor()
            for d_str in week_dates:
                for hid in range(1, 36):
                    key = f"{d_str}:{hid}"
                    e_val = excel_matrix.get(key, 0)
                    s_val = sqlite_matrix.get(key, 0)
                    if has_week_baseline:
                        b_val = b_matrix.get(key, 0)
                        if e_val != b_val and e_val != s_val:
                            cur.execute("""
                            INSERT OR REPLACE INTO daily_checks (check_date, habit_id, status, memo, created_at)
                            VALUES (?, ?, ?, 'Synced from Excel', CURRENT_TIMESTAMP)
                            """, (d_str, hid, e_val))
                            changes += 1
                    else:
                        if e_val == 1 and s_val == 0:
                            cur.execute("""
                            INSERT OR REPLACE INTO daily_checks (check_date, habit_id, status, memo, created_at)
                            VALUES (?, ?, 1, 'Synced from Excel', CURRENT_TIMESTAMP)
                            """, (d_str, hid))
                            changes += 1
            if changes > 0:
                self._bump_sync_seq(conn)

        merged_matrix = self._get_week_matrix_from_sqlite(week_dates)
        try:
            mtime = target_path.stat().st_mtime
        except Exception:
            mtime = 0.0
        self._save_baseline(week_start_str, merged_matrix, mtime)
        return changes

    def sync_from_excel(self, excel_path: str = None) -> tuple:
        """Manually pull external changes from Excel into SQLite."""
        lang = self.get_language()
        target_path = self._resolve_excel_target(excel_path, auto_create=False)
        if not target_path.is_file():
            return False, 0, tr("db_excel_not_found", lang, path=target_path)
        with EXCEL_LOCK:
            try:
                changes = self._pull_excel_changes_locked(target_path)
                return True, changes, tr("db_from_excel_ok", lang, changes=changes)
            except PermissionError:
                return False, 0, tr("db_sync_locked", lang)
            except Exception as e:
                return False, 0, tr("db_from_excel_err", lang, err=e)

    def check_and_pull_excel_if_modified(self, excel_path: str = None) -> tuple:
        """Fast stat-check: pull from Excel into SQLite only if Excel file mtime advanced externally."""
        target_path = self._resolve_excel_target(excel_path, auto_create=False)
        if not target_path.is_file():
            return False, 0
        baseline = self._load_baseline()
        last_mtime = float(baseline.get("excel_mtime", 0.0) or 0.0)
        try:
            cur_mtime = target_path.stat().st_mtime
        except Exception:
            return False, 0
        if last_mtime > 0.0 and cur_mtime <= last_mtime + 0.05:
            return False, 0
        ok, changes, _ = self.sync_from_excel(str(target_path))
        return ok, changes

    def sync_to_excel(self, excel_path: str = None, log_entry: dict = None):
        """Bidirectional sync: merge any newer Excel edits into SQLite, then write SQLite week -> Excel."""
        lang = self.get_language()
        target_path = self._resolve_excel_target(excel_path, auto_create=True)
        if not target_path.exists():
            return False, tr("db_excel_not_found", lang, path=target_path)

        with EXCEL_LOCK:
            wb = None
            try:
                # 1. Preserve manual Excel edits if Excel was modified externally since last sync
                baseline = self._load_baseline()
                last_mtime = float(baseline.get("excel_mtime", 0.0) or 0.0)
                cur_mtime = target_path.stat().st_mtime
                pulled_count = 0
                if not baseline or cur_mtime > last_mtime + 0.05:
                    pulled_count = self._pull_excel_changes_locked(target_path)

                # 2. Write authoritative merged SQLite week state back to Excel
                wb = openpyxl.load_workbook(target_path)
                ws_track = self._find_sheet(wb, "tracker")
                if ws_track is None:
                    return False, tr("db_excel_not_found", lang, path=target_path)

                start_of_week, week_dates = self._get_week_dates()
                for day_offset, cur_date_str in enumerate(week_dates):
                    col_idx = 4 + day_offset  # Col D=Mon, ..., J=Sun
                    checks = self.get_checks_for_date(cur_date_str)
                    for habit_id in range(1, 36):
                        row_idx = habit_id + 4  # Habit 1 is row 5
                        is_checked = checks.get(habit_id, {}).get("status", 0) == 1
                        ws_track.cell(row=row_idx, column=col_idx, value=1 if is_checked else "")

                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                # Update dashboard status
                ws_dash = self._find_sheet(wb, "dashboard")
                if ws_dash is not None:
                    if log_entry:
                        matched = log_entry.get("matched_names") or []
                        hdr = tr("db_dash_coaching_hdr", lang, channel=log_entry.get("channel", "App"), ts=now_str)
                        ref = tr("db_dash_coaching_ref", lang, habits=", ".join(matched) if matched else tr("db_dash_no_habit", lang))
                        ws_dash["B19"].value = f"{hdr}\n\n{log_entry.get('coaching', '')}\n\n{ref}"
                    else:
                        extra = tr("db_dash_pulled_extra", lang, count=pulled_count) if pulled_count else ""
                        hdr = tr("db_dash_sync_hdr", lang, extra=extra, ts=now_str)
                        ws_dash["B19"].value = f"{hdr}\n\n{tr('db_dash_sync_body', lang)}"

                # Append to AI Bot Integration Log sheet when check-in event occurred
                ws_log = self._find_sheet(wb, "log")
                if log_entry and ws_log is not None:
                    next_row = ws_log.max_row + 1
                    matched = log_entry.get("matched_names") or []
                    ws_log.cell(row=next_row, column=2, value=now_str)
                    ws_log.cell(row=next_row, column=3, value=log_entry.get("channel", "Desktop Widget"))
                    ws_log.cell(row=next_row, column=4, value=log_entry.get("message", ""))
                    ws_log.cell(row=next_row, column=5, value=tr("db_log_matched", lang, count=len(matched), names=", ".join(matched[:3])))
                    ws_log.cell(row=next_row, column=6, value=log_entry.get("coaching", ""))
                    ws_log.cell(row=next_row, column=7, value=tr("db_log_status_ok", lang))

                wb.save(target_path)
                new_mtime = target_path.stat().st_mtime
                merged_matrix = self._get_week_matrix_from_sqlite(week_dates)
                self._save_baseline(start_of_week.isoformat(), merged_matrix, new_mtime)

                suffix = tr("db_sync_pulled", lang, count=pulled_count) if pulled_count else ""
                return True, tr("db_sync_ok", lang, name=target_path.name, suffix=suffix)
            except PermissionError:
                return False, tr("db_sync_locked", lang)
            except Exception as e:
                return False, tr("db_sync_err", lang, err=e)
            finally:
                if wb is not None:
                    try:
                        wb.close()
                    except Exception:
                        pass

    def write_weekly_review_to_excel(self, report_text: str, excel_path: str = None):
        lang = self.get_language()
        target_path = self._resolve_excel_target(excel_path)
        if not target_path.exists():
            return False, tr("db_excel_not_found", lang, path=target_path)
        with EXCEL_LOCK:
            wb = None
            try:
                wb = openpyxl.load_workbook(target_path)
                ws_rev = self._find_sheet(wb, "review")
                if ws_rev is not None:
                    ws_rev["B17"].value = report_text
                wb.save(target_path)
                return True, tr("db_rev_ok", lang, name=target_path.name)
            except PermissionError:
                return False, tr("db_rev_locked", lang)
            except Exception as e:
                return False, tr("db_rev_err", lang, err=e)
            finally:
                if wb is not None:
                    try:
                        wb.close()
                    except Exception:
                        pass
