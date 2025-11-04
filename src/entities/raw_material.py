from src.entities.units import Unit

class RawMaterial:
    """
    Represents a basic ingredient used in one or more recipes.
    """

    def __init__(
        self,
        name: str,
        unit: Unit,
        unit_cost: float,
        stock_quantity: float,
        prep_time: float,
        supplier: str = None,
        shelf_life_days: int = None,
        category: str = None,
    ):
        # --- primary attributes ---
        self.name = name  # e.g. "Flour 00"
        self.unit = unit  # e.g. "kg", "L"
        self.unit_cost = unit_cost  # €/unit
        self.stock_quantity = stock_quantity  # how much is available in stock
        self.prep_time = prep_time  # hours needed for preparation / preprocessing

        # --- optional metadata ---
        self.supplier = supplier
        self.shelf_life_days = shelf_life_days
        self.category = category

    def __repr__(self) -> str:
        return f"RawMaterial(name={self.name}, cost={self.unit_cost:.2f}€/ {self.unit})"

    def describe(self) -> str:
        """
        Returns a human-readable description of the raw material.
        """
        return (
            f"Raw material: {self.name}\n"
            f"  - Category: {self.category or 'n/a'}\n"
            f"  - Supplier: {self.supplier or 'n/a'}\n"
            f"  - Cost: {self.unit_cost:.2f} €/ {self.unit}\n"
            f"  - In stock: {self.stock_quantity} {self.unit}\n"
            f"  - Preparation time: {self.prep_time} h\n"
        )
