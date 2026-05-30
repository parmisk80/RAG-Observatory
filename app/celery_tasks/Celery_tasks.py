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
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset


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

# TASK 1 -> DOCUMENT INGESTION
@celery_app.task(bind = True , max_retries = 3 , default_retry_delay = 60)
def process_document(self , document_id : str , file_path : str):

        try:
                
            logger.info(f"Starting pipeline for documnet : {document_id}")

            # STEP 1 -> Pars PDF
            logger.info("Parsing PDF process...")
            raw_text = _parse_pdf(file_path)
            logger.info(f"Extracted {len(raw_text)} characters from PDF")
            

            # STEP 2 -> Clean Text
            logger.info("Cleaning Text...")
            clean_text = _cleaning_text(raw_text)


            # STEP 3 -> Chunk Text
            logger.info("Chunking Text...")
            chunk = _chunk_text(clean_text)
            logger.info(f"Created {len(chunk)} chunks")


            # STEP 4 -> Generate Embeddings
            logger.info("Generating embeddings via Ollama...")
            embeddings = _generate_embeddings(chunk)


            # STEP 5 -> Store in Chromadb
            logger.info("Storing vectors in Chromadb...")
            _store_in_chromadb(document_id , chunk , embeddings)

            logger.info(f"document {document_id} processed successfully.")
            return {"status": "completed", "document_id": document_id, "chunks": len(chunk)}
        

        except fitz.FileDataError as exc:
              logger.error(f"PDF parse error {document_id} : {exc} ")
              raise self.retry(exc = exc)
        except ChromaError as exc:
              logger.error(f"Chromadb error for {document_id} : {exc}")
              raise self.retry(exc=exc)
        except Exception as exc:
              logger.error(f"Unexpected error for {document_id}: {exc}")    
              raise self.retry(exc=exc)          
        

"""
Extract textual content from a PDF document using PyMuPDF.

Each page is processed individually and appended
to the final aggregated text output.

The extracted text preserves page ordering and inserts
page markers to improve downstream chunk traceability.

Args:
    file_path (str):
        Path to the target PDF document.

Returns:
    str:
        Full extracted document text.
"""
def _parse_pdf(file_path : str) -> str :
    with fitz.open(file_path) as doc:
        full_text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            full_text += f"\n[Page {page_num + 1}]\n{text}"

    return full_text    


"""
Normalize and clean raw extracted text.

Cleaning operations include:
- Unicode normalization
- Removing invalid control characters
- Reducing excessive newlines
- Removing duplicated whitespace

The goal of this stage is to prepare cleaner
input for chunking and embedding generation.

Args:
    text (str):
        Raw extracted text from the PDF document.

Returns:
    str:
        Cleaned and normalized text.
"""
def _cleaning_text(text : str) -> str:
      text = unicodedata.normalize("NFKC" , text)

      text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
      text = re.sub(r'\n{3,}', '\n\n', text)
      text = re.sub(r' {2,}', ' ', text)

      return text.strip()


"""
Split cleaned text into smaller semantic-aware chunks.

Chunking improves:
- Retrieval quality
- Embedding consistency
- Context precision
- LLM context injection

The RecursiveCharacterTextSplitter attempts to preserve
semantic boundaries while respecting chunk size limits.

Args:
    text (str):
        Cleaned document text.

Returns:
    list[str]:
        List of generated text chunks.
"""
def _chunk_text(text : str) -> list[str] :
      splitter = RecursiveCharacterTextSplitter(
            chunk_size = 500 ,  
            chunk_overlap = 50 , 
            separators=["\n\n", "\n", ".", " "])
      
      return splitter.split_text(text)


"""
Generate vector embeddings for document chunks using Ollama.

Each chunk is converted into a dense vector representation
that can later be used for semantic similarity search
inside the vector database.

Args:
    chunks (list[str]):
        List of text chunks generated during chunking.

Returns:
    list[list[float]]:
        List of embedding vectors corresponding
        to each text chunk.
"""
def _generate_embeddings(chunks : list[str]) -> list[list[float]]: # every chunk is a list of float numbers.
      embeddings = []
      for chunk in chunks:
            response = ollama.embeddings(model = settings.OLLAMA_EMBED_MODEL , prompt = chunk)

            embeddings.append(response['embedding'])

      return embeddings     


