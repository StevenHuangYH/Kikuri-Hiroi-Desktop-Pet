#!/usr/bin/env python3
"""
UI Components
------------
Defines the floating hardware HUD window, dialogue speech bubble window,
and dynamic right-click context menu with Dark / Light mode support and rounded corners.
"""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from src.config import (
    TRANSPARENT_COLOR,
    ROWS_CONFIG,
    I18N,
    THEMES,
)

if TYPE_CHECKING:
    from src.pet_controller import KikuriDesktopPet


def draw_rounded_card(
    canvas: tk.Canvas,
    w: int,
    h: int,
    radius: int = 8,
    fill: str = "#17141f",
    outline: str = "#433256",
    width: int = 1,
) -> int:
    """Draw a smooth rounded rectangle card on a transparent canvas."""
    canvas.delete("card_bg")
    x1, y1 = 1, 1
    x2, y2 = w - 1, h - 1
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    poly_id = canvas.create_polygon(
        points,
        smooth=True,
        fill=fill,
        outline=outline,
        width=width,
        tags="card_bg",
    )
    canvas.tag_lower("card_bg")
    return poly_id


class HUDWindow:
    """Floating Windows 11 Fluent-style ultra-compact mini card displaying live CPU, RAM, and GPU."""

    def __init__(self, master: tk.Tk, theme: str = 'dark'):
        self.master = master
        self.theme = theme if theme in THEMES else 'dark'
        self.last_cpu = 0.0
        self.last_ram = 0.0
        self.last_gpu = 0.0

        self.window = tk.Toplevel(master)
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", True)
        self.window.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.window.config(bg=TRANSPARENT_COLOR)

        self.canvas = tk.Canvas(self.window, bg=TRANSPARENT_COLOR, highlightthickness=0)
        self.canvas.pack()

        t = THEMES[self.theme]

        # Compact inner container (no redundant headers, streamlined 3-row layout)
        self.inner = tk.Frame(
            self.canvas,
            bg=t['card_bg'],
            padx=6,
            pady=4,
        )

        font_label = ("Segoe UI", 8, "bold")
        font_val = ("Consolas", 8, "bold")

        # 1. CPU Row (Left: ● CPU, Right: Monospace tabular %)
        self.row_cpu = tk.Frame(self.inner, bg=t['card_bg'])
        self.row_cpu.pack(fill=tk.X, pady=0)
        self.lbl_cpu_name = tk.Label(
            self.row_cpu, text="● CPU", bg=t['card_bg'], fg=t['cpu'], font=font_label, anchor="w"
        )
        self.lbl_cpu_name.pack(side=tk.LEFT)
        self.lbl_cpu_val = tk.Label(
            self.row_cpu, text=" --%", bg=t['card_bg'], fg=t['cpu'], font=font_val, anchor="e"
        )
        self.lbl_cpu_val.pack(side=tk.RIGHT, padx=(2, 0))

        # 2. RAM Row (Left: ● RAM, Right: Monospace tabular %)
        self.row_ram = tk.Frame(self.inner, bg=t['card_bg'])
        self.row_ram.pack(fill=tk.X, pady=0)
        self.lbl_ram_name = tk.Label(
            self.row_ram, text="● RAM", bg=t['card_bg'], fg=t['ram'], font=font_label, anchor="w"
        )
        self.lbl_ram_name.pack(side=tk.LEFT)
        self.lbl_ram_val = tk.Label(
            self.row_ram, text=" --%", bg=t['card_bg'], fg=t['ram'], font=font_val, anchor="e"
        )
        self.lbl_ram_val.pack(side=tk.RIGHT, padx=(2, 0))

        # 3. GPU Row (Left: ● GPU, Right: Monospace tabular %)
        self.row_gpu = tk.Frame(self.inner, bg=t['card_bg'])
        self.row_gpu.pack(fill=tk.X, pady=0)
        self.lbl_gpu_name = tk.Label(
            self.row_gpu, text="● GPU", bg=t['card_bg'], fg=t['gpu'], font=font_label, anchor="w"
        )
        self.lbl_gpu_name.pack(side=tk.LEFT)
        self.lbl_gpu_val = tk.Label(
            self.row_gpu, text=" --%", bg=t['card_bg'], fg=t['gpu'], font=font_val, anchor="e"
        )
        self.lbl_gpu_val.pack(side=tk.RIGHT, padx=(2, 0))

        self.inner.update_idletasks()
        self.w = self.inner.winfo_reqwidth() + 4
        self.h = self.inner.winfo_reqheight() + 4
        self.canvas.config(width=self.w, height=self.h)
        draw_rounded_card(self.canvas, self.w, self.h, radius=8, fill=t['card_bg'], outline=t['border'])
        self.win_item = self.canvas.create_window(2, 2, window=self.inner, anchor="nw", width=self.w - 4)

        self.is_visible = True

    def set_theme(self, theme_name: str) -> None:
        """Switch theme dynamically between dark and light."""
        if theme_name not in THEMES:
            return
        self.theme = theme_name
        t = THEMES[self.theme]

        self.inner.config(bg=t['card_bg'])

        for row in (self.row_cpu, self.row_ram, self.row_gpu):
            row.config(bg=t['card_bg'])

        for widget in (
            self.lbl_cpu_name, self.lbl_cpu_val,
            self.lbl_ram_name, self.lbl_ram_val,
            self.lbl_gpu_name, self.lbl_gpu_val,
        ):
            widget.config(bg=t['card_bg'])

        self.update_metrics(self.last_cpu, self.last_ram, self.last_gpu)

    def update_metrics(self, cpu_pct: float, ram_pct: float, gpu_pct: float) -> None:
        """Update hardware metric labels with Kikuri Hiroi character-matched Fluent adaptive colors."""
        self.last_cpu = cpu_pct
        self.last_ram = ram_pct
        self.last_gpu = gpu_pct

        t = THEMES[self.theme]

        cpu_col = t['cpu'] if cpu_pct < 60 else (t['warn'] if cpu_pct < 85 else t['alert'])
        self.lbl_cpu_name.config(bg=t['card_bg'], fg=cpu_col)
        self.lbl_cpu_val.config(bg=t['card_bg'], text=f"{cpu_pct:3.0f}%", fg=cpu_col)

        ram_col = t['ram'] if ram_pct < 70 else (t['warn'] if ram_pct < 85 else t['alert'])
        self.lbl_ram_name.config(bg=t['card_bg'], fg=ram_col)
        self.lbl_ram_val.config(bg=t['card_bg'], text=f"{ram_pct:3.0f}%", fg=ram_col)

        gpu_col = t['gpu'] if gpu_pct < 60 else (t['warn'] if gpu_pct < 85 else t['alert'])
        self.lbl_gpu_name.config(bg=t['card_bg'], fg=gpu_col)
        self.lbl_gpu_val.config(bg=t['card_bg'], text=f"{gpu_pct:3.0f}%", fg=gpu_col)

        # High load overdrive border alert
        if cpu_pct >= 85 or ram_pct >= 90 or gpu_pct >= 85:
            draw_rounded_card(self.canvas, self.w, self.h, radius=8, fill=t['card_bg'], outline=t['border_alert'])
        else:
            draw_rounded_card(self.canvas, self.w, self.h, radius=8, fill=t['card_bg'], outline=t['border'])

    def update_position(self, pos_x: float, pos_y: float, cell_w: int) -> None:
        """Anchor HUD snugly right beside Kikuri's visible body bounds with boundary flipping."""
        screen_w = self.master.winfo_screenwidth()
        screen_h = self.master.winfo_screenheight()
        hud_w = self.w if hasattr(self, 'w') else 90
        hud_h = self.h if hasattr(self, 'h') else 69

        scale = cell_w / 192.0
        cell_h = int(208 * scale)

        # Kikuri character body is located horizontally between 32px and 160px of the 192px sprite cell
        kikuri_left = int(pos_x + 32 * scale)
        kikuri_right = int(pos_x + 160 * scale)

        # Position snugly to the left of Kikuri's body (just 2px gap)
        hud_x = kikuri_left - hud_w - 2
        if hud_x < 4:
            # Flip snugly to the right of Kikuri's body if near left screen boundary
            hud_x = kikuri_right + 2
        hud_x = max(4, min(screen_w - hud_w - 4, hud_x))

        # Align vertically alongside Kikuri's mid-body
        hud_y = int(pos_y + (cell_h - hud_h) // 2 + 10 * scale)
        hud_y = max(10, min(screen_h - hud_h - 40, hud_y))

        self.window.geometry(f"+{hud_x}+{hud_y}")

    def show(self) -> None:
        self.window.deiconify()
        self.is_visible = True

    def hide(self) -> None:
        self.window.withdraw()
        self.is_visible = False

    def destroy(self) -> None:
        try:
            self.window.destroy()
        except Exception:
            pass


class SpeechBubble:
    """Windows 11 Notification Toast styled speech bubble (dialogue text only, rounded card)."""

    def __init__(self, master: tk.Tk, theme: str = 'dark'):
        self.master = master
        self.theme = theme if theme in THEMES else 'dark'
        self.window = tk.Toplevel(master)
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", True)
        self.window.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.window.config(bg=TRANSPARENT_COLOR)

        self.canvas = tk.Canvas(self.window, bg=TRANSPARENT_COLOR, highlightthickness=0)
        self.canvas.pack()

        t = THEMES[self.theme]

        # Toast notification inner card containing only quotes
        self.inner = tk.Frame(
            self.canvas,
            bg=t['card_bg'],
            padx=12,
            pady=9,
        )

        # Dialogue text only (no name badge / desktop pet headers)
        self.lbl_text = tk.Label(
            self.inner,
            text="",
            bg=t['card_bg'],
            fg=t['text_primary'],
            font=("Microsoft YaHei UI", 9),
            wraplength=260,
            justify=tk.LEFT,
        )
        self.lbl_text.pack(anchor=tk.W)

        self.win_id = self.canvas.create_window(2, 2, window=self.inner, anchor="nw")
        self.current_w = 200
        self.current_h = 45

        self.window.withdraw()
        self.hide_timer = None

    def set_theme(self, theme_name: str) -> None:
        """Switch theme dynamically between dark and light."""
        if theme_name not in THEMES:
            return
        self.theme = theme_name
        t = THEMES[self.theme]
        self.inner.config(bg=t['card_bg'])
        self.lbl_text.config(bg=t['card_bg'], fg=t['text_primary'])

    def show_speech(
        self,
        text: str,
        pos_x: float,
        pos_y: float,
        cell_w: int,
        duration_ms: int = 3500,
        lang: str = 'jp',
    ) -> None:
        """Show dialogue text and schedule automatic dismissal."""
        t = THEMES[self.theme]
        self.lbl_text.config(text=text, bg=t['card_bg'], fg=t['text_primary'])

        self.inner.update_idletasks()
        self.current_w = max(140, self.inner.winfo_reqwidth() + 4)
        self.current_h = self.inner.winfo_reqheight() + 4

        self.canvas.config(width=self.current_w, height=self.current_h)
        draw_rounded_card(self.canvas, self.current_w, self.current_h, radius=8, fill=t['card_bg'], outline=t['border'])

        self.update_position(pos_x, pos_y, cell_w)
        self.window.deiconify()

        if self.hide_timer:
            self.master.after_cancel(self.hide_timer)
        self.hide_timer = self.master.after(duration_ms, self.hide)

    def update_position(self, pos_x: float, pos_y: float, cell_w: int) -> None:
        """Position speech bubble directly above the pet with screen boundary safety."""
        screen_w = self.master.winfo_screenwidth()
        bubble_w = self.current_w
        bubble_h = self.current_h

        b_x = int(pos_x + (cell_w - bubble_w) // 2)
        b_x = max(8, min(screen_w - bubble_w - 8, b_x))

        b_y = int(pos_y - bubble_h - 10)
        if b_y < 5:
            # If pet is near top of screen, flip bubble below pet
            b_y = int(pos_y + (cell_w * 208 // 192) + 8)
        self.window.geometry(f"+{b_x}+{b_y}")

    def hide(self) -> None:
        self.window.withdraw()

    def destroy(self) -> None:
        if self.hide_timer:
            try:
                self.master.after_cancel(self.hide_timer)
            except Exception:
                pass
        try:
            self.window.destroy()
        except Exception:
            pass


class FluentMenu:
    """Individual Windows 11 Fluent-styled popup menu card with Dark/Light theme and rounded corners."""

    def __init__(self, master: tk.Tk, parent_menu: FluentMenu | None = None, theme: str = 'dark'):
        self.master = master
        self.parent_menu = parent_menu
        self.theme = theme if theme in THEMES else 'dark'
        self.window: tk.Toplevel | None = None
        self.canvas: tk.Canvas | None = None
        self.inner: tk.Frame | None = None
        self.items: list[dict] = []
        self.active_submenu: FluentMenu | None = None
        self.active_item_index: int | None = None
        self.active_widgets: tuple | None = None
        self.hover_open_timer = None
        self.hover_close_timer = None
        self._global_click_bind_id = None
        self._outside_poll_timer = None

    def add_command(self, label: str, command=None, checked: bool = False) -> None:
        self.items.append({'type': 'command', 'label': label, 'command': command, 'checked': checked})

    def add_cascade(self, label: str, menu: FluentMenu) -> None:
        menu.parent_menu = self
        menu.theme = self.theme
        self.items.append({'type': 'cascade', 'label': label, 'menu': menu})

    def add_separator(self) -> None:
        self.items.append({'type': 'separator'})

    def _get_root_menu(self) -> FluentMenu:
        root = self
        while root.parent_menu:
            root = root.parent_menu
        return root

    def _get_all_menu_windows(self) -> list[tk.Toplevel]:
        windows = []
        def collect(m: FluentMenu):
            if m.window and m.window.winfo_exists():
                windows.append(m.window)
            if m.active_submenu:
                collect(m.active_submenu)
        collect(self._get_root_menu())
        return windows

    def _is_point_in_any_menu(self, px: int, py: int) -> bool:
        for win in self._get_all_menu_windows():
            try:
                wx = win.winfo_rootx()
                wy = win.winfo_rooty()
                ww = win.winfo_width()
                wh = win.winfo_height()
                if wx <= px <= wx + ww and wy <= py <= wy + wh:
                    return True
            except Exception:
                pass
        return False

    def close(self) -> None:
        self._cancel_timers()
        if self.active_submenu:
            self.active_submenu.close()
            self.active_submenu = None
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass
            self.window = None
        self.active_item_index = None
        self.active_widgets = None

        if not self.parent_menu and self._global_click_bind_id:
            try:
                self.master.unbind_all("<ButtonPress>")
            except Exception:
                pass
            self._global_click_bind_id = None

    def close_all(self) -> None:
        self._get_root_menu().close()

    def _cancel_timers(self) -> None:
        if self._outside_poll_timer:
            try:
                self.master.after_cancel(self._outside_poll_timer)
            except Exception:
                pass
            self._outside_poll_timer = None
        if self.hover_open_timer:
            try:
                self.master.after_cancel(self.hover_open_timer)
            except Exception:
                pass
            self.hover_open_timer = None
        if self.hover_close_timer:
            try:
                self.master.after_cancel(self.hover_close_timer)
            except Exception:
                pass
            self.hover_close_timer = None

    def _poll_outside_click(self) -> None:
        """Poll mouse press state to close menu when clicking anywhere outside menu bounds."""
        if not self.window or not self.window.winfo_exists():
            return

        try:
            import ctypes
            if bool(ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000 or ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000):
                class _Point(ctypes.Structure):
                    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
                pt = _Point()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                if not self._is_point_in_any_menu(pt.x, pt.y):
                    self.close_all()
                    return
        except Exception:
            pass

        self._outside_poll_timer = self.master.after(35, self._poll_outside_click)

    def _set_row_style(self, row: tk.Frame, lbl: tk.Label, ind: tk.Label | None, is_hover: bool) -> None:
        t = THEMES[self.theme]
        bg = t['hover_pill'] if is_hover else t['card_bg']
        try:
            row.config(bg=bg)
            lbl.config(bg=bg)
            if ind:
                ind.config(bg=bg)
        except Exception:
            pass

    def _on_item_enter(self, idx: int, item: dict, row: tk.Frame, lbl: tk.Label, ind: tk.Label | None) -> None:
        if self.hover_open_timer:
            try:
                self.master.after_cancel(self.hover_open_timer)
            except Exception:
                pass
            self.hover_open_timer = None
        if self.hover_close_timer:
            try:
                self.master.after_cancel(self.hover_close_timer)
            except Exception:
                pass
            self.hover_close_timer = None

        if self.active_widgets and self.active_item_index != idx:
            prev_row, prev_lbl, prev_ind = self.active_widgets
            self._set_row_style(prev_row, prev_lbl, prev_ind, False)

        self.active_item_index = idx
        self.active_widgets = (row, lbl, ind)
        self._set_row_style(row, lbl, ind, True)

        if item['type'] == 'cascade':
            sub: FluentMenu = item['menu']
            sub.theme = self.theme
            if self.active_submenu != sub:
                if self.active_submenu:
                    self.active_submenu.close()
                    self.active_submenu = None

                def open_sub():
                    if self.window and self.window.winfo_exists() and row.winfo_exists():
                        row.update_idletasks()
                        rx = row.winfo_rootx() + row.winfo_width() - 2
                        ry = row.winfo_rooty() - 4
                        sub.show(rx, ry)
                        self.active_submenu = sub

                self.hover_open_timer = self.master.after(90, open_sub)
        else:
            if self.active_submenu:
                def close_sub():
                    if self.active_submenu:
                        self.active_submenu.close()
                        self.active_submenu = None

                self.hover_close_timer = self.master.after(140, close_sub)

    def _on_item_leave(self, idx: int, item: dict, row: tk.Frame, lbl: tk.Label, ind: tk.Label | None) -> None:
        if item['type'] == 'cascade' and self.active_submenu == item['menu']:
            return
        if self.active_item_index == idx:
            self._set_row_style(row, lbl, ind, False)
            self.active_item_index = None
            self.active_widgets = None

    def _on_item_click(self, item: dict, row: tk.Frame) -> None:
        if item['type'] == 'command':
            cmd = item.get('command')
            self.close_all()
            if cmd:
                cmd()
        elif item['type'] == 'cascade':
            sub = item['menu']
            sub.theme = self.theme
            if self.active_submenu == sub:
                sub.close()
                self.active_submenu = None
            else:
                if self.active_submenu:
                    self.active_submenu.close()
                row.update_idletasks()
                rx = row.winfo_rootx() + row.winfo_width() - 2
                ry = row.winfo_rooty() - 4
                sub.show(rx, ry)
                self.active_submenu = sub

    def _on_global_click(self, event) -> None:
        menu_windows = self._get_all_menu_windows()
        w = event.widget
        while w:
            if w in menu_windows:
                return
            w = getattr(w, 'master', None)
        self.close_all()

    def show(self, x: int, y: int) -> None:
        self.close()

        self.window = tk.Toplevel(self.master)
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", True)
        self.window.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.window.config(bg=TRANSPARENT_COLOR)

        self.canvas = tk.Canvas(self.window, bg=TRANSPARENT_COLOR, highlightthickness=0)
        self.canvas.pack()

        t = THEMES[self.theme]

        # Inner container card with theme palette
        self.inner = tk.Frame(
            self.canvas,
            bg=t['card_bg'],
            padx=4,
            pady=4,
        )

        for idx, item in enumerate(self.items):
            if item['type'] == 'separator':
                sep_frame = tk.Frame(self.inner, bg=t['card_bg'], height=7)
                sep_frame.pack(fill=tk.X, padx=4)
                sep_line = tk.Frame(sep_frame, bg=t['sep'], height=1)
                sep_line.pack(fill=tk.X, pady=3)
                continue

            row = tk.Frame(self.inner, bg=t['card_bg'], cursor="hand2")
            row.pack(fill=tk.X, padx=2, pady=1)

            lbl_text = tk.Label(
                row,
                text=item['label'],
                bg=t['card_bg'],
                fg=t['text_primary'],
                font=("Microsoft YaHei UI", 9),
                anchor="w",
                padx=8,
                pady=4,
            )
            lbl_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

            if item['type'] == 'cascade':
                lbl_ind = tk.Label(
                    row,
                    text="›",
                    bg=t['card_bg'],
                    fg=t['cascade_arrow'],
                    font=("Segoe UI", 10, "bold"),
                    padx=6,
                )
                lbl_ind.pack(side=tk.RIGHT)
            elif item.get('checked', False):
                lbl_ind = tk.Label(
                    row,
                    text="✓",
                    bg=t['card_bg'],
                    fg=t['accent'],
                    font=("Segoe UI", 9, "bold"),
                    padx=6,
                )
                lbl_ind.pack(side=tk.RIGHT)
            else:
                lbl_ind = None

            def make_handlers(i_idx=idx, i_data=item, i_row=row, i_lbl=lbl_text, i_ind=lbl_ind):
                def on_enter(event):
                    self._on_item_enter(i_idx, i_data, i_row, i_lbl, i_ind)

                def on_leave(event):
                    self._on_item_leave(i_idx, i_data, i_row, i_lbl, i_ind)

                def on_click(event):
                    self._on_item_click(i_data, i_row)

                for w in [i_row, i_lbl] + ([i_ind] if i_ind else []):
                    w.bind("<Enter>", on_enter)
                    w.bind("<Leave>", on_leave)
                    w.bind("<Button-1>", on_click)

            make_handlers()

        self.inner.update_idletasks()
        req_w = self.inner.winfo_reqwidth() + 4
        req_h = self.inner.winfo_reqheight() + 4

        self.canvas.config(width=req_w, height=req_h)
        draw_rounded_card(self.canvas, req_w, req_h, radius=8, fill=t['card_bg'], outline=t['border'])
        self.canvas.create_window(2, 2, window=self.inner, anchor="nw")

        screen_w = self.master.winfo_screenwidth()
        screen_h = self.master.winfo_screenheight()

        if x + req_w > screen_w - 8:
            if self.parent_menu and self.parent_menu.window and self.parent_menu.window.winfo_exists():
                pw = self.parent_menu.window.winfo_width()
                px = self.parent_menu.window.winfo_rootx()
                x = max(8, px - req_w + 2)
            else:
                x = max(8, screen_w - req_w - 8)
        if y + req_h > screen_h - 40:
            y = max(8, screen_h - req_h - 40)

        self.window.geometry(f"+{x}+{y}")
        self.window.deiconify()

        self.window.bind("<Escape>", lambda e: self.close_all())

        if not self.parent_menu:
            if not self._global_click_bind_id:
                self._global_click_bind_id = self.master.bind_all("<ButtonPress>", self._on_global_click)
            self.master.after(120, self._poll_outside_click)


class ContextMenu:
    """Dynamic Windows 11 Fluent-styled context menu generator matching language, theme, and pet state."""

    def __init__(self, master: tk.Tk, pet: KikuriDesktopPet):
        self.master = master
        self.pet = pet
        self.root_menu: FluentMenu | None = None

    def rebuild_menu(self) -> FluentMenu:
        """Build the full context menu with Windows 11 Fluent styling, Dark/Light theme, and Kikuri palette."""
        if self.root_menu:
            self.root_menu.close()

        t = I18N[self.pet.settings.language]
        m = t['menu']
        st = t['states']
        theme = getattr(self.pet.settings, 'theme', 'dark')

        self.root_menu = FluentMenu(self.master, theme=theme)

        # 1. Animation state submenu
        state_menu = FluentMenu(self.master, theme=theme)
        for state in ROWS_CONFIG:
            state_label = st.get(state, state.capitalize())
            is_active = self.pet.current_state == state
            state_menu.add_command(
                label=state_label,
                command=lambda s=state: self.pet.set_state(s, manual=True),
                checked=is_active,
            )
        self.root_menu.add_cascade(label=m['states'], menu=state_menu)

        # 2. Scale submenu
        scale_menu = FluentMenu(self.master, theme=theme)
        scale_menu.add_command(
            label=m['scale_75'],
            command=lambda: self.pet.change_scale(0.75),
            checked=abs(self.pet.settings.scale - 0.75) < 0.05,
        )
        scale_menu.add_command(
            label=m['scale_100'],
            command=lambda: self.pet.change_scale(1.0),
            checked=abs(self.pet.settings.scale - 1.0) < 0.05,
        )
        scale_menu.add_command(
            label=m['scale_125'],
            command=lambda: self.pet.change_scale(1.25),
            checked=abs(self.pet.settings.scale - 1.25) < 0.05,
        )
        scale_menu.add_command(
            label=m['scale_150'],
            command=lambda: self.pet.change_scale(1.5),
            checked=abs(self.pet.settings.scale - 1.5) < 0.05,
        )
        self.root_menu.add_cascade(label=m['scale'], menu=scale_menu)

        # 3. Animation speed submenu
        speed_menu = FluentMenu(self.master, theme=theme)
        speed_menu.add_command(
            label=m['speed_slow'],
            command=lambda: self.pet.set_speed(0.7),
            checked=abs(self.pet.settings.speed_multiplier - 0.7) < 0.05,
        )
        speed_menu.add_command(
            label=m['speed_normal'],
            command=lambda: self.pet.set_speed(1.0),
            checked=abs(self.pet.settings.speed_multiplier - 1.0) < 0.05,
        )
        speed_menu.add_command(
            label=m['speed_fast'],
            command=lambda: self.pet.set_speed(1.4),
            checked=abs(self.pet.settings.speed_multiplier - 1.4) < 0.05,
        )
        self.root_menu.add_cascade(label=m['speed'], menu=speed_menu)

        # 4. UI Theme submenu (Dark / Light)
        theme_menu = FluentMenu(self.master, theme=theme)
        theme_menu.add_command(
            label=m['theme_dark'],
            command=lambda: self.pet.set_theme('dark'),
            checked=theme == 'dark',
        )
        theme_menu.add_command(
            label=m['theme_light'],
            command=lambda: self.pet.set_theme('light'),
            checked=theme == 'light',
        )
        self.root_menu.add_cascade(label=m['theme'], menu=theme_menu)

        # 5. Language switcher submenu
        lang_menu = FluentMenu(self.master, theme=theme)
        lang_menu.add_command(
            label="🇨🇳 中文 (Chinese)",
            command=lambda: self.pet.set_language('cn'),
            checked=self.pet.settings.language == 'cn',
        )
        lang_menu.add_command(
            label="🇬🇧 English",
            command=lambda: self.pet.set_language('en'),
            checked=self.pet.settings.language == 'en',
        )
        lang_menu.add_command(
            label="🇯🇵 日本語 (Japanese)",
            command=lambda: self.pet.set_language('jp'),
            checked=self.pet.settings.language == 'jp',
        )
        self.root_menu.add_cascade(label=m['lang'], menu=lang_menu)

        self.root_menu.add_separator()
        self.root_menu.add_command(label=m['toast'], command=self.pet.trigger_toast)
        self.root_menu.add_command(label=m['bday'], command=self.pet.trigger_birthday_greeting)
        self.root_menu.add_command(
            label=m['stats'],
            command=self.pet.toggle_hud,
            checked=self.pet.settings.show_hud,
        )
        self.root_menu.add_command(
            label=m['roam'],
            command=self.pet.toggle_wander,
            checked=self.pet.settings.is_wandering,
        )
        self.root_menu.add_command(
            label=m['autostart'],
            command=self.pet.toggle_autostart,
            checked=self.pet.settings.autostart,
        )

        self.root_menu.add_separator()
        self.root_menu.add_command(label=m['exit'], command=self.pet.quit_app)

        return self.root_menu

    def post(self, x_root: int, y_root: int) -> None:
        """Display the popup menu at cursor coordinates."""
        if self.root_menu:
            self.root_menu.show(x_root, y_root)

    def close(self) -> None:
        """Close active popup menu."""
        if self.root_menu:
            self.root_menu.close_all()
