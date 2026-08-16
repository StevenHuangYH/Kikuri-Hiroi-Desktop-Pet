# 🎸 Kikuri Hiroi Desktop Pet

A lightweight, interactive Windows desktop pet featuring **Kikuri Hiroi (廣井きくり)** from *Bocchi the Rock!*. Built with Python and Windows 11 Fluent Design aesthetics.

---

## ✨ Features

- **🎨 Windows 11 Fluent Design**: Smooth 8px rounded corners with **Dark Mode** (Dark Mica) and **Light Mode** (Light Acrylic) support.
- **⚡ Compact Performance Monitor**: Real-time **CPU / RAM / GPU** tracker with pixel-perfect tabular numbers, adaptive load colors, and a snug 2px body-proximity fit.
- **💬 Minimalist Dialogue**: Floating voice quote bubbles (Chinese, English, Japanese) with audio and birthday easter eggs.
- **🎸 Audio-Reactive Bass Groove**: Automatically jams on bass when system audio or music is detected.
- **🖱️ Fluent Right-Click Menu**: Translucent hover pills, submenus, and global click-outside auto-dismissal.
- **🐾 Roaming & Physics**: 8 animated states, autonomous desktop wandering, and left-click drag-and-drop.
- **🌐 Customization**: 4 scale sizes (75%, 100%, 125%, 150%), 3 animation speeds, and Windows autostart toggle.

---

## 🚀 Quick Start

### Option 1: Standalone Portable EXE (No Python Needed)
1. Download `KikuriHiroiDesktopPet.exe` from [Releases](../../releases).
2. Double-click to run — zero installation required.

### Option 2: Run from Source
```bash
# Clone repository
git clone https://github.com/TotoroCN/kikuri-hiroi-desktop-pet.git
cd kikuri-hiroi-desktop-pet

# Install dependencies
pip install -r requirements.txt

# Run
python desktop_pet.py
```

---

## 🎮 Controls

| Action | Input | Description |
| :--- | :--- | :--- |
| **Move / Drag** | Left-Click & Drag | Relocate pet anywhere on screen |
| **Interact** | Left-Click | Trigger wave animation & dialogue quote |
| **Settings Menu** | Right-Click | Open Windows 11 Fluent context menu |
| **Dismiss Menu** | Click Outside / `Esc` | Instantly close open context menu |
| **Roam Mode** | Menu → 🐾 自由漫游 | Toggle autonomous wandering |
| **System HUD** | Menu → 📊 系统监控 | Toggle CPU/RAM/GPU performance card |
| **UI Theme** | Menu → 🎨 UI 主题风格 | Toggle Dark Mode / Light Mode |

---

## 🔨 Build Standalone EXE

```bash
# Compile standalone executable with icon and bundled assets
python -m PyInstaller build_config/KikuriHiroiDesktopPet.spec --clean

# Package release
python tools/package_release.py
```

---

## 📜 License

[MIT License](LICENSE) © 2026. Character artwork based on *Bocchi the Rock!* (© Aki Hamaji / Houbunsha, Aniplex).
