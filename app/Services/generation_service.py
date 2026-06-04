import ollama
import logging
import time
from typing import Optional
from config.config import settings


logger = logging.getLogger(__name__)


"""
Service responsible for generating final answers
using retrieved context chunks and a local LLM.

This service receives:

- User question
- Retrieved context chunks

and produces:

- Grounded answer
- Generation metadata
- Monitoring statistics

The generation stage represents the final
step of the RAG pipeline.
"""
class GenerationService:
    """
    Initialize the Generation Service.

    Loads generation model configuration,
    runtime parameters, and internal monitoring
    metrics used for performance tracking.
    """
    def __init__(self):
        self.model = settings.OLLAMA_GENERATION_MODEL
        self.base_url = settings.OLLAMA_BASE_URL
        self.max_tokens = settings.GENERATION_MAX_TOKEN
        self.temperature = settings.GENERATION_TEMPERATURE
        self._stats = {
            "total_generations" : 0,
            "failed_generations" : 0,
            "empty_context" : 0,
            "avg_latency" :0.0
        }

    """
    Convert retrieved chunks into a formatted context block.

    Each retrieved chunk is transformed into a structured
    text representation containing:

    - Chunk identifier
    - Source information
    - Retrieval score
    - Chunk content

    This formatted context is later injected into
    the LLM prompt.

    Args:
        contexts (list[dict]):
            Retrieved context chunks.

    Returns:
        str:
            Formatted context string.
    """
    def _format_context(self, contexts: list[dict]) -> str:

        if not contexts:
            return ""

        formatted_chunks = []

        for i, chunk in enumerate(contexts, start=1):
            text   = chunk.get("text",   "").strip()
            source = chunk.get("source", "unknown")
            score  = chunk.get("score",  0.0)

            formatted_chunks.append(f"[Chunk {i}] (source: {source} | score: {score})\n{text}")

        return "\n\n".join(formatted_chunks)  

    """
    Construct the final RAG prompt.

    The generated prompt contains:

    - System instructions
    - Retrieved context
    - User question

    The prompt explicitly restricts the model
    to answering only from the provided context.

    Args:
        question (str):
            User question.

        formatted_context (str):
            Retrieved context formatted as text.

    Returns:
        str:
            Final prompt sent to the LLM.
    """
    def _build_prompt(
        self,
        question:          str,
        formatted_context: str,
    ) -> str:
        return (
            "You are a precise question-answering assistant.\n"
            "Answer the question using ONLY the information provided in the context below.\n"
            "If the context does not contain enough information, say: "
            "'I cannot find sufficient information to answer this question.'\n"
            "Do NOT make up facts. Do NOT use outside knowledge.\n\n"

            "\n"
            "CONTEXT:\n"
            "\n"
            f"{formatted_context}\n\n"

            "\n"
            "QUESTION:\n"
            "\n"
            f"{question}\n\n"

            "\n"
            "ANSWER:\n"
            "\n"
        )  
    
    """
    Generate an answer using the configured LLM.

    The method sends the prepared prompt
    to the Ollama model and returns
    the generated response.

    Args:
        prompt (str):
            Fully constructed prompt.

    Returns:
        str:
            Generated answer.
    """
    def _generate_answer(self, prompt: str) -> str:

        response = ollama.chat(
            model    = self.model,
            messages = [
                {
                    "role":    "user",
                    "content": prompt,
                }
            ],
            options  = {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
                "top_p":       0.9,
            },
        )

        return response["message"]["content"].strip()
    

    """
    Generate a grounded answer from retrieved context.

    Pipeline:

        Question
            ↓
        Retrieved Context
            ↓
        Context Formatting
            ↓
        Prompt Construction
            ↓
        Ollama Generation
            ↓
        Final Answer

    If no context is available,
    generation is skipped and a fallback
    response is returned.

    Args:
        question (str):
            User question.

        contexts (list[dict]):
            Retrieved context chunks.

    Returns:
        dict:
            Generated answer together with
            generation metadata.
    """
    def generate(self, question: str , contexts: list[dict]) -> dict:
        
        start = time.time()

        if not contexts:
            self._stats["empty_context"] += 1
            logger.warning({
                "stage":   "generation",
                "status":  "no_context",
                "message": "Empty context — generation blocked",
                "question": question[:60],
            })
            return {
                "answer":   "No relevant information found.",
                "question": question,
                "metadata": {
                    "status":        "no_context",
                    "model":         self.model,
                    "chunks_used":   0,
                    "latency_ms":    0.0,
                },
            }
        
        try:
            # format context 
            formatted_context = self._format_context(contexts)

            # build prompt 
            prompt = self._build_prompt(question, formatted_context)

            # LLM call
            answer = self._generate_answer(prompt)

            # metadata
            latency = (time.time() - start) * 1000
            self._update_stats(success=True, latency=latency)

            logger.info({
                "stage":       "generation",
                "status":      "success",
                "latency_ms":  round(latency, 2),
                "question":    question[:60],
                "answer":      answer[:80],
                "chunks_used": len(contexts),
            })

            return {
                "answer":   answer,
                "question": question,
                "metadata": {
                    "status":        "success",
                    "model":         self.model,
                    "chunks_used":   len(contexts),
                    "latency_ms":    round(latency, 2),
                    "temperature":   self.temperature,
                    "top_sources":   [
                        c.get("source", "unknown")
                        for c in contexts[:3]
                    ],
                },
            }
        

        except Exception as exc:
            latency = (time.time() - start) * 1000
            self._update_stats(success=False, latency=latency)

            logger.error({
                "stage":   "generation",
                "status":  "failed",
                "message": str(exc),
                "question": question[:60],
            })

            return {
                "answer":   "An error occurred during generation.",
                "question": question,
                "metadata": {
                    "status":      "error",
                    "model":       self.model,
                    "chunks_used": len(contexts),
                    "latency_ms":  round(latency, 2),
                    "error":       str(exc),
                },
            }
        
    """
    Perform health checks for generation dependencies.

    Verifies:

    - Ollama connectivity
    - Model availability
    - Inference readiness

    Returns:
        dict:
            Health status information for
            the generation service.
    """   
    def health_check(self) -> dict:
        results = {}

        try:
            ollama.chat(
                model    = self.model,
                messages = [{"role": "user", "content": "ping"}],
                options  = {"num_predict": 1},
            )
            results["ollama"]         = "healthy"
            results["model"]          = self.model
            results["model_status"]   = "loaded"

        except Exception as exc:
            results["ollama"]       = f"unhealthy: {exc}"
            results["model_status"] = "unavailable"

        overall          = "healthy" if "unhealthy" not in str(results.get("ollama", "")) else "unhealthy"
        results["overall"] = overall

        return results
    

    """
    Return generation service statistics.

    Metrics include:

    - Total generations
    - Failed generations
    - Empty context events
    - Average latency
    - Success rate

    Returns:
        dict:
            Aggregated generation metrics.
    """
    def get_generation_stats(self) -> dict:
        total   = self._stats["total_generations"]
        failed  = self._stats["failed_generations"]
        success = total - failed

        return {
            "total_generations":  total,
            "failed_generations": failed,
            "empty_context_hits": self._stats["empty_context"],
            "success_rate":       round(success / max(total, 1) * 100, 2),
            "avg_latency_ms":     round(self._stats["avg_latency_ms"], 2),
            "model":              self.model,
        }
    
    """
    Update internal generation metrics.

    Maintains running averages and counters
    for generation requests.

    Args:
        success (bool):
            Whether generation succeeded.

        latency (float):
            Generation latency in milliseconds.

    Returns:
        None
    """
    def _update_stats(self, success: bool, latency: float):
        n = self._stats["total_generations"]
        self._stats["total_generations"] += 1
        self._stats["avg_latency_ms"] = (
            (self._stats["avg_latency_ms"] * n + latency) / (n + 1)
        )
        if not success:
            self._stats["failed_generations"] += 1