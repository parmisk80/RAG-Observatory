from fastapi import FastAPI

from api.routes.ask import router as ask_router
from api.routes.documents import router as documents_router
from api.routes.retrieval import router as retrieval_router
from api.routes.evaluation import router as evaluation_router
from api.routes.metrics import router as metrics_router
from api.routes.Error import router as Error_router

app = FastAPI(
    title="RAG Observatory API",
    version="1.0.0"
)


app.include_router(ask_router)

app.include_router(documents_router)

app.include_router(retrieval_router)

app.include_router(evaluation_router)

app.include_router(metrics_router)

app.include_router(Error_router)


@app.get("/health")
async def health_check():

    return {
        "status": "healthy"
    }