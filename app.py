import pandas as pd
import streamlit as st

from notion import pull_from_notion, set_up_graph
from graph import get_ingredients, list_recipes, get_similar_recipes, shopping_list_order

# Set up Streamlit page configuration
st.set_page_config(page_title="Meal Planner", layout="wide")

#pull & cache notion data
@st.cache_data
def fetch_data():
    return pull_from_notion()

data = fetch_data()
conn = set_up_graph(data)

recipes = list_recipes(conn)
recipe_names = list(recipes['name'])
recipe_ids = list(recipes['id'])
ingredients = get_ingredients(conn)
ingredient_names = list(ingredients['n.name'])
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

    return [recipes.iloc[recipe_names.index(option)]['id'] for option in recipe_list]

tab1, tab2, tab3 = st.tabs(["Browse", "Calendar", "Grocery List"])

# Session state for meal schedule
if 'selected_meals' not in st.session_state:
    st.session_state.selected_meals = {day: {'Lunch': None, 'Dinner': None} for day in dow}

# Session state for meals selected for the week (not yet scheduled)
if 'week_meals' not in st.session_state:
    st.session_state.week_meals = []

def add_to_week(recipe_name):
    """Add a meal to this week's collection"""
    if recipe_name not in st.session_state.week_meals:
        st.session_state.week_meals.append(recipe_name)

def remove_from_week(recipe_name):
    """Remove a meal from this week's collection"""
    if recipe_name in st.session_state.week_meals:
        st.session_state.week_meals.remove(recipe_name)

def add_meal_to_schedule(recipe_name, day, meal_type):
    """Add a meal to the schedule"""
    st.session_state.selected_meals[day][meal_type] = recipe_name

def remove_meal_from_schedule(day, meal_type):
    """Remove a meal from the schedule"""
    st.session_state.selected_meals[day][meal_type] = None

def get_scheduled_recipes():
    """Get list of all scheduled recipe names"""
    scheduled = []
    for day in dow:
        for meal_type in ['Lunch', 'Dinner']:
            meal = st.session_state.selected_meals[day][meal_type]
            if meal:
                scheduled.append(meal)
    return list(set(scheduled))  # Remove duplicates

def get_all_week_recipes():
    """Get all recipes for the week (both scheduled and unscheduled)"""
    all_recipes = st.session_state.week_meals + get_scheduled_recipes()
    return list(set(all_recipes))  # Remove duplicates

with tab1:

    sidebar, main_content = st.columns([3, 2])

    with sidebar:
        st.markdown("### All Recipes")

        # Initialize search state
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""

        # Initialize recipes to show count
        if 'recipes_to_show' not in st.session_state:
            st.session_state.recipes_to_show = 20

        # Text input with on_change to ensure real-time updates
        def update_search():
            st.session_state.search_query = st.session_state.recipe_search_input
            st.session_state.recipes_to_show = 20  # Reset count when search changes

        search_query = st.text_input(
            "Search recipes...",
            key="recipe_search_input",
            value=st.session_state.search_query,
            on_change=update_search,
            placeholder="Type to filter..."
        )

        # Filter recipes based on search
        filtered_recipes = [r for r in recipe_names if not search_query or search_query.lower() in r.lower()]

        # Display recipe cards in 2 columns
        col1, col2 = st.columns(2)

        recipes_displayed = min(st.session_state.recipes_to_show, len(filtered_recipes))
        for idx, recipe in enumerate(filtered_recipes[:recipes_displayed]):
            with col1 if idx % 2 == 0 else col2:
                with st.container(border=True):
                    st.markdown(f"<small>**{recipe}**</small>", unsafe_allow_html=True)
                    if recipe in st.session_state.week_meals:
                        st.button("✓", key=f"added_{recipe}", disabled=True, use_container_width=True)
                    else:
                        if st.button("➕", key=f"add_week_{recipe}", use_container_width=True):
                            add_to_week(recipe)
                            st.rerun()

        # Show More button
        if recipes_displayed < len(filtered_recipes):
            if st.button(f"Show More ({len(filtered_recipes) - recipes_displayed} remaining)", use_container_width=True):
                st.session_state.recipes_to_show += 20
                st.rerun()

    with main_content:
        st.markdown("### This Week's Meals")

        all_week = get_all_week_recipes()

        if all_week:
            # Show recommendations based on selected meals
            st.markdown("**Recommended**")
            recs_df = get_similar_recipes(conn, all_week)

            if not recs_df.empty:
                recs_df = recs_df[~recs_df['recipe'].isin(all_week)]

                for _, rec in recs_df.head(3).iterrows():
                    with st.container(border=True):
                        cols = st.columns([4, 1])
                        with cols[0]:
                            st.markdown(f"<small>**{rec['recipe']}**</small>", unsafe_allow_html=True)
                            st.caption(f"↻ {rec['sharedIngredientCount']} shared")
                        with cols[1]:
                            if st.button("➕", key=f"add_rec_{rec['recipe']}", use_container_width=True):
                                add_to_week(rec['recipe'])
                                st.rerun()

            st.divider()
            st.markdown("**Selected Meals**")
            st.caption(f"{len(all_week)} meals for this week")

            # Show week meals (not yet scheduled)
            for meal in st.session_state.week_meals:
                with st.container(border=True):
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.markdown(f"<small>{meal}</small>", unsafe_allow_html=True)
                    with cols[1]:
                        if st.button("✕", key=f"remove_week_{meal}", use_container_width=True):
                            remove_from_week(meal)
                            st.rerun()
        else:
            st.info("Add meals from the browse list to get started!")

