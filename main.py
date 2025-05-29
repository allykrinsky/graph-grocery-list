from notion import query_notion, create_df_from_notion
from graph import create_db, define_schemas, load_data
from helpers import parse_ingredients, parse_recipe
import os 
from dotenv import load_dotenv

load_dotenv()


databases = {
    "Recipe" : {
        "ID" : os.getenv("RECIPE_ID"),
        "token": os.getenv("RECIPE_TOKEN")

    },
    "Ingredient" : {
        "ID" : os.getenv("INGREDIENT_ID") ,
        "token": os.getenv("INGREDIENT_TOKEN")

    }
}

if __name__ == "__main__":


    # spin up graph
    conn = create_db()
    define_schemas(conn)


    for db, db_id in databases.items():
        response = query_notion(db_id)

        if db == 'Recipe':
            recipe_nodes = parse_recipe(response)
            load_data(conn, "Recipe", recipe_nodes)
        else:
            ingredient_nodes, contains = parse_ingredients(response)
            load_data(conn, "Ingredient", ingredient_nodes)
            load_data(conn, "Contains", contains)
            # load_data(conn, "UsedIn", used_in)


    