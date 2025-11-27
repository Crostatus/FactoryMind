from src.entities.machine import Machine
from src.entities.machine_recipe_setting import MachineRecipeSetting
from src.entities.recipe import Recipe
from src.entities.units import Unit

def evaluate_recipe_time(machine: Machine, recipe_setting: MachineRecipeSetting, amount_needed: float) -> float:
    time = recipe_setting.setup_time
    
    amount_needed = amount_needed / recipe_setting.yield_rate

    # Calculate the amount of output needed
    how_many_times_recipe = ceil(amount_needed / recipe_setting.recipe.output_quantity)
    
    # Calculate total production time
    time += how_many_times_recipe * recipe_setting.time

    # Calculate total loading time
    loading_time = sum(
        (quantity * how_many_times_recipe) / machine.get_loading_rate(recipe_setting.recipe.materials[material])
        for material, quantity in recipe_setting.recipe.ingredients.items()
    )
    time += loading_time

    # Calculate total unloading time
    unloading_times = ceil(amount_needed / recipe_setting.capacity)
    time += unloading_times * recipe_setting.unload_time

    return time
    