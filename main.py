from notion import query_notion, create_df_from_notion
from graph import create_db, define_schemas, load_data
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
        df = create_df_from_notion(response)

        # load data into graph
        load_data(conn, db, df)
