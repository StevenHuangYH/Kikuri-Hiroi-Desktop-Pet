# Kikuri Hiroi Desktop Pet

A lightweight, interactive Windows desktop pet featuring **Kikuri Hiroi (廣井きくり)** from *Bocchi the Rock!*. Built with Python and Windows 11 Fluent Design aesthetics.

---

## Features

- **Windows 11 Fluent Design**: Smooth 8px rounded corners with **Dark Mode** (Dark Mica) and **Light Mode** (Light Acrylic) support.
- **Compact Performance Monitor**: Real-time **CPU / RAM / GPU** tracker with pixel-perfect tabular numbers, adaptive load colors, and a snug 2px body-proximity fit.
- **Minimalist Dialogue**: Floating voice quote bubbles (Chinese, English, Japanese) with audio and birthday interactions.
- **Audio-Reactive Bass Groove**: Automatically jams on bass when system audio or music playback is detected.
- **Fluent Context Menu**: Translucent hover pills, cascading submenus, and global click-outside auto-dismissal.
- **Roaming & Physics**: 8 animated states, autonomous desktop wandering, and left-click drag-and-drop.
- **Customization**: 4 scale sizes (75%, 100%, 125%, 150%), 3 animation speeds, and Windows autostart toggle.

---

## Project Structure

```
kikuri-hiroi-desktop-pet/
├── desktop_pet.py            # Main application entry point
├── app_icon.ico              # Yamaha TRB1004J Natural bass application icon
├── requirements.txt          # Python dependencies
├── Start_Pet.bat             # One-click Windows batch launcher
├── README.md                 # Project documentation
├── LICENSE                   # MIT License
├── .gitignore                # Git ignore rules
├── src/                      # Core application modules
│   ├── __init__.py
│   ├── config.py             # Themes, translations, animation frames, constants
│   ├── pet_controller.py     # Main animation loop, event handling, drag & wander AI
│   ├── settings.py           # PetSettings model & JSON persistence manager
│   ├── sprite_renderer.py    # Sprite sheet caching & multi-scale rendering
│   ├── system_monitor.py     # Hardware metrics (CPU/RAM/GPU) & audio playback detector
│   └── ui_components.py      # HUDWindow, SpeechBubble, FluentMenu & ContextMenu
├── build_config/             # Packaging & build configuration
│   ├── KikuriHiroiDesktopPet.spec # PyInstaller standalone build spec
│   └── version_info.txt      # Windows executable metadata
└── tools/                    # Development & release packaging scripts
    ├── package_release.py    # Automated standalone release packager
    └── process_classic_frames.py # Sprite atlas compositing tool
```

---

## Quick Start

### Option 1: Standalone Portable EXE (No Python Required)
1. Download `KikuriHiroiDesktopPet.exe` from Releases.
2. Double-click to run.

### Option 2: Run from Source
```bash
# Clone repository
git clone https://github.com/StevenHuangYH/kikuri-hiroi-desktop-pet.git
cd kikuri-hiroi-desktop-pet

# Install dependencies
pip install -r requirements.txt

# Run
python desktop_pet.py
```

---

## Controls

| Action | Input | Description |
| :--- | :--- | :--- |
| Move / Drag | Left-Click & Drag | Relocate pet anywhere on screen |
| Interact | Left-Click | Trigger wave animation and voice quote |
| Settings Menu | Right-Click | Open Windows 11 Fluent context menu |
| Dismiss Menu | Click Outside / Esc | Instantly close open context menu |
| Roam Mode | Menu -> Roam Mode | Toggle autonomous wandering |
| System HUD | Menu -> System Stats | Toggle CPU / RAM / GPU monitoring card |
| UI Theme | Menu -> UI Theme | Toggle Dark Mode / Light Mode |

---

## Build Standalone EXE

```bash
# Compile standalone executable with icon and bundled assets
python -m PyInstaller build_config/KikuriHiroiDesktopPet.spec --clean

# Package release
python tools/package_release.py
```

---

## License

MIT License (c) 2026. Character artwork and concept based on *Bocchi the Rock!* (c) Aki Hamaji / Houbunsha, Aniplex.
