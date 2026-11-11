"""
=============================================================================
🌟 ALL-IN-ONE LIFE OS : Floating Assistant Widget (Tkinter Multilingual UI)
=============================================================================
1. 화면 어디든 드래그 가능한 세련된 반투명 플로팅 비서 위젯 (ko/en/ja/zh 4개 국어)
2. 능동적 랜덤 넛지 말풍선 & 3-상태 빠른 응답 ([✅ 완료], [🚀 지금 할게], [⏸️ 보류])
3. 날짜 자유 이동 (◀ 어제 / 오늘 / 내일 ▶) & 과거/미래 일지/메모 기록
4. 자연어 일과 즉시 입력 및 AI 비서 실시간 코칭
5. 설정 내 언어 즉시 전환 (기본: 시스템 언어 자동 감지) & 실시간 UI 재구성
=============================================================================
"""

import sys
import os
import json
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from i18n import (
    tr,
    get_app_name,
    get_ui_font,
    format_date_banner,
    format_date_nav_labels,
    get_language_options,
    resolve_language,
    LANGUAGE_LABELS,
)
from i18n_personas import get_personas
from app_icon import apply_tk_app_icon
from ui_theme import THEME, get_tk_lucide_icon

try:
    import winsound
except ImportError:
    winsound = None


def _bind_cross_platform_scroll(widget, canvas):
    """Bind mouse wheel scrolling across Windows, macOS, and Linux."""
    def _on_wheel(event):
        if not canvas.winfo_exists():
            return
        if sys.platform == "darwin":
            units = -1 if event.delta > 0 else (1 if event.delta < 0 else 0)
        else:
            units = int(-1 * (event.delta / 120)) if abs(event.delta) >= 120 else (-1 if event.delta > 0 else 1)
        if units:
            canvas.yview_scroll(units, "units")

    widget.bind("<MouseWheel>", _on_wheel)
    widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units") if canvas.winfo_exists() else None)
    widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units") if canvas.winfo_exists() else None)


