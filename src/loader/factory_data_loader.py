import json
from pathlib import Path
from src.entities.power_profile import MachinePowerProfile
from src.entities.units import Unit
from src.entities.raw_material import RawMaterial
from src.entities.recipe import Recipe
from src.entities.machine import Machine, MachineStorage, PowerProfile, MachineLoadingRates, LoadingRate
from src.entities.machine_recipe_setting import MachineRecipeSetting
from src.entities.order import Order, OrderItem
from src.utils.logging import log
from datetime import datetime
from src.schemas import MaterialSchema, RecipeSchema, MachineSchema, MachineRecipeSettingSchema, OrderSchema

class FactoryDataLoader:
    """
    Handles loading and linking all factory data from JSON files.
    """

    def __init__(
        self, 
        data_dir: str = "src/data",
        materials_file: str = "materials.json",
        recipes_file: str = "recipes.json",
        machines_file: str = "machines.json",
        machine_recipe_settings_file: str = "machines_recipe_settings.json",
        orders_file: str = "orders.json"
    ):
        self.data_dir = Path(data_dir)
        
        # Resource file paths
        self.materials_path = self.data_dir / materials_file
        self.recipes_path = self.data_dir / recipes_file
        self.machines_path = self.data_dir / machines_file
        self.machine_recipe_settings_path = self.data_dir / machine_recipe_settings_file
        self.orders_path = self.data_dir / orders_file

        self.materials: dict[str, RawMaterial] = {}
        self.recipes: dict[str, Recipe] = {}
        self.machines: dict[str, Machine] = {}
        self.orders: dict[str, Order] = {}        

    # ------------------------
    # PUBLIC LOADERS
    # ------------------------
    def load_all(self):        
        """Load all data in correct dependency order."""              
        log.info("Going to load factory data...")
                
        self._load_materials()
        self._load_recipes()
        self._load_machines()
        self._load_machine_recipe_settings()
        self._load_orders()

        log.success(f"Loaded {len(self.materials)} materials, "
              f"{len(self.recipes)} recipes, {len(self.machines)} machines, "
              f"{len(self.orders)} orders.")

    # ------------------------
    # INTERNAL LOADERS
    # ------------------------
    def _load_materials(self):
        """
        Loading materials
        """
        log.debug(f"Loading materials from '{self.materials_path.name}' ...")
        
        with open(self.materials_path, "r") as f:
            data = json.load(f)

        loaded = 0
        skipped = 0

        for i, item in enumerate(data, start=1):
            try:
                # 1. Validate and Parse with Pydantic
                # This automatically checks types, constraints, and missing fields.
                schema = MaterialSchema(**item)

                # 2. Check logical duplicates (business logic)
                if schema.name in self.materials:
                    raise ValueError(f"Duplicate material '{schema.name}'")

                # 3. Create Entity (Domain Object)
                # We map the validated schema back to our internal entity.
                material = RawMaterial(
                    name=schema.name,
                    unit=Unit(schema.unit),
                    unit_cost=schema.unit_cost,
                    stock_quantity=schema.stock_quantity
                )
                
                self.materials[material.name] = material
                loaded += 1
                log.trace(f"Loaded {material}")

            except Exception as e:
                skipped += 1
                # Pydantic errors are very descriptive!
                log.warn(f"Skipped material #{i}: {e}")
        
        log.success(f"Loaded {loaded} materials ({skipped} skipped)")

    def _load_recipes(self):
        """
        Loading using for Recipes.
        """
        log.debug(f"Loading recipes from '{self.recipes_path.name}' ...")

        with open(self.recipes_path, "r") as f:
            data = json.load(f)

        loaded = 0
        skipped = 0

        for i, item in enumerate(data, start=1):
            try:
                # 1. Validate with Pydantic
                schema = RecipeSchema(**item)

                # 2. Business Logic Checks
                if schema.name in self.recipes:
                    raise ValueError(f"Duplicate recipe '{schema.name}'")
                
                # Check output quantity coherence
                if schema.output_unit == Unit.PIECE.value and not float(schema.output_quantity).is_integer():
                     raise ValueError(f"Recipe '{schema.name}' output quantity must be integer when unit is 'piece'")

                # 3. Resolve Ingredients (Foreign Keys)
                ingredients = {}
                for mat_name, qty in schema.ingredients.items():
                    if mat_name not in self.materials:
                        raise ValueError(f"Ingredient '{mat_name}' not found in loaded materials")
                    
                    material = self.materials[mat_name]
                    
                    # Unit consistency check
                    if material.unit == Unit.PIECE and not float(qty).is_integer():
                        raise ValueError(f"Ingredient '{mat_name}' uses unit 'piece' but quantity '{qty}' is not an integer")

                    ingredients[material] = float(qty)

                # 4. Create Entity
                recipe = Recipe(
                    name=schema.name,
                    ingredients=ingredients,
                    output_quantity=schema.output_quantity,
                    output_unit=Unit(schema.output_unit),
                    description=schema.description,
                    category=schema.category
                )
                
                self.recipes[recipe.name] = recipe
                loaded += 1
                log.trace(f"Loaded {recipe}")

            except Exception as e:
                skipped += 1
                log.warn(f"Skipped recipe #{i}: {e}")

        log.success(f"Loaded {loaded} recipes ({skipped} skipped)")
          

    def _load_machines(self):
        """
        Loading machines
        """
        log.debug(f"Loading machines from '{self.machines_path.name}' ...")

        with open(self.machines_path, "r") as f:
            data = json.load(f)

        loaded = 0
        skipped = 0

        for i, item in enumerate(data, start=1):
            try:
                # 1. Validate with Pydantic
                schema = MachineSchema(**item)

                # 2. Business Logic Checks
                if schema.name in self.machines:
                    raise ValueError(f"Duplicate machine '{schema.name}'")

                # 3. Process Power Profile
                power_profile = {}
                for state, factor in schema.power_profile.items():
                    power_profile[MachinePowerProfile(state)] = factor

                # 5. Process Loading Rates
                by_unit_rates = {}
                by_material_rates = {}
                
                for key, value in schema.material_loading_rate.items():
                    if key in [u.value for u in Unit]:
                        unit = Unit(key)
                        if unit == Unit.PIECE and not float(value).is_integer():
                             raise ValueError(f"Machine '{schema.name}' loading rate for unit 'piece' must be integer")
                        by_unit_rates[unit] = LoadingRate(rate=value, quant=Unit.SECONDS, over_quant=unit)
                    else:
                        # Material name
                        if key not in self.materials:
                             log.warn(f"Machine '{schema.name}' defines loading rate for unknown material '{key}'")
                        
                        # Try to determine unit from material if known
                        over_quant = Unit.PIECE
                        if key in self.materials:
                            over_quant = self.materials[key].unit
                            if over_quant == Unit.PIECE and not float(value).is_integer():
                                raise ValueError(f"Machine '{schema.name}' loading rate for material '{key}' uses unit 'piece' but value is not integer")

                        by_material_rates[key] = LoadingRate(rate=value, quant=Unit.SECONDS, over_quant=over_quant)

                loading_rates = MachineLoadingRates(by_unit=by_unit_rates, by_material=by_material_rates)

                # 5. Create Entity
                machine = Machine(
                    name=schema.name,
                    nominal_power_kw=schema.nominal_power_kw,
                    power_profile=power_profile,                    
                    loading_rates=loading_rates,
                    max_working_hours_per_day=schema.max_working_hours_per_day,
                )

                self.machines[machine.name] = machine
                loaded += 1
                log.trace(f"Loaded {machine}")

            except Exception as e:
                skipped += 1
                log.warn(f"Skipped machine #{i}: {e}")

        log.success(f"Loaded {loaded} machines ({skipped} skipped)")
            
            
    def _load_machine_recipe_settings(self):
        """
        Loading machine recipe settings using Pydantic.
        """
        log.debug(f"Loading settings from '{self.machine_recipe_settings_path.name}' ...")

        with open(self.machine_recipe_settings_path, "r") as f:
            data = json.load(f)

        loaded = 0
        skipped = 0

        for i, item in enumerate(data, start=1):
            try:
                # 1. Validate with Pydantic
                schema = MachineRecipeSettingSchema(**item)

                # 2. Resolve Foreign Keys
                if schema.machine not in self.machines:
                    raise ValueError(f"Machine '{schema.machine}' not found.")
                if schema.recipe not in self.recipes:
                    raise ValueError(f"Recipe '{schema.recipe}' not found.")

                machine = self.machines[schema.machine]
                recipe = self.recipes[schema.recipe]

                # 3. Data Integrity Constraints
                # If recipe output unit is PIECE, capacity must be an integer
                if recipe.output_unit == Unit.PIECE and not float(schema.capacity).is_integer():
                    raise ValueError(
                        f"Machine '{schema.machine}' recipe '{schema.recipe}': "
                        f"capacity must be an integer when recipe output_unit is 'piece'"
                    )

                # 4. Create Entity
                setting = MachineRecipeSetting(
                    recipe=recipe,
                    time=schema.time,
                    setup_time=schema.setup_time,
                    unload_time=schema.unload_time,
                    yield_rate=schema.yield_rate,
                    capacity=schema.capacity,                    
                    energy_factor=schema.energy_factor
                )

                machine.add_setting(setting)
                loaded += 1
                log.trace(f"Loaded {setting}\n        on machine: {machine.name}")

            except Exception as e:
                skipped += 1
                log.warn(f"Skipped setting #{i}: {e}")

        log.success(f"Loaded {loaded} settings ({skipped} skipped)")

    def _load_orders(self):
        """
        Loading orders using Pydantic.
        """
        log.debug(f"Loading orders from '{self.orders_path.name}' ...")

        with open(self.orders_path, "r") as f:
            data = json.load(f)

        loaded = 0
        skipped = 0

        for i, item in enumerate(data, start=1):
            try:
                # 1. Validate with Pydantic
                schema = OrderSchema(**item)

                # 2. Business Logic Checks
                if schema.name in self.orders:
                    raise ValueError(f"Duplicate order '{schema.name}'")

                # 3. Resolve Foreign Keys and Create Items
                order_items = []
                for item_schema in schema.items:
                    if item_schema.recipe not in self.recipes:
                        raise ValueError(f"Recipe '{item_schema.recipe}' not found.")
                    
                    recipe = self.recipes[item_schema.recipe]
                    
                    # 4. Data Integrity Constraints
                    # If recipe output unit is PIECE, quantity must be an integer
                    if recipe.output_unit == Unit.PIECE and not float(item_schema.quantity).is_integer():
                        raise ValueError(
                            f"Order '{schema.name}' recipe '{item_schema.recipe}': "
                            f"quantity must be an integer when recipe output_unit is 'piece'"
                        )
                    
                    order_item = OrderItem(
                        recipe=recipe,
                        quantity=item_schema.quantity
                    )
                    order_items.append(order_item)

                # 5. Create Entity
                order = Order(
                    name=schema.name,
                    items=order_items
                )

                self.orders[order.name] = order
                loaded += 1
                log.trace(f"Loaded {order}")

            except Exception as e:
                skipped += 1
                log.warn(f"Skipped order #{i}: {e}")

        log.success(f"Loaded {loaded} orders ({skipped} skipped)")

