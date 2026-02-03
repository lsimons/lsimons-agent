# Build System Design: Binary Distribution

## Decisions

- **Code signing:** Deferred (can add later)
- **Auto-update:** Yes, using GitHub Releases as backend
- **Icons:** Generated from `docs/Leo-Bot.png`
- **Linux formats:** AppImage only (for now)
- **Build orchestration:** npm scripts + Python script (Option B)

## Goal

Create distributable installers for Windows, Mac, and Linux that:
- Include embedded Python runtime (no system Python required)
- Include embedded Node.js/Electron runtime
- Work offline after installation
- Feel like a native app (icons, file associations, etc.)

## Current Architecture

```
User launches Electron app
    → Electron spawns `uv run lsimons-agent-web`
    → FastAPI server starts on localhost:8765
    → Electron loads http://127.0.0.1:8765
```

**Problem:** This requires `uv` and Python to be installed on the user's system.

## Proposed Architecture

```
User launches Electron app
    → Electron spawns bundled Python executable
    → FastAPI server starts on localhost:8765
    → Electron loads http://127.0.0.1:8765
```

**Change:** Bundle a standalone Python executable instead of relying on system Python/uv.

## Components to Bundle

| Component | Tool | Output |
|-----------|------|--------|
| Python backend | PyInstaller | Single executable or directory |
| Electron frontend | electron-builder | Platform-specific installer |
| Combined | electron-builder extraFiles | Single distributable |

## Recommended Approach: PyInstaller + electron-builder

### Step 1: PyInstaller for Python Backend

Create a standalone executable from `lsimons-agent-web`:

```
packages/lsimons-agent-web/
├── lsimons-agent-web.spec    # PyInstaller spec file
└── ...
```

PyInstaller will bundle:
- Python 3.12 interpreter
- All Python dependencies (fastapi, uvicorn, httpx, etc.)
- lsimons-agent package
- lsimons-agent-web package
- Templates and static files

Output:
- **Mac:** `dist/lsimons-agent-web` (Mach-O executable)
- **Windows:** `dist/lsimons-agent-web.exe`
- **Linux:** `dist/lsimons-agent-web` (ELF executable)

### Step 2: electron-builder for Electron App

```
packages/lsimons-agent-electron/
├── electron-builder.yml      # Build configuration
├── main.js                   # Updated to find bundled Python
├── build/                    # Icons and assets
│   ├── icon.icns            # macOS
│   ├── icon.ico             # Windows
│   └── icon.png             # Linux
└── ...
```

electron-builder will:
- Package Electron runtime
- Include the PyInstaller output as extraFiles
- Create platform-specific installers

Output:
- **Mac:** `.dmg` installer + `.app` bundle
- **Windows:** `.exe` installer (NSIS or MSI)
- **Linux:** `.AppImage`, `.deb`, `.rpm`

### Step 3: Modified main.js

```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

// Auto-updater (only used in packaged builds)
let autoUpdater;
if (app.isPackaged) {
  autoUpdater = require('electron-updater').autoUpdater;
}

const SERVER_URL = 'http://127.0.0.1:8765';
const PROJECT_ROOT = path.join(__dirname, '..', '..');

let mainWindow;
let serverProcess;

function getServerCommand() {
  if (app.isPackaged) {
    // In packaged app, use bundled executable
    const ext = process.platform === 'win32' ? '.exe' : '';
    return {
      command: path.join(process.resourcesPath, 'backend', `lsimons-agent-web${ext}`),
      args: [],
      options: {}
    };
  } else {
    // In development, use uv
    return {
      command: 'uv',
      args: ['run', 'lsimons-agent-web'],
      options: { cwd: PROJECT_ROOT }
    };
  }
}

function startServer() {
  const { command, args, options } = getServerCommand();
  serverProcess = spawn(command, args, {
    ...options,
    stdio: ['ignore', 'pipe', 'pipe']
  });
  // ... rest of server startup logic
}

// Auto-update setup
function setupAutoUpdater() {
  if (!autoUpdater) return;

  autoUpdater.on('update-downloaded', (info) => {
    const { dialog } = require('electron');
    dialog.showMessageBox({
      type: 'info',
      title: 'Update Ready',
      message: `Version ${info.version} is ready. Restart to apply?`,
      buttons: ['Restart', 'Later']
    }).then((result) => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  });

  autoUpdater.checkForUpdatesAndNotify();
}

app.whenReady().then(() => {
  startServer();
  // ... create window
  setupAutoUpdater();
});
```

## Directory Structure (Packaged App)

