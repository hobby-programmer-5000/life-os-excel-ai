"""
=============================================================================
💬 ALL-IN-ONE LIFE OS : Zero-Dependency Discord Bot (Gateway v10 + REST)
=============================================================================
Communicates directly with Discord using pure Python stdlib TLS WebSocket +
requests (no discord.py or external tunnel needed). Messages sent via DM or
designated server channel sync SQLite, Desktop Widget, and Excel in real time.
=============================================================================
"""

import os
import re
import ssl
import json
import time
import base64
import socket
import struct
import hashlib
import threading
import requests
from urllib.parse import urlparse

from database import DatabaseManager
from assistant_engine import AssistantEngine
from bot_commands import process_bot_message
from i18n import tr, resolve_language


class _MinimalWebSocketClient:
    """Pure-stdlib RFC 6455 TLS WebSocket client sufficient for Discord Gateway v10."""

    WS_MAGIC = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self):
        self._sock = None
        self._buf = bytearray()
        self._send_lock = threading.Lock()
        self._closed = False

    def connect(self, wss_url: str, timeout: float = 15.0):
        parsed = urlparse(wss_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "wss" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        raw = socket.create_connection((host, port), timeout=timeout)
        if parsed.scheme == "wss":
            ctx = ssl.create_default_context()
            self._sock = ctx.wrap_socket(raw, server_hostname=host)
        else:
            self._sock = raw

        key_b64 = base64.b64encode(os.urandom(16)).decode("ascii")
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key_b64}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "User-Agent: LifeOS-DiscordBot/2.0\r\n\r\n"
        ).encode("ascii")
        self._sock.sendall(req)

        # Read HTTP 101 handshake cleanly without discarding post-header WebSocket frames
        raw_hdr = bytearray()
        while b"\r\n\r\n" not in raw_hdr:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise ConnectionError("WebSocket handshake closed before completion")
            raw_hdr.extend(chunk)
            if len(raw_hdr) > 65536:
                raise ConnectionError("WebSocket handshake response too large")

        sep_idx = raw_hdr.index(b"\r\n\r\n") + 4
        header_text = bytes(raw_hdr[:sep_idx]).decode("latin-1")
        if " 101 " not in header_text.splitlines()[0]:
            raise ConnectionError(f"WebSocket upgrade rejected: {header_text.splitlines()[0]}")

        expected_accept = base64.b64encode(hashlib.sha1(key_b64.encode("ascii") + self.WS_MAGIC).digest()).decode("ascii")
        accept_match = re.search(r"(?im)^Sec-WebSocket-Accept:\s*(\S+)", header_text)
        if accept_match and accept_match.group(1).strip() != expected_accept:
            raise ConnectionError("Invalid Sec-WebSocket-Accept header")

        if sep_idx < len(raw_hdr):
            self._buf.extend(raw_hdr[sep_idx:])

    def _read_exact(self, n: int, timeout: float = 65.0) -> bytes:
        self._sock.settimeout(timeout)
        while len(self._buf) < n:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise ConnectionError("WebSocket connection closed by peer")
            self._buf.extend(chunk)
        out = bytes(self._buf[:n])
        del self._buf[:n]
        return out

    def send_frame(self, opcode: int, payload: bytes = b""):
        if self._closed or not self._sock:
            return
        with self._send_lock:
            length = len(payload)
            header = bytearray([0x80 | (opcode & 0x0F)])
            if length < 126:
                header.append(0x80 | length)
            elif length <= 65535:
                header.append(0x80 | 126)
                header.extend(struct.pack("!H", length))
            else:
                header.append(0x80 | 127)
                header.extend(struct.pack("!Q", length))

            mask = os.urandom(4)
            header.extend(mask)
            masked = bytes(b ^ mask[i & 3] for i, b in enumerate(payload))
            self._sock.sendall(bytes(header) + masked)

    def send_json(self, obj: dict):
        self.send_frame(0x1, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def recv_json(self, timeout: float = 65.0):
        """Receive next WebSocket message (handling fragments & ping/pong). Returns (close_code, dict_or_None)."""
        fragments = []
        while True:
            b1, b2 = self._read_exact(2, timeout=timeout)
            fin = bool(b1 & 0x80)
            opcode = b1 & 0x0F
            masked = bool(b2 & 0x80)
            length = b2 & 0x7F

            if length == 126:
                length = struct.unpack("!H", self._read_exact(2, timeout=timeout))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._read_exact(8, timeout=timeout))[0]

            mask_key = self._read_exact(4, timeout=timeout) if masked else None
            data = self._read_exact(length, timeout=timeout) if length else b""
            if masked and mask_key:
                data = bytes(b ^ mask_key[i & 3] for i, b in enumerate(data))

            if opcode == 0x9:  # PING -> reply with masked PONG immediately
                self.send_frame(0xA, data)
                continue
            if opcode == 0xA:  # PONG
                continue
            if opcode == 0x8:  # CLOSE
                code = struct.unpack("!H", data[:2])[0] if len(data) >= 2 else 1000
                return code, None

            fragments.append(data)
            if fin:
                full_bytes = b"".join(fragments)
                fragments.clear()
                if opcode in (0x1, 0x0):
                    return None, json.loads(full_bytes.decode("utf-8"))

    def close(self, code: int = 1000):
        if self._closed:
            return
        self._closed = True
        try:
            self.send_frame(0x8, struct.pack("!H", code))
        except Exception:
            pass
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None


