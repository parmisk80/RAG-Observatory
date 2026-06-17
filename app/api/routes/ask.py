from celery.result import AsyncResult
from fastapi import APIRouter , status , HTTPException
from fastapi.responses import JSONResponse
from models.models import AskRequest 
from celery_tasks.Celery_tasks import ask_rag , celery_app


router = APIRouter(prefix="/api/v1" , tags=["Ask"])

@router.post("/ask")
def ask(payload: AskRequest):
    
    task = ask_rag.delay(question=payload.question , conversation_id=payload.conversation_id)

    return {"task_id": task.id , "status" : "queued"}


@router.get("/answer/{task_id}" , response_model=None)
async def answer(task_id: str):
    result = AsyncResult(task_id, app=celery_app)


    if result.state == "Pending" or result.state == "Started":

        return {"status" : "processing"}

    if result.state == "Failure":

        return {'status' : "failed"}
    
    if result.state == "Success":

        return { "status": "completed" , "data": result.get() }


    return {"status": "processing"}