```
lsimons-agent.app/                    # macOS
├── Contents/
│   ├── MacOS/
│   │   └── lsimons-agent            # Electron main process
│   ├── Resources/
│   │   ├── app.asar                 # Electron app code
│   │   └── backend/
│   │       └── lsimons-agent-web    # PyInstaller output
│   └── Info.plist

lsimons-agent/                        # Windows (installed)
├── lsimons-agent.exe                 # Electron main process
├── resources/
│   ├── app.asar
│   └── backend/
│       └── lsimons-agent-web.exe
└── ...
```

## Build Scripts

npm scripts orchestrate the build, calling a Python script for backend bundling:

```json
// packages/lsimons-agent-electron/package.json
{
  "scripts": {
    "build:icons": "cd ../.. && uv run python scripts/build_icons.py",
    "build:backend": "cd ../.. && uv run python scripts/build_backend.py",
    "build:mac": "npm run build:icons && npm run build:backend && electron-builder --mac",
    "build:win": "npm run build:icons && npm run build:backend && electron-builder --win",
    "build:linux": "npm run build:icons && npm run build:backend && electron-builder --linux",
    "build": "npm run build:icons && npm run build:backend && electron-builder"
  }
}
```

### Icon Generation Script

```python
# scripts/build_icons.py
"""Generate platform-specific icons from docs/Leo-Bot.png"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "docs" / "Leo-Bot.png"
BUILD_DIR = ROOT / "packages" / "lsimons-agent-electron" / "build"


def main():
    BUILD_DIR.mkdir(exist_ok=True)

    # Check for required tools
    # macOS: use sips (built-in) + iconutil
    # All platforms: use Pillow as fallback

    try:
        from PIL import Image
        generate_with_pillow()
    except ImportError:
        print("Pillow not installed, trying platform tools...")
        if sys.platform == "darwin":
            generate_mac_icons_native()
        else:
            print("Install Pillow: uv add pillow --dev")
            sys.exit(1)


def generate_with_pillow():
    from PIL import Image

    img = Image.open(SOURCE)

    # Windows .ico (multiple sizes embedded)
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = [img.resize(size, Image.LANCZOS) for size in ico_sizes]
    ico_images[0].save(
        BUILD_DIR / "icon.ico",
        format="ICO",
        sizes=ico_sizes,
        append_images=ico_images[1:]
    )
    print(f"Created {BUILD_DIR / 'icon.ico'}")

    # Linux .png (256x256)
    img.resize((256, 256), Image.LANCZOS).save(BUILD_DIR / "icon.png")
    print(f"Created {BUILD_DIR / 'icon.png'}")

    # macOS .icns (requires iconset folder)
    if sys.platform == "darwin":
        generate_icns_with_pillow(img)


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
        if size <= 512:
            resized.save(iconset / f"icon_{size//2}x{size//2}@2x.png")

    # Use iconutil to create .icns
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(BUILD_DIR / "icon.icns")],
        check=True
    )
    print(f"Created {BUILD_DIR / 'icon.icns'}")

    # Clean up iconset folder
    import shutil
    shutil.rmtree(iconset)


def generate_mac_icons_native():
    """macOS-only: use sips and iconutil"""
    iconset = BUILD_DIR / "icon.iconset"
    iconset.mkdir(exist_ok=True)

    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in sizes:
        subprocess.run([
            "sips", "-z", str(size), str(size),
            str(SOURCE), "--out", str(iconset / f"icon_{size}x{size}.png")
        ], check=True)
        if size <= 512:
            subprocess.run([
                "sips", "-z", str(size), str(size),
                str(SOURCE), "--out", str(iconset / f"icon_{size//2}x{size//2}@2x.png")
            ], check=True)

    subprocess.run([
        "iconutil", "-c", "icns", str(iconset), "-o", str(BUILD_DIR / "icon.icns")
    ], check=True)

    import shutil
    shutil.rmtree(iconset)


if __name__ == "__main__":
    main()
```

### Backend Build Script

```python
# scripts/build_backend.py
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
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--clean", str(spec_file)],
        cwd=WEB_PACKAGE,
        check=True
    )

    print(f"Backend built successfully in {WEB_PACKAGE / 'dist'}")


if __name__ == "__main__":
    main()
```

## electron-builder Configuration

```yaml
# packages/lsimons-agent-electron/electron-builder.yml
appId: com.lsimons.agent
productName: lsimons-agent
directories:
  output: dist
  buildResources: build

# Auto-update via GitHub Releases
publish:
  provider: github
  owner: lsimons
  repo: lsimons-agent

extraFiles:
  - from: "../lsimons-agent-web/dist/lsimons-agent-web"
    to: "backend"
    filter:
      - "**/*"

mac:
  category: public.app-category.developer-tools
  target:
    - dmg
    - zip  # Required for auto-update on Mac
  icon: build/icon.icns

win:
  target:
    - nsis
  icon: build/icon.ico

linux:
  target:
    - AppImage
  icon: build/icon.png
  category: Development

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
```

