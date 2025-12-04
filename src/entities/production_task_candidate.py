from __future__ import annotations
from math import ceil
from src.entities.machine import Machine
from src.entities.power_profile import MachinePowerProfile
from src.entities.recipe import Recipe
from src.entities.units import Unit, str_quant
from src.utils.logging import log

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
        
        self.how_many_times_recipe = ceil(self.actual_quantity / self.recipe.output_quantity)      
        
        self.idle_time, self.loading_time, self.producing_time = self._evaluate_recipe_total_time()
        
        # Calculate base estimated time (actual working time)
        base_estimated_time = self.idle_time + self.loading_time + self.producing_time
        
        # Adjust for machine's max working hours per day
        # If machine works less than 24h/day, we need to account for non-working hours
        work_hours = base_estimated_time / 3600.0  # Convert seconds to hours
        
        # Calculate how many days are needed
        days_needed = ceil(work_hours / self.machine.max_working_hours_per_day)
        
        # Calculate non-working hours to add (all days except the last one)
        non_working_hours_per_day = 24 - self.machine.max_working_hours_per_day
        total_non_working_hours = (days_needed - 1) * non_working_hours_per_day
        
        # Estimated time includes work time + non-working hours
        self.estimated_time = base_estimated_time + (total_non_working_hours * 3600)
        
        self.energy_consumption_per_profiles = {
            MachinePowerProfile.IDLE: self.idle_time * self.machine.nominal_power_kw * self.machine.power_profile.items[MachinePowerProfile.IDLE],
            MachinePowerProfile.LOADING: self.loading_time * self.machine.nominal_power_kw * self.machine.power_profile.items[MachinePowerProfile.LOADING],
            MachinePowerProfile.PRODUCE: self.producing_time * self.machine.nominal_power_kw * self.machine.power_profile.items[MachinePowerProfile.PRODUCE]
        }
        self.total_energy_consumption = sum(self.energy_consumption_per_profiles.values())


    def __repr__(self) -> str:
        return (
            f"Candidate '{self.machine.name}' => {str_quant(self.actual_quantity, self.recipe.output_unit)} '{self.recipe.name}' in {self.estimated_time:.2f}s"
        )        

    def _evaluate_recipe_total_time(self) -> float:                        
                    
        idle_time = self.recipe_settings.setup_time        
        
        # Calculate total production time
        producing_time = self.how_many_times_recipe * self.recipe_settings.time        

        # Calculate total loading time
        loading_time = sum(
            ((quantity * self.how_many_times_recipe) / self.machine.get_loading_rate(material))
            for material, quantity in self.recipe.ingredients.items()
        )

        # Calculate total unloading time
        unloading_times = ceil(self.actual_quantity / self.recipe_settings.capacity)
        idle_time += unloading_times * self.recipe_settings.unload_time

        return (
            idle_time, loading_time, producing_time
        )
    
    def _evaluate_recipe_total_ingredients(self) -> dict:
        """
        Calculate the total quantity required for each ingredient.
        
        Returns:
            Dictionary mapping RawMaterial total quantity needed
        """
        total_ingredients = {}
        
        for material, qty_per_output in self.recipe.ingredients.items():
            total_needed = qty_per_output * self.how_many_times_recipe
            total_ingredients[material] = total_needed

        return total_ingredients

    def is_valid(self) -> bool:
        """
        Check if the candidate can be executed given the available materials.
        """
        
        total_ingredients = self._evaluate_recipe_total_ingredients()
        
        for material, quantity in total_ingredients.items():
            if material.stock_quantity < quantity:
                log.trace(f"Not enough material '{material.name}' for recipe '{self.recipe.name}'. Needed: {quantity}, Available: {material.stock_quantity}")
                return False
            
        return True