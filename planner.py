from shiny import App, reactive, render, ui
from helpers import normalize_name, process_inputs, generate_list
from graph import list_recipe_id, insert_ingredient, insert_recipe, get_ingredients

import faicons

# Create the app UI
app_ui = ui.page_fluid(
    ui.h2("Meal Planner"),
    ui.navset_pill(
        ui.nav_panel("Grocery List",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.h4("Add to List"),
                    ui.input_checkbox_group(
                        "select",
                        "Select an option below:",
                        choices=list_recipe_id()[0]
                    )
                ),
                ui.h4("Check List"),
                ui.output_ui("ui_checklist")
            )
        ),
        ui.nav_panel("New Recipes",
        
            ui.h4("Add Ingredients to Recipe"),
            ui.div(
                {"class": "d-flex align-items-center gap-2 mb-3"},
                ui.output_ui("get_recipes"),
                ui.input_action_button(
                    "add_new_recipe",
                    label=faicons.icon_svg("plus"),
                    class_="fa fa-plus btn-link text-secondary border-0"
                ),
            ),
            ui.output_ui("dynamic_inputs"),
            ui.div(
                {"class": "d-flex align-items-center gap-2 mb-3"},
                
                # ui.input_text("qty2", "Quantity", placeholder="Quantity..."),
                # ui.output_ui("get_ing"), 
                # ui.input_text("location2", "Location", placeholder="Location..."),
                # ui.input_action_button(
                #     "add_new_ingredient",
                #     label=faicons.icon_svg("plus"),
                #     class_="fa fa-plus btn-link text-secondary border-0"
                # ),
            ),
            ui.input_action_button("add_more", "Add More"),

            ui.input_action_button("submit2", "Submit"),
        ),
        id="tab",
    )
)


def server(input, output, session):

    list_ids = list_recipe_id()[1]
    recipes = reactive.Value(list_recipe_id()[0])
    ingredients = reactive.Value(get_ingredients())


    # create dropdowns for recipe & ingredients
    @render.ui
    def get_recipes():
        return ui.input_selectize(
            "recipe_select",
            "Select a Recipe",
            recipes(),

        )

    @render.ui
    def get_ing():
        return ui.input_selectize(
            f"ing_sel{counter.get()+2}",
            "Select an Ingredient",
            ingredients().to_dict()
        )
    
    counter = reactive.value(1)
    
    @reactive.effect
    @reactive.event(input.add_more)
    def _():
        counter.set(counter.get() + 1)
    
    @output
    @render.ui
    def dynamic_inputs():
        # Create additional input fields based on counter
        inputs = []
        for i in range(counter.get()):
            # i + 2 because we start with text1
            inputs.append(
                ui.div(
                    {"class": "d-flex align-items-center gap-2 mb-3"},
                    ui.input_text(f"qty{i+2}", "Quantity", placeholder="Quantity..."),
                    ui.output_ui("get_ing"), 
                    ui.input_text(f"location{i+2}", "Location", placeholder="Location..."),
                    ui.input_action_button(
                        f"add_new_ingredient{i+2}",
                        label=faicons.icon_svg("plus"),
                        class_="fa fa-plus btn-link text-secondary border-0"
                    ) # this needs to get hooked back up
                )
            )
        return ui.div(*inputs)


    

    # modals
    @reactive.effect
    @reactive.event(input.add_new_recipe)
    def _():
        m = ui.modal(
            ui.input_text("name", "Recipe", placeholder="Recipe..."),
            ui.input_text("r_type", "Type", placeholder="Type..."),
            ui.input_action_button("submit_recipes", "Add"),
            ui.output_text("test_submit"), 
            title="Add New Recipe",
            easy_close=True
        )
        ui.modal_show(m)


    @reactive.effect
    @reactive.event(input.add_new_ingredient)
    def _():
        n = ui.modal(
            ui.input_text("ingredient_name", "Ingredients", placeholder="Ingredient..."),
            ui.input_text("location", "Location", placeholder="Location..."),
            ui.input_action_button("submit_ing", "Add"),
            title="Add New Ingredient",
            easy_close=True
        )
        ui.modal_show(n)
    

    # generate grocery list based on input
    @reactive.Calc
    def make_list():
        return input.select()


    # display grocery checklist
    @output
    @render.ui
    def ui_checklist():
        selected_ids = make_list()
        if selected_ids:
            recipes = [list_ids[int(i)] for i in selected_ids]
            df = generate_list(recipes)
            df["result"] = df["Quantity"].astype(str) + " " + df["Ingredient"]
            return ui.input_checkbox_group("Check", "Select an option below:", choices=df["result"].to_dict())
        return None


    # actually submit recipe to graph & display sucessful submission
    @output
    @render.text
    @reactive.event(input.submit_recipes)
    def test_submit():
        # submitting the stuff into the graph
        # insert_recipe({input.name()}, {input.r_type()})
        return (
            f"Recipe Successfully Submitted:\n"
            f"Name: {input.name()}\n"
        )
        

    # actually submit ingredient to graph & display sucessful submission
    @output
    @render.text
    @reactive.event(input.submit_ing)
    def submit_recipe():
        # submitting the stuff into the graph
        
        insert_ingredient(normalize_name(input.ingredient_name()), input.ingredient_name(), input.location())
        return (
            f"Ingredient Successfully Created:\n"
            f"Name: {input.ingredient_name()}\n"
        )

app = App(app_ui, server)
