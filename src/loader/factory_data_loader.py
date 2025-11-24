import json
from pathlib import Path
from src.entities.power_profile import MachinePowerProfile
from src.entities.units import Unit
from src.entities.raw_material import RawMaterial
from src.entities.recipe import Recipe
from src.entities.machine import Machine, MachineStorage, PowerProfile, MachineLoadingRates, LoadingRate
from src.entities.machine_recipe_setting import MachineRecipeSetting
from src.utils.logging import log
from datetime import datetime
from src.schemas import MaterialSchema

class FactoryDataLoader:
    """
    Handles loading and linking all factory data from JSON files.
    """

    def __init__(self, data_dir: str = "src/data"):
        self.data_dir = Path(data_dir)

        self.materials: dict[str, RawMaterial] = {}
        self.recipes: dict[str, Recipe] = {}
        self.machines: dict[str, Machine] = {}        

    # ------------------------
    # PUBLIC LOADERS
    # ------------------------
    def load_all(self):        
        """Load all data in correct dependency order."""              
        log.info("Going to load factory data...")
                
        self._load_materials_pydantic()
        self._load_recipes()
        self._load_machines()
        self._load_machine_recipe_settings()

        log.success(f"Loaded {len(self.materials)} materials, "
              f"{len(self.recipes)} recipes, {len(self.machines)} machines.")

    # ------------------------
    # INTERNAL LOADERS
    # ------------------------
    def _load_materials(self):
        path = self.data_dir / "materials.json"
        log.debug(f"Loading materials from '{path.name}' ...")
        
        with open(path, "r") as f:
            data = json.load(f)

        loaded = 0
        skipped = 0

        for i, m in enumerate(data, start=1):
            try:
                name = str(m.get("name", "")).strip()
                unit_str = str(m.get("unit", "")).strip()

                # --- Basic checks ---
                if not name:
                    raise ValueError("Missing name")
                if name in self.materials:
                    raise ValueError(f"Duplicate material '{name}'")
                if unit_str not in [u.value for u in Unit]:
                    raise ValueError(f"Material '{name}' has invalid unit '{unit_str}'")
                if m.get("unit_cost", -1) < 0:
                    raise ValueError(f"Material '{name}' has negative unit_cost.")
                if m.get("stock_quantity", -1) < 0:
                    raise ValueError(f"Material '{name}' has negative stock_quantity.")
                if m.get("prep_time", -1) < 0:
                    raise ValueError(f"Material '{name}' has negative prep_time.")

                
                material = RawMaterial(
                    name=name,
                    unit=Unit(unit_str),
                    unit_cost=float(m["unit_cost"]),
                    stock_quantity=float(m["stock_quantity"]),
                    prep_time=float(m["prep_time"]),
                )
                self.materials[material.name] = material
                loaded += 1
                log.trace(f"Loaded {material}")

            except Exception as e:
                skipped += 1
                log.warn(f"Skipped material #{i}: {e}")
        
        if(loaded == 0):
            log.error("No materials loaded. Please check the data files")
        else:
            log.info(f"Loaded {loaded} materials ({skipped} skipped)")

    def _load_materials_pydantic(self):
        """
        Example of robust loading using Pydantic.
        """
        path = self.data_dir / "materials.json"
        log.debug(f"Loading materials (Pydantic) from '{path.name}' ...")
        
        with open(path, "r") as f:
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
                    stock_quantity=schema.stock_quantity,
                    prep_time=schema.prep_time,
                )
                
                self.materials[material.name] = material
                loaded += 1
                log.trace(f"Loaded {material}")

            except Exception as e:
                skipped += 1
                # Pydantic errors are very descriptive!
                log.warn(f"Skipped material #{i}: {e}")
        
        log.success(f"[Pydantic] Loaded {loaded} materials ({skipped} skipped)")


    def _load_recipes(self):
        path = self.data_dir / "recipes.json"
        log.debug(f"Loading recipes from '{path.name}' ...")

        with open(path, "r") as f:
            data = json.load(f)

        loaded = 0
        skipped = 0

        for i, r in enumerate(data, start=1):
            try:
                name = str(r.get("name", "")).strip()
                output_quantity = float(r.get("output_quantity", -1))
                output_unit_str = str(r.get("output_unit", "")).strip()
                ingredients_dict = r.get("ingredients", {})

                # --- Basic checks ---
                if not name:
                    raise ValueError("Missing recipe name")
                if name in self.recipes:
                    raise ValueError(f"Duplicate recipe '{name}'")
                if output_quantity <= 0:
                    raise ValueError(f"Recipe '{name}' has invalid output_quantity '{output_quantity}'")
                if output_unit_str not in [u.value for u in Unit]:
                    raise ValueError(f"Recipe '{name}' has invalid output unit '{output_unit_str}'")
                if not ingredients_dict or not isinstance(ingredients_dict, dict):
                    raise ValueError(f"Recipe '{name}' has no valid ingredients")

                output_unit = Unit(output_unit_str)

                # --- Check output quantity coherence ---
                if output_unit == Unit.PIECE and not float(output_quantity).is_integer():
                    raise ValueError(f"Recipe '{name}' output quantity must be integer when unit is 'piece' (got {output_quantity})")

                # --- Validate ingredients ---
                ingredients = {}
                for mat_name, qty in ingredients_dict.items():
                    mat_name_clean = str(mat_name).strip()
                    if mat_name_clean not in self.materials:
                        raise ValueError(f"Ingredient '{mat_name_clean}' not found in loaded materials")
                    if not isinstance(qty, (int, float)) or qty <= 0:
                        raise ValueError(f"Ingredient '{mat_name_clean}' has invalid quantity '{qty}'")

                    material = self.materials[mat_name_clean]
                    
                    if material.unit == Unit.PIECE and not float(qty).is_integer():
                        raise ValueError(f"Ingredient '{mat_name_clean}' uses unit 'piece' but quantity '{qty}' is not an integer")

                    ingredients[material] = float(qty)
                
                recipe = Recipe(
                    name=name,
                    ingredients=ingredients,
                    output_quantity=output_quantity,
                    output_unit=output_unit,
                )
                self.recipes[recipe.name] = recipe
                loaded += 1
                log.trace(f"Loaded {recipe}")

            except Exception as e:
                skipped += 1
                log.warn(f"Skipped recipe #{i}: {e}")

        if(loaded == 0):
            log.error("No recipes loaded. Please check the data files")
        else:
            log.info(f"Loaded {loaded} recipes ({skipped} skipped)")
            

    def _load_machines(self):
        path = self.data_dir / "machines.json"
        log.debug(f"Loading machines from '{path.name}' ...")

        with open(path, "r") as f:
            data = json.load(f)

        loaded = 0
        skipped = 0

        for i, m in enumerate(data, start=1):
            try:
                name = str(m.get("name", "")).strip()
                hourly_cost = float(m.get("hourly_cost", -1))
                nominal_power_kw = float(m.get("nominal_power_kw", -1))
                base_efficiency = float(m.get("base_efficiency", -1))
                shifts_per_day = int(m.get("shifts_per_day", 0))
                hours_per_shift = float(m.get("hours_per_shift", 0))
                power_profile = m.get("power_profile", {})
                storage_dict = m.get("internal_storage_capacity", {})
                loading_rate_dict = m.get("material_loading_rate", {})

                # --- Basic checks ---
                if not name:
                    raise ValueError("Missing machine name")
                if name in self.machines:
                    raise ValueError(f"Duplicate machine '{name}'")
                if hourly_cost < 0:
                    raise ValueError(f"Machine '{name}' has negative hourly_cost")
                if nominal_power_kw <= 0:
                    raise ValueError(f"Machine '{name}' has invalid nominal_power_kw ({nominal_power_kw})")
                if not (0 < base_efficiency <= 1):
                    raise ValueError(f"Machine '{name}' has invalid base_efficiency ({base_efficiency})")
                if shifts_per_day <= 0 or hours_per_shift <= 0:
                    raise ValueError(f"Machine '{name}' has invalid working schedule ({shifts_per_day}x{hours_per_shift})")
                
                # --- Validate power profile ---
                valid_profiles = {}
                if not isinstance(power_profile, dict):
                    raise ValueError(f"Machine '{name}' power_profile must be a dict")
                for state, factor in power_profile.items():                    
                    if not state in [s.value for s in MachinePowerProfile]:
                        raise ValueError(f"Machine '{name}' has invalid power profile state '{state}' (allowed: {[s.value for s in MachinePowerProfile]})")
                    if not isinstance(factor, (int, float)) or factor < 0:
                        raise ValueError(f"Machine '{name}' invalid power factor '{factor}' for state '{state}'")                                        
                    valid_profiles[MachinePowerProfile(state)] = float(factor)

                # --- Validate and split storage capacity ---
                if not isinstance(storage_dict, dict):
                    raise ValueError(f"Machine '{name}' internal_storage_capacity must be a dict")

                by_unit = {}
                by_material = {}
                for key, value in storage_dict.items():
                    if not isinstance(value, (int, float)) or value < 0:
                        raise ValueError(f"Machine '{name}' invalid capacity '{value}' for '{key}'")

                    # Distinguish between Unit and material name
                    if key in [u.value for u in Unit]:
                        by_unit[Unit(key)] = float(value)
                    else:
                        by_material[str(key).strip()] = float(value)

                storage = MachineStorage(by_unit=by_unit, by_material=by_material)

                # --- Validate and split loading rate ---
                if not isinstance(loading_rate_dict, dict):
                    raise ValueError(f"Machine '{name}' material_loading_rate must be a dict")

                by_unit_rates = {}
                by_material_rates = {}
                
                for key, value in loading_rate_dict.items():
                    key_str = str(key).strip()
                    if not isinstance(value, (int, float)) or value <= 0:
                        raise ValueError(f"Machine '{name}' invalid loading rate '{value}' for '{key_str}'")

                    # Distinguish between unit and material name
                    if key_str in [u.value for u in Unit]:
                        unit = Unit(key_str)
                        if unit == Unit.PIECE and not float(value).is_integer():
                            raise ValueError(
                                f"Machine '{name}' loading rate for unit 'piece' must be integer (got {value})"
                            )
                        # Create LoadingRate object
                        by_unit_rates[unit] = LoadingRate(rate=float(value), quant=Unit.SECONDS, over_quant=unit)
                    else:
                        # interpret as material name
                        if key_str not in self.materials:
                            log.warn(f"Machine '{name}' defines loading rate for unknown material '{key_str}'")
                        else:
                            mat = self.materials[key_str]
                            # consistency check: same unit
                            if mat.unit == Unit.PIECE and not float(value).is_integer():
                                raise ValueError(
                                    f"Machine '{name}' loading rate for material '{key_str}' uses unit 'piece' "
                                    f"but non-integer value {value}"
                                )                        
                        over_quant = Unit.PIECE
                        if key_str in self.materials:
                            over_quant = self.materials[key_str].unit
                        
                        by_material_rates[key_str] = LoadingRate(rate=float(value), quant=Unit.SECONDS, over_quant=over_quant)

                loading_rates = MachineLoadingRates(by_unit=by_unit_rates, by_material=by_material_rates)
                            
                # --- All good, create machine ---
                machine = Machine(
                    name=name,
                    hourly_cost=hourly_cost,
                    nominal_power_kw=nominal_power_kw,
                    base_efficiency=base_efficiency,
                    shifts_per_day=shifts_per_day,
                    hours_per_shift=hours_per_shift,
                    power_profile=valid_profiles,
                    storage=storage,
                    loading_rates=loading_rates,
                )

                self.machines[machine.name] = machine
                loaded += 1
                log.trace(f"Loaded {machine}")

            except Exception as e:
                skipped+= 1
                log.warn(f"Skipped machine #{i}: {e}")
        
        if(loaded == 0):
            log.error("No machines loaded. Please check the data files")
        else:
            log.info(f"Loaded {loaded} machines ({skipped} skipped)")
            

        
        

    def _load_machine_recipe_settings(self):
        path = self.data_dir / "machines_recipe_settings.json"
        with open(path, "r") as f:
            data = json.load(f)

        for s in data:
            if s["machine"] not in self.machines:
                raise ValueError(f"Machine '{s['machine']}' not found.")
            if s["recipe"] not in self.recipes:
                raise ValueError(f"Recipe '{s['recipe']}' not found.")

            machine = self.machines[s["machine"]]
            recipe = self.recipes[s["recipe"]]

            setting = MachineRecipeSetting(
                recipe=recipe,
                unit_time=s["unit_time"],
                setup_time=s["setup_time"],
                yield_rate=s["yield_rate"],
                batch_capacity=s["batch_capacity"],
                batch_unit=Unit(s["batch_unit"]),
                batch_label=s.get("batch_label", "batch"),
                energy_factor=s.get("energy_factor", 1.0)
            )

            machine.add_setting(setting)

