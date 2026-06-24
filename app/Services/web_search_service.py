from duckduckgo_search import DDGS
import logging 

logger = logging.getLogger(__name__)

class WebSearchService:

    def __init__(self , max_results : int = 5):
        self.max_results = max_results

    def search(self , query : str) -> list[dict] :
        try : 
            with DDGS() as ddgs:
                results = list(ddgs.text(query , max_results=self.max_results))


            return [
                {
                    "id" : f"web_{i}" , 
                    "text" : r.get("body" , "") , 
                    "source" : r.get("href" , "") , 
                    "metadata" : {"title" : r.get("title" , "") , "type" : "web"}
                }

                for i , r in enumerate(results)

            ]    
        
        except Exception as exc :
            logger.error(f"Web search failed : {exc}")
            return []
        

    def health_check(self) -> dict :
        try :
            with DDGS() as ddgs :
                list(ddgs.text("text" , max_results=1))
            return {"service" : "web_search" , "status" : "healthy"}
        except Exception as exc:
            return {'serivce' : "Web_search" , "status" : "unhealthy" , "error" : str(exc)}        