from fastapi import APIRouter , status , HTTPException
from fastapi.responses import JSONResponse
from models.models import  EvaluationRequest , EvaluationResponse 


router = APIRouter(prefix='/api/v1/evaluation' , tags=['Evaluation'])

@router.post("/evaluate" , response_model= EvaluationResponse)
async def evaluate_generated_answers(evaluate_process : EvaluationRequest):
    if evaluate_process.generated_answer.strip == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Generated answers cannot be empty")
    
    response = EvaluationResponse(faithfulness_score = 0.91 ,relevance_score = 0.88 , correctness_score = 0.93)

    return JSONResponse(status_code=status.HTTP_200_OK ,content=response.model_dump())
