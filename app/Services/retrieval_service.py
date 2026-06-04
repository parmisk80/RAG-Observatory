import chromadb
import ollama
import string
import time
import logging
from typing import Optional
from dataclasses import dataclass
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from config.config import settings


logger = logging.getLogger(__name__)


"""
Container object representing a retrieved document chunk.

This structure is used throughout the retrieval pipeline
to store chunk content together with retrieval metadata.

Attributes:
    id (str):
        Unique identifier of the chunk.

    text (str):
        Retrieved chunk content.

    score (float):
        Relevance score assigned during retrieval
        or reranking.

    source (str):
        Origin of the retrieval result
        (e.g. ChromaDB, BM25).

    metadata (dict):
        Additional document metadata associated
        with the chunk.
"""
@dataclass
class RetrievedChunk:
    id : str
    text : str
    score : float
    source : str
    metadata : dict

class RetrievalService:
    """
    Initialize the Retrieval Service.

    Loads all retrieval components required by the
    RAG pipeline including:

    - ChromaDB vector database
    - Cross Encoder reranker
    - BM25 sparse retriever

    The service also initializes internal statistics
    used for monitoring retrieval performance.
    """
    def __init__(self):
        self.embed_model = settings.OLLAMA_EMBED_MODEL
        self.rerank_model = settings.CROSS_ENCODER_MODEL
        self.collection_name = settings.CHROMA_COLLECTION
        self._corpus: list[str] = []
        self._bm25:   Optional[BM25Okapi] = None
        self._stats = {
            "total_retrievals":  0,
            "failed_retrievals": 0,
            "avg_latency_ms":    0.0,
            "avg_results_count": 0.0,
        }
        self._init_chromadb()
        self._init_cross_encoder()
        self._init_bm25()


    """
    Initialize and connect to ChromaDB.

    Creates a client connection and loads the target
    document collection used for vector similarity search.

    Raises:
        Exception:
            If the ChromaDB server is unavailable
            or collection initialization fails.
    """
    def _init_chromadb(self):
        try:
            self._chroma = chromadb.HttpClient(
                host = settings.CHROMA_HOST,
                port = settings.CHROMA_PORT,
            )
            self._collection = self._chroma.get_or_create_collection(
                name     = self.collection_name,
                metadata = {"hnsw:space": "cosine"},
            )
            logger.info({
                "stage":      "retrieval_init",
                "status":     "chromadb_connected",
                "collection": self.collection_name,
            })
        except Exception as exc:
            logger.error(f"ChromaDB init failed: {exc}")
            raise    


    """
    Load the Cross Encoder reranking model.

    The Cross Encoder is used after retrieval to
    improve ranking quality by evaluating the semantic
    relationship between the user query and candidate chunks.

    If loading fails, reranking is automatically disabled.
    """
    def _init_cross_encoder(self):
            
            try:
                self._cross_encoder = CrossEncoder(self.rerank_model)
                logger.info({
                    "stage":  "retrieval_init",
                    "status": "cross_encoder_loaded",
                    "model":  self.rerank_model,
            })
            except Exception as exc:
                logger.warning(f"Cross encoder init failed — reranking disabled: {exc}")
                self._cross_encoder = None


    """
    Build a BM25 sparse retrieval index.

    Documents are loaded from ChromaDB and tokenized
    to create a keyword-based search index.

    BM25 improves retrieval quality by complementing
    vector search with exact keyword matching.
    """
    def _init_bm25(self):
            try:
                results = self._collection.get(include=["documents"])
                docs    = results.get("documents", [])

                if docs:
                    self._corpus = docs
                    tokenized    = [self._tokenize(d) for d in docs]
                    self._bm25   = BM25Okapi(tokenized)
                    logger.info({
                        "stage":     "retrieval_init",
                        "status":    "bm25_indexed",
                        "doc_count": len(docs),
                    })
                else:
                    logger.warning("ChromaDB collection is empty — BM25 disabled")

            except Exception as exc:
                logger.warning(f"BM25 init failed: {exc}")
                self._bm25 = None

    """
    Normalize and tokenize text for BM25 indexing.

    Operations include:
    - Lowercasing
    - Punctuation removal
    - Whitespace tokenization

    Args:
        text (str):
            Input text.

    Returns:
        list[str]:
            List of normalized tokens.
    """
    def _tokenize(self, text: str) -> list[str]:
            text   = text.lower()
            text   = text.translate(str.maketrans("", "", string.punctuation))
            return text.split()       
        

    """
    Generate an embedding vector for a user query.

    The embedding is produced using an Ollama embedding model
    and is later used for vector similarity search
    inside ChromaDB.

    Args:
        query (str):
            User search query.

    Returns:
        list[float]:
            Dense vector representation of the query.
    """
    def _generate_query_embedding(self, query: str) -> list[float]:
            try:
                response = ollama.embeddings(
                    model  = self.embed_model,
                    prompt = query,
                )
                return response["embedding"]

            except Exception as exc:
                logger.error({
                    "stage":   "embedding",
                    "status":  "failed",
                    "message": str(exc),
                    "query":   query[:60],
                })
                raise


    """
    Perform dense vector retrieval using ChromaDB.

    The query embedding is compared against all stored
    document embeddings to retrieve the most semantically
    relevant chunks.

    Args:
        query_embedding (list[float]):
            Vector representation of the query.

        top_k (int):
            Number of results to retrieve.

    Returns:
        list[RetrievedChunk]:
            Retrieved chunks ranked by vector similarity.
    """
    def _search_chromadb(self,query_embedding: list[float] , top_k: int,) -> list[RetrievedChunk]:

            results = self._collection.query(
                query_embeddings = [query_embedding],
                n_results        = top_k,
                include          = ["documents", "metadatas", "distances"],
            )

            chunks = []
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ids       = results.get("ids",       [[]])[0]

            for doc, meta, dist, doc_id in zip(documents, metadatas, distances, ids):
                score = max(0.0, 1 - dist)
                chunks.append(RetrievedChunk(
                    id       = doc_id,
                    text     = doc,
                    score    = round(score, 4),
                    source   = meta.get("source", "unknown"),
                    metadata = meta,
                ))

            return chunks   


    """
    Perform sparse keyword-based retrieval using BM25.

    This method complements vector retrieval by identifying
    documents that contain exact keyword matches.

    Args:
        query (str):
            User search query.

        top_k (int):
            Number of results to retrieve.

    Returns:
        list[RetrievedChunk]:
            BM25-ranked retrieval results.
    """
    def _bm25_search(
        self,
        query: str,
        top_k: int,
    ) -> list[RetrievedChunk]:

            if self._bm25 is None or not self._corpus:
                return []

            tokenized_query = self._tokenize(query)
            scores          = self._bm25.get_scores(tokenized_query)

            top_indices = sorted(
                range(len(scores)),
                key     = lambda i: scores[i],
                reverse = True,
            )[:top_k]

            chunks = []
            for idx in top_indices:
                if scores[idx] > 0:
                    chunks.append(RetrievedChunk(
                        id       = f"bm25_{idx}",
                        text     = self._corpus[idx],
                        score    = round(float(scores[idx]), 4),
                        source   = "bm25",
                        metadata = {"bm25_index": idx},
                    ))

            return chunks


    """
    Rebuild the BM25 index from the latest ChromaDB documents.

    This method should be executed whenever new documents
    are ingested into the vector database to ensure that
    the BM25 index remains synchronized.

    Returns:
        None
    """        
    def reload_bm25(self) -> None:
         

        results = self._collection.get(
            include=["documents"]
        )

        docs = results.get("documents", [])

        if not docs:
            self._bm25 = None
            self._corpus = []
            return

        self._corpus = docs

        tokenized_docs = [
            self._tokenize(doc)
            for doc in docs
        ]

        self._bm25 = BM25Okapi(tokenized_docs)

        logger.info({
            "stage": "bm25_reload",
            "status": "success",
            "documents": len(docs),
        })

    """
    Combine dense and sparse retrieval results.

    Hybrid retrieval merges:
    - ChromaDB vector search
    - BM25 keyword search

    Results are fused using Reciprocal Rank Fusion (RRF)
    to improve overall retrieval recall and robustness.

    Args:
        query (str):
            Original user query.

        query_embedding (list[float]):
            Query embedding vector.

        top_k (int):
            Number of final results.

    Returns:
        list[RetrievedChunk]:
            Hybrid-ranked candidate chunks.
    """
    def hybrid_search(
        self,
        query:           str,
        query_embedding: list[float],
        top_k:           int,
        dense_weight: float = settings.DENSE_WEIGHT ,
        sparse_weight: float = settings.SPARSE_WEIGHT ,
        candidate_k:     int   = 20
    ) -> list[RetrievedChunk]:
            

            dense_results  = self._search_chromadb(query_embedding, candidate_k)
            sparse_results = self._bm25_search(query, candidate_k)

            scores: dict[str, float] = {}

            for rank, chunk in enumerate(dense_results):
                rrf_score = 1 / (60 + rank + 1)
                scores[chunk.text] = scores.get(chunk.text, 0) + dense_weight * rrf_score

            for rank, chunk in enumerate(sparse_results):
                rrf_score = 1 / (60 + rank + 1)
                scores[chunk.text] = scores.get(chunk.text, 0) + sparse_weight * rrf_score


            all_chunks: dict[str, RetrievedChunk] = {}
            for chunk in dense_results + sparse_results:
                if chunk.text not in all_chunks:
                    all_chunks[chunk.text] = chunk

            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

            return [
                RetrievedChunk(
                    id       = all_chunks[text].id,
                    text     = text,
                    score    = round(score, 4),
                    source   = all_chunks[text].source,
                    metadata = all_chunks[text].metadata,
                )
                for text, score in ranked
                if text in all_chunks
            ]
        
    """
    Rerank retrieved chunks using a Cross Encoder model.

    The Cross Encoder evaluates each query-chunk pair
    directly and assigns a semantic relevance score.

    This stage improves ranking precision by selecting
    the most contextually relevant chunks.

    Args:
        query (str):
            User query.

        chunks (list[RetrievedChunk]):
            Candidate retrieval results.

        top_k (int):
            Number of final chunks to return.

    Returns:
        list[RetrievedChunk]:
            Reranked retrieval results.
    """
    def _rerank_with_cross_encoder(
        self,
        query:   str,
        chunks:  list[RetrievedChunk],
        top_k:   int,
    ) -> list[RetrievedChunk]:

            if self._cross_encoder is None or not chunks:
                return chunks[:top_k] 
            
            pairs  = [(query, chunk.text) for chunk in chunks]
            scores = self._cross_encoder.predict(pairs)

            reranked = sorted(
            zip(chunks, scores),
            key     = lambda x: x[1],
            reverse = True,)[:top_k]

            return [
            
                RetrievedChunk(
                    id = chunk.id,
                    text = chunk.text,
                    score = round(float(score), 4),
                    source = chunk.source,
                    metadata = chunk.metadata,
                    )
                    for chunk, score in reranked
                ]
        


    """
    Convert RetrievedChunk objects into serializable dictionaries.

    This method prepares retrieval results for API responses
    and downstream services.

    Args:
        chunks (list[RetrievedChunk]):
            Retrieved chunks.

    Returns:
        list[dict]:
            Serialized retrieval results.
    """
    def _format_results(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[dict]:

            return [
                {
                    "id":       chunk.id,
                    "text":     chunk.text,
                    "score":    chunk.score,
                    "source":   chunk.source,
                    "metadata": chunk.metadata,
                }
                for chunk in chunks
            ]
        

    """
    Retrieve the most relevant context for a user query.

    Retrieval Pipeline:

        Query
        ↓
        Query Embedding
        ↓
        Dense Retrieval (ChromaDB)
        ↓
        Sparse Retrieval (BM25)
        ↓
        Hybrid Fusion (RRF)
        ↓
        Cross Encoder Reranking
        ↓
        Top-K Context Chunks

    Args:
        query (str):
            User search query.

        top_k (int):
            Number of final chunks returned.

    Returns:
        list[dict]:
            Ranked context chunks with scores
            and metadata.
    """
    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        
            start = time.time()

            try:
                query_embedding = self._generate_query_embedding(query)

               
                chunks = self.hybrid_search(
                    query           = query,
                    query_embedding = query_embedding,
                    top_k           = top_k * 4,  
                )

               
                chunks = self._rerank_with_cross_encoder(query, chunks, top_k)

                
                results = self._format_results(chunks)

                latency = (time.time() - start) * 1000
                self._update_stats(success=True, latency=latency, result_count=len(results))

                logger.info({
                    "stage":        "retrieval",
                    "status":       "success",
                    "latency_ms":   round(latency, 2),
                    "query":        query[:60],
                    "results_count": len(results),
                    "top_score":    results[0]["score"] if results else 0,
                })

                return results

            except Exception as exc:
                latency = (time.time() - start) * 1000
                self._update_stats(success=False, latency=latency, result_count=0)

                logger.error({
                    "stage":   "retrieval",
                    "status":  "failed",
                    "message": str(exc),
                    "query":   query[:60],
                })
                return []
            

        
    """
    Perform health checks for all retrieval dependencies.

    Verifies:
    - ChromaDB connectivity
    - Ollama embedding model availability
    - BM25 index status
    - Cross Encoder status

    Returns:
        dict:
            Health information for all retrieval
            components and overall service status.
    """
    def health_check(self) -> dict:
            results = {}

            try:
                self._chroma.heartbeat()
                results["chromadb"] = "healthy"
            except Exception as exc:
                results["chromadb"] = f"unhealthy: {exc}"

            
            try:
                ollama.embeddings(model=self.embed_model, prompt="test")
                results["ollama_embed"] = "healthy"
            except Exception as exc:
                results["ollama_embed"] = f"unhealthy: {exc}"

            
            results["bm25"]         = "active" if self._bm25 else "disabled"
            results["cross_encoder"] = "active" if self._cross_encoder else "disabled"

            overall         = "healthy" if all("unhealthy" not in str(v) for v in results.values()) else "degraded"
            results["overall"] = overall

            return results
        


    """
    Return retrieval performance statistics.

    Metrics include:
    - Total retrieval requests
    - Failed retrievals
    - Success rate
    - Average latency
    - Average result count

    Returns:
        dict:
            Aggregated retrieval service metrics.
    """
    def get_retrieval_stats(self) -> dict:
            total   = self._stats["total_retrievals"]
            failed  = self._stats["failed_retrievals"]
            success = total - failed

            return {
                "total_retrievals":   total,
                "failed_retrievals":  failed,
                "success_rate":       round(success / max(total, 1) * 100, 2),
                "avg_latency_ms":     round(self._stats["avg_latency_ms"], 2),
                "avg_results_count":  round(self._stats["avg_results_count"], 2),
                "bm25_active":        self._bm25 is not None,
                "cross_encoder_active": self._cross_encoder is not None,
            }
        

    """
    Update internal retrieval performance metrics.

    This method maintains running averages for:
    - Retrieval latency
    - Number of returned results
    - Failure rate

    Args:
        success (bool):
            Whether the retrieval operation succeeded.

        latency (float):
            Request latency in milliseconds.

        result_count (int):
            Number of retrieved chunks.

    Returns:
        None
    """
    def _update_stats(self, success: bool, latency: float, result_count: int):
            n = self._stats["total_retrievals"]
            self._stats["total_retrievals"] += 1

            self._stats["avg_latency_ms"] = (
                (self._stats["avg_latency_ms"] * n + latency) / (n + 1)
            )
            self._stats["avg_results_count"] = (
                (self._stats["avg_results_count"] * n + result_count) / (n + 1)
            )
            if not success:
                self._stats["failed_retrievals"] += 1