from math import ceil
from src.entities.units import Unit
from src.entities.recipe import Recipe

class MachineRecipeSetting:
    """
    Describes how a specific machine behaves for a given recipe.
    All time values are expressed in SECONDS.
    """

    def __init__(
        self,
        recipe: Recipe,
        time: float,        # s per output unit
        setup_time: float,       # s for startup/changeover
        unload_time: float, # s for unloading batch
        yield_rate: float,
        capacity: float,        
        energy_factor: float = 1.0,  # recipe-specific load factor
    ):
        self.recipe = recipe
        self.time = time
        self.setup_time = setup_time
        self.unload_time = unload_time
        self.yield_rate = yield_rate
        self.capacity = capacity
        self.energy_factor = energy_factor
        self.machine: "Machine" | None = None  # dynamically linked

    def __repr__(self):
        from src.entities.units import str_quant, str_quant_over_quant
        lines = [
            f"Setting for recipe '{self.recipe.name}'",
            f"  - Batch capacity: {str_quant(self.capacity, self.recipe.output_unit)}",
            f"  - Unit time:      {str_quant(self.time, Unit.SECONDS)} per {self.recipe.output_unit.value}",
            f"  - Setup time:     {str_quant(self.setup_time, Unit.SECONDS)}",
            f"  - Unload time:    {str_quant(self.unload_time, Unit.SECONDS)}",
            f"  - Yield rate:     {str_quant(self.yield_rate * 100, Unit.PERCENT)}",
            f"  - Energy factor:  {str_quant(self.energy_factor * 100, Unit.PERCENT)} of nominal",
        ]
        return "\n".join(lines)
