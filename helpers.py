import kuzu
import pandas as pd
from yfiles_jupyter_graphs import GraphWidget
from typing import Union, Any
import networkx as nx
from graph import find_edges


# helpers
def custom_node_color_mapping(node: dict[str, Any]):
    """let the color be orange or blue if the index is even or odd respectively"""
    return ("#eb4934" if node['properties']['_label'] == "Recipe" else "#2456d4")

def normalize_name(name):
    return name.lower().replace(" ", "_")

# build the grocery list for all requested recipes
def generate_list(recipes):
    # recipes = ["taco_bowl", "curry", "quinoa"]

    print(recipes)
    
    dfs = []
    for rec in recipes:
        # dfs.append(get_recipe(rec, conn))
        dfs.append(find_edges(rec))
         
    result = pd.concat(dfs, ignore_index=True)
 
    
    return pd.DataFrame(result.groupby("Ingredient")["Quantity"].count().reset_index(), index=None)
    

def process_inputs(text1, text2):
    # Example function that processes the inputs
    return f"Processed: {text1} and {text2}"

# def add_full_recipe(recipe, type, ingredient, location, qty):
#     recipe_dict = {"name" : normalize_name(recipe), "display_name": recipe, "type": type}

#     ingredient_dict = [{"name" : normalize_name(ingredient), "display_name": ingredient, "type": location}]

#     quant, label = qty.split()
#     relationship = {"quantity" : quant, "label": label}

#     try:
#         insert_recipe(recipe_dict)
#     except:
#         print("recipe already exists")
#     try:
#         insert_ingredient(ingredient_dict)
#     except:
#         print("ingredient already exists")

    
#     create_relationship(recipe, ingredient, relationship)
    








