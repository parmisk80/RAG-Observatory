"""
Celery application configuration for the RAG Observatory platform.

This module contains all asynchronous background tasks responsible for:
- Document ingestion
- PDF parsing
- Text cleaning
- Chunking
- Embedding generation
- Vector storage
- RAG evaluation
- Cache cleanup
- Metrics aggregation

The tasks are executed asynchronously using Celery workers
with Redis acting as both broker and result backend.
"""

from celery import Celery
import numpy as np
import redis
import fitz  #PyMuPDF # reading PDF.
import chromadb # database for store vectors. (embedding)
from chromadb.errors import ChromaError
import ollama # use Ollama API. (generate embedding with local models)
import unicodedata # normalize special characters.
import re # text pattern.
import logging 
from config.config import settings
from Services.ingestion_service import document_ingestion
from Services.query_rewrite_service import QueryRewriteService
from Services.generation_service import GenerationService
from Services.evaluation_service import EvaluationService
from Services.retrieval_service import RetrievalService
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset


rewrite_service = QueryRewriteService()

retrieval_service = RetrievalService()

generation_service = GenerationService()

evaluation_service = EvaluationService()


logger = logging.getLogger(__name__)

celery_app = Celery("RAG-Observatory" , broker = settings.CELERY_BROKER_URL , backend = settings.CELERY_BACKEND_URL)

# connection to servers
redis_client = redis.Redis.from_url(settings.CELERY_BACKEND_URL , decode_responses=True)
chroma_client = chromadb.HttpClient(host = settings.CHROMA_HOST, port = settings.CHROMA_PORT )



"""
End-to-end document ingestion pipeline.

This task processes uploaded PDF documents through multiple stages:
1. Parse PDF content
2. Normalize and clean extracted text
3. Split text into semantic chunks
4. Generate vector embeddings using Ollama
5. Store embeddings and metadata in ChromaDB

Args:
    document_id (str):
        Unique identifier for the uploaded document.

    file_path (str):
        Absolute or relative path to the uploaded PDF file.

Returns:
    dict:
        Dictionary containing:
        - processing status
        - document identifier
        - total generated chunks

Raises:
    Retry:
        Automatically retries the task on:
        - PDF parsing failures
        - ChromaDB failures
        - unexpected runtime exceptions
"""

# DOCUMENT INGESTION
@celery_app.task(bind = True , max_retries = 3 , default_retry_delay = 60)
def process_document(self , document_id : str , file_path : str):
        
        try:
            ingestion = document_ingestion(document_id, file_path)
            
            return ingestion
        

        except fitz.FileDataError as exc:
              logger.error(f"PDF parse error {document_id} : {exc} ")
              raise self.retry(exc = exc)
        except ChromaError as exc:
              logger.error(f"Chromadb error for {document_id} : {exc}")
              raise self.retry(exc=exc)
        except Exception as exc:
              logger.error(f"Unexpected error for {document_id}: {exc}")    
              raise self.retry(exc=exc)          
        

# QUERY REWRITE
@celery_app.task(bind = True , max_retries = 3 , default_retry_delay = 60)
def query_rewrite(self , query : str) -> str :

    try:
        query_rewriting = rewrite_service.rewrite_query(query)

        return query_rewriting
    

    except Exception as exc:
         
         logger.error(f"Query rewrite failed : {exc}")
         raise self.retry(exc = exc)   

    
# RETRIEVAL
@celery_app.task(bind = True , max_retries = 3 , default_retry_delay = 60)
def retrieval_context(self, query : str):
     
     try:
          retrieved_context = retrieval_service.retrieve_context(query=query)

          return retrieved_context
     

     except Exception as exc:
          
          logger.error(f"Retrieval failed : {exc}")
          return self.retry(exc=exc)


# GENERATION     
@celery_app.task(bind=True , max_retries=3, default_retry_delay=60)
def generate_answer(self, question: str, contexts: list):

    try:

        answer = generation_service.generate(question=question, contexts=contexts)

        return answer

    except Exception as exc:

        logger.error(f"Generation failed: {exc}")
        raise self.retry(exc=exc)     


# FULL EVALUATION REPORT
@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def evaluation_report(
    self,
    question: str,
    answer: str,
    contexts: list,
    ground_truth: str,
    original_query: str = None,
    rewritten_query: str = None):

    try:

        report = (
            evaluation_service.generate_evaluation_report(
                    question=question,
                    answer=answer,
                    contexts=contexts,
                    ground_truth=ground_truth,
                    original_query=original_query,
                    rewritten_query=rewritten_query))

        return report

    except Exception as exc:

        logger.error(f"Evaluation failed: {exc}")
        raise self.retry(exc=exc)


# HEALTH CHECK
@celery_app.task
def system_health():

    return {
        "query_rewrite":
            rewrite_service.health_check(),

        "retrieval":
            retrieval_service.health_check(),

        "generation":
            generation_service.health_check(),

        "evaluation":
            evaluation_service.health_check()}


# METRICS
@celery_app.task
def aggregate_metrics():

    return {

        "query_rewrite": {
            "health":
                rewrite_service.health_check()
        },

        "retrieval": {
            "stats":
                retrieval_service.get_retrieval_stats(),

            "health":
                retrieval_service.health_check()
        },

        "generation": {
            "health":
                generation_service.health_check()
        },

        "evaluation": {
            "stats":
                evaluation_service.get_evaluation_stats(),

            "health":
                evaluation_service.health_check()}}



# CLEANUP
@celery_app.task
def clean_up_cache():

    logger.info("Cleanup task executed")
    return {"status": "success"}