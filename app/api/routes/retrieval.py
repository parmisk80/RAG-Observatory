from fastapi import APIRouter , status , HTTPException
from models.models import RetrievalSearchRequest
from celery_tasks.Celery_tasks import retrieval_context , celery_app
from celery.result import AsyncResult


router = APIRouter(prefix='/api/v1/retrieval' , tags=['Retrieval'])

@router.post("/search")
async def retrieval_serach(request : RetrievalSearchRequest):

    if request.query.strip() == "" :

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail='Query can not be empty')
    

    task = retrieval_context.delay(query = request.query)

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