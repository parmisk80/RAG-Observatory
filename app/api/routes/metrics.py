from fastapi import APIRouter , status , HTTPException
from fastapi.responses import JSONResponse
from models import MetricsResponse


router = APIRouter(prefix='api/v1/metrics' , tags=['Metrics'])

@router.get("/metrics" , response_model=MetricsResponse)
async def metrics_operations():
    response = MetricsResponse(total_request = 120, total_documents =35 , average_response_time =1.42 ,average_retrieval_time = 0.38)

    return JSONResponse(status_code=status.HTTP_200_OK , content=response.model.dump())