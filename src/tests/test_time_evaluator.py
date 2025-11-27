import pytest
from src.entities.machine import Machine, MachineLoadingRates, LoadingRate
from src.entities.recipe import Recipe
from src.entities.machine_recipe_setting import MachineRecipeSetting
from src.entities.raw_material import RawMaterial
from src.entities.units import Unit
from src.utils.time_evaluator import evaluate_recipe_time

def test_evaluate_recipe_time_with_loading_time():
    # 1. Setup Materials
    flour = RawMaterial(name="Flour", unit=Unit.KILOGRAM, unit_cost=1.0, stock_quantity=1000.0, prep_time=0.0)
    sugar = RawMaterial(name="Sugar", unit=Unit.KILOGRAM, unit_cost=2.0, stock_quantity=1000.0, prep_time=0.0)

    # 2. Setup Recipe
    # Produces 100 PIECEs using 50kg Flour and 20kg Sugar
    recipe = Recipe(
        name="Cookie",
        ingredients={flour: 50.0, sugar: 20.0},
        output_quantity=100.0,
        output_unit=Unit.PIECE
    )

    # 3. Setup Machine with Loading Rates
    # Loads 10 kg/s (generic by unit)
    loading_rates = MachineLoadingRates(
        by_unit={Unit.KILOGRAM: LoadingRate(rate=10.0, quant=Unit.KILOGRAM, over_quant=Unit.SECONDS)}
    )
    machine = Machine(name="Oven", nominal_power_kw=10.0, loading_rates=loading_rates)

    # 4. Setup MachineRecipeSetting
    # Capacity: 100 PIECEs per batch
    # Time: 1s per PIECE (processing) -> 100s per batch
    # Setup: 60s
    # Unload: 30s
    setting = MachineRecipeSetting(
        recipe=recipe,
        time=1.0,
        setup_time=60.0,
        unload_time=30.0,
        yield_rate=1.0,
        capacity=100.0
    )
    machine.add_setting(setting)

    # 5. Evaluate Time for 200 PIECEs (2 Batches)
    # Expected Calculation:
    # - Num Batches: 200 / 100 = 2
    # - Total Ingredients:
    #   - Flour: 50 * 2 = 100 kg
    #   - Sugar: 20 * 2 = 40 kg
    #   - Total Weight: 140 kg
    # - Loading Time: 
    #   - Flour: 100 kg / 10 kg/s = 10 s
    #   - Sugar: 40 kg / 10 kg/s = 4 s
    #   - Total Loading: 14 s
    # - Processing Time: 200 pieces * 1 s/piece = 200 s
    # - Setup Time: 60 s
    # - Unload Time: 2 batches * 30 s/batch = 60 s
    # - Total Time: 14 + 200 + 60 + 60 = 334 s

    total_time = evaluate_recipe_time(machine, setting, recipe, amount_needed=200.0)
    
    assert total_time == 334.0
