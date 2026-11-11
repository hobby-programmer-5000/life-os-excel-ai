"""
=============================================================================
🤖 ALL-IN-ONE LIFE OS : Proactive Assistant Engine & OS Integration
=============================================================================
1. 스마트 랜덤 넛지 (Nudge) 생성기 (시간대별 미완료 습관 스마트 필터링 & 4개 국어 지원)
2. 3-상태 응답 상태 머신 ([✅ 완료], [🚀 지금 할게], [⏸️ 일단 보류])
3. 100% 오프라인 다국어 자연어 일과 분석 및 습관 매핑 (Local Multilingual NLP)
4. 윈도우 시작프로그램(Registry) 다국어 이름 동기화 컨트롤러
=============================================================================
"""

import os
import sys
import random
import datetime

from ai_secretary import LocalHabitNLP
from i18n import tr, get_autostart_reg_name, ALL_AUTOSTART_REG_NAMES
from i18n_habits import get_habits_catalog
from i18n_personas import get_personas

# Exported default personas catalog for backward compatibility
PERSONAS = get_personas()

# Habits anchored to specific times of day (24h local clock) so out-of-window
# nudges (e.g., asking pre-bed/evening routines at 03:00 AM) are never surfaced.
# Habits absent from this table are timeless and participate in random selection anytime.
HABIT_ALLOWED_HOURS = {
    5: set(range(6, 12)),                         # 오전 고부가가치 의사결정 (06~11시)
    6: set(range(5, 12)),                         # 기상 직후 아침 자연광 15분 (05~11시)
    7: set(range(5, 22)),                         # 찬물 샤워 / 냉수욕 (05~21시, 한밤중 수면 방해 회피)
    8: {20, 21, 22, 23},                          # 취침 1시간 전 디지털 디톡스 (20~23시)
    9: {19, 20, 21, 22, 23},                      # 8~9시간 완전 수면 환경 구축 (19~23시)
    15: {19, 20, 21, 22, 23},                     # 잠들기 전 매일 5가지 감사일기 (19~23시)
    16: set(range(4, 10)),                        # 새벽 4시 기상 & 집필 루틴 (04~09시)
    33: set(range(5, 12)) | {18, 19, 20, 21, 22}, # 아침 자문 & 저녁 회고 (05~11시 / 18~22시)
    34: {17, 18, 19, 20, 21},                     # 저녁 셧다운 의식 (17~21시)
}


def is_habit_suitable_for_hour(habit_id: int, hour: int) -> bool:
    """Return True if habit_id has no time-of-day restriction or matches hour (0..23)."""
    allowed = HABIT_ALLOWED_HOURS.get(habit_id)
    return True if allowed is None else (int(hour) in allowed)


