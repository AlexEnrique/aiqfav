from fastapi import FastAPI

from .routes.v1.customers import router as customers_router_v1
from .routes.v1.products import router as products_router_v1

__all__ = ['create_app']


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(customers_router_v1, prefix='/v1')
    app.include_router(products_router_v1, prefix='/v1')
    return app
