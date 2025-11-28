from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from src.entities.units import Unit
from src.entities.power_profile import MachinePowerProfile

class MaterialSchema(BaseModel):
    name: str = Field(..., min_length=1, description="Unique name of the material")
    unit: str = Field(..., description="Unit of measurement (e.g., 'kg', 'L', 'piece')")
    unit_cost: float = Field(..., ge=0, description="Cost per unit")
    stock_quantity: float = Field(..., ge=0, description="Current stock quantity")
    prep_time: float = Field(..., ge=0, description="Preparation time in seconds")


    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: str) -> str:
        # Check if the string is a valid member of the Unit enum
        valid_units = [u.value for u in Unit]
        if v not in valid_units:
            raise ValueError(f"Invalid unit '{v}'. Must be one of {valid_units}")
        return v

class RecipeSchema(BaseModel):
    name: str = Field(..., min_length=1)
    ingredients: dict[str, float] = Field(..., description="Map of material name to quantity")
    output_quantity: float = Field(..., gt=0)
    output_unit: str
    
    # Optional
    description: Optional[str] = None
    category: Optional[str] = None

    @field_validator("output_unit")
    @classmethod
    def validate_unit(cls, v: str) -> str:
        valid_units = [u.value for u in Unit]
        if v not in valid_units:
            raise ValueError(f"Invalid unit '{v}'. Must be one of {valid_units}")
        return v

    @field_validator("ingredients")
    @classmethod
    def validate_ingredients(cls, v: dict[str, float]) -> dict[str, float]:
        if not v:
            raise ValueError("Ingredients cannot be empty")
        for name, qty in v.items():
            if qty <= 0:
                raise ValueError(f"Ingredient '{name}' must have positive quantity")
        return v

class MachineSchema(BaseModel):
    name: str = Field(..., min_length=1)
    nominal_power_kw: float = Field(..., gt=0)

    power_profile: dict[str, float] = Field(default_factory=dict)
    material_loading_rate: dict[str, float] = Field(default_factory=dict)

    @field_validator("power_profile")
    @classmethod
    def validate_power_profile(cls, v: dict[str, float]) -> dict[str, float]:
        valid_states = [s.value for s in MachinePowerProfile]
        for state, factor in v.items():
            if state not in valid_states:
                raise ValueError(f"Invalid power state '{state}'. Must be one of {valid_states}")
            if factor < 0:
                raise ValueError(f"Power factor for '{state}' must be non-negative")
        return v

    @field_validator("material_loading_rate")
    @classmethod
    def validate_positive_values(cls, v: dict[str, float]) -> dict[str, float]:
        for key, val in v.items():
            if val < 0:
                 raise ValueError(f"Value for '{key}' must be non-negative")
        return v

class MachineRecipeSettingSchema(BaseModel):
    machine: str = Field(..., min_length=1)
    recipe: str = Field(..., min_length=1)
    time: float = Field(..., gt=0)
    setup_time: float = Field(..., ge=0)
    unload_time: float = Field(0.0, ge=0)
    yield_rate: float = Field(..., gt=0, le=1)
    capacity: float = Field(..., gt=0)    
    energy_factor: float = Field(1.0, gt=0)

class OrderItemSchema(BaseModel):
    recipe: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)

class OrderSchema(BaseModel):
    name: str = Field(..., min_length=1)
    items: list[OrderItemSchema] = Field(..., min_length=1)
    
    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[OrderItemSchema]) -> list[OrderItemSchema]:
        if not v:
            raise ValueError("Order must have at least one item")
        return v

