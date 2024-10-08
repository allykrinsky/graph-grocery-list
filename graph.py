import kuzu
import pandas as pd
from yfiles_jupyter_graphs import GraphWidget
from typing import Union, Any
import networkx as nx

db = kuzu.Database("./final_db",read_only=True)
conn = kuzu.Connection(db)

def custom_node_color_mapping(node: dict[str, Any]):
    """let the color be orange or blue if the index is even or odd respectively"""
    return ("#eb4934" if node['properties']['_label'] == "Recipe" else "#2456d4")


def get_graph():
    response = conn.execute(
        """
        MATCH (n)-[r:Contains]-(m)
        RETURN *
        """
    )
    G = response.get_as_networkx(directed=False)
    
    return G

def list_recipe_id():
    response = conn.execute(
            """
            MATCH (n:Recipe)
            RETURN n.name, n.display_name
            """
        )
    options = {}
    ids = {}
    count = 0
    while response.has_next():
        rep = response.get_next()
        options[count] = rep[1]
        ids[count] = rep[0]
        count +=1 
        # meals[rep[0]] = rep[1]
        # list.append([rep[0], rep[0]])

    # return pd.DataFrame(list, columns=['Recipes'])
    return options, ids


def list_recipes():
    response = conn.execute(
            """
            MATCH (n:Recipe)
            RETURN n.display_name
            """
        )
    list = []
    while response.has_next():
        list.append(response.get_next()[0])

    return pd.DataFrame(list, columns=['Recipes'])

def get_recipe(recipeName, conn):

    response = conn.execute(
                f"""
                MATCH (n:Ingredient)-[r:Contains]-(m:Recipe)
                WHERE m.name = '{recipeName}'
                RETURN n.display_name, r.quantity
                """
            )
    list = []
    while response.has_next():
        list.append(response.get_next())

    return pd.DataFrame(list, columns=['Ingredient', 'Quantity'])


def get_recipes_from_input():
    pass

def generate_list(recipes):
    # recipes = ["taco_bowl", "curry", "quinoa"]

    print(recipes)
    
    dfs = []
    for rec in recipes:
        dfs.append(get_recipe(rec, conn))
         
    result = pd.concat(dfs, ignore_index=True)
 
    
    return pd.DataFrame(result.groupby("Ingredient")["Quantity"].count().reset_index(), index=None)
    

 

