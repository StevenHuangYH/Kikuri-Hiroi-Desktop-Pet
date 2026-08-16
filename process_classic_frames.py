#!/usr/bin/env python3
"""
Classic Green Dress Spritesheet Generator for Kikuri Hiroi Desktop Pet
----------------------------------------------------------------------
Extracts genuine artist keyframes from run/decoded, normalizes dimensions,
and compiles the full 12x9 atlas (2304x1872) with crisp binary alpha
(zero ghosting, zero edge halos, and strict boundary safety).
"""

import os
import math
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import numpy as np

CELL_W = 192
CELL_H = 208
ATLAS_COLS = 12
ATLAS_ROWS = 7
ATLAS_W = ATLAS_COLS * CELL_W   # 2304
ATLAS_H = ATLAS_ROWS * CELL_H   # 1456
BASELINE_Y = 198
TARGET_H = 180

ROWS_CONFIG = {
    'idle':          {'row': 0, 'frames': 12},
    'running-right': {'row': 1, 'frames': 12},
    'running-left':  {'row': 2, 'frames': 12},
    'waving':        {'row': 3, 'frames': 12},
    'jumping':       {'row': 4, 'frames': 12},
    'failed':        {'row': 5, 'frames': 12},
    'waiting':       {'row': 6, 'frames': 12},
}


def remove_chroma_key_crisp(img: Image.Image, key_rgb=(0, 255, 255), tolerance=100) -> Image.Image:
    """Crisp binary chroma-key removal that cleanly isolates Cyan background while 100% preserving skin, face, and eyes."""
    rgba = np.array(img.convert('RGBA')).astype(np.float32)
    r, g, b, a = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]
    kr, kg, kb = key_rgb

    dist = np.sqrt((r - kr)**2 + (g - kg)**2 + (b - kb)**2)
    # Background is specifically Cyan (low red, high green, high blue):
    cyan_bg = (r < 95) & (g > 150) & (b > 150) & ((g - r) > 45) & ((b - r) > 45)
    is_bg = ((dist < tolerance) & (r < 100)) | cyan_bg | (a < 40)

    # Defringe edge pixels with cyan contamination (only on dark/non-skin borders)
    edge_spill = (r < 100) & (g > 120) & (b > 120) & ((g - r) > 30) & ((b - r) > 30) & (~is_bg)
    r[edge_spill] = np.minimum(r[edge_spill], 30.0)
    g[edge_spill] = np.minimum(g[edge_spill], 30.0)
    b[edge_spill] = np.minimum(b[edge_spill], 30.0)

    # Hard binary alpha: strictly 255 on character, 0 on background
    a[is_bg] = 0.0
    a[~is_bg] = 255.0

    r[is_bg] = 0.0
    g[is_bg] = 0.0
    b[is_bg] = 0.0

    out_arr = np.stack([r, g, b, a], axis=2).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out_arr, mode='RGBA')


def fit_to_cell(sprite: Image.Image, target_h=TARGET_H, baseline_y=BASELINE_Y, cell_w=CELL_W, cell_h=CELL_H) -> Image.Image:
    """Scale sprite to standard height and center with strict safe margins inside 192x208."""
    bbox = sprite.getbbox()
    if not bbox:
        return Image.new('RGBA', (cell_w, cell_h), (0, 0, 0, 0))

    cropped = sprite.crop(bbox)
    cw, ch = cropped.size

    scale = target_h / float(ch)
    new_w = max(1, int(round(cw * scale)))
    new_h = max(1, int(round(ch * scale)))

    # Strict padding: max width 176px (leaves at least 8px margin on left & right)
    max_w = cell_w - 16
    if new_w > max_w:
        scale = max_w / float(cw)
        new_w = max_w
        new_h = max(1, int(round(ch * scale)))

    # Max height: 184px (leaves at least 12px margin top & bottom)
    max_h = cell_h - 24
    if new_h > max_h:
        scale = max_h / float(ch)
        new_h = max_h
        new_w = max(1, int(round(cw * scale)))

    resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Re-binarize alpha after resize to eliminate semi-transparent edge pixels
    r_arr = np.array(resized)
    r_arr[:, :, 3] = np.where(r_arr[:, :, 3] >= 128, 255, 0).astype(np.uint8)
    r_arr[r_arr[:, :, 3] == 0] = 0
    resized = Image.fromarray(r_arr, mode='RGBA')

    canvas = Image.new('RGBA', (cell_w, cell_h), (0, 0, 0, 0))
    pos_x = (cell_w - new_w) // 2
    pos_y = baseline_y - new_h
    pos_y = max(4, min(cell_h - new_h - 4, pos_y))
    pos_x = max(4, min(cell_w - new_w - 4, pos_x))

    canvas.paste(resized, (pos_x, pos_y), resized)
    return canvas


