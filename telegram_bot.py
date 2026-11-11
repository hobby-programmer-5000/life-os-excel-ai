"""
=============================================================================
📱 ALL-IN-ONE LIFE OS : 무설치 초경량 텔레그램 AI 비서 봇 (Telegram Bot)
=============================================================================
별도의 무거운 라이브러리 없이 requests만으로 Telegram Bot API(Long Polling)와 통신하며,
스마트폰에서 보낸 일과 메시지를 SQLite DB + 데스크톱 플로팅 위젯 + 엑셀에 실시간 반영합니다.

지원 명령어:
  /start, /help   : 시작 및 사용법 안내
  /status, /today : 오늘(35대 습관) 달성 현황 조회
  /nudge          : 현재 시간대 추천 습관 넛지 받기
  /review         : 이번 주 종합 달성률 리포트 & 엑셀 주간회고 저장
  /어제 <내용>    : 어제 날짜로 소급 체크인
  (일반 메시지)   : 자연어 일과 분석 -> 자동 체크인 & 거인 페르소나 코칭
=============================================================================
"""

import os
import sys
import time
import datetime
import threading
import requests
from database import DatabaseManager
from assistant_engine import AssistantEngine
from bot_commands import build_bot_status_text, process_bot_message
from i18n import tr, resolve_language

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


class TelegramBotRunner:
    """Zero-dependency Telegram Bot API long-polling runner (desktop + standalone compatible)."""
    API_BASE = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token: str, db_manager=None, assistant_engine=None, on_checkin=None):
        self.token = (token or "").strip()
        self.db = db_manager or DatabaseManager()
        self.engine = assistant_engine or AssistantEngine(self.db)
        self.on_checkin = on_checkin
        self._running = False
        self._thread = None
        self._offset = 0
        self.bot_username = ""
        self.last_error = ""

    @property
    def is_running(self) -> bool:
        return self._running and self._thread is not None and self._thread.is_alive()

    @classmethod
    def verify_token(cls, token: str, lang: str = None) -> tuple:
        active_lang = resolve_language(lang)
        t = (token or "").strip()
        if not t:
            return False, tr("tg_empty_token", active_lang)
        try:
            url = cls.API_BASE.format(token=t, method="getMe")
            res = requests.get(url, timeout=8)
            data = res.json()
            if res.status_code == 200 and data.get("ok"):
                uname = data["result"].get("username", "unknown")
                return True, tr("tg_verify_ok", active_lang, uname=uname)
            return False, tr("tg_verify_fail", active_lang, detail=data.get("description", res.status_code))
        except Exception as e:
            return False, tr("tg_verify_err", active_lang, err=e)

    def _call(self, method: str, params: dict = None, timeout: int = 30):
        url = self.API_BASE.format(token=self.token, method=method)
        res = requests.post(url, json=params or {}, timeout=timeout)
        return res.json()

    def _send_reply(self, chat_id: int, text: str):
        try:
            self._call("sendMessage", {"chat_id": chat_id, "text": text}, timeout=10)
        except Exception:
            pass

    def _build_status_text(self) -> str:
        return build_bot_status_text(self.db, self.engine)

    def handle_text_message(self, text: str) -> str:
        """Process a single incoming text message or command and return localized reply text."""
        return process_bot_message(
            self.db,
            self.engine,
            text,
            channel="Telegram Bot",
            on_checkin=self.on_checkin,
            prefer_bang=False,
        )

    def _poll_loop(self):
        ok, info = self.verify_token(self.token, lang=self.db.get_language())
        if not ok:
            self.last_error = info
            self._running = False
            return
        self.bot_username = info
        self.last_error = ""

        while self._running:
            try:
                data = self._call(
                    "getUpdates",
                    {"offset": self._offset, "timeout": 20, "allowed_updates": ["message"]},
                    timeout=25
                )
                if data.get("ok"):
                    for upd in data.get("result", []):
                        self._offset = upd["update_id"] + 1
                        message = upd.get("message") or {}
                        chat_id = (message.get("chat") or {}).get("id")
                        text = message.get("text")
                        if chat_id and text:
                            reply = self.handle_text_message(text)
                            if reply:
                                self._send_reply(chat_id, reply)
                else:
                    self.last_error = str(data.get("description", "getUpdates error"))
                    time.sleep(3)
            except Exception as e:
                self.last_error = str(e)
                time.sleep(3)

    def start(self) -> tuple:
        lang = self.db.get_language()
        if not self.token or "your_telegram_bot_token" in self.token:
            return False, tr("tg_token_missing", lang)
        if self.is_running:
            return True, tr("tg_already_running", lang, name=self.bot_username or "Telegram Bot")

        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        return True, tr("tg_bg_started", lang)

    def stop(self):
        self._running = False
        # Do not block UI thread for long polling timeout
        self._thread = None


def run_telegram_bot():
    db = DatabaseManager()
    engine = AssistantEngine(db)
    token = db.get_setting("telegram_token", "") or os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token or "your_telegram_bot_token" in token:
        print("[!] TELEGRAM_BOT_TOKEN 이 설정되지 않았습니다.")
        print("    .env 파일에 TELEGRAM_BOT_TOKEN='당신의_토큰' 을 입력하거나")
        print("    플로팅 위젯 [⚙️ 설정 > 🌐 모바일 봇 연동]에서 토큰을 등록해 주세요.")
        return

    ok, info = TelegramBotRunner.verify_token(token)
    if not ok:
        print(f"[!] 텔레그램 연결 실패: {info}")
        return

    runner = TelegramBotRunner(token, db_manager=db, assistant_engine=engine)
    print("=" * 65)
    print(f"🤖 [Life OS] 텔레그램 AI 비서 봇 가동! {info}")
    print("   스마트폰 텔레그램에서 메시지를 보내면 PC DB/위젯/엑셀이 즉시 동기화됩니다.")
    print("   (종료하려면 Ctrl+C 를 누르세요)")
    print("=" * 65)
    runner._running = True
    try:
        runner._poll_loop()
    except KeyboardInterrupt:
        print("\n텔레그램 봇을 종료합니다.")
        runner.stop()


if __name__ == "__main__":
    run_telegram_bot()
