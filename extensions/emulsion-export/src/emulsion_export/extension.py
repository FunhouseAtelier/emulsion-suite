"""
ExportExtension — Emulsion extension for exporting website templates.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from emulsion.extensions import EmulsionExtension
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .exporter import TemplateExporter

if TYPE_CHECKING:
    from emulsion.app import EmulsionApp


class ExportExtension(EmulsionExtension):
    """
    Exports an Emulsion website as a portable template bundle.

    Args:
        output_dir:  Directory to write the export bundle.
        prefix:      URL prefix for export admin routes. Default: "/admin/export".
    """

    name = "export"
    version = "0.1.0"

    def __init__(
        self,
        output_dir: str | Path = "./exports",
        prefix: str = "/admin/export",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.prefix = prefix
        self._exporter = TemplateExporter(output_dir=self.output_dir)

    def on_app_created(self, app: "EmulsionApp") -> None:
        """Register export admin routes."""
        router = APIRouter(prefix=self.prefix, tags=["export"])

        @router.post("/run")
        async def run_export() -> JSONResponse:
            """Trigger a full site export."""
            result = await self._exporter.run()
            return JSONResponse(result)

        @router.get("/status")
        async def export_status() -> JSONResponse:
            """Return export status and output directory info."""
            return JSONResponse({
                "output_dir": str(self.output_dir.resolve()),
                "exists": self.output_dir.exists(),
            })

        app.fastapi.include_router(router)

    def on_build_complete(self, manifest_path: str) -> None:
        """Copy the island manifest into the export output directory."""
        src = Path(manifest_path)
        if src.exists():
            dest = self.output_dir / ".vite" / "island-manifest.json"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(src.read_bytes())
