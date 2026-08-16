#!/usr/bin/env python3
"""
UI Components
------------
Defines the floating hardware HUD window, dialogue speech bubble window,
and dynamic right-click context menu.
"""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from src.config import (
    TRANSPARENT_COLOR,
    ROWS_CONFIG,
    I18N,
)

if TYPE_CHECKING:
    from src.pet_controller import KikuriDesktopPet


class HUDWindow:
    """Floating HUD window displaying live CPU, RAM, and GPU utilization."""

    def __init__(self, master: tk.Tk):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", True)
        self.window.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.window.config(bg=TRANSPARENT_COLOR)

        self.frame = tk.Frame(
            self.window,
            bg="#181a24",
            highlightbackground="#e0436b",
            highlightthickness=1,
            padx=8,
            pady=4,
        )
        self.frame.pack()

        custom_font = ("Segoe UI", 8, "bold")
        self.lbl_cpu = tk.Label(self.frame, text="CPU: --%", bg="#181a24", fg="#4ade80", font=custom_font)
        self.lbl_cpu.pack(side=tk.LEFT, padx=3)

        self.lbl_ram = tk.Label(self.frame, text="RAM: --%", bg="#181a24", fg="#60a5fa", font=custom_font)
        self.lbl_ram.pack(side=tk.LEFT, padx=3)

        self.lbl_gpu = tk.Label(self.frame, text="GPU: --%", bg="#181a24", fg="#f472b6", font=custom_font)
        self.lbl_gpu.pack(side=tk.LEFT, padx=3)

        self.is_visible = True

    def update_metrics(self, cpu_pct: float, ram_pct: float, gpu_pct: float) -> None:
        """Update hardware metric labels and adaptive threshold colors."""
        cpu_col = "#4ade80" if cpu_pct < 60 else ("#facc15" if cpu_pct < 85 else "#f87171")
        self.lbl_cpu.config(text=f"CPU: {cpu_pct:.0f}%", fg=cpu_col)

        ram_col = "#60a5fa" if ram_pct < 70 else ("#facc15" if ram_pct < 85 else "#f87171")
        self.lbl_ram.config(text=f"RAM: {ram_pct:.0f}%", fg=ram_col)

        gpu_col = "#f472b6" if gpu_pct < 60 else ("#facc15" if gpu_pct < 85 else "#f87171")
        self.lbl_gpu.config(text=f"GPU: {gpu_pct:.0f}%", fg=gpu_col)

    def update_position(self, pos_x: float, pos_y: float, cell_w: int) -> None:
        """Anchor HUD position right above pet sprite with screen boundary safety."""
        screen_w = self.master.winfo_screenwidth()
        hud_w = 240
        hud_x = int(pos_x + (cell_w - hud_w) // 2)
        hud_x = max(8, min(screen_w - hud_w - 8, hud_x))

        hud_y = int(pos_y - 32)
        if hud_y < 5:
            # If pet is near top of screen, flip HUD below pet
            hud_y = int(pos_y + (cell_w * 208 // 192) + 6)
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
    """Floating speech bubble window with auto-hide timer and rich borders."""

    def __init__(self, master: tk.Tk):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", True)
        self.window.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.window.config(bg=TRANSPARENT_COLOR)

        self.frame = tk.Frame(
            self.window,
            bg="#ffffff",
            highlightbackground="#e0436b",
            highlightthickness=2,
            padx=12,
            pady=6,
        )
        self.frame.pack()

        self.lbl_text = tk.Label(
            self.frame,
            text="",
            bg="#ffffff",
            fg="#1a1a1a",
            font=("Microsoft YaHei", 9, "bold"),
            wraplength=230,
        )
        self.lbl_text.pack()
        self.window.withdraw()
        self.hide_timer = None

    def show_speech(self, text: str, pos_x: float, pos_y: float, cell_w: int, duration_ms: int = 3500) -> None:
        """Show message text and schedule automatic dismissal."""
        self.lbl_text.config(text=text)
        self.update_position(pos_x, pos_y, cell_w)
        self.window.deiconify()

        if self.hide_timer:
            self.master.after_cancel(self.hide_timer)
        self.hide_timer = self.master.after(duration_ms, self.hide)

    def update_position(self, pos_x: float, pos_y: float, cell_w: int) -> None:
        """Position speech bubble directly above the pet with screen boundary safety."""
        screen_w = self.master.winfo_screenwidth()
        bubble_w = 260
        b_x = int(pos_x + (cell_w - bubble_w) // 2)
        b_x = max(8, min(screen_w - bubble_w - 8, b_x))

        b_y = int(pos_y - 70)
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


class ContextMenu:
    """Dynamic context menu generator matching language and pet state."""

    def __init__(self, master: tk.Tk, pet: KikuriDesktopPet):
        self.master = master
        self.pet = pet
        self.menu: tk.Menu | None = None

    def rebuild_menu(self) -> tk.Menu:
        """Build the full context menu for the current language and state."""
        t = I18N[self.pet.settings.language]
        m = t['menu']
        st = t['states']

        self.menu = tk.Menu(self.master, tearoff=0, bg="#1a1d26", fg="#f0f2f5", activebackground="#e0436b")

        # 1. Animation state submenu
        state_menu = tk.Menu(self.menu, tearoff=0, bg="#1a1d26", fg="#f0f2f5", activebackground="#e0436b")
        for state in ROWS_CONFIG:
            state_label = st.get(state, state.capitalize())
            is_active = self.pet.current_state == state
            label_text = f"{state_label}  ✔" if is_active else state_label
            state_menu.add_command(label=label_text, command=lambda s=state: self.pet.set_state(s, manual=True))
        self.menu.add_cascade(label=m['states'], menu=state_menu)

        # 2. Scale submenu
        scale_menu = tk.Menu(self.menu, tearoff=0, bg="#1a1d26", fg="#f0f2f5", activebackground="#e0436b")
        scale_menu.add_command(
            label=m['scale_75'] + ("  ✔" if abs(self.pet.settings.scale - 0.75) < 0.05 else ""),
            command=lambda: self.pet.change_scale(0.75)
        )
        scale_menu.add_command(
            label=m['scale_100'] + ("  ✔" if abs(self.pet.settings.scale - 1.0) < 0.05 else ""),
            command=lambda: self.pet.change_scale(1.0)
        )
        scale_menu.add_command(
            label=m['scale_125'] + ("  ✔" if abs(self.pet.settings.scale - 1.25) < 0.05 else ""),
            command=lambda: self.pet.change_scale(1.25)
        )
        scale_menu.add_command(
            label=m['scale_150'] + ("  ✔" if abs(self.pet.settings.scale - 1.5) < 0.05 else ""),
            command=lambda: self.pet.change_scale(1.5)
        )
        self.menu.add_cascade(label=m['scale'], menu=scale_menu)

        # 3. Animation speed submenu
        speed_menu = tk.Menu(self.menu, tearoff=0, bg="#1a1d26", fg="#f0f2f5", activebackground="#e0436b")
        speed_menu.add_command(
            label=m['speed_slow'] + ("  ✔" if abs(self.pet.settings.speed_multiplier - 0.7) < 0.05 else ""),
            command=lambda: self.pet.set_speed(0.7)
        )
        speed_menu.add_command(
            label=m['speed_normal'] + ("  ✔" if abs(self.pet.settings.speed_multiplier - 1.0) < 0.05 else ""),
            command=lambda: self.pet.set_speed(1.0)
        )
        speed_menu.add_command(
            label=m['speed_fast'] + ("  ✔" if abs(self.pet.settings.speed_multiplier - 1.4) < 0.05 else ""),
            command=lambda: self.pet.set_speed(1.4)
        )
        self.menu.add_cascade(label=m['speed'], menu=speed_menu)

        # 4. Language switcher submenu
        lang_menu = tk.Menu(self.menu, tearoff=0, bg="#1a1d26", fg="#f0f2f5", activebackground="#e0436b")
        lang_menu.add_command(
            label="🇨🇳 中文 (Chinese)" + ("  ✔" if self.pet.settings.language == 'cn' else ""),
            command=lambda: self.pet.set_language('cn')
        )
        lang_menu.add_command(
            label="🇬🇧 English" + ("  ✔" if self.pet.settings.language == 'en' else ""),
            command=lambda: self.pet.set_language('en')
        )
        lang_menu.add_command(
            label="🇯🇵 日本語 (Japanese)" + ("  ✔" if self.pet.settings.language == 'jp' else ""),
            command=lambda: self.pet.set_language('jp')
        )
        self.menu.add_cascade(label=m['lang'], menu=lang_menu)

        self.menu.add_separator()
        self.menu.add_command(label=m['toast'], command=self.pet.trigger_toast)
        self.menu.add_command(label=m['bday'], command=self.pet.trigger_birthday_greeting)
        self.menu.add_command(
            label=m['stats'] + ("  ✔" if self.pet.settings.show_hud else ""),
            command=self.pet.toggle_hud
        )
        self.menu.add_command(
            label=m['roam'] + ("  ✔" if self.pet.settings.is_wandering else ""),
            command=self.pet.toggle_wander
        )
        self.menu.add_command(
            label=m['autostart'] + ("  ✔" if self.pet.settings.autostart else ""),
            command=self.pet.toggle_autostart
        )

        self.menu.add_separator()
        self.menu.add_command(label=m['exit'], command=self.pet.quit_app)

        return self.menu

    def post(self, x_root: int, y_root: int) -> None:
        """Display the popup menu at cursor coordinates."""
        if self.menu:
            self.menu.post(x_root, y_root)
