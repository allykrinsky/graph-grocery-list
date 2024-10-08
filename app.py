# This file generated by Quarto; do not edit by hand.
# shiny_mode: core

from __future__ import annotations

from pathlib import Path
from shiny import App, Inputs, Outputs, Session, ui

from shiny import reactive, render
from shiny.express import ui
# from shiny.express import input

# ========================================================================




def server(input: Inputs, output: Outputs, session: Session) -> None:
    from graph import list_recipe_id, list_recipes
    from graph import generate_list

    options, list_ids = list_recipe_id()

    ui.input_checkbox_group(  
        "select",  
        "Select an option below:",  
        options
    ) 

    # ui.input_action_button("action_button", "Generate List")    

    @reactive.Calc
    def make_list():
        return input.select()


    # ui.input_switch("show_slider", "Show slider", True)

    # ========================================================================

    # @render.data_frame
    # def test():

    #     ids = make_list()

    #     if len(ids) > 0 :
    #         recipes = []
    #         for i in ids:
    #             recipes.append(list_ids[int(i)])
        
    #         df = generate_list(recipes)

    #         return render.DataTable(df) 


    # ========================================================================

    # ui.input_switch("show_slider", "Show slider", True)

    @render.express  
    def ui_slider():  

        ids = make_list()
        if len(ids) > 0 :
            recipes = []
            for i in ids:
                recipes.append(list_ids[int(i)])
        
            df = generate_list(recipes)
            df['result'] = df['Quantity'].astype(str) + ' ' + df['Ingredient']

            ui.input_checkbox_group(  
                "Check",  
                "Select an option below:",  
                df['result'].to_dict()
            ) 


    # ========================================================================



    return None


_static_assets = ["index_files"]
_static_assets = {"/" + sa: Path(__file__).parent / sa for sa in _static_assets}

app = App(
    Path(__file__).parent / "index.html",
    server,
    static_assets=_static_assets,
)
