"""
=============================================================================
🖥️ ALL-IN-ONE LIFE OS : Windows System Tray Manager (Pystray)
=============================================================================
작업표시줄 트레이 아이콘 상주, 백그라운드 백업, 우클릭 팝업 메뉴 및 토글
=============================================================================
"""

import ctypes
import threading
import sys
from PIL import Image
import pystray
from pystray import MenuItem as item
from i18n import tr, get_app_name, resolve_language
from app_icon import load_app_icon_image

# Set console encoding
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def create_tray_icon_image():
    """Load the unified Growth Graph app icon for the Windows System Tray."""
    return load_app_icon_image(size=64)

class SystemTrayManager:
    def __init__(self, on_show=None, on_nudge=None, on_full_list=None, on_settings=None, on_sync=None, on_exit=None,
                 lang_getter=None):
        self.on_show = on_show
        self.on_nudge = on_nudge
        self.on_full_list = on_full_list
        self.on_settings = on_settings
        self.on_sync = on_sync
        self.on_exit = on_exit
        self.lang_getter = lang_getter or (lambda: resolve_language(None))

        self.icon = None
        self._thread = None
        self._stop_event = threading.Event()

    def _active_lang(self, lang: str = None) -> str:
        if lang:
            return resolve_language(lang)
        try:
            return resolve_language(self.lang_getter())
        except Exception:
            return resolve_language(None)

    def _build_menu(self, lang: str = None):
        l = self._active_lang(lang)
        return pystray.Menu(
            item(tr("tray_open_hide", l), lambda icon, item: self.on_show() if self.on_show else None, default=True),
            item(tr("tray_nudge", l), lambda icon, item: self.on_nudge() if self.on_nudge else None),
            item(tr("tray_full_list", l), lambda icon, item: self.on_full_list() if self.on_full_list else None),
            item(tr("tray_sync", l), lambda icon, item: self.on_sync() if self.on_sync else None),
            pystray.Menu.SEPARATOR,
            item(tr("tray_settings", l), lambda icon, item: self.on_settings() if self.on_settings else None),
            item(tr("tray_exit", l), lambda icon, item: self.stop())
        )

    def _has_windows_taskbar(self) -> bool:
        if not sys.platform.startswith("win"):
            return True
        try:
            return bool(ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None))
        except Exception:
            return True

    def _watch_windows_boot_tray(self):
        """If started before Explorer created the taskbar during reboot, re-show once ready."""
        for _ in range(40):  # up to ~20s, exits immediately on stop_event
            if self._stop_event.wait(0.5):
                return
            if self._has_windows_taskbar():
                if self._stop_event.wait(0.5):
                    return
                if self.icon:
                    try:
                        self.icon._show()
                    except Exception:
                        pass
                    try:
                        self.icon.update_menu()
                    except Exception:
                        pass
                return

    def start(self):
        self._stop_event.clear()
        lang = self._active_lang()
        image = create_tray_icon_image()
        menu = self._build_menu(lang)
        self.icon = pystray.Icon("LifeOS_HabitAssistant", image, get_app_name(lang), menu)

        saw_tray = self._has_windows_taskbar()
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()
        if sys.platform.startswith("win") and not saw_tray:
            threading.Thread(target=self._watch_windows_boot_tray, daemon=True).start()

    def update_language(self, lang: str = None):
        """Update tray tooltip app name and context menu labels immediately on language switch."""
        l = self._active_lang(lang)
        if self.icon:
            try:
                self.icon.title = get_app_name(l)
                self.icon.menu = self._build_menu(l)
                self.icon.update_menu()
            except Exception:
                pass

    def show_notification(self, title: str, message: str):
        """Display Windows native Toast notification via Pystray Tray Icon"""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                print(f"[!] 윈도우 토스트 알림 표시 오류: {e}")

    def stop(self):
        self._stop_event.set()
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()
