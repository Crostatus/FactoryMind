from src.entities.raw_material import RawMaterial
from src.entities.units import Unit, str_quant

class Recipe:
    """
    Represents the formula of a finished product, defined by its required raw materials.
    """

    def __init__(
        self,
        name: str,
        ingredients: dict[RawMaterial, float],
        output_quantity: float,  # quantity produced per recipe
        description: str = None,
        category: str = None,
        output_unit: Unit = Unit.PIECE,
    ):
        # --- core attributes ---
        self.name = name
        self.ingredients = ingredients
        self.output_quantity = output_quantity
        
        # --- optional attributes ---
        self.description = description
        self.category = category
        self.output_unit = output_unit        

    def __repr__(self):                            
        str_recipe = [f"Recipe '{self.name}' ({len(self.ingredients)} ingredients)"]                
        str_recipe.append(f"   Ingredients for {str_quant(self.output_quantity, self.output_unit)}:")        
        for mat, qty in self.ingredients.items():
            str_recipe.append(f"     - {mat.name}: {str_quant(qty, mat.unit)}")            
        return "\n".join(str_recipe)       