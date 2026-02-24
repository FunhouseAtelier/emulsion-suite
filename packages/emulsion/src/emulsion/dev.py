"""
Development server orchestration.

Runs FastAPI (uvicorn) and Vite concurrently via asyncio subprocesses.
Both processes share stdout/stderr so their logs are interleaved in the terminal.
"""

from __future__ import annotations

import asyncio
import os
import signal
import sys


async def run_dev_server(
    app_module: str,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    vite_port: int = 5173,
    reload_dirs: list[str] | None = None,
) -> None:
    """
    Start the Emulsion development server.

    Concurrently runs:
      - uvicorn <app_module> --reload   on <host>:<port>
      - pnpm vite --port <vite_port>

    Environment variables set for the duration:
      EMULSION_DEV_MODE=true
      EMULSION_VITE_PORT=<vite_port>
    """
    os.environ["EMULSION_DEV_MODE"] = "true"
    os.environ["EMULSION_VITE_PORT"] = str(vite_port)

    reload_dir_args: list[str] = []
    for d in (reload_dirs or ["."]):
        reload_dir_args += ["--reload-dir", d]

    uvicorn_cmd = [
        sys.executable, "-m", "uvicorn",
        app_module,
        "--host", host,
        "--port", str(port),
        "--reload",
        *reload_dir_args,
    ]

    vite_cmd = ["pnpm", "vite", "--port", str(vite_port)]

    print(f"[emulsion] FastAPI  → http://{host}:{port}")
    print(f"[emulsion] Vite HMR → http://localhost:{vite_port}")
    print("[emulsion] Press Ctrl+C to stop\n")

    uvicorn_proc = await asyncio.create_subprocess_exec(
        *uvicorn_cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    vite_proc = await asyncio.create_subprocess_exec(
        *vite_cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    loop = asyncio.get_running_loop()

    def _shutdown(*_: object) -> None:
        uvicorn_proc.terminate()
        vite_proc.terminate()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown)
        except (NotImplementedError, OSError):
            # Windows doesn't support add_signal_handler for all signals
            signal.signal(sig, _shutdown)  # type: ignore[arg-type]

    await asyncio.gather(
        uvicorn_proc.wait(),
        vite_proc.wait(),
        return_exceptions=True,
    )
