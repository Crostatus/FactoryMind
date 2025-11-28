from math import ceil
from src.entities.machine import Machine
from src.entities.recipe import Recipe
from src.entities.units import Unit

def evaluate_recipe_time(machine: Machine, recipeName: str, amount_needed: float) -> float:
    recipe_setting = machine.get_setting_for_recipe_from_name(recipeName)
    recipe = recipe_setting.recipe
    
    if not recipe_setting:
        raise ValueError(f"Machine '{machine.name}' does not support recipe '{recipe.name}'")
    if not recipe:
        raise ValueError(f"Machine '{machine.name}' does not support recipe '{recipe.name}'")
    
    time = recipe_setting.setup_time
    
    amount_needed = amount_needed / recipe_setting.yield_rate
    if(recipe.output_unit == Unit.PIECE):
        amount_needed = ceil(amount_needed)

    # Calculate the amount of output needed
    how_many_times_recipe = ceil(amount_needed / recipe.output_quantity)
    
    # Calculate total production time
    time += how_many_times_recipe * recipe_setting.time

    # Calculate total loading time
    loading_time = sum(
        (quantity * how_many_times_recipe) / machine.get_loading_rate(material)
        for material, quantity in recipe.ingredients.items()
    )
    time += loading_time

    # Calculate total unloading time
    unloading_times = ceil(amount_needed / recipe_setting.capacity)
    time += unloading_times * recipe_setting.unload_time

    return time
    