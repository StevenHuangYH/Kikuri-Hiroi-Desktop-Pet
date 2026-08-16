#!/usr/bin/env python3
"""
Pet Controller
--------------
Main application controller orchestrating animations, autonomous wandering,
drag-and-drop physics, hardware monitoring, dialogs, events, and context menus.
"""

from __future__ import annotations

import datetime
import os
import time
import tkinter as tk
from pathlib import Path

from src.config import (
    BASE_CELL_W,
    BASE_CELL_H,
    TRANSPARENT_COLOR,
    ROWS_CONFIG,
    I18N,
    get_app_dir,
    get_bundle_dir,
    set_autostart_registry,
)
from src.settings import SettingsManager, PetSettings
from src.sprite_renderer import SpriteRenderer
from src.system_monitor import SystemMonitor
from src.ui_components import HUDWindow, SpeechBubble, ContextMenu


class KikuriDesktopPet:
    """Core application controller for Kikuri Hiroi Desktop Pet."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Kikuri Hiroi Desktop Pet")

        self.script_dir = get_app_dir()
        self.bundle_dir = get_bundle_dir()
        try:
            os.chdir(self.script_dir)
        except Exception:
            pass

        # Set Window icon if present
        for icon_candidate in [self.bundle_dir / "app_icon.ico", self.script_dir / "app_icon.ico"]:
            if icon_candidate.is_file():
                try:
                    self.root.iconbitmap(str(icon_candidate))
                    break
                except Exception:
                    pass

        # Window configuration
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        self.root.config(bg=TRANSPARENT_COLOR)

        # Settings Manager
        self.settings_manager = SettingsManager(self.script_dir)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.settings: PetSettings = self.settings_manager.load_settings(screen_w, screen_h)

        # Sprite Renderer
        self.renderer = SpriteRenderer(self.script_dir, self.bundle_dir)
        self.renderer.load_spritesheet()
        self.cached_frames = self.renderer.render_cached_frames(
            self.settings.scale, self.settings.cell_w, self.settings.cell_h
        )

        # Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.settings.cell_w,
            height=self.settings.cell_h,
            bg=TRANSPARENT_COLOR,
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack()

        # Animation states
        self.current_state = 'idle'
        self.current_frame = 0
        self.anim_timer = None
        self.wander_target_x = self.settings.pos_x

        # Canvas image item (Single persistent item to eliminate Tkinter transparency ghost trails)
        frames = self.cached_frames.get(self.current_state, [])
        initial_img = frames[0] if frames else None
        if initial_img:
            self.pet_img_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=initial_img, tags="pet_img")
        else:
            self.pet_img_item = None

        # Hardware metrics
        self.cpu_pct = 0.0
        self.ram_pct = 0.0
        self.gpu_pct = 0.0
        self.last_high_load_state_change = 0.0

        # Dragging state
        self.drag_start_x = 0.0
        self.drag_start_y = 0.0
        self.is_dragging = False

        # Mouse bindings
        self.canvas.bind("<ButtonPress-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_up)
        self.canvas.bind("<Button-3>", self.show_context_menu)

        # UI Components
        self.hud = HUDWindow(self.root)
        if not self.settings.show_hud:
            self.hud.hide()

        self.bubble = SpeechBubble(self.root)
        self.context_menu = ContextMenu(self.root, self)
        self.context_menu.rebuild_menu()

        self.update_window_position()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Background Hardware Monitor
        self.system_monitor = SystemMonitor(on_update=self.on_hardware_stats_updated)
        self.system_monitor.start()

        # Birthday check timer
        self.check_birthday_event()

        # Start animation & wander loops
        self.animate_step()
        self.roam_decision_step()

        # Startup entrance greeting
        self.root.after(700, self.play_launch_greeting)

    def save_settings(self) -> None:
        """Persist current settings to disk."""
        self.settings_manager.save_settings(self.settings)

    def play_launch_greeting(self) -> None:
        """Play entrance greeting."""
        self.set_state('jumping')
        t = I18N[self.settings.language]
        launch_quotes = {
            'jp': "がはは！今日も元気にロックでいこう！🍶✨",
            'cn': "嘎哈哈！今天也要加油干活、全力摇滚哦！🍶✨",
            'en': "Gahaha! Let's rock hard and have a great day! 🍶✨",
        }
        msg = launch_quotes.get(self.settings.language, t['quotes'][0])
        self.show_speech(msg, duration_ms=5000)
        self.root.after(4500, lambda: self.set_state('waving'))
        self.root.after(9000, lambda: self.set_state('idle'))

    def set_language(self, lang: str) -> None:
        """Switch current display language."""
        if lang in I18N:
            self.settings.language = lang
            self.context_menu.rebuild_menu()
            msg = {
                "en": "Language set to English! 🇬🇧✨",
                "cn": "语言已切换为简体中文！🇨🇳✨",
                "jp": "言語を日本語に切り替えました！🇯🇵✨"
            }
            self.show_speech(msg.get(lang, "Language updated!"))
            self.save_settings()

    def set_speed(self, multiplier: float) -> None:
        """Adjust animation playback speed."""
        self.settings.speed_multiplier = multiplier
        self.context_menu.rebuild_menu()
        txt = (
            f"Speed set to {multiplier}x ⏱️" if self.settings.language == 'en'
            else (f"动画播放速度已设为 {multiplier}x ⏱️" if self.settings.language == 'cn'
                  else f"アニメーション速度を {multiplier}x に変更しました ⏱️")
        )
        self.show_speech(txt, duration_ms=2500)
        self.save_settings()

    def change_scale(self, scale: float) -> None:
        """Adjust pet rendering scale and re-render frame cache."""
        self.settings.scale = scale
        cell_w = self.settings.cell_w
        cell_h = self.settings.cell_h

        self.canvas.config(width=cell_w, height=cell_h)
        self.cached_frames = self.renderer.render_cached_frames(
            self.settings.scale, cell_w, cell_h
        )

        frames = self.cached_frames.get(self.current_state, [])
        if frames and self.pet_img_item is not None:
            self.canvas.itemconfig(self.pet_img_item, image=frames[self.current_frame % len(frames)])

        self.context_menu.rebuild_menu()
        self.update_window_position()
        self.save_settings()

        scale_pct = int(scale * 100)
        feedback = {
            "en": f"Pet size set to {scale_pct}%! 🔍",
            "cn": f"宠物大小已调整为 {scale_pct}%！🔍",
            "jp": f"サイズを {scale_pct}% に変更しました！🔍"
        }
        self.show_speech(feedback.get(self.settings.language, f"Size: {scale_pct}%"), duration_ms=2000)

    def trigger_toast(self) -> None:
        """Play sake drink celebration toast."""
        self.set_state('review')
        t = I18N[self.settings.language]
        self.show_speech(t['toast_msg'], duration_ms=4500)
        self.root.after(4600, lambda: self.set_state('idle'))

    def show_speech(self, text: str, duration_ms: int = 3500) -> None:
        """Display dialogue bubble near the pet."""
        self.bubble.show_speech(
            text, self.settings.pos_x, self.settings.pos_y, self.settings.cell_w, duration_ms
        )

    def show_context_menu(self, event) -> None:
        """Display context menu at event position."""
        self.context_menu.rebuild_menu()
        self.context_menu.post(event.x_root, event.y_root)

    def update_window_position(self) -> None:
        """Update positions of main pet window and attached floating UI."""
        self.root.geometry(
            f"{self.settings.cell_w}x{self.settings.cell_h}+{int(self.settings.pos_x)}+{int(self.settings.pos_y)}"
        )
        self.hud.update_position(self.settings.pos_x, self.settings.pos_y, self.settings.cell_w)
        self.bubble.update_position(self.settings.pos_x, self.settings.pos_y, self.settings.cell_w)

    def toggle_hud(self) -> None:
        """Toggle HUD window visibility."""
        self.settings.show_hud = not self.settings.show_hud
        if self.settings.show_hud:
            self.hud.show()
        else:
            self.hud.hide()
        self.context_menu.rebuild_menu()
        self.save_settings()

    def toggle_wander(self) -> None:
        """Toggle autonomous roaming mode."""
        self.settings.is_wandering = not self.settings.is_wandering
        self.context_menu.rebuild_menu()
        t = I18N[self.settings.language]
        if self.settings.is_wandering:
            self.show_speech(t['roam_on'])
        else:
            self.show_speech(t['roam_off'])
            self.set_state('idle')
        self.save_settings()

    def toggle_autostart(self) -> None:
        """Toggle auto-start on Windows boot, update registry and persist setting."""
        self.settings.autostart = not self.settings.autostart
        set_autostart_registry(self.settings.autostart)
        self.save_settings()
        self.context_menu.rebuild_menu()
        t = I18N[self.settings.language]
        msg = t['autostart_on'] if self.settings.autostart else t['autostart_off']
        self.show_speech(msg)

    def set_state(self, state: str, manual: bool = False) -> None:
        """Change current animation state."""
        if state not in ROWS_CONFIG:
            return
        if self.current_state != state:
            self.current_state = state
            self.current_frame = 0
        if manual:
            self.settings.is_wandering = False

    def animate_step(self) -> None:
        """Render next frame and schedule subsequent step."""
        frames = self.cached_frames.get(self.current_state, [])
        if frames:
            frame_img = frames[self.current_frame % len(frames)]
            if self.pet_img_item is not None:
                self.canvas.itemconfig(self.pet_img_item, image=frame_img)
            else:
                self.pet_img_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=frame_img, tags="pet_img")

            durations = ROWS_CONFIG[self.current_state]['durations']
            dur = durations[self.current_frame % len(durations)]
            dur = int(dur / self.settings.speed_multiplier)

            self.current_frame = (self.current_frame + 1) % len(frames)
            self.anim_timer = self.root.after(dur, self.animate_step)
        else:
            self.anim_timer = self.root.after(200, self.animate_step)

    def roam_decision_step(self) -> None:
        """Autonomous roaming / wander decision engine."""
        if self.settings.is_wandering and not self.is_dragging:
            screen_w = self.root.winfo_screenwidth()
            min_x = 20
            max_x = screen_w - self.settings.cell_w - 20

            dist = self.wander_target_x - self.settings.pos_x

            # If near target, pick action or pause
            if abs(dist) < 15:
                choice = datetime.datetime.now().microsecond % 10
                if choice < 5:
                    self.set_state('idle')
                elif choice < 7:
                    self.set_state('waving')
                elif choice < 9:
                    self.set_state('jumping')
                else:
                    self.set_state('waiting')

                self.wander_target_x = min_x + (datetime.datetime.now().microsecond % int(max_x - min_x))
                next_delay = 3500 + (datetime.datetime.now().microsecond % 3500)
                self.root.after(next_delay, self.roam_decision_step)
                return
            else:
                # Move towards target smoothly (1px per step for relaxed stroll)
                if dist > 0:
                    self.set_state('running-right')
                    self.settings.pos_x += min(dist, 1)
                else:
                    self.set_state('running-left')
                    self.settings.pos_x += max(dist, -1)

                # Clamp pos_x within screen bounds
                self.settings.pos_x = max(min_x, min(max_x, self.settings.pos_x))
                self.update_window_position()
                self.root.after(75, self.roam_decision_step)
                return

        self.root.after(1000, self.roam_decision_step)

    def on_hardware_stats_updated(self, cpu_pct: float, ram_pct: float, gpu_pct: float) -> None:
        """Callback from background monitor thread."""
        self.cpu_pct = cpu_pct
        self.ram_pct = ram_pct
        self.gpu_pct = gpu_pct
        self.root.after(0, self.update_monitor_ui)

    def update_monitor_ui(self) -> None:
        """Update HUD UI and trigger high-load state changes."""
        self.hud.update_metrics(self.cpu_pct, self.ram_pct, self.gpu_pct)

        now = time.time()
        if now - self.last_high_load_state_change > 15 and not self.is_dragging:
            if self.cpu_pct > 80 or self.gpu_pct > 80:
                self.set_state('jumping')
                self.last_high_load_state_change = now
            elif self.ram_pct > 92 or self.cpu_pct > 95:
                self.set_state('failed')
                self.last_high_load_state_change = now

    def check_birthday_event(self) -> None:
        """Check if today is 8/15 Birthday Celebration."""
        now = datetime.datetime.now()
        if now.month == 8 and now.day == 15:
            self.trigger_birthday_greeting()
        self.root.after(15 * 60 * 1000, self.check_birthday_event)

    def trigger_birthday_greeting(self) -> None:
        """Play special 8/15 birthday greeting."""
        self.set_state('jumping')
        msg = I18N[self.settings.language]['bday_msg']
        self.show_speech(msg, duration_ms=6500)
        self.root.after(4500, lambda: self.set_state('waving'))

    def on_left_down(self, event) -> None:
        """Start dragging."""
        self.is_dragging = True
        self.drag_start_x = event.x_root - self.settings.pos_x
        self.drag_start_y = event.y_root - self.settings.pos_y

    def on_left_drag(self, event) -> None:
        """Update position while dragging with strict screen boundary clamping."""
        if self.is_dragging:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            new_x = event.x_root - self.drag_start_x
            new_y = event.y_root - self.drag_start_y
            self.settings.pos_x = max(10, min(screen_w - self.settings.cell_w - 10, new_x))
            self.settings.pos_y = max(40, min(screen_h - self.settings.cell_h - 40, new_y))
            self.update_window_position()

    def on_left_up(self, event) -> None:
        """Finish dragging and trigger quote dialogue."""
        if self.is_dragging:
            self.is_dragging = False
            self.save_settings()
            self.set_state('waving')
            now = datetime.datetime.now()
            if now.month == 8 and now.day == 15:
                self.trigger_birthday_greeting()
            else:
                t = I18N[self.settings.language]
                quotes = t['quotes']
                quote_idx = int(time.time()) % len(quotes)
                self.show_speech(quotes[quote_idx])

    def quit_app(self) -> None:
        """Clean shutdown and resource release."""
        self.save_settings()
        if hasattr(self, 'system_monitor'):
            self.system_monitor.stop()
        if hasattr(self, 'hud'):
            self.hud.destroy()
        if hasattr(self, 'bubble'):
            self.bubble.destroy()
        try:
            self.root.destroy()
        except Exception:
            pass


def main() -> None:
    """Application entry point."""
    root = tk.Tk()
    app = KikuriDesktopPet(root)
    root.mainloop()


if __name__ == "__main__":
    main()
