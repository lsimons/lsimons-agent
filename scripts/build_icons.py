"""Generate platform-specific icons from docs/Leo-Bot.png"""

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "docs" / "Leo-Bot.png"
BUILD_DIR = ROOT / "packages" / "lsimons-agent-electron" / "build"


def main():
    if not SOURCE.exists():
        print(f"Error: {SOURCE} not found")
        sys.exit(1)

    BUILD_DIR.mkdir(exist_ok=True)

    # Check if Pillow is available
    pillow_available = importlib.util.find_spec("PIL") is not None

    if pillow_available:
        generate_with_pillow()
    else:
        print("Pillow not installed, trying platform tools...")
        if sys.platform == "darwin":
            generate_mac_icons_native()
        else:
            print("Install Pillow: uv add pillow --dev")
            sys.exit(1)


def generate_with_pillow():
    from PIL import Image

    img = Image.open(SOURCE)

    # Ensure RGBA mode for transparency support
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # Windows .ico (multiple sizes embedded)
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = [img.resize(size, Image.LANCZOS) for size in ico_sizes]
    ico_images[0].save(
        BUILD_DIR / "icon.ico", format="ICO", sizes=ico_sizes, append_images=ico_images[1:]
    )
    print(f"Created {BUILD_DIR / 'icon.ico'}")

    # Linux .png (256x256)
    img.resize((256, 256), Image.LANCZOS).save(BUILD_DIR / "icon.png")
    print(f"Created {BUILD_DIR / 'icon.png'}")

    # macOS .icns (requires iconset folder)
    if sys.platform == "darwin":
        generate_icns_with_pillow(img)
    else:
        print("Skipping .icns generation (not on macOS)")


def generate_icns_with_pillow(img):
    from PIL import Image

    iconset = BUILD_DIR / "icon.iconset"
    iconset.mkdir(exist_ok=True)

    # macOS iconset requires specific sizes and naming
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in sizes:
        # Standard resolution
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(iconset / f"icon_{size}x{size}.png")
        # Retina (@2x) - half the stated size at double density
        if size >= 32 and size <= 512:
            resized.save(iconset / f"icon_{size//2}x{size//2}@2x.png")

    # Use iconutil to create .icns
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(BUILD_DIR / "icon.icns")],
        check=True,
    )
    print(f"Created {BUILD_DIR / 'icon.icns'}")

    # Clean up iconset folder
    shutil.rmtree(iconset)


def generate_mac_icons_native():
    """macOS-only: use sips and iconutil"""
    iconset = BUILD_DIR / "icon.iconset"
    iconset.mkdir(exist_ok=True)

    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in sizes:
        subprocess.run(
            [
                "sips",
                "-z",
                str(size),
                str(size),
                str(SOURCE),
                "--out",
                str(iconset / f"icon_{size}x{size}.png"),
            ],
            check=True,
            capture_output=True,
        )
        if size >= 32 and size <= 512:
            subprocess.run(
                [
                    "sips",
                    "-z",
                    str(size),
                    str(size),
                    str(SOURCE),
                    "--out",
                    str(iconset / f"icon_{size//2}x{size//2}@2x.png"),
                ],
                check=True,
                capture_output=True,
            )

    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(BUILD_DIR / "icon.icns")],
        check=True,
    )
    print(f"Created {BUILD_DIR / 'icon.icns'}")

    # Also create .ico and .png using sips
    subprocess.run(
        [
            "sips",
            "-z",
            "256",
            "256",
            str(SOURCE),
            "--out",
            str(BUILD_DIR / "icon.png"),
        ],
        check=True,
        capture_output=True,
    )
    print(f"Created {BUILD_DIR / 'icon.png'}")

    # For .ico on macOS without Pillow, just copy PNG and warn
    print("Warning: .ico generation requires Pillow on macOS")
    print("Windows builds may fail without proper .ico file")

    shutil.rmtree(iconset)


if __name__ == "__main__":
    main()
