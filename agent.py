from crewai import Agent, Task, Crew
from graph import get_similar_recipes 
# from crewai_tools import BaseTool
from crewai_tools.tools.base_tool import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Type, Any
import json

# from crewai_tools import (
#   ScrapeWebsiteTool,
#   SerperDevTool
# )

import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_MODEL_NAME"] = os.getenv("OPENAI_MODEL_NAME")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['SERPER_API_KEY'] = os.getenv("SERPER_API_KEY")


class SimilarRecipesInput(BaseModel):
    """Arguments crew-agents must supply."""
    names: List[str] = Field(..., description="Recipe names to look up")


class SimilarRecipesTool(BaseTool):
    name: str = "similar_recipe_finder"
    description: str = (
        "Given one or more recipe names, return a list of the most "
        "ingredient-similar recipes for each input.")
    
    args_schema: Type[BaseModel] = SimilarRecipesInput      
    _conn: Any = PrivateAttr(default=None)     

    def __init__(self, conn, **tool_kwargs):
        super().__init__(**tool_kwargs)        
        self._conn = conn   
   
    def _run(self, names: List[str]) -> str:
        data = get_similar_recipes(self.conn, names)
        
        return json.dumps(data, indent=2)
