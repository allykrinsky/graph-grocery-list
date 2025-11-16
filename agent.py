import os
import json
from dotenv import load_dotenv

from crewai import Agent, Task, Crew
from graph import get_similar_recipes 
# from crewai_tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Type, Any
# from crewai_tools import (
#   ScrapeWebsiteTool,
#   SerperDevTool
# )

from crewai_tools import tool

load_dotenv()

os.environ["OPENAI_MODEL_NAME"] = os.getenv("OPENAI_MODEL_NAME")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['SERPER_API_KEY'] = os.getenv("SERPER_API_KEY")


@tool("sim_tool")
def sim_tool(db, names):
    """
    Given one or more recipe names, return a list of the most
    ingredient-similar recipes for each input.

    db: database connector object (defaults to db)
    names: List[str] containing names of recipes

    """
    return get_similar_recipes(db, names)

recommender = Agent(
    role       = "Recipe Recommender",
    goal       = "Create a weekly dinner menu using similar recipes so that the grocery bill and food waste is minimized, but there is diversity in the meals",
    backstory  = "You know everything about flavour pairings.",
    tools      = [sim_tool]
)

task = Task(
    description = "User likes Cherry Tomato Pasta and Steak + Baked Potato. Suggest 3 "
                  "similar recipes they should try this week.",
    expected_output = "A friendly bulleted list with reasons.",
    agent=recommender
)

crew = Crew(agents=[recommender], tasks=[task])
crew.kickoff()



# class SimilarRecipesInput(BaseModel):
#     """Arguments crew-agents must supply."""
#     names: List[str] = Field(..., description="Recipe names to look up")


# class SimilarRecipesTool(BaseTool):
#     name: str = "similar_recipe_finder"
#     description: str = (
#         "Given one or more recipe names, return a list of the most "
#         "ingredient-similar recipes for each input.")
    
#     args_schema: Type[BaseModel] = SimilarRecipesInput      
#     _conn: Any = PrivateAttr(default=None)     

#     def __init__(self, conn, **tool_kwargs):
#         super().__init__(**tool_kwargs)        
#         self._conn = conn   
   
#     def _run(self, names: List[str]) -> str:
#         data = get_similar_recipes(self.conn, names)
        
#         return json.dumps(data, indent=2)
