from __future__ import annotations
from math import ceil
from src.entities.machine import Machine
from src.entities.power_profile import MachinePowerProfile
from src.entities.recipe import Recipe
from src.entities.units import Unit, str_quant

class ProductionTaskCandidate:
    """
    Represents a candidate machine for a specific production task (recipe + quantity).
    Contains the calculated estimated time.
    """
    def __init__(
        self,
        machine: Machine,
        recipe: Recipe,
        requested_quantity: float,        
    ):
        self.machine = machine
        self.recipe = recipe
        self.requested_quantity = requested_quantity
        self.recipe_settings = machine.get_setting_for_recipe_from_name(recipe.name)
        
        if not self.recipe_settings:
            raise ValueError(f"Machine '{machine.name}' does not support recipe '{recipe.name}'")
        if not recipe:
            raise ValueError(f"Machine '{machine.name}' does not support recipe '{recipe.name}'")
        
        self.actual_quantity = requested_quantity / self.recipe_settings.yield_rate
        if(recipe.output_unit == Unit.PIECE):
            self.actual_quantity = ceil(self.actual_quantity)
                
        self.idle_time, self.loading_time, self.producing_time = self._evaluate_recipe_total_time()
        self.estimated_time = self.idle_time + self.loading_time + self.producing_time
        
        self.energy_consumption_per_profiles = {
            MachinePowerProfile.IDLE: self.idle_time * machine.nominal_power_kw * machine.power_profile.items[MachinePowerProfile.IDLE],
            MachinePowerProfile.LOADING: self.loading_time * machine.nominal_power_kw * machine.power_profile.items[MachinePowerProfile.LOADING],
            MachinePowerProfile.PRODUCE: self.producing_time * machine.nominal_power_kw * machine.power_profile.items[MachinePowerProfile.PRODUCE]
        }
        self.total_energy_consumption = sum(self.energy_consumption_per_profiles.values())


    def __repr__(self) -> str:
        return (
            f"Candidate '{self.machine.name}' => {str_quant(self.actual_quantity, self.recipe.output_unit)} '{self.recipe.name}' in {self.estimated_time:.2f}s"
        )        

    def _evaluate_recipe_total_time(self) -> float:                        
                    
        idle_time = self.recipe_settings.setup_time        
        
        # Calculate the amount of output needed
        how_many_times_recipe = ceil(self.actual_quantity / self.recipe.output_quantity)
        
        # Calculate total production time
        producing_time = how_many_times_recipe * self.recipe_settings.time        

        # Calculate total loading time
        loading_time = sum(
            ((quantity * how_many_times_recipe) / self.machine.get_loading_rate(material)) + material.prep_time
            for material, quantity in self.recipe.ingredients.items()
        )

        # Calculate total unloading time
        unloading_times = ceil(self.actual_quantity / self.recipe_settings.capacity)
        idle_time += unloading_times * self.recipe_settings.unload_time

        return (
            idle_time, loading_time, producing_time
        )