with tab2:
    st.subheader("Calendar")

    # Two column layout
    unscheduled_meals, schedule_view = st.columns([2, 5])

    with unscheduled_meals:
        st.markdown("### Unscheduled Meals")

        # Show meals that haven't been placed in the calendar yet
        scheduled = get_scheduled_recipes()
        unscheduled = [m for m in st.session_state.week_meals if m not in scheduled]

        if unscheduled:
            st.caption(f"{len(unscheduled)} meals to schedule")
            for meal in unscheduled:
                with st.container(border=True):
                    st.markdown(f"<small>**{meal}**</small>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        day_select = st.selectbox(
                            "Day",
                            options=dow,
                            key=f"day_{meal}",
                            label_visibility="collapsed"
                        )
                    with col2:
                        meal_select = st.selectbox(
                            "Meal",
                            options=['Lunch', 'Dinner'],
                            index=1,
                            key=f"meal_{meal}",
                            label_visibility="collapsed"
                        )
                    with col3:
                        if st.button("📅", key=f"schedule_{meal}", use_container_width=True):
                            add_meal_to_schedule(meal, day_select, meal_select)
                            st.rerun()
        else:
            st.info("All meals scheduled! Add more from Browse tab.")

    with schedule_view:
        st.markdown("### This Week's Menu")

        # Display weekly grid
        for meal_type in ['Lunch', 'Dinner']:
            st.markdown(f"**{meal_type}**")
            cols = st.columns(7)

            for idx, day in enumerate(dow):
                with cols[idx]:
                    st.markdown(f"*{day[:3]}*")  # Show abbreviated day name
                    meal = st.session_state.selected_meals[day][meal_type]

                    if meal:
                        # Show meal with remove button
                        st.markdown(f"✓ {meal[:15]}...")  # Truncate long names
                        if st.button("✕", key=f"remove_{day}_{meal_type}", help="Remove meal"):
                            remove_meal_from_schedule(day, meal_type)
                            st.rerun()
                    else:
                        st.markdown("—")
            st.divider()

        # Generate grocery list button
        scheduled_recipes = get_scheduled_recipes()
        if scheduled_recipes:
            st.markdown(f"**{len(scheduled_recipes)} unique recipes scheduled**")
            if st.button("📋 Generate Grocery List", type="primary", use_container_width=True):
                st.session_state['quick_list_recipes'] = scheduled_recipes
                st.success("Grocery list generated! Check the 'Grocery List' tab.")
        else:
            st.info("Add meals to your schedule to generate a grocery list")

with tab3:

    st.subheader("Grocery List")

    # Check if we have recipes from schedule
    if 'quick_list_recipes' in st.session_state and st.session_state.quick_list_recipes:
        selected_options = st.session_state.quick_list_recipes
        st.success(f"Using {len(selected_options)} recipes from your schedule")

        # Option to modify
        if st.checkbox("Modify recipe selection"):
            selected_options = st.multiselect(
                "Adjust recipes:",
                options=recipe_names,
                default=selected_options,
                key="select_modify"
            )
    else:
        st.info("Generate a list from your schedule, or manually select recipes below")
        selected_options = st.multiselect(
            "Select recipes:", options=recipe_names, key="select"
        )

    generated_list, manual_list = st.columns(2)

    with generated_list:

        if selected_options:

            # generate list
            st.markdown("### Shopping List")
            list_df = shopping_list_order(conn, selected_options)

            # Group by location for organized shopping
            if not list_df.empty:
                # Group by aisle/location
                list_df['location'] = list_df['location'].fillna('other')

                for location in sorted(list_df['location'].unique()):
                    st.markdown(f"**{location.title()}**")
                    location_items = list_df[list_df['location'] == location]

                    # Count occurrences
                    counts = location_items.groupby("ingredient").size().reset_index(name='count')

                    for _, row in counts.iterrows():
                        count_str = f"({row['count']}x) " if row['count'] > 1 else ""
                        st.checkbox(f"{count_str}{row['ingredient']}", key=f"check_{location}_{row['ingredient']}")

                    st.divider()
            else:
                st.warning("No ingredients found for selected recipes")

    