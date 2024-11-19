import streamlit as st
from helpers import normalize_name, process_inputs, generate_list
from graph import list_recipe_id, insert_ingredient, insert_recipe, get_ingredients, find_node, list_recipes, create_relationship
import pandas as pd

# Set up Streamlit page configuration
st.set_page_config(page_title="Meal Planner", layout="wide")


# TODO need to flip these 
# Helper variables
# list_ids = list_recipe_id()[1]
recipes = list_recipes()
recipe_names = list(recipes['n.display_name'])
ingredients = get_ingredients()
ingredient_names = list(ingredients['n.display_name'])
counter = 1
labels = {0: 'pack', 1: 'tsp', 2: 'tbsp', 3: 'cup', 4: 'piece'}

# Navigation tabs
tab1, tab2 = st.tabs(["Grocery List", "New Recipes"])

# Tab 1: Grocery List
with tab1:
    st.header("Grocery List")
    selected_options = st.multiselect(
        "Select an option below:", options=recipe_names, key="select"
    )

    # print(selected_options)
    if selected_options:
        
        selected_ids = [recipes.iloc[recipe_names.index(option)]['n.name'] for option in selected_options]
        # print('test')
        # print(selected_ids)
        df = generate_list(selected_ids)
        df["result"] = df["Quantity"].astype(str) + " " + df["Ingredient"]
        # st.checkbox("Check List")
        # st.write(df["result"].to_list())
        st.write("Check List")
        for item in df["result"].to_list():
            st.checkbox(item)

# TODO fix the formatting of this page
# Tab 2: New Recipes
with tab2:
    st.header("Add Ingredients to Recipe")
    
    # Dropdown to select recipes
    recipe_select = st.selectbox("Select a Recipe", options=recipe_names, key="recipe_select")
    
    # Dynamic ingredient input fields
    if "ingredient_count" not in st.session_state:
        st.session_state["ingredient_count"] = 1
    
    # if st.button("Add More"):
    #     st.session_state["ingredient_count"] += 1

    for i in range(st.session_state["ingredient_count"]):
        qty = st.text_input(f"Quantity {i+1}", placeholder="Quantity...")
        label = st.selectbox("Quantity Label", options=labels.values(), key=f"label{i+1}")
        ing_name = st.selectbox("Select an Ingredient", options=ingredient_names, key=f"ing_sel{i+1}")
        
    
    if st.button("Submit"):
        recipe_name = recipes.iloc[recipe_names.index(recipe_select)]['n.name']
        ingredient_name = ingredients.iloc[ingredient_names.index(ing_name)]['n.name']
        create_relationship(recipe_name, ingredient_name, qty, label)
        st.write(f"create_relationship({recipe_name}, {ingredient_name}, {qty}, {label})")


    # Modal to add a new recipe
    with st.expander("Add New Recipe"):
        recipe_name = st.text_input("Recipe Name")
        r_type = st.text_input("Type")
        if st.button("Add Recipe"):
            id = normalize_name(recipe_name)
            if len(find_node(id)) > 0:
                st.warning("This recipe already exists")
            else:
                insert_recipe(id, recipe_name, r_type)
                st.success(f"Recipe '{recipe_name}' successfully submitted")

    # Modal to add a new ingredient
    with st.expander("Add New Ingredient"):
        ingredient_name = st.text_input("Ingredient Name")
        location = st.text_input("Location")
        if st.button("Add Ingredient"):
            id = normalize_name(ingredient_name)
            if len(find_node(id)) > 0:
                st.warning("This ingredient already exists")
            else:
                insert_ingredient(id, ingredient_name, location)
                st.success(f"Ingredient '{ingredient_name}' successfully created")
