"""
emulsion-export — website template exporter extension for Emulsion.

Provides:
- ExportExtension: hooks into EmulsionApp to add export routes
- TemplateExporter: crawls the app and generates a portable export bundle

Usage:
    from emulsion import EmulsionApp
    from emulsion_export import ExportExtension

    app = EmulsionApp(
        extensions=[ExportExtension(output_dir="./exports")]
    )
"""

from .extension import ExportExtension
from .exporter import TemplateExporter

__all__ = ["ExportExtension", "TemplateExporter"]
