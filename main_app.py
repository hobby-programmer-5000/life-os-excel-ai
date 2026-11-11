"""
=============================================================================
🚀 ALL-IN-ONE LIFE OS : Main Desktop Application Entrypoint
=============================================================================
윈도우 시스템 트레이, 능동형 플로팅 비서, 글로벌 핫키, 모바일 봇/웹훅 브릿지 통합 실행기
=============================================================================
"""

import sys
import os
import tkinter as tk
from database import DatabaseManager
from assistant_engine import AssistantEngine
from floating_widget import FloatingAssistantWidget
from tray_manager import SystemTrayManager
from hotkey_manager import GlobalHotkeyManager
from bot_bridge import BotBridgeServer
from telegram_bot import TelegramBotRunner
from discord_bot import DiscordBotRunner
from i18n import tr
import i18n_habits  # Ensure PyInstaller bundles 35-habit catalog
import i18n_personas  # Ensure PyInstaller bundles 4-language persona catalog

# Set console encoding
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def main():
    # 1. Initialize Core Engine & Database
    db = DatabaseManager()
    engine = AssistantEngine(db)

    # 2. Initialize Tkinter Root
    root = tk.Tk()

    # 3. Runtime Service Containers
    tray = None
    widget = None
    hotkey = None
    services = {"bridge": None, "telegram": None, "discord": None}

    def on_remote_checkin(res):
        if widget:
            root.after(0, lambda r=res: widget.handle_remote_checkin(r))

    def refresh_bot_services():
        # Stop existing runners before applying updated host/port/token
        for svc_key in ("bridge", "telegram", "discord"):
            if services[svc_key]:
                services[svc_key].stop()
                services[svc_key] = None

        status_notes = []

        if db.get_setting("webhook_enabled", "false") == "true":
            host = db.get_setting("webhook_host", "127.0.0.1") or "127.0.0.1"
            try:
                port = int(db.get_setting("webhook_port", "8080"))
            except Exception:
                port = 8080
            bridge = BotBridgeServer(db, engine, host=host, port=port, on_checkin=on_remote_checkin)
            ok, msg = bridge.start()
            services["bridge"] = bridge if ok else None
            status_notes.append(msg)

        if db.get_setting("telegram_enabled", "false") == "true":
            token = db.get_setting("telegram_token", "") or os.getenv("TELEGRAM_BOT_TOKEN", "")
            tg = TelegramBotRunner(token, db, engine, on_checkin=on_remote_checkin)
            ok, msg = tg.start()
            services["telegram"] = tg if ok else None
            status_notes.append(msg)

        if db.get_setting("discord_enabled", "false") == "true":
            dc_token = db.get_setting("discord_token", "") or os.getenv("DISCORD_BOT_TOKEN", "")
            dc_chan = db.get_setting("discord_channel_id", "") or os.getenv("DISCORD_CHANNEL_ID", "")
            dc = DiscordBotRunner(dc_token, db, engine, allowed_channel_id=dc_chan, on_checkin=on_remote_checkin)
            ok, msg = dc.start()
            services["discord"] = dc if ok else None
            status_notes.append(msg)

        return status_notes

    def get_bot_status():
        lang = db.get_language()
        b = services["bridge"]
        t = services["telegram"]
        d = services["discord"]
        stopped = tr("bot_stopped", lang)
        connecting = tr("bot_connecting", lang)
        return {
            "webhook_running": bool(b and b.is_running),
            "webhook_url": f"http://{b.host}:{b.port}" if (b and b.is_running) else stopped,
            "telegram_running": bool(t and t.is_running),
            "telegram_info": (t.bot_username or connecting) if (t and t.is_running) else (t.last_error if t else stopped),
            "discord_running": bool(d and d.is_running),
            "discord_info": (d.bot_username or connecting) if (d and d.is_running) else (d.last_error if d else stopped),
        }

    def toggle_show():
        if root.winfo_viewable():
            root.after(0, widget.hide_to_tray)
        else:
            root.after(0, widget.show_window)

    def trigger_nudge_from_tray():
        root.after(0, lambda: [widget.show_window(), widget.trigger_nudge()])

    def open_full_list_from_tray():
        root.after(0, lambda: [widget.show_window(), widget.open_full_checklist_window()])

    def open_settings_from_tray():
        root.after(0, lambda: [widget.show_window(), widget.open_settings_dialog()])

    def sync_from_tray():
        root.after(0, widget.manual_sync_excel)

    def on_toast_notify(title, message):
        if tray:
            tray.show_notification(title, message)

    def exit_application():
        for svc_key in ("bridge", "telegram", "discord"):
            if services[svc_key]:
                services[svc_key].stop()
        if hotkey:
            hotkey.stop()
        if tray and tray.icon:
            tray.icon.stop()
        root.after(0, root.destroy)
        sys.exit(0)

    def on_language_changed(new_lang):
        if tray:
            tray.update_language(new_lang)

    # 4. Initialize Floating Assistant Widget
    widget = FloatingAssistantWidget(
        root=root,
        db_manager=db,
        assistant_engine=engine,
        on_minimize_to_tray=lambda: None,
        on_quit=exit_application,
        on_nudge_notify=on_toast_notify,
        on_bot_config_changed=refresh_bot_services,
        get_bot_status=get_bot_status,
        on_language_changed=on_language_changed
    )

    # 5. Initialize System Tray Manager
    tray = SystemTrayManager(
        on_show=toggle_show,
        on_nudge=trigger_nudge_from_tray,
        on_full_list=open_full_list_from_tray,
        on_settings=open_settings_from_tray,
        on_sync=sync_from_tray,
        on_exit=exit_application,
        lang_getter=db.get_language
    )
    tray.start()

    # 6. Initialize Global Hotkey (Ctrl + Shift + H)
    hotkey = GlobalHotkeyManager(on_hotkey_triggered=toggle_show)
    hotkey.start()

    # 7. Start Mobile Bot / Webhook Services if enabled
    refresh_bot_services()

    # 8. Run Tkinter Mainloop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        exit_application()


if __name__ == "__main__":
    main()