"""
Store document chunks and embeddings inside ChromaDB.

Each chunk is stored together with:
- unique chunk identifier
- embedding vector
- metadata information

Metadata allows traceability between chunks
and their original source document.

Args:
    document_id (str):
        Unique identifier for the source document.
    chunks (list[str]):
        List of generated text chunks.
    embeddings (list[list[float]]):
        Vector embeddings associated with each chunk.
Returns:
    None
"""
def _store_in_chromadb(document_id : str , chunks : list[str] , embeddings : list[list[float]]):
      
      collection = chroma_client.get_or_create_collection(name = "documents")
      embeddings = np.array(embeddings, dtype=np.float32)
      collection.add(
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))] ,
            documents = chunks , 
            embeddings = embeddings , 
            metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
      )




"""
Evaluate generated RAG responses using RAGAS metrics.

This task measures the quality of generated answers
based on retrieval context and expected ground truth.

Evaluation metrics include:
- Faithfulness
- Answer Relevancy
- Context Precision

Args:
    question (str):
        Original user query.

    answer (str):
        Generated answer from the RAG pipeline.

    context (list[str]):
        Retrieved context chunks used during generation.

    ground_truth (str):
        Expected reference answer.

Returns:
    dict:
        Dictionary containing evaluation metric scores.

Raises:
    Retry:
        Retries task automatically on evaluation failures.
"""
# TASK 2 -> RAG EVALUATION
@celery_app.task(bind = True , max_retries = 2 , default_retry_delay = 30)
def evaluate_rag(self , question : str , answer : str , context : list[str] , ground_truth : str):
    
    try:
              
        logger.info(f"Startinh RAG evaluation for question: {question[:50]} ...")

        data = {
                "question" : [question] , 
                "answer" : [answer] ,
                "contexts" : [context] , 
                "ground_truth" : [ground_truth]
              }

        dataset = Dataset.from_dict(data) # RAG is just working with datasets (not dict)

        results = evaluate(dataset = dataset , metrics = [faithfulness , answer_relevancy , context_precision])

        evaluation_result = {
                "faithfulness" : round(float(results['faithfulness']) , 4) , 
                "answer_relevancy" : round(float(results['answer_relevancy']),4) , 
                "context_precision" : round(float(results['context_precision']) , 4)
              }
              

        logger.info(f"Evaluation completed: {evaluation_result}")
        return evaluation_result

    except Exception as exc :
            logger.error(f"Evaluation error: {exc}")
            raise self.retry(exc=exc)


"""
Remove expired or orphan Redis cache entries.

This maintenance task helps:
- reduce memory usage
- remove stale cache keys
- maintain cache consistency

The task scans cache namespaces associated
with the RAG pipeline and removes invalid entries.

Returns:
    dict:
        Cleanup summary containing deleted key count.

Raises:
    Retry:
        Retries task automatically on Redis failures.
"""
# TASK 3 — CACHE CLEANUP
@celery_app.task(bind = True , max_retries = 2)
def clean_up_cache(self):

    try:
        logger.info("Starting cache cleanup...")
        deleted_count = 0

        keys = redis_client.keys("rag:cache:*")

        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl == -1:
                redis_client.delete(key)
                deleted_count += 1
                logger.debug(f"Deleted orphan key: {key}")

        logger.info(f"Cache cleanup completed. Deleted {deleted_count} keys.")
        return {"status": "cache cleaned", "deleted_keys": deleted_count}

    except redis.RedisError as exc:
        logger.error(f"Redis error during cleanup: {exc}")
        raise self.retry(exc=exc)



"""
Aggregate system monitoring metrics for observability dashboards.

This task collects and summarizes:
- total requests
- failed requests
- average latency
- success rate

The aggregated metrics can later be visualized
inside Grafana dashboards.

Returns:
    dict:
        Aggregated system monitoring statistics.

Raises:
    Retry:
        Retries task automatically on Redis failures.
"""
# TASK 4 —> METRICS AGGREGATION
@celery_app.task(bind=True, max_retries=2)
def aggregate_metrics(self):
     
    try:
        logger.info("Aggregating system metrics...")

        total_requests = int(redis_client.get("metrics:total_requests") or 0)
        failed_requests = int(redis_client.get("metrics:failed_requests") or 0)

        
        latency_values = redis_client.lrange("metrics:latency_history", 0, -1)
        if latency_values:
            avg_latency = sum(float(v) for v in latency_values) / len(latency_values)
            avg_latency = round(avg_latency, 2)
        else:
            avg_latency = 0.0

        metrics = {
            "total_requests": total_requests,
            "failed_requests": failed_requests,
            "success_rate": round((total_requests - failed_requests) / max(total_requests, 1) * 100, 2),
            "average_latency_ms": avg_latency,
        }

        logger.info(f"Metrics aggregated: {metrics}")
        return metrics

    except redis.RedisError as exc:
        logger.error(f"Redis error during metrics aggregation: {exc}")
        raise self.retry(exc=exc)