if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class FloatingAssistantWidget:
    def __init__(self, root, db_manager, assistant_engine, on_minimize_to_tray=None, on_quit=None,
                 on_nudge_notify=None, on_bot_config_changed=None, get_bot_status=None,
                 on_language_changed=None):
        self.root = root
        self.db = db_manager
        self.engine = assistant_engine
        self.on_minimize_to_tray = on_minimize_to_tray
        self.on_quit = on_quit
        self.on_nudge_notify = on_nudge_notify
        self.on_bot_config_changed = on_bot_config_changed
        self.get_bot_status = get_bot_status
        self.on_language_changed = on_language_changed

        # State
        self.current_date = datetime.date.today()
        self.current_nudge_habit_id = None
        self._full_checklist_win = None
        self._keyword_help_win = None
        self._bot_settings_win = None
        self._quick_canvas = None
        self._quick_scroll_top = 0.0
        self._last_sync_seq, last_evt = self.db.get_sync_state()
        self._last_event_ts = (last_evt or {}).get("timestamp", "")
        self.custom_habit_ids = self._load_custom_habit_ids()
        self._drag_data = {"x": 0, "y": 0}
        self._placeholder = ""
        self.context_menu = None

        # Setup main floating window properties (follows detected/selected language)
        self.root.title(get_app_name(self._lang()))
        apply_tk_app_icon(self.root, cache_owner=self)
        if sys.platform.startswith("win"):
            self.root.overrideredirect(True)
        try:
            self.root.attributes("-topmost", True)
        except Exception:
            pass

        opacity = float(self.db.get_setting("opacity", "0.94"))
        try:
            self.root.attributes("-alpha", opacity)
        except Exception:
            pass

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        w, h = 392, 540
        x = screen_w - w - 40
        y = max(40, screen_h - h - 70)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Modern Minimal 60-30-10 Obsidian & Zinc Palette (see ui_theme.py)
        self.c_bg = THEME["bg"]
        self.c_card = THEME["card"]
        self.c_surface_alt = THEME["surface_alt"]
        self.c_border = THEME["border"]
        self.c_border_strong = THEME["border_strong"]
        self.c_text = THEME["text"]
        self.c_sub = THEME["sub"]
        self.c_muted = THEME["muted"]
        self.c_cta_bg = THEME["cta_bg"]
        self.c_cta_fg = THEME["cta_fg"]
        self.c_accent = THEME["accent"]
        self.c_green = THEME["green"]
        self.c_green_btn = THEME["green_btn"]
        self.c_gold = THEME["gold"]
        self.c_warn_bg = THEME["warn_bg"]
        self.c_warn_border = THEME["warn_border"]
        self.c_warn_fg = THEME["warn_fg"]

        self.root.configure(bg=self.c_bg)
        self._configure_ttk_styles()

        self._build_ui()
        self._bind_mouse_events()
        self._refresh_date_display()
        self.trigger_nudge()

        self._schedule_next_nudge()
        self._schedule_db_poll()

    def _lang(self) -> str:
        return self.db.get_language()

    def _font(self) -> str:
        return get_ui_font(self._lang())

    def _t(self, key: str, **kwargs) -> str:
        return tr(key, self._lang(), **kwargs)

    def _configure_ttk_styles(self):
        """Apply dark neutral clam styling for scrollbars and comboboxes."""
        try:
            style = ttk.Style(self.root)
            if "clam" in style.theme_names():
                style.theme_use("clam")
            style.configure(
                "Minimal.Vertical.TScrollbar",
                background=self.c_border,
                troughcolor=self.c_bg,
                bordercolor=self.c_bg,
                arrowcolor=self.c_sub,
                relief="flat",
                width=9,
            )
            style.map(
                "Minimal.Vertical.TScrollbar",
                background=[("active", self.c_border_strong)],
            )
            style.configure(
                "Minimal.TCombobox",
                fieldbackground=self.c_surface_alt,
                background=self.c_surface_alt,
                foreground=self.c_text,
                bordercolor=self.c_border,
                darkcolor=self.c_surface_alt,
                lightcolor=self.c_border,
                arrowcolor=self.c_sub,
                selectbackground=self.c_border_strong,
                selectforeground=self.c_text,
            )
            style.map(
                "Minimal.TCombobox",
                fieldbackground=[("readonly", self.c_surface_alt)],
                foreground=[("readonly", self.c_text)],
            )
            self.root.option_add("*TCombobox*Listbox.background", self.c_card)
            self.root.option_add("*TCombobox*Listbox.foreground", self.c_text)
            self.root.option_add("*TCombobox*Listbox.selectBackground", self.c_border_strong)
            self.root.option_add("*TCombobox*Listbox.selectForeground", self.c_text)
        except Exception:
            pass

    def _ico(self, name: str, size: int = 14, color: str = None, bg: str = None, stroke_width: float = 2.0):
        """Return a cached Lucide PhotoImage rendered cleanly on the target background."""
        return get_tk_lucide_icon(
            self,
            name,
            size=size,
            color=color or self.c_sub,
            bg=bg or self.c_card,
            stroke_width=stroke_width,
        )

    def _bind_hover(self, widget, bg_idle: str, bg_hover: str, fg_idle: str = None, fg_hover: str = None, icons: tuple = None):
        """Attach smooth hover transitions while preserving disabled button state."""
        def _enter(_e):
            try:
                if str(widget.cget("state")) == "disabled":
                    return
            except Exception:
                pass
            cfg = {"bg": bg_hover}
            if fg_hover:
                cfg["fg"] = fg_hover
            if icons:
                cfg["image"] = icons[1]
            widget.config(**cfg)

        def _leave(_e):
            cfg = {"bg": bg_idle}
            if fg_idle:
                cfg["fg"] = fg_idle
            if icons:
                cfg["image"] = icons[0]
            widget.config(**cfg)

        widget.bind("<Enter>", _enter)
        widget.bind("<Leave>", _leave)

    def _make_dark_entry(self, parent, width: int = 0, show: str = None, font_size: int = 9):
        """Create a uniform Modern Minimal dark Entry input with 1px hairline border."""
        kwargs = {
            "font": (self._font(), font_size),
            "bg": self.c_surface_alt,
            "fg": self.c_text,
            "insertbackground": self.c_text,
            "disabledbackground": self.c_card,
            "disabledforeground": self.c_muted,
            "relief": tk.FLAT,
            "highlightbackground": self.c_border,
            "highlightcolor": self.c_border_strong,
            "highlightthickness": 1,
        }
        if width > 0:
            kwargs["width"] = width
        if show:
            kwargs["show"] = show
        return tk.Entry(parent, **kwargs)

    def _make_dialog_header(self, win, icon_name: str, title: str, subtitle: str = None):
        """Build a unified Modern Minimal header band + 1px hairline separator for popups."""
        f_fam = self._font()
        head = tk.Frame(win, bg=self.c_card)
        head.pack(fill=tk.X)
        row = tk.Frame(head, bg=self.c_card)
        row.pack(fill=tk.X, padx=14, pady=(10, 4 if subtitle else 10))
        tk.Label(
            row,
            image=self._ico(icon_name, size=16, color=self.c_text, bg=self.c_card),
            bg=self.c_card,
        ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(
            row, text=title, font=(f_fam, 10, "bold"),
            bg=self.c_card, fg=self.c_text, anchor="w",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        lbl_sub = None
        if subtitle:
            lbl_sub = tk.Label(
                head, text=subtitle, font=(f_fam, 8),
                bg=self.c_card, fg=self.c_sub, justify=tk.LEFT, anchor="w", wraplength=510,
            )
            lbl_sub.pack(fill=tk.X, padx=14, pady=(0, 8))
        tk.Frame(win, bg=self.c_border, height=1).pack(fill=tk.X)
        return head, lbl_sub

    def _make_card_section_label(self, parent, icon_name: str, text: str, bg: str = None, padx: int = 10, pady=(6, 2)):
        """Build an inline monochrome icon + muted heading inside settings/bot cards."""
        bg = bg or self.c_card
        row = tk.Frame(parent, bg=bg)
        row.pack(fill=tk.X, padx=padx, pady=pady)
        tk.Label(row, image=self._ico(icon_name, size=13, color=self.c_sub, bg=bg), bg=bg).pack(side=tk.LEFT, padx=(0, 6))
        lbl = tk.Label(row, text=text, font=(self._font(), 8, "bold"), bg=bg, fg=self.c_text, anchor="w")
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return row, lbl

    def _close_child_popups(self):
        for attr in ("_full_checklist_win", "_keyword_help_win", "_bot_settings_win"):
            win = getattr(self, attr, None)
            if win and win.winfo_exists():
                try:
                    win.destroy()
                except Exception:
                    pass
            setattr(self, attr, None)

    def apply_language_change(self):
        """Hot-reload entire widget UI, SQLite catalog, autostart label, and tray when language switches."""
        new_lang = self._lang()
        self.engine.refresh_language()
        self.root.title(get_app_name(new_lang))
        self._close_child_popups()

        self._quick_canvas = None
        if getattr(self, "context_menu", None):
            try:
                self.context_menu.destroy()
            except Exception:
                pass
        if getattr(self, "main_frame", None) and self.main_frame.winfo_exists():
            self.main_frame.destroy()

        self._build_ui()
        self._bind_mouse_events()
        self._refresh_date_display()
        self.trigger_nudge()

        # Sync autostart registry display name if enabled
        if self.db.get_setting("autostart_enabled") == "true":
            from assistant_engine import WindowsAutostartManager
            WindowsAutostartManager.set_autostart(True, lang=new_lang)

        if self.on_language_changed:
            try:
                self.on_language_changed(new_lang)
            except Exception:
                pass

    def _build_ui(self):
        f_fam = self._font()
        lang = self._lang()
        self._placeholder = self._t("entry_placeholder")

        self.main_frame = tk.Frame(
            self.root, bg=self.c_bg,
            highlightbackground=self.c_border, highlightthickness=1,
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Top Header Bar (Calm Monochrome + Growth Graph Anchor)
        header = tk.Frame(self.main_frame, bg=self.c_card, height=40)
        header.pack(fill=tk.X, padx=0, pady=0)
        tk.Frame(self.main_frame, bg=self.c_border, height=1).pack(fill=tk.X)

        # Pack right-side window controls FIRST so long titles never clip them
        btn_box = tk.Frame(header, bg=self.c_card)
        btn_box.pack(side=tk.RIGHT, padx=(2, 6), pady=5)

        ico_set_idle = self._ico("settings", size=14, color=self.c_sub, bg=self.c_card)
        ico_set_hov = self._ico("settings", size=14, color=self.c_text, bg=self.c_surface_alt)
        btn_settings = tk.Label(btn_box, image=ico_set_idle, bg=self.c_card, cursor="hand2", padx=4, pady=4)
        btn_settings.pack(side=tk.LEFT, padx=1)
        btn_settings.bind("<Button-1>", lambda e: self.open_settings_dialog())
        self._bind_hover(btn_settings, self.c_card, self.c_surface_alt, icons=(ico_set_idle, ico_set_hov))

        ico_min_idle = self._ico("minus", size=14, color=self.c_sub, bg=self.c_card)
        ico_min_hov = self._ico("minus", size=14, color=self.c_text, bg=self.c_surface_alt)
        btn_min = tk.Label(btn_box, image=ico_min_idle, bg=self.c_card, cursor="hand2", padx=4, pady=4)
        btn_min.pack(side=tk.LEFT, padx=1)
        btn_min.bind("<Button-1>", lambda e: self.hide_to_tray())
        self._bind_hover(btn_min, self.c_card, self.c_surface_alt, icons=(ico_min_idle, ico_min_hov))

        ico_close_idle = self._ico("x", size=14, color=self.c_sub, bg=self.c_card)
        ico_close_hov = self._ico("x", size=14, color="#F87171", bg=self.c_surface_alt)
        btn_close = tk.Label(btn_box, image=ico_close_idle, bg=self.c_card, cursor="hand2", padx=4, pady=4)
        btn_close.pack(side=tk.LEFT, padx=1)
        btn_close.bind("<Button-1>", lambda e: self.handle_close_button())
        self._bind_hover(btn_close, self.c_card, self.c_surface_alt, icons=(ico_close_idle, ico_close_hov))

        title_box = tk.Frame(header, bg=self.c_card)
        title_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 4), pady=7)
        self.lbl_icon = tk.Label(
            title_box,
            image=self._ico("trending-up", size=16, color=self.c_green, bg=self.c_card),
            bg=self.c_card,
        )
        self.lbl_icon.pack(side=tk.LEFT, padx=(0, 6))
        self.lbl_title = tk.Label(
            title_box, text="Life OS",
            font=(f_fam, 9, "bold"), bg=self.c_card, fg=self.c_text,
        )
        self.lbl_title.pack(side=tk.LEFT)
        self.lbl_persona = tk.Label(
            title_box, text="",
            font=(f_fam, 8), bg=self.c_card, fg=self.c_sub, anchor="w",
        )
        self.lbl_persona.pack(side=tk.LEFT, padx=(5, 0))
        self.update_persona_header()

        # 2. Date Navigation Bar
        date_bar = tk.Frame(self.main_frame, bg=self.c_bg)
        date_bar.pack(fill=tk.X, padx=10, pady=(8, 4))

        self.btn_prev = tk.Button(
            date_bar, text=self._t("btn_prev_day"), font=(f_fam, 8),
            bg=self.c_card, fg=self.c_sub,
            activebackground=self.c_surface_alt, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=7, pady=2, cursor="hand2", command=lambda: self.navigate_date(-1),
        )
        self.btn_prev.pack(side=tk.LEFT)
        self._bind_hover(self.btn_prev, self.c_card, self.c_surface_alt, self.c_sub, self.c_text)

        self.lbl_date = tk.Label(date_bar, text="", font=(f_fam, 9, "bold"), bg=self.c_bg, fg=self.c_text)
        self.lbl_date.pack(side=tk.LEFT, expand=True)

        self.btn_next = tk.Button(
            date_bar, text=self._t("btn_next_day"), font=(f_fam, 8),
            bg=self.c_card, fg=self.c_sub,
            activebackground=self.c_surface_alt, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=7, pady=2, cursor="hand2", command=lambda: self.navigate_date(1),
        )
        self.btn_next.pack(side=tk.RIGHT)
        self._bind_hover(self.btn_next, self.c_card, self.c_surface_alt, self.c_sub, self.c_text)

        self.btn_today = tk.Button(
            date_bar, text=self._t("btn_today"), font=(f_fam, 8),
            bg=self.c_card, fg=self.c_muted,
            activebackground=self.c_surface_alt, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=6, pady=2, cursor="hand2", command=self.go_to_today,
        )
        self.btn_today.pack(side=tk.RIGHT, padx=4)

        # 3. Active Nudge Card (1 Primary CTA + 2 Restrained Ghost Actions)
        self.nudge_card = tk.Frame(
            self.main_frame, bg=self.c_card,
            highlightbackground=self.c_border, highlightthickness=1,
        )
        self.nudge_card.pack(fill=tk.X, padx=10, pady=6)

        role_row = tk.Frame(self.nudge_card, bg=self.c_card)
        role_row.pack(fill=tk.X, padx=9, pady=(7, 2))
        tk.Label(
            role_row,
            image=self._ico("bot", size=12, color=self.c_muted, bg=self.c_card),
            bg=self.c_card,
        ).pack(side=tk.LEFT, padx=(0, 5))
        self.lbl_nudge_role = tk.Label(
            role_row, text=self._t("nudge_role_header"), font=(f_fam, 8, "bold"),
            bg=self.c_card, fg=self.c_sub, anchor="w",
        )
        self.lbl_nudge_role.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lbl_nudge_text = tk.Label(
            self.nudge_card, text=self._t("nudge_loading"), font=(f_fam, 9),
            bg=self.c_card, fg=self.c_text, wraplength=322, justify=tk.LEFT, anchor="w",
        )
        self.lbl_nudge_text.pack(fill=tk.X, padx=9, pady=(3, 5))

        self.btn_row = tk.Frame(self.nudge_card, bg=self.c_card)
        self.btn_row.pack(fill=tk.X, padx=9, pady=(2, 8))

        self.btn_done = tk.Button(
            self.btn_row,
            image=self._ico("check", size=13, color="#FFFFFF", bg=self.c_green_btn),
            compound=tk.LEFT, text=f" {self._t('btn_done')}".lstrip(),
            font=(f_fam, 8, "bold"),
            bg=self.c_green_btn, fg="#FFFFFF",
            activebackground=self.c_green, activeforeground="#FFFFFF",
            relief=tk.FLAT, bd=0, padx=7, pady=4, cursor="hand2",
            command=lambda: self.on_nudge_action("completed"),
        )
        # Keep exact text string on btn_done for i18n/regression test compatibility
        self.btn_done.config(text=self._t("btn_done"))
        self.btn_done.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        self._bind_hover(self.btn_done, self.c_green_btn, self.c_green)

        self.btn_doing = tk.Button(
            self.btn_row,
            image=self._ico("play", size=12, color=self.c_text, bg=self.c_surface_alt),
            compound=tk.LEFT, text=self._t("btn_doing"),
            font=(f_fam, 8),
            bg=self.c_surface_alt, fg=self.c_text,
            activebackground=self.c_border, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=7, pady=4, cursor="hand2",
            command=lambda: self.on_nudge_action("doing_now"),
        )
        self.btn_doing.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        self._bind_hover(self.btn_doing, self.c_surface_alt, self.c_border)

        self.btn_hold = tk.Button(
            self.btn_row,
            image=self._ico("clock", size=12, color=self.c_sub, bg=self.c_card),
            compound=tk.LEFT, text=self._t("btn_hold"),
            font=(f_fam, 8),
            bg=self.c_card, fg=self.c_sub,
            activebackground=self.c_surface_alt, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=7, pady=4, cursor="hand2",
            command=lambda: self.on_nudge_action("postponed"),
        )
        self.btn_hold.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self._bind_hover(self.btn_hold, self.c_card, self.c_surface_alt, self.c_sub, self.c_text)

        # 5 & 6. Pack bottom controls FIRST so long coaching messages never clip them
        footer = tk.Frame(self.main_frame, bg=self.c_bg)
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 7))

        ico_xlsx_idle = self._ico("file-spreadsheet", size=12, color=self.c_sub, bg=self.c_bg)
        ico_xlsx_hov = self._ico("file-spreadsheet", size=12, color=self.c_text, bg=self.c_bg)
        btn_open = tk.Label(
            footer, image=ico_xlsx_idle, compound=tk.LEFT,
            text=f" {self._t('btn_open_excel')}",
            font=(f_fam, 8), bg=self.c_bg, fg=self.c_sub, cursor="hand2",
        )
        btn_open.pack(side=tk.RIGHT, padx=(8, 0))
        btn_open.bind("<Button-1>", lambda e: self.open_excel_directly())
        self._bind_hover(btn_open, self.c_bg, self.c_bg, self.c_sub, self.c_text, icons=(ico_xlsx_idle, ico_xlsx_hov))

        ico_sync_idle = self._ico("refresh-cw", size=12, color=self.c_sub, bg=self.c_bg)
        ico_sync_hov = self._ico("refresh-cw", size=12, color=self.c_text, bg=self.c_bg)
        btn_sync = tk.Label(
            footer, image=ico_sync_idle, compound=tk.LEFT,
            text=f" {self._t('btn_sync')}",
            font=(f_fam, 8), bg=self.c_bg, fg=self.c_sub, cursor="hand2",
        )
        btn_sync.pack(side=tk.RIGHT, padx=(6, 4))
        btn_sync.bind("<Button-1>", lambda e: self.manual_sync_excel())
        self._bind_hover(btn_sync, self.c_bg, self.c_bg, self.c_sub, self.c_text, icons=(ico_sync_idle, ico_sync_hov))

        status_wrap = tk.Frame(footer, bg=self.c_bg)
        status_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(status_wrap, text="●", font=(f_fam, 7), bg=self.c_bg, fg=self.c_green).pack(side=tk.LEFT, padx=(0, 4))
        self.lbl_status = tk.Label(
            status_wrap, text=self._t("status_auto_sync"),
            font=(f_fam, 8), bg=self.c_bg, fg=self.c_muted, anchor="w",
        )
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 5. Natural Language Check-in Box (Single Crisp Monochrome CTA)
        input_box_frame = tk.Frame(
            self.main_frame, bg=self.c_card,
            highlightbackground=self.c_border, highlightthickness=1,
        )
        input_box_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(4, 6))

        btn_send = tk.Button(
            input_box_frame,
            image=self._ico("send-horizontal", size=12, color=self.c_cta_fg, bg=self.c_cta_bg),
            compound=tk.LEFT, text=self._t("btn_send"),
            font=(f_fam, 8, "bold"),
            bg=self.c_cta_bg, fg=self.c_cta_fg,
            activebackground="#FFFFFF", activeforeground=self.c_cta_fg,
            relief=tk.FLAT, bd=0, padx=9, pady=3, cursor="hand2",
            command=self.submit_natural_checkin,
        )
        btn_send.pack(side=tk.RIGHT, padx=(3, 5), pady=5)
        self._bind_hover(btn_send, self.c_cta_bg, "#FFFFFF")

        btn_help = tk.Button(
            input_box_frame, text="?", font=(f_fam, 8, "bold"),
            bg=self.c_surface_alt, fg=self.c_sub,
            activebackground=self.c_border, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=7, pady=3, cursor="hand2",
            command=self.open_keyword_help_dialog,
        )
        btn_help.pack(side=tk.RIGHT, padx=(2, 0), pady=5)
        self._bind_hover(btn_help, self.c_surface_alt, self.c_border, self.c_sub, self.c_text)

        self.entry_checkin = tk.Entry(
            input_box_frame, font=(f_fam, 9),
            bg=self.c_surface_alt, fg=self.c_muted,
            insertbackground=self.c_text, relief=tk.FLAT,
            highlightbackground=self.c_border, highlightcolor=self.c_border_strong, highlightthickness=1,
        )
        self.entry_checkin.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 4), pady=5, ipady=4)
        self.entry_checkin.insert(0, self._placeholder)
        self.entry_checkin.bind("<FocusIn>", self._on_entry_focus_in)
        self.entry_checkin.bind("<FocusOut>", self._on_entry_focus_out)
        self.entry_checkin.bind("<Return>", lambda e: self.submit_natural_checkin())

        # 4. Habits Quick View / Checklist Container
        mid_label_bar = tk.Frame(self.main_frame, bg=self.c_bg)
        mid_label_bar.pack(fill=tk.X, padx=10, pady=(4, 4))

        self.lbl_habits_stat = tk.Label(
            mid_label_bar, text="", font=(f_fam, 8, "bold"),
            bg=self.c_bg, fg=self.c_text,
        )
        self.lbl_habits_stat.pack(side=tk.LEFT)

        self._ico_shuffle = self._ico("shuffle", size=12, color=self.c_sub, bg=self.c_surface_alt)
        self._ico_all_scroll = self._ico("list-checks", size=12, color=self.c_text, bg=self.c_surface_alt)
        self.btn_shuffle = tk.Button(
            mid_label_bar, image=self._ico_shuffle, compound=tk.LEFT,
            text=self._t("btn_shuffle"), font=(f_fam, 8),
            bg=self.c_surface_alt, fg=self.c_sub,
            activebackground=self.c_border, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=6, pady=1, cursor="hand2",
            command=self.shuffle_quick_habits,
        )
        self.btn_shuffle.pack(side=tk.LEFT, padx=8)
        self._bind_hover(self.btn_shuffle, self.c_surface_alt, self.c_border, self.c_sub, self.c_text)

        ico_full_idle = self._ico("arrow-up-right", size=12, color=self.c_sub, bg=self.c_bg)
        ico_full_hov = self._ico("arrow-up-right", size=12, color=self.c_text, bg=self.c_bg)
        btn_full_list = tk.Label(
            mid_label_bar, image=ico_full_idle, compound=tk.RIGHT,
            text=f"{self._t('link_full_list')} ",
            font=(f_fam, 8), bg=self.c_bg, fg=self.c_sub, cursor="hand2",
        )
        btn_full_list.pack(side=tk.RIGHT)
        btn_full_list.bind("<Button-1>", lambda e: self.open_full_checklist_window())
        self._bind_hover(btn_full_list, self.c_bg, self.c_bg, self.c_sub, self.c_text, icons=(ico_full_idle, ico_full_hov))

        self.quick_list_frame = tk.Frame(
            self.main_frame, bg=self.c_card,
            highlightbackground=self.c_border, highlightthickness=1,
        )
        self.quick_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 4))
        self._populate_quick_habits()

        self._build_context_menu()

    def _bind_mouse_events(self):
        for widget in [self.main_frame, self.lbl_title, self.lbl_persona]:
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<ButtonRelease-1>", self._stop_drag)
            widget.bind("<B1-Motion>", self._on_drag)
            widget.bind("<Button-3>", self._show_context_menu)

    def _start_drag(self, event):
        self._drag_data["x"] = event.x_root - self.root.winfo_x()
        self._drag_data["y"] = event.y_root - self.root.winfo_y()

    def _stop_drag(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def _on_drag(self, event):
        x = event.x_root - self._drag_data["x"]
        y = event.y_root - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def _build_context_menu(self):
        self.context_menu = tk.Menu(
            self.root, tearoff=0,
            bg=self.c_card, fg=self.c_text,
            activebackground=self.c_surface_alt, activeforeground=self.c_text,
        )
        self.context_menu.add_command(label=self._t("menu_nudge"), command=self.trigger_nudge)
        self.context_menu.add_command(label=self._t("menu_full_list"), command=self.open_full_checklist_window)
        self.context_menu.add_command(label=self._t("menu_sync"), command=self.manual_sync_excel)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=self._t("menu_settings"), command=self.open_settings_dialog)
        self.context_menu.add_command(label=self._t("menu_bot_settings"), command=self.open_bot_settings_dialog)
        self.context_menu.add_command(label=self._t("menu_hide_tray"), command=self.hide_to_tray)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=self._t("menu_exit"), command=self.quit_app)

    def _show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    # --- Date Navigation ---
    def navigate_date(self, offset: int):
        self.current_date += datetime.timedelta(days=offset)
        self._refresh_date_display()

    def go_to_today(self):
        self.current_date = datetime.date.today()
        self._refresh_date_display()

    def _refresh_date_display(self):
        today = datetime.date.today()
        diff = (self.current_date - today).days
        lang = self._lang()
        self.lbl_date.config(text=format_date_banner(self.current_date, diff, lang))
        prev_txt, today_txt, next_txt = format_date_nav_labels(diff, lang)
        self.btn_prev.config(text=prev_txt)
        today_fg = self.c_muted if diff == 0 else self.c_text
        self.btn_today.config(text=today_txt, fg=today_fg)
        self._bind_hover(self.btn_today, self.c_card, self.c_surface_alt, today_fg, self.c_text)
        self.btn_next.config(text=next_txt)
        self._populate_quick_habits()

    def _get_quick_view_mode(self):
        mode = self.db.get_setting("quick_view_mode", "custom")
        return mode if mode in ("custom", "all_scroll") else "custom"

    def _get_quick_habit_limit(self):
        try:
            limit = int(self.db.get_setting("quick_habit_limit", "5"))
            return max(1, min(35, limit))
        except Exception:
            return 5

    def _normalize_custom_ids(self, ids, limit):
        valid = []
        for x in ids:
            if isinstance(x, int) and 1 <= x <= 35 and x not in valid:
                valid.append(x)
        if len(valid) > limit:
            return valid[:limit]
        for cand in range(1, 36):
            if len(valid) >= limit:
                break
            if cand not in valid:
                valid.append(cand)
        return valid

    def _load_custom_habit_ids(self):
        limit = self._get_quick_habit_limit()
        raw = self.db.get_setting("custom_habit_ids", "")
        if raw:
            try:
                ids = json.loads(raw)
                return self._normalize_custom_ids(ids, limit)
            except Exception:
                pass
        return self._normalize_custom_ids([1, 2, 6, 11, 15], limit)

    def _save_custom_habit_ids(self):
        try:
            self.db.set_setting("custom_habit_ids", json.dumps(self.custom_habit_ids))
        except Exception:
            pass

    def _set_status(self, text: str):
        short_text = text if len(text) <= 34 else text[:31] + "..."
        self.lbl_status.config(text=short_text)

    def _adjust_window_height(self):
        try:
            self.root.update_idletasks()
            screen_h = self.root.winfo_screenheight()
            max_h = min(700, screen_h - 60)
            req_h = max(520, min(max_h, self.main_frame.winfo_reqheight() + 4))
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            if y + req_h > screen_h - 45:
                y = max(20, screen_h - req_h - 45)
            self.root.geometry(f"392x{req_h}+{x}+{y}")
        except Exception:
            pass

    def shuffle_quick_habits(self):
        import random
        limit = self._get_quick_habit_limit()
        date_str = self.current_date.isoformat()
        uncompleted = self.db.get_uncompleted_habits_for_date(date_str)
        all_ids = list(range(1, 36))

        if len(uncompleted) >= limit:
            new_ids = random.sample(uncompleted, limit)
        else:
            remaining = [hid for hid in all_ids if hid not in uncompleted]
            fill_count = limit - len(uncompleted)
            new_ids = uncompleted + random.sample(remaining, min(fill_count, len(remaining)))

        if self.current_nudge_habit_id and self.current_nudge_habit_id in all_ids:
            if self.current_nudge_habit_id not in new_ids and new_ids:
                new_ids[0] = self.current_nudge_habit_id

        self.custom_habit_ids = new_ids
        self._save_custom_habit_ids()
        self._populate_quick_habits()

    # --- Quick Habits Checklist ---
    def _populate_quick_habits(self):
        if self._quick_canvas and self._quick_canvas.winfo_exists():
            try:
                self._quick_scroll_top = self._quick_canvas.yview()[0]
            except Exception:
                self._quick_scroll_top = 0.0
        self._quick_canvas = None

        for widget in self.quick_list_frame.winfo_children():
            widget.destroy()

        f_fam = self._font()
        date_str = self.current_date.isoformat()
        checks = self.db.get_checks_for_date(date_str)
        mode = self._get_quick_view_mode()
        limit = self._get_quick_habit_limit()
        habits = self.engine.habits

        completed_count = sum(1 for hid in range(1, 36) if checks.get(hid, {}).get("status", 0) == 1)
        self.lbl_habits_stat.config(text=self._t("stats_header", done=completed_count, total=35))

        if mode == "all_scroll":
            self.btn_shuffle.config(
                image=self._ico_all_scroll, text=self._t("badge_all_scroll"),
                fg=self.c_text, command=self.open_settings_dialog,
            )
            display_ids = list(range(1, 36))
        else:
            self.btn_shuffle.config(
                image=self._ico_shuffle, text=self._t("btn_shuffle"),
                fg=self.c_sub, command=self.shuffle_quick_habits,
            )
            self.custom_habit_ids = self._normalize_custom_ids(self.custom_habit_ids, limit)
            display_ids = self.custom_habit_ids

        use_scroll = (mode == "all_scroll") or (len(display_ids) > 5)

        if use_scroll:
            canvas_h = 195 if mode == "all_scroll" else min(195, max(120, len(display_ids) * 24))
            canvas = tk.Canvas(self.quick_list_frame, bg=self.c_card, highlightthickness=0, height=canvas_h)
            scrollbar = ttk.Scrollbar(
                self.quick_list_frame, orient="vertical", command=canvas.yview,
                style="Minimal.Vertical.TScrollbar",
            )
            container = tk.Frame(canvas, bg=self.c_card)

            container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas_win = canvas.create_window((0, 0), window=container, anchor="nw")
            canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_win, width=e.width))
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self._quick_canvas = canvas

            _bind_cross_platform_scroll(canvas, canvas)
            _bind_cross_platform_scroll(container, canvas)
        else:
            container = self.quick_list_frame

        ico_checked = self._ico("square-check", size=14, color=self.c_green, bg=self.c_card)
        ico_unchecked = self._ico("square", size=14, color=self.c_muted, bg=self.c_card)

        for hid in display_ids:
            h = next((x for x in habits if x["id"] == hid), None)
            if not h:
                continue

            is_done = checks.get(hid, {}).get("status", 0) == 1
            row = tk.Frame(container, bg=self.c_card)
            row.pack(fill=tk.X, padx=7, pady=3)

            lbl_chk = tk.Label(
                row, image=ico_checked if is_done else ico_unchecked,
                bg=self.c_card, cursor="hand2",
            )
            lbl_chk.pack(side=tk.LEFT, padx=(1, 7))
            lbl_chk.bind("<Button-1>", lambda e, habit_id=hid: self.toggle_habit(habit_id))

            prefix = f"{hid}. " if mode == "all_scroll" else ""
            lbl_name = tk.Label(row, text=f"{prefix}[{h['category']}] {h['name']}", font=(f_fam, 8),
                                bg=self.c_card, fg=self.c_text if not is_done else self.c_muted, anchor="w", cursor="hand2")
            lbl_name.pack(side=tk.LEFT, fill=tk.X, expand=True)
            lbl_name.bind("<Button-1>", lambda e, habit_id=hid: self.toggle_habit(habit_id))

            if self._quick_canvas:
                _bind_cross_platform_scroll(row, self._quick_canvas)
                _bind_cross_platform_scroll(lbl_chk, self._quick_canvas)
                _bind_cross_platform_scroll(lbl_name, self._quick_canvas)

        if self._quick_canvas and self._quick_scroll_top > 0.0:
            self.root.update_idletasks()
            try:
                self._quick_canvas.yview_moveto(self._quick_scroll_top)
            except Exception:
                pass

    def _sync_local_seq(self):
        try:
            seq, evt = self.db.get_sync_state()
            self._last_sync_seq = seq
            if evt and evt.get("timestamp"):
                self._last_event_ts = evt["timestamp"]
        except Exception:
            pass

    def toggle_habit(self, habit_id: int):
        date_str = self.current_date.isoformat()
        self.db.toggle_check(date_str, habit_id)
        self._sync_local_seq()
        if self.db.get_setting("auto_sync_excel") == "true":
            _, msg = self.db.sync_to_excel()
            self._set_status(msg)
        self._refresh_date_display()

    def play_nudge_sound(self):
        if self.db.get_setting("sound_enabled", "true") == "true":
            try:
                if winsound:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                else:
                    self.root.bell()
            except Exception:
                pass

    # --- Nudge Logic ---
    def trigger_nudge(self, is_auto=False):
        date_str = self.current_date.isoformat()
        nudge_info = self.engine.get_smart_nudge(date_str)
        self.current_nudge_habit_id = nudge_info["habit_id"]

        self.lbl_nudge_text.config(text=nudge_info["question"])
        state_val = tk.DISABLED if nudge_info.get("all_done") else tk.NORMAL
        self.btn_done.config(state=state_val)
        self.btn_doing.config(state=state_val)
        self.btn_hold.config(state=state_val)

        self._adjust_window_height()

        if is_auto and not nudge_info.get("all_done"):
            self.play_nudge_sound()
            if self.on_nudge_notify and self.db.get_setting("toast_enabled", "true") == "true":
                title = self._t("toast_nudge_title", app_name=get_app_name(self._lang()))
                self.on_nudge_notify(title, nudge_info["question"])

    def on_nudge_action(self, action_type: str):
        if not self.current_nudge_habit_id:
            return
        date_str = self.current_date.isoformat()
        res = self.engine.process_nudge_response(self.current_nudge_habit_id, action_type, date_str)
        self._sync_local_seq()
        self.lbl_nudge_text.config(text=res["message"])
        self._refresh_date_display()
        self._adjust_window_height()

    def _schedule_next_nudge(self):
        try:
            mins = int(self.db.get_setting("nudge_interval_minutes", "45"))
        except Exception:
            mins = 45
        self.root.after(mins * 60 * 1000, self._on_periodic_nudge_timer)

    def _on_periodic_nudge_timer(self):
        self.trigger_nudge(is_auto=True)
        self.root.deiconify()
        self._schedule_next_nudge()

    # --- Live Remote Sync ---
    def _schedule_db_poll(self):
        self.root.after(2500, self._poll_remote_sync)

    def _poll_remote_sync(self):
        try:
            ok_x, excel_changes = self.db.check_and_pull_excel_if_modified()
            if ok_x and excel_changes > 0:
                self._sync_local_seq()
                self._set_status(self._t("status_excel_pulled", count=excel_changes))
                self._refresh_date_display()

            seq, evt = self.db.get_sync_state()
            if seq != self._last_sync_seq:
                self._last_sync_seq = seq
                if evt and evt.get("timestamp") and evt["timestamp"] != self._last_event_ts:
                    self._last_event_ts = evt["timestamp"]
                    self.handle_remote_checkin({
                        "channel": evt.get("channel", self._t("channel_mobile_bot")),
                        "coaching": evt.get("coaching", ""),
                        "matched_ids": evt.get("matched_ids", []),
                        "checked_habits": [],
                    })
                else:
                    self._refresh_date_display()
        except Exception:
            pass
        self._schedule_db_poll()

    def handle_remote_checkin(self, res: dict):
        self._sync_local_seq()
        channel = res.get("channel", self._t("channel_mobile_bot"))
        coaching = res.get("coaching", "")
        if coaching:
            self.lbl_nudge_text.config(text=f"[{channel}]\n{coaching}")
        self._set_status(self._t("status_remote_synced", channel=channel))
        self._refresh_date_display()
        self._adjust_window_height()

        matched = res.get("matched_ids") or []
        if matched:
            self.play_nudge_sound()
            if self.on_nudge_notify and self.db.get_setting("toast_enabled", "true") == "true":
                self.on_nudge_notify(
                    self._t("toast_remote_title", channel=channel),
                    self._t("toast_remote_body", count=len(matched)),
                )

    # --- Natural Language Check-in ---
    def _on_entry_focus_in(self, event):
        if self.entry_checkin.get() == self._placeholder:
            self.entry_checkin.delete(0, tk.END)
            self.entry_checkin.config(fg=self.c_text)

    def _on_entry_focus_out(self, event):
        if not self.entry_checkin.get().strip():
            self.entry_checkin.insert(0, self._placeholder)
            self.entry_checkin.config(fg=self.c_muted)

    def submit_natural_checkin(self):
        text = self.entry_checkin.get().strip()
        if not text or text == self._placeholder:
            return

        date_str = self.current_date.isoformat()
        res = self.engine.process_natural_checkin(text, date_str, channel="Desktop Widget")
        self._sync_local_seq()
        self.entry_checkin.delete(0, tk.END)

        self.lbl_nudge_text.config(text=res["coaching"])
        self._refresh_date_display()
        self._adjust_window_height()

    # --- Manual Excel Sync & Open ---
    def manual_sync_excel(self):
        ok, msg = self.db.sync_to_excel()
        self._set_status(msg)
        if ok:
            messagebox.showinfo(self._t("dlg_excel_sync_title"), self._t("dlg_excel_sync_ok_body", msg=msg), parent=self.root)
        else:
            messagebox.showwarning(self._t("dlg_excel_sync_warn_title"), msg, parent=self.root)

    def open_excel_directly(self):
        ok, msg = self.db.open_excel_file()
        self._set_status(msg)
        if not ok:
            messagebox.showwarning(self._t("dlg_excel_open_warn_title"), msg, parent=self.root)

    # --- Full 35 Checklist Window ---
    def open_full_checklist_window(self):
        if self._full_checklist_win and self._full_checklist_win.winfo_exists():
            self._full_checklist_win.lift()
            self._full_checklist_win.focus_force()
            return

        f_fam = self._font()
        lang = self._lang()
        win = tk.Toplevel(self.root)
        self._full_checklist_win = win
        apply_tk_app_icon(win, cache_owner=self)
        date_str = self.current_date.isoformat()
        win.title(self._t("full_win_title", app_name=get_app_name(lang), date=date_str))
        win.geometry("560x660")
        win.configure(bg=self.c_bg)
        win.attributes("-topmost", True)

        checks = self.db.get_checks_for_date(date_str)
        limit = self._get_quick_habit_limit()
        completed_count = sum(1 for hid in range(1, 36) if checks.get(hid, {}).get("status", 0) == 1)

        head = tk.Frame(win, bg=self.c_card)
        head.pack(fill=tk.X)
        head_row = tk.Frame(head, bg=self.c_card)
        head_row.pack(fill=tk.X, padx=14, pady=(10, 4))
        tk.Label(
            head_row, image=self._ico("list-checks", size=16, color=self.c_text, bg=self.c_card),
            bg=self.c_card,
        ).pack(side=tk.LEFT, padx=(0, 8))
        header_lbl = tk.Label(
            head_row, text=self._t("full_header", date=date_str, done=completed_count),
            font=(f_fam, 10, "bold"), bg=self.c_card, fg=self.c_text, anchor="w",
        )
        header_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        sub_lbl = tk.Label(
            head, text=self._t("full_sub", limit=limit),
            font=(f_fam, 8), bg=self.c_card, fg=self.c_sub, anchor="w",
        )
        sub_lbl.pack(fill=tk.X, padx=14, pady=(0, 9))
        tk.Frame(win, bg=self.c_border, height=1).pack(fill=tk.X)

        canvas = tk.Canvas(win, bg=self.c_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            win, orient="vertical", command=canvas.yview,
            style="Minimal.Vertical.TScrollbar",
        )
        scroll_frame = tk.Frame(canvas, bg=self.c_bg)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        scroll_cwin = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(scroll_cwin, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        _bind_cross_platform_scroll(win, canvas)
        _bind_cross_platform_scroll(canvas, canvas)
        _bind_cross_platform_scroll(scroll_frame, canvas)

        pin_widgets = {}

        def refresh_pin_styles():
            for pid, pw in pin_widgets.items():
                is_pinned = pid in self.custom_habit_ids
                pw.config(
                    text=self._t("pin_fixed") if is_pinned else self._t("pin_default"),
                    fg=self.c_text if is_pinned else self.c_muted,
                )

        def toggle_pin_habit(target_hid):
            cur_limit = self._get_quick_habit_limit()
            if target_hid in self.custom_habit_ids:
                if len(self.custom_habit_ids) > 1:
                    self.custom_habit_ids.remove(target_hid)
                    sub_lbl.config(text=self._t("pin_removed", hid=target_hid, cur=len(self.custom_habit_ids), limit=cur_limit), fg=self.c_sub)
                else:
                    sub_lbl.config(text=self._t("pin_min_warn"), fg=self.c_warn_fg)
            else:
                while len(self.custom_habit_ids) >= cur_limit:
                    self.custom_habit_ids.pop()
                self.custom_habit_ids.insert(0, target_hid)
                sub_lbl.config(text=self._t("pin_added", hid=target_hid, cur=len(self.custom_habit_ids), limit=cur_limit), fg=self.c_green)
            self._save_custom_habit_ids()
            self._populate_quick_habits()
            refresh_pin_styles()

        ico_done_chk = self._ico("check", size=12, color="#FFFFFF", bg=self.c_green_btn)
        ico_todo_chk = self._ico("square", size=12, color=self.c_muted, bg=self.c_surface_alt)

        for h in self.engine.habits:
            hid = h["id"]
            is_done = checks.get(hid, {}).get("status", 0) == 1

            row = tk.Frame(scroll_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
            row.pack(fill=tk.X, padx=4, pady=3)

            btn_chk = tk.Button(
                row,
                image=ico_done_chk if is_done else ico_todo_chk,
                compound=tk.LEFT,
                text=f" {self._t('chk_done') if is_done else self._t('chk_todo')}",
                font=(f_fam, 8, "bold"),
                bg=self.c_green_btn if is_done else self.c_surface_alt,
                fg="#FFFFFF" if is_done else self.c_sub,
                activebackground=self.c_green if is_done else self.c_border,
                activeforeground="#FFFFFF",
                relief=tk.FLAT, bd=0, padx=7, pady=3, cursor="hand2",
            )
            btn_chk.pack(side=tk.LEFT, padx=6, pady=5)

            is_pinned = hid in self.custom_habit_ids
            btn_pin = tk.Label(row, text=self._t("pin_fixed") if is_pinned else self._t("pin_default"), font=(f_fam, 8, "bold"),
                               bg=self.c_card, fg=self.c_text if is_pinned else self.c_muted, cursor="hand2", padx=4)
            btn_pin.pack(side=tk.RIGHT, padx=(4, 10))
            btn_pin.bind("<Button-1>", lambda e, th=hid: toggle_pin_habit(th))
            pin_widgets[hid] = btn_pin

            info_box = tk.Frame(row, bg=self.c_card)
            info_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4)

            lbl_title = tk.Label(info_box, text=f"No.{hid} [{h['category']}] {h['name']}", font=(f_fam, 9, "bold"),
                                 bg=self.c_card, fg=self.c_text if not is_done else self.c_muted,
                                 anchor="w", justify=tk.LEFT, wraplength=330, cursor="hand2")
            lbl_title.pack(fill=tk.X)

            kw_preview = ", ".join(h.get("keywords", [])[:5])
            lbl_kw = tk.Label(info_box, text=self._t("kw_preview_label", kws=kw_preview), font=(f_fam, 7),
                              bg=self.c_card, fg=self.c_sub, anchor="w", justify=tk.LEFT, wraplength=330)
            lbl_kw.pack(fill=tk.X)

            def make_handler(target_hid, b_widget, l_widget):
                def _do_toggle():
                    self.toggle_habit(target_hid)
                    now_checks = self.db.get_checks_for_date(self.current_date.isoformat())
                    now_done = now_checks.get(target_hid, {}).get("status", 0) == 1
                    b_widget.config(
                        image=ico_done_chk if now_done else ico_todo_chk,
                        text=f" {self._t('chk_done') if now_done else self._t('chk_todo')}",
                        bg=self.c_green_btn if now_done else self.c_surface_alt,
                        fg="#FFFFFF" if now_done else self.c_sub,
                    )
                    l_widget.config(fg=self.c_muted if now_done else self.c_text)
                    c_cnt = sum(1 for x in range(1, 36) if now_checks.get(x, {}).get("status", 0) == 1)
                    header_lbl.config(text=self._t("full_header", date=self.current_date.isoformat(), done=c_cnt))
                return _do_toggle

            h_func = make_handler(hid, btn_chk, lbl_title)
            btn_chk.config(command=h_func)
            lbl_title.bind("<Button-1>", lambda e, f=h_func: f())

    # --- In-App Keyword Help Popup ---
    def open_keyword_help_dialog(self):
        if self._keyword_help_win and self._keyword_help_win.winfo_exists():
            self._keyword_help_win.lift()
            self._keyword_help_win.focus_force()
            return

        f_fam = self._font()
        win = tk.Toplevel(self.root)
        self._keyword_help_win = win
        apply_tk_app_icon(win, cache_owner=self)
        win.title(self._t("kw_win_title"))
        win.geometry("500x580")
        win.configure(bg=self.c_bg)
        win.attributes("-topmost", True)

        self._make_dialog_header(win, "keyboard", self._t("kw_header"), subtitle=self._t("kw_tip"))

        search_bar = tk.Frame(win, bg=self.c_bg, padx=12, pady=8)
        search_bar.pack(fill=tk.X)
        tk.Label(search_bar, text=self._t("kw_search_lbl"), font=(f_fam, 8, "bold"), bg=self.c_bg, fg=self.c_sub).pack(side=tk.LEFT)
        entry_filter = self._make_dark_entry(search_bar, font_size=9)
        entry_filter.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0), ipady=3)

        canvas = tk.Canvas(win, bg=self.c_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview, style="Minimal.Vertical.TScrollbar")
        list_frame = tk.Frame(canvas, bg=self.c_bg)

        list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win = canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_win, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=(0, 10))

        _bind_cross_platform_scroll(win, canvas)
        _bind_cross_platform_scroll(canvas, canvas)
        _bind_cross_platform_scroll(list_frame, canvas)

        def insert_keyword_to_entry(kw):
            cur_val = self.entry_checkin.get()
            if cur_val == self._placeholder:
                self.entry_checkin.delete(0, tk.END)
                self.entry_checkin.config(fg=self.c_text)
                cur_val = ""
            prefix = f"{cur_val.strip()} " if cur_val.strip() else ""
            self.entry_checkin.delete(0, tk.END)
            self.entry_checkin.insert(0, self._t("kw_entry_suffix", prefix=prefix, sample=kw))
            self.entry_checkin.focus_force()

        def render_rows(query=""):
            for w in list_frame.winfo_children():
                w.destroy()
            q = query.strip().lower().replace(" ", "")
            for h in self.engine.habits:
                kws = h.get("keywords", [])
                haystack = f"{h['id']} {h['category']} {h['name']} {' '.join(kws)}".lower().replace(" ", "")
                if q and q not in haystack:
                    continue
                row = tk.Frame(list_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1, cursor="hand2")
                row.pack(fill=tk.X, padx=4, pady=3)

                t_lbl = tk.Label(row, text=f"No.{h['id']} [{h['category']}] {h['name']}", font=(f_fam, 8, "bold"),
                                 bg=self.c_card, fg=self.c_text, anchor="w", justify=tk.LEFT, wraplength=430,
                                 padx=9, pady=3, cursor="hand2")
                t_lbl.pack(fill=tk.X)

                k_lbl = tk.Label(row, text=", ".join(kws), font=(f_fam, 8),
                                 bg=self.c_card, fg=self.c_sub, anchor="w", justify=tk.LEFT, wraplength=430,
                                 padx=9, pady=3, cursor="hand2")
                k_lbl.pack(fill=tk.X)

                first_kw = kws[0] if kws else h["name"]
                for w_item in (row, t_lbl, k_lbl):
                    w_item.bind("<Button-1>", lambda e, sample=first_kw: insert_keyword_to_entry(sample))
                    _bind_cross_platform_scroll(w_item, canvas)

        render_rows()
        entry_filter.bind("<KeyRelease>", lambda e: render_rows(entry_filter.get()))

    def update_persona_header(self):
        try:
            persona = self.engine.get_current_persona()
            self.lbl_title.config(text="Life OS")
            if hasattr(self, "lbl_persona"):
                self.lbl_persona.config(text=f"· {persona['name']}")
        except Exception:
            pass

    # --- Settings Dialog (with Language Selector!) ---
    def open_settings_dialog(self):
        from assistant_engine import WindowsAutostartManager

        f_fam = self._font()
        lang = self._lang()
        app_name = get_app_name(lang)
        personas = get_personas(lang)

        win = tk.Toplevel(self.root)
        apply_tk_app_icon(win, cache_owner=self)
        win.title(self._t("set_win_title", app_name=app_name))
        dlg_h = min(730, self.root.winfo_screenheight() - 50)
        win.geometry(f"468x{dlg_h}")
        win.configure(bg=self.c_bg)
        win.attributes("-topmost", True)

        self._make_dialog_header(win, "settings", self._t("set_header", app_name=app_name))

        content = tk.Frame(win, bg=self.c_bg, padx=14, pady=10)
        content.pack(fill=tk.BOTH, expand=True)

        hk_box = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        hk_box.pack(fill=tk.X, pady=(0, 8), padx=2)
        tk.Label(
            hk_box, image=self._ico("keyboard", size=13, color=self.c_sub, bg=self.c_card),
            bg=self.c_card,
        ).pack(side=tk.LEFT, padx=(9, 6), pady=6)
        tk.Label(
            hk_box, text=self._t("set_hotkey_lbl"), font=(f_fam, 9, "bold"),
            bg=self.c_card, fg=self.c_text,
        ).pack(side=tk.LEFT, pady=6)
        tk.Label(
            hk_box, text=self._t("set_hotkey_desc"), font=(f_fam, 8),
            bg=self.c_card, fg=self.c_sub,
        ).pack(side=tk.LEFT, padx=6, pady=6)

        # Language Selector Box (Default: Auto-detect OS language)
        l_frame = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        l_frame.pack(fill=tk.X, pady=(0, 8), padx=2, ipady=4)
        self._make_card_section_label(l_frame, "globe", self._t("set_lang_lbl"))

        lang_options = get_language_options(lang)
        curr_lang_setting = self.db.get_setting("language", "auto")
        curr_lang_disp = next((lbl for code, lbl in lang_options if code == curr_lang_setting), lang_options[0][1])

        cmb_language = ttk.Combobox(
            l_frame, values=[lbl for _, lbl in lang_options],
            state="readonly", font=(f_fam, 9), style="Minimal.TCombobox",
        )
        cmb_language.set(curr_lang_disp)
        cmb_language.pack(fill=tk.X, padx=10, pady=(2, 4))

        # Persona Selector Box
        p_frame = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        p_frame.pack(fill=tk.X, pady=(0, 8), padx=2, ipady=4)
        self._make_card_section_label(p_frame, "bot", self._t("set_persona_lbl"))

        persona_keys = ("huberman", "buffett", "musk_grok", "aurelius")
        persona_options = [(personas[k]["title"], k) for k in persona_keys]
        curr_p_key = self.db.get_setting("persona", "huberman")
        curr_disp = next((t[0] for t in persona_options if t[1] == curr_p_key), persona_options[0][0])

        cmb_persona = ttk.Combobox(
            p_frame, values=[t[0] for t in persona_options],
            state="readonly", font=(f_fam, 9), style="Minimal.TCombobox",
        )
        cmb_persona.set(curr_disp)
        cmb_persona.pack(fill=tk.X, padx=10, pady=(2, 4))

        # Checkboxes
        var_autostart = tk.BooleanVar(value=WindowsAutostartManager.is_autostart_enabled())
        tk.Checkbutton(content, text=self._t("set_chk_autostart"), variable=var_autostart,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_surface_alt,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        var_tray = tk.BooleanVar(value=self.db.get_setting("close_to_tray") == "true")
        tk.Checkbutton(content, text=self._t("set_chk_tray"), variable=var_tray,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_surface_alt,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        var_top = tk.BooleanVar(value=self.db.get_setting("always_on_top") == "true")
        tk.Checkbutton(content, text=self._t("set_chk_top"), variable=var_top,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_surface_alt,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        var_sound = tk.BooleanVar(value=self.db.get_setting("sound_enabled", "true") == "true")
        tk.Checkbutton(content, text=self._t("set_chk_sound"), variable=var_sound,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_surface_alt,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        var_toast = tk.BooleanVar(value=self.db.get_setting("toast_enabled", "true") == "true")
        tk.Checkbutton(content, text=self._t("set_chk_toast"), variable=var_toast,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_surface_alt,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        interval_frame = tk.Frame(content, bg=self.c_bg)
        interval_frame.pack(fill=tk.X, pady=4)
        tk.Label(interval_frame, text=self._t("set_interval_lbl"), font=(f_fam, 9), bg=self.c_bg, fg=self.c_text).pack(side=tk.LEFT)
        entry_interval = self._make_dark_entry(interval_frame, width=6, font_size=9)
        entry_interval.insert(0, self.db.get_setting("nudge_interval_minutes", "45"))
        entry_interval.pack(side=tk.LEFT, padx=8, ipady=2)

        opacity_frame = tk.Frame(content, bg=self.c_bg)
        opacity_frame.pack(fill=tk.X, pady=4)
        tk.Label(opacity_frame, text=self._t("set_opacity_lbl"), font=(f_fam, 9), bg=self.c_bg, fg=self.c_text).pack(side=tk.LEFT)

        try:
            init_opacity = max(0.30, min(1.00, float(self.db.get_setting("opacity", "0.94"))))
        except Exception:
            init_opacity = 0.94
        init_pct = int(round(init_opacity * 100))

        var_opacity_pct = tk.IntVar(value=init_pct)
        lbl_opacity_val = tk.Label(
            opacity_frame, text=f"{init_pct}%", width=5,
            font=(f_fam, 9, "bold"), bg=self.c_bg, fg=self.c_text, anchor="e",
        )

        def on_opacity_slide(val_str):
            try:
                pct = max(30, min(100, int(float(val_str))))
            except Exception:
                pct = init_pct
            lbl_opacity_val.config(text=f"{pct}%")
            try:
                self.root.attributes("-alpha", pct / 100.0)
            except Exception:
                pass

        scale_opacity = tk.Scale(
            opacity_frame,
            from_=30, to=100,
            orient=tk.HORIZONTAL,
            resolution=1,
            variable=var_opacity_pct,
            command=on_opacity_slide,
            showvalue=False,
            bg=self.c_border_strong, fg=self.c_text,
            troughcolor=self.c_card, activebackground=self.c_cta_bg,
            highlightbackground=self.c_border, highlightthickness=1,
            sliderrelief=tk.FLAT, sliderlength=16, width=10,
        )
        scale_opacity.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 6))
        lbl_opacity_val.pack(side=tk.RIGHT)

        adv_frame = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        adv_frame.pack(fill=tk.X, pady=(6, 6), padx=2, ipady=4)

        self._make_card_section_label(adv_frame, "sliders-horizontal", self._t("set_adv_header"))

        var_view_mode = tk.StringVar(value=self._get_quick_view_mode())
        limit_row = tk.Frame(adv_frame, bg=self.c_card)

        tk.Label(limit_row, text=self._t("set_adv_limit_lbl"), font=(f_fam, 8),
                 bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_quick_limit = self._make_dark_entry(limit_row, width=5, font_size=9)
        entry_quick_limit.insert(0, str(self._get_quick_habit_limit()))
        entry_quick_limit.pack(side=tk.LEFT, padx=8, ipady=2)

        def sync_limit_state():
            entry_quick_limit.config(state=tk.NORMAL if var_view_mode.get() == "custom" else tk.DISABLED)

        tk.Radiobutton(
            adv_frame, text=self._t("set_adv_custom"),
            variable=var_view_mode, value="custom", command=sync_limit_state,
            font=(f_fam, 8), bg=self.c_card, fg=self.c_text,
            selectcolor=self.c_surface_alt, activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(anchor="w", padx=10, pady=1)

        tk.Radiobutton(
            adv_frame, text=self._t("set_adv_all"),
            variable=var_view_mode, value="all_scroll", command=sync_limit_state,
            font=(f_fam, 8), bg=self.c_card, fg=self.c_text,
            selectcolor=self.c_surface_alt, activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(anchor="w", padx=10, pady=1)

        limit_row.pack(fill=tk.X, padx=16, pady=(4, 4))
        sync_limit_state()

        # Expose control references cleanly for automated GUI regression testing
        win._cmb_language = cmb_language
        win._lang_options = lang_options
        win._scale_opacity = scale_opacity
        win._var_opacity_pct = var_opacity_pct
        win._lbl_opacity_val = lbl_opacity_val

        def cancel_settings():
            try:
                self.root.attributes("-alpha", init_opacity)
            except Exception:
                pass
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", cancel_settings)
        win._cancel_settings = cancel_settings

        def save_settings():
            sel_lang_disp = cmb_language.get()
            sel_lang_code = next((code for code, lbl in lang_options if lbl == sel_lang_disp), "auto")
            self.db.set_setting("language", sel_lang_code)
            new_lang = self._lang()

            sel_text = cmb_persona.get()
            sel_key = next((t[1] for t in persona_options if t[0] == sel_text), "huberman")
            self.db.set_setting("persona", sel_key)

            enable_auto = var_autostart.get()
            WindowsAutostartManager.set_autostart(enable_auto, lang=new_lang)
            self.db.set_setting("autostart_enabled", "true" if enable_auto else "false")
            self.db.set_setting("close_to_tray", "true" if var_tray.get() else "false")
            self.db.set_setting("always_on_top", "true" if var_top.get() else "false")
            self.db.set_setting("sound_enabled", "true" if var_sound.get() else "false")
            self.db.set_setting("toast_enabled", "true" if var_toast.get() else "false")
            self.root.attributes("-topmost", var_top.get())

            try:
                mins = int(entry_interval.get())
                self.db.set_setting("nudge_interval_minutes", str(mins))
            except Exception:
                pass

            try:
                op = round(max(0.30, min(1.00, var_opacity_pct.get() / 100.0)), 2)
                self.db.set_setting("opacity", str(op))
                self.root.attributes("-alpha", op)
            except Exception:
                pass

            new_mode = var_view_mode.get()
            self.db.set_setting("quick_view_mode", new_mode)
            try:
                new_limit = max(1, min(35, int(entry_quick_limit.get())))
                self.db.set_setting("quick_habit_limit", str(new_limit))
                self.custom_habit_ids = self._normalize_custom_ids(self.custom_habit_ids, new_limit)
                self._save_custom_habit_ids()
            except Exception:
                pass

            self.apply_language_change()

            new_personas = get_personas(new_lang)
            messagebox.showinfo(
                tr("set_saved_title", new_lang),
                tr("set_saved_body", new_lang, persona=new_personas[sel_key]["name"], lang_label=LANGUAGE_LABELS.get(new_lang, new_lang)),
                parent=win,
            )
            win.destroy()

        btn_bar = tk.Frame(content, bg=self.c_bg)
        btn_bar.pack(fill=tk.X, pady=8)

        btn_bot = tk.Button(
            btn_bar,
            image=self._ico("webhook", size=13, color=self.c_sub, bg=self.c_card),
            compound=tk.LEFT, text=f" {self._t('set_btn_bot')}",
            font=(f_fam, 9),
            bg=self.c_card, fg=self.c_sub,
            activebackground=self.c_surface_alt, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=10, pady=5, cursor="hand2",
            command=self.open_bot_settings_dialog,
        )
        btn_bot.pack(side=tk.LEFT)
        self._bind_hover(btn_bot, self.c_card, self.c_surface_alt, self.c_sub, self.c_text)

        btn_save = tk.Button(
            btn_bar, text=self._t("set_btn_save"), font=(f_fam, 9, "bold"),
            bg=self.c_cta_bg, fg=self.c_cta_fg,
            activebackground="#FFFFFF", activeforeground=self.c_cta_fg,
            relief=tk.FLAT, bd=0, padx=16, pady=5, cursor="hand2",
            command=save_settings,
        )
        btn_save.pack(side=tk.RIGHT)
        self._bind_hover(btn_save, self.c_cta_bg, "#FFFFFF")

        win._save_settings = save_settings
        return win

    # --- Mobile Bot & Webhook Bridge Settings ---
    def open_bot_settings_dialog(self):
        import threading
        import webbrowser

        if self._bot_settings_win and self._bot_settings_win.winfo_exists():
            self._bot_settings_win.lift()
            self._bot_settings_win.focus_force()
            return

        f_fam = self._font()
        win = tk.Toplevel(self.root)
        self._bot_settings_win = win
        apply_tk_app_icon(win, cache_owner=self)
        win.title(self._t("bot_win_title"))
        dlg_h = min(740, self.root.winfo_screenheight() - 50)
        win.geometry(f"565x{dlg_h}")
        win.configure(bg=self.c_bg)
        win.attributes("-topmost", True)

        self._make_dialog_header(win, "webhook", self._t("bot_header"), subtitle=self._t("bot_path_guide"))

        # Save button placeholder packed at BOTTOM before scrollable middle frame so it is never clipped
        footer_bar = tk.Frame(win, bg=self.c_bg)
        footer_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 10))

        scroll_wrap = tk.Frame(win, bg=self.c_bg)
        scroll_wrap.pack(fill=tk.BOTH, expand=True, padx=(10, 4), pady=6)

        canvas = tk.Canvas(scroll_wrap, bg=self.c_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            scroll_wrap, orient="vertical", command=canvas.yview,
            style="Minimal.Vertical.TScrollbar",
        )
        body = tk.Frame(canvas, bg=self.c_bg, padx=6, pady=4)

        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_win, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        _bind_cross_platform_scroll(win, canvas)
        _bind_cross_platform_scroll(canvas, canvas)
        _bind_cross_platform_scroll(body, canvas)

        def _bind_scroll_recursive(parent_widget):
            for child in parent_widget.winfo_children():
                _bind_cross_platform_scroll(child, canvas)
                _bind_scroll_recursive(child)

        def run_async_check(btn, idle_lbl, title_ok, title_warn, worker_fn):
            btn.config(text=self._t("bot_tg_testing"), state=tk.DISABLED)

            def _worker():
                ok, info = worker_fn()
                def _done():
                    if btn.winfo_exists():
                        btn.config(text=idle_lbl, state=tk.NORMAL)
                        if ok:
                            messagebox.showinfo(title_ok, info, parent=win)
                        else:
                            messagebox.showwarning(title_warn, info, parent=win)
                self.root.after(0, _done)

            threading.Thread(target=_worker, daemon=True).start()

        st_card = tk.Frame(body, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        st_card.pack(fill=tk.X, pady=(0, 8))
        lbl_live = tk.Label(st_card, text=self._t("bot_status_loading"), font=(f_fam, 8), bg=self.c_card, fg=self.c_sub,
                            justify=tk.LEFT, anchor="w", padx=10, pady=6)
        lbl_live.pack(fill=tk.X)

        def refresh_status_label():
            if self.get_bot_status:
                st = self.get_bot_status()
                w_icon = self._t("bot_running") if st.get("webhook_running") else self._t("bot_stopped")
                t_icon = self._t("bot_receiving") if st.get("telegram_running") else self._t("bot_stopped")
                d_icon = self._t("bot_receiving") if st.get("discord_running") else self._t("bot_stopped")
                lbl_live.config(text=self._t(
                    "bot_status_live",
                    w_icon=w_icon, w_url=st.get("webhook_url", ""),
                    t_icon=t_icon, t_info=st.get("telegram_info", ""),
                    d_icon=d_icon, d_info=st.get("discord_info", ""),
                ))
            else:
                lbl_live.config(text=self._t("bot_status_standalone"))

        refresh_status_label()

        ico_ext = self._ico("external-link", size=11, color=self.c_text, bg=self.c_surface_alt)

        # 1. Telegram Bot Settings (+ Anti-Impersonation Security Warning)
        tg_card = tk.Frame(body, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        tg_card.pack(fill=tk.X, pady=(0, 8), ipady=4)

        tg_head = tk.Frame(tg_card, bg=self.c_card)
        tg_head.pack(fill=tk.X, padx=8, pady=(6, 4))

        btn_tg_portal = tk.Button(
            tg_head, image=ico_ext, compound=tk.RIGHT,
            text=f"{self._t('bot_tg_btn_botfather')} ", font=(f_fam, 7, "bold"),
            bg=self.c_surface_alt, fg=self.c_text,
            activebackground=self.c_border, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=8, pady=3, cursor="hand2",
            command=lambda: webbrowser.open("https://t.me/BotFather"),
        )
        btn_tg_portal.pack(side=tk.RIGHT)
        self._bind_hover(btn_tg_portal, self.c_surface_alt, self.c_border)

        var_tg_on = tk.BooleanVar(value=self.db.get_setting("telegram_enabled", "false") == "true")
        tk.Checkbutton(
            tg_head, text=self._t("bot_tg_chk"),
            variable=var_tg_on, font=(f_fam, 9, "bold"),
            bg=self.c_card, fg=self.c_text, selectcolor=self.c_surface_alt,
            activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(side=tk.LEFT)

        warn_box = tk.Frame(tg_card, bg=self.c_warn_bg, highlightbackground=self.c_warn_border, highlightthickness=1)
        warn_box.pack(fill=tk.X, padx=10, pady=(2, 6))
        warn_inner = tk.Frame(warn_box, bg=self.c_warn_bg)
        warn_inner.pack(fill=tk.X, padx=8, pady=5)
        tk.Label(
            warn_inner, image=self._ico("info", size=13, color=self.c_warn_fg, bg=self.c_warn_bg),
            bg=self.c_warn_bg,
        ).pack(side=tk.LEFT, anchor="n", padx=(0, 7), pady=(2, 0))
        tk.Label(
            warn_inner, text=self._t("bot_tg_warn"),
            font=(f_fam, 7), bg=self.c_warn_bg, fg=self.c_text,
            justify=tk.LEFT, anchor="w", wraplength=430,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            tg_card, text=self._t("bot_tg_steps"),
            font=(f_fam, 7), bg=self.c_card, fg=self.c_sub, justify=tk.LEFT, anchor="w", wraplength=465, padx=10,
        ).pack(fill=tk.X, pady=(0, 5))

        tg_row = tk.Frame(tg_card, bg=self.c_card)
        tg_row.pack(fill=tk.X, padx=10, pady=3)
        tk.Label(tg_row, text="Bot Token:", font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_tg_tok = self._make_dark_entry(tg_row, show="*", font_size=8)
        entry_tg_tok.insert(0, self.db.get_setting("telegram_token", "") or os.getenv("TELEGRAM_BOT_TOKEN", ""))
        entry_tg_tok.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, ipady=2)

        def test_tg_token():
            from telegram_bot import TelegramBotRunner
            tok = entry_tg_tok.get().strip()
            active_lang = self._lang()
            run_async_check(
                btn_tg_test, self._t("bot_tg_btn_test"),
                self._t("bot_tg_test_ok_title"), self._t("bot_tg_test_warn_title"),
                lambda: TelegramBotRunner.verify_token(tok, lang=active_lang),
            )

        btn_tg_test = tk.Button(
            tg_row, text=self._t("bot_tg_btn_test"), font=(f_fam, 7, "bold"),
            bg=self.c_surface_alt, fg=self.c_text,
            activebackground=self.c_border, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=8, pady=3, cursor="hand2",
            command=test_tg_token,
        )
        btn_tg_test.pack(side=tk.RIGHT)
        self._bind_hover(btn_tg_test, self.c_surface_alt, self.c_border)

        # 2. Discord Bot Settings (Built-in Gateway v10)
        dc_card = tk.Frame(body, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        dc_card.pack(fill=tk.X, pady=(0, 8), ipady=4)

        dc_head = tk.Frame(dc_card, bg=self.c_card)
        dc_head.pack(fill=tk.X, padx=8, pady=(6, 4))

        btn_dc_portal = tk.Button(
            dc_head, image=ico_ext, compound=tk.RIGHT,
            text=f"{self._t('bot_dc_btn_portal')} ", font=(f_fam, 7, "bold"),
            bg=self.c_surface_alt, fg=self.c_text,
            activebackground=self.c_border, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=8, pady=3, cursor="hand2",
            command=lambda: webbrowser.open("https://discord.com/developers/applications"),
        )
        btn_dc_portal.pack(side=tk.RIGHT)
        self._bind_hover(btn_dc_portal, self.c_surface_alt, self.c_border)

        var_dc_on = tk.BooleanVar(value=self.db.get_setting("discord_enabled", "false") == "true")
        tk.Checkbutton(
            dc_head, text=self._t("bot_dc_chk"),
            variable=var_dc_on, font=(f_fam, 9, "bold"),
            bg=self.c_card, fg=self.c_text, selectcolor=self.c_surface_alt,
            activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(side=tk.LEFT)

        dc_warn = tk.Frame(dc_card, bg=self.c_warn_bg, highlightbackground=self.c_warn_border, highlightthickness=1)
        dc_warn.pack(fill=tk.X, padx=10, pady=(2, 6))
        dc_warn_inner = tk.Frame(dc_warn, bg=self.c_warn_bg)
        dc_warn_inner.pack(fill=tk.X, padx=8, pady=5)
        tk.Label(
            dc_warn_inner, image=self._ico("lock", size=13, color=self.c_warn_fg, bg=self.c_warn_bg),
            bg=self.c_warn_bg,
        ).pack(side=tk.LEFT, anchor="n", padx=(0, 7), pady=(2, 0))
        tk.Label(
            dc_warn_inner, text=self._t("bot_dc_warn"),
            font=(f_fam, 7), bg=self.c_warn_bg, fg=self.c_text,
            justify=tk.LEFT, anchor="w", wraplength=430,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            dc_card, text=self._t("bot_dc_steps"),
            font=(f_fam, 7), bg=self.c_card, fg=self.c_sub, justify=tk.LEFT, anchor="w", wraplength=465, padx=10,
        ).pack(fill=tk.X, pady=(0, 5))

        dc_row1 = tk.Frame(dc_card, bg=self.c_card)
        dc_row1.pack(fill=tk.X, padx=10, pady=3)
        tk.Label(dc_row1, text="Bot Token:", font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_dc_tok = self._make_dark_entry(dc_row1, show="*", font_size=8)
        entry_dc_tok.insert(0, self.db.get_setting("discord_token", "") or os.getenv("DISCORD_BOT_TOKEN", ""))
        entry_dc_tok.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, ipady=2)

        def test_dc_token():
            from discord_bot import DiscordBotRunner
            tok = entry_dc_tok.get().strip()
            active_lang = self._lang()
            run_async_check(
                btn_dc_test, self._t("bot_dc_btn_test"),
                self._t("bot_dc_test_ok_title"), self._t("bot_dc_test_warn_title"),
                lambda: DiscordBotRunner.verify_token(tok, lang=active_lang),
            )

        btn_dc_test = tk.Button(
            dc_row1, text=self._t("bot_dc_btn_test"), font=(f_fam, 7, "bold"),
            bg=self.c_surface_alt, fg=self.c_text,
            activebackground=self.c_border, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=8, pady=3, cursor="hand2",
            command=test_dc_token,
        )
        btn_dc_test.pack(side=tk.RIGHT)
        self._bind_hover(btn_dc_test, self.c_surface_alt, self.c_border)

        dc_row2 = tk.Frame(dc_card, bg=self.c_card)
        dc_row2.pack(fill=tk.X, padx=10, pady=3)
        tk.Label(dc_row2, text=self._t("bot_dc_ch_lbl"), font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_dc_chan = self._make_dark_entry(dc_row2, font_size=8)
        entry_dc_chan.insert(0, self.db.get_setting("discord_channel_id", "") or os.getenv("DISCORD_CHANNEL_ID", ""))
        entry_dc_chan.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, ipady=2)

        # 3. Webhook Bridge Settings (Android HTTP Shortcuts · Wi-Fi iPhone)
        wh_card = tk.Frame(body, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        wh_card.pack(fill=tk.X, pady=(0, 8), ipady=4)

        var_wh_on = tk.BooleanVar(value=self.db.get_setting("webhook_enabled", "false") == "true")
        tk.Checkbutton(
            wh_card, text=self._t("bot_wh_chk"),
            variable=var_wh_on, font=(f_fam, 9, "bold"),
            bg=self.c_card, fg=self.c_text, selectcolor=self.c_surface_alt,
            activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(anchor="w", padx=8, pady=(6, 4))

        wh_row = tk.Frame(wh_card, bg=self.c_card)
        wh_row.pack(fill=tk.X, padx=12, pady=3)
        tk.Label(wh_row, text="Host:", font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_host = self._make_dark_entry(wh_row, width=14, font_size=8)
        entry_host.insert(0, self.db.get_setting("webhook_host", "127.0.0.1"))
        entry_host.pack(side=tk.LEFT, padx=(4, 10), ipady=2)

        tk.Label(wh_row, text="Port:", font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_port = self._make_dark_entry(wh_row, width=6, font_size=8)
        entry_port.insert(0, self.db.get_setting("webhook_port", "8080"))
        entry_port.pack(side=tk.LEFT, padx=4, ipady=2)

        def test_webhook_live():
            import requests as _req
            h_val = entry_host.get().strip() or "127.0.0.1"
            target_host = "127.0.0.1" if h_val == "0.0.0.0" else h_val
            p_val = entry_port.get().strip() or "8080"
            if self.get_bot_status and not self.get_bot_status().get("webhook_running"):
                messagebox.showwarning(self._t("bot_wh_test_warn_title"), self._t("bot_wh_test_need_on"), parent=win)
                return
            url = f"http://{target_host}:{p_val}/stats"

            def _do():
                try:
                    res = _req.get(url, timeout=4)
                    if res.status_code == 200:
                        data = res.json()
                        return True, f"HTTP 200 OK ({url})\n{data.get('service', '')} · {data.get('persona', '')}"
                    return False, f"HTTP {res.status_code}: {url}"
                except Exception as e:
                    return False, f"{self._t('bot_wh_test_need_on')}\n({url}: {e})"

            run_async_check(btn_wh_test, self._t("bot_wh_btn_test"), self._t("bot_wh_test_ok_title"), self._t("bot_wh_test_warn_title"), _do)

        btn_wh_test = tk.Button(
            wh_row, text=self._t("bot_wh_btn_test"), font=(f_fam, 7, "bold"),
            bg=self.c_surface_alt, fg=self.c_text,
            activebackground=self.c_border, activeforeground=self.c_text,
            relief=tk.FLAT, bd=0, highlightbackground=self.c_border, highlightthickness=1,
            padx=8, pady=3, cursor="hand2",
            command=test_webhook_live,
        )
        btn_wh_test.pack(side=tk.RIGHT)
        self._bind_hover(btn_wh_test, self.c_surface_alt, self.c_border)

        tk.Label(wh_card, text=self._t("bot_wh_tip"), font=(f_fam, 7), bg=self.c_card, fg=self.c_sub,
                 justify=tk.LEFT, wraplength=465).pack(anchor="w", padx=10, pady=(3, 4))

        win._bot_cards = {"telegram": tg_card, "discord": dc_card, "webhook": wh_card}

        _bind_scroll_recursive(body)

        def save_bot_settings():
            self.db.set_setting("webhook_enabled", "true" if var_wh_on.get() else "false")
            self.db.set_setting("webhook_host", entry_host.get().strip() or "127.0.0.1")
            try:
                p_num = max(1024, min(65535, int(entry_port.get().strip())))
                self.db.set_setting("webhook_port", str(p_num))
            except Exception:
                self.db.set_setting("webhook_port", "8080")

            self.db.set_setting("discord_enabled", "true" if var_dc_on.get() else "false")
            self.db.set_setting("discord_token", entry_dc_tok.get().strip())
            self.db.set_setting("discord_channel_id", entry_dc_chan.get().strip())

            self.db.set_setting("telegram_enabled", "true" if var_tg_on.get() else "false")
            self.db.set_setting("telegram_token", entry_tg_tok.get().strip())

            notes = []
            if self.on_bot_config_changed:
                notes = self.on_bot_config_changed() or []
            refresh_status_label()

            summary = "\n".join(f"• {n}" for n in notes) if notes else self._t("bot_saved_default")
            messagebox.showinfo(self._t("bot_saved_title"), summary, parent=win)

        btn_apply = tk.Button(
            footer_bar, text=self._t("bot_btn_apply"), font=(f_fam, 9, "bold"),
            bg=self.c_cta_bg, fg=self.c_cta_fg,
            activebackground="#FFFFFF", activeforeground=self.c_cta_fg,
            relief=tk.FLAT, bd=0, padx=18, pady=6, cursor="hand2",
            command=save_bot_settings,
        )
        btn_apply.pack()
        self._bind_hover(btn_apply, self.c_cta_bg, "#FFFFFF")

    # --- Window Minimize & Close ---
    def handle_close_button(self):
        close_to_tray = self.db.get_setting("close_to_tray") == "true"
        if close_to_tray:
            self.hide_to_tray()
        else:
            self.quit_app()

    def hide_to_tray(self):
        self.root.withdraw()
        if self.on_minimize_to_tray:
            self.on_minimize_to_tray()

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self):
        if self.on_quit:
            self.on_quit()
        else:
            self.root.destroy()
            sys.exit(0)
