from fastapi import APIRouter , status , HTTPException , UploadFile , File , Form
from fastapi.responses import JSONResponse
from pathlib import Path
import random
import shutil
from models.models import DocumentMetadata , UploadResponse
from celery_tasks.tasks import process_document


router = APIRouter(prefix='/api/v1/documents' , tags=['Documents'])


upload_dir = Path("uploaded_documents")
upload_dir.mkdir(exist_ok= True)


@router.post("/upload" , response_model=UploadResponse)
async def upload_document(file : UploadFile = File(...) , title : str = Form(...) , source : str = Form(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail='Only PDF files are allowed.')
    
    doc_id = random.randint(10000, 50000)

    file_path = upload_dir / file.filename
    with open(file_path , "wb") as buffer:
        shutil.copyfileobj(file.file , buffer)

    result = process_document.delay(
        document_id=str(doc_id),
        file_path=str(file_path)
    )

    metadata = DocumentMetadata(title = title , source = source , tags = ['rag' , 'ai'] , uploaded_by_user_id = "user_123")

    response = UploadResponse(document_id = doc_id , file_name = file.filename , chunk_created = 0 , status = "uploaded", task_id=result.id, user_id=doc_id)

    return JSONResponse(status_code=status.HTTP_201_CREATED , content=response.model_dump())