def extract_components(img_path: Path, min_w=30, min_h=150) -> list[tuple[int, int, int, int]]:
    """Find discrete sprite bounding boxes in image, sorted strictly left-to-right."""
    img = Image.open(img_path).convert('RGBA')
    arr = np.array(img)
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    dist = np.sqrt((r - 0.0)**2 + (g - 255.0)**2 + (b - 255.0)**2)
    cyan_var = ((g > 140) & (b > 140) & (r < 110)) | ((g > 195) & (b > 195))
    is_bg = (dist < 120) | cyan_var
    mask = (a > 50) & (~is_bg)
    H, W = mask.shape
    visited = np.zeros((H, W), dtype=bool)
    boxes = []

    for y in range(0, H, 2):
        for x in range(0, W, 2):
            if mask[y, x] and not visited[y, x]:
                q = [(y, x)]
                visited[y, x] = True
                min_x, max_x, min_y, max_y = x, x, y, y
                cnt = 0
                while q:
                    cy, cx = q.pop()
                    cnt += 1
                    if cx < min_x: min_x = cx
                    if cx > max_x: max_x = cx
                    if cy < min_y: min_y = cy
                    if cy > max_y: max_y = cy
                    for dy, dx in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and not visited[ny, nx] and mask[ny, nx]:
                            visited[ny, nx] = True
                            q.append((ny, nx))
                if cnt > 100 and (max_y - min_y) >= min_h and (max_x - min_x) >= min_w:
                    boxes.append((min_x, min_y, max_x, max_y))

    # Sort strictly left to right to preserve animation order
    boxes.sort(key=lambda b: b[0])
    return boxes


def extract_keyframe_cells(img_path: Path, target_h=TARGET_H) -> list[Image.Image]:
    """Extract, defringe, and cell-fit all keyframes from an image file using uniform row-consistent scaling."""
    src = Image.open(img_path)
    keyed = remove_chroma_key_crisp(src)
    boxes = extract_components(img_path)
    if not boxes:
        return []

    max_h = max(b[3] - b[1] for b in boxes)
    max_w = max(b[2] - b[0] for b in boxes)
    baseline_source_y = max(b[3] for b in boxes)
    scale = min(target_h / float(max_h), (CELL_W - 16) / float(max_w))

    frames = []
    for b in boxes:
        crop = keyed.crop(b)
        cw, ch = crop.size
        new_w = max(1, int(round(cw * scale)))
        new_h = max(1, int(round(ch * scale)))

        resized = crop.resize((new_w, new_h), Image.Resampling.LANCZOS)
        r_arr = np.array(resized)
        r_arr[:, :, 3] = np.where(r_arr[:, :, 3] >= 128, 255, 0).astype(np.uint8)
        r_arr[r_arr[:, :, 3] == 0] = 0
        resized = Image.fromarray(r_arr, mode='RGBA')

        feet_diff = baseline_source_y - b[3]
        pos_y = BASELINE_Y - new_h - int(round(feet_diff * scale))
        pos_x = (CELL_W - new_w) // 2
        pos_x = max(4, min(CELL_W - new_w - 4, pos_x))
        pos_y = max(4, min(CELL_H - new_h - 4, pos_y))

        canvas = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
        canvas.paste(resized, (pos_x, pos_y), resized)
        frames.append(canvas)

    return frames


