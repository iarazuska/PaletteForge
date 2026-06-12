import json
import os
from datetime import datetime

STORAGE_DIR = os.path.join(os.path.expanduser("~"), ".paletteforge")
STORAGE_FILE = os.path.join(STORAGE_DIR, "palettes.json")


def ensure_dir():
    os.makedirs(STORAGE_DIR, exist_ok=True)


def load_palettes():
    ensure_dir()
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_palettes(palettes):
    ensure_dir()
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(palettes, f, indent=2, ensure_ascii=False)


def add_palette(palettes, name, colors):
    palette = {
        "name": name,
        "colors": colors,
        "created_at": datetime.now().isoformat()
    }
    palettes.insert(0, palette)
    save_palettes(palettes)
    return palettes


def delete_palette(palettes, index):
    if 0 <= index < len(palettes):
        palettes.pop(index)
        save_palettes(palettes)
    return palettes


def export_palette_css(name, colors):
    lines = [f":root {{"]
    for i, color in enumerate(colors):
        lines.append(f"  --color-{i + 1}: {color};")
    lines.append("}")
    return "\n".join(lines)