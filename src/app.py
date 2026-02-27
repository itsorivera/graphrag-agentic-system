from fastapi import FastAPI
from src.adapter.rest import router as investments_router

import logging

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(investments_router)
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy",
                "message": "The application is running smoothly!"}

    @app.get("/health/liveness")
    async def liveness_check():
        return {"status": "alive"}

    @app.get("/health/readiness")
    async def readiness_check():
        return {"status": "ready"}

    return app

app = create_app()