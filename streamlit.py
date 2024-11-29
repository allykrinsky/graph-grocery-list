import streamlit as st
from helpers import normalize_name, generate_list, create_shopping_list, list_order
from graph import insert_ingredient, insert_recipe, get_ingredients, find_node, list_recipes, create_relationship, get_similar_recipes
import pandas as pd

# Set up Streamlit page configuration
st.set_page_config(page_title="Meal Planner", layout="wide")

recipes = list_recipes()
recipe_names = list(recipes['n.display_name'])
recipe_ids = list(recipes['n.name'])
ingredients = get_ingredients()
ingredient_names = list(ingredients['n.display_name'])
counter = 1
labels = {0: 'pack', 1: 'tsp', 2: 'tbsp', 3: 'cup', 4: 'piece', 5 : 'item'}
dow = ['Sunday', 'Monday', 'Tuesaday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
manual = []

st.header("Meal Planner")

if 'meal_list' not in st.session_state:
    st.session_state['meal_list'] = pd.DataFrame([["None" for i in range(len(dow))], ["None" for i in range(len(dow))]], columns=[dow], index=['Lunch', 'Dinner'])

if 'manual_list' not in st.session_state:
    st.session_state.manual_list = []


def map_display_to_recipe(recipe_list):

    return [recipes.iloc[recipe_names.index(option)]['n.name'] for option in recipe_list]

tab1, tab2 = st.tabs(["List", "Schedule"])

with tab1:

    st.subheader("Grocery List")
    
    selected_options = st.multiselect(
        "Select an option below:", options=recipe_names, key="select"
    )

    generated_list, manual_list = st.columns(2)

    with generated_list:

        if selected_options:

            selected_ids = [recipes.iloc[recipe_names.index(option)]['n.name'] for option in selected_options]
            recs = get_similar_recipes(selected_ids)['recipe'].tolist()

            ids = [recipes.iloc[recipe_ids.index(i)]['n.display_name'] for i in recs]
            st.pills("You may also like...", ids[:3] , selection_mode="multi")
            

            st.write("Check List")

            # generate list
            list_df = create_shopping_list(selected_ids)
            for row in list_df.iterrows():
                qty = 1 if row[1]['qty'].strip() == 'eyeball' else row[1]['qty'].strip()
                label = '' if row[1]['label'].strip() == 'na' else row[1]['label'].strip()
                st.checkbox(str(qty) + " " + str(label) + " " + row[1]['ingredient'])

    with manual_list:
       
        new_item = st.text_input("Add More to the List")
        if st.button('Add'):
            st.session_state.manual_list.append(new_item)

        for item in st.session_state.manual_list:
                st.checkbox(item) 
        

with tab2:
    st.subheader("Schedule")

    items, meal_plan = st.columns([1, 3])

    @st.dialog("Add to Meal Plan")
    def schedule_modal(item):
        days = st.multiselect("Day", options=dow, key="dow_select")
        meal = st.selectbox("Meal", options=['Lunch', 'Dinner'], key="meal_select")
        if st.button("Add to Meal Plan"):
            add_to_schedule(item, days, meal)
        
    def add_to_schedule(item_input, day_input, meal_input):
        idx = 0 if meal_input == 'Lunch' else 1
        for d in day_input:
            day_idx = dow.index(d)
            st.session_state.meal_list.iloc[idx, day_idx] = item_input
   
    with items:
        for r in recipe_names:
            if st.button(f"{r}", icon=":material/add:"): 
                schedule_modal(r)


    with meal_plan:
        st.data_editor(st.session_state.meal_list, num_rows="dynamic")
        if st.button("Generate List", type="primary"): 
                list = []
                for i in range(len(dow)):
                    if st.session_state.meal_list.iloc[0, i] != "None":
                        list.append(st.session_state.meal_list.iloc[0, i])

                    if st.session_state.meal_list.iloc[1, i] != "None":
                        list.append(st.session_state.meal_list.iloc[1, i])

                st.write(generate_list(map_display_to_recipe(list)))



     
with st.sidebar:

    st.subheader("Add Ingredients to Recipe")
    recipe_select = st.selectbox("Select a Recipe", options=recipe_names, key="recipe_select")

    with st.container():
        col1, col2, col3 = st.columns(3)

        # Dynamic ingredient input fields
        if "ingredient_count" not in st.session_state:
            st.session_state["ingredient_count"] = 1

        if st.button("Add More", icon=":material/add:"):
            st.session_state["ingredient_count"] += 1
            st.write(st.session_state["ingredient_count"])

        inputs = []
        for i in range(st.session_state["ingredient_count"]):
            with col1:
                qty = st.number_input('Quantity', step=1, key=f"Quantity {i+1}",)

            with col2:
                label = st.selectbox("Label", options=labels.values(), key=f"label{i+1}")
                
            with col3:
                ing_name = st.selectbox("Ingredient", options=ingredient_names, key=f"ing_sel{i+1}")

            inputs.append({
                "ing" : ingredients.iloc[ingredient_names.index(ing_name)]['n.name'],
                "qty": qty,
                "label" : label
            })
            

    if st.button("Submit", type="primary"):
        recipe_name = recipes.iloc[recipe_names.index(recipe_select)]['n.name']
        for i in inputs:
            create_relationship(recipe_name, i['ing'], i['qty'], i['label'])
            st.write(f"create_relationship({recipe_name}, {i['ing']}, {i['qty']}, {i['label']})")


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
        location = st.selectbox("location", options=list_order, key="loc")
        if st.button("Add Ingredient"):
            id = normalize_name(ingredient_name)
            if len(find_node(id)) > 0:
                st.warning("This ingredient already exists")
            else:
                insert_ingredient(id, ingredient_name, location)
                st.success(f"Ingredient '{ingredient_name}' successfully created")
