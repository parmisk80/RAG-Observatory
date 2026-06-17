from fastapi import APIRouter
from models.models import MetricsResponse
from celery_tasks.Celery_tasks import aggregate_metrics , celery_app
from celery.result import AsyncResult

router = APIRouter(prefix='/api/v1/metrics' , tags=['Metrics'])

@router.get("/metrics")
async def metrics_operations():

    task = aggregate_metrics.delay()
    
    return {"task_id" : task.id , "status" : "queued"}




@router.get("/result/{task_id}")
async def retrieval_result(task_id: str):

    result = AsyncResult(task_id, app=celery_app)

    if result.state in ("PENDING", "STARTED"):
        return {"status": "processing"}

    if result.state == "FAILURE":
        return {"status": "failed"}

    if result.state == "SUCCESS":
        return {
            "status": "completed",
            "result": result.get()}

    return {"status": "processing"}