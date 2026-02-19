from fastapi import FastAPI
from adapter.rest import router as investments_router

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