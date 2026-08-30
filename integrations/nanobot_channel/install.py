#!/usr/bin/env python3
"""Install the versioned imGram overlay into a nanobot v0.3.0 environment."""

from __future__ import annotations

import argparse
import importlib.metadata
import shutil
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--site-packages",
        type=Path,
        help="Directory containing the installed nanobot package (auto-detected by default).",
    )
    args = parser.parse_args()

    try:
        version = importlib.metadata.version("nanobot-ai")
    except importlib.metadata.PackageNotFoundError:
        parser.error("nanobot-ai is not installed in this Python environment")
    if version != "0.3.0":
        parser.error(f"this overlay targets nanobot-ai 0.3.0, found {version}")

    if args.site_packages is None:
        import nanobot

        site_packages = Path(nanobot.__file__).resolve().parent.parent
    else:
        site_packages = args.site_packages.resolve()

    source = Path(__file__).resolve().parent / "nanobot"
    target = site_packages / "nanobot"
    if not target.is_dir():
        parser.error(f"nanobot package not found under {site_packages}")

    channel_target = target / "channels" / "imgram"
    channel_target.mkdir(parents=True, exist_ok=True)
    for file in (source / "channels" / "imgram").glob("*.py"):
        shutil.copy2(file, channel_target / file.name)

    shutil.copy2(
        source / "agent" / "tools" / "imgram.py",
        target / "agent" / "tools" / "imgram.py",
    )
    print(f"Installed imGram nanobot overlay into {target}")
    print("Restart the nanobot gateway to load the channel and Agent tool.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