class AssistantEngine:
    def __init__(self, db_manager, nlp_client=None):
        self.db = db_manager
        self._explicit_nlp = nlp_client
        self.nlp = nlp_client or LocalHabitNLP(lang=self.get_language())
        self.db.seed_habits(self.habits)
        if self.db.get_setting("migrated_excel_to_sqlite", "false") != "true":
            self.db.import_from_excel()
            self.db.set_setting("migrated_excel_to_sqlite", "true")

    def get_language(self) -> str:
        return self.db.get_language()

    @property
    def habits(self) -> list:
        return get_habits_catalog(self.get_language())

    def refresh_language(self):
        """Re-seed SQLite habits master table for the active language."""
        self.db.seed_habits(self.habits)

    def _get_nlp(self):
        if self._explicit_nlp:
            return self._explicit_nlp
        return LocalHabitNLP(lang=self.get_language())

    def get_current_persona(self) -> dict:
        lang = self.get_language()
        personas = get_personas(lang)
        key = self.db.get_setting("persona", "huberman")
        return personas.get(key, personas["huberman"])

    def get_smart_nudge(self, target_date_str: str = None, now_hour: int = None):
        """Pick an uncompleted habit suited for the current time of day and generate a localized nudge."""
        today_str = datetime.date.today().isoformat()
        if not target_date_str:
            target_date_str = today_str

        lang = self.get_language()
        persona = self.get_current_persona()
        habits = self.habits

        uncompleted_ids = self.db.get_uncompleted_habits_for_date(target_date_str)
        if not uncompleted_ids:
            return {
                "habit_id": None,
                "habit_name": tr("all_done_title", lang),
                "question": tr("all_done_nudge", lang, persona=persona["name"]),
                "all_done": True,
                "persona_name": persona["name"],
                "persona_emoji": persona["emoji"],
            }

        hour = datetime.datetime.now().hour if now_hour is None else (int(now_hour) % 24)
        candidates = [h for h in habits if h["id"] in uncompleted_ids]
        apply_time_filter = (now_hour is not None) or (target_date_str == today_str)

        if apply_time_filter:
            eligible = [h for h in candidates if is_habit_suitable_for_hour(h["id"], hour)]
            if not eligible:
                return {
                    "habit_id": None,
                    "habit_name": tr("window_done_title", lang),
                    "question": tr(
                        "window_done_nudge", lang,
                        persona=persona["name"], remaining=len(candidates),
                    ),
                    "all_done": True,
                    "window_done": True,
                    "persona_name": persona["name"],
                    "persona_emoji": persona["emoji"],
                }
        else:
            eligible = candidates

        selected = random.choice(eligible)
        template = random.choice(persona["nudge_templates"])
        question = template.replace("{name}", selected["name"])

        return {
            "habit_id": selected["id"],
            "habit_name": selected["name"],
            "category": selected["category"],
            "question": f"[{persona['name']}]\n\"{question}\"",
            "all_done": False,
            "persona_name": persona["name"],
            "persona_emoji": persona["emoji"],
        }

    def process_nudge_response(self, habit_id: int, response_type: str, date_str: str = None):
        if not date_str:
            date_str = datetime.date.today().isoformat()

        lang = self.get_language()
        persona = self.get_current_persona()
        habit = next((h for h in self.habits if h["id"] == habit_id), None)
        h_name = habit["name"] if habit else tr("habit_fallback_name", lang, hid=habit_id)

        if response_type == "completed":
            self.db.toggle_check(date_str, habit_id, status=1)
            if self.db.get_setting("auto_sync_excel") == "true":
                self.db.sync_to_excel()

            praise = random.choice(persona["praise_templates"]).replace("{name}", h_name)
            return {"status": "completed", "message": f"[{persona['name']}]\n\"{praise}\""}

        elif response_type == "doing_now":
            enc = random.choice(persona["doing_now_templates"]).replace("{name}", h_name)
            return {"status": "doing_now", "message": f"[{persona['name']}]\n\"{enc}\""}

        elif response_type == "postponed":
            delay = random.choice(persona["postpone_templates"]).replace("{name}", h_name)
            return {"status": "postponed", "message": f"[{persona['name']}]\n\"{delay}\""}

        return {"status": "unknown", "message": tr("unknown_response", lang)}

    def process_natural_checkin(self, text: str, date_str: str = None, channel: str = "Desktop Widget"):
        if not date_str:
            date_str = datetime.date.today().isoformat()

        lang = self.get_language()
        persona = self.get_current_persona()
        habits = self.habits

        nlp_client = self._get_nlp()
        try:
            matched_ids, base_coaching = nlp_client.analyze_checkin(text, lang=lang)
        except TypeError:
            matched_ids, base_coaching = nlp_client.analyze_checkin(text)

        checked_names = []
        for hid in matched_ids:
            self.db.toggle_check(date_str, hid, status=1)
            h = next((x for x in habits if x["id"] == hid), None)
            if h:
                checked_names.append(h["name"])

        if matched_ids:
            h_sample = checked_names[0] if checked_names else tr("default_habit_sample", lang)
            persona_coaching = (
                f"[{persona['name']}]\n"
                f"\"{random.choice(persona['praise_templates']).replace('{name}', h_sample)}\"\n\n"
                f"{base_coaching}"
            )
        else:
            persona_coaching = (
                f"[{persona['name']}]\n"
                f"\"{base_coaching}\""
            )

        self.db.save_log_for_date(date_str, summary_text=text, ai_coaching=persona_coaching)

        if channel != "Desktop Widget":
            self.db.record_remote_checkin_event(channel, text, persona_coaching, matched_ids)

        excel_ok, excel_msg = (True, "disabled")
        if self.db.get_setting("auto_sync_excel") == "true":
            log_entry = {
                "channel": channel,
                "message": text,
                "matched_names": checked_names,
                "coaching": persona_coaching,
            }
            excel_ok, excel_msg = self.db.sync_to_excel(log_entry=log_entry)

        checks = self.db.get_checks_for_date(date_str)
        day_done = sum(1 for hid in range(1, 36) if checks.get(hid, {}).get("status", 0) == 1)

        return {
            "date": date_str,
            "language": lang,
            "channel": channel,
            "matched_ids": matched_ids,
            "checked_habits": checked_names,
            "coaching": persona_coaching,
            "day_completed_count": day_done,
            "excel_synced": excel_ok,
            "excel_status": excel_msg,
        }

    def generate_weekly_summary(self):
        lang = self.get_language()
        persona = self.get_current_persona()
        stats = self.db.get_weekly_stats()
        report_msg = tr(
            "weekly_report_msg",
            lang,
            persona=persona["name"],
            start=stats["week_start"],
            end=stats["week_end"],
            count=stats["completed_count"],
            rate=stats["weekly_rate"],
            today=stats["today_date"],
            today_done=stats["today_completed"],
        )
        ok, msg = self.db.write_weekly_review_to_excel(report_msg)
        return {
            "stats": stats,
            "report": report_msg,
            "excel_synced": ok,
            "excel_status": msg,
        }


