# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for lsimons-agent-web"""

import sys
from pathlib import Path

block_cipher = None

# Get the package directory
spec_dir = Path(SPECPATH)
src_dir = spec_dir / "src" / "lsimons_agent_web"

# Also need to include lsimons-agent package
agent_src = spec_dir.parent / "lsimons-agent" / "src"

a = Analysis(
    [str(src_dir / "server.py")],
    pathex=[str(spec_dir / "src"), str(agent_src)],
    binaries=[],
    datas=[
        ("templates", "templates"),
        ("static", "static"),
    ],
    hiddenimports=[
        # uvicorn internals
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        # fastapi/starlette
        "starlette.routing",
        "starlette.middleware",
        "starlette.middleware.errors",
        # our packages
        "lsimons_agent",
        "lsimons_agent.agent",
        "lsimons_agent.llm",
        "lsimons_agent.tools",
        "lsimons_agent_web",
        "lsimons_agent_web.server",
        # httpx
        "httpx",
        "httpcore",
        "h11",
        "anyio",
        "sniffio",
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
    name="lsimons-agent-web",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
