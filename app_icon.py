"""
=============================================================================
📈 ALL-IN-ONE LIFE OS : Unified Growth Graph App Icon Helper & Generator
=============================================================================
Provides one single source of truth for the Growth Graph icon used across:
  1. PyInstaller standalone Windows EXE / Desktop Shortcut (assets/app_icon.ico)
  2. Windows System Tray Icon (tray_manager.py)
  3. Tkinter Floating Widget & All Popup Dialog Titlebars (floating_widget.py)
=============================================================================
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw


def _resource_base_dir() -> Path:
    """Locate bundled PyInstaller _MEIPASS directory or local repository root."""
    if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def get_app_icon_paths() -> tuple[Path, Path]:
    """Return (ico_path, png_path) for the canonical app icon assets."""
    assets_dir = _resource_base_dir() / "assets"
    return assets_dir / "app_icon.ico", assets_dir / "app_icon.png"


def render_growth_icon_image(size: int = 256) -> Image.Image:
    """Render a calm, Modern Minimalist Growth Graph tile icon (Lucide trending-up style)."""
    from ui_theme import render_lucide_icon

    base = 512
    img = Image.new("RGBA", (base, base), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # Matte zinc-obsidian squircle with subtle crisp hairline border (opaque interior)
    pad = 28
    draw.rounded_rectangle(
        (pad, pad, base - pad, base - pad),
        radius=116,
        fill=(17, 18, 22, 255),         # #111216
        outline=(46, 51, 61, 255),      # Crisp subtle titanium rim
        width=18,
    )
    # Subtle quiet baseline axis inside tile
    draw.line((118, 372, 394, 372), fill=(39, 39, 42, 255), width=8)

    # Render genuine Lucide 'trending-up' stroke vector cleanly centered in emerald
    trend_fg = render_lucide_icon("trending-up", size=340, color="#10B981", stroke_width=2.3)
    offset = (base - 340) // 2
    img.alpha_composite(trend_fg, (offset, offset - 6))

    if size != base:
        return img.resize((size, size), Image.Resampling.LANCZOS)
    return img


def generate_icon_assets(target_assets_dir: Path = None) -> tuple[Path, Path]:
    """Generate assets/app_icon.png and multi-resolution assets/app_icon.ico."""
    assets_dir = Path(target_assets_dir) if target_assets_dir else Path(__file__).resolve().parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    ico_path = assets_dir / "app_icon.ico"
    png_path = assets_dir / "app_icon.png"

    hi = render_growth_icon_image(512)
    png_img = hi.resize((256, 256), Image.Resampling.LANCZOS)
    png_img.save(png_path, format="PNG")

    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    hi.save(ico_path, format="ICO", sizes=ico_sizes)
    return ico_path, png_path


def load_app_icon_image(size: int = 64) -> Image.Image:
    """Load canonical growth graph icon (or synthesize identically on fallback)."""
    _, png_path = get_app_icon_paths()
    if png_path.is_file():
        try:
            with Image.open(png_path) as im:
                rgba = im.convert("RGBA")
                if rgba.size != (size, size):
                    rgba = rgba.resize((size, size), Image.Resampling.LANCZOS)
                return rgba.copy()
        except Exception:
            pass
    return render_growth_icon_image(size)


def apply_tk_app_icon(win, cache_owner=None):
    """Apply unified growth icon cleanly to a Tk root or Toplevel window."""
    ico_path, png_path = get_app_icon_paths()
    if sys.platform.startswith("win") and ico_path.is_file():
        try:
            win.iconbitmap(default=str(ico_path))
        except Exception:
            try:
                win.iconbitmap(str(ico_path))
            except Exception:
                pass
    if png_path.is_file():
        try:
            import tkinter as tk
            photo = tk.PhotoImage(master=win, file=str(png_path))
            if cache_owner is not None:
                cache_owner._app_icon_photo = photo
            else:
                win._app_icon_photo = photo
            win.iconphoto(True, photo)
        except Exception:
            pass


if __name__ == "__main__":
    ico, png = generate_icon_assets()
    print(f"Generated {ico} ({ico.stat().st_size}B) and {png} ({png.stat().st_size}B)")
