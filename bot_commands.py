"""
=============================================================================
💬 ALL-IN-ONE LIFE OS : Shared Multilingual Chat-Bot Command Processor
=============================================================================
Shared message handler used by both TelegramBotRunner and DiscordBotRunner
to prevent duplicated logic across messaging platforms.
=============================================================================
"""

import datetime
from i18n import tr, get_app_name


def build_bot_status_text(db, engine) -> str:
    """Build localized daily & weekly progress summary for messenger bots."""
    lang = db.get_language()
    stats = db.get_weekly_stats()
    today_str = stats["today_date"]
    checks = db.get_checks_for_date(today_str)
    done_list = []
    todo_list = []
    for h in engine.habits:
        if checks.get(h["id"], {}).get("status", 0) == 1:
            done_list.append(f"✅ {h['id']}. {h['name']}")
        else:
            todo_list.append(f"⬜ {h['id']}. {h['name']}")

    done_preview = "\n".join(done_list[:10]) if done_list else tr("tg_no_done", lang)
    todo_preview = "\n".join(todo_list[:5]) if todo_list else tr("tg_all_done", lang)
    return tr(
        "tg_status_text",
        lang,
        today=today_str,
        done=stats["today_completed"],
        rate=stats["weekly_rate"],
        count=stats["completed_count"],
        done_preview=done_preview,
        todo_preview=todo_preview,
    )


def process_bot_message(db, engine, text: str, channel: str = "Bot", on_checkin=None, prefer_bang: bool = False) -> str:
    """Process incoming chat commands (/ or !) or natural check-ins cleanly."""
    msg = (text or "").strip()
    if not msg:
        return ""

    lang = db.get_language()
    low = msg.lower()

    if any(low.startswith(cmd) for cmd in ("/start", "/help", "!start", "!help")):
        persona = engine.get_current_persona()
        reply = tr(
            "tg_start_text",
            lang,
            app_name=get_app_name(lang),
            emoji=persona["emoji"],
            persona=persona["name"],
        )
        if prefer_bang:
            reply = (
                reply
                .replace("/status", "!status")
                .replace("/nudge", "!nudge")
                .replace("/review", "!review")
                .replace("/yesterday", "!yesterday")
                .replace("/어제", "!어제")
                .replace("/昨日", "!昨日")
                .replace("/昨天", "!昨天")
            )
        return reply

    if any(low.startswith(cmd) for cmd in ("/status", "/today", "!status", "!today")):
        return build_bot_status_text(db, engine)

    if any(low.startswith(cmd) for cmd in ("/nudge", "!nudge")):
        nudge = engine.get_smart_nudge()
        return tr("tg_nudge_prefix", lang, question=nudge["question"])

    if any(low.startswith(cmd) for cmd in ("/review", "!review")):
        rev = engine.generate_weekly_summary()
        return tr("tg_review_prefix", lang, report=rev["report"], status=rev["excel_status"])

    target_date = datetime.date.today().isoformat()
    clean_msg = msg
    yesterday_cmds = (
        "/yesterday", "/어제", "/昨日", "/昨天",
        "!yesterday", "!어제", "!昨日", "!昨天",
    )
    matched_y_cmd = next((c for c in yesterday_cmds if low == c or low.startswith(c + " ")), None)
    if matched_y_cmd:
        clean_msg = msg[len(matched_y_cmd):].strip()
        if not clean_msg:
            msg_out = tr("tg_yesterday_empty", lang)
            return msg_out.replace("`/어제", "`!어제").replace("`/yesterday", "`!yesterday") if prefer_bang else msg_out
        target_date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    res = engine.process_natural_checkin(clean_msg, date_str=target_date, channel=channel)
    if on_checkin:
        try:
            on_checkin(res)
        except Exception:
            pass

    checked_block = (
        "\n".join(f"  ✅ {h}" for h in res["checked_habits"])
        if res["checked_habits"]
        else tr("tg_no_matched_kw", lang)
    )
    return tr(
        "tg_reply_text",
        lang,
        coaching=res["coaching"],
        date=res["date"],
        done=res["day_completed_count"],
        checked_block=checked_block,
    )
