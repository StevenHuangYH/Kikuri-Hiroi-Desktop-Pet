#!/usr/bin/env python3
"""
Sprite Renderer
---------------
Locates and loads Kikuri spritesheet, applies morphological boundary edge sharpening,
defringes background spill, and pre-renders cached PhotoImage frames for Tkinter canvas.
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageTk

try:
    import numpy as np
except ImportError:
    np = None

from src.config import (
    BASE_CELL_W,
    BASE_CELL_H,
    ROWS_CONFIG,
    get_app_dir,
    get_bundle_dir,
)


class SpriteRenderer:
    """Handles spritesheet loading, edge processing, scaling, and frame caching."""

    def __init__(self, script_dir: Path | None = None, bundle_dir: Path | None = None):
        self.script_dir = script_dir or get_app_dir()
        self.bundle_dir = bundle_dir or get_bundle_dir()
        self.atlas_image: Image.Image | None = None
        self.cached_frames: dict[str, list[ImageTk.PhotoImage]] = {}

    def find_spritesheet(self) -> Path:
        """Find the appropriate spritesheet candidate file on disk."""
        candidates = [
            self.script_dir / "pet" / "outfits" / "default" / "spritesheet.webp",
            self.bundle_dir / "pet" / "outfits" / "default" / "spritesheet.webp",
            self.script_dir / "pet" / "spritesheet.webp",
            self.bundle_dir / "pet" / "spritesheet.webp",
            self.script_dir / "run" / "final" / "spritesheet.webp",
            self.bundle_dir / "run" / "final" / "spritesheet.webp",
            self.script_dir / "pet" / "outfits" / "default" / "spritesheet.png",
            self.bundle_dir / "pet" / "outfits" / "default" / "spritesheet.png",
        ]

        for p in candidates:
            if p.is_file():
                return p

        raise FileNotFoundError("Could not find Kikuri spritesheet atlas image")

    def load_spritesheet(self) -> None:
        """Load spritesheet atlas image."""
        if self.atlas_image is not None:
            return
        sheet_path = self.find_spritesheet()
        self.atlas_image = Image.open(sheet_path).convert("RGBA")

    def render_cached_frames(self, scale: float, cell_w: int, cell_h: int) -> dict[str, list[ImageTk.PhotoImage]]:
        """
        Pre-render and scale frames with razor-sharp outer edges while keeping interior art smooth and natural.
        Returns a dictionary mapping state name to a list of PhotoImage objects.
        """
        if self.atlas_image is None:
            return {}

        self.cached_frames.clear()
        bg_rgb = (0, 0, 1, 255)

        for state, config in ROWS_CONFIG.items():
            row_idx = config['row']
            frames_count = config['frames']
            frame_list = []

            for col_idx in range(frames_count):
                left = col_idx * BASE_CELL_W
                top = row_idx * BASE_CELL_H
                crop = self.atlas_image.crop((left, top, left + BASE_CELL_W, top + BASE_CELL_H))

                if scale != 1.0:
                    crop = crop.resize((cell_w, cell_h), Image.Resampling.LANCZOS)

                # Process frame: crisp binary alpha mask with pure #000001 key
                if np is not None:
                    arr = np.array(crop)
                    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

                    # 100% Crisp binary alpha: strictly 255 or 0
                    alpha_binary = np.where(a >= 128, 255, 0).astype(np.uint8)
                    bin_alpha_img = Image.fromarray(alpha_binary, mode='L')

                    # Clean RGB (zero out any transparent pixels to prevent color key bleed)
                    r_clean = np.where(alpha_binary > 0, r, 0).astype(np.uint8)
                    g_clean = np.where(alpha_binary > 0, g, 0).astype(np.uint8)
                    b_clean = np.where(alpha_binary > 0, b, 0).astype(np.uint8)
                    clean_rgb = Image.fromarray(np.stack([r_clean, g_clean, b_clean], axis=2), 'RGB')

                    # Composite onto exact transparent color key
                    bg = Image.new("RGBA", (cell_w, cell_h), bg_rgb)
                    bg.paste(clean_rgb.convert("RGBA"), (0, 0), bin_alpha_img)
                    rgb_img_final = bg.convert("RGB")
                else:
                    alpha = crop.split()[3]
                    bin_alpha_img = alpha.point(lambda p: 255 if p >= 128 else 0)
                    base_rgb = crop.convert("RGB")
                    bg = Image.new("RGBA", (cell_w, cell_h), bg_rgb)
                    bg.paste(base_rgb.convert("RGBA"), (0, 0), bin_alpha_img)
                    rgb_img_final = bg.convert("RGB")

                frame_list.append(ImageTk.PhotoImage(rgb_img_final))

            self.cached_frames[state] = frame_list

        return self.cached_frames
