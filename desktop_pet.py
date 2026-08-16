#!/usr/bin/env python3
"""
Kikuri Hiroi Desktop Pet
------------------------
Standalone animated desktop pet with real-time CPU, RAM, and GPU monitoring,
relaxed smooth animations, autonomous wandering, drag-and-drop,
multi-language switching (EN / CN / JP), and 8/15 Birthday Celebration.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.pet_controller import KikuriDesktopPet, main

if __name__ == "__main__":
    main()
