"""
=============================================================================
🌟 ALL-IN-ONE LIFE OS : AI 습관 비서 (AI Habit Secretary)
=============================================================================
1. 자연어 일과 보고 분석 -> 35대 성공인 습관 자동 매핑 & 다국어 NLP/LLM 코칭
2. 거인들의 철학(버핏, 후버만, 아우렐리우스 등) 기반 맞춤 코칭 & SQLite/Excel 양방향 동기화
3. 한국어(ko), 영어(en), 일본어(ja), 중국어(zh) 4개 국어 지원 (시스템 언어 자동 감지)
=============================================================================
"""

import os
import sys
import json
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


class LLMClient:
    """Supports Grok, OpenAI, Gemini, or Offline multilingual rule-based NLP."""
    def __init__(self, provider=None, api_key=None, lang=None):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "mock")).lower()
        self.api_key = api_key or os.getenv("GROK_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.lang = lang

    @staticmethod
    def _is_safe_cross_lang_kw(kw: str) -> bool:
        """Guard short ASCII words (like 'why') from triggering accidental matches in other locales."""
        s = kw.strip().lower().replace(" ", "")
        if not s:
            return False
        if s.isascii():
            return len(s) >= 4
        return len(s) >= 2

    def analyze_checkin(self, user_text: str, lang: str = None):
        """Map user text to matched habits and generate personalized advice in active language."""
        active_lang = resolve_language(lang or self.lang)
        catalog = get_habits_catalog(active_lang)

        matched_ids = []
        user_lower = (user_text or "").lower().replace(" ", "")
        for habit in catalog:
            found = False
            # 1. Exact match against active language's keywords
            for kw in habit["keywords"]:
                if kw.lower().replace(" ", "") in user_lower:
                    found = True
                    break
            # 2. Safe cross-language matching (e.g. English keyword typed while UI is Korean)
            if not found:
                for kw in habit.get("all_keywords", []):
                    if self._is_safe_cross_lang_kw(kw) and kw.lower().replace(" ", "") in user_lower:
                        found = True
                        break
            if found:
                matched_ids.append(habit["id"])

        if self.provider in ["grok", "openai", "gemini"] and self.api_key:
            try:
                return self._call_llm_api(user_text, matched_ids, active_lang, catalog)
            except Exception as e:
                print(f"[!] LLM call failed ({e}), falling back to local NLP engine.")

        return self._local_nlp_synthesize(user_text, matched_ids, active_lang, catalog)

    def _call_llm_api(self, user_text: str, pre_matched: list, active_lang: str, catalog: list):
        import requests
        catalog_summary = "\n".join(f"{h['id']}: [{h['category']}] {h['name']}" for h in catalog)
        system_prompt = tr("llm_system_prompt", active_lang, catalog=catalog_summary)
        user_prompt = tr("llm_user_msg", active_lang, text=user_text, pre_matched=pre_matched)

        content = None
        if self.provider in ["grok", "openai"]:
            url = "https://api.x.ai/v1/chat/completions" if self.provider == "grok" else "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "grok-beta" if self.provider == "grok" else "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                data = res.json()
                content = json.loads(data["choices"][0]["message"]["content"])

        elif self.provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]
                }],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                data = res.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                content = json.loads(raw_text)

        if isinstance(content, dict):
            raw_ids = content.get("matched_habit_ids") or []
            clean_ids = []
            for x in raw_ids:
                if isinstance(x, int) and 1 <= x <= 35 and x not in clean_ids:
                    clean_ids.append(x)
            coaching = str(content.get("coaching_message") or "").strip()
            if coaching:
                return clean_ids, coaching

        return self._local_nlp_synthesize(user_text, pre_matched, active_lang, catalog)

    def _local_nlp_synthesize(self, user_text: str, matched_ids: list, active_lang: str = None, catalog: list = None):
        lang = resolve_language(active_lang or self.lang)
        cat = catalog or get_habits_catalog(lang)
        if not matched_ids:
            matched_ids = []
            advice = tr("llm_no_match", lang)
        else:
            names = [h["name"] for h in cat if h["id"] in matched_ids]
            advice = tr("llm_success_advice", lang, names=", ".join(names[:2]), count=len(matched_ids))
        return matched_ids, advice


class LifeOSSecretary:
    """Manages SQLite primary timeline + Excel dual sync for CLI check-ins and coaching."""
    def __init__(self, excel_path=None, llm_client=None, lang=None):
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
        self.engine = AssistantEngine(self.db, llm_client=llm_client)

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
