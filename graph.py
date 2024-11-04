import kuzu

db = kuzu.Database("./final_db", read_only=True)
conn = kuzu.Connection(db)


# get nodes by name
def find_node(name):
    response = conn.execute(
        """
        MATCH (n)
        WHERE n.name = $name
        RETURN n.name, n.type
        """
        , {"name" : name})
    return response.get_as_df()


# returns True if an edge exists between the 2 nodes
def is_edge(recipe, ingredient):

    response = conn.execute(
        """
        MATCH (n:Recipe)-[r:Contains]->(m:Ingredient)
        WHERE n.name = $recipe AND m.name = $ingredient, 
        RETURN m.name, n.name, r.quantity;
        """, {"recipe" : recipe, "ingredient" : ingredient})
    
    return len(response.get_as_df()) > 0
        

# find all ingredients for a given recipe
def find_edges(recipe):
    response = conn.execute(
        """
        MATCH (n:Recipe)-[r:Contains]->(m:Ingredient)
        WHERE n.name = $name
        RETURN m.name, r.quantity;
        """, {"name" : recipe})
    
    df = response.get_as_df()
    df.columns = ['Ingredient', 'Quantity']

    return df
    




# create new recipe nodes
def insert_recipe(name, display_name, type):
    conn.execute(
        """
        CREATE (u:Recipe {name : $name, display_name: $display_name, type: $type});
        """
        , {"name" : name, "display_name": display_name, "type": type})
    

# insert new ingredient nodes
def insert_ingredient(name, display_name, type):
    conn.execute(
        """
        CREATE (u:Ingredient {name : $name, display_name: $display_name, type: $type});
        """
        , {"name" : name, "display_name": display_name, "type": type})
    

# draw edge  between recipe and ingredient
def create_relationship(recipe_name, ingredient_name, qty, label):

    conn.execute(
        """
        MATCH (u1:Recipe), (u2:Ingredient)
        WHERE u1.name = $recipe_name AND u2.name = $ingredient_name
        CREATE (u1)-[r:Contains {quantity: $qty, label: $label}]->(u2)
        RETURN r;
        """,
        {"recipe_name": recipe_name, "ingredient_name": ingredient_name, "qty": qty, "label":label}
    )

def get_ingredients():
    response = conn.execute(
            """
            MATCH (n:Ingredient)
            RETURN n.display_name
            """
        )
    return response.get_as_df()

# list recipes with associated IDs
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

    return options, ids


# def get_graph():
#     response = conn.execute(
#         """
#         MATCH (n)-[r:Contains]-(m)
#         RETURN *
#         """
#     )
#     G = response.get_as_networkx(directed=False)
    
#     return G