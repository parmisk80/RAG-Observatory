from fastapi import APIRouter , status , HTTPException 
from fastapi.responses import JSONResponse
from models.models import ErrorResponse

router = APIRouter(prefix='/api/v1/errors' , tags=['Errors'])

@router.get("/errors" , response_model=ErrorResponse)
async def get_errors():

    response = ErrorResponse(detail = 'invalid request' , error_code = '400_BAD_REQUEST')

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST , content=response.model.dump())