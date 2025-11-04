import json
from pathlib import Path
from src.entities.units import Unit
from src.entities.raw_material import RawMaterial
from src.entities.recipe import Recipe
from src.entities.machine import Machine
from src.entities.machine_recipe_setting import MachineRecipeSetting


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
        self._load_materials()
        self._load_recipes()
        self._load_machines()
        self._load_machine_recipe_settings()

        print(f"[INFO] Loaded {len(self.materials)} materials, "
              f"{len(self.recipes)} recipes, {len(self.machines)} machines.")

    # ------------------------
    # INTERNAL LOADERS
    # ------------------------
    def _load_materials(self):
        path = self.data_dir / "materials.json"
        with open(path, "r") as f:
            data = json.load(f)

        for m in data:
            material = RawMaterial(
                name=m["name"],
                unit=Unit(m["unit"]),
                unit_cost=m["unit_cost"],
                stock_quantity=m["stock_quantity"],
                prep_time=m["prep_time"],
            )
            self.materials[material.name] = material

    def _load_recipes(self):
        path = self.data_dir / "recipes.json"
        with open(path, "r") as f:
            data = json.load(f)

        for r in data:
            ingredients = {}
            for mat_name, qty in r["ingredients"].items():
                if mat_name not in self.materials:
                    raise ValueError(f"Material '{mat_name}' not found for recipe '{r['name']}'")
                ingredients[self.materials[mat_name]] = qty

            recipe = Recipe(
                name=r["name"],
                ingredients=ingredients,
                output_quantity=r["output_quantity"],
                output_unit=Unit(r["output_unit"])
            )
            self.recipes[recipe.name] = recipe

    def _load_machines(self):
        path = self.data_dir / "machines.json"
        with open(path, "r") as f:
            data = json.load(f)

        for m in data:
            machine = Machine(
                name=m["name"],
                hourly_cost=m["hourly_cost"],
                nominal_power_kw=m["nominal_power_kw"],
                base_efficiency=m["base_efficiency"],
                shifts_per_day=m["shifts_per_day"],
                hours_per_shift=m["hours_per_shift"],
                power_profile=m.get("power_profile", {"idle": 0.1, "load": 0.6, "produce": 1.0}),
                internal_storage_capacity=m.get("internal_storage_capacity", {}),
                material_loading_rate=m.get("material_loading_rate", {}),
            )
            self.machines[machine.name] = machine

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

    # ------------------------
    # UTILITIES
    # ------------------------
    def summary(self):
        lines = [
            f"📦 Materials loaded: {len(self.materials)}",
            f"🍪 Recipes loaded: {len(self.recipes)}",
            f"⚙️ Machines loaded: {len(self.machines)}",
        ]
        return "\n".join(lines)