# =============================================================================
# Windows OS Startup Registry Controller
# =============================================================================
class WindowsAutostartManager:
    REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    STARTUP_APPROVED_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
    APP_NAME = "LifeOS_HabitAssistant"
    _STARTUP_APPROVED_ENABLED = b"\x02" + b"\x00" * 11

    @classmethod
    def format_autostart_command(cls, exe_or_py_path: str = None) -> str:
        """Return a cleanly double-quoted startup command safe for spaced/Unicode paths."""
        if exe_or_py_path is not None:
            raw = str(exe_or_py_path).strip()
            if raw:
                if raw.startswith('"'):
                    return raw
                if raw.lower().endswith(".exe") or os.path.exists(raw):
                    return f'"{raw}"'
                return raw

        if getattr(sys, "frozen", False):
            return f'"{os.path.abspath(sys.executable)}"'
        return f'"{os.path.abspath(sys.executable)}" "{os.path.abspath(sys.argv[0])}"'

    @classmethod
    def _resolve_reg_key(cls, reg_key_override: str = None) -> str:
        return reg_key_override or os.environ.get("LIFE_OS_AUTOSTART_REG_KEY") or cls.REG_KEY

    @classmethod
    def _resolve_approved_key(cls, approved_key_override: str = None) -> str:
        return approved_key_override or os.environ.get("LIFE_OS_APPROVED_REG_KEY") or cls.STARTUP_APPROVED_REG_KEY

    @classmethod
    def is_startup_approved(cls, reg_name: str, approved_key_override: str = None) -> bool:
        """Return False if Windows Task Manager explicitly disabled this Run entry."""
        if not sys.platform.startswith("win") or not reg_name:
            return True
        approved_key = cls._resolve_approved_key(approved_key_override)
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, approved_key, 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, reg_name)
                if isinstance(val, (bytes, bytearray)) and len(val) >= 1:
                    return val[0] in (0x02, 0x06)
        except FileNotFoundError:
            return True
        except Exception:
            return True
        return True

    @classmethod
    def get_registered_autostart(cls, reg_key_override: str = None):
        """Return (reg_name, command_value) if any Life OS Run key is registered, else (None, None)."""
        if not sys.platform.startswith("win"):
            return None, None
        reg_key = cls._resolve_reg_key(reg_key_override)
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_READ) as key:
                for reg_name in ALL_AUTOSTART_REG_NAMES:
                    try:
                        val, _ = winreg.QueryValueEx(key, reg_name)
                        if val:
                            return reg_name, str(val)
                    except FileNotFoundError:
                        continue
        except Exception:
            pass
        return None, None

    @classmethod
    def is_autostart_enabled(cls, reg_key_override: str = None, approved_key_override: str = None) -> bool:
        if not sys.platform.startswith("win"):
            return False
        reg_name, val = cls.get_registered_autostart(reg_key_override=reg_key_override)
        if not reg_name or not val:
            return False
        return cls.is_startup_approved(reg_name, approved_key_override=approved_key_override)

    @classmethod
    def _delete_legacy_values(cls, winreg, reg_key: str, keep_name: str = None, access_mask: int = 0):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_SET_VALUE | access_mask) as key:
                for reg_name in ALL_AUTOSTART_REG_NAMES:
                    if keep_name is None or reg_name != keep_name:
                        try:
                            winreg.DeleteValue(key, reg_name)
                        except FileNotFoundError:
                            pass
        except FileNotFoundError:
            pass
        except OSError:
            pass

    @classmethod
    def set_autostart(
        cls,
        enable: bool,
        exe_or_py_path: str = None,
        lang: str = None,
        reg_key_override: str = None,
        approved_key_override: str = None,
    ):
        if not sys.platform.startswith("win"):
            return False, tr("autostart_not_win", lang)
        target_reg_name = get_autostart_reg_name(lang)
        reg_key = cls._resolve_reg_key(reg_key_override)
        approved_key = cls._resolve_approved_key(approved_key_override)
        try:
            import winreg
            with winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                reg_key,
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_READ,
            ) as key:
                # Clean previous localized/legacy entries first to avoid duplicates
                for reg_name in ALL_AUTOSTART_REG_NAMES:
                    if not enable or reg_name != target_reg_name:
                        try:
                            winreg.DeleteValue(key, reg_name)
                        except FileNotFoundError:
                            pass

                cls._delete_legacy_values(
                    winreg,
                    approved_key,
                    keep_name=target_reg_name if enable else None,
                )

                if enable:
                    cmd = cls.format_autostart_command(exe_or_py_path)
                    winreg.SetValueEx(key, target_reg_name, 0, winreg.REG_SZ, cmd)
                    # Record explicit Task Manager StartupApproved=Enabled state when possible
                    try:
                        with winreg.CreateKeyEx(
                            winreg.HKEY_CURRENT_USER,
                            approved_key,
                            0,
                            winreg.KEY_SET_VALUE | winreg.KEY_READ,
                        ) as app_key:
                            winreg.SetValueEx(
                                app_key,
                                target_reg_name,
                                0,
                                winreg.REG_BINARY,
                                cls._STARTUP_APPROVED_ENABLED,
                            )
                    except OSError:
                        pass
                    stored, _ = winreg.QueryValueEx(key, target_reg_name)
                    if str(stored) != cmd:
                        return False, "Autostart error: registry read-back mismatch"
                    return True, tr("autostart_enabled_ok", lang)
                return True, tr("autostart_disabled_ok", lang)
        except Exception as e:
            return False, f"Autostart error: {e}"

    @classmethod
    def _extract_exe_path(cls, cmd_value: str) -> str:
        raw = str(cmd_value or "").strip()
        if not raw:
            return ""
        if raw.startswith('"'):
            end = raw.find('"', 1)
            if end > 1:
                return raw[1:end]
        exe_idx = raw.lower().find(".exe")
        if exe_idx != -1:
            return raw[: exe_idx + 4]
        return raw

    @classmethod
    def sync_autostart_if_enabled(
        cls,
        db_manager=None,
        lang: str = None,
        exe_or_py_path: str = None,
        reg_key_override: str = None,
        approved_key_override: str = None,
    ):
        """Self-heal legacy unquoted/moved Run entries at frozen exe startup without touching dev runs."""
        if not sys.platform.startswith("win"):
            return False, "not-windows"
        if os.environ.get("LIFE_OS_SKIP_AUTOSTART_SYNC") == "1":
            return False, "skipped-by-env"
        has_custom_reg = bool(reg_key_override or os.environ.get("LIFE_OS_AUTOSTART_REG_KEY"))
        # Never mutate production HKCU Run when running isolated LIFE_OS_DATA_DIR sandboxes
        if os.environ.get("LIFE_OS_DATA_DIR") and not has_custom_reg:
            return False, "skipped-sandbox-data-dir"
        # Protect production HKCU Run entry when launched as an unfrozen dev script
        if not getattr(sys, "frozen", False) and exe_or_py_path is None and not has_custom_reg:
            return False, "skipped-unfrozen-dev"

        active_lang = lang or (db_manager.get_setting("language") if db_manager else None)
        if active_lang == "auto":
            active_lang = None
        db_enabled = (db_manager.get_setting("autostart_enabled") == "true") if db_manager else False
        reg_name, reg_val = cls.get_registered_autostart(reg_key_override=reg_key_override)

        if reg_name and not cls.is_startup_approved(reg_name, approved_key_override=approved_key_override):
            if db_manager and db_enabled:
                db_manager.set_setting("autostart_enabled", "false")
            return False, "disabled-by-windows"

        has_lifeos_entry = bool(reg_val and "lifeos_assistant" in reg_val.lower())
        if not db_enabled and not has_lifeos_entry:
            return False, "not-enabled"

        target_path_override = exe_or_py_path
        if not db_enabled and target_path_override is None and reg_val:
            existing_exe = cls._extract_exe_path(reg_val)
            cur_exe = os.path.abspath(sys.executable) if getattr(sys, "frozen", False) else ""
            if existing_exe and os.path.exists(existing_exe) and (not cur_exe or os.path.normcase(existing_exe) != os.path.normcase(cur_exe)):
                # Preserve valid existing installation path while fixing missing quotes/StartupApproved
                target_path_override = existing_exe

        expected_cmd = cls.format_autostart_command(target_path_override)
        target_reg_name = get_autostart_reg_name(active_lang)
        needs_quote = bool(reg_val and not reg_val.strip().startswith('"'))
        needs_update = (reg_name != target_reg_name) or (reg_val != expected_cmd) or needs_quote

        if needs_update:
            ok, msg = cls.set_autostart(
                True,
                exe_or_py_path=target_path_override,
                lang=active_lang,
                reg_key_override=reg_key_override,
                approved_key_override=approved_key_override,
            )
            if ok and db_manager and not db_enabled and target_path_override is None:
                db_manager.set_setting("autostart_enabled", "true")
            return ok, msg

        if db_manager and not db_enabled and target_path_override is None:
            db_manager.set_setting("autostart_enabled", "true")
        return True, "already-synced"
