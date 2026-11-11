"""
=============================================================================
🖥️ ALL-IN-ONE LIFE OS : Windows System Tray Manager (Pystray)
=============================================================================
작업표시줄 트레이 아이콘 상주, 백그라운드 백업, 우클릭 팝업 메뉴 및 토글
=============================================================================
"""

import threading
import sys
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from i18n import tr, get_app_name, resolve_language

# Set console encoding
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def create_tray_icon_image():
    """Dynamically generate a high-res modern app icon for Windows Tray"""
    width = 64
    height = 64
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded gradient navy background
    draw.ellipse((4, 4, 60, 60), fill="#0F172A", outline="#38BDF8", width=3)
    # Inner glowing core
    draw.ellipse((14, 14, 50, 50), fill="#1E293B", outline="#10B981", width=2)
    # Robot / Star core mark
    draw.rectangle((22, 26, 42, 38), fill="#38BDF8")
    draw.ellipse((26, 29, 30, 33), fill="#0F172A")
    draw.ellipse((34, 29, 38, 33), fill="#0F172A")
    # Smile
    draw.arc((26, 30, 38, 42), start=0, end=180, fill="#10B981", width=2)

    return img

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

    def start(self):
        lang = self._active_lang()
        image = create_tray_icon_image()
        menu = self._build_menu(lang)
        self.icon = pystray.Icon("LifeOS_HabitAssistant", image, get_app_name(lang), menu)

        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

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
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()
