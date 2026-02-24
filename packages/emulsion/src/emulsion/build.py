"""
Production build orchestration.

Runs the Vite build (which invokes @emulsion/vite-plugin) to produce:
  - static/islands/<name>-<hash>.js   per-island bundles
  - static/islands/emulsion-hydration-<hash>.js   the page-level hydration entry
  - static/.vite/island-manifest.json   maps island names → hashed filenames
"""

from __future__ import annotations

import asyncio
import sys


async def run_build(output_dir: str = "static") -> int:
    """
    Run `pnpm vite build` and return the exit code.

    The Vite config (vite.config.ts in the app directory) is responsible for
    configuring the output directory and invoking @emulsion/vite-plugin.
    """
    cmd = ["pnpm", "vite", "build"]

    print(f"[emulsion] Building islands → {output_dir}/")

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    await proc.wait()
    code = proc.returncode or 0

    if code == 0:
        print(f"[emulsion] Build complete → {output_dir}/")
    else:
        print(f"[emulsion] Build failed (exit {code})", file=sys.stderr)

    return code
