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
        nominal_power_kw: float,
        power_profile: dict[MachinePowerProfile, float] | None = None,        
        loading_rates: Optional[MachineLoadingRates] = None,
    ):
        self.name = name
        self.nominal_power_kw = nominal_power_kw
        self.power_profile = PowerProfile(power_profile)        
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

    def get_setting_for_recipe(self, recipe: "Recipe") -> "MachineRecipeSetting" | None:
        """Returns the setting for a given recipe, or None if not supported."""
        for setting in self.settings:
            if setting.recipe == recipe:
                return setting
        return None    
    
    def get_loading_rate(self, material: "RawMaterial") -> float:
        """Returns the loading rate for a specific material (unit/s)."""
        # 1. Check specific material rate
        if material.name in self.loading_rates.by_material:
            rate_obj = self.loading_rates.by_material[material.name]
            return rate_obj.rate
            
        # 2. Check generic unit rate
        if material.unit in self.loading_rates.by_unit:
            rate_obj = self.loading_rates.by_unit[material.unit]
            return rate_obj.rate
            
        # Default fallback (should ideally not happen if data is correct)
        # Returning 1.0 to avoid division by zero, but logging would be better
        return 1.0

    def __repr__(self) -> str:
        lines = [
            f"Machine: '{self.name}'",
            f"  - Nominal power: {str_quant(self.nominal_power_kw, Unit.KILOWATT)}",
            f"  - Power profile:",
        ]
        for k, v in self.power_profile.items.items():            
            lines.append(f"      {k}: {str_quant(v*100, Unit.PERCENT)} of nominal")
     
        lines.append("  - Loading rates:")
        for key, value in self.loading_rates.by_unit.items():
             lines.append(f"      {key}: {value}")
        for key, value in self.loading_rates.by_material.items():
             lines.append(f"      {key}: {value}")                

        return "\n".join(lines)
