#!/usr/bin/env python3
"""
Kikuri Hiroi Desktop Pet - Package Root
"""

from src.config import (
    TRANSPARENT_COLOR,
    BASE_CELL_W,
    BASE_CELL_H,
    ROWS_CONFIG,
    I18N,
    get_app_dir,
    get_bundle_dir,
    get_autostart_command,
    is_autostart_registered,
    set_autostart_registry,
)
from src.settings import PetSettings, SettingsManager
from src.system_monitor import SystemMonitor, get_gpu_usage
from src.sprite_renderer import SpriteRenderer
from src.ui_components import HUDWindow, SpeechBubble, ContextMenu
from src.pet_controller import KikuriDesktopPet, main

__all__ = [
    "TRANSPARENT_COLOR",
    "BASE_CELL_W",
    "BASE_CELL_H",
    "ROWS_CONFIG",
    "I18N",
    "get_app_dir",
    "get_bundle_dir",
    "get_autostart_command",
    "is_autostart_registered",
    "set_autostart_registry",
    "PetSettings",
    "SettingsManager",
    "SystemMonitor",
    "get_gpu_usage",
    "SpriteRenderer",
    "HUDWindow",
    "SpeechBubble",
    "ContextMenu",
    "KikuriDesktopPet",
    "main",
]
