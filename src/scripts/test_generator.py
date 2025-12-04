"""
Quick test script for the FactoryDataGenerator
"""
from src.generator.factory_data_generator import FactoryDataGenerator
import json

def main():
    # Create generator
    generator = FactoryDataGenerator()
    
    # Generate materials
    materials = generator.generate_materials(count=10)
    
    # Print materials
    print("\n" + "="*60)
    print("GENERATED MATERIALS")
    print("="*60)
    print(json.dumps(materials, indent=2, ensure_ascii=False))
    
    # Verify piece units have integer quantities for materials
    print("\n" + "="*60)
    print("MATERIALS VALIDATION CHECK")
    print("="*60)
    for mat in materials:
        if mat["unit"] == "piece":
            is_int = isinstance(mat["stock_quantity"], int)
            print(f"✓ {mat['name']} (piece): stock_quantity={mat['stock_quantity']} is_int={is_int}")
    
    # Generate recipes using the materials
    recipes = generator.generate_recipes(materials, count=7)
    
    # Print recipes
    print("\n" + "="*60)
    print("GENERATED RECIPES")
    print("="*60)
    print(json.dumps(recipes, indent=2, ensure_ascii=False))
    
    # Verify piece units have integer quantities for recipes
    print("\n" + "="*60)
    print("RECIPES VALIDATION CHECK")
    print("="*60)
    for recipe in recipes:
        print(f"\n{recipe['name']}:")
        print(f"  - Output: {recipe['output_quantity']} {recipe['output_unit']}")
        
        # Check output quantity
        if recipe["output_unit"] == "piece":
            is_int = isinstance(recipe["output_quantity"], int)
            print(f"  - Output quantity is_int={is_int} ✓" if is_int else f"  - Output quantity is_int={is_int} ✗")
        
        # Check ingredient quantities
        for ing_name, ing_qty in recipe["ingredients"].items():
            # Find material unit
            mat_unit = next((m["unit"] for m in materials if m["name"] == ing_name), None)
            if mat_unit == "piece":
                is_int = isinstance(ing_qty, int)
                status = "✓" if is_int else "✗"
                print(f"  - Ingredient {ing_name} ({mat_unit}): qty={ing_qty} is_int={is_int} {status}")
    
    # Generate machines using the materials
    machines = generator.generate_machines(materials, count=4)
    
    # Print machines
    print("\n" + "="*60)
    print("GENERATED MACHINES")
    print("="*60)
    print(json.dumps(machines, indent=2, ensure_ascii=False))
    
    # Verify piece units have integer loading rates
    print("\n" + "="*60)
    print("MACHINES VALIDATION CHECK")
    print("="*60)
    for machine in machines:
        print(f"\n{machine['name']}:")
        print(f"  - Power: {machine['nominal_power_kw']} kW")
        print(f"  - Power Profile: idle={machine['power_profile']['idle']}, "
              f"loading={machine['power_profile']['loading']}, "
              f"produce={machine['power_profile']['produce']}")
        print(f"  - Loading Rates:")
        
        for key, rate in machine["material_loading_rate"].items():
            # Check if it's a unit or material name
            is_piece_unit = (key == "piece")
            
            # If it's a material name, check the material's unit
            mat_unit = None
            if not is_piece_unit and materials:
                mat = next((m for m in materials if m["name"] == key), None)
                if mat:
                    mat_unit = mat["unit"]
                    is_piece_unit = (mat_unit == "piece")
            
            if is_piece_unit:
                is_int = isinstance(rate, int)
                status = "✓" if is_int else "✗"
                unit_info = f" ({mat_unit})" if mat_unit else ""
                print(f"    - {key}{unit_info}: rate={rate} is_int={is_int} {status}")
            else:
                print(f"    - {key}: rate={rate}")
    
    # Generate machine recipe settings
    settings = generator.generate_machine_recipe_settings(machines, recipes)
    
    # Print settings
    print("\n" + "="*60)
    print("GENERATED MACHINE RECIPE SETTINGS")
    print("="*60)
    print(json.dumps(settings, indent=2, ensure_ascii=False))
    
    # Verify coverage and piece unit constraints
    print("\n" + "="*60)
    print("SETTINGS VALIDATION CHECK")
    print("="*60)
    
    # Check that all recipes are covered
    covered_recipes = set(s["recipe"] for s in settings)
    all_recipes = set(r["name"] for r in recipes)
    
    print(f"\nRecipe Coverage:")
    print(f"  - Total recipes: {len(all_recipes)}")
    print(f"  - Covered recipes: {len(covered_recipes)}")
    print(f"  - All covered: {'✓' if covered_recipes == all_recipes else '✗'}")
    
    if covered_recipes != all_recipes:
        missing = all_recipes - covered_recipes
        print(f"  - Missing recipes: {missing}")
    
    # Check piece unit constraints for capacity
    print(f"\nCapacity Validation (piece units):")
    for setting in settings:
        recipe = next((r for r in recipes if r["name"] == setting["recipe"]), None)
        if recipe and recipe["output_unit"] == "piece":
            is_int = isinstance(setting["capacity"], int)
            status = "✓" if is_int else "✗"
            print(f"  - {setting['recipe']} on {setting['machine']}: capacity={setting['capacity']} is_int={is_int} {status}")

if __name__ == "__main__":
    main()

