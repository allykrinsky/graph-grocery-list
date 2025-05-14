from notion import query_notion, create_df_from_notion
from graph import create_db, define_schemas, load_data

databases = {
    "Recipe" : "recipes_id",
    "Ingredient" : "ingredients_id",
    "relationship" : "rel_id"
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
