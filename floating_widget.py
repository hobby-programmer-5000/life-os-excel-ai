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
        w, h = 370, 540
        x = screen_w - w - 40
        y = max(40, screen_h - h - 70)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Modern Dark Color Palette
        self.c_bg = "#0F172A"
        self.c_card = "#1E293B"
        self.c_border = "#334155"
        self.c_text = "#F8FAFC"
        self.c_sub = "#94A3B8"
        self.c_accent = "#38BDF8"
        self.c_green = "#10B981"
        self.c_gold = "#F59E0B"
        self.c_purple = "#A855F7"

        self.root.configure(bg=self.c_bg)

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

        self.main_frame = tk.Frame(self.root, bg=self.c_bg, highlightbackground=self.c_accent, highlightthickness=1)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Top Header Bar
        header = tk.Frame(self.main_frame, bg=self.c_card, height=36)
        header.pack(fill=tk.X, padx=0, pady=0)

        title_box = tk.Frame(header, bg=self.c_card)
        title_box.pack(side=tk.LEFT, padx=10, pady=6)
        self.lbl_icon = tk.Label(title_box, text="🤖", font=("Segoe UI Emoji", 12), bg=self.c_card, fg=self.c_text)
        self.lbl_icon.pack(side=tk.LEFT)
        self.lbl_title = tk.Label(title_box, text=f" {get_app_name(lang)}", font=(f_fam, 10, "bold"), bg=self.c_card, fg=self.c_accent)
        self.lbl_title.pack(side=tk.LEFT)
        self.update_persona_header()

        btn_box = tk.Frame(header, bg=self.c_card)
        btn_box.pack(side=tk.RIGHT, padx=6)

        btn_settings = tk.Label(btn_box, text="⚙️", font=("Segoe UI Emoji", 10), bg=self.c_card, fg=self.c_sub, cursor="hand2")
        btn_settings.pack(side=tk.LEFT, padx=3)
        btn_settings.bind("<Button-1>", lambda e: self.open_settings_dialog())

        btn_min = tk.Label(btn_box, text="━", font=(f_fam, 9, "bold"), bg=self.c_card, fg=self.c_sub, cursor="hand2")
        btn_min.pack(side=tk.LEFT, padx=4)
        btn_min.bind("<Button-1>", lambda e: self.hide_to_tray())

        btn_close = tk.Label(btn_box, text="✕", font=(f_fam, 10, "bold"), bg=self.c_card, fg="#EF4444", cursor="hand2")
        btn_close.pack(side=tk.LEFT, padx=4)
        btn_close.bind("<Button-1>", lambda e: self.handle_close_button())

        # 2. Date Navigation Bar
        date_bar = tk.Frame(self.main_frame, bg=self.c_bg)
        date_bar.pack(fill=tk.X, padx=10, pady=(8, 4))

        self.btn_prev = tk.Button(date_bar, text=self._t("btn_prev_day"), font=(f_fam, 8), bg=self.c_card, fg=self.c_text,
                                  relief=tk.FLAT, padx=6, pady=2, cursor="hand2", command=lambda: self.navigate_date(-1))
        self.btn_prev.pack(side=tk.LEFT)

        self.lbl_date = tk.Label(date_bar, text="", font=(f_fam, 9, "bold"), bg=self.c_bg, fg=self.c_text)
        self.lbl_date.pack(side=tk.LEFT, expand=True)

        self.btn_next = tk.Button(date_bar, text=self._t("btn_next_day"), font=(f_fam, 8), bg=self.c_card, fg=self.c_text,
                                  relief=tk.FLAT, padx=6, pady=2, cursor="hand2", command=lambda: self.navigate_date(1))
        self.btn_next.pack(side=tk.RIGHT)

        self.btn_today = tk.Button(date_bar, text=self._t("btn_today"), font=(f_fam, 8), bg=self.c_card, fg=self.c_accent,
                                   relief=tk.FLAT, padx=5, pady=2, cursor="hand2", command=self.go_to_today)
        self.btn_today.pack(side=tk.RIGHT, padx=4)

        # 3. Active Nudge Card
        self.nudge_card = tk.Frame(self.main_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        self.nudge_card.pack(fill=tk.X, padx=10, pady=6)

        self.lbl_nudge_role = tk.Label(self.nudge_card, text=self._t("nudge_role_header"), font=(f_fam, 8, "bold"),
                                       bg=self.c_card, fg=self.c_gold, anchor="w")
        self.lbl_nudge_role.pack(fill=tk.X, padx=8, pady=(6, 2))

        self.lbl_nudge_text = tk.Label(self.nudge_card, text=self._t("nudge_loading"), font=(f_fam, 9),
                                       bg=self.c_card, fg=self.c_text, wraplength=325, justify=tk.LEFT)
        self.lbl_nudge_text.pack(fill=tk.X, padx=8, pady=4)

        self.btn_row = tk.Frame(self.nudge_card, bg=self.c_card)
        self.btn_row.pack(fill=tk.X, padx=8, pady=(4, 8))

        self.btn_done = tk.Button(self.btn_row, text=self._t("btn_done"), font=(f_fam, 8, "bold"),
                                  bg=self.c_green, fg="#FFFFFF", relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
                                  command=lambda: self.on_nudge_action("completed"))
        self.btn_done.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_doing = tk.Button(self.btn_row, text=self._t("btn_doing"), font=(f_fam, 8, "bold"),
                                   bg="#2563EB", fg="#FFFFFF", relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
                                   command=lambda: self.on_nudge_action("doing_now"))
        self.btn_doing.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_hold = tk.Button(self.btn_row, text=self._t("btn_hold"), font=(f_fam, 8),
                                  bg="#475569", fg="#FFFFFF", relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
                                  command=lambda: self.on_nudge_action("postponed"))
        self.btn_hold.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # 5 & 6. Pack bottom controls FIRST so long coaching messages never clip them
        footer = tk.Frame(self.main_frame, bg=self.c_bg)
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 6))

        btn_open = tk.Label(footer, text=self._t("btn_open_excel"), font=(f_fam, 7, "underline"), bg=self.c_bg, fg=self.c_green, cursor="hand2")
        btn_open.pack(side=tk.RIGHT, padx=(6, 0))
        btn_open.bind("<Button-1>", lambda e: self.open_excel_directly())

        btn_sync = tk.Label(footer, text=self._t("btn_sync"), font=(f_fam, 7, "underline"), bg=self.c_bg, fg=self.c_accent, cursor="hand2")
        btn_sync.pack(side=tk.RIGHT, padx=(6, 2))
        btn_sync.bind("<Button-1>", lambda e: self.manual_sync_excel())

        self.lbl_status = tk.Label(footer, text=self._t("status_auto_sync"), font=(f_fam, 7), bg=self.c_bg, fg=self.c_sub, anchor="w")
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 5. Natural Language Check-in Box
        input_box_frame = tk.Frame(self.main_frame, bg=self.c_card)
        input_box_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(4, 6))

        btn_send = tk.Button(input_box_frame, text=self._t("btn_send"), font=(f_fam, 8, "bold"),
                             bg=self.c_accent, fg="#0F172A", relief=tk.FLAT, padx=8, pady=2, cursor="hand2",
                             command=self.submit_natural_checkin)
        btn_send.pack(side=tk.RIGHT, padx=(2, 4), pady=4)

        btn_help = tk.Button(input_box_frame, text="?", font=(f_fam, 8, "bold"),
                             bg="#334155", fg=self.c_gold, relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
                             command=self.open_keyword_help_dialog)
        btn_help.pack(side=tk.RIGHT, padx=(2, 0), pady=4)

        self.entry_checkin = tk.Entry(input_box_frame, font=(f_fam, 9), bg="#0F172A", fg=self.c_sub,
                                      insertbackground=self.c_text, relief=tk.FLAT, highlightbackground=self.c_border, highlightthickness=1)
        self.entry_checkin.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4), pady=4, ipady=3)
        self.entry_checkin.insert(0, self._placeholder)
        self.entry_checkin.bind("<FocusIn>", self._on_entry_focus_in)
        self.entry_checkin.bind("<FocusOut>", self._on_entry_focus_out)
        self.entry_checkin.bind("<Return>", lambda e: self.submit_natural_checkin())

        # 4. Habits Quick View / Checklist Container
        mid_label_bar = tk.Frame(self.main_frame, bg=self.c_bg)
        mid_label_bar.pack(fill=tk.X, padx=10, pady=(2, 2))

        self.lbl_habits_stat = tk.Label(mid_label_bar, text="", font=(f_fam, 8, "bold"),
                                        bg=self.c_bg, fg=self.c_accent)
        self.lbl_habits_stat.pack(side=tk.LEFT)

        self.btn_shuffle = tk.Button(mid_label_bar, text=self._t("btn_shuffle"), font=(f_fam, 7, "bold"),
                                     bg=self.c_card, fg=self.c_gold, relief=tk.FLAT, padx=4, pady=0, cursor="hand2",
                                     command=self.shuffle_quick_habits)
        self.btn_shuffle.pack(side=tk.LEFT, padx=6)

        btn_full_list = tk.Label(mid_label_bar, text=self._t("link_full_list"), font=(f_fam, 8, "underline"),
                                 bg=self.c_bg, fg=self.c_sub, cursor="hand2")
        btn_full_list.pack(side=tk.RIGHT)
        btn_full_list.bind("<Button-1>", lambda e: self.open_full_checklist_window())

        self.quick_list_frame = tk.Frame(self.main_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        self.quick_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        self._populate_quick_habits()

        self._build_context_menu()

    def _bind_mouse_events(self):
        for widget in [self.main_frame, self.lbl_title]:
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
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.c_card, fg=self.c_text, activebackground=self.c_accent, activeforeground="#0F172A")
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
        self.btn_today.config(text=today_txt, fg=self.c_sub if diff == 0 else self.c_accent)
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
            self.root.geometry(f"370x{req_h}+{x}+{y}")
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
            self.btn_shuffle.config(text=self._t("badge_all_scroll"), fg=self.c_accent, command=self.open_settings_dialog)
            display_ids = list(range(1, 36))
        else:
            self.btn_shuffle.config(text=self._t("btn_shuffle"), fg=self.c_gold, command=self.shuffle_quick_habits)
            self.custom_habit_ids = self._normalize_custom_ids(self.custom_habit_ids, limit)
            display_ids = self.custom_habit_ids

        use_scroll = (mode == "all_scroll") or (len(display_ids) > 5)

        if use_scroll:
            canvas_h = 195 if mode == "all_scroll" else min(195, max(120, len(display_ids) * 24))
            canvas = tk.Canvas(self.quick_list_frame, bg=self.c_card, highlightthickness=0, height=canvas_h)
            scrollbar = ttk.Scrollbar(self.quick_list_frame, orient="vertical", command=canvas.yview)
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

        for hid in display_ids:
            h = next((x for x in habits if x["id"] == hid), None)
            if not h:
                continue

            is_done = checks.get(hid, {}).get("status", 0) == 1
            row = tk.Frame(container, bg=self.c_card)
            row.pack(fill=tk.X, padx=6, pady=2)

            chk_txt = "☑" if is_done else "☐"
            chk_color = self.c_green if is_done else self.c_sub
            lbl_chk = tk.Label(row, text=chk_txt, font=(f_fam, 10, "bold"), bg=self.c_card, fg=chk_color, cursor="hand2")
            lbl_chk.pack(side=tk.LEFT, padx=(2, 6))
            lbl_chk.bind("<Button-1>", lambda e, habit_id=hid: self.toggle_habit(habit_id))

            prefix = f"{hid}. " if mode == "all_scroll" else ""
            lbl_name = tk.Label(row, text=f"{prefix}[{h['category']}] {h['name']}", font=(f_fam, 8),
                                bg=self.c_card, fg=self.c_text if not is_done else self.c_sub, anchor="w", cursor="hand2")
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
            self._set_status(f"⚡ {msg}")
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
            self.lbl_nudge_text.config(text=f"📱 [{channel}]\n{coaching}")
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
            self.entry_checkin.config(fg=self.c_sub)

    def submit_natural_checkin(self):
        text = self.entry_checkin.get().strip()
        if not text or text == self._placeholder:
            return

        date_str = self.current_date.isoformat()
        res = self.engine.process_natural_checkin(text, date_str, channel="Desktop Widget")
        self._sync_local_seq()
        self.entry_checkin.delete(0, tk.END)

        self.lbl_nudge_text.config(text=f"💬 {res['coaching']}")
        self._refresh_date_display()
        self._adjust_window_height()

    # --- Manual Excel Sync & Open ---
    def manual_sync_excel(self):
        ok, msg = self.db.sync_to_excel()
        self._set_status(f"⚡ {msg}")
        if ok:
            messagebox.showinfo(self._t("dlg_excel_sync_title"), self._t("dlg_excel_sync_ok_body", msg=msg), parent=self.root)
        else:
            messagebox.showwarning(self._t("dlg_excel_sync_warn_title"), msg, parent=self.root)

    def open_excel_directly(self):
        ok, msg = self.db.open_excel_file()
        self._set_status(f"📂 {msg}")
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
        date_str = self.current_date.isoformat()
        win.title(self._t("full_win_title", app_name=get_app_name(lang), date=date_str))
        win.geometry("560x660")
        win.configure(bg=self.c_bg)
        win.attributes("-topmost", True)

        checks = self.db.get_checks_for_date(date_str)
        limit = self._get_quick_habit_limit()
        completed_count = sum(1 for hid in range(1, 36) if checks.get(hid, {}).get("status", 0) == 1)

        header_lbl = tk.Label(win, text=self._t("full_header", date=date_str, done=completed_count),
                              font=(f_fam, 10, "bold"), bg=self.c_card, fg=self.c_accent, pady=8)
        header_lbl.pack(fill=tk.X)

        sub_lbl = tk.Label(win, text=self._t("full_sub", limit=limit),
                           font=(f_fam, 8), bg=self.c_card, fg=self.c_sub, pady=3)
        sub_lbl.pack(fill=tk.X)

        canvas = tk.Canvas(win, bg=self.c_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.c_bg)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=520)
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
                    fg=self.c_gold if is_pinned else self.c_sub,
                )

        def toggle_pin_habit(target_hid):
            cur_limit = self._get_quick_habit_limit()
            if target_hid in self.custom_habit_ids:
                if len(self.custom_habit_ids) > 1:
                    self.custom_habit_ids.remove(target_hid)
                    sub_lbl.config(text=self._t("pin_removed", hid=target_hid, cur=len(self.custom_habit_ids), limit=cur_limit), fg=self.c_sub)
                else:
                    sub_lbl.config(text=self._t("pin_min_warn"), fg=self.c_gold)
            else:
                while len(self.custom_habit_ids) >= cur_limit:
                    self.custom_habit_ids.pop()
                self.custom_habit_ids.insert(0, target_hid)
                sub_lbl.config(text=self._t("pin_added", hid=target_hid, cur=len(self.custom_habit_ids), limit=cur_limit), fg=self.c_green)
            self._save_custom_habit_ids()
            self._populate_quick_habits()
            refresh_pin_styles()

        for h in self.engine.habits:
            hid = h["id"]
            is_done = checks.get(hid, {}).get("status", 0) == 1

            row = tk.Frame(scroll_frame, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
            row.pack(fill=tk.X, padx=4, pady=3)

            btn_chk = tk.Button(row, text=self._t("chk_done") if is_done else self._t("chk_todo"), font=(f_fam, 8, "bold"),
                                bg=self.c_green if is_done else "#475569", fg="#FFFFFF", relief=tk.FLAT, padx=6, pady=3,
                                cursor="hand2")
            btn_chk.pack(side=tk.LEFT, padx=6, pady=4)

            info_box = tk.Frame(row, bg=self.c_card)
            info_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4)

            lbl_title = tk.Label(info_box, text=f"No.{hid} [{h['category']}] {h['name']}", font=(f_fam, 9, "bold"),
                                 bg=self.c_card, fg=self.c_text if not is_done else self.c_sub, anchor="w", cursor="hand2")
            lbl_title.pack(fill=tk.X)

            kw_preview = ", ".join(h.get("keywords", [])[:5])
            lbl_kw = tk.Label(info_box, text=self._t("kw_preview_label", kws=kw_preview), font=(f_fam, 7),
                              bg=self.c_card, fg=self.c_sub, anchor="w")
            lbl_kw.pack(fill=tk.X)

            is_pinned = hid in self.custom_habit_ids
            btn_pin = tk.Label(row, text=self._t("pin_fixed") if is_pinned else self._t("pin_default"), font=(f_fam, 8, "bold"),
                               bg=self.c_card, fg=self.c_gold if is_pinned else self.c_sub, cursor="hand2", padx=4)
            btn_pin.pack(side=tk.RIGHT, padx=8)
            btn_pin.bind("<Button-1>", lambda e, th=hid: toggle_pin_habit(th))
            pin_widgets[hid] = btn_pin

            def make_handler(target_hid, b_widget, l_widget):
                def _do_toggle():
                    self.toggle_habit(target_hid)
                    now_checks = self.db.get_checks_for_date(self.current_date.isoformat())
                    now_done = now_checks.get(target_hid, {}).get("status", 0) == 1
                    b_widget.config(
                        text=self._t("chk_done") if now_done else self._t("chk_todo"),
                        bg=self.c_green if now_done else "#475569",
                    )
                    l_widget.config(fg=self.c_sub if now_done else self.c_text)
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
        win.title(self._t("kw_win_title"))
        win.geometry("500x580")
        win.configure(bg=self.c_bg)
        win.attributes("-topmost", True)

        tk.Label(win, text=self._t("kw_header"), font=(f_fam, 10, "bold"),
                 bg=self.c_card, fg=self.c_accent, pady=8).pack(fill=tk.X)

        tk.Label(
            win, text=self._t("kw_tip"),
            font=(f_fam, 8), bg=self.c_card, fg=self.c_sub, justify=tk.LEFT, wraplength=475, pady=5, padx=10,
        ).pack(fill=tk.X)

        search_bar = tk.Frame(win, bg=self.c_bg, padx=10, pady=6)
        search_bar.pack(fill=tk.X)
        tk.Label(search_bar, text=self._t("kw_search_lbl"), font=(f_fam, 8, "bold"), bg=self.c_bg, fg=self.c_text).pack(side=tk.LEFT)
        entry_filter = tk.Entry(search_bar, font=(f_fam, 9), bg=self.c_card, fg=self.c_text,
                                insertbackground=self.c_text, relief=tk.FLAT, highlightbackground=self.c_border, highlightthickness=1)
        entry_filter.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0), ipady=2)

        canvas = tk.Canvas(win, bg=self.c_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
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
                row.pack(fill=tk.X, padx=4, pady=2)

                t_lbl = tk.Label(row, text=f"No.{h['id']} [{h['category']}] {h['name']}", font=(f_fam, 8, "bold"),
                                 bg=self.c_card, fg=self.c_text, anchor="w", padx=8, pady=2, cursor="hand2")
                t_lbl.pack(fill=tk.X)

                k_lbl = tk.Label(row, text=f"🔑 {', '.join(kws)}", font=(f_fam, 8),
                                 bg=self.c_card, fg=self.c_gold, anchor="w", padx=8, pady=2, cursor="hand2")
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
            self.lbl_icon.config(text=persona["emoji"])
            self.lbl_title.config(text=f" Life OS [{persona['name']}]")
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
        win.title(self._t("set_win_title", app_name=app_name))
        dlg_h = min(715, self.root.winfo_screenheight() - 50)
        win.geometry(f"460x{dlg_h}")
        win.configure(bg=self.c_bg)
        win.attributes("-topmost", True)

        tk.Label(win, text=self._t("set_header", app_name=app_name), font=(f_fam, 11, "bold"),
                 bg=self.c_card, fg=self.c_accent, pady=8).pack(fill=tk.X)

        content = tk.Frame(win, bg=self.c_bg, padx=15, pady=8)
        content.pack(fill=tk.BOTH, expand=True)

        hk_box = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_accent, highlightthickness=1)
        hk_box.pack(fill=tk.X, pady=(0, 8), padx=2)
        tk.Label(hk_box, text=self._t("set_hotkey_lbl"), font=(f_fam, 9, "bold"),
                 bg=self.c_card, fg=self.c_accent).pack(side=tk.LEFT, padx=8, pady=4)
        tk.Label(hk_box, text=self._t("set_hotkey_desc"), font=(f_fam, 8),
                 bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT, padx=2, pady=4)

        # Language Selector Box (Default: Auto-detect OS language)
        l_frame = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_green, highlightthickness=1)
        l_frame.pack(fill=tk.X, pady=(0, 8), padx=2, ipady=3)
        tk.Label(l_frame, text=self._t("set_lang_lbl"), font=(f_fam, 9, "bold"),
                 bg=self.c_card, fg=self.c_green).pack(anchor="w", padx=8, pady=(4, 2))

        lang_options = get_language_options(lang)
        curr_lang_setting = self.db.get_setting("language", "auto")
        curr_lang_disp = next((lbl for code, lbl in lang_options if code == curr_lang_setting), lang_options[0][1])

        cmb_language = ttk.Combobox(l_frame, values=[lbl for _, lbl in lang_options], state="readonly", font=(f_fam, 9))
        cmb_language.set(curr_lang_disp)
        cmb_language.pack(fill=tk.X, padx=8, pady=(0, 4))

        # Persona Selector Box
        p_frame = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        p_frame.pack(fill=tk.X, pady=(0, 8), padx=2, ipady=3)
        tk.Label(p_frame, text=self._t("set_persona_lbl"), font=(f_fam, 9, "bold"),
                 bg=self.c_card, fg=self.c_gold).pack(anchor="w", padx=8, pady=(4, 2))

        persona_keys = ("huberman", "buffett", "musk_grok", "aurelius")
        persona_options = [(personas[k]["title"], k) for k in persona_keys]
        curr_p_key = self.db.get_setting("persona", "huberman")
        curr_disp = next((t[0] for t in persona_options if t[1] == curr_p_key), persona_options[0][0])

        cmb_persona = ttk.Combobox(p_frame, values=[t[0] for t in persona_options], state="readonly", font=(f_fam, 9))
        cmb_persona.set(curr_disp)
        cmb_persona.pack(fill=tk.X, padx=8, pady=(0, 4))

        # Checkboxes
        var_autostart = tk.BooleanVar(value=WindowsAutostartManager.is_autostart_enabled())
        tk.Checkbutton(content, text=self._t("set_chk_autostart"), variable=var_autostart,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_card,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        var_tray = tk.BooleanVar(value=self.db.get_setting("close_to_tray") == "true")
        tk.Checkbutton(content, text=self._t("set_chk_tray"), variable=var_tray,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_card,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        var_top = tk.BooleanVar(value=self.db.get_setting("always_on_top") == "true")
        tk.Checkbutton(content, text=self._t("set_chk_top"), variable=var_top,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_card,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        var_sound = tk.BooleanVar(value=self.db.get_setting("sound_enabled", "true") == "true")
        tk.Checkbutton(content, text=self._t("set_chk_sound"), variable=var_sound,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_card,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        var_toast = tk.BooleanVar(value=self.db.get_setting("toast_enabled", "true") == "true")
        tk.Checkbutton(content, text=self._t("set_chk_toast"), variable=var_toast,
                       font=(f_fam, 9), bg=self.c_bg, fg=self.c_text, selectcolor=self.c_card,
                       activebackground=self.c_bg, activeforeground=self.c_text).pack(anchor="w", pady=2)

        interval_frame = tk.Frame(content, bg=self.c_bg)
        interval_frame.pack(fill=tk.X, pady=3)
        tk.Label(interval_frame, text=self._t("set_interval_lbl"), font=(f_fam, 9), bg=self.c_bg, fg=self.c_text).pack(side=tk.LEFT)
        entry_interval = tk.Entry(interval_frame, width=6, font=(f_fam, 9))
        entry_interval.insert(0, self.db.get_setting("nudge_interval_minutes", "45"))
        entry_interval.pack(side=tk.LEFT, padx=8)

        opacity_frame = tk.Frame(content, bg=self.c_bg)
        opacity_frame.pack(fill=tk.X, pady=3)
        tk.Label(opacity_frame, text=self._t("set_opacity_lbl"), font=(f_fam, 9), bg=self.c_bg, fg=self.c_text).pack(side=tk.LEFT)

        try:
            init_opacity = max(0.30, min(1.00, float(self.db.get_setting("opacity", "0.94"))))
        except Exception:
            init_opacity = 0.94
        init_pct = int(round(init_opacity * 100))

        var_opacity_pct = tk.IntVar(value=init_pct)
        lbl_opacity_val = tk.Label(
            opacity_frame, text=f"{init_pct}%", width=5,
            font=(f_fam, 9, "bold"), bg=self.c_bg, fg=self.c_accent, anchor="e",
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
            bg=self.c_bg, fg=self.c_text,
            troughcolor=self.c_card, activebackground=self.c_accent,
            highlightthickness=0, sliderrelief=tk.FLAT,
        )
        scale_opacity.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 6))
        lbl_opacity_val.pack(side=tk.RIGHT)

        adv_frame = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_accent, highlightthickness=1)
        adv_frame.pack(fill=tk.X, pady=(6, 6), padx=2, ipady=4)

        tk.Label(adv_frame, text=self._t("set_adv_header"), font=(f_fam, 9, "bold"),
                 bg=self.c_card, fg=self.c_accent).pack(anchor="w", padx=8, pady=(5, 2))

        var_view_mode = tk.StringVar(value=self._get_quick_view_mode())
        limit_row = tk.Frame(adv_frame, bg=self.c_card)

        tk.Label(limit_row, text=self._t("set_adv_limit_lbl"), font=(f_fam, 8),
                 bg=self.c_card, fg=self.c_text).pack(side=tk.LEFT)
        entry_quick_limit = tk.Entry(limit_row, width=5, font=(f_fam, 9))
        entry_quick_limit.insert(0, str(self._get_quick_habit_limit()))
        entry_quick_limit.pack(side=tk.LEFT, padx=8)

        def sync_limit_state():
            entry_quick_limit.config(state=tk.NORMAL if var_view_mode.get() == "custom" else tk.DISABLED)

        tk.Radiobutton(
            adv_frame, text=self._t("set_adv_custom"),
            variable=var_view_mode, value="custom", command=sync_limit_state,
            font=(f_fam, 8), bg=self.c_card, fg=self.c_text,
            selectcolor=self.c_bg, activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(anchor="w", padx=8, pady=1)

        tk.Radiobutton(
            adv_frame, text=self._t("set_adv_all"),
            variable=var_view_mode, value="all_scroll", command=sync_limit_state,
            font=(f_fam, 8), bg=self.c_card, fg=self.c_text,
            selectcolor=self.c_bg, activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(anchor="w", padx=8, pady=1)

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

        tk.Button(btn_bar, text=self._t("set_btn_bot"), font=(f_fam, 9, "bold"),
                  bg=self.c_card, fg=self.c_gold, relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
                  command=self.open_bot_settings_dialog).pack(side=tk.LEFT)

        tk.Button(btn_bar, text=self._t("set_btn_save"), font=(f_fam, 9, "bold"),
                  bg=self.c_accent, fg="#0F172A", relief=tk.FLAT, padx=14, pady=5, cursor="hand2",
                  command=save_settings).pack(side=tk.RIGHT)

        win._save_settings = save_settings
        return win

    # --- Mobile Bot & LLM API Integration Settings ---
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
        win.title(self._t("bot_win_title"))
        dlg_h = min(740, self.root.winfo_screenheight() - 50)
        win.geometry(f"535x{dlg_h}")
        win.configure(bg=self.c_bg)
        win.attributes("-topmost", True)

        tk.Label(win, text=self._t("bot_header"), font=(f_fam, 10, "bold"), bg=self.c_card, fg=self.c_accent, pady=8).pack(fill=tk.X)
        tk.Label(win, text=self._t("bot_path_guide"), font=(f_fam, 7), bg=self.c_card, fg=self.c_sub, pady=3).pack(fill=tk.X)

        # Save button placeholder packed at BOTTOM before scrollable middle frame so it is never clipped
        footer_bar = tk.Frame(win, bg=self.c_bg)
        footer_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=6)

        scroll_wrap = tk.Frame(win, bg=self.c_bg)
        scroll_wrap.pack(fill=tk.BOTH, expand=True, padx=(10, 4), pady=4)

        canvas = tk.Canvas(scroll_wrap, bg=self.c_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_wrap, orient="vertical", command=canvas.yview)
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
                            justify=tk.LEFT, anchor="w", padx=8, pady=5)
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

        # 1. Telegram Bot Settings (+ Anti-Impersonation Security Warning)
        tg_card = tk.Frame(body, bg=self.c_card, highlightbackground=self.c_green, highlightthickness=1)
        tg_card.pack(fill=tk.X, pady=(0, 8), ipady=4)

        tg_head = tk.Frame(tg_card, bg=self.c_card)
        tg_head.pack(fill=tk.X, padx=8, pady=(4, 2))

        var_tg_on = tk.BooleanVar(value=self.db.get_setting("telegram_enabled", "false") == "true")
        tk.Checkbutton(
            tg_head, text=self._t("bot_tg_chk"),
            variable=var_tg_on, font=(f_fam, 9, "bold"),
            bg=self.c_card, fg=self.c_text, selectcolor=self.c_bg,
            activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(side=tk.LEFT)

        tk.Button(
            tg_head, text=self._t("bot_tg_btn_botfather"), font=(f_fam, 7, "bold"),
            bg="#1D4ED8", fg="#FFFFFF", relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
            command=lambda: webbrowser.open("https://t.me/BotFather"),
        ).pack(side=tk.RIGHT)

        warn_box = tk.Frame(tg_card, bg="#451A03", highlightbackground=self.c_gold, highlightthickness=1)
        warn_box.pack(fill=tk.X, padx=10, pady=(2, 4))
        tk.Label(
            warn_box, text=self._t("bot_tg_warn"),
            font=(f_fam, 7, "bold"), bg="#451A03", fg="#FDE68A",
            justify=tk.LEFT, anchor="w", wraplength=455, padx=6, pady=4,
        ).pack(fill=tk.X)

        tk.Label(
            tg_card, text=self._t("bot_tg_steps"),
            font=(f_fam, 7), bg=self.c_card, fg=self.c_sub, justify=tk.LEFT, anchor="w", wraplength=465, padx=10,
        ).pack(fill=tk.X, pady=(0, 4))

        tg_row = tk.Frame(tg_card, bg=self.c_card)
        tg_row.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(tg_row, text="Bot Token:", font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_tg_tok = tk.Entry(tg_row, font=(f_fam, 8), show="*")
        entry_tg_tok.insert(0, self.db.get_setting("telegram_token", "") or os.getenv("TELEGRAM_BOT_TOKEN", ""))
        entry_tg_tok.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        def test_tg_token():
            from telegram_bot import TelegramBotRunner
            tok = entry_tg_tok.get().strip()
            active_lang = self._lang()
            run_async_check(
                btn_tg_test, self._t("bot_tg_btn_test"),
                self._t("bot_tg_test_ok_title"), self._t("bot_tg_test_warn_title"),
                lambda: TelegramBotRunner.verify_token(tok, lang=active_lang),
            )

        btn_tg_test = tk.Button(tg_row, text=self._t("bot_tg_btn_test"), font=(f_fam, 7, "bold"),
                                bg="#334155", fg=self.c_green, relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
                                command=test_tg_token)
        btn_tg_test.pack(side=tk.RIGHT)

        # 2. Discord Bot Settings (Built-in Gateway v10)
        dc_card = tk.Frame(body, bg=self.c_card, highlightbackground="#818CF8", highlightthickness=1)
        dc_card.pack(fill=tk.X, pady=(0, 8), ipady=4)

        dc_head = tk.Frame(dc_card, bg=self.c_card)
        dc_head.pack(fill=tk.X, padx=8, pady=(4, 2))

        var_dc_on = tk.BooleanVar(value=self.db.get_setting("discord_enabled", "false") == "true")
        tk.Checkbutton(
            dc_head, text=self._t("bot_dc_chk"),
            variable=var_dc_on, font=(f_fam, 9, "bold"),
            bg=self.c_card, fg=self.c_text, selectcolor=self.c_bg,
            activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(side=tk.LEFT)

        tk.Button(
            dc_head, text=self._t("bot_dc_btn_portal"), font=(f_fam, 7, "bold"),
            bg="#4F46E5", fg="#FFFFFF", relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
            command=lambda: webbrowser.open("https://discord.com/developers/applications"),
        ).pack(side=tk.RIGHT)

        dc_warn = tk.Frame(dc_card, bg="#1E1B4B", highlightbackground="#818CF8", highlightthickness=1)
        dc_warn.pack(fill=tk.X, padx=10, pady=(2, 4))
        tk.Label(
            dc_warn, text=self._t("bot_dc_warn"),
            font=(f_fam, 7, "bold"), bg="#1E1B4B", fg="#C7D2FE",
            justify=tk.LEFT, anchor="w", wraplength=455, padx=6, pady=4,
        ).pack(fill=tk.X)

        tk.Label(
            dc_card, text=self._t("bot_dc_steps"),
            font=(f_fam, 7), bg=self.c_card, fg=self.c_sub, justify=tk.LEFT, anchor="w", wraplength=465, padx=10,
        ).pack(fill=tk.X, pady=(0, 4))

        dc_row1 = tk.Frame(dc_card, bg=self.c_card)
        dc_row1.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(dc_row1, text="Bot Token:", font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_dc_tok = tk.Entry(dc_row1, font=(f_fam, 8), show="*")
        entry_dc_tok.insert(0, self.db.get_setting("discord_token", "") or os.getenv("DISCORD_BOT_TOKEN", ""))
        entry_dc_tok.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        def test_dc_token():
            from discord_bot import DiscordBotRunner
            tok = entry_dc_tok.get().strip()
            active_lang = self._lang()
            run_async_check(
                btn_dc_test, self._t("bot_dc_btn_test"),
                self._t("bot_dc_test_ok_title"), self._t("bot_dc_test_warn_title"),
                lambda: DiscordBotRunner.verify_token(tok, lang=active_lang),
            )

        btn_dc_test = tk.Button(dc_row1, text=self._t("bot_dc_btn_test"), font=(f_fam, 7, "bold"),
                                bg="#334155", fg="#A5B4FC", relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
                                command=test_dc_token)
        btn_dc_test.pack(side=tk.RIGHT)

        dc_row2 = tk.Frame(dc_card, bg=self.c_card)
        dc_row2.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(dc_row2, text=self._t("bot_dc_ch_lbl"), font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_dc_chan = tk.Entry(dc_row2, font=(f_fam, 8))
        entry_dc_chan.insert(0, self.db.get_setting("discord_channel_id", "") or os.getenv("DISCORD_CHANNEL_ID", ""))
        entry_dc_chan.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        # 3. Webhook Bridge Settings (Android HTTP Shortcuts · Wi-Fi iPhone)
        wh_card = tk.Frame(body, bg=self.c_card, highlightbackground=self.c_accent, highlightthickness=1)
        wh_card.pack(fill=tk.X, pady=(0, 8), ipady=4)

        var_wh_on = tk.BooleanVar(value=self.db.get_setting("webhook_enabled", "false") == "true")
        tk.Checkbutton(
            wh_card, text=self._t("bot_wh_chk"),
            variable=var_wh_on, font=(f_fam, 9, "bold"),
            bg=self.c_card, fg=self.c_text, selectcolor=self.c_bg,
            activebackground=self.c_card, activeforeground=self.c_text,
        ).pack(anchor="w", padx=8, pady=(4, 2))

        wh_row = tk.Frame(wh_card, bg=self.c_card)
        wh_row.pack(fill=tk.X, padx=12, pady=2)
        tk.Label(wh_row, text="Host:", font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_host = tk.Entry(wh_row, width=14, font=(f_fam, 8))
        entry_host.insert(0, self.db.get_setting("webhook_host", "127.0.0.1"))
        entry_host.pack(side=tk.LEFT, padx=(4, 10))

        tk.Label(wh_row, text="Port:", font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_port = tk.Entry(wh_row, width=6, font=(f_fam, 8))
        entry_port.insert(0, self.db.get_setting("webhook_port", "8080"))
        entry_port.pack(side=tk.LEFT, padx=4)

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

        btn_wh_test = tk.Button(wh_row, text=self._t("bot_wh_btn_test"), font=(f_fam, 7, "bold"),
                                bg="#334155", fg=self.c_accent, relief=tk.FLAT, padx=6, pady=2, cursor="hand2",
                                command=test_webhook_live)
        btn_wh_test.pack(side=tk.RIGHT)

        tk.Label(wh_card, text=self._t("bot_wh_tip"), font=(f_fam, 7), bg=self.c_card, fg=self.c_gold,
                 justify=tk.LEFT, wraplength=465).pack(anchor="w", padx=10, pady=(2, 2))

        # 4. LLM API Mode Settings
        llm_card = tk.Frame(body, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1)
        llm_card.pack(fill=tk.X, pady=(0, 8), ipady=4)

        win._bot_cards = {"telegram": tg_card, "discord": dc_card, "webhook": wh_card, "llm": llm_card}

        tk.Label(llm_card, text=self._t("bot_llm_hdr"), font=(f_fam, 8, "bold"),
                 bg=self.c_card, fg=self.c_gold).pack(anchor="w", padx=8, pady=(4, 2))

        llm_row1 = tk.Frame(llm_card, bg=self.c_card)
        llm_row1.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(llm_row1, text=self._t("bot_llm_provider"), font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        providers = ["mock", "grok", "openai", "gemini"]
        cmb_prov = ttk.Combobox(llm_row1, values=providers, state="readonly", width=12, font=(f_fam, 8))
        cur_prov = self.db.get_setting("llm_provider", "mock")
        cmb_prov.set(cur_prov if cur_prov in providers else "mock")
        cmb_prov.pack(side=tk.LEFT, padx=6)

        llm_row2 = tk.Frame(llm_card, bg=self.c_card)
        llm_row2.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(llm_row2, text="API Key:", font=(f_fam, 8), bg=self.c_card, fg=self.c_sub).pack(side=tk.LEFT)
        entry_api_key = tk.Entry(llm_row2, font=(f_fam, 8), show="*")
        entry_api_key.insert(0, self.db.get_setting("llm_api_key", ""))
        entry_api_key.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

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
            self.db.set_setting("llm_provider", cmb_prov.get())
            self.db.set_setting("llm_api_key", entry_api_key.get().strip())

            notes = []
            if self.on_bot_config_changed:
                notes = self.on_bot_config_changed() or []
            refresh_status_label()

            summary = "\n".join(f"• {n}" for n in notes) if notes else self._t("bot_saved_default")
            messagebox.showinfo(self._t("bot_saved_title"), summary, parent=win)

        tk.Button(footer_bar, text=self._t("bot_btn_apply"), font=(f_fam, 9, "bold"),
                  bg=self.c_accent, fg="#0F172A", relief=tk.FLAT, padx=14, pady=6, cursor="hand2",
                  command=save_bot_settings).pack()

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
