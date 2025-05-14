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
        filter={
            "and":[
                {
                    "property": "Status",
                    "status": {
                        "equals": "Posted"
                    }},
                {
                    "property": "KB",
                    "checkbox" : {
                        "equals" : True
                    }}]  
        })

# normalize names from notion + convert to DF
def create_df_from_notion(notion_data):
    df = pd.DataFrame(notion_data)
    df['id'] = df['name'].apply(lambda x: normalize_name(x))

    return df



