# 🎸 Kikuri Hiroi Desktop Pet (廣井きくり デスクトップペット)

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20(64--bit)-blue.svg)](https://github.com/StevenHuangYH/customize-desktop-pet)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![UI Style](https://img.shields.io/badge/Design-Windows%2011%20Fluent%20Design-purple.svg)](https://learn.microsoft.com/en-us/windows/apps/design/fluent-design-system/)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)

An interactive, lightweight, and customizable desktop pet featuring **Kikuri Hiroi (廣井きくり)**, the legendary drunken bassist of **SICK HACK** from *Bocchi the Rock!*.

Crafted with **Windows 11 Fluent Design** aesthetics, featuring dark/light mode themes, real-time hardware performance monitoring, audio-reactive bass jamming, and multi-language support.

---

## ✨ Features

### 🎨 Windows 11 Fluent Design & Dark / Light Modes
- **Character-Matched Dual Themes**:
  - 🌙 **Dark Mode (Dark Mica)**: Deep violet mica background (`#17141f`), subtle plum border (`#433256`), and soft lilac glow.
  - ☀️ **Light Mode (Light Acrylic)**: Clean porcelain white (`#fbf9fd`), soft lilac border (`#e2d9eb`), and high-contrast typography.
- **8px Smooth Rounded Corners**: Rendered via vector polygon canvas drawing on transparent borderless windows.
- **Dynamic Hot-Switching**: Switch themes seamlessly from the right-click menu with persistent settings.

### ⚡ Ultra-Compact Hardware Performance Monitor (HUD)
- **Real-Time System Tracking**: Live metrics for **CPU**, **RAM**, and **GPU** usage.
- **Minimalist Footprint**: Shrunk by **48.2%** down to `90×69px` to prevent screen clutter.
- **Snug 2px Character Attachment**: Automatically detects character sprite bounds and sits snugly 2px beside Kikuri's body (flips to the right shoulder when near the left screen edge).
- **Pixel-Perfect Monospace Alignment**: Uses geometric indicator dots (`●`) and `Consolas` tabular digits (`f"{val:3.0f}%"`), ensuring labels, digits, and `%` symbols are locked in vertical alignment.
- **Adaptive Load Indicators & Alerts**: Dynamic color shifts (Lilac/Mint/Pink → Amber Warning → Overdrive Red Alert border).

### 💬 Minimalist Floating Dialogue Bubbles
- **Distraction-Free Dialogue**: Displays pure dialogue text without redundant header tags or separators.
- **Interactive Voice Quotes**: Features Japanese, Simplified Chinese, and English quotes, drunk sake toasts, and special **August 15th Birthday Celebrations**.
- **Smart Boundary Flipping**: Automatically flips below the character when near the top of the screen.

### 🎸 Audio-Reactive Bass Groove
- **Background Music Detection**: Automatically detects system audio/music playback and switches Kikuri into her signature **slap bass groove** (`playing` animation state) with exclusive music quotes!

### 🖱️ Custom Windows 11 Context Menu
- **Native-Look Custom Menu**: Bypasses classic Win32 popup menus with custom translucent pill hover states, cascading submenus (`›`), and checkmarks (`✓`).
- **Global Click-Outside Dismissal**: Instantly closes when clicking anywhere outside the menu on screen (desktop, other apps, taskbar, or pet).

### 🐾 Autonomous Roaming & Physics Dragging
- **8 Animated States**: `Idle`, `Walk Left`, `Walk Right`, `Wave`, `Jump`, `Dizzy/Fail`, `Waiting`, and `Bass Groove`.
- **Wander AI**: Naturally strolls across your desktop with pause and random action triggers.
- **Physics Dragging**: Left-click and drag anywhere on screen with boundary clamping and location persistence.

### 🌐 Multi-Language & Customization
- **3 Supported Languages**: 🇨🇳 简体中文 (Chinese), 🇬🇧 English, 🇯🇵 日本語 (Japanese).
- **4 Size Scales**: 75% (Small), 100% (Normal), 125% (Medium), 150% (Large).
- **3 Animation Speeds**: 0.7x (Relaxed), 1.0x (Standard), 1.4x (Fast).
- **Launch on Startup**: One-click autostart toggle via Windows registry.

---

## 🚀 Getting Started

### Option 1: Standalone Portable EXE (No Python Required)
1. Download `KikuriHiroiDesktopPet_v1.0.zip` or `KikuriHiroiDesktopPet.exe` from [Releases](https://github.com/StevenHuangYH/customize-desktop-pet/releases).
2. Extract the archive and double-click **`KikuriHiroiDesktopPet.exe`** (or `启动桌宠.bat`).
3. Enjoy your desktop pet!

### Option 2: Running from Source

#### Prerequisites
- Windows 10 / Windows 11 (64-bit)
- Python 3.10 or higher

#### Installation
```bash
# 1. Clone the repository
git clone https://github.com/StevenHuangYH/customize-desktop-pet.git
cd "customize-desktop-pet"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the desktop pet
python desktop_pet.py
# Or double-click Start_Pet.bat
```

---

## 🎮 Controls & Shortcuts

| Action | Control | Description |
| :--- | :--- | :--- |
| **Move / Drag** | Left-Click & Drag | Relocate Kikuri anywhere on your desktop (auto-saves coordinates). |
| **Interact / Dialogue** | Left-Click Release | Kikuri waves and speaks a random voice quote. |
| **Context Menu** | Right-Click | Open the Windows 11 Fluent settings menu. |
| **Dismiss Menu** | Left-Click Outside / `Esc` | Instantly close the open context menu. |
| **Toggle Roaming** | Menu → 🐾 Roam Mode | Toggle autonomous wandering across screen. |
| **Toggle Performance HUD** | Menu → 📊 System Stats | Toggle the CPU / RAM / GPU monitoring card. |
| **Switch Theme** | Menu → 🎨 UI Theme | Toggle between Dark Mode and Light Mode. |

---

## 📁 Project Structure

```
Kikuri Hiroi Desktop Pet/
├── desktop_pet.py            # Main application entrypoint
├── app_icon.ico              # Yamaha TRB1004J Natural bass application icon
├── requirements.txt          # Python dependencies
├── Start_Pet.bat             # One-click Windows batch launcher
├── src/                      # Core application modules
│   ├── config.py             # Themes, I18N translations, animation frames, constants
│   ├── pet_controller.py     # Main animation loop, event handling, drag & wander AI
│   ├── ui_components.py      # HUDWindow, SpeechBubble, FluentMenu & ContextMenu
│   ├── system_monitor.py     # Background CPU/RAM/GPU & Audio playback tracker
│   ├── settings.py           # PetSettings model & JSON persistence manager
│   └── sprite_renderer.py    # Sprite sheet caching & multi-scale rendering
├── pet/                      # Runtime assets & user settings
│   ├── outfits/default/      # Character sprite sheets (PNG / WebP)
│   └── settings.json         # User preferences and window position persistence
├── build_config/             # Packaging & build configuration
│   ├── KikuriHiroiDesktopPet.spec # PyInstaller standalone build spec
│   └── version_info.txt      # Windows executable metadata
└── tools/                    # Development & release packaging scripts
    └── package_release.py    # Automated standalone release packager
```

---

## 🔨 Building Standalone Executable

To compile a standalone `.exe` using PyInstaller:

```bash
# 1. Build single-file executable with embedded resources & icon
python -m PyInstaller build_config/KikuriHiroiDesktopPet.spec --clean

# 2. Package release distribution and ZIP archive
python tools/package_release.py
```
Compiled binaries will be generated under `dist/` and `release/`.

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

Character artwork and concept based on *Bocchi the Rock!* (© Aki Hamaji / Houbunsha, Aniplex).
