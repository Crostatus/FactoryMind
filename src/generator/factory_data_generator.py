import json
import random
from pathlib import Path
from src.utils.logging import log
from src.entities.units import Unit


class FactoryDataGenerator:
    """
    Handles generation of factory data to JSON files.
    """

    def __init__(
        self, 
        output_dir: str = "src/data/generated",
        materials_file: str = "materials.json",
        recipes_file: str = "recipes.json",
        machines_file: str = "machines.json",
        machine_recipe_settings_file: str = "machines_recipe_settings.json",
        orders_file: str = "orders.json"
    ):
        """
        Initialize the data generator with output paths.
        
        Args:
            output_dir: Directory where generated files will be written
            materials_file: Name of the materials JSON file
            recipes_file: Name of the recipes JSON file
            machines_file: Name of the machines JSON file
            machine_recipe_settings_file: Name of the machine recipe settings JSON file
            orders_file: Name of the orders JSON file
        """
        self.output_dir = Path(output_dir)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Resource file paths
        self.materials_path = self.output_dir / materials_file
        self.recipes_path = self.output_dir / recipes_file
        self.machines_path = self.output_dir / machines_file
        self.machine_recipe_settings_path = self.output_dir / machine_recipe_settings_file
        self.orders_path = self.output_dir / orders_file
        
        log.info(f"Data generator initialized with output directory: {self.output_dir}")
    
    def generate_materials(self, count: int = None) -> list[dict]:
        """
        Generate a list of N random materials.
        
        Args:
            count: Number of materials to generate. If None, chooses random between 5 and 15.
            
        Returns:
            List of material dictionaries ready to be saved as JSON
        """
        if count is None:
            count = random.randint(5, 15)
        
        log.info(f"Generating {count} random materials...")
        
        # Base material names for variety
        material_types = [
            "Flour", "Sugar", "Butter", "Eggs", "Milk", "Cream", "Chocolate", 
            "Vanilla", "Salt", "Yeast", "Honey", "Oil", "Cocoa", "Almonds",
            "Walnuts", "Hazelnuts", "Cinnamon", "Nutmeg", "Baking Powder",
            "Cornstarch", "Gelatin", "Raisins", "Coconut", "Lemon", "Orange"
        ]
        
        # Material variants
        variants = ["00", "Type 1", "Type 2", "Premium", "Organic", "Extra", "Fine", "Fresh"]
        
        # Valid units for food materials (not kilowatt, euro, percent, hour, seconds!)
        valid_material_units = [
            Unit.GRAM.value, 
            Unit.KILOGRAM.value, 
            Unit.LITER.value, 
            Unit.MILLILITER.value, 
            Unit.PIECE.value
        ]
        
        materials = []
        used_names = set()
        
        for i in range(count):
            # Generate unique name
            attempts = 0
            while attempts < 100:  # Prevent infinite loop
                base_name = random.choice(material_types)
                
                # Sometimes add variant
                if random.random() > 0.5:
                    variant = random.choice(variants)
                    name = f"{base_name} {variant}"
                else:
                    name = base_name
                
                if name not in used_names:
                    used_names.add(name)
                    break
                attempts += 1
            
            # Select unit (only valid material units)
            unit = random.choice(valid_material_units)
            
            # Generate cost (between 0.10 and 50.00 eur)
            unit_cost = round(random.uniform(0.10, 50.00), 2)
            
            # Generate stock quantity
            # If unit is piece, stock must be integer
            if unit == Unit.PIECE.value:
                stock_quantity = random.randint(50, 1000)
            else:
                stock_quantity = round(random.uniform(10.0, 1000.0), 2)
            
            material = {
                "name": name,
                "unit": unit,
                "unit_cost": unit_cost,
                "stock_quantity": stock_quantity
            }
            
            materials.append(material)
            log.trace(f"Generated material: {name} ({unit}, cost={unit_cost}, stock={stock_quantity})")
        
        log.success(f"Generated {len(materials)} materials")
        return materials
    
    def generate_recipes(self, materials: list[dict], count: int = None) -> list[dict]:
        """
        Generate a list of N random recipes using the provided materials.
        
        Args:
            materials: List of material dictionaries (must have 'name', 'unit' keys)
            count: Number of recipes to generate. If None, chooses random between 3 and 10.
            
        Returns:
            List of recipe dictionaries ready to be saved as JSON
        """
        if not materials:
            raise ValueError("Cannot generate recipes without materials")
        
        if count is None:
            count = random.randint(3, 10)
        
        log.info(f"Generating {count} random recipes from {len(materials)} materials...")
        
        # Recipe base names
        recipe_types = [
            "Biscuits", "Cookies", "Cake", "Bread", "Pastry", "Tart", "Pie",
            "Cream", "Dough", "Mix", "Batter", "Filling", "Frosting",
            "Muffins", "Brownies", "Cupcakes", "Rolls", "Croissants"
        ]
        
        # Recipe variants
        variants = [
            "Classic", "Premium", "Deluxe", "Traditional", "Homemade",
            "Special", "Artisan", "Gourmet", "Rustic", "Golden"
        ]
        
        # Create a map for quick unit lookup
        material_units = {mat["name"]: mat["unit"] for mat in materials}
        
        recipes = []
        used_names = set()
        
        for i in range(count):
            # Generate unique name
            attempts = 0
            while attempts < 100:
                base_name = random.choice(recipe_types)
                
                # Sometimes add variant
                if random.random() > 0.6:
                    variant = random.choice(variants)
                    name = f"{variant} {base_name}"
                else:
                    name = base_name
                
                if name not in used_names:
                    used_names.add(name)
                    break
                attempts += 1
            
            # Select 1 to 4 random ingredients
            num_ingredients = random.randint(1, 4)
            selected_materials = random.sample(materials, min(num_ingredients, len(materials)))
            
            # Generate ingredient quantities
            ingredients = {}
            for mat in selected_materials:
                mat_name = mat["name"]
                mat_unit = mat["unit"]
                
                # If material unit is piece, quantity must be integer
                if mat_unit == Unit.PIECE.value:
                    quantity = random.randint(1, 20)
                else:
                    quantity = round(random.uniform(0.1, 10.0), 2)
                
                ingredients[mat_name] = quantity
            
            # Generate output
            # Random output unit
            output_unit = random.choice([Unit.PIECE.value, Unit.KILOGRAM.value, Unit.LITER.value])
            
            # If output unit is piece, output_quantity must be integer
            if output_unit == Unit.PIECE.value:
                output_quantity = random.randint(10, 200)
            else:
                output_quantity = round(random.uniform(0.5, 20.0), 2)
            
            # Optional fields
            categories = ["Bakery", "Pastry", "Dessert", "Savory", "Preparation", "Base"]
            category = random.choice(categories) if random.random() > 0.3 else None
            
            recipe = {
                "name": name,
                "ingredients": ingredients,
                "output_quantity": output_quantity,
                "output_unit": output_unit
            }
            
            # Add optional fields if present
            if category:
                recipe["category"] = category
            
            recipes.append(recipe)
            log.trace(f"Generated recipe: {name} ({len(ingredients)} ingredients, output={output_quantity} {output_unit})")
        
        log.success(f"Generated {len(recipes)} recipes")
        return recipes
    
    def generate_machines(self, materials: list[dict] = None, count: int = None) -> list[dict]:
        """
        Generate a list of N random machines.
        
        Args:
            materials: Optional list of material dictionaries. If provided, some machines 
                      will have specific loading rates for these materials.
            count: Number of machines to generate. If None, chooses random between 2 and 5.
            
        Returns:
            List of machine dictionaries ready to be saved as JSON
        """
        if count is None:
            count = random.randint(2, 5)
        
        log.info(f"Generating {count} random machines...")
        
        # Machine base names
        machine_types = [
            "Mixer", "Oven", "Blender", "Processor", "Packaging Unit",
            "Cooler", "Heater", "Roller", "Extruder", "Cutter",
            "Slicer", "Grinder", "Press", "Line", "Station"
        ]
        
        # Machine variants
        variants = ["Pro", "3000", "X", "Ultra", "Max", "Plus", "Advanced", "Industrial"]
        suffixes = ["A", "B", "1", "2", "Alpha", "Beta"]
        
        machines = []
        used_names = set()
        
        for i in range(count):
            # Generate unique name
            attempts = 0
            while attempts < 100:
                base_name = random.choice(machine_types)
                
                # Build name with variant and/or suffix
                if random.random() > 0.5:
                    variant = random.choice(variants)
                    name = f"{base_name} {variant}"
                else:
                    name = base_name
                
                # Sometimes add suffix
                if random.random() > 0.7:
                    suffix = random.choice(suffixes)
                    name = f"{name} {suffix}"
                
                if name not in used_names:
                    used_names.add(name)
                    break
                attempts += 1
            
            # Generate nominal power (between 3.0 and 25.0 kW)
            nominal_power_kw = round(random.uniform(3.0, 25.0), 1)
            
            # Generate power profile
            # idle: 0.05-0.2, loading: 0.4-0.7, produce: 0.8-1.0
            power_profile = {
                "idle": round(random.uniform(0.05, 0.2), 2),
                "loading": round(random.uniform(0.4, 0.7), 2),
                "produce": round(random.uniform(0.8, 1.0), 2)
            }
            
            # Generate material loading rate
            material_loading_rate = {}
            
            # Decide if this machine has material-specific rates or unit-based rates
            if materials and random.random() > 0.4:
                # Add specific material loading rates (1-3 materials)
                num_materials = random.randint(1, min(3, len(materials)))
                selected_materials = random.sample(materials, num_materials)
                
                for mat in selected_materials:
                    mat_name = mat["name"]
                    mat_unit = mat["unit"]
                    
                    # If material unit is piece, loading rate must be integer
                    if mat_unit == Unit.PIECE.value:
                        rate = random.randint(1, 10)
                    else:
                        rate = round(random.uniform(0.5, 5.0), 2)
                    
                    material_loading_rate[mat_name] = rate
            
            # Add loading rates for ALL valid material units (not kW, euro, etc.)
            valid_material_units = [
                Unit.GRAM.value, 
                Unit.KILOGRAM.value, 
                Unit.LITER.value, 
                Unit.MILLILITER.value, 
                Unit.PIECE.value
            ]
            
            for unit in valid_material_units:
                # If unit is piece, loading rate must be integer
                if unit == Unit.PIECE.value:
                    rate = random.randint(1, 10)
                else:
                    rate = round(random.uniform(0.5, 5.0), 2)
                
                material_loading_rate[unit] = rate
            
            
            # Generate max working hours per day (8-24)
            max_working_hours_per_day = random.randint(8, 24)
            
            machine = {
                "name": name,
                "nominal_power_kw": nominal_power_kw,
                "max_working_hours_per_day": max_working_hours_per_day,
                "power_profile": power_profile,
                "material_loading_rate": material_loading_rate
            }
            
            machines.append(machine)
            log.trace(f"Generated machine: {name} (power={nominal_power_kw}kW, max_hours={max_working_hours_per_day}h/day, {len(material_loading_rate)} loading rates)")
        
        log.success(f"Generated {len(machines)} machines")
        return machines
    
    def generate_machine_recipe_settings(
        self, 
        machines: list[dict], 
        recipes: list[dict]
    ) -> list[dict]:
        """
        Generate machine recipe settings ensuring every recipe is covered by at least one machine.
        
        Args:
            machines: List of machine dictionaries (must have 'name' key)
            recipes: List of recipe dictionaries (must have 'name', 'output_unit' keys)
            
        Returns:
            List of machine recipe setting dictionaries ready to be saved as JSON
        """
        if not machines:
            raise ValueError("Cannot generate settings without machines")
        if not recipes:
            raise ValueError("Cannot generate settings without recipes")
        
        log.info(f"Generating machine recipe settings for {len(recipes)} recipes and {len(machines)} machines...")
        
        settings = []
        
        # Track which recipes have been covered
        covered_recipes = set()
        
        # First pass: ensure every recipe is covered by at least one machine
        for recipe in recipes:
            recipe_name = recipe["name"]
            recipe_output_unit = recipe["output_unit"]
            
            # Pick a random machine for this recipe
            machine = random.choice(machines)
            machine_name = machine["name"]
            
            # Generate setting
            setting = self._generate_single_setting(machine_name, recipe_name, recipe_output_unit)
            settings.append(setting)
            covered_recipes.add(recipe_name)
            
            #log.trace(f"Assigned recipe '{recipe_name}' to machine '{machine_name}'")
        
        # Second pass: optionally add more settings (some recipes can be produced by multiple machines)
        # Add 0-2 extra settings per recipe for variety
        for recipe in recipes:
            recipe_name = recipe["name"]
            recipe_output_unit = recipe["output_unit"]
            
            # Decide how many extra machines can handle this recipe
            num_extra = random.randint(0, min(2, len(machines) - 1))
            
            if num_extra > 0:
                # Pick different machines
                available_machines = [m for m in machines]
                random.shuffle(available_machines)
                
                for i in range(num_extra):
                    machine = available_machines[i]
                    machine_name = machine["name"]
                    
                    # Check if this combination already exists
                    exists = any(
                        s["machine"] == machine_name and s["recipe"] == recipe_name 
                        for s in settings
                    )
                    
                    if not exists:
                        setting = self._generate_single_setting(machine_name, recipe_name, recipe_output_unit)
                        settings.append(setting)
                        log.trace(f"Added extra setting: recipe '{recipe_name}' on machine '{machine_name}'")
        
        log.success(f"Generated {len(settings)} machine recipe settings (all {len(recipes)} recipes covered)")
        return settings
    
    def _generate_single_setting(
        self, 
        machine_name: str, 
        recipe_name: str, 
        recipe_output_unit: str
    ) -> dict:
        """
        Generate a single machine recipe setting with random parameters.
        
        Args:
            machine_name: Name of the machine
            recipe_name: Name of the recipe
            recipe_output_unit: Output unit of the recipe (to respect piece constraints)
            
        Returns:
            Dictionary with machine recipe setting
        """
        # Time per batch (in seconds)
        time = round(random.uniform(1.0, 15.0), 1)
        
        # Setup time (in seconds)
        setup_time = round(random.uniform(30.0, 180.0), 1)
        
        # Unload time (in seconds)
        unload_time = round(random.uniform(30.0, 120.0), 1)
        
        # Yield rate (0.90 to 1.0)
        yield_rate = round(random.uniform(0.90, 1.0), 2)
        
        # Capacity (batch size)
        # If recipe output unit is piece, capacity must be integer
        if recipe_output_unit == Unit.PIECE.value:
            capacity = random.randint(20, 150)
        else:
            capacity = round(random.uniform(1.0, 20.0), 2)
        
        # Energy factor (0.8 to 1.3)
        energy_factor = round(random.uniform(0.8, 1.3), 2)
        
        setting = {
            "machine": machine_name,
            "recipe": recipe_name,
            "time": time,
            "setup_time": setup_time,
            "unload_time": unload_time,
            "yield_rate": yield_rate,
            "capacity": capacity,
            "energy_factor": energy_factor
        }
        
        return setting
    
    def generate_orders(self, recipes: list[dict], count: int = None, min_quantity: float = None) -> list[dict]:
        """
        Generate a list of N random orders.
        
        Args:
            recipes: List of recipe dictionaries (must have 'name', 'output_unit' keys)
            count: Number of orders to generate. If None, chooses random between 1 and 3.
            min_quantity: Minimum quantity for each recipe item. If None, uses defaults (50 for pieces, 5.0 for kg/L)
            
        Returns:
            List of order dictionaries ready to be saved as JSON
        """
        if not recipes:
            raise ValueError("Cannot generate orders without recipes")
        
        if count is None:
            count = random.randint(1, 3)
        
        log.info(f"Generating {count} random orders from {len(recipes)} recipes...")
        
        order_names = [
            "Daily Production Order", "Weekly Order", "Special Order",
            "Rush Order", "Customer Request", "Bulk Order",
            "Premium Order", "Standard Order", "Express Order"
        ]
        
        orders = []
        used_names = set()
        
        for i in range(count):
            # Generate unique name
            attempts = 0
            while attempts < 100:
                name = random.choice(order_names)
                if len(order_names) > count:
                    # Add number to avoid duplicates
                    if random.random() > 0.5:
                        name = f"{name} #{i+1}"
                
                if name not in used_names:
                    used_names.add(name)
                    break
                attempts += 1
            
            # Select 1-4 recipes for this order
            num_items = random.randint(1, min(4, len(recipes)))
            selected_recipes = random.sample(recipes, num_items)
            
            items = []
            for recipe in selected_recipes:
                recipe_name = recipe["name"]
                recipe_output_unit = recipe["output_unit"]
                
                # Determine min and max quantities based on unit and min_quantity parameter
                if recipe_output_unit == Unit.PIECE.value:
                    min_qty = int(min_quantity) if min_quantity is not None else 50
                    quantity = random.randint(min_qty, 1000)
                else:
                    min_qty = min_quantity if min_quantity is not None else 5.0
                    quantity = round(random.uniform(min_qty, 100.0), 2)
                
                items.append({
                    "recipe": recipe_name,
                    "quantity": quantity
                })
            
            order = {
                "name": name,
                "items": items
            }
            
            orders.append(order)
            log.trace(f"Generated order: {name} ({len(items)} items)")
        
        log.success(f"Generated {len(orders)} orders")
        return orders
    
    def generate_and_save_all(
        self,
        num_materials: int = None,
        num_recipes: int = None,
        num_machines: int = None,
        num_orders: int = None,
        min_order_quantity: float = None
    ) -> dict:
        """
        Generate all factory data and save to JSON files.
        
        Args:
            num_materials: Number of materials to generate (default: random 5-15)
            num_recipes: Number of recipes to generate (default: random 3-10)
            num_machines: Number of machines to generate (default: random 2-5)
            num_orders: Number of orders to generate (default: random 1-3)
            min_order_quantity: Minimum quantity for each recipe in orders (default: 50 for pieces, 5.0 for kg/L)
            
        Returns:
            Dictionary with counts of generated items
        """

        log.info("Starting data generation...")
        
        # Generate all data in dependency order
        materials = self.generate_materials(count=num_materials)
        recipes = self.generate_recipes(materials, count=num_recipes)
        machines = self.generate_machines(materials, count=num_machines)
        settings = self.generate_machine_recipe_settings(machines, recipes)
        orders = self.generate_orders(recipes, count=num_orders, min_quantity=min_order_quantity)
        
        # Save to files        
        log.info("Saving generated data to files...")                
        self.save_to_json(materials, self.materials_path, "materials")
        self.save_to_json(recipes, self.recipes_path, "recipes")
        self.save_to_json(machines, self.machines_path, "machines")
        self.save_to_json(settings, self.machine_recipe_settings_path, "machine recipe settings")
        self.save_to_json(orders, self.orders_path, "orders")
        
        # Return summary
        summary = {
            "materials": len(materials),
            "recipes": len(recipes),
            "machines": len(machines),
            "settings": len(settings),
            "orders": len(orders),
            "output_dir": str(self.output_dir)
        }
                
        log.info(f"All files saved to: {summary['output_dir']}\n\n")
        
        return summary
    
    def save_to_json(self, data: list, file_path: Path, data_type: str):
        """
        Save data to a JSON file.
        
        Args:
            data: List of dictionaries to save
            file_path: Path where to save the file
            data_type: Description of the data type (for logging)
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            log.debug(f"Saved {len(data)} {data_type} to '{file_path.name}'")
        except Exception as e:
            log.error(f"Failed to save {data_type} to '{file_path.name}': {e}")
            raise
