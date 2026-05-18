"""Make routing engine importable without Home Assistant installed.

The full package (``custom_components/benni_notification_router/__init__.py``)
imports Home Assistant, which is not installed in the test env. We side-load
the package as a namespace pointing at the component directory and stub out
``__init__`` so submodules with only stdlib deps (``const``, ``routing``)
import cleanly.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG_DIR = ROOT / "custom_components" / "benni_notification_router"

pkg = types.ModuleType("benni_notification_router")
pkg.__path__ = [str(PKG_DIR)]
sys.modules.setdefault("benni_notification_router", pkg)
