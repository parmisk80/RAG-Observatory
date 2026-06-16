from fastapi import APIRouter , status , HTTPException
from models.models import  EvaluationRequest , EvaluationResponse 
from celery_tasks.Celery_tasks import evaluation_report , celery_app
from celery.result import AsyncResult


router = APIRouter(prefix='/api/v1/evaluation' , tags=['Evaluation'])

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