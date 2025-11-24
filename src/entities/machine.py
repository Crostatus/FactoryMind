from __future__ import annotations
from ast import Dict
from typing import Optional
from src.entities.machine_recipe_setting import MachineRecipeSetting
from src.entities.power_profile import MachinePowerProfile
from src.entities.raw_material import RawMaterial
from src.entities.units import Unit, str_quant, str_quant_over_quant


SECONDS_PER_HOUR = 3600

class LoadingRate:
    def __init__(self, rate: float, quant: Unit, over_quant: Unit):
        self.rate = rate
        self.quant = quant
        self.over_quant = over_quant
    
    def __repr__(self) -> str:
        return f"{str_quant_over_quant(self.rate, self.quant, self.over_quant)}"

class MachineLoadingRates:
    def __init__(
        self,
        by_unit: Optional[Dict[Unit, LoadingRate]] = None,
        by_material: Optional[Dict[str, LoadingRate]] = None
    ):
        self.by_unit = by_unit or {}
        self.by_material = by_material or {}
        

class MachineStorage:
    """Represent machine storage limits."""
    def __init__(
        self,
        by_unit: Optional[Dict[Unit, float]] = None,
        by_material: Optional[Dict[str, float]] = None
    ):
        self.by_unit = by_unit or {}
        self.by_material = by_material or {}

class PowerProfile:
    def __init__(
        self, profile: Optional[dict[MachinePowerProfile, float]] = None
    ):
        self.items = profile or {MachinePowerProfile.IDLE: 1.0, MachinePowerProfile.LOADING: 1.0, MachinePowerProfile.PRODUCE: 1.0}
        for conf in [u for u in MachinePowerProfile]:
            if conf not in self.items:
                self.items[conf] = 1.0        # Defaults to 1 => just nominal power

class Machine:
    """
    Represents a production machine or line with physical and operational characteristics.
    All time values are expressed in SECONDS.
    Energy model: nominal power (kW) x state profile factor x time.
    """

    def __init__(
        self,
        name: str,
        hourly_cost: float,
        nominal_power_kw: float,
        base_efficiency: float,
        shifts_per_day: int,
        hours_per_shift: int,
        power_profile: dict[MachinePowerProfile, float] | None = None,
        storage: Optional[MachineStorage] = None,        
        loading_rates: Optional[MachineLoadingRates] = None,
    ):
        self.name = name
        self.hourly_cost = hourly_cost
        self.nominal_power_kw = nominal_power_kw
        self.base_efficiency = base_efficiency
        self.shifts_per_day = shifts_per_day
        self.hours_per_shift = hours_per_shift
        self.power_profile = PowerProfile(power_profile)        
        self.storage = storage or MachineStorage()        
        self.loading_rates = loading_rates or MachineLoadingRates()
        self.settings: list["MachineRecipeSetting"] = []  # collegamenti ricette -> macchina

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
            1️ specifica per materiale
            2️ fallback per unità (es. 'kg', 'L', 'piece')
            3️ default = 0
        """
        rate = 0.0
        if material.name in self.loading_rates.by_material:
            rate = self.loading_rates.by_material[material.name].rate
        elif material.unit in self.loading_rates.by_unit:
            rate = self.loading_rates.by_unit[material.unit].rate
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
        if material.name in self.storage.by_material:
            return self.storage.by_material[material.name]
        elif material.unit.value in self.storage.by_unit:
            return self.storage.by_unit[material.unit.value]
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
            factor = self.power_profile.items.get(state, 0)
            energy += self.nominal_power_kw * factor * (seconds / SECONDS_PER_HOUR)
        return energy

    def __repr__(self) -> str:
        lines = [
            f"Machine: '{self.name}'",
            f"  - Nominal power: {str_quant(self.nominal_power_kw, Unit.KILOWATT)}",
            f"  - Efficiency:    {str_quant(self.base_efficiency * 100, Unit.PERCENT)}",
            f"  - Hourly cost:   {str_quant_over_quant(self.hourly_cost, Unit.EURO, Unit.HOUR)}",            
            f"  - Shifts/day:    {self.shifts_per_day} x {str_quant(self.hours_per_shift, Unit.HOUR)}",            
            f"  - Power profile:",
        ]
        for k, v in self.power_profile.items.items():            
            lines.append(f"      {k}: {str_quant(v*100, Unit.PERCENT)} of nominal")
     
        lines.append("  - Loading rates:")
        for key, value in self.loading_rates.by_unit.items():
             lines.append(f"      {key}: {value}")
        for key, value in self.loading_rates.by_material.items():
             lines.append(f"      {key}: {value}")

        lines.append("  - Storage capacity:")
        for key, value in self.storage.by_unit.items():
            lines.append(f"      {str_quant(value, key)}")

        for key, value in self.storage.by_material.items():
            lines.append(f"      {key}: {value}")
        

        return "\n".join(lines)
