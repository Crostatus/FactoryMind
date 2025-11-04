from math import ceil
from src.entities.units import Unit

class MachineRecipeSetting:
    """
    Describes how a specific machine behaves for a given recipe.
    All time values are expressed in SECONDS.
    """

    def __init__(
        self,
        recipe,
        unit_time: float,        # s per output unit
        setup_time: float,       # s for startup/changeover
        yield_rate: float,
        batch_capacity: float,
        batch_unit: Unit,
        batch_label: str = "batch",
        energy_factor: float = 1.0,  # recipe-specific load factor
    ):
        self.recipe = recipe
        self.unit_time = unit_time
        self.setup_time = setup_time
        self.yield_rate = yield_rate
        self.batch_capacity = batch_capacity
        self.batch_unit = batch_unit
        self.batch_label = batch_label
        self.energy_factor = energy_factor
        self.machine: "Machine" | None = None  # dynamically linked

    def effective_batch_time(self) -> float:
        return (self.batch_capacity * self.unit_time) / self.yield_rate

    def total_batch_time(self, loading_time: float = 0.0) -> float:
        """Setup + load + production."""
        return self.setup_time + loading_time + self.effective_batch_time()

    def energy_consumption_batch(self, loading_time: float = 0.0) -> float:
        """
        Calculates total energy (kWh) for one batch based on machine state profile
        and recipe-specific factor.
        """
        if not self.machine:
            raise ValueError("Setting must be linked to a Machine.")

        # durations per state (s)
        durations = {
            "idle": 0.0,
            "load": loading_time,
            "produce": self.effective_batch_time(),
        }
        # base energy from machine power profile
        base_energy = self.machine.energy_use(durations)
        return base_energy * self.energy_factor

    def __repr__(self):
        return f"<Setting {self.recipe.name} ({self.batch_capacity}{self.batch_unit.value}/{self.batch_label})>"