class DiscordBotRunner:
    """Zero-dependency Discord Bot API (Gateway v10 WSS + REST v10) runner."""

    API_BASE = "https://discord.com/api/v10"
    INTENTS_FULL = (1 << 0) | (1 << 9) | (1 << 12) | (1 << 15)  # GUILDS | GUILD_MESSAGES | DIRECT_MESSAGES | MESSAGE_CONTENT
    INTENTS_DM_ONLY = (1 << 0) | (1 << 9) | (1 << 12)           # Fallback if privileged Message Content Intent disabled

    def __init__(self, token: str, db_manager=None, assistant_engine=None, allowed_channel_id: str = "", on_checkin=None):
        self.token = self.normalize_token(token)
        self.db = db_manager or DatabaseManager()
        self.engine = assistant_engine or AssistantEngine(self.db)
        self.allowed_channel_id = (allowed_channel_id or "").strip()
        self.on_checkin = on_checkin

        self._running = False
        self._thread = None
        self._ws = None
        self._seq = None
        self._intents = self.INTENTS_FULL
        self.bot_user_id = ""
        self.bot_username = ""
        self.last_error = ""

    @staticmethod
    def normalize_token(token: str) -> str:
        t = (token or "").strip()
        if t.lower().startswith("bot "):
            t = t[4:].strip()
        return t

    @property
    def is_running(self) -> bool:
        return self._running and self._thread is not None and self._thread.is_alive()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (https://github.com/life-os-excel-ai, 2.0)",
        }

    @classmethod
    def verify_token(cls, token: str, lang: str = None) -> tuple:
        active_lang = resolve_language(lang)
        t = cls.normalize_token(token)
        if not t:
            return False, tr("dc_empty_token", active_lang)
        try:
            res = requests.get(
                f"{cls.API_BASE}/users/@me",
                headers={"Authorization": f"Bot {t}", "User-Agent": "DiscordBot (https://life-os, 2.0)"},
                timeout=8,
            )
            data = res.json() if res.content else {}
            if res.status_code == 200 and data.get("id"):
                uname = data.get("username", "unknown")
                return True, tr("dc_verify_ok", active_lang, uname=uname)
            return False, tr("dc_verify_fail", active_lang, detail=data.get("message", res.status_code))
        except Exception as e:
            return False, tr("dc_verify_err", active_lang, err=e)

    def _send_reply(self, channel_id: str, text: str):
        if not channel_id or not text:
            return
        try:
            requests.post(
                f"{self.API_BASE}/channels/{channel_id}/messages",
                headers=self._headers(),
                json={"content": text[:1990]},
                timeout=10,
            )
        except Exception:
            pass

    def handle_message_event(self, payload: dict):
        """Evaluate a Discord MESSAGE_CREATE payload and return (channel_id, reply_text) or None."""
        author = payload.get("author") or {}
        if author.get("bot"):
            return None
        if self.bot_user_id and str(author.get("id", "")) == self.bot_user_id:
            return None

        channel_id = str(payload.get("channel_id") or "").strip()
        if not channel_id:
            return None

        guild_id = payload.get("guild_id")
        raw_text = str(payload.get("content") or "").strip()
        if not raw_text:
            return None

        was_mentioned = False
        if self.bot_user_id:
            mention_pat = rf"^<@!?{re.escape(self.bot_user_id)}>\s*"
            if re.match(mention_pat, raw_text):
                was_mentioned = True
                raw_text = re.sub(mention_pat, "", raw_text, count=1).strip()

        if not raw_text:
            return None

        # Route gating:
        # 1) Direct Messages (guild_id is None): respond to every message naturally
        # 2) Configured dedicated server channel_id: respond to every message in that channel
        # 3) Other server channels: respond only when @mentioned or using '!' commands so normal chat isn't interrupted
        if guild_id:
            if self.allowed_channel_id:
                if channel_id != self.allowed_channel_id:
                    return None
            elif not (was_mentioned or raw_text.startswith("!")):
                return None

        reply = process_bot_message(
            self.db,
            self.engine,
            raw_text,
            channel="Discord Bot",
            on_checkin=self.on_checkin,
            prefer_bang=bool(guild_id and not self.allowed_channel_id),
        )
        return (channel_id, reply) if reply else None

    def _get_gateway_url(self) -> str:
        try:
            res = requests.get(f"{self.API_BASE}/gateway/bot", headers=self._headers(), timeout=8)
            if res.status_code == 200:
                url = res.json().get("url")
                if url:
                    sep = "&" if "?" in url else "?"
                    return f"{url}{sep}v=10&encoding=json"
        except Exception:
            pass
        return "wss://gateway.discord.gg/?v=10&encoding=json"

    def _connect_and_listen(self):
        wss_url = self._get_gateway_url()
        ws = _MinimalWebSocketClient()
        self._ws = ws
        ws.connect(wss_url, timeout=15)

        close_code, hello = ws.recv_json(timeout=15)
        if close_code is not None or not isinstance(hello, dict) or hello.get("op") != 10:
            raise ConnectionError(f"Expected Discord HELLO(10), got op={hello} close={close_code}")

        hb_interval = max(5.0, float((hello.get("d") or {}).get("heartbeat_interval", 41250)) / 1000.0)
        hb_stop = threading.Event()

        def _heartbeat_loop():
            while not hb_stop.is_set() and self._running:
                try:
                    ws.send_json({"op": 1, "d": self._seq})
                except Exception:
                    break
                hb_stop.wait(hb_interval)

        hb_thread = threading.Thread(target=_heartbeat_loop, daemon=True)
        hb_thread.start()

        # Identify session
        ws.send_json({
            "op": 2,
            "d": {
                "token": self.token,
                "intents": self._intents,
                "properties": {"os": "windows" if os.name == "nt" else "linux", "browser": "life_os", "device": "life_os"},
            },
        })

        try:
            while self._running:
                code, pkt = ws.recv_json(timeout=hb_interval + 15.0)
                if code is not None:
                    if code == 4004:
                        self.last_error = tr("dc_verify_fail", self.db.get_language(), detail="Invalid Token (4004)")
                        self._running = False
                        return
                    if code == 4014 and self._intents == self.INTENTS_FULL:
                        # Privileged Message Content Intent not turned on -> auto-fallback to DM-safe intents
                        self._intents = self.INTENTS_DM_ONLY
                        self.last_error = tr("dc_intent_hint", self.db.get_language())
                    break
                if not isinstance(pkt, dict):
                    continue

                if pkt.get("s") is not None:
                    self._seq = pkt["s"]

                op = pkt.get("op")
                if op == 1:
                    ws.send_json({"op": 1, "d": self._seq})
                elif op in (7, 9):
                    break
                elif op == 0:
                    ev = pkt.get("t")
                    data = pkt.get("d") or {}
                    if ev == "READY":
                        usr = data.get("user") or {}
                        self.bot_user_id = str(usr.get("id") or "")
                        self.bot_username = tr("dc_verify_ok", self.db.get_language(), uname=usr.get("username", "DiscordBot"))
                        if self._intents == self.INTENTS_FULL:
                            self.last_error = ""
                    elif ev == "MESSAGE_CREATE":
                        handled = self.handle_message_event(data)
                        if handled:
                            ch_id, reply = handled
                            self._send_reply(ch_id, reply)
        finally:
            hb_stop.set()
            ws.close()
            self._ws = None

    def _run_loop(self):
        ok, info = self.verify_token(self.token, lang=self.db.get_language())
        if not ok:
            self.last_error = info
            self._running = False
            return
        self.bot_username = info
        self.last_error = ""

        while self._running:
            try:
                self._connect_and_listen()
                if self._running:
                    time.sleep(2.0)
            except Exception as e:
                if self._running:
                    self.last_error = str(e)
                    time.sleep(4.0)

    def start(self) -> tuple:
        lang = self.db.get_language()
        if not self.token:
            return False, tr("dc_token_missing", lang)
        if self.is_running:
            return True, tr("dc_already_running", lang, name=self.bot_username or "Discord Bot")

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        return True, tr("dc_bg_started", lang)

    def stop(self):
        self._running = False
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
        self._thread = None
