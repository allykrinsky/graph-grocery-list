import kuzu
import pandas as pd
from yfiles_jupyter_graphs import GraphWidget
from typing import Union, Any
import networkx as nx
from graph import find_edges, shopping_list_order

list_order = {
    'bread' : 1,
    'produce' : 2,
    'fridge' : 3,
    'dairy' : 4,
    'protein' : 5,
    'packaged' : 6,
    'freezer' : 7
}

# helpers
def custom_node_color_mapping(node: dict[str, Any]):
    """let the color be orange or blue if the index is even or odd respectively"""
    return ("#eb4934" if node['properties']['_label'] == "Recipe" else "#2456d4")

def normalize_name(name):
    return name.lower().replace(" ", "_")

# build the grocery list for all requested recipes
def generate_list(recipes):

    create_shopping_list(recipes)
    
    dfs = []
    for rec in recipes:
        dfs.append(find_edges(rec))
         
    result = pd.concat(dfs, ignore_index=True)
    
    return pd.DataFrame(result.groupby("Ingredient")["Quantity"].count().reset_index(), index=None)


def create_shopping_list(recipes):

    df = shopping_list_order(recipes)

    df2 = pd.DataFrame(df.groupby(by=["ingredient",'location', 'label'])["qty"].sum().reset_index(), index=None)
    df2 = df2[['qty', 'label', 'ingredient', 'location']]
    df2['sort_order'] = df2["location"].map((lambda x: list_order[x.strip()]))
    df_sorted = df2.sort_values(by="sort_order").drop(columns="sort_order")

    # print(df_sorted)

    return df_sorted





