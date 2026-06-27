"""conftest.py — ensure agent_reach and its deps are importable in the uv pytest env.

The uv-isolated pytest binary doesn't inherit all system site-packages paths.
We add them here so that yaml, requests, etc. are used directly rather than
mocked. Loguru, rich, feedparser, and yt-dlp are not in any system path, so
they get lightweight stubs that satisfy import-time requirements without
swallowing output (rich.print maps to builtin print so capsys works).
"""
import builtins
import sys
import os
from unittest.mock import MagicMock

# 1. Project root → agent_reach importable
sys.path.insert(0, os.path.dirname(__file__))

# 2. System paths that hold yaml, requests, etc. — use real implementations
for _p in (
    "/usr/lib/python3/dist-packages",
    "/root/.local/lib/python3.11/site-packages",
):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.append(_p)

# 3. Stub deps not present in any accessible path, preserving test-observable
#    behavior (rich.print must still write to stdout so capsys can capture it).
for _mod in ("loguru", "rich", "rich.markup", "feedparser", "yt_dlp"):
    if _mod not in sys.modules:
        try:
            __import__(_mod)
        except ImportError:
            stub = MagicMock()
            sys.modules[_mod] = stub
            if _mod == "rich":
                # rich.print is imported as rprint in cli.py/_cmd_doctor —
                # map it to builtin print so capsys captures the output.
                stub.print = builtins.print
            elif _mod == "rich.markup":
                stub.escape = lambda x: x
