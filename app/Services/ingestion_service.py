import fitz  #PyMuPDF # reading PDF.
import chromadb # database for store vectors. (embedding)
import ollama # use Ollama API. (generate embedding with local models)
import unicodedata # normalize special characters.
import re # text pattern.
import redis
import logging 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.config import settings


logger = logging.getLogger(__name__)

# connection to servers
redis_client = redis.Redis.from_url(settings.CELERY_BACKEND_URL , decode_responses=True)
chroma_client = chromadb.HttpClient(host = settings.CHROMA_HOST, port = settings.CHROMA_PORT )


def document_ingestion(document_id : str , file_path : str) -> dict :

    logger.info(f"Starting pipeline for documnet : {document_id}")


    logger.info("Parsing PDF")
    raw_text = _parse_pdf(file_path)

    logger.info("Cleaning text")
    clean_text = _clean_text(raw_text)

    logger.info("Chunking text")
    chunk = _chunk_text(clean_text)

    logger.info("Generating embeddings")
    embeddings = _generate_embeddings(chunk)


    logger.info("Storing vectors")
    _store_in_chromadb(document_id = document_id , chunk = chunk , embeddings = embeddings)

    logger.info(f"document {document_id} processed successfully.")
    return {"status": "completed", "document_id": document_id, "chunks": len(chunk)}





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
      doc = fitz.open(file_path)
      full_text = ""
      for page_num , page in enumerate(doc):
            text = page.get_text() 
            full_text += f"\n[Page {page_num + 1}]\n{text}" 
      doc.close()
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
def _clean_text(text : str) -> str:
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
      collection.add(
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))] ,
            documents = chunks , 
            embeddings = embeddings , 
            metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
      )
      


"""
Check connectivity to external services used by
the ingestion pipeline.

Verifies:
- Ollama availability
- ChromaDB availability

Returns:
    dict:
        Health status information.
"""
def health_check() -> dict:

    try:

        chroma_client.heartbeat()

        ollama.generate(
            model=settings.OLLAMA_LLM_MODEL,
            prompt="ping",
            options={"num_predict": 1}
        )

        return {"service": "ingestion", "status": "healthy"}

    except Exception as exc:

        logger.error(f"Ingestion health check failed: {exc}")

        return {"service": "ingestion", "status": "unhealthy", "error": str(exc)}      