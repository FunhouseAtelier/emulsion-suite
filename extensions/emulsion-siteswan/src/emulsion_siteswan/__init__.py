"""
emulsion-siteswan — SiteSwan website importer extension for Emulsion.

Provides:
- SiteSwanExtension: hooks into EmulsionApp to add import routes
- SiteSwanImporter: downloads and converts SiteSwan sites

Usage:
    from emulsion import EmulsionApp
    from emulsion_siteswan import SiteSwanExtension

    app = EmulsionApp(
        extensions=[SiteSwanExtension(site_id="abc123")]
    )
"""

from .extension import SiteSwanExtension
from .importer import SiteSwanImporter

__all__ = ["SiteSwanExtension", "SiteSwanImporter"]
