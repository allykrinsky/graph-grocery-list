import kuzu


# TODO is there a setting for in memory vs saved
def create_db():
    db = kuzu.Database()
    conn = kuzu.Connection(db)

    return conn


def define_schemas(conn):
    conn.execute("CREATE NODE TABLE Recipe(id STRING, name STRING, type STRING, PRIMARY KEY (id))")
    # conn.execute("CREATE NODE TABLE Recipe(id STRING, name STRING, type STRING, vibe STRING, servings INT, cookTime STRING, PRIMARY KEY (id))")
    conn.execute("CREATE NODE TABLE Ingredient(id STRING, name STRING, location STRING, PRIMARY KEY (id))")
    conn.execute("CREATE REL TABLE Contains(FROM Recipe TO Ingredient, quantity STRING, label STRING)")
    conn.execute("CREATE REL TABLE UsedIn(FROM Ingredient TO Recipe)")

def load_data(conn, table, df):

    query = f"COPY {table} FROM df"
    conn.execute(
        query
    )


### GETS #####

# get nodes by name
def find_node(conn, name):
    response = conn.execute(
        """
        MATCH (n)
        WHERE n.name = $name
        RETURN n.name, n.type
        """
        , {"name" : name})
    return response.get_as_df()


# returns True if an edge exists between the 2 nodes
def is_edge(conn, recipe, ingredient):

    response = conn.execute(
        """
        MATCH (n:Recipe)-[r:Contains]->(m:Ingredient)
        WHERE n.name = $recipe AND m.name = $ingredient, 
        RETURN m.name, n.name, r.quantity;
        """, {"recipe" : recipe, "ingredient" : ingredient})
    
    return len(response.get_as_df()) > 0
        

# find all ingredients for a given recipe
def find_edges(conn, recipe):
    response = conn.execute(
        """
        MATCH (n)-[r]->(m)
        WHERE n.name = $name
        RETURN m.display_name, r.quantity;
        """, {"name" : recipe})
    
    df = response.get_as_df()
    df.columns = ['Ingredient', 'Quantity']

    return df

def get_ingredients(conn):
    response = conn.execute(
            """
            MATCH (n:Ingredient)
            RETURN n.display_name, n.name
            """
        )
    return response.get_as_df()

def list_recipes(conn):
    response = conn.execute(
            """
            MATCH (n:Recipe)
            RETURN n.name as id, n.display_name as name
            """
        )
    return response.get_as_df()
    

def get_recipes_by_ingredient(conn, name):
    response = conn.execute(
        """
        MATCH (n:Ingredient)-[r:UsedIn]->(m:Recipe)
        WHERE n.name = $name
        RETURN m.name, m.type;
        """
        , {"name" : name})
    print(response.get_as_df())


def shopping_list_order(conn, recipes):
    response = conn.execute(
        """
        UNWIND $inputRecipes AS inputRecipeName
        MATCH (n:Recipe {name: inputRecipeName})-[r]->(m:Ingredient)
        RETURN m.display_name as ingredient, r.quantity as qty, r.label as label, m.type as location;
        """, {"inputRecipes" : recipes})
    
    df = response.get_as_df()
    # print(df)
    # df.columns = ['Ingredient', 'Quantity']

    return df


#### CREATE ####

# create new recipe nodes
def insert_recipe(conn, name, display_name, type):
    conn.execute(
        """
        CREATE (u:Recipe {name : $name, display_name: $display_name, type: $type});
        """
        , {"name" : name, "display_name": display_name, "type": type})
    

# insert new ingredient nodes
def insert_ingredient(conn, name, display_name, type):
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
        CREATE (u2)-[q:usedIn {quantity: $qty, label: $label}]->(u1)
        RETURN r, q;
        """,
        {"recipe_name": recipe_name, "ingredient_name": ingredient_name, "qty": qty, "label":label}
    )

#### DELTE ###

def delete_node(conn, name):
    response = conn.execute(
        """
        MATCH (u) WHERE u.name = $name DETACH DELETE u;
        """
        , {"name" : name})
    print(response.get_as_df())


def delete_relationship(conn, recipe, ingredient):
    response = conn.execute(
        """
        MATCH (u:Recipe)-[f]->(u1:Ingredient)
        WHERE u.name = $recipe AND u1.name = $ingredient
        DELETE f;
        """
        , {"recipe" : recipe, "ingredient": ingredient})
    print(response.get_as_df())


#### Recommendations ####
def get_similar_recipes(conn, names):
    response = conn.execute(
        """
        UNWIND $inputRecipes AS inputRecipeName
        MATCH (inputRecipe:Recipe {name: inputRecipeName})-[:Contains]->(inputIngredient:Ingredient)
        WITH inputIngredient, COLLECT(inputRecipe) AS inputRecipes
        MATCH (similarRecipe:Recipe)<-[:UsedIn]-(similarIngredient:Ingredient)
        WHERE similarIngredient.name = inputIngredient.name
        AND NOT similarRecipe IN inputRecipes
        WITH similarRecipe, collect(similarIngredient) AS sharedIngredients
        WHERE size(sharedIngredients) > 0
        RETURN similarRecipe.name as recipe, size(sharedIngredients) AS sharedIngredientCount
        ORDER BY sharedIngredientCount DESC;
        """, {"inputRecipes" : names}
    )
    
    df = response.get_as_df()
    
    return df