from fastapi import APIRouter , status , HTTPException
from fastapi.responses import JSONResponse
from models.models import RetrievalSearchRequest , RetrievalResult , RetrievalSearchResponse


router = APIRouter(prefix='/api/v1/retrieval' , tags=['Retrieval'])

@router.get("/question/{question_id}" , response_model = RetrievalSearchRequest)
async def retrieval_serach(question_id : str):
    if question_id != "question_123":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail='Quwstion not found')
    
    results = [
        RetrievalResult( document_id = 'doc_1' , chunk_id = 'chunk_1' , content = 'RAG system use vector DB.' , similarity_score = 0.95) ,
        RetrievalResult( document_id = 'doc_2' , chunk_id = 'chunk_8' , content = 'FastAPI is a modern Framework.' , similarity_score = 0.89)
        ]
    
    if request.document_id:
        [results for result in results if result.document_id == request.document_id]
        
    response = RetrievalSearchResponse(results = results)

    return JSONResponse(status_code=status.HTTP_200_OK , content=response.model.dump())