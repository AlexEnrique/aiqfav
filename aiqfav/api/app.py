from fastapi import FastAPI

from .routes.customers_v1 import router as customers_router_v1

__all__ = ['create_app']


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(customers_router_v1, prefix='/v1')
    return app
