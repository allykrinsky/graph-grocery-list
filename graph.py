import kuzu
import pandas as pd


def get_recipe(recipeName, conn):

    response = conn.execute(
                f"""
                MATCH (n:Ingredient)-[r:UsedIn]->(m:Recipe)
                WHERE m.name = '{recipeName}'
                RETURN n.name, r.quantity
                """
            )
    list = []
    while response.has_next():
        # print(response.get_next())
        list.append(response.get_next())

    return pd.DataFrame(list, columns=['Ingredient', 'Quantity'])

def main() -> None:
    # Create an empty on-disk database and connect to it
    db = kuzu.Database("./full_db")
    conn = kuzu.Connection(db)

    recipes = ["sausage_risotto", "short_rib_bowl", "salmon_bowl", "caprese_sandwich", "vodka_pasta"]

    dfs = []
    for rec in recipes:
        dfs.append(get_recipe(rec, conn))
         
    result = pd.concat(dfs, ignore_index=True)
    # print(result)
    
    print(result.groupby("Ingredient")["Quantity"].count())
    

main()