"""
=============================================================================
⌨️ ALL-IN-ONE LIFE OS : Windows Native Global Hotkey Manager (ctypes)
=============================================================================
별도의 무거운 패키지나 드라이버 권한 없이
윈도우 표준 user32.dll RegisterHotKey API를 사용하여
어떤 작업(웹서핑, 코딩, 문서작업 등) 중이든
'Ctrl + Shift + H' 로 플로팅 비서를 즉시 팝업/숨김 토글합니다.
=============================================================================
"""

import sys
import ctypes
from ctypes import wintypes
import threading

# Windows Hotkey Constants
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
HOTKEY_ID = 101

user32 = ctypes.windll.user32 if sys.platform.startswith("win") else None

class GlobalHotkeyManager:
    def __init__(self, on_hotkey_triggered=None, vk_key=0x48, modifiers=(MOD_CONTROL | MOD_SHIFT)):
        """
        Default Hotkey: Ctrl + Shift + H (VK_H = 0x48)
        """
        self.on_hotkey_triggered = on_hotkey_triggered
        self.vk_key = vk_key
        self.modifiers = modifiers
        self._thread = None
        self._thread_id = None
        self._running = False

    def start(self):
        if not sys.platform.startswith("win"):
            return
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._hotkey_loop, daemon=True)
        self._thread.start()

    def _hotkey_loop(self):
        kernel32 = ctypes.windll.kernel32
        self._thread_id = kernel32.GetCurrentThreadId()

        # Register Hotkey
        # RegisterHotKey(HWND hWnd, int id, UINT fsModifiers, UINT vk)
        success = user32.RegisterHotKey(None, HOTKEY_ID, self.modifiers | MOD_NOREPEAT, self.vk_key)
        if not success:
            # Fallback without MOD_NOREPEAT for older Windows versions
            success = user32.RegisterHotKey(None, HOTKEY_ID, self.modifiers, self.vk_key)

        if not success:
            print("[!] 글로벌 핫키(Ctrl+Shift+H) 등록에 실패했습니다. (다른 프로그램이 선점했을 수 있습니다)")
            self._running = False
            return

        print("⌨️ [Life OS] 글로벌 단축키 등록 완료: Ctrl + Shift + H")

        msg = wintypes.MSG()
        while self._running:
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res <= 0 or msg.message == WM_QUIT:
                break

            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                if self.on_hotkey_triggered:
                    try:
                        self.on_hotkey_triggered()
                    except Exception as e:
                        print(f"[!] 핫키 콜백 실행 오류: {e}")

            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(None, HOTKEY_ID)

    def stop(self):
        self._running = False
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
