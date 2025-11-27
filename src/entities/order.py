from __future__ import annotations
from src.entities.units import Unit, str_quant

class OrderItem:
    """
    Represents a single line item in an order: a recipe and the quantity requested.
    """
    
    def __init__(self, recipe, quantity: float):
        self.recipe = recipe
        self.quantity = quantity
    
    @property
    def unit(self) -> Unit:
        """Returns the unit from the associated recipe's output unit."""
        return self.recipe.output_unit
    
    def __repr__(self) -> str:
        return f"  - {self.recipe.name}: {str_quant(self.quantity, self.unit)}"


class Order:
    """
    Represents a production order containing multiple recipe requests.
    """
    
    def __init__(self, name: str, items: list[OrderItem]):
        self.name = name
        self.items = items
    
    def __repr__(self) -> str:
        lines = [f"Order '{self.name}'"]
        for item in self.items:
            lines.append(str(item))
        return "\n".join(lines)
