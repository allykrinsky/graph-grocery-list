import os
from notion_client import Client as NotionClient
from dotenv import load_dotenv
from pprint import pprint
from helpers import normalize_name
import pandas as pd

# Load API keys from .env
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

# TODO: register db & set up connections - i need to create 3-4 distinct dbs 
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
notion = NotionClient(auth=NOTION_TOKEN)

# query notion based on which database i want
def query_notion(db_id):
    return notion.databases.query(
        database_id=db_id,
        # filter={
        #     "and":[
        #         {
        #             "property": "Status",
        #             "status": {
        #                 "equals": "Posted"
        #             }},
        #         {
        #             "property": "KB",
        #             "checkbox" : {
        #                 "equals" : True
        #             }}]  
        # }
    )

# return DF with columns id, ingredient_name, aisle, recipe_ids
def parse_ingredient_response(notion_data):
    return pd.DataFrame([
        {
            "id": val["id"],
            "ingredient_name": val["properties"]["Name"]["title"][0]["plain_text"]
                if val["properties"]["Name"]["title"] else None,
            "aisle": val["properties"]["Aisle"]["select"]["name"]
                if val["properties"]["Aisle"]["select"] else None,
            "recipe_ids": [r["id"] for r in val["properties"]["Recipes"]["relation"]],
        }
        for val in notion_data["results"]
    ])

def create_relationship_table(data):
    return data.explode('recipe_ids')

# return DF with columns id, recipe_name, type
def parse_recipe_response(notion_data):

    return pd.DataFrame([
        {
            "id": val["id"],
            "recipe_name": val["properties"]["Name"]["title"][0]["plain_text"]
                if val["properties"]["Name"]["title"] else None,
            "type": val["properties"]["Type"]["select"]["name"]
                if val["properties"]["Type"]["select"] else None,
        }
        for val in notion_data["results"]
    ])