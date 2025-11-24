from src.entities.units import Unit, str_quant, str_quant_over_quant

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
    ):
        # --- primary attributes ---
        self.name = name  # e.g. "Flour 00"
        self.unit = unit  # e.g. "kg", "L"
        self.unit_cost = unit_cost  # €/unit
        self.stock_quantity = stock_quantity  # how much is available in stock
        self.prep_time = prep_time  # seconds needed for preparation / preprocessing

    def __repr__(self) -> str:                        
        return f"Material '{self.name}' (stock={str_quant(self.stock_quantity, self.unit)} | cost={str_quant_over_quant(self.unit_cost, Unit.EURO, self.unit)} | prep_time={str_quant(self.prep_time, Unit.SECONDS)})"

    def describe(self) -> str:
        """
        Returns a human-readable description of the raw material.
        """
        return (
            f"Raw material: {self.name}\n"
            f"  - Category:         {self.category or 'n/a'}\n"
            f"  - Supplier:         {self.supplier or 'n/a'}\n"
            f"  - Cost:             {str_quant_over_quant(self.unit_cost, Unit.EURO, self.unit)}\n"        
            f"  - In stock:         {str_quant(self.stock_quantity, self.unit)}\n"
            f"  - Preparation time: {str_quant(self.prep_time, Unit.SECONDS)} s\n"
            f"  - Preparation time: {self.prep_time} s\n"
        )
