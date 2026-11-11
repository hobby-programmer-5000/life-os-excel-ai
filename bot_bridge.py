"""
=============================================================================
🌐 ALL-IN-ONE LIFE OS : 통합 봇 & 웹훅 브릿지 서버 (Bot Bridge Server)
=============================================================================
Discord, Telegram, Slack, iPhone 단축어, Grok Bot 등 어떤 외부 봇/웹훅이든
HTTP 요청 한 번으로 SQLite 타임라인 + 플로팅 위젯 + 엑셀을 실시간 동시 동기화합니다.
외부 패키지 없이 Python 표준 라이브러리(ThreadingHTTPServer)로 구동됩니다.
=============================================================================
"""

import sys
import json
import datetime
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from database import DatabaseManager
from assistant_engine import AssistantEngine
from i18n import tr, get_app_name

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def _resolve_target_date(payload: dict) -> str:
    """Resolve optional date ('YYYY-MM-DD'), day_offset (int), or weekday column (4..10)."""
    if payload.get("date"):
        try:
            datetime.date.fromisoformat(str(payload["date"]))
            return str(payload["date"])
        except Exception:
            pass
    if "day_offset" in payload and payload["day_offset"] is not None:
        try:
            return (datetime.date.today() + datetime.timedelta(days=int(payload["day_offset"]))).isoformat()
        except Exception:
            pass
    if "day" in payload and payload["day"] is not None:
        try:
            col = int(payload["day"])
            if 4 <= col <= 10:
                today = datetime.date.today()
                monday = today - datetime.timedelta(days=today.weekday())
                return (monday + datetime.timedelta(days=col - 4)).isoformat()
        except Exception:
            pass
    return datetime.date.today().isoformat()


def _make_handler_class(db: DatabaseManager, engine: AssistantEngine, on_checkin=None):
    class BotWebhookHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            # Quiet standard HTTP access logging inside headless GUI exe
            if getattr(sys, "stdout", None) and not getattr(sys, "frozen", False):
                super().log_message(format, *args)

        def _send_json(self, status_code: int, data: dict):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self._send_json(200, {"status": "ok"})

        def do_GET(self):
            path = urlparse(self.path).path
            lang = db.get_language()
            habits = engine.habits

            if path in ("/", "/health"):
                persona = engine.get_current_persona()
                self._send_json(200, {
                    "status": "online",
                    "service": get_app_name(lang),
                    "language": lang,
                    "active_persona": persona["name"],
                    "endpoints": {
                        "GET /stats": "/stats",
                        "GET /habits": "/habits",
                        "POST /checkin": "/checkin",
                        "POST /nudge": "/nudge",
                        "POST /review": "/review"
                    }
                })
            elif path == "/stats":
                stats = db.get_weekly_stats()
                checks = db.get_checks_for_date(stats["today_date"])
                done_names = [
                    h["name"] for h in habits
                    if checks.get(h["id"], {}).get("status", 0) == 1
                ]
                self._send_json(200, {
                    "status": "success",
                    "language": lang,
                    "stats": stats,
                    "persona": engine.get_current_persona()["name"],
                    "today_completed_habits": done_names
                })
            elif path == "/habits":
                self._send_json(200, {
                    "status": "success",
                    "language": lang,
                    "count": len(habits),
                    "habits": habits,
                })
            elif path == "/review":
                rev = engine.generate_weekly_summary()
                self._send_json(200, {"status": "success", **rev})
            else:
                self._send_json(404, {"status": "error", "message": "Unknown endpoint"})

        def do_POST(self):
            path = urlparse(self.path).path
            lang = db.get_language()
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length) if content_length > 0 else b""

            try:
                payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
            except Exception:
                self._send_json(400, {"status": "error", "error": tr("bridge_invalid_json", lang)})
                return

            if path == "/checkin":
                user_msg = str(payload.get("message") or payload.get("text") or payload.get("content") or "").strip()
                channel = str(payload.get("channel") or payload.get("source") or "Webhook Bot").strip()
                target_date = _resolve_target_date(payload)

                if not user_msg:
                    self._send_json(400, {"status": "error", "error": tr("bridge_empty_msg", lang)})
                    return

                res = engine.process_natural_checkin(user_msg, date_str=target_date, channel=channel)
                if on_checkin:
                    try:
                        on_checkin(res)
                    except Exception:
                        pass

                checked_str = ", ".join(res["checked_habits"]) if res["checked_habits"] else tr("bridge_no_habit", lang)
                reply_text = tr(
                    "bridge_reply_text",
                    lang,
                    coaching=res["coaching"],
                    date=res["date"],
                    done=res["day_completed_count"],
                    checked=checked_str,
                )
                self._send_json(200, {
                    "status": "success",
                    "language": lang,
                    "reply_text": reply_text,
                    "data": res
                })

            elif path == "/nudge":
                target_date = _resolve_target_date(payload)
                nudge = engine.get_smart_nudge(target_date)
                self._send_json(200, {"status": "success", "nudge": nudge})

            elif path == "/review":
                rev = engine.generate_weekly_summary()
                self._send_json(200, {"status": "success", **rev})

            else:
                self._send_json(404, {"status": "error", "message": "Unknown endpoint"})

    return BotWebhookHandler


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class BotBridgeServer:
    """Thread-safe controller for the built-in or standalone webhook server."""
    def __init__(self, db_manager=None, assistant_engine=None, host="127.0.0.1", port=8080, on_checkin=None):
        self.db = db_manager or DatabaseManager()
        self.engine = assistant_engine or AssistantEngine(self.db)
        self.host = host
        self.port = int(port)
        self.on_checkin = on_checkin
        self._server = None
        self._thread = None
        self.last_error = ""

    @property
    def is_running(self) -> bool:
        return self._server is not None and self._thread is not None and self._thread.is_alive()

    def start(self) -> tuple:
        lang = self.db.get_language()
        if self.is_running:
            return True, tr("bridge_already_running", lang, host=self.host, port=self.port)
        try:
            handler_cls = _make_handler_class(self.db, self.engine, self.on_checkin)
            self._server = ReusableThreadingHTTPServer((self.host, self.port), handler_cls)
            self.port = self._server.server_address[1]
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()
            self.last_error = ""
            return True, tr("bridge_running", lang, host=self.host, port=self.port)
        except Exception as e:
            self.last_error = str(e)
            self._server = None
            return False, tr("bridge_start_fail", lang, err=e)

    def stop(self):
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
            except Exception:
                pass
            self._server = None
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None


def run_bridge(port=8080, host="0.0.0.0"):
    bridge = BotBridgeServer(host=host, port=port)
    ok, msg = bridge.start()
    if not ok:
        print(f"[!] {msg}")
        return
    print("=" * 65)
    print(f"🤖 [Life OS AI 비서] 통합 웹훅 브릿지 가동 중 ({host}:{port})")
    print(f"👉 상태 확인: http://localhost:{port}/stats")
    print(f"👉 체크인 POST: http://localhost:{port}/checkin")
    print("   (SQLite DB ↔ 데스크톱 위젯 ↔ 엑셀 실시간 통합 동기화 활성)")
    print("=" * 65)
    try:
        while bridge.is_running:
            bridge._thread.join(0.5)
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
        bridge.stop()


if __name__ == "__main__":
    port_num = 8080
    host_addr = "0.0.0.0"
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port_num = int(sys.argv[1])
    if len(sys.argv) > 2:
        host_addr = sys.argv[2]
    run_bridge(port=port_num, host=host_addr)
