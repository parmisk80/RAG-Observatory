from pydantic import BaseModel , Field , field_validator
from typing import Optional , List , Dict , Any , Union


"""Requset model"""
# Request payload for user questions in the RAG system
class AskRequest(BaseModel):
    user_id : str | int
    question : str = Field(min_length = 3 , max_length = 300 , description = "User question" )
    conversation_id : Optional[Union[str , int]] = None
    
    @field_validator('question')
    @classmethod
    def clean_question(cls , value):
        if value.strip() == "" :
            raise ValueError("Question field cannot be empty")
        return value
    

"""Response model"""
# Represents a retrieved document chunk returned by the retrieval pipeline
class SourceDocument(BaseModel):
    document_id : Optional[Union[str , int]]
    chunk_id : Optional[Union[str , int]]
    document_source_id : Optional[Union[str , int]]
    score : float  
    owner_user_id : str | int



# Response returned after generating an answer from the RAG pipeline
class AskResponse(BaseModel):
    answer : str = Field(min_length = 3)
    conversation_id : str
    retrieved_documents :List[SourceDocument]
    user_id : str | int


"""Metadata"""    
# Metadata associated with uploaded documents
class DocumentMetadata(BaseModel):
    title : Optional[str] = None
    source : Optional[str] = None
    tags : Optional[List[str]] = None
    uploaded_by_user_id : str | int


"""Response"""
# Response returned after successful document upload and chunking
class UploadResponse(BaseModel):
    document_id : Optional[Union[str , int]]
    file_name : str
    chunk_created : int
    status : str
    user_id : str | int


"""Request"""
# Request schema for semantic retrieval search
class RetrievalSearchRequest(BaseModel):
    query : str
    top_k : int = Field(default = 5 , ge = 1 , le = 20)   
    user_id : str | int
    document_id : str | None = None

"""Response"""
# Single retrieval result returned by the vector search system
class RetrievalResult(BaseModel):
    document_id : Optional[Union[str , int]]
    chunk_id : Optional[Union[str , int]]
    content : str
    similarity_score : float

# Aggregated retrieval search response
class RetrievalSearchResponse(BaseModel):
    results : List[RetrievalResult]


"""Request"""
# Request schema for evaluating generated answers
class EvaluationRequest(BaseModel):
    question : str = Field(min_length = 3)
    generated_answer : str = Field(min_length = 3)
    expected_answer : str = Field(min_length = 3)     


"""Response"""
# Evaluation metrics for generated responses
class EvaluationResponse(BaseModel):
    faithfulness_score : float
    relevance_score : float
    correctness_score : float


"""Response"""
# Operational metrics for monitoring system performance
class MetricsResponse(AskRequest):
    total_request : int 
    total_documents : int 
    average_response_time : float
    average_retrieval_time : float


"Response"
# Health check response used for monitoring service availability
class HealthResponse(BaseModel):
    status : str = 'Health' 


"""Error model"""
# Standardized API error response
class ErrorResponse(BaseModel):
    detail : str 
    error_code : str | None = None          