def generate_all_classic_frames(project_dir: Path):
    run_dir = project_dir / 'run'
    decoded_dir = run_dir / 'decoded'
    frames_dir = run_dir / 'frames'
    frames_dir.mkdir(parents=True, exist_ok=True)

    base_cell = fit_to_cell(remove_chroma_key_crisp(Image.open(decoded_dir / 'base.png')), target_h=TARGET_H)

    all_state_frames = {}

    # State mappings from keyframe list to 12 frames (100% DISCRETE, ZERO ghosting / zero blending)
    state_files = {
        'idle':          ('idle.png',          [0, 0, 1, 2, 3, 3, 4, 5, 5, 4, 3, 1]),
        'running-right': ('running-right.png', [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]),
        'running-left':  ('running-left.png',  [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]),
        'waving':        ('waving.png',        [0, 1, 2, 3, 2, 3, 2, 3, 2, 1, 0, 0]),
        'jumping':       ('jumping.png',       [4, 4, 1, 0, 0, 0, 2, 3, 4, 4, 1, 1]),
        'failed':        ('failed.png',        [0, 1, 2, 3, 4, 5, 6, 7, 6, 4, 2, 0]),
        'waiting':       ('waiting.png',       [0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0, 0]),
    }

    for state, (filename, map_12) in state_files.items():
        filepath = decoded_dir / filename
        if filepath.is_file():
            keyframes = extract_keyframe_cells(filepath, target_h=TARGET_H)
        else:
            keyframes = []

        if not keyframes:
            keyframes = [base_cell]

        nk = len(keyframes)
        twelve_frames = []
        for idx in map_12:
            safe_idx = idx % nk
            twelve_frames.append(keyframes[safe_idx].copy())

        all_state_frames[state] = twelve_frames

    # Build Atlas
    atlas = Image.new('RGBA', (ATLAS_W, ATLAS_H), (0, 0, 0, 0))
    frames_manifest = {'ok': True, 'rows': {}}

    for state, config in ROWS_CONFIG.items():
        row_idx = config['row']
        state_dir = frames_dir / state
        state_dir.mkdir(parents=True, exist_ok=True)
        
        frames = all_state_frames.get(state, [])
        frame_paths = []
        
        for col_idx, frame in enumerate(frames):
            frame_filename = f'{col_idx:02d}.png'
            frame_path = state_dir / frame_filename
            frame.save(frame_path, 'PNG')
            frame_paths.append(str(frame_path))
            
            paste_x = col_idx * CELL_W
            paste_y = row_idx * CELL_H
            atlas.paste(frame, (paste_x, paste_y), frame)
            
        frames_manifest['rows'][state] = {
            'row': row_idx,
            'frames_count': len(frames),
            'frame_files': frame_paths
        }

    with open(frames_dir / 'frames-manifest.json', 'w', encoding='utf-8') as f:
        json.dump(frames_manifest, f, indent=2)

    final_dir = run_dir / 'final'
    final_dir.mkdir(parents=True, exist_ok=True)
    atlas.save(final_dir / 'spritesheet.png', 'PNG')
    atlas.save(final_dir / 'spritesheet.webp', 'WEBP', lossless=True, quality=100)

    outfits_dir = project_dir / 'pet' / 'outfits'
    default_outfit_dir = outfits_dir / 'default'
    default_outfit_dir.mkdir(parents=True, exist_ok=True)

    atlas.save(default_outfit_dir / 'spritesheet.png', 'PNG')
    atlas.save(default_outfit_dir / 'spritesheet.webp', 'WEBP', lossless=True, quality=100)

    atlas.save(project_dir / 'pet' / 'spritesheet.webp', 'WEBP', lossless=True, quality=100)

    print(f'[Classic] Atlas compiled successfully with {ATLAS_COLS}x{ATLAS_ROWS} = {ATLAS_COLS * ATLAS_ROWS} frames!')
    print(f'Saved to {default_outfit_dir / "spritesheet.webp"}')


if __name__ == '__main__':
    project_root = Path(__file__).parent.resolve()
    generate_all_classic_frames(project_root)
