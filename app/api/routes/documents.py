from fastapi import APIRouter , status , HTTPException , UploadFile , File , Form
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from models.models import DocumentMetadata , UploadResponse


router = APIRouter(prefix='/api/v1/documents' , tags=['Documents'])


upload_dir = Path("uploaded_documents")
upload_dir.mkdir(exist_ok= True)


@router.post("/upload" , response_model=UploadResponse)
async def upload_document(file : UploadFile = File(...) , title : str = Form(...) , source : str = Form(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail='Only PDF files are allowed.')
    

    file_path = upload_dir / file.filename
    with open(file_path , "wb") as buffer:
        shutil.copyfileobj(file.file , buffer)


    metadata = DocumentMetadata(title = title , source = source , tags = ['rag' , 'ai'] , uploaded_by_user_id = "user_123")

    response = UploadResponse(document_id = "doc_123" , file_name = file.filename , chunk_created = 15 , status = "uploaded")

    return JSONResponse(status_code=status.HTTP_201_CREATED , content=response.model_dump())
