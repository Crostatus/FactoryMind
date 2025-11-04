from entities.raw_material import RawMaterial
from entities.units import Unit

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
        output_unit: Unit = Unit.PIECE,  # <-- now uses the same Enum        
    ):
        # --- core attributes ---
        self.name = name
        self.ingredients = ingredients  # {RawMaterial: qty per output_unit}
        self.output_quantity = output_quantity
        
        # --- optional attributes ---
        self.description = description
        self.category = category
        self.output_unit = output_unit        

    def __repr__(self):
        return f"Recipe({self.name}, {len(self.ingredients)} ingredients, output={self.output_quantity} {self.output_unit.value})"

    def list_ingredients(self) -> str:
        """
        Returns a formatted string listing all ingredients and their required quantities.
        """
        lines = [f"Recipe: {self.name} (Output: {self.output_quantity} {self.output_unit.value})"]
        for mat, qty in self.ingredients.items():
            lines.append(f"  - {mat.name}: {qty} {mat.unit.value} per {self.output_unit.value}")
        return "\n".join(lines)