## PyInstaller Spec File

```python
# packages/lsimons-agent-web/lsimons-agent-web.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/lsimons_agent_web/server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='lsimons-agent-web',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

## Auto-Updater Implementation

### Dependencies

Add `electron-updater` to the electron package:

```json
// packages/lsimons-agent-electron/package.json
{
  "dependencies": {
    "electron-updater": "^6.1.0"
  }
}
```

### Auto-Update Code

Add to main.js:

```javascript
const { autoUpdater } = require('electron-updater');

// Configure logging
autoUpdater.logger = require('electron-log');
autoUpdater.logger.transports.file.level = 'info';

// Check for updates after app is ready
app.whenReady().then(() => {
  // Only check for updates in packaged app
  if (app.isPackaged) {
    autoUpdater.checkForUpdatesAndNotify();
  }
});

// Auto-updater events
autoUpdater.on('update-available', (info) => {
  console.log('Update available:', info.version);
});

autoUpdater.on('update-downloaded', (info) => {
  // Prompt user to restart
  const { dialog } = require('electron');
  dialog.showMessageBox({
    type: 'info',
    title: 'Update Ready',
    message: `Version ${info.version} has been downloaded. Restart to apply the update?`,
    buttons: ['Restart', 'Later']
  }).then((result) => {
    if (result.response === 0) {
      autoUpdater.quitAndInstall();
    }
  });
});

autoUpdater.on('error', (err) => {
  console.error('Auto-update error:', err);
});
```

### Release Process

To publish a new release:

1. Update version in `packages/lsimons-agent-electron/package.json`
2. Build all platforms: `npm run build`
3. Create GitHub release with the version tag (e.g., `v1.0.0`)
4. Upload artifacts from `packages/lsimons-agent-electron/dist/`:
   - Mac: `.dmg` and `.zip` (zip required for auto-update)
   - Windows: `.exe`
   - Linux: `.AppImage`
5. Publish the release

electron-builder can also publish directly:
```bash
# Set GitHub token
export GH_TOKEN=your_github_token

# Build and publish
npm run build -- --publish always
```

## Alternatives Considered

### Alternative 1: Embed Python + uv directly

Bundle a portable Python installation and uv binary alongside Electron.

**Pros:**
- No PyInstaller complexity
- Can update Python packages without rebuilding

**Cons:**
- Larger bundle size (~100MB+ for Python)
- More complex path management
- Need to bundle uv for each platform

### Alternative 2: Briefcase (BeeWare)

Use Briefcase to create native app bundles for Python.

**Pros:**
- Designed for Python apps
- Native packaging for each platform

**Cons:**
- Would need to restructure to fit Briefcase model
- Less control over Electron integration
- Two different "app bundling" tools

### Alternative 3: PyOxidizer

Use PyOxidizer instead of PyInstaller.

**Pros:**
- Single-file executables
- Rust-based, potentially faster startup

**Cons:**
- Less mature than PyInstaller
- More complex configuration
- Some library compatibility issues

### Alternative 4: Tauri instead of Electron

Replace Electron with Tauri (Rust-based).

**Pros:**
- Much smaller bundle size
- Better security model

**Cons:**
- Major rewrite of frontend integration
- Still need to solve Python bundling
- Not addressing the actual problem

## Recommendation

**PyInstaller + electron-builder** is the recommended approach because:

1. **Mature tooling** - Both tools are well-documented and widely used
2. **Minimal code changes** - Only main.js needs modification
3. **Clear separation** - Python backend and Electron frontend built separately
4. **CI/CD friendly** - Both support automated builds
5. **Cross-platform** - Both support all three target platforms

## Implementation Phases

### Phase 1: Local Mac Build
1. Add PyInstaller and Pillow as dev dependencies
2. Create `scripts/build_icons.py`
3. Create `scripts/build_backend.py`
4. Create `packages/lsimons-agent-web/lsimons-agent-web.spec`
5. Test PyInstaller build locally
6. Update main.js to detect packaged mode and spawn bundled backend
7. Add electron-updater dependency
8. Add auto-update code to main.js
9. Create `packages/lsimons-agent-electron/electron-builder.yml`
10. Update `packages/lsimons-agent-electron/package.json` with build scripts
11. Test full build on Mac

### Phase 2: Cross-Platform Builds
1. Test Windows build (can use Wine or VM)
2. Test Linux build (AppImage)
3. Adjust spec/config as needed

### Phase 3: CI/CD (Future)
1. GitHub Actions workflow for automated builds
2. Code signing for Mac/Windows
3. Auto-publish to GitHub Releases

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `scripts/build_icons.py` | Create | Icon generation script |
| `scripts/build_backend.py` | Create | PyInstaller wrapper script |
| `packages/lsimons-agent-web/lsimons-agent-web.spec` | Create | PyInstaller spec file |
| `packages/lsimons-agent-electron/main.js` | Modify | Add packaged mode detection + auto-update |
| `packages/lsimons-agent-electron/package.json` | Modify | Add build scripts + electron-updater |
| `packages/lsimons-agent-electron/electron-builder.yml` | Create | Build configuration |
| `pyproject.toml` | Modify | Add pyinstaller, pillow to dev deps |
| `.gitignore` | Modify | Add build output directories |
| `docker/Dockerfile.builder` | Create | Docker image for cross-platform builds |
| `.github/workflows/build.yml` | Create | CI/CD workflow for releases |

## Build Environments

### Local Development (Docker)

For local cross-platform builds from Mac, use Docker containers:

```json
// packages/lsimons-agent-electron/package.json
{
  "scripts": {
    "build:linux:docker": "docker run --rm -v \"$(pwd)/../..:/project\" -w /project/packages/lsimons-agent-electron electronuserland/builder:18 bash -c \"npm run build:backend && npm run build:linux\"",
    "build:win:docker": "docker run --rm -v \"$(pwd)/../..:/project\" -w /project/packages/lsimons-agent-electron electronuserland/builder:18-wine bash -c \"npm run build:backend && npm run build:win\""
  }
}
```

**Docker images used:**
- `electronuserland/builder:18` - Linux builds (Node 18 + build tools)
- `electronuserland/builder:18-wine` - Windows builds (includes Wine)

**Note:** These containers need Python 3.12+ and uv installed. Create a custom Dockerfile:

```dockerfile
# docker/Dockerfile.builder
FROM electronuserland/builder:18-wine

