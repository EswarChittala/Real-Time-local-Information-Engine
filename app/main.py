from fastapi import FastAPI
from app.api.routes import health, observations, questions
from app.core.config import settings

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Real-Time Hyperlocal Information Engine API"
)

# Register routes
app.include_router(health.router)
app.include_router(observations.router)
app.include_router(questions.router)

@app.get("/")
def root():
    return {
        "engine": settings.project_name,
        "version": settings.version,
        "docs": "/docs"
    }
