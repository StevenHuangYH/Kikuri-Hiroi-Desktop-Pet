#!/usr/bin/env python3
"""
Settings Manager
----------------
Handles loading, validation, and JSON persistence for pet configurations,
window coordinates, and Windows autostart registry state.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.config import (
    BASE_CELL_W,
    BASE_CELL_H,
    I18N,
    get_app_dir,
    is_autostart_registered,
    set_autostart_registry,
)


@dataclass
class PetSettings:
    language: str = 'cn'           # Default language: Chinese (Simplified)
    scale: float = 0.75            # Default scale: 75% (Compact)
    speed_multiplier: float = 1.0
    show_hud: bool = True
    is_wandering: bool = True
    is_bass_playing: bool = False  # Continuous Bass Playing Mode
    autostart: bool = False
    theme: str = 'dark'            # UI Theme: 'dark' or 'light'
    pos_x: float = 0.0
    pos_y: float = 0.0

    @property
    def cell_w(self) -> int:
        return int(BASE_CELL_W * self.scale)

    @property
    def cell_h(self) -> int:
        return int(BASE_CELL_H * self.scale)


class SettingsManager:
    """Manages reading and writing user preferences to pet/settings.json."""

    def __init__(self, script_dir: Path | None = None):
        self.script_dir = script_dir or get_app_dir()
        self.settings_path = self.script_dir / "pet" / "settings.json"
        if not self.settings_path.is_file() and (self.script_dir / "settings.json").is_file():
            self.settings_path = self.script_dir / "settings.json"

    def load_settings(self, screen_w: int, screen_h: int) -> PetSettings:
        """Load settings from JSON file or apply default values."""
        settings = PetSettings()

        # Compute default bottom-right screen coordinates
        settings.pos_x = float(screen_w - settings.cell_w - 60)
        settings.pos_y = float(screen_h - settings.cell_h - 100)

        if self.settings_path.is_file():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get('language') in I18N:
                        settings.language = data['language']
                    if 'scale' in data:
                        settings.scale = float(data['scale'])
                    if 'speed_multiplier' in data:
                        settings.speed_multiplier = float(data['speed_multiplier'])
                    if 'show_hud' in data:
                        settings.show_hud = bool(data['show_hud'])
                    if 'is_wandering' in data:
                        settings.is_wandering = bool(data['is_wandering'])
                    if 'is_bass_playing' in data:
                        settings.is_bass_playing = bool(data['is_bass_playing'])
                    if 'autostart' in data:
                        settings.autostart = bool(data['autostart'])
                    else:
                        settings.autostart = is_autostart_registered()
                    if 'theme' in data and data['theme'] in ('dark', 'light'):
                        settings.theme = data['theme']
                    if 'pos_x' in data and 'pos_y' in data:
                        sx, sy = float(data['pos_x']), float(data['pos_y'])
                        if 0 <= sx <= screen_w - 40 and 0 <= sy <= screen_h - 40:
                            settings.pos_x = sx
                            settings.pos_y = sy
            except Exception as e:
                print(f"Warning: Failed to load settings from {self.settings_path}: {e}")

        # Synchronize Windows registry state with loaded autostart setting
        if settings.autostart != is_autostart_registered():
            set_autostart_registry(settings.autostart)

        return settings

    def save_settings(self, settings: PetSettings) -> None:
        """Persist current settings to pet/settings.json."""
        target_path = self.script_dir / "pet" / "settings.json"
        data = {
            'language': settings.language,
            'scale': settings.scale,
            'speed_multiplier': settings.speed_multiplier,
            'show_hud': settings.show_hud,
            'is_wandering': settings.is_wandering,
            'is_bass_playing': settings.is_bass_playing,
            'autostart': settings.autostart,
            'theme': settings.theme,
            'pos_x': int(settings.pos_x),
            'pos_y': int(settings.pos_y),
        }
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save settings to {target_path}: {e}")
