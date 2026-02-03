"""Build Python backend with PyInstaller"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
WEB_PACKAGE = ROOT / "packages" / "lsimons-agent-web"


def main():
    spec_file = WEB_PACKAGE / "lsimons-agent-web.spec"

    if not spec_file.exists():
        print(f"Error: {spec_file} not found")
        sys.exit(1)

    # Run PyInstaller
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(spec_file)],
        cwd=WEB_PACKAGE,
    )

    if result.returncode != 0:
        print("PyInstaller build failed")
        sys.exit(1)

    print(f"Backend built successfully in {WEB_PACKAGE / 'dist'}")


if __name__ == "__main__":
    main()
