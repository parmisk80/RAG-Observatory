from fastapi import APIRouter , status , HTTPException
from fastapi.responses import JSONResponse
from models.models import AskRequest , AskResponse


router = APIRouter(prefix="/api/v1" , tags=["Ask"])

@router.post("/ask")
async def ask_question(request : AskRequest):
    if request.question.strip() == "":
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST , detail = "Question cannot be empty")
    return JSONResponse(status_code = status.HTTP_202_ACCEPTED , content = {'task_id' : "Task_123" , 'status' : "processing"}) 



@router.get("answer/{task_id}" , response_model=AskResponse)
async def get_answer(task_id : str):
    if task_id != 'Task_123':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='Task not found')
    response = AskResponse(answer = 'FastAPI is a modern Python web framework.',
                           conversation_id = 'cpnv_123' , 
                           retrieved_documnets = [{
                               "document_id" : 'doc_1' , 
                               "chunk_id" : 'chunk_1' ,
                               "document_source_id" : 'source_1' , 
                               "score" : 0.95
                           }])
    
    return response