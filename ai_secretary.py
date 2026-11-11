"""
=============================================================================
🌟 ALL-IN-ONE LIFE OS : AI 습관 비서 (Local Multilingual NLP Habit Secretary)
=============================================================================
1. 100% 오프라인 다국어 자연어 분석 -> 35대 성공인 습관 자동 매핑 & 코칭 (외부 유료 API 불필요)
2. 거인들의 철학(버핏, 후버만, 아우렐리우스 등) 기반 맞춤 코칭 & SQLite/Excel 양방향 동기화
3. 한국어(ko), 영어(en), 일본어(ja), 중국어(zh) 4개 국어 지원 (시스템 언어 자동 감지)
=============================================================================
"""

import os
import re
import sys
import argparse
import datetime
from pathlib import Path

from i18n import resolve_language, tr, get_app_name, SUPPORTED_LANGUAGES
from i18n_habits import get_habits_catalog

# Set console encoding to UTF-8 for Windows PowerShell / CMD
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Default paths (respects LIFE_OS_DATA_DIR when overridden)
_env_data_dir = os.getenv("LIFE_OS_DATA_DIR", "").strip()
BASE_DIR = Path(_env_data_dir).resolve() if _env_data_dir else Path(__file__).resolve().parent
DEFAULT_EXCEL_PATH = BASE_DIR / "Life_OS_Successful_Habits.xlsx"

# Exported catalog for backward compatibility (localized to active OS/env locale)
HABITS_CATALOG = get_habits_catalog()

_NORM_RE = re.compile(r"[\s\-_·.,!?;:'\"()~]+")

# Extra flexible multi-word phrase patterns for common separated phrasings across ko/en/ja/zh
_EXTRA_PHRASE_PATTERNS = {
    6: (
        re.compile(r"晒.{0,8}太阳"),
        re.compile(r"아침.{0,8}(햇빛|햇볕)"),
    ),
    8: (
        re.compile(r"(put|keep).{0,14}(phone|screen).{0,14}(away|off)", re.I),
        re.compile(r"(before bed|bedtime).{0,16}(no phone|phone away|screens? off)", re.I),
        re.compile(r"(자기\s*전|잠들기\s*전|취침\s*전).{0,12}(스마트폰|폰|화면|휴대폰).{0,10}(멀리|치우|끄|꺼|안\s*보)"),
        re.compile(r"(스마트폰|휴대폰).{0,8}(멀리|치웠|치움)"),
        re.compile(r"(寝る前|就寝前).{0,10}(スマホ|画面).{0,10}(見な|オフ|離)"),
    ),
}