# Install Python 3.12 and uv
RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.12 python3.12-venv python3.12-dev \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -sf /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /project
```

Build and use custom image:
```bash
# Build the image (one-time)
docker build -t lsimons-agent-builder -f docker/Dockerfile.builder .

# Use for builds
npm run build:linux:docker  # Uses custom image
npm run build:win:docker    # Uses custom image
```

Updated scripts with custom image:
```json
{
  "scripts": {
    "build:linux:docker": "docker run --rm -v \"$(pwd)/../..:/project\" -w /project/packages/lsimons-agent-electron lsimons-agent-builder bash -c \"cd ../.. && uv sync && cd packages/lsimons-agent-electron && npm ci && npm run build:linux\"",
    "build:win:docker": "docker run --rm -v \"$(pwd)/../..:/project\" -w /project/packages/lsimons-agent-electron lsimons-agent-builder bash -c \"cd ../.. && uv sync && cd packages/lsimons-agent-electron && npm ci && npm run build:win\""
  }
}
```

### CI/CD (GitHub Actions)

Native runners for each platform ensure best compatibility:

```yaml
# .github/workflows/build.yml
name: Build

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-mac:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - uses: astral-sh/setup-uv@v4
      - name: Install dependencies
        run: |
          uv sync
          cd packages/lsimons-agent-electron && npm ci
      - name: Build
        run: cd packages/lsimons-agent-electron && npm run build:mac
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/upload-artifact@v4
        with:
          name: mac-build
          path: packages/lsimons-agent-electron/dist/*.dmg

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - uses: astral-sh/setup-uv@v4
      - name: Install dependencies
        run: |
          uv sync
          cd packages/lsimons-agent-electron && npm ci
      - name: Build
        run: cd packages/lsimons-agent-electron && npm run build:win
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/upload-artifact@v4
        with:
          name: windows-build
          path: packages/lsimons-agent-electron/dist/*.exe

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - uses: astral-sh/setup-uv@v4
      - name: Install dependencies
        run: |
          uv sync
          cd packages/lsimons-agent-electron && npm ci
      - name: Build
        run: cd packages/lsimons-agent-electron && npm run build:linux
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/upload-artifact@v4
        with:
          name: linux-build
          path: packages/lsimons-agent-electron/dist/*.AppImage

  release:
    needs: [build-mac, build-windows, build-linux]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - uses: actions/download-artifact@v4
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            mac-build/*.dmg
            mac-build/*.zip
            windows-build/*.exe
            linux-build/*.AppImage
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Build Environment Summary

| Platform | Local Dev | CI/CD |
|----------|-----------|-------|
| macOS | Native (`npm run build:mac`) | `macos-latest` runner |
| Windows | Docker (`npm run build:win:docker`) | `windows-latest` runner |
| Linux | Docker (`npm run build:linux:docker`) | `ubuntu-latest` runner |
