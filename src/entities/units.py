from enum import Enum

class Unit(Enum):
    GRAM = "g"
    KILOGRAM = "kg"
    LITER = "L"
    MILLILITER = "mL"
    PIECE = "pc"
    
    def __str__(self):
        """Human-readable representation (so print(Unit.KILOGRAM) -> 'kg')."""
        return self.value