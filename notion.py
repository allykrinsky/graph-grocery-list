import os
from dotenv import load_dotenv
import streamlit as st

from notion_client import Client
import pandas as pd

from graph import create_db, define_schemas, load_data
from helpers import parse_ingredients, parse_recipe

load_dotenv()

# Get secrets from Streamlit secrets (for deployment) or environment variables (for local dev)
def get_secret(key):
    """Get secret from st.secrets if available, otherwise from environment variables"""
    try:
        # Try to get from Streamlit secrets (for deployment)
        return st.secrets[key]
    except (FileNotFoundError, KeyError, Exception):
        # If secrets.toml doesn't exist, key not found, or can't be read, fall back to env vars
        pass

    # Fall back to environment variables (for local development)
    return os.getenv(key)

databases = {
    "Recipe" : {
        "ID" : get_secret("RECIPE_SOURCE"),
        "token": get_secret("RECIPE_TOKEN")

    },
    "Ingredient" : {
        "ID" : get_secret("INGREDIENT_SOURCE"),
        "token": get_secret("INGREDIENT_TOKEN")

    }
}

def set_up_graph(data):

    conn = create_db()
    define_schemas(conn)

    for db in databases.keys():

        if db == 'Recipe':
            recipe_nodes = parse_recipe(data[db])
            load_data(conn, "Recipe", recipe_nodes)
        else:
            ingredient_nodes, contains = parse_ingredients(data[db])
            load_data(conn, "Ingredient", ingredient_nodes)
            load_data(conn, "Contains", contains)
            load_data(conn, "UsedIn", contains[contains.columns[::-1]])

    return conn


def pull_from_notion():
    # conn = create_db()
    # define_schemas(conn)

    data = {}
    for db, db_id in databases.items():

        client = Client(auth=databases.get(db)['token'])
        response = query_notion(client, db_id['ID'])
        print("Connected to Notion: " + db)

        data[db] = response
        
    return data

# query notion based on which database i want
def query_notion(client, db_id):
    return client.data_sources.query(
        data_source_id=db_id
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