from __future__ import annotations
from src.entities.machine_recipe_setting import MachineRecipeSetting
from src.entities.raw_material import RawMaterial
from src.entities.units import Unit


SECONDS_PER_HOUR = 3600


class Machine:
    """
    Represents a production machine or line with physical and operational characteristics.
    All time values are expressed in SECONDS.
    Energy model: nominal power (kW) × state profile factor × time.
    """

    def __init__(
        self,
        name: str,
        hourly_cost: float,
        nominal_power_kw: float,
        base_efficiency: float,
        shifts_per_day: int,
        hours_per_shift: int,
        power_profile: dict[str, float] | None = None,
        internal_storage_capacity: dict[str, float] | None = None,  # per unità o materiale
        material_loading_rate: dict[str, float] | None = None,      # per unità o materiale
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
        self.settings: list["MachineRecipeSetting"] = []  # collegamenti ricette → macchina

    # --- associations --------------------------------------------------------
    def add_setting(self, setting: "MachineRecipeSetting"):
        """Collega una configurazione ricetta–macchina."""
        setting.machine = self
        self.settings.append(setting)

    def supported_recipes(self):
        """Ritorna la lista di ricette supportate."""
        return [s.recipe for s in self.settings]

    # --- hybrid loading logic ------------------------------------------------
    def loading_time(self, quantity: float, material: "RawMaterial") -> float:
        """
        Calcola il tempo di caricamento in secondi per una certa quantità di materiale.
        Priorità:
            1️⃣ specifica per materiale
            2️⃣ fallback per unità (es. 'kg', 'L', 'piece')
            3️⃣ default = 0
        """
        rate = 0.0
        if material.name in self.material_loading_rate:
            rate = self.material_loading_rate[material.name]
        elif material.unit.value in self.material_loading_rate:
            rate = self.material_loading_rate[material.unit.value]
        return quantity * rate

    # --- hybrid storage logic ------------------------------------------------
    def storage_capacity_for(self, material: "RawMaterial") -> float | None:
        """
        Restituisce la quantità massima stoccabile per il materiale.
        Priorità:
            1️⃣ specifica per materiale
            2️⃣ fallback per unità
            3️⃣ None se non definita
        """
        if material.name in self.internal_storage_capacity:
            return self.internal_storage_capacity[material.name]
        elif material.unit.value in self.internal_storage_capacity:
            return self.internal_storage_capacity[material.unit.value]
        return None

    # --- derived metrics -----------------------------------------------------
    def total_available_time(self) -> float:
        """Tempo totale giornaliero disponibile (in secondi)."""
        return self.shifts_per_day * self.hours_per_shift * SECONDS_PER_HOUR

    def energy_use(self, state_durations: dict[str, float]) -> float:
        """
        Calcola l'energia totale (in kWh) in base ai tempi di stato:
        state_durations = {'idle': s, 'load': s, 'produce': s}
        """
        energy = 0.0
        for state, seconds in state_durations.items():
            factor = self.power_profile.get(state, 0)
            energy += self.nominal_power_kw * factor * (seconds / SECONDS_PER_HOUR)
        return energy

    # --- debug ---------------------------------------------------------------
    def __repr__(self):
        return f"<Machine {self.name}, {self.nominal_power_kw:.1f}kW nominal>"

    def describe(self) -> str:
        lines = [
            f"Machine: {self.name}",
            f"  - Nominal power: {self.nominal_power_kw:.2f} kW",
            f"  - Efficiency: {self.base_efficiency*100:.1f}%",
            f"  - Hourly cost: {self.hourly_cost:.2f} €/h",
            f"  - Shifts/day: {self.shifts_per_day} × {self.hours_per_shift}h",
            f"  - Power profile:",
        ]
        for k, v in self.power_profile.items():
            lines.append(f"      {k}: {v*100:.0f}% of nominal")

        if self.internal_storage_capacity:
            lines.append("  - Storage capacity:")
            for key, value in self.internal_storage_capacity.items():
                lines.append(f"      {key}: {value:.1f}")

        if self.material_loading_rate:
            lines.append("  - Loading rates:")
            for key, value in self.material_loading_rate.items():
                lines.append(f"      {key}: {value:.2f} s/unit")

        return "\n".join(lines)
