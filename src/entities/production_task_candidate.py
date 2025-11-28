from __future__ import annotations
from src.entities.machine import Machine
from src.entities.recipe import Recipe
from src.entities.units import str_quant

class ProductionTaskCandidate:
    """
    Represents a candidate machine for a specific production task (recipe + quantity).
    Contains the calculated estimated time.
    """
    def __init__(
        self,
        machine: Machine,
        recipe: Recipe,
        total_quantity: float,
        estimated_time: float
    ):
        self.machine = machine
        self.recipe = recipe
        self.total_quantity = total_quantity
        self.estimated_time = estimated_time

    def __repr__(self) -> str:
        return (
            f"Candidate(Machine='{self.machine.name}', "
            f"Recipe='{self.recipe.name}', "
            f"Qty={str_quant(self.total_quantity, self.recipe.output_unit)}, "
            f"Time={self.estimated_time:.2f}s)"
        )