class LocalHabitNLP:
    """Offline multilingual rule-based NLP matcher & coaching synthesizer (zero API cost)."""

    def __init__(self, lang=None):
        self.lang = lang

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize case, whitespace, hyphens, and punctuation so '2-minute' matches '2 minute'."""
        return _NORM_RE.sub("", (text or "").lower())

    @staticmethod
    def _is_safe_cross_lang_kw(kw: str) -> bool:
        """Guard short ASCII words (like 'why') from triggering accidental matches in other locales."""
        s = _NORM_RE.sub("", (kw or "").lower())
        if not s:
            return False
        if s.isascii():
            return len(s) >= 4
        return len(s) >= 2

    def analyze_checkin(self, user_text: str, lang: str = None):
        """Map user text to matched habits and generate localized advice in active language."""
        active_lang = resolve_language(lang or self.lang)
        catalog = get_habits_catalog(active_lang)

        matched_ids = []
        raw_text = (user_text or "").strip()
        user_norm = self._normalize_text(raw_text)
        if user_norm:
            for habit in catalog:
                hid = habit["id"]
                found = False
                # 1. Match normalized active language keywords
                for kw in habit["keywords"]:
                    kw_norm = self._normalize_text(kw)
                    if kw_norm and kw_norm in user_norm:
                        found = True
                        break
                # 2. Match flexible multi-word conversational phrasing patterns
                if not found and hid in _EXTRA_PHRASE_PATTERNS:
                    for pat in _EXTRA_PHRASE_PATTERNS[hid]:
                        if pat.search(raw_text):
                            found = True
                            break
                # 3. Safe cross-language matching (e.g. English keyword typed while UI is Korean)
                if not found:
                    for kw in habit.get("all_keywords", []):
                        kw_norm = self._normalize_text(kw)
                        if kw_norm and self._is_safe_cross_lang_kw(kw) and kw_norm in user_norm:
                            found = True
                            break
                if found:
                    matched_ids.append(hid)

        return self._synthesize_coaching(matched_ids, active_lang, catalog)

    def _synthesize_coaching(self, matched_ids: list, active_lang: str = None, catalog: list = None):
        lang = resolve_language(active_lang or self.lang)
        cat = catalog or get_habits_catalog(lang)
        if not matched_ids:
            matched_ids = []
            advice = tr("nlp_no_match", lang)
        else:
            names = [h["name"] for h in cat if h["id"] in matched_ids]
            advice = tr("nlp_success_advice", lang, names=", ".join(names[:2]), count=len(matched_ids))
        return matched_ids, advice


class LifeOSSecretary:
    """Manages SQLite primary timeline + Excel dual sync for CLI check-ins and coaching."""
    def __init__(self, excel_path=None, nlp_client=None, lang=None):
        from database import DatabaseManager
        from assistant_engine import AssistantEngine
        self.db = DatabaseManager()
        if lang and lang.strip().lower() in (*SUPPORTED_LANGUAGES, "auto"):
            self.db.set_setting("language", lang.strip().lower())
        if excel_path:
            self.excel_path = Path(excel_path)
            self.db.set_setting("excel_path", str(self.excel_path))
        else:
            self.excel_path = self.db._resolve_excel_target(auto_create=False)
        self.engine = AssistantEngine(self.db, nlp_client=nlp_client)

    def check_in(self, message: str, day_col_index: int = None, channel: str = "CLI / Assistant"):
        """Process natural language check-in into SQLite DB + Excel dual sync."""
        today = datetime.date.today()
        if day_col_index is not None and 4 <= int(day_col_index) <= 10:
            monday = today - datetime.timedelta(days=today.weekday())
            target_date = (monday + datetime.timedelta(days=int(day_col_index) - 4)).isoformat()
            col_idx = int(day_col_index)
        else:
            target_date = today.isoformat()
            col_idx = 4 + today.weekday()

        res = self.engine.process_natural_checkin(message, date_str=target_date, channel=channel)
        return {
            "status": "success",
            "date": target_date,
            "matched_habit_ids": res["matched_ids"],
            "checked_habits": res["checked_habits"],
            "coaching_message": res["coaching"],
            "day_column": col_idx,
            "excel_path": str(self.db._resolve_excel_target()),
            "language": self.db.get_language(),
        }

    def generate_weekly_report(self):
        """Analyzes the current week SQLite tracking and updates Excel KPT review."""
        rev = self.engine.generate_weekly_summary()
        stats = rev["stats"]
        lang = self.db.get_language()
        return tr("cli_review_summary", lang, count=stats["completed_count"], rate=stats["weekly_rate"])


# =============================================================================
# CLI Interface & Demonstration
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="ALL-IN-ONE LIFE OS : Multilingual AI Habit Assistant")
    parser.add_argument("--checkin", type=str, help="Natural language check-in report")
    parser.add_argument("--day", type=int, default=None, help="Weekday column index (4=Mon .. 10=Sun)")
    parser.add_argument("--review", action="store_true", help="Generate AI weekly summary review")
    parser.add_argument("--interactive", action="store_true", help="Interactive CLI assistant session")
    parser.add_argument("--excel", type=str, default=None, help="Optional custom Excel workbook path")
    parser.add_argument("--lang", type=str, default=None, help="Override language: auto, ko, en, ja, zh")

    args = parser.parse_args()
    secretary = LifeOSSecretary(excel_path=args.excel, lang=args.lang)
    lang = secretary.db.get_language()
    app_name = get_app_name(lang)

    if args.checkin:
        print(f"\n{tr('cli_analyzing', lang, msg=args.checkin)}")
        result = secretary.check_in(args.checkin, day_col_index=args.day, channel="CLI User")
        print("\n" + "=" * 60)
        print(tr("cli_checked_hdr", lang))
        for h in result["checked_habits"]:
            print(f"  ✅ {h}")
        print(f"\n{tr('cli_coaching_hdr', lang)}")
        print(f"  \"{result['coaching_message']}\"")
        print(f"\n{tr('cli_excel_done', lang, path=result['excel_path'])}")
        print("=" * 60 + "\n")

    elif args.review:
        print(f"\n{tr('cli_review_analyzing', lang)}")
        report = secretary.generate_weekly_report()
        print(f"\n{report}")
        print(f"{tr('cli_review_done', lang)}\n")

    elif args.interactive:
        print("\n" + "=" * 65)
        print(tr("cli_interactive_hdr", lang))
        print(tr("cli_interactive_sub", lang))
        print("=" * 65 + "\n")

        while True:
            try:
                user_msg = input(tr("cli_prompt_you", lang)).strip()
                if not user_msg:
                    continue
                if user_msg.lower() in ["exit", "q", "quit", "종료", "終了", "退出"]:
                    print(tr("cli_bye", lang))
                    break

                res = secretary.check_in(user_msg, channel="Interactive Session")
                print(f"\n{tr('cli_bot_say', lang, coaching=res['coaching_message'])}")
                print(f"{tr('cli_bot_checked', lang, habits=', '.join(res['checked_habits']))}\n")
            except (KeyboardInterrupt, EOFError):
                break
    else:
        print("\n" + "=" * 65)
        print(tr("cli_ready_title", lang, app_name=app_name))
        print(tr("cli_ready_examples", lang))
        print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
