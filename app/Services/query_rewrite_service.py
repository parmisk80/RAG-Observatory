import logging
import ollama # call local models (with ollama API)
import time # measuring latancy
from typing import Optional
from config.config import settings


logger = logging.getLogger(__name__)



"""
Query rewriting service based on local Ollama models.

This service improves user questions before retrieval by
rewriting ambiguous or verbose queries into concise,
retrieval-friendly search queries.

Responsibilities:
- Query rewriting
- Rewrite validation
- Fallback handling
- Rewrite metrics collection
- Service health monitoring
"""
class QueryRewriteService:

        """
        Initialize Query Rewrite Service.

        Loads:
        - Ollama model configuration
        - Ollama endpoint
        - Internal rewrite metrics

        The service keeps lightweight runtime statistics
        for monitoring and observability.
        """
        def __init__(self):
            self.model_name = settings.OLLAMA_EMBED_MODEL
            self.base_url =  settings.OLLAMA_BASE_URL
            self._stats = {
                  
                  "total_rewrites" : 0 , # counter of rewrites
                  "failed_rewrites" : 0 , # counter of failed rewrites
                  "fallback_used" : 0 , # counter of ollama's wrong responses
                  "avg_latancy_ms" : 0.0 , # Ollama Avg responding -> ms
                  
            } # private Variabls



        """
        Build a rewrite prompt for the language model.

        Args:
            query:
                Original user query.

        Returns:
            Prompt instructing the model to rewrite the query
            for retrieval optimization.
        """
        def _build_prompt(self, query : str) -> str :
              
              return (
            "You are a search query optimizer.\n"
            "Rewrite the user query to be shorter, keyword-focused, "
            "and better suited for document retrieval.\n"
            "Rules:\n"
            "- Keep important entities and keywords\n"
            "- Remove unnecessary words\n"
            "- Do NOT change the meaning\n"
            "- Output ONLY the rewritten query, nothing else\n\n"
            f"Original query: {query}\n"
            "Rewritten query:"
        )


        """
        Rewrite a user query using an Ollama model.

        Workflow:
            Query
            ↓
            Prompt
            ↓
            Ollama
            ↓
            validation
            ↓
            Fallback (if needed)

        Args:
            query:
                Original user query.

        Returns:
            Rewritten query suitable for vector retrieval.
        """
        def rewrite_query(self, query : str) -> str :
              
              start = time.time()
            
              try :
                    
                prompt = self._build_prompt(query)
                response = ollama.generate(model= self.model_name, prompt= prompt , options= {"temperature": 0.3, "num_predict": 50})

                rewrite = response["response"].strip()

                if not self.validate_rewrite(query , rewrite) :
                     logger.warning(f"Invalid rewrite for query : '{query}' - using fallback ")
                     rewrite = self.fallback_query(query)
                     self._stats["fallback_used"] += 1

                latency_ms = (time.time() - start) * 1000 # * 1000 -> ms
                self._update_stats(success=True, latency=latency_ms)

                logger.info({
                "stage":      "query_rewrite",
                "status":     "success",
                "latency_ms": round(latency_ms, 2),
                "original":   query[:60],
                "rewrite":    rewrite[:60],
            })
                

                return rewrite
              
              except Exception as exc:
                   
                latency_ms = (time.time() - start) * 1000
                self._update_stats(success=False, latency=latency_ms)


              logger.error({
                "stage":   "query_rewrite",
                "status":  "error",
                "message": str(exc),
                "query":   query[:60],
            })

              return self.fallback_query(query)


        """
        Validate the generated rewrite.

        Checks:
        - Non-empty output
        - Reasonable length
        - No prompt leakage
        - Semantic plausibility

        Args:
            original:
                Original query.

            rewrite:
                Generated query.

        Returns:
            True if rewrite is accepted,
            otherwise False.
        """
        def validate_rewrite(self, original : str , rewrite : str ) -> bool :
             
             if not rewrite or not rewrite.strip():
                  return False
             
             if len(rewrite.split()) > len(original.split()) * 2:
                  return False
             
             if "rewrite query" in rewrite.lower() :
                  return False

             if rewrite.strip() == original.strip():
                  return False

             return True


        """
        Generate a safe fallback query.

        This method removes common stopwords and keeps
        the most informative keywords from the original query.

        Args:
            query:
                Original user query.

        Returns:
            Simplified retrieval-friendly query.
        """
        def fallback_query(self, query : str) :

             """
             Lazy import
             """
             import re 
             import string


             stopwords = {
                  "a", "an", "the", "is", "are", "was", "were",
                  "what", "who", "where", "when", "how", "why",
                  "do", "does", "did", "in", "on", "at", "to",
                  "of", "for", "and", "or", "but"
                  }            


             text = query.lower().translate(str.maketrans("", "", string.punctuation))
             tokens = [w for w in text.split() if w not in stopwords and len(w) > 2]

             result = " ".join(tokens[:8]) if tokens else query
             logger.info(f"Fallback query used: '{result}'")
             return result
        

        """
        Rewrite multiple queries in sequence.

        Useful for:
        - Evaluation pipelines
        - Benchmark datasets
        - Batch retrieval experiments

        Args:
            queries:
                List of user queries.

        Returns:
            List of rewritten queries.
        """
        def rewrite_batch(self, queries : list[str]) -> list[str] :
             
             result = []
             for query in queries :
                  result.append(self.rewrite_query(query))
             
             return result
        


        """
        Verify service availability.

        Performs a lightweight Ollama request to ensure
        the rewrite model is reachable and operational.

        Returns:
            Service health information.
        """
        def health_check(self) -> dict:

            try:
                response = ollama.generate( model = self.model_name , prompt  = "ping", options = {"num_predict": 1})
                
                return {"status": "healthy", "model": self.model_name}

            except Exception as exc:
            
                logger.error(f"Ollama health check failed: {exc}")
                return {"service" : "query_rewriter", 
                        "status": "unhealthy", 
                        "model": self.model_name, 
                        "error": str(exc),
                        "ollama_url" : self.base_url}


        """
        Return runtime rewrite statistics.

        Metrics:
        - Total rewrites
        - Failed rewrites
        - Fallback usage
        - Average latency
        - Success rate

        Returns:
            Dictionary containing rewrite metrics.
        """
        def get_rewrite_stats(self) -> dict:
             

            return {
                "total_rewrites":  self._stats["total_rewrites"],
                "failed_rewrites": self._stats["failed_rewrites"],
                "fallback_used":   self._stats["fallback_used"],
                "avg_latency_ms":  round(self._stats["avg_latency_ms"], 2),
                "success_rate":    self._calc_success_rate()
                }
        

        """
        Update internal rewrite metrics.

        Args:
            success:
                Indicates whether rewrite succeeded.

            latency:
                Request latency in milliseconds.
        """

        def _update_stats(self, success: bool, latency: float):
            n = self._stats["total_rewrites"]

            self._stats["total_rewrites"] += 1

            # correct rolling average
            self._stats["avg_latency_ms"] = (
                (self._stats["avg_latency_ms"] * n + latency)
                / (n + 1)
            )

            if not success:
                self._stats["failed_rewrites"] += 1



        """
        Calculate rewrite success rate.

         Returns:
           Success percentage between 0 and 100.
        """
        def _calc_success_rate(self) -> float:
             
            total = self._stats["total_rewrites"]
            if total == 0:
                return 0.0
            
            failed = self._stats["failed_rewrites"]

            return round((total - failed) / total * 100, 2)
