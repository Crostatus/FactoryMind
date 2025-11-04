from src.entities.machine_recipe_setting import MachineRecipeSetting
from src.entities.raw_material import RawMaterial


class Machine:
    def __init__(
        self,
        name: str,
        hourly_cost: float,
        nominal_power_kw: float,
        base_efficiency: float,
        shifts_per_day: int,
        hours_per_shift: int,
        power_profile: dict[str, float] | None = None,
        internal_storage_capacity: dict[str, float] | None = None,  # now supports per-material or per-unit
        material_loading_rate: dict[str, float] | None = None,
    ):
        self.name = name
        self.hourly_cost = hourly_cost
        self.nominal_power_kw = nominal_power_kw
        self.base_efficiency = base_efficiency
        self.shifts_per_day = shifts_per_day
        self.hours_per_shift = hours_per_shift
        self.power_profile = power_profile or {"idle": 0.1, "load": 0.6, "produce": 1.0}
        self.internal_storage_capacity = internal_storage_capacity or {}
        self.material_loading_rate = material_loading_rate or {}
        self.settings: list["MachineRecipeSetting"] = []

    # --- hybrid loading logic ---
    def loading_time(self, quantity: float, material: "RawMaterial") -> float:
        rate = 0.0
        if material.name in self.material_loading_rate:
            rate = self.material_loading_rate[material.name]
        elif material.unit.value in self.material_loading_rate:
            rate = self.material_loading_rate[material.unit.value]
        return quantity * rate

    # --- hybrid storage logic ---
    def storage_capacity_for(self, material: "RawMaterial") -> float | None:
        """
        Returns the maximum storable quantity for the given material.
        Priority:
            1. specific material
            2. unit fallback
            3. None if undefined
        """
        if material.name in self.internal_storage_capacity:
            return self.internal_storage_capacity[material.name]
        elif material.unit.value in self.internal_storage_capacity:
            return self.internal_storage_capacity[material.unit.value]
        return None

    def describe(self) -> str:
        lines = [
            f"Machine: {self.name}",
            f"  - Nominal power: {self.nominal_power_kw:.2f} kW",
            f"  - Efficiency: {self.base_efficiency*100:.1f}%",
            f"  - Hourly cost: {self.hourly_cost:.2f} €/h",
        ]
        if self.internal_storage_capacity:
            lines.append("  - Storage capacity:")
            for key, value in self.internal_storage_capacity.items():
                lines.append(f"      {key}: {value:.1f}")
        if self.material_loading_rate:
            lines.append("  - Loading rates:")
            for key, value in self.material_loading_rate.items():
                lines.append(f"      {key}: {value:.2f} s/unit")
        return "\n".join(lines)
