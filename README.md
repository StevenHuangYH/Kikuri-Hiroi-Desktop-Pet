# Customize Desktop Pet (Kikuri Hiroi Desktop Pet)

An interactive, customizable desktop pet application built with Python and PySide6 / PyQt, featuring real-time system performance HUD, multiple language support, high-framerate animations, outfits, and autonomous roaming.

---

## ✨ Features

1. **Hardware HUD Monitoring**:
   - Real-time CPU, RAM, and NVIDIA GPU usage / VRAM monitoring.
   - High-load interaction reactions.
2. **Multi-Language Support**:
   - English, Simplified Chinese (简体中文), Japanese (日本語) real-time switching.
3. **Smooth Sprite Animations & Roaming**:
   - Multi-frame high-FPS sprite sheet animations (idle, walk, waving, jumping, review, failed, etc.).
   - Autonomous roaming, drag-and-drop, position persistence, and startup configuration.
4. **Customization & Outfits**:
   - Modular sprite sheet & configuration loading (`pet.json`, `settings.json`, custom outfits).
   - Adjustable pet scale and animation playback speed.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Dependencies:
  ```bash
  pip install -r requirements.txt # or install PySide6, psutil, etc.
  ```

### Run

```bash
python desktop_pet.py
```

---

## 📦 Project Structure

- `desktop_pet.py`: Main entry point for the desktop pet application.
- `src/`: Core logic modules (controller, sprite renderer, system monitor, settings, UI components).
- `pet/`: Outfits, sprite sheets, and JSON configurations.
- `run/`: Sprite processing workflows, prompt templates, and frame datasets.
- `package_release.py`: Build and packaging automation script.
