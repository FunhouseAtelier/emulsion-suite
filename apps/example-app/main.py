"""
Emulsion example application.

Demonstrates:
- Two islands (Counter, ProductCard) embedded in Jinja2 templates
- SPA navigation between pages (React Router Data Mode)
- The ?format=json endpoint for React Router loaders
"""

from emulsion import EmulsionApp, EmulsionPage

app = EmulsionApp(
    title="Emulsion Example",
    debug=True,
)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.page("/")
class HomePage(EmulsionPage):
    template = "home.html"
    islands = ["Counter"]
    title = "Home — Emulsion Example"

    async def data(self) -> dict:
        return {
            "heading": "Welcome to Emulsion",
            "subheading": "A Python-first framework with React islands.",
            "products": [
                {"id": "1", "name": "Widget Pro", "price": 29.99},
                {"id": "2", "name": "Gadget Max", "price": 49.99},
                {"id": "3", "name": "Thingamajig", "price": 14.99},
            ],
        }


@app.page("/products/{product_id}")
class ProductPage(EmulsionPage):
    template = "product.html"
    islands = ["AddToCart", "ReviewCarousel"]
    title = "Product Detail — Emulsion Example"

    async def data(self, product_id: str) -> dict:
        # In a real app, fetch from a database
        products = {
            "1": {"id": "1", "name": "Widget Pro", "price": 29.99, "in_stock": True,
                  "description": "The finest widget money can buy."},
            "2": {"id": "2", "name": "Gadget Max", "price": 49.99, "in_stock": True,
                  "description": "Maximise your gadget experience."},
            "3": {"id": "3", "name": "Thingamajig", "price": 14.99, "in_stock": False,
                  "description": "A thingamajig for all occasions."},
        }
        product = products.get(product_id, {"id": product_id, "name": "Unknown", "price": 0.0,
                                            "in_stock": False, "description": ""})
        return {"product": product}


# ---------------------------------------------------------------------------
# ASGI entry point (uvicorn main:app)
# ---------------------------------------------------------------------------
# EmulsionApp implements __call__, so it is itself an ASGI app.
