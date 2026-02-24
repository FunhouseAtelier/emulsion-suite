"""
Emulsion — A Python-first web framework fusing FastAPI with React islands.

Usage:
    from emulsion import EmulsionApp, EmulsionPage

    app = EmulsionApp()

    @app.page("/")
    class HomePage(EmulsionPage):
        template = "home.html"

        async def data(self) -> dict:
            return {"title": "Welcome"}
"""

from .app import EmulsionApp
from .page import EmulsionPage
from .extensions import EmulsionExtension

__all__ = ["EmulsionApp", "EmulsionPage", "EmulsionExtension"]
__version__ = "0.1.0